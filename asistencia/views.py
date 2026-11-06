# Create your views here.
import cv2
from django.shortcuts import render
from django.http import StreamingHttpResponse
from .camara import Camara

def generar_frames():
    camara = Camara()
    try:
        while True:
            frame = camara.obtener_frame()
            if frame is None:
                break
            ok, jpg = cv2.imencode('.jpg', frame)
            if not ok:
                continue
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n'
                   + jpg.tobytes() + b'\r\n')
    finally:
        camara.liberar()

def video_feed(request):
    return StreamingHttpResponse(
        generar_frames(),
        content_type='multipart/x-mixed-replace; boundary=frame'
    )

def inicio(request):
    return render(request, 'asistencia/inicio.html')
