#!/usr/bin/env python3
import os
from ultralytics import YOLO

print("Verificando modelo YOLO...\n")

# Ruta del modelo
model_path = "src/ml/models/yolov8n/best.pt"

print(f"Buscando modelo en: {model_path}")
if os.path.exists(model_path):
    print("Archivo encontrado")

    try:
        print("\nCargando modelo...")
        model = YOLO(model_path)
        print("Modelo cargado correctamente")

        print(f"\nInfo del modelo:")
        print(f"  Modelo: {model.model_name}")
        print(f"  Nombres de clases: {model.names}")
        print(f"  Cantidad de clases: {len(model.names)}")

    except Exception as e:
        print(f"Error cargando modelo: {e}")
else:
    print(f"Archivo NO encontrado")
    print(f"\nArchivos en src/ml/models/:")
    for item in os.listdir("src/ml/models/"):
        print(f"  - {item}")
