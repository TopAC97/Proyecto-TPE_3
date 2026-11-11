from django.contrib import admin

from .models import Asistencia, Horario

admin.site.register(Horario)
admin.site.register(Asistencia)
