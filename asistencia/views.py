import os

import cv2
import numpy as np
from django.contrib import messages
from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.timezone import localtime
from django.views.decorators.http import require_POST

from .camara import Camara
from .forms import HorarioForm
from .models import Asistencia, Horario


# ---------- Horarios ----------

def horario_abierto(hora=None):
    """Horario en el que se está tomando asistencia en este momento."""
    hora = hora or localtime().time()

    for horario in Horario.objects.all():
        if horario.esta_abierto(hora):
            return horario

    return None


def horario_de_referencia(ahora=None):
    """Horario abierto o, si no hay, la última clase que terminó hoy."""
    ahora = ahora or localtime()
    abierto = horario_abierto(ahora.time())

    if abierto:
        return abierto, True

    terminados_hoy = [
        h for h in Horario.objects.all()
        if h.fin_de_sesion(ahora).date() == ahora.date()
    ]
    if not terminados_hoy:
        return None, False

    ultimo = max(terminados_hoy, key=lambda h: h.fin_de_sesion(ahora))
    return ultimo, False


def info_horario(horario, abierto):
    if horario is None:
        return None

    return {
        'nombre': horario.nombre,
        'turno': horario.turno,
        'inicio': horario.hora_inicio.strftime('%H:%M'),
        'tardanza': horario.hora_tardanza.strftime('%H:%M'),
        'fin': horario.hora_fin.strftime('%H:%M'),
        'abierto': abierto,
    }


# ---------- Cámara ----------

def registrar_si_corresponde(nombre):
    """Registra la llegada una vez por día y por horario.

    Si no hay un horario abierto, la asistencia se guarda igual
    (sin clase asociada) para que nunca se pierda un reconocimiento.
    """
    ahora = localtime()
    horario = horario_abierto(ahora.time())

    # Una sesión nocturna (p. ej. 22:00 → 00:00) empieza "ayer" si ya pasó
    # la medianoche, por eso se busca desde el inicio de la sesión.
    if horario:
        desde = horario.inicio_de_sesion(ahora)
    else:
        desde = ahora.replace(hour=0, minute=0, second=0, microsecond=0)

    existe = Asistencia.objects.filter(
        nombre=nombre,
        horario=horario,
        fecha_hora__gte=desde,
    ).exists()

    if existe:
        return True

    estado = horario.estado_para(ahora.time()) if horario else 'presente'

    Asistencia.objects.create(
        nombre=nombre,
        horario=horario,
        estado=estado,
    )
    print('Asistencia registrada:', nombre, '-', horario.nombre if horario else 'sin horario')
    return True


def generar_frames():
    camara = Camara()
    registrados = set()

    try:
        while True:
            frame = camara.obtener_frame()

            if frame is None:
                break

            nombre = camara.ultimo_reconocido

            if nombre:
                ahora = localtime()
                horario = horario_abierto(ahora.time())
                sesion = horario.inicio_de_sesion(ahora) if horario else ahora.date()
                clave = (nombre, horario.id if horario else None, sesion)

                if clave not in registrados:
                    if registrar_si_corresponde(nombre):
                        registrados.add(clave)

            ok, jpg = cv2.imencode('.jpg', frame)

            if not ok:
                continue

            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n'
                + jpg.tobytes()
                + b'\r\n'
            )

    finally:
        camara.liberar()


def video_feed(request):
    return StreamingHttpResponse(
        generar_frames(),
        content_type='multipart/x-mixed-replace; boundary=frame'
    )


# ---------- Datos ----------

def estudiantes_registrados():
    ruta = os.path.join(os.path.dirname(__file__), 'nombres.npy')

    try:
        nombres = np.load(ruta, allow_pickle=True).item()
    except (OSError, ValueError):
        return []

    return sorted(nombres.values())


def preparar_registros(asistencias):
    registros = []

    for asistencia in asistencias:
        fecha_hora = localtime(asistencia.fecha_hora)
        registros.append({
            'nombre': asistencia.nombre,
            'fecha': fecha_hora.strftime('%d/%m/%Y'),
            'hora': fecha_hora.strftime('%H:%M'),
            'estado': asistencia.estado,
            'clase': asistencia.horario.nombre if asistencia.horario else '—',
        })

    return registros


def datos_de_hoy():
    ahora = localtime()
    horario, abierto = horario_de_referencia(ahora)

    if horario:
        # Clase en curso o la última que terminó hoy: se muestra esa sesión
        # y quien no llegó cuenta como ausente.
        asistencias = Asistencia.objects.filter(
            horario=horario,
            fecha_hora__gte=horario.inicio_de_sesion(ahora),
        )
    else:
        # Sin clases hoy: todas las llegadas del día.
        asistencias = Asistencia.objects.filter(fecha_hora__date=ahora.date())

    registros = preparar_registros(
        asistencias.select_related('horario').order_by('-fecha_hora')
    )

    llegaron = {registro['nombre'] for registro in registros}
    ausentes = [n for n in estudiantes_registrados() if n not in llegaron]

    resumen = {
        'presentes': sum(r['estado'] == 'presente' for r in registros),
        'tardanzas': sum(r['estado'] == 'tardanza' for r in registros),
        'ausentes': len(ausentes),
    }

    return {
        'registros': registros,
        'resumen': resumen,
        'ausentes': ausentes,
        'horario': info_horario(horario, abierto),
    }


# ---------- Páginas ----------

def inicio(request):
    contexto = datos_de_hoy()
    contexto['pestana'] = 'camara'
    return render(request, 'asistencia/inicio.html', contexto)


def lista_asistencias(request):
    asistencias = Asistencia.objects.select_related('horario').order_by('-fecha_hora')

    return render(
        request,
        'asistencia/lista_asistencias.html',
        {'registros': preparar_registros(asistencias), 'pestana': 'historial'}
    )


def obtener_asistencias(request):
    datos = datos_de_hoy()

    return JsonResponse({
        'asistencias': datos['registros'],
        'resumen': datos['resumen'],
        'ausentes': datos['ausentes'],
        'horario': datos['horario'],
    })


def horarios(request, pk=None):
    editando = get_object_or_404(Horario, pk=pk) if pk else None

    if request.method == 'POST':
        form = HorarioForm(request.POST, instance=editando)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Horario actualizado.' if editando else 'Horario registrado.'
            )
            return redirect('horarios')
    else:
        form = HorarioForm(instance=editando)

    abierto = horario_abierto()

    return render(request, 'asistencia/horarios.html', {
        'form': form,
        'editando': editando,
        'horarios': Horario.objects.all(),
        'abierto_id': abierto.id if abierto else None,
        'pestana': 'horarios',
    })


@require_POST
def eliminar_horario(request, pk):
    horario = get_object_or_404(Horario, pk=pk)
    horario.delete()
    messages.success(request, 'Horario eliminado.')
    return redirect('horarios')
