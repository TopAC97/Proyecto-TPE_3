import cv2
import os
import numpy as np

carpeta = "asistencia"

reconocedor = cv2.face.LBPHFaceRecognizer_create()
reconocedor.read(os.path.join(carpeta, "modelo_rostros.yml"))

nombres = np.load(
    os.path.join(carpeta, "nombres.npy"),
    allow_pickle=True
).item()

detector = cv2.CascadeClassifier(
    os.path.join(carpeta, "haarcascade_frontalface_default.xml")
)

camara = cv2.VideoCapture(0)

print("Mira a la camara. Presiona Q para salir.")

while True:
    ok, frame = camara.read()

    if not ok:
        break

    gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rostros = detector.detectMultiScale(gris, 1.3, 5)

    for (x, y, w, h) in rostros:
        rostro = gris[y:y+h, x:x+w]
        rostro = cv2.resize(rostro, (200, 200))

        etiqueta, confianza = reconocedor.predict(rostro)

        if confianza < 80 and etiqueta in nombres:
            nombre = nombres[etiqueta]
            color = (0, 255, 0)
        else:
            nombre = "Desconocido"
            color = (0, 0, 255)

        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)

        cv2.putText(
            frame,
            nombre,
            (x, y-10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            color,
            2
        )

    cv2.imshow("Reconocimiento facial", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camara.release()
cv2.destroyAllWindows()
