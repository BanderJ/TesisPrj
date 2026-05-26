"""
CamaraSimulada - Generador de frames de prueba para desarrollo sin cámara física.
Simula granos de café (círculos) en la pantalla para testear el pipeline YOLO.
"""

import threading
import cv2
import numpy as np
import random


class CamaraSimulada:
    """
    Simula una cámara capturando granos de café.
    Genera frames con círculos (granos) en posiciones aleatorias.
    """

    def __init__(self) -> None:
        self._latest_jpeg: bytes | None = None
        self._frame_lock = threading.Lock()
        self._new_frame = threading.Event()
        self._running = False
        self._thread: threading.Thread | None = None

    def _capture_loop(self) -> None:
        """Loop de generación de frames simulados."""
        while self._running:
            # Crear frame vacío (café marrón oscuro)
            frame = np.ones((720, 1280, 3), dtype=np.uint8) * 60

            # Dibujar granos simulados (círculos aleatorios)
            num_granos = random.randint(5, 15)
            for _ in range(num_granos):
                x = random.randint(100, 1180)
                y = random.randint(100, 620)
                radio = random.randint(20, 40)
                # Colores variados para simular defectos diferentes
                color_idx = random.randint(0, 5)
                colores = [
                    (50, 50, 50),      # Negro
                    (100, 100, 200),   # Rojo
                    (0, 165, 255),     # Naranja
                    (200, 150, 100),   # Azul claro
                    (100, 200, 200),   # Amarillo
                    (150, 150, 150),   # Gris
                ]
                color = colores[color_idx]
                cv2.circle(frame, (x, y), radio, color, -1)

            # Codificar a JPEG
            _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
            jpeg = buf.tobytes()

            with self._frame_lock:
                self._latest_jpeg = jpeg
            self._new_frame.set()

            # ~60fps (16ms por frame)
            threading.Event().wait(0.016)

    def iniciar(self) -> bool:
        """Inicia la generación de frames simulados."""
        if self._running:
            return True
        self._running = True
        self._thread = threading.Thread(
            target=self._capture_loop, daemon=True, name="camara-simulada"
        )
        self._thread.start()
        print("✅ Cámara simulada iniciada (frames de prueba)")
        return True

    def cerrar(self) -> None:
        """Detiene la generación de frames."""
        self._running = False
        self._new_frame.set()
        if self._thread:
            self._thread.join(timeout=2)
            self._thread = None

    def esta_disponible(self) -> bool:
        return self._running

    def esperar_frame(self, timeout: float = 1.0) -> bytes | None:
        """Bloquea hasta que haya un frame nuevo o expire el timeout."""
        self._new_frame.wait(timeout)
        self._new_frame.clear()
        with self._frame_lock:
            return self._latest_jpeg


camara_simulada = CamaraSimulada()
