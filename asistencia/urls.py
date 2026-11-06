from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('video_feed/', views.video_feed, name='video_feed'),
]