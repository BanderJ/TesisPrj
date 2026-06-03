"""
TrackerService - Integración de Captura + Procesamiento ML
Coordina CamaraService (captura de frames) con CoffeeRenTracker (procesamiento YOLO).
"""

import threading
import time
import cv2
import numpy as np

from src.services.camara_service import camara_service
from src.ml.tracker import CoffeeRenTracker
from src.ml.classifier import generar_reporte
from src.utilities.arduino_serial import arduino_serial
from src.utilities.servo_controller import servo_controller

# Umbral de confianza global para todas las detecciones YOLO
# Bajado a 0.20 para production: mejor recall en agrio (0.61) y partido (0.50)
# Preferir falsos positivos sobre granos defectuosos no detectados
CONF_THRESHOLD = 0.50


class TrackerService:
    """
    Servicio que gestiona la captura de video y procesamiento de defectos en tiempo real.
    - Captura frames desde CamaraService (1280x720 @ 60fps)
    - Procesa con CoffeeRenTracker (YOLO + ByteTrack)
    - Calcula grado con classifier.py (SCA)
    """

    def __init__(self, model_name: str = "yolov8n"):
        self.model_name = model_name
        self.conf = CONF_THRESHOLD

        # Inicializar tracker YOLO con umbral de confianza centralizado
        self.tracker = CoffeeRenTracker(conf=CONF_THRESHOLD, model_name=model_name)

        # Estado
        self.activo = False
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()

        # Último frame anotado (JPEG)
        self._frame_anotado: bytes | None = None

        # Estado de error por desconexión de cámara
        self._camara_desconectada: bool = False
        self._error_camara: str | None = None

    def iniciar(self) -> bool:
        """
        Inicia la captura y procesamiento.

        Returns:
            bool: True si inició exitosamente, False si error
        """
        with self._lock:
            if self.activo:
                return True

            # Limpiar estado de error previo al reiniciar
            self._camara_desconectada = False
            self._error_camara = None
            servo_controller.desbloquear()

            # Iniciar captura desde cámara
            print(f"📷 Iniciando CamaraService...")
            if not camara_service.iniciar():
                print("No se pudo iniciar la cámara")
                return False

            # Esperar a que la cámara esté lista
            time.sleep(1)
            if not camara_service.esta_disponible():
                print("Cámara no está disponible después de esperar")
                return False

            print("Cámara disponible")

            # Iniciar hilo de procesamiento
            self.activo = True
            self._thread = threading.Thread(
                target=self._loop_procesamiento,
                daemon=True,
                name="tracker-processing"
            )
            self._thread.start()
            print(f"TrackerService iniciado (modelo: {self.model_name})")
            return True

    def detener(self) -> None:
        """Detiene la captura y procesamiento."""
        with self._lock:
            self.activo = False

        if self._thread:
            self._thread.join(timeout=2.0)
            self._thread = None

        camara_service.cerrar()
        self.tracker.resetear_conteo()
        print("⏹️  TrackerService detenido - cámara liberada")

    def _on_camara_desconectada(self) -> None:
        """Reacción de emergencia ante pérdida de cámara."""
        self.activo = False
        self._camara_desconectada = True
        self._error_camara = "Desconexión con cámara. La clasificación se ha detenido."
        servo_controller.bloquear()
        arduino_serial.enviar_comando("SERVO:DEFECTO")
        print("⚠️  Cámara desconectada — servo fijado en posición DEFECTO")

    def _loop_procesamiento(self) -> None:
        """Loop principal de procesamiento (corre en hilo separado)."""
        t_anterior = time.time()
        frame_count = 0

        while self.activo:
            # Detectar desconexión de cámara
            if not camara_service.esta_disponible():
                self._on_camara_desconectada()
                break

            # Obtener frame desde CamaraService
            jpeg_bytes = camara_service.esperar_frame(timeout=1.0)
            if jpeg_bytes is None:
                continue

            # Decodificar JPEG a frame OpenCV
            frame = self._jpeg_a_frame(jpeg_bytes)
            if frame is None:
                continue

            # Procesar con tracker
            frame_anotado_jpeg = self.tracker.procesar_frame(frame)

            if frame_anotado_jpeg is not None:
                frame_count += 1
                if frame_count % 30 == 0:  # Log cada 30 frames (~1 vez por segundo a 30fps)
                    print(f"TrackerService: procesados {frame_count} frames")
                with self._lock:
                    self._frame_anotado = frame_anotado_jpeg
                    # Actualizar FPS
                    self.tracker._actualizar_fps(t_anterior)
                    t_anterior = time.time()
            else:
                print("Tracker retornó None para frame_anotado_jpeg")

    def obtener_frame_streaming(self) -> bytes | None:
        """
        Retorna el último frame anotado en JPEG (para MJPEG streaming).
        Retorna inmediatamente sin bloquear.

        Returns:
            bytes: JPEG codificado, o None si no hay frame disponible
        """
        with self._lock:
            return self._frame_anotado

    def obtener_conteo_actual(self) -> dict[str, int]:
        return self.tracker.obtener_conteo()

    def obtener_conteo_enriquecido(self) -> dict:
        conteo = self.obtener_conteo_actual()
        eq = self.tracker.EQUIVALENCIAS_DEFECTO
        total_defectos = sum(v for k, v in conteo.items() if eq.get(k, 0.0) > 0.0)
        total_sanos    = sum(v for k, v in conteo.items() if eq.get(k, 0.0) == 0.0)
        conteo_agrupado = {
            grupo: sum(conteo.get(c, 0) for c in clases)
            for grupo, clases in self.tracker.GRUPOS_DISPLAY.items()
        }
        return {
            "conteo":           conteo,
            "total_granos":     total_defectos + total_sanos,
            "total_defectos":   total_defectos,
            "total_sanos":      total_sanos,
            "conteo_agrupado":  conteo_agrupado,
            "clases_detectadas": len(conteo),
        }

    def generar_reporte_lote(self) -> dict:
        """
        Genera reporte de clasificación del lote actual.

        Returns:
            dict: {grado, defectos, apto_specialty, detalles_por_clase, ...}
        """
        conteo = self.obtener_conteo_actual()
        return generar_reporte(conteo, self.tracker.EQUIVALENCIAS_DEFECTO)

    def resetear_lote(self) -> None:
        """Resetea el conteo para iniciar análisis de un nuevo lote."""
        self.tracker.resetear_conteo()
        print("Lote reseteado")

    def esta_activo(self) -> bool:
        """Verifica si el servicio está activo."""
        return self.activo and camara_service.esta_disponible()

    def obtener_estado_error(self) -> dict:
        """Retorna el estado de error de cámara para el frontend."""
        return {
            "camara_desconectada": self._camara_desconectada,
            "error": self._error_camara,
        }

    @staticmethod
    def _jpeg_a_frame(jpeg_bytes: bytes) -> np.ndarray | None:
        """
        Decodifica JPEG a frame OpenCV BGR.

        Args:
            jpeg_bytes: Bytes JPEG

        Returns:
            np.ndarray: Frame BGR, o None si error
        """
        try:
            nparr = np.frombuffer(jpeg_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return frame
        except Exception as e:
            print(f"Error decodificando JPEG: {e}")
            return None


# Instancia global del servicio
tracker_service = TrackerService(model_name="yolov26n_2cls")
