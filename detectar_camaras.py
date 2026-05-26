"""
Script para detectar cámaras disponibles en el sistema Windows.
Prueba diferentes índices y backends.
"""
import cv2

print("🔍 Detectando cámaras disponibles...\n")

# Probar con CAP_DSHOW (DirectShow - Windows)
print("=== Probando con CAP_DSHOW (DirectShow) ===")
for idx in range(5):
    cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
    if cap.isOpened():
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        print(f"✅ Cámara encontrada en índice {idx}: {w}x{h} @ {fps}fps")

        # Intentar leer frame
        ret, frame = cap.read()
        if ret:
            print(f"   ✅ Frame leído correctamente ({frame.shape})")
        else:
            print(f"   ❌ No se pudo leer frame")
        cap.release()
    else:
        print(f"❌ Índice {idx}: sin dispositivo")

print("\n=== Probando con CAP_ANY (automático) ===")
for idx in range(5):
    cap = cv2.VideoCapture(idx)
    if cap.isOpened():
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        print(f"✅ Cámara encontrada en índice {idx}: {w}x{h} @ {fps}fps")
        cap.release()
    else:
        print(f"❌ Índice {idx}: sin dispositivo")

print("\n✅ Detección completada. Usa el índice encontrado arriba.")
