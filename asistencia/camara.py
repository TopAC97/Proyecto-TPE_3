import cv2
import os
import numpy as np

class Camara:
    def __init__(self, indice=0):
        self.video = cv2.VideoCapture(indice)
        self.ultimo_reconocido = None

        carpeta = os.path.dirname(__file__)

        ruta_cascada = os.path.join(
            carpeta,
            'haarcascade_frontalface_default.xml'
        )

        self.detector = cv2.CascadeClassifier(ruta_cascada)

        self.reconocedor = cv2.face.LBPHFaceRecognizer_create()

        self.reconocedor.read(
            os.path.join(carpeta, 'modelo_rostros.yml')
        )

        self.nombres = np.load(
            os.path.join(carpeta, 'nombres.npy'),
            allow_pickle=True
        ).item()

    def obtener_frame(self):
        ok, frame = self.video.read()

        if not ok:
            return None

        gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        rostros = self.detector.detectMultiScale(
            gris, 1.3, 5
        )
        self.ultimo_reconocido = None

        for (x, y, w, h) in rostros:
            rostro = gris[y:y+h, x:x+w]
            rostro = cv2.resize(rostro, (200, 200))

            etiqueta, confianza = self.reconocedor.predict(rostro)

            if confianza < 50 and etiqueta in self.nombres:
                nombre = self.nombres[etiqueta]
                color = (0, 255, 0)
                self.ultimo_reconocido = nombre
            else:
                nombre = 'Desconocido'
                color = (0, 0, 255)

            cv2.rectangle(
                frame,
                (x, y),
                (x+w, y+h),
                color,
                2
            )

            cv2.putText(
                frame,
                nombre,
                (x, y-10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                color,
                2
            )

        return frame

    def liberar(self):
        if self.video.isOpened():
            self.video.release()
