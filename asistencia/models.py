from datetime import timedelta

from django.db import models

MINUTOS_DIA = 24 * 60


def a_minutos(hora):
    return hora.hour * 60 + hora.minute


def turno_de(hora):
    """Mañana: 05:00–11:59 · Tarde: 12:00–18:59 · Noche: 19:00–04:59."""
    h = hora.hour
    if 5 <= h < 12:
        return 'Mañana'
    if 12 <= h < 19:
        return 'Tarde'
    return 'Noche'


class Horario(models.Model):
    nombre = models.CharField(max_length=100)
    hora_inicio = models.TimeField('Inicio de la clase')
    hora_tardanza = models.TimeField('Tardanza desde')
    hora_fin = models.TimeField('Fin de la clase')

    class Meta:
        ordering = ['hora_inicio']

    def __str__(self):
        return f'{self.nombre} ({self.hora_inicio:%H:%M} - {self.hora_fin:%H:%M})'

    # Todas las comparaciones se hacen en "minutos desde el inicio de la clase"
    # (módulo 24 h), así funcionan también las clases que pasan la medianoche,
    # por ejemplo 22:00 → 00:00.
    def minutos_desde_inicio(self, hora):
        return (a_minutos(hora) - a_minutos(self.hora_inicio)) % MINUTOS_DIA

    @property
    def duracion(self):
        return self.minutos_desde_inicio(self.hora_fin)

    @property
    def cruza_medianoche(self):
        return self.hora_fin <= self.hora_inicio

    @property
    def turno(self):
        return turno_de(self.hora_inicio)

    def esta_abierto(self, hora):
        return self.minutos_desde_inicio(hora) <= self.duracion

    def estado_para(self, hora):
        if self.minutos_desde_inicio(hora) >= self.minutos_desde_inicio(self.hora_tardanza):
            return 'tardanza'
        return 'presente'

    def inicio_de_sesion(self, ahora):
        """Fecha y hora en que empezó la sesión más reciente (<= ahora)."""
        inicio = ahora.replace(
            hour=self.hora_inicio.hour,
            minute=self.hora_inicio.minute,
            second=0,
            microsecond=0,
        )
        if inicio > ahora:
            inicio -= timedelta(days=1)
        return inicio

    def fin_de_sesion(self, ahora):
        return self.inicio_de_sesion(ahora) + timedelta(minutes=self.duracion)

    def se_cruza_con(self, otro):
        return otro.esta_abierto(self.hora_inicio) or self.esta_abierto(otro.hora_inicio)


class Asistencia(models.Model):
    ESTADOS = [
        ('presente', 'Presente'),
        ('tardanza', 'Tardanza'),
    ]

    nombre = models.CharField(max_length=100)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='presente')
    horario = models.ForeignKey(
        Horario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='asistencias',
    )

    def __str__(self):
        return self.nombre
