"""
CoffeeRen - Módulo de Tracking en Tiempo Real
Detecta y trackea granos de café usando ByteTrack.
Cada grano recibe un ID único para contar defectos sin duplicados.
"""

import cv2
import threading
import time
import importlib.util
from collections import defaultdict
from ultralytics import YOLO
import os
import sys

from src.utilities.servo_controller import servo_controller

# Configuración de cámara
CAMARA_WIDTH    = 1280  # Resolución operativa
CAMARA_HEIGHT   = 720
CAMARA_FPS      = 60    # FPS de procesamiento


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

        # Cargar constantes (CLASES, COLORES, EQUIVALENCIAS) específicas del modelo
        self._cargar_constantes_modelo()

        # Estado del tracking
        self.conteo_ids_confianza = defaultdict(list)  # {track_id: [(clase, conf), ...]}
        self._ids_servados: set[int] = set()           # track_ids ya enviados al servo
        self.lock = threading.Lock()

        # Estadísticas
        self.fps_actual = 0.0

    def _cargar_constantes_modelo(self) -> None:
        """Carga dinámicamente las constantes (CLASES, COLORES, etc) del modelo."""
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        constants_path = os.path.join(BASE_DIR, "models", self.model_name, "constants.py")

        if not os.path.exists(constants_path):
            raise FileNotFoundError(
                f"constants.py no encontrado para modelo {self.model_name} en {constants_path}"
            )

        spec = importlib.util.spec_from_file_location(
            f"src.ml.models.{self.model_name}.constants",
            constants_path
        )
        constants_module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = constants_module
        spec.loader.exec_module(constants_module)

        self.CLASES = constants_module.CLASES
        self.COLORES = constants_module.COLORES
        self.EQUIVALENCIAS_DEFECTO = constants_module.EQUIVALENCIAS_DEFECTO
        self.COLORES_DEFECTOS = {cls: (0, 0, 255) for cls in self.CLASES}

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
                    clase = self.CLASES[clase_idx] if clase_idx < len(self.CLASES) else "desconocido"
                    conf_score = float(box.conf[0])
                    x1, y1, x2, y2 = map(int, box.xyxy[0])

                    # Guardar detección y programar servo para IDs nuevos
                    with self.lock:
                        self.conteo_ids_confianza[track_id].append((clase, conf_score))
                        if track_id not in self._ids_servados:
                            self._ids_servados.add(track_id)
                            servo_controller.solicitar(
                                obtener_clase=lambda tid=track_id: self._mejor_clase_para(tid),
                                equivalencias=self.EQUIVALENCIAS_DEFECTO,
                            )

                    # Color: ROJO para defectos (todos los detectados son defectos)
                    color = self.COLORES_DEFECTOS.get(clase, (0, 0, 255))

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
        total_granos = len(self.conteo_ids_confianza)
        stats_text = f"Granos: {total_granos} | FPS: {self.fps_actual:.1f} | Detecciones: {detecciones_count}"
        cv2.putText(
            frame_anotado, stats_text,
            (15, 35),
            cv2.FONT_HERSHEY_SIMPLEX, 0.8,
            (0, 255, 255), 2
        )

        # Log de debug - mostrar siempre si no hay detecciones
        if total_granos > 0 and detecciones_count > 0:
            conteo_final = self._calcular_conteo_final()
            print(f"🎯 Detecciones: {detecciones_count} | Total únicos: {total_granos} | {conteo_final}")
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
            self.conteo_ids_confianza = defaultdict(list)
            self._ids_servados = set()
        servo_controller.limpiar_cola()

    def obtener_conteo(self) -> dict[str, int]:
        """
        Retorna el conteo actual de granos únicos por clase.
        Usa la clase con MAYOR CONFIANZA para cada ID único.

        Returns:
            dict: {clase: cantidad_granos_unicos}
        """
        with self.lock:
            conteo_final = self._calcular_conteo_final()
        return conteo_final

    def _mejor_clase_para(self, track_id: int) -> str | None:
        """
        Retorna la clase con mayor confianza acumulada para el track_id dado.
        Llamado por servo_controller en el momento de activar el servo,
        cuando ya se han acumulado más detecciones que en el primer frame.
        """
        with self.lock:
            detecciones = self.conteo_ids_confianza.get(track_id, [])
        if not detecciones:
            return None
        return max(detecciones, key=lambda x: x[1])[0]

    def _calcular_conteo_final(self) -> dict[str, int]:
        """Calcula conteo final usando la clase con mayor confianza por ID."""
        conteo_por_clase = defaultdict(set)

        for track_id, detecciones in self.conteo_ids_confianza.items():
            if not detecciones:
                continue
            # Usar la clase con mayor confianza para este ID
            clase_final = max(detecciones, key=lambda x: x[1])[0]
            conteo_por_clase[clase_final].add(track_id)

        return {clase: len(ids) for clase, ids in conteo_por_clase.items()}

    def _actualizar_fps(self, t_anterior: float) -> float:
        """Actualiza el FPS y retorna el nuevo tiempo anterior."""
        t_actual = time.time()
        delta = t_actual - t_anterior
        if delta > 0:
            self.fps_actual = 1.0 / delta
        return t_actual
