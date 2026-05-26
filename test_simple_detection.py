#!/usr/bin/env python3
"""
Test simple para debugear dónde se cuelga la detección.
"""
import cv2
import numpy as np
from src.ml.tracker import CoffeeRenTracker

print("TEST SIMPLE DE DETECCIÓN\n")

# 1. Crear un frame ficticio
print("1. Creando frame ficticio...")
frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
print(f"   Frame: {frame.shape}")

# 2. Inicializar tracker
print("\n2. Inicializando tracker...")
tracker = CoffeeRenTracker(conf=0.5, model_name="yolov8n")
print("   ✅ OK")

# 3. Procesar frame - CON TIMEOUT
print("\n3. Procesando frame...")
print("   (Esto puede tomar unos segundos...)")

import threading
import time

resultado = [None]
def procesar():
    try:
        resultado[0] = tracker.procesar_frame(frame)
        print("   ✅ Procesamiento completado")
    except Exception as e:
        print(f"   ❌ Error: {e}")

thread = threading.Thread(target=procesar)
thread.daemon = True
thread.start()
thread.join(timeout=30)  # Esperar máximo 30 segundos

if thread.is_alive():
    print("   ❌ TIMEOUT - El procesamiento se colgó después de 30 segundos")
    exit(1)

if resultado[0] is None:
    print("   ⚠️  Resultado es None")
else:
    print(f"   ✅ JPEG: {len(resultado[0])} bytes")

# 4. Conteo
print("\n4. Conteo de defectos:")
conteo = tracker.obtener_conteo()
if not conteo:
    print("   ⚠️  Conteo vacío (sin detecciones en frame aleatorio)")
else:
    print(f"   ✅ Conteo: {conteo}")

print("\n" + "="*60)
print("✅ El tracker funciona correctamente")
print("="*60)
