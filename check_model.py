#!/usr/bin/env python3
"""Diagnóstico rápido del modelo YOLO activo.

Carga el modelo que usa el tracker (yolov26n_2cls) y muestra sus clases.
Prefiere best.onnx sobre best.pt, igual que src/ml/tracker.py.

Uso:
    python check_model.py [nombre_modelo]
"""
import os
import sys

from ultralytics import YOLO

MODELO_POR_DEFECTO = "yolov26n_2cls"
BASE_DIR = os.path.join("src", "ml", "models")


def resolver_modelo(model_name: str) -> str | None:
    """Retorna la ruta al peso preferiendo ONNX sobre .pt; None si no hay ninguno."""
    for nombre in ("best.onnx", "best.pt"):
        ruta = os.path.join(BASE_DIR, model_name, nombre)
        if os.path.exists(ruta):
            return ruta
    return None


def main() -> int:
    model_name = sys.argv[1] if len(sys.argv) > 1 else MODELO_POR_DEFECTO
    print(f"Verificando modelo YOLO: {model_name}\n")

    model_path = resolver_modelo(model_name)
    if model_path is None:
        print(f"No se encontró best.onnx ni best.pt en {BASE_DIR}/{model_name}/")
        carpeta = os.path.join(BASE_DIR, model_name)
        if os.path.isdir(carpeta):
            print("Contenido de la carpeta:")
            for item in sorted(os.listdir(carpeta)):
                print(f"  - {item}")
        else:
            print(f"La carpeta {carpeta} no existe. Descarga el modelo desde Google Drive.")
        return 1

    print(f"Peso encontrado: {model_path}")
    try:
        print("Cargando modelo...")
        model = YOLO(model_path)
        print("Modelo cargado correctamente\n")
        print(f"  Nombres de clases: {model.names}")
        print(f"  Cantidad de clases: {len(model.names)}")
        return 0
    except Exception as e:
        print(f"Error cargando modelo: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
