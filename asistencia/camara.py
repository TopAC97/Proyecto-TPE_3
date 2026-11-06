import cv2

class Camara:
    def __init__(self, indice=0):
        self.video = cv2.VideoCapture(indice)

    def obtener_frame(self):
        ok, frame = self.video.read()
        return frame if ok else None

    def liberar(self):
        if self.video.isOpened():
            self.video.release()