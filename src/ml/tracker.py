"""
CoffeeRen - Módulo de Tracking en Tiempo Real
Detecta y trackea granos de café usando ByteTrack.
Cada grano recibe un ID único para contar defectos sin duplicados.
"""

import cv2
import threading
import time
from collections import defaultdict
from ultralytics import YOLO
import os

# Configuración de cámara
CAMARA_WIDTH    = 1280  # Resolución operativa
CAMARA_HEIGHT   = 720
CAMARA_FPS      = 60    # FPS de procesamiento

# Clases del modelo YOLO
CLASES = [
    "agrio_ligero", "agrio_severo", "averanado", "blanco",
    "broca_severo", "broca_ligero", "cascarilla_cereza_seca",
    "cascarilla_pergamino", "cereza_seca", "concha", "deforme",
    "inmaduro", "negro", "partido_maquina", "partido_mitad",
    "pergamino", "verde"
]

# Colores por clase (BGR): Rojo para defectos, Verde para descritos como buenos
# En SCA, todos los detectados son defectos (rojo)
COLORES_DEFECTOS = {cls: (0, 0, 255) for cls in CLASES}  # Rojo para todos (defectos)


class CoffeeRenTracker:
    def __init__(self, conf: float, model_name: str = "yolov8n"):
        """
        Inicializa el tracker de granos de café.

        Args:
            conf: Umbral de confianza para detecciones (0.0 - 1.0) — requerido
            model_name: Nombre del modelo YOLO a usar (yolov8n, yolo26n, yolo11n)
        """
        self.conf = conf
        self.model_name = model_name

        # Cargar modelo YOLO con fallback a yolov8n
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(BASE_DIR, "models", model_name, "best.pt")

        # Si el modelo pedido no existe, usar yolov8n como fallback
        if not os.path.exists(model_path):
            print(f"⚠️  Modelo no encontrado: {model_name}")
            fallback_model = "yolov8n"
            fallback_path = os.path.join(BASE_DIR, "models", fallback_model, "best.pt")

            if os.path.exists(fallback_path):
                print(f"📦 Usando fallback: {fallback_model}")
                model_path = fallback_path
                self.model_name = fallback_model
            else:
                raise FileNotFoundError(
                    f"Ningún modelo disponible:\n"
                    f"  - Primario: {model_name} → no encontrado\n"
                    f"  - Fallback: {fallback_model} → no encontrado\n"
                    f"Descarga best.pt desde Google Drive a models/yolov8n/"
                )

        self.model = YOLO(model_path)
        print(f"✅ Modelo YOLO cargado: {self.model_name} (conf={conf})")

        # Estado del tracking
        self.conteo_ids = defaultdict(set)        # {clase: {id1, id2, ...}}
        self.ultimo_frame_anotado: bytes | None = None
        self.lock = threading.Lock()

        # Estadísticas
        self.fps_actual = 0.0

    def procesar_frame(self, frame) -> bytes | None:
        """
        Procesa un frame con ByteTrack y retorna JPEG anotado.

        Args:
            frame: Frame BGR de OpenCV (1280x720 @ 60fps)

        Returns:
            bytes: Frame codificado en JPEG con anotaciones, o None si error
        """
        if frame is None:
            return None

        # Tracking con ByteTrack
        try:
            results = self.model.track(
                source=frame,
                conf=self.conf,
                imgsz=1280,  # Mayor resolución para detectar granos pequeños
                tracker="bytetrack.yaml",
                persist=True,
                verbose=False
            )
        except Exception as e:
            print(f"⚠️  Error en tracking: {e}")
            return None

        result = results[0]
        frame_anotado = frame.copy()

        detecciones_count = 0
        # Procesar detecciones con IDs
        if result.boxes is not None and len(result.boxes) > 0:
            if result.boxes.id is not None:
                for box in result.boxes:
                    detecciones_count += 1
                    track_id = int(box.id[0])
                    clase_idx = int(box.cls[0])
                    clase = CLASES[clase_idx] if clase_idx < len(CLASES) else "desconocido"
                    conf_score = float(box.conf[0])
                    x1, y1, x2, y2 = map(int, box.xyxy[0])

                    # Registrar ID único por clase
                    with self.lock:
                        self.conteo_ids[clase].add(track_id)

                    # Color: ROJO para defectos (todos los detectados son defectos)
                    color = COLORES_DEFECTOS.get(clase, (0, 0, 255))

                    # Dibujar bounding box
                    cv2.rectangle(frame_anotado, (x1, y1), (x2, y2), color, 3)

                    # Etiqueta: ID, nombre del defecto, confianza
                    label = f"#{track_id} {clase} {conf_score:.2%}"
                    (tw, th), _ = cv2.getTextSize(
                        label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2
                    )

                    # Fondo blanco para texto legible
                    cv2.rectangle(
                        frame_anotado,
                        (x1, y1 - th - 8),
                        (x1 + tw + 4, y1 - 2),
                        color, -1
                    )

                    # Texto en blanco
                    cv2.putText(
                        frame_anotado, label,
                        (x1 + 2, y1 - 4),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (255, 255, 255), 2
                    )

        # Estadísticas en esquina superior izquierda
        total_granos = sum(len(ids) for ids in self.conteo_ids.values())
        stats_text = f"Granos: {total_granos} | FPS: {self.fps_actual:.1f} | Detecciones: {detecciones_count}"
        cv2.putText(
            frame_anotado, stats_text,
            (15, 35),
            cv2.FONT_HERSHEY_SIMPLEX, 0.8,
            (0, 255, 255), 2
        )

        # Log de debug - mostrar siempre si no hay detecciones
        if total_granos > 0 and detecciones_count > 0:
            conteo_por_clase = {cls: len(ids) for cls, ids in self.conteo_ids.items() if len(ids) > 0}
            print(f"🎯 Detecciones: {detecciones_count} | Total únicos: {total_granos} | {conteo_por_clase}")
        elif detecciones_count == 0:
            print(f"⚠️  Frame procesado sin detecciones (boxes: {len(result.boxes) if result.boxes is not None else 0})")

        # Codificar frame anotado a JPEG
        try:
            _, buffer = cv2.imencode(".jpg", frame_anotado, [
                cv2.IMWRITE_JPEG_QUALITY, 85
            ])
            return buffer.tobytes()
        except Exception as e:
            print(f"⚠️  Error codificando JPEG: {e}")
            return None

    def resetear_conteo(self) -> None:
        """Resetea el conteo de IDs para un nuevo lote."""
        with self.lock:
            self.conteo_ids = defaultdict(set)

    def obtener_conteo(self) -> dict[str, int]:
        """
        Retorna el conteo actual de granos únicos por clase.

        Returns:
            dict: {clase: cantidad_granos_unicos}
        """
        with self.lock:
            return {clase: len(ids) for clase, ids in self.conteo_ids.items()}

    def obtener_frame_jpeg(self) -> bytes | None:
        """Retorna el último frame anotado en JPEG (para streaming)."""
        with self.lock:
            return self.ultimo_frame_anotado

    def _actualizar_fps(self, t_anterior: float) -> float:
        """Actualiza el FPS y retorna el nuevo tiempo anterior."""
        t_actual = time.time()
        delta = t_actual - t_anterior
        if delta > 0:
            self.fps_actual = 1.0 / delta
        return t_actual
