"""
Lista las cámaras del sistema y mide el FPS real de cada índice.

Sirve para identificar la ELP AR0234 ("Global Shutter Camera") frente a la
webcam interna de la laptop y cámaras virtuales (OBS). La ELP es la que da
FPS_real alto (>50) a 1920x1080: significa que negoció MJPEG.

Uso:
    python scripts/detectar_camaras.py

Normalmente NO hace falta fijar nada: el servicio autodetecta la ELP por el
nombre del dispositivo. Si la autodetección falla, fijar en .env:
    CAM_INDICE=1                (índice fijo)
    CAM_INDICE=Global Shutter   (coincidencia por nombre)
"""
import os
import time

os.environ.setdefault("OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS", "0")

import cv2

ANCHO, ALTO, FPS = 1920, 1080, 90
# Media Foundation primero: es el backend que negocia MJPEG con la ELP.
BACKENDS = [("MSMF", cv2.CAP_MSMF), ("ANY", cv2.CAP_ANY), ("DSHOW", cv2.CAP_DSHOW)]


def nombres_directshow() -> list[str]:
    try:
        from pygrabber.dshow_graph import FilterGraph
        return FilterGraph().get_input_devices()
    except Exception as e:
        print(f"(pygrabber no disponible: {e})")
        return []


def medir(cap: cv2.VideoCapture, n: int = 60) -> float:
    t0 = time.monotonic()
    leidos = sum(1 for _ in range(n) if cap.read()[0])
    return leidos / max(time.monotonic() - t0, 1e-6)


def probar(idx: int, nombre: str) -> None:
    for bk_nombre, bk in BACKENDS:
        cap = cv2.VideoCapture(idx, bk)
        if not cap.isOpened():
            cap.release()
            continue
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, ANCHO)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, ALTO)
        cap.set(cv2.CAP_PROP_FPS, FPS)
        ret, frame = cap.read()
        if not ret or frame is None:
            print(f"  [{idx}] {nombre} ({bk_nombre}): abre pero no entrega frames")
            cap.release()
            continue
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps_real = medir(cap)
        marca = "  <-- MJPEG" if fps_real > 50 else "  (sin comprimir / YUY2)"
        print(f"  [{idx}] {nombre} ({bk_nombre}): {w}x{h}  FPS_real={fps_real:.0f}{marca}")
        cap.release()
        return
    print(f"  [{idx}] {nombre}: no abre con ningún backend")


if __name__ == "__main__":
    nombres = nombres_directshow()
    print("Dispositivos DirectShow:")
    for i, n in enumerate(nombres):
        print(f"  {i}: {n}")

    print(f"\nProbando cada índice a {ANCHO}x{ALTO}:")
    for i in range(max(len(nombres), 6)):
        probar(i, nombres[i] if i < len(nombres) else "(sin nombre)")

    print("\nLa ELP es la que da FPS_real alto (>50). Si la autodetección por nombre")
    print("no la agarra, fijá CAM_INDICE en .env con ese índice.")
