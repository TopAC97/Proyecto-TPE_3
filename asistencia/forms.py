from django import forms

from .models import Horario


class HorarioForm(forms.ModelForm):
    class Meta:
        model = Horario
        fields = ['nombre', 'hora_inicio', 'hora_tardanza', 'hora_fin']
        labels = {
            'nombre': 'Nombre de la clase',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Ej.: Programación I'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time'}, format='%H:%M'),
            'hora_tardanza': forms.TimeInput(attrs={'type': 'time'}, format='%H:%M'),
            'hora_fin': forms.TimeInput(attrs={'type': 'time'}, format='%H:%M'),
        }

    def clean(self):
        datos = super().clean()
        inicio = datos.get('hora_inicio')
        tardanza = datos.get('hora_tardanza')
        fin = datos.get('hora_fin')

        if not (inicio and tardanza and fin):
            return datos

        # Horario temporal para validar con la misma lógica que usa la cámara
        # (admite clases que pasan la medianoche, p. ej. 22:00 → 00:00).
        prueba = Horario(hora_inicio=inicio, hora_tardanza=tardanza, hora_fin=fin)
        hasta_tardanza = prueba.minutos_desde_inicio(tardanza)

        if prueba.duracion == 0:
            raise forms.ValidationError('La hora de fin no puede ser igual a la de inicio.')

        if not (0 < hasta_tardanza <= prueba.duracion):
            raise forms.ValidationError(
                'Las horas deben ir en orden: inicio, luego tardanza, luego fin '
                '(si la clase pasa la medianoche, el fin puede ser del día siguiente).'
            )

        otros = Horario.objects.all()
        if self.instance.pk:
            otros = otros.exclude(pk=self.instance.pk)

        for otro in otros:
            if prueba.se_cruza_con(otro):
                raise forms.ValidationError(
                    f'Este horario se cruza con «{otro.nombre}» '
                    f'({otro.hora_inicio:%H:%M} – {otro.hora_fin:%H:%M}).'
                )

        return datos
