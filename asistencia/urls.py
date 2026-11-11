from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('video_feed/', views.video_feed, name='video_feed'),
    path('asistencias/', views.lista_asistencias, name='lista_asistencias'),
    path('obtener_asistencias/', views.obtener_asistencias, name='obtener_asistencias'),
    path('horarios/', views.horarios, name='horarios'),
    path('horarios/<int:pk>/editar/', views.horarios, name='editar_horario'),
    path('horarios/<int:pk>/eliminar/', views.eliminar_horario, name='eliminar_horario'),
]
