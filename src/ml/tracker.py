"""
CoffeeRen - Módulo de Tracking en Tiempo Real
Detecta y trackea granos de café usando ByteTrack.
Cada grano recibe un ID único para contar defectos sin duplicados.
"""

import cv2
import threading
import time
import importlib.util
from collections import defaultdict, deque, Counter
from ultralytics import YOLO
import os
import sys

from src.utilities.servo_controller import servo_controller


class CoffeeRenTracker:
    def __init__(self, conf: float, model_name: str = "yolov26n_2cls"):
        """
        Inicializa el tracker de granos de café.

        Args:
            conf: Umbral de confianza para detecciones (0.0 - 1.0) — requerido
            model_name: Nombre del modelo YOLO a usar (yolov26n_2cls — único modelo activo)
        """
        self.conf = conf
        self.model_name = model_name

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self._tracker_cfg = os.path.join(BASE_DIR, "bytetrack.yaml")

        # Modelo principal — prefiere ONNX si existe, fallback a .pt
        model_path = self._resolver_modelo(BASE_DIR, model_name)
        if model_path is None:
            raise FileNotFoundError(
                f"Modelo '{model_name}' no encontrado en models/{model_name}/ "
                f"(se buscó best.onnx y best.pt). "
                f"Descarga best.pt desde Google Drive a models/{model_name}/"
            )

        import torch
        import numpy as np
        self._device = 0 if torch.cuda.is_available() else "cpu"
        self.model = YOLO(model_path)
        print(f"Modelo YOLO cargado: {self.model_name} ({os.path.basename(model_path)}, conf={conf}, device={self._device})")

        self._cargar_constantes(BASE_DIR, self.model_name)

        # Warmup: inicializa CUDA/ONNX con predict() — NO usar track(persist=False) aquí.
        # track(persist=False) registra un callback permanent que recrea ByteTrack
        # en cada frame y llama reset_id(), reiniciando el contador de IDs a 0.
        print("Calentando modelo YOLO (CUDA/ONNX)...")
        dummy = np.zeros((640, 640, 3), dtype=np.uint8)
        self.model.predict(dummy, imgsz=640, device=self._device, verbose=False)
        print("Modelo listo.")

        # Estado del tracking
        # deque(maxlen=30): evita acumulación ilimitada si la faja se pausa
        self.conteo_ids_confianza: defaultdict[int, deque] = defaultdict(lambda: deque(maxlen=30))
        self._ids_servados: set[int] = set()
        self.lock = threading.Lock()

        # Mapping ByteTrack → ID global: garantiza que el contador nunca retrocede
        # aunque ByteTrack reinicie su contador interno (ej. reconexión de cámara).
        self._id_global: int = 0
        self._bytetrack_a_global: dict[int, int] = {}

        # Estadísticas y debug
        self.fps_actual = 0.0
        self.ultima_deteccion_frame_ts: float | None = None

    # ── Helpers de inicialización ─────────────────────────────────────────────

    @staticmethod
    def _resolver_modelo(base_dir: str, model_name: str) -> str | None:
        """Retorna la ruta al modelo preferiendo ONNX sobre .pt; None si ninguno existe."""
        for nombre in ("best.onnx", "best.pt"):
            ruta = os.path.join(base_dir, "models", model_name, nombre)
            if os.path.exists(ruta):
                return ruta
        return None

    def _cargar_constantes(self, base_dir: str, model_name: str) -> None:
        """Carga dinámicamente las constantes del modelo desde su constants.py."""
        constants_path = os.path.join(base_dir, "models", model_name, "constants.py")
        if not os.path.exists(constants_path):
            raise FileNotFoundError(
                f"constants.py no encontrado para modelo {model_name} en {constants_path}"
            )
        spec = importlib.util.spec_from_file_location(
            f"src.ml.models.{model_name}.constants", constants_path
        )
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)

        self.CLASES                = mod.CLASES
        self.COLORES               = mod.COLORES
        self.EQUIVALENCIAS_DEFECTO = mod.EQUIVALENCIAS_DEFECTO
        self.GRANO_MIN_PX          = getattr(mod, "GRANO_MIN_PX", 8)
        self.GRANO_MAX_PX          = getattr(mod, "GRANO_MAX_PX", 200)
        self.GRUPOS_DISPLAY        = getattr(mod, "GRUPOS_DISPLAY", {})

    # ── Pipeline principal ────────────────────────────────────────────────────

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

        try:
            results = self.model.track(
                source=frame,
                conf=self.conf,
                imgsz=640,
                device=self._device,
                tracker=self._tracker_cfg,
                persist=True,   # CRÍTICO: mantiene estado ByteTrack entre frames
                verbose=False
            )
        except Exception as e:
            print(f"Error en tracking: {e}")
            return None

        result = results[0]
        frame_anotado = frame.copy()
        detecciones_count = 0

        if result.boxes is not None and len(result.boxes) > 0:
            if result.boxes.id is not None:
                for box in result.boxes:
                    detecciones_count += 1
                    bytetrack_id = int(box.id[0])
                    clase_idx    = int(box.cls[0])
                    clase        = self.CLASES[clase_idx] if clase_idx < len(self.CLASES) else "desconocido"
                    conf_score   = float(box.conf[0])
                    x1, y1, x2, y2 = map(int, box.xyxy[0])

                    # Filtro de tamaño: descarta objetos fuera del rango de un grano
                    w, h = x2 - x1, y2 - y1
                    if not (self.GRANO_MIN_PX <= w <= self.GRANO_MAX_PX
                            and self.GRANO_MIN_PX <= h <= self.GRANO_MAX_PX):
                        # Calibración: dibujar el descartado en gris con sus dimensiones
                        # para ajustar GRANO_MIN_PX / GRANO_MAX_PX en constants.py
                        cv2.rectangle(frame_anotado, (x1, y1), (x2, y2), (128, 128, 128), 1)
                        cv2.putText(frame_anotado, f"{w}x{h}px", (x1, max(y1 - 4, 12)),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (128, 128, 128), 1)
                        continue

                    with self.lock:
                        # Mapping bytetrack_id → id_global: garantiza que el contador
                        # nunca retrocede aunque ByteTrack reinicie su secuencia interna.
                        if bytetrack_id not in self._bytetrack_a_global:
                            self._id_global += 1
                            self._bytetrack_a_global[bytetrack_id] = self._id_global
                        track_id = self._bytetrack_a_global[bytetrack_id]

                        self.conteo_ids_confianza[track_id].append((clase, conf_score))
                        if track_id not in self._ids_servados:
                            self._ids_servados.add(track_id)
                            servo_controller.solicitar(
                                obtener_clase=lambda tid=track_id: self._mejor_clase_para(tid),
                                equivalencias=self.EQUIVALENCIAS_DEFECTO,
                            )

                    color = self.COLORES.get(clase, (0, 0, 255))
                    cv2.rectangle(frame_anotado, (x1, y1), (x2, y2), color, 3)

                    label = f"#{track_id} {clase} {conf_score:.2%} {w}x{h}px"
                    (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
                    cv2.rectangle(frame_anotado, (x1, y1 - th - 8), (x1 + tw + 4, y1 - 2), color, -1)
                    cv2.putText(frame_anotado, label, (x1 + 2, y1 - 4),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        # Overlay de estadísticas
        total_granos = len(self.conteo_ids_confianza)
        stats_text = f"Granos: {total_granos} | FPS: {self.fps_actual:.1f} | Detecciones: {detecciones_count}"
        cv2.putText(frame_anotado, stats_text, (15, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        if detecciones_count > 0:
            self.ultima_deteccion_frame_ts = time.time()

        if total_granos > 0 and detecciones_count > 0:
            with self.lock:
                conteo_debug = self._calcular_conteo_final()
            print(f"Detecciones: {detecciones_count} | Total únicos: {total_granos} | {conteo_debug}")
        elif detecciones_count == 0:
            boxes_count = len(result.boxes) if result.boxes is not None else 0
            print(f"Frame procesado sin detecciones (boxes: {boxes_count})")

        # Limpieza de IDs globales que ya salieron del frame y no tienen servo pendiente
        if result.boxes is not None and result.boxes.id is not None:
            bt_activos = {int(b.id[0]) for b in result.boxes if b.id is not None}
        else:
            bt_activos = set()
        with self.lock:
            ids_global_activos = {self._bytetrack_a_global[bt] for bt in bt_activos if bt in self._bytetrack_a_global}
            ids_a_limpiar = set(self.conteo_ids_confianza.keys()) - ids_global_activos - self._ids_servados
            for tid in ids_a_limpiar:
                del self.conteo_ids_confianza[tid]

        try:
            _, buffer = cv2.imencode(".jpg", frame_anotado, [cv2.IMWRITE_JPEG_QUALITY, 85])
            return buffer.tobytes()
        except Exception as e:
            print(f"Error codificando JPEG: {e}")
            return None

    # ── API pública ───────────────────────────────────────────────────────────

    def resetear_conteo(self) -> None:
        """Resetea el conteo de IDs para un nuevo lote. El mapping global garantiza
        que los nuevos IDs de ByteTrack no colisionen con los del lote anterior."""
        with self.lock:
            self.conteo_ids_confianza = defaultdict(lambda: deque(maxlen=30))
            self._ids_servados = set()
            self._bytetrack_a_global = {}
            self._id_global = 0
        self.ultima_deteccion_frame_ts = None
        servo_controller.limpiar_cola()

    def obtener_conteo(self) -> dict[str, int]:
        """
        Retorna el conteo actual de granos únicos por clase.
        Usa votación por mayoría; fallback a mayor confianza individual.

        Returns:
            dict: {clase: cantidad_granos_unicos}
        """
        with self.lock:
            return self._calcular_conteo_final()

    def _mejor_clase_para(self, track_id: int) -> str | None:
        """
        Retorna la clase con mayor soporte estadístico para el track_id.
        Con >= 5 detecciones usa votación por mayoría (conf promedio >= 0.45).
        Fallback: clase con mayor confianza individual.
        Llamado por servo_controller tras SERVO_DELAY_S con más frames acumulados.
        """
        with self.lock:
            detecciones = list(self.conteo_ids_confianza.get(track_id, []))
        if not detecciones:
            return None
        if len(detecciones) >= 5:
            clases = [c for c, _ in detecciones]
            clase_mayoritaria = Counter(clases).most_common(1)[0][0]
            conf_promedio = sum(
                c for cls, c in detecciones if cls == clase_mayoritaria
            ) / clases.count(clase_mayoritaria)
            if conf_promedio >= 0.45:
                return clase_mayoritaria
        return max(detecciones, key=lambda x: x[1])[0]

    def _calcular_conteo_final(self) -> dict[str, int]:
        """
        Calcula conteo final por clase usando votación por mayoría por ID.
        Debe llamarse con self.lock adquirido.
        """
        conteo_por_clase: defaultdict[str, set] = defaultdict(set)

        for track_id, detecciones in self.conteo_ids_confianza.items():
            if not detecciones:
                continue

            # Votación por mayoría
            if len(detecciones) >= 5:
                clases = [c for c, _ in detecciones]
                clase_mayoritaria = Counter(clases).most_common(1)[0][0]
                conf_promedio = sum(
                    c for cls, c in detecciones if cls == clase_mayoritaria
                ) / clases.count(clase_mayoritaria)
                clase_final = (
                    clase_mayoritaria if conf_promedio >= 0.45
                    else max(detecciones, key=lambda x: x[1])[0]
                )
            else:
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
