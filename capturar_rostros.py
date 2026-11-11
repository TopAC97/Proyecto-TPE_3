import cv2
import os

nombre = input("Escribe el nombre del estudiante: ")

carpeta = os.path.join("asistencia", "rostros", nombre)
os.makedirs(carpeta, exist_ok=True)

ruta_cascada = os.path.join(
    "asistencia",
    "haarcascade_frontalface_default.xml"
)

detector = cv2.CascadeClassifier(ruta_cascada)
camara = cv2.VideoCapture(0)

contador = 0
fotograma = 0

print("Mira a la cámara. Presiona Q para terminar.")

while True:
    ok, frame = camara.read()

    if not ok:
        print("No se pudo abrir la cámara.")
        break

    gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rostros = detector.detectMultiScale(gris, 1.3, 5)

    for (x, y, w, h) in rostros:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        fotograma += 1

        if fotograma % 5 == 0 and contador < 30:
            rostro = gris[y:y+h, x:x+w]
            rostro = cv2.resize(rostro, (200, 200))

            contador += 1
            archivo = os.path.join(carpeta, f"{contador}.jpg")
            cv2.imwrite(archivo, rostro)

    cv2.putText(
        frame,
        f"Fotos guardadas: {contador}/30",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2
    )

    cv2.imshow("Registro de rostros", frame)

    if contador >= 30 or cv2.waitKey(1) & 0xFF == ord('q'):
        break

camara.release()
cv2.destroyAllWindows()

print(f"Se guardaron {contador} fotografias.")
