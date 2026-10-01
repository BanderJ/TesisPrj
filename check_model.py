#!/usr/bin/env python3
"""Diagnóstico rápido del modelo YOLO activo.

Carga el modelo que usa el tracker (yolov26n_2cls) con la misma regla que
src/ml/tracker.py: con GPU CUDA prefiere best.pt (PyTorch nativo, FP16 si la
GPU lo soporta); sin GPU prefiere best.onnx. Muestra el dispositivo y las clases.

Uso:
    python check_model.py [nombre_modelo]
"""
import os
import sys

import torch
from ultralytics import YOLO

MODELO_POR_DEFECTO = "yolov26n_2cls"
BASE_DIR = os.path.join("src", "ml", "models")
CLASES_ESPERADAS = {0: "defecto", 1: "verde"}


def resolver_modelo(model_name: str, prefer_pt: bool) -> str | None:
    """Ruta al peso según el hardware (mismo orden que el tracker); None si no hay ninguno."""
    orden = ("best.pt", "best.onnx") if prefer_pt else ("best.onnx", "best.pt")
    for nombre in orden:
        ruta = os.path.join(BASE_DIR, model_name, nombre)
        if os.path.exists(ruta):
            return ruta
    return None


def main() -> int:
    model_name = sys.argv[1] if len(sys.argv) > 1 else MODELO_POR_DEFECTO
    print(f"Verificando modelo YOLO: {model_name}\n")

    cuda_ok = torch.cuda.is_available()
    print(f"PyTorch: {torch.__version__}  CUDA disponible: {cuda_ok}")
    if cuda_ok:
        cap = torch.cuda.get_device_capability(0)
        print(f"GPU: {torch.cuda.get_device_name(0)} (compute capability {cap[0]}.{cap[1]})")
    elif torch.__version__.endswith("+cpu"):
        print("ADVERTENCIA: torch es la variante solo-CPU. Ver requirements.txt para instalar la variante CUDA.")

    model_path = resolver_modelo(model_name, prefer_pt=cuda_ok)
    if model_path is None:
        print(f"No se encontró best.pt ni best.onnx en {BASE_DIR}/{model_name}/")
        carpeta = os.path.join(BASE_DIR, model_name)
        if os.path.isdir(carpeta):
            print("Contenido de la carpeta:")
            for item in sorted(os.listdir(carpeta)):
                print(f"  - {item}")
        else:
            print(f"La carpeta {carpeta} no existe. Descarga el modelo desde Google Drive.")
        return 1

    half = bool(cuda_ok and torch.cuda.get_device_capability(0)[0] >= 7 and model_path.endswith(".pt"))
    print(f"Peso que usará el tracker: {model_path}  (device={'0' if cuda_ok else 'cpu'}, half={half})")
    if cuda_ok and model_path.endswith(".onnx"):
        print("AVISO: hay GPU pero falta best.pt; se usará el .onnx en CPU/FP32. Descarga best.pt de Google Drive.")

    try:
        print("Cargando modelo...")
        model = YOLO(model_path)
        print("Modelo cargado correctamente\n")
        print(f"  Nombres de clases: {model.names}")
        print(f"  Cantidad de clases: {len(model.names)}")
        if dict(model.names) != CLASES_ESPERADAS:
            print(f"ERROR: el orden de clases debe ser {CLASES_ESPERADAS} (ver constants.py).")
            return 1
        return 0
    except Exception as e:
        print(f"Error cargando modelo: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
