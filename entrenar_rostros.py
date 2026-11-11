import cv2
import os
import numpy as np

carpeta_principal = os.path.join("asistencia", "rostros")

rostros = []
etiquetas = []

etiqueta = 0
nombres = {}

for nombre in os.listdir(carpeta_principal):
    carpeta = os.path.join(carpeta_principal, nombre)

    if not os.path.isdir(carpeta):
        continue

    nombres[etiqueta] = nombre

    for archivo in os.listdir(carpeta):
        if archivo.endswith(".jpg"):
            ruta = os.path.join(carpeta, archivo)

            imagen = cv2.imread(ruta, cv2.IMREAD_GRAYSCALE)

            if imagen is not None:
                rostros.append(imagen)
                etiquetas.append(etiqueta)

    etiqueta += 1

if len(rostros) == 0:
    print("No hay fotografias para entrenar.")
else:
    reconocedor = cv2.face.LBPHFaceRecognizer_create()

    reconocedor.train(
        rostros,
        np.array(etiquetas)
    )

    reconocedor.save(
        os.path.join("asistencia", "modelo_rostros.yml")
    )

    np.save(
        os.path.join("asistencia", "nombres.npy"),
        nombres
    )

    print("¡Entrenamiento completado!")
    print("Personas registradas:", nombres)
    print("Fotografias utilizadas:", len(rostros))
