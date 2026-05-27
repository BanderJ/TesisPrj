"""
CoffeeRen - Módulo de Inferencia (Legacy)
No se usa en el flujo actual (ByteTrack está en tracker.py).
Se mantiene para referencia y posibles usos futuros.
"""

from ultralytics import YOLO
import cv2
import os
import importlib.util
import sys

# Ruta base de modelos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")


class CoffeeRenInference:
    def __init__(self, model_name: str = "yolov8n", conf: float = 0.3):
        """
        Inicializa el modelo de inferencia.

        Args:
            model_name: Nombre del modelo a cargar (yolov8n, yolo26n, yolo11n)
            conf: Umbral de confianza para detecciones (0.0 - 1.0)
        """
        self.conf = conf
        self.model_name = model_name
        model_path = os.path.join(MODELS_DIR, model_name, "best.pt")

        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Modelo no encontrado: {model_path}\n"
                f"Asegúrate de copiar best.pt en models/{model_name}/"
            )

        self.model = YOLO(model_path)
        self._cargar_constantes_modelo()
        print(f"✅ Modelo cargado: {model_name} (conf={conf})")

    def _cargar_constantes_modelo(self) -> None:
        """Carga dinámicamente las constantes del modelo."""
        constants_path = os.path.join(MODELS_DIR, self.model_name, "constants.py")

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

    def predecir(self, frame):
        """
        Realiza inferencia sobre un frame.

        Args:
            frame: Imagen BGR de OpenCV

        Returns:
            results: Resultado de YOLO con bounding boxes y clases
        """
        results = self.model.predict(
            source=frame,
            conf=self.conf,
            verbose=False,
            device=0  # GPU si disponible, sino CPU automáticamente
        )
        return results[0]

    def dibujar_detecciones(self, frame, result):
        """
        Dibuja bounding boxes y etiquetas sobre el frame.

        Args:
            frame: Imagen BGR original
            result: Resultado de YOLO

        Returns:
            frame_anotado: Frame con anotaciones dibujadas
        """
        frame_anotado = frame.copy()

        if result.boxes is None:
            return frame_anotado

        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            clase_idx = int(box.cls[0])
            clase = self.CLASES[clase_idx] if clase_idx < len(self.CLASES) else "desconocido"
            conf = float(box.conf[0])
            color = self.COLORES.get(clase, (128, 128, 128))

            # Dibujar bounding box
            cv2.rectangle(frame_anotado, (x1, y1), (x2, y2), color, 2)

            # Etiqueta con clase y confianza
            label = f"{clase} {conf:.2f}"
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(frame_anotado, (x1, y1 - th - 6), (x1 + tw, y1), color, -1)
            cv2.putText(
                frame_anotado, label,
                (x1, y1 - 4),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                (0, 0, 0), 1
            )

        return frame_anotado
