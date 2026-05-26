#!/usr/bin/env python3
"""
Test para verificar si el modelo YOLO está detectando correctamente.
"""
import cv2
from src.ml.tracker import CoffeeRenTracker

print("="*70)
print("TEST: VERIFICAR DETECCIÓN YOLO")
print("="*70)

try:
    # Inicializar tracker
    print("\n1️⃣  Inicializando tracker...")
    tracker = CoffeeRenTracker(conf=0.5, model_name="yolov8n")
    print("   ✅ Tracker inicializado")

    # Obtener un frame de la cámara
    print("\n2️⃣  Capturando frame de la cámara...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("   ❌ No se pudo abrir la cámara")
        exit(1)

    ret, frame = cap.read()
    cap.release()

    if not ret or frame is None:
        print("   ❌ No se pudo capturar frame")
        exit(1)
    print(f"   ✅ Frame capturado: {frame.shape}")

    # Procesar frame
    print("\n3️⃣  Procesando frame con YOLO...")
    resultado_jpeg = tracker.procesar_frame(frame)

    if resultado_jpeg is None:
        print("   ❌ procesar_frame retornó None")
    else:
        print(f"   ✅ Frame procesado: {len(resultado_jpeg)} bytes JPEG")

    # Obtener conteo
    print("\n4️⃣  Obteniendo conteo de defectos...")
    conteo = tracker.obtener_conteo()

    if not conteo:
        print("   ⚠️  Conteo vacío - el modelo NO detectó defectos")
    else:
        print(f"   ✅ Conteo: {conteo}")
        total = sum(conteo.values())
        print(f"   Total granos únicos: {total}")

    print("\n" + "="*70)
    if not conteo:
        print("❌ PROBLEMA: El modelo no está detectando defectos")
        print("   Causas posibles:")
        print("   - Modelo no entrenado para los defectos")
        print("   - Threshold de confianza muy alto")
        print("   - Imagen de prueba no tiene defectos visibles")
    else:
        print("✅ El modelo SÍ está detectando defectos correctamente")
    print("="*70)

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
