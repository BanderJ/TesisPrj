"""
CoffeeRen - Módulo de Tracking en Tiempo Real
Detecta y trackea granos de café usando ByteTrack.
Cada grano recibe un ID único para contar defectos sin duplicados.
"""

import cv2
import numpy as np
import threading
import time
import importlib.util
import yaml
from collections import defaultdict, deque
from ultralytics import YOLO
from ultralytics.engine.results import Boxes
from ultralytics.trackers.byte_tracker import BYTETracker
from ultralytics.utils import IterableSimpleNamespace
import os
import sys
from typing import Any

from src.config import Config
from src.utilities.servo_controller import servo_controller
from src.utilities.latencia import medidor_latencia


class CoffeeRenTracker:
    # Margen alrededor de la caja al recortar la evidencia de materia extraña:
    # sin contexto el recorte es una mancha sin escala y el operario no puede
    # juzgar si el sistema acertó.
    EVIDENCIA_PADDING_PX: int = 6

    def __init__(self, conf: float, model_name: str = "yolov26n_2cls"):
        """
        Inicializa el tracker de granos de café.

        Args:
            conf: Umbral de confianza para detecciones (0.0 - 1.0) — requerido
            model_name: Nombre del modelo YOLO a usar (yolov26n_2cls — único modelo activo)
        """
        self.conf = conf
        self.model_name = model_name

        # Evidencia minima antes de accionar el servo. Con el piso de conf bajo
        # (ByteTrack filtra con sus propios umbrales), un track efimero de baja
        # confianza no debe disparar la separacion fisica del grano.
        self.SERVO_MIN_FRAMES = 2
        self.SERVO_CONF_MIN = 0.45
        # yolov26n_2cls es end2end (sin NMS): Ultralytics ignora `iou` y la
        # cabeza puede emitir la misma caja dos veces, una por clase. Este IoU
        # lo aplica _deduplicar_tile, sin distinguir clase. Alto para no
        # suprimir cajas de granos que se tocan.
        self.IOU_NMS = 0.80
        # Fraccion de la caja menor que debe caer dentro de la mayor para
        # tratarlas como el mismo grano aunque el IoU no llegue a IOU_NMS
        # (caja anidada). Dos granos distintos nunca quedan uno dentro de otro.
        self.IOS_CONTENIDA = 0.90
        # IoU para fusionar la caja de un grano que cae en el solape de dos tiles.
        self.NMS_ENTRE_TILES = 0.5
        # Sesgo hacia la clase sana al resolver la clase de un track: la confianza
        # acumulada de defecto debe superar a la de la clase sana por este factor
        # para marcar el grano como defecto. 1.0 = voto puro por confianza; 1.3
        # corrige parcialmente el sesgo del modelo a "defecto" (en pruebas confunde
        # ~40% de granos buenos). Subirlo reduce falsos defectos a costa de dejar
        # pasar defectos reales. Parche: el arreglo de fondo es reentrenar con las
        # clases balanceadas. Solo actúa si el track tuvo alguna detección sana.
        self.MARGEN_DEFECTO = 1.3

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self._tracker_cfg = os.path.join(BASE_DIR, "bytetrack.yaml")

        import torch
        cuda_ok = torch.cuda.is_available()
        self._device = 0 if cuda_ok else "cpu"
        # Capacidad de cómputo de la GPU: >= 7.0 tiene FP16 real (RTX). La GTX
        # 1050 Mobile (6.1) no; ahí se queda en FP32 igual que la CPU.
        cap_ok = cuda_ok and torch.cuda.get_device_capability(0)[0] >= 7
        if not cuda_ok:
            print("  ADVERTENCIA: PyTorch no detecta CUDA. La inferencia correra en "
                  "CPU y usara todos los nucleos. Instala torch con CUDA "
                  "(ver requirements.txt) para usar la GPU.")

        # Tope de hilos de CPU: aunque la inferencia vaya en GPU, OpenCV y las
        # ops de glue de PyTorch reparten trabajo entre todos los nucleos.
        if Config.ML_MAX_THREADS_CPU > 0:
            cv2.setNumThreads(Config.ML_MAX_THREADS_CPU)
            torch.set_num_threads(Config.ML_MAX_THREADS_CPU)

        # En GPU se prefiere best.pt (PyTorch nativo, sin depender de
        # onnxruntime-gpu/cuDNN); en CPU se prefiere best.onnx (mas rapido).
        model_path = self._resolver_modelo(BASE_DIR, model_name, prefer_pt=cuda_ok)
        if model_path is None:
            raise FileNotFoundError(
                f"Modelo '{model_name}' no encontrado en models/{model_name}/ "
                f"(se buscó best.pt y best.onnx). "
                f"Descarga best.pt desde Google Drive a models/{model_name}/"
            )

        # FP16 solo si de verdad se cargó un .pt en una GPU capaz: los .onnx se
        # exportaron con half=False y pasar half=True a onnxruntime no aplica.
        self._half = bool(cap_ok and model_path.endswith(".pt"))

        self.model = YOLO(model_path)
        print(f"Modelo YOLO cargado: {self.model_name} ({os.path.basename(model_path)}, "
              f"conf={conf}, device={self._device}, half={self._half})")

        self._cargar_constantes(BASE_DIR, self.model_name)

        # ByteTrack gestionado a mano: la deteccion corre por tiles (varias
        # inferencias por frame) y hay que fusionarlas ANTES de trackear, algo
        # que model.track() no permite. Se alimenta con las cajas ya fusionadas.
        with open(self._tracker_cfg, encoding="utf-8") as _f:
            _cfg_bt = IterableSimpleNamespace(**yaml.safe_load(_f))
        self._bytetracker = BYTETracker(args=_cfg_bt)
        self._reset_bytetrack = False
        # Época del lote: resetear_conteo la incrementa. Un frame que empezó en
        # una época anterior no escribe en el conteo del lote nuevo.
        self._epoca_lote = 0

        # Warmup: inicializa CUDA/ONNX con predict() — NO usar track(persist=False) aquí.
        # track(persist=False) registra un callback permanent que recrea ByteTrack
        # en cada frame y llama reset_id(), reiniciando el contador de IDs a 0.
        print("Calentando modelo YOLO (CUDA/ONNX)...")
        dummy = np.zeros((640, 640, 3), dtype=np.uint8)
        self.model.predict(dummy, imgsz=640, device=self._device, half=self._half, verbose=False)
        print("Modelo listo.")

        # Estado del tracking
        # deque(maxlen=30): evita acumulación ilimitada si la faja se pausa
        self.conteo_ids_confianza: defaultdict[int, deque] = defaultdict(lambda: deque(maxlen=30))
        # Máximo de confianza visto en TODA la vida del track (no solo en la
        # ventana de 30 que retiene conteo_ids_confianza). _resolver_clase_display
        # necesita esto para que "nunca superó UMBRAL_CONF_CONOCIDO" sea permanente:
        # con el deque acotado, una detección ruidosa vieja que ya salió de la
        # ventana dejaba de contar y el track oscilaba entre 'desconocido' y una
        # clase conocida cada vez que la ventana se desplazaba.
        self._conf_max_historico: defaultdict[int, float] = defaultdict(float)
        self._ids_servados: set[int] = set()
        # Evidencia de materia extraña: un recorte JPEG por track marcado
        # 'desconocido'. El ML solo recorta y encola — quien escribe a disco y
        # emite el evento es tracker_service (el ML no toca disco ni BD).
        self._ids_evidenciados: set[int] = set()
        self._cola_evidencias: deque = deque(maxlen=50)
        # ts (time.monotonic) de la primera vez que se vio cada track: referencia
        # real para el servo aunque la solicitud se posponga por falta de evidencia.
        self._ts_primer_avistamiento: dict[int, float | None] = {}
        self.lock = threading.Lock()

        # Mapping ByteTrack → ID global: garantiza que el contador nunca retrocede
        # aunque ByteTrack reinicie su contador interno (ej. reconexión de cámara).
        self._id_global: int = 0
        self._bytetrack_a_global: dict[int, int] = {}

        # Estadísticas y debug
        # Instantes de los frames procesados; el FPS es cuántos caen en el último
        # segundo. maxlen cubre de sobra el techo de la cámara (~90 fps).
        self._fps_tiempos: deque[float] = deque(maxlen=256)
        self.ultima_deteccion_frame_ts: float | None = None

        # Gate de movimiento: miniatura en gris del último frame evaluado.
        self._gris_movimiento: np.ndarray | None = None
        self._gate_log_ts = 0.0
        # Throttle del log de descartes por tamaño (ML_DEBUG_SERVO): con grilla
        # 3x3 a 30 fps son cientos de líneas/s de E/S síncrona en el hilo del
        # tracker, que frena el pipeline justo en lo que se está midiendo.
        self._debug_descarte_ts = 0.0
        self._log_conteo_ts = 0.0
        # Diagnóstico de granos juntos (ML_DEBUG_SERVO): cajas de grano que
        # _deduplicar_tile eliminó a causa de una caja fuera de rango (un grupo
        # > GRANO_MAX_PX o una caja < GRANO_MIN_PX dentro del grano). Las del
        # frame actual se dibujan; el resto se acumula para un resumen en
        # consola cada 2 s.
        self._debug_suprimidas: list[np.ndarray] = []
        self._debug_frames = 0
        self._debug_grupos = 0
        self._debug_n_suprimidas = 0
        self._debug_ejemplo = ""
        self._debug_grupos_ts = 0.0

    # ── Helpers de inicialización ─────────────────────────────────────────────

    @staticmethod
    def _resolver_modelo(base_dir: str, model_name: str, prefer_pt: bool = False) -> str | None:
        """Ruta al modelo. En GPU se prefiere best.pt (PyTorch nativo); en CPU se
        prefiere best.onnx (mas rapido en CPU). None si no existe ninguno."""
        orden = ("best.pt", "best.onnx") if prefer_pt else ("best.onnx", "best.pt")
        for nombre in orden:
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

        # Sin valores por defecto: si falta una constante, el arranque falla con
        # un mensaje claro en vez de seguir con valores de otra cámara o modelo.
        requeridas = (
            "CLASES", "COLORES", "EQUIVALENCIAS_DEFECTO", "GRANO_MIN_PX", "GRANO_MAX_PX",
            "TILES_X", "TILES_Y", "TILE_SOLAPE_PX", "CLASE_DESCONOCIDO",
            "UMBRAL_CONF_CONOCIDO", "DESCONOCIDO_MIN_FRAMES",
        )
        faltan = [nombre for nombre in requeridas if not hasattr(mod, nombre)]
        if faltan:
            raise AttributeError(f"Faltan constantes en {constants_path}: {', '.join(faltan)}")
        for nombre in requeridas:
            setattr(self, nombre, getattr(mod, nombre))
        self.GRUPOS_DISPLAY = getattr(mod, "GRUPOS_DISPLAY", {})

    # ── Detección ────────────────────────────────────────────────────────────

    def _grilla_tiles(self, w: int, h: int) -> list[tuple[int, int, int, int]]:
        """Rects (x0, y0, x1, y1) de los tiles, con solape para no cortar granos
        que caen en el borde entre dos tiles."""
        nx, ny, s = self.TILES_X, self.TILES_Y, self.TILE_SOLAPE_PX
        tw, th = w // nx, h // ny
        rects = []
        for iy in range(ny):
            for ix in range(nx):
                rects.append((
                    max(ix * tw - s, 0),
                    max(iy * th - s, 0),
                    min((ix + 1) * tw + s, w),
                    min((iy + 1) * th + s, h),
                ))
        return rects

    def _detectar(self, frame: np.ndarray) -> np.ndarray:
        """Corre YOLO sobre el frame y devuelve las cajas en coordenadas del
        frame completo: array (N, 6) con filas [x1, y1, x2, y2, conf, cls].

        El modelo se entrenó con 1 grano por imagen a ~640px. En la faja/mesa el
        grano ocupa una fracción chica de un frame 1920x1080, así que al reescalar
        todo el frame a imgsz=640 el grano queda demasiado pequeño y el modelo no
        lo detecta. Partir el frame en tiles acerca cada grano a la escala de
        entrenamiento; cada tile se infiere a imgsz=640 (ese parámetro no cambia).
        Con TILES_X = TILES_Y = 1 se infiere el frame completo (comportamiento
        previo al tiling)."""
        h, w = frame.shape[:2]
        tiles = self._grilla_tiles(w, h)
        subs = [frame[y0:y1, x0:x1] for (x0, y0, x1, y1) in tiles]
        # Un solo batch: en GPU es una pasada para todos los tiles; en CPU
        # equivale a las llamadas sueltas anteriores.
        resultados = self.model.predict(
            subs, imgsz=640, conf=self.conf,
            device=self._device, half=self._half, verbose=False,
        )
        cajas: list[np.ndarray] = []
        self._debug_suprimidas = []
        for idx, ((x0, y0, x1, y1), r) in enumerate(zip(tiles, resultados)):
            if r.boxes is None or len(r.boxes) == 0:
                continue
            supresiones: list[tuple[np.ndarray, np.ndarray]] | None = (
                [] if Config.ML_DEBUG_SERVO else None
            )
            b = self._deduplicar_tile(r.boxes.data.cpu().numpy(), supresiones)  # (n, 6): x1, y1, x2, y2, conf, cls
            if supresiones is not None:
                self._registrar_supresion_debug(b, supresiones, x0, y0)
            b[:, [0, 2]] += x0
            b[:, [1, 3]] += y0
            # 7a columna = indice de tile: _fusionar_cajas no une dos cajas del
            # mismo tile (_deduplicar_tile ya las separo -> son granos distintos).
            b = np.hstack([b, np.full((len(b), 1), idx, dtype=np.float32)])
            cajas.append(b)

        if Config.ML_DEBUG_SERVO:
            self._log_supresion_debug()
        if not cajas:
            return np.zeros((0, 6), dtype=np.float32)
        todas = np.vstack(cajas)                    # (N, 7)
        if len(tiles) == 1:
            return todas[:, :6]
        return self._fusionar_cajas(todas)[:, :6]

    def _deduplicar_tile(self, cajas: np.ndarray,
                         supresiones: list[tuple[np.ndarray, np.ndarray]] | None = None) -> np.ndarray:
        """NMS agnóstico a la clase dentro de un tile. Filas (x1, y1, x2, y2, conf, cls).

        El modelo es end2end: no pasa por NMS y, si un grano queda cerca del
        50/50, la cabeza emite la misma caja como 'defecto' y como 'verde'. Sin
        este filtro ByteTrack recibe las dos: una alterna la clase del track
        existente y la otra abre un track nuevo (el grano se cuenta dos veces).
        Se conserva la caja más confiada; la otra se descarta si su IoU con ella
        alcanza IOU_NMS o si queda contenida en ella (IOS_CONTENIDA).

        Si se pasa `supresiones`, se le agrega cada par (caja descartada, caja
        que la descartó); lo usa el diagnóstico de ML_DEBUG_SERVO."""
        if len(cajas) < 2:
            return cajas
        cajas = cajas[np.argsort(-cajas[:, 4])]
        quedan: list[np.ndarray] = []
        for c in cajas:
            supresora = None
            for q in quedan:
                iou, ios = self._iou_ios(c, q)
                if iou >= self.IOU_NMS or ios >= self.IOS_CONTENIDA:
                    supresora = q
                    break
            if supresora is None:
                quedan.append(c)
            elif supresiones is not None:
                supresiones.append((c, supresora))
        return np.array(quedan, dtype=cajas.dtype)

    def _es_tamano_grano(self, w: float, h: float) -> bool:
        """True si una caja de w x h px está en el rango de tamaño de un grano."""
        return (self.GRANO_MIN_PX <= w <= self.GRANO_MAX_PX
                and self.GRANO_MIN_PX <= h <= self.GRANO_MAX_PX)

    def _registrar_supresion_debug(self, quedan: np.ndarray,
                                   supresiones: list[tuple[np.ndarray, np.ndarray]],
                                   x0: int, y0: int) -> None:
        """Diagnóstico (ML_DEBUG_SERVO): anota las cajas de tamaño de grano que
        _deduplicar_tile eliminó a causa de una caja de grupo, es decir, una caja
        fuera del rango de grano que el filtro de tamaño descarta después. Si hay
        supresiones, los granos que se tocan sí se detectan pero se pierden en la
        deduplicación; si no las hay, el modelo solo marca el grupo."""
        self._debug_grupos += sum(
            1 for q in quedan if max(q[2] - q[0], q[3] - q[1]) > self.GRANO_MAX_PX
        )
        for c, g in supresiones:
            w, h = c[2] - c[0], c[3] - c[1]
            if not self._es_tamano_grano(w, h) or self._es_tamano_grano(g[2] - g[0], g[3] - g[1]):
                continue
            caja = c.copy()
            caja[[0, 2]] += x0
            caja[[1, 3]] += y0
            self._debug_suprimidas.append(caja)
            self._debug_n_suprimidas += 1
            # La supresora también puede ser una caja menor que GRANO_MIN_PX
            # dentro del grano, con más confianza que él.
            supresora = f"{int(g[2] - g[0])}x{int(g[3] - g[1])}px conf={g[4]:.2f}"
            grano = f"grano {int(w)}x{int(h)}px conf={c[4]:.2f}"
            if max(g[2] - g[0], g[3] - g[1]) > self.GRANO_MAX_PX:
                self._debug_ejemplo = f"grupo {supresora} contiene {grano}"
            else:
                self._debug_ejemplo = f"caja chica {supresora} dentro de {grano}"

    def _log_supresion_debug(self) -> None:
        """Resumen de _registrar_supresion_debug en consola, como máximo cada 2 s."""
        self._debug_frames += 1
        ahora = time.monotonic()
        if ahora - self._debug_grupos_ts <= 2.0:
            return
        if self._debug_grupos or self._debug_n_suprimidas:
            linea =(f"[det-debug] {self._debug_frames} frames: {self._debug_grupos} cajas de grupo "
                     f"(> {self.GRANO_MAX_PX}px), {self._debug_n_suprimidas} cajas de grano "
                     f"suprimidas por una caja fuera de rango")
            if self._debug_n_suprimidas:
                linea += f". Ej.: {self._debug_ejemplo}"
            print(linea)
        self._debug_grupos_ts = ahora
        self._debug_frames = self._debug_grupos = self._debug_n_suprimidas = 0
        self._debug_ejemplo = ""

    @staticmethod
    def _iou_ios(a: np.ndarray, b: np.ndarray) -> tuple[float, float]:
        """IoU e IoS (intersección / área de la caja menor) de dos cajas
        (x1, y1, x2, y2, ...). (0, 0) si no se tocan o alguna tiene área nula."""
        ix = max(0.0, min(a[2], b[2]) - max(a[0], b[0]))
        iy = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
        inter = ix * iy
        area_a = (a[2] - a[0]) * (a[3] - a[1])
        area_b = (b[2] - b[0]) * (b[3] - b[1])
        if inter <= 0 or min(area_a, area_b) <= 0:
            return 0.0, 0.0
        return float(inter / (area_a + area_b - inter)), float(inter / min(area_a, area_b))

    def _fusionar_cajas(self, cajas: np.ndarray) -> np.ndarray:
        """Une la caja de un grano partido por la costura entre dos tiles.
        Entrada/salida: filas (x1, y1, x2, y2, conf, cls, idx_tile).

        Solo funde cajas de tiles DISTINTOS (col 6): dos cajas del mismo tile ya
        pasaron por _deduplicar_tile y son granos distintos — nunca se
        funden, así dos granos que se tocan siguen contando por separado.

        Cross-tile se funden si se solapan (IoU >= NMS_ENTRE_TILES o IoS >= 0.6)
        Y la caja envolvente no supera 1.6x a la mayor de las dos — evita que dos
        granos vecinos que caen en la costura se peguen en una caja gigante.
        Misma clase -> caja envolvente + mayor confianza; distinta clase -> se
        conserva la más confiada. Se repite hasta que el conteo se estabiliza."""
        cajas = cajas.astype(np.float32)
        for _ in range(4):
            # área descendente: la caja más completa absorbe a los recortes
            cajas = cajas[np.argsort(-(cajas[:, 2] - cajas[:, 0]) * (cajas[:, 3] - cajas[:, 1]))]
            fusion: list[np.ndarray] = []
            for c in cajas:
                for k, f in enumerate(fusion):
                    if int(c[6]) == int(f[6]):
                        continue                       # mismo tile -> granos distintos
                    iou, ios = self._iou_ios(c, f)
                    if iou == 0.0 or (iou < self.NMS_ENTRE_TILES and ios < 0.6):
                        continue
                    area_c = (c[2] - c[0]) * (c[3] - c[1])
                    area_f = (f[2] - f[0]) * (f[3] - f[1])
                    env = (max(c[2], f[2]) - min(c[0], f[0])) * (max(c[3], f[3]) - min(c[1], f[1]))
                    if env > 1.6 * max(area_c, area_f):
                        continue                       # fusionar agrandaría demasiado
                    if int(c[5]) == int(f[5]):
                        fusion[k] = np.array([
                            min(c[0], f[0]), min(c[1], f[1]),
                            max(c[2], f[2]), max(c[3], f[3]),
                            max(c[4], f[4]), f[5], f[6],
                        ], dtype=np.float32)
                    elif c[4] > f[4]:
                        fusion[k] = c
                    break
                else:
                    fusion.append(c)
            if len(fusion) == len(cajas):
                break
            cajas = np.array(fusion, dtype=np.float32)
        return cajas if len(cajas) else np.zeros((0, 7), dtype=np.float32)

    # ── Pipeline principal ────────────────────────────────────────────────────

    def hay_movimiento(self, frame: np.ndarray) -> bool:
        """True si el frame cambió respecto al último frame que pasó a inferencia.
        Se compara una miniatura 160x90 en gris: por debajo de ML_GATE_UMBRAL
        (diferencia media de intensidad) la faja está quieta y no vale la pena
        correr YOLO. El primer frame siempre cuenta como movimiento.

        La referencia solo se actualiza cuando el frame pasa el gate. Si se
        actualizara en cada llamada, una faja lenta (JGY370, 10 RPM) nunca
        acumularía diferencia entre dos frames consecutivos y la inferencia se
        omitiría con la faja en marcha."""
        gris = cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), (160, 90))
        if self._gris_movimiento is None:
            self._gris_movimiento = gris
            return True
        diff = float(np.mean(cv2.absdiff(gris, self._gris_movimiento)))
        ahora = time.monotonic()
        if ahora - self._gate_log_ts > 2.0:
            self._gate_log_ts = ahora
            print(f"gate: diff media={diff:.2f} (umbral={Config.ML_GATE_UMBRAL})")
        if diff >= Config.ML_GATE_UMBRAL:
            self._gris_movimiento = gris
            return True
        return False

    def procesar_frame(self, frame: np.ndarray, ts_frame: float | None = None) -> bytes | None:
        """
        Procesa un frame con ByteTrack y retorna JPEG anotado.

        Args:
            frame: Frame BGR de OpenCV (resolución de Config.CAM_WIDTH x CAM_HEIGHT)
            ts_frame: time.monotonic() de captura del frame. El servo se programa
                      desde este instante para descontar la latencia de inferencia.

        Returns:
            bytes: Frame codificado en JPEG con anotaciones, o None si error
        """
        if frame is None:
            return None

        # Cronometro del pipeline: t_toma es cuando este hilo recibe el frame, asi
        # que t_toma - ts_frame es lo que el frame espero en cola.
        t_toma = time.monotonic()

        with self.lock:
            epoca = self._epoca_lote
            reiniciar = self._reset_bytetrack
            self._reset_bytetrack = False

        try:
            if reiniciar:
                # ByteTrack solo se toca desde este hilo.
                self._bytetracker.reset()
            dets = self._detectar(frame)                 # (N, 6) en coords del frame completo
            t_inf1 = time.monotonic()
            tracks = self._bytetracker.update(
                Boxes(dets, orig_shape=frame.shape[:2]).cpu().numpy(), frame
            )
        except Exception as e:
            print(f"Error en tracking: {e}")
            return None

        frame_anotado = frame.copy()
        detecciones_count = 0

        # Diagnóstico: granos detectados que la deduplicación eliminó a causa de
        # una caja fuera de rango (en magenta, debajo de las cajas de los tracks).
        for c in self._debug_suprimidas:
            sx1, sy1, sx2, sy2 = map(int, c[:4])
            cv2.rectangle(frame_anotado, (sx1, sy1), (sx2, sy2), (255, 0, 255), 1)
            cv2.putText(frame_anotado, f"sup {c[4]:.2f}", (sx1, max(sy1 - 4, 12)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)

        # tracks: filas (x1, y1, x2, y2, bytetrack_id, conf, cls, idx_deteccion)
        for pista in tracks:
            detecciones_count += 1
            bytetrack_id = int(pista[4])
            clase_idx    = int(pista[6])
            clase_frame  = self.CLASES[clase_idx] if clase_idx < len(self.CLASES) else self.CLASE_DESCONOCIDO
            conf_score   = float(pista[5])
            x1, y1, x2, y2 = map(int, pista[:4])

            # Filtro de tamaño: descarta objetos fuera del rango de un grano
            w, h = x2 - x1, y2 - y1
            if not self._es_tamano_grano(w, h):
                # Calibración: dibujar el descartado en gris con sus dimensiones
                # para ajustar GRANO_MIN_PX / GRANO_MAX_PX en constants.py
                cv2.rectangle(frame_anotado, (x1, y1), (x2, y2), (128, 128, 128), 1)
                cv2.putText(frame_anotado, f"{w}x{h}px", (x1, max(y1 - 4, 12)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (128, 128, 128), 1)
                if Config.ML_DEBUG_SERVO:
                    _ahora = time.monotonic()
                    if _ahora - self._debug_descarte_ts > 2.0:
                        self._debug_descarte_ts = _ahora
                        print(f"[servo-debug] bt#{bytetrack_id} DESCARTADO por tamaño "
                              f"{w}x{h}px (rango {self.GRANO_MIN_PX}-{self.GRANO_MAX_PX}) "
                              f"conf={conf_score:.2f} clase={clase_frame}")
                continue

            with self.lock:
                if epoca != self._epoca_lote:
                    # El lote se reinició mientras se procesaba este frame: sus
                    # tracks son del lote anterior y no se cuentan en el nuevo.
                    break
                # Mapping bytetrack_id → id_global: garantiza que el contador
                # nunca retrocede aunque ByteTrack reinicie su secuencia interna.
                if bytetrack_id not in self._bytetrack_a_global:
                    self._id_global += 1
                    self._bytetrack_a_global[bytetrack_id] = self._id_global
                track_id = self._bytetrack_a_global[bytetrack_id]

                self.conteo_ids_confianza[track_id].append((clase_frame, conf_score))
                if conf_score > self._conf_max_historico[track_id]:
                    self._conf_max_historico[track_id] = conf_score
                self._ts_primer_avistamiento.setdefault(track_id, ts_frame)
                # Clase para dibujar: resuelta sobre TODO el historial del track,
                # no la de este frame — quita el parpadeo sano<->defecto y marca
                # 'desconocido' los objetos que nunca dieron una deteccion segura.
                clase = self._resolver_clase_display(
                    track_id, list(self.conteo_ids_confianza[track_id])
                ) or clase_frame

                # Solo se pide separacion cuando el track tiene respaldo:
                # evita que una deteccion debil y efimera accione el servo.
                # La referencia temporal sigue siendo el primer avistamiento
                # para no degradar la precision del delay.
                if track_id not in self._ids_servados and self._evidencia_suficiente(track_id):
                    self._ids_servados.add(track_id)
                    servo_controller.solicitar(
                        obtener_clase=lambda tid=track_id: self._mejor_clase_para(tid),
                        equivalencias=self.EQUIVALENCIAS_DEFECTO,
                        t_referencia=self._ts_primer_avistamiento.get(track_id) or ts_frame,
                    )

                # Materia extraña: se guarda una foto del objeto para que el
                # operario pueda verificar después qué se desvió. Mismo criterio
                # de evidencia que el servo — no se fotografía una detección
                # débil y efímera — y una sola vez por track.
                if (clase == self.CLASE_DESCONOCIDO
                        and track_id not in self._ids_evidenciados
                        and self._evidencia_suficiente(track_id)):
                    self._ids_evidenciados.add(track_id)
                    self._encolar_evidencia(frame, track_id, x1, y1, x2, y2, conf_score)

            color = self.COLORES.get(clase, (0, 0, 255))
            grosor = 2 if clase == self.CLASE_DESCONOCIDO else 3
            cv2.rectangle(frame_anotado, (x1, y1), (x2, y2), color, grosor)

            nombre = "objeto desconocido" if clase == self.CLASE_DESCONOCIDO else clase
            ### label = f"#{track_id} {nombre} {conf_score:.2%} {w}x{h}px"
            label = f"#{track_id} {nombre}"
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            cv2.rectangle(frame_anotado, (x1, y1 - th - 8), (x1 + tw + 4, y1 - 2), color, -1)
            cv2.putText(frame_anotado, label, (x1 + 2, y1 - 4),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        # Overlay de estadísticas
        total_granos = len(self.conteo_ids_confianza)
        stats_text = f"Granos: {total_granos} | Detecciones: {detecciones_count}"
        cv2.putText(frame_anotado, stats_text, (15, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        if detecciones_count > 0:
            self.ultima_deteccion_frame_ts = time.time()

        # Resumen en consola cada 2 s, no por frame: imprimir 30 veces por segundo
        # frena este hilo, que es el que se cronometra para el indicador de latencia.
        ahora_log = time.monotonic()
        if ahora_log - self._log_conteo_ts > 2.0:
            self._log_conteo_ts = ahora_log
            if detecciones_count > 0:
                with self.lock:
                    conteo_debug = self._calcular_conteo_final()
                print(f"Detecciones: {detecciones_count} | Total únicos: {total_granos} | {conteo_debug}")
            else:
                print(f"Frame procesado sin detecciones (cajas crudas: {len(dets)})")

        # Limpieza de IDs globales que ya salieron del frame y no tienen servo pendiente
        bt_activos = {int(pista[4]) for pista in tracks}
        with self.lock:
            ids_global_activos = {self._bytetrack_a_global[bt] for bt in bt_activos if bt in self._bytetrack_a_global}
            # Si el lote se reinició durante este frame, sus tracks no son del lote
            # nuevo: no hay nada que limpiar.
            ids_a_limpiar = (
                set(self.conteo_ids_confianza.keys()) - ids_global_activos - self._ids_servados
                if epoca == self._epoca_lote else set()
            )
            for tid in ids_a_limpiar:
                if Config.ML_DEBUG_SERVO:
                    # Estos tracks se van sin haber accionado el servo: nunca
                    # juntaron evidencia (SERVO_MIN_FRAMES / SERVO_CONF_MIN).
                    # _resolver_clase_display, no _mejor_clase_para: ya se tiene el lock.
                    d = list(self.conteo_ids_confianza[tid])
                    if d:
                        print(f"[servo-debug] #{tid} SIN SERVO (evidencia insuficiente): "
                              f"n_det={len(d)}/{self.SERVO_MIN_FRAMES} "
                              f"conf_max={max(c for _, c in d):.2f}/{self.SERVO_CONF_MIN} "
                              f"clase={self._resolver_clase_display(tid, d)}")
                del self.conteo_ids_confianza[tid]
                self._conf_max_historico.pop(tid, None)
                self._ts_primer_avistamiento.pop(tid, None)

        # Indicador de tesis: latencia captura -> registro. Se mide aqui porque el
        # conteo ya esta actualizado y el servo ya fue solicitado; el encode JPEG
        # que sigue es streaming al navegador, no parte del pipeline de decision.
        if Config.ML_MEDIR_LATENCIA and ts_frame is not None:
            t_fin = time.monotonic()
            try:
                medidor_latencia.registrar({
                    "espera_ms":        (t_toma - ts_frame) * 1000.0,
                    "procesamiento_ms": (t_inf1 - t_toma) * 1000.0,
                    "decision_ms":      (t_fin - t_inf1) * 1000.0,
                    "total_ms":         (t_fin - ts_frame) * 1000.0,
                })
            except Exception as exc:
                # Medir jamas puede tumbar la clasificacion.
                print(f"[latencia] Error registrando muestra: {exc}")

        try:
            # La detección ya corrió a resolución completa; solo se reduce lo
            # que se transmite al navegador (menos encode, menos ancho de banda).
            ancho = Config.ML_STREAM_ANCHO
            if ancho and frame_anotado.shape[1] > ancho:
                alto = round(frame_anotado.shape[0] * ancho / frame_anotado.shape[1])
                frame_anotado = cv2.resize(frame_anotado, (ancho, alto))
            _, buffer = cv2.imencode(
                ".jpg", frame_anotado, [cv2.IMWRITE_JPEG_QUALITY, Config.ML_STREAM_JPEG_QUALITY]
            )
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
            self._conf_max_historico = defaultdict(float)
            self._ids_servados = set()
            self._ids_evidenciados = set()
            self._cola_evidencias.clear()
            self._ts_primer_avistamiento = {}
            self._bytetrack_a_global = {}
            self._id_global = 0
            self._epoca_lote += 1
            # El hilo de procesamiento resetea ByteTrack en el próximo frame (evita
            # tocar el tracker desde otro hilo mientras corre procesar_frame).
            self._reset_bytetrack = True
            self._gris_movimiento = None
        self.ultima_deteccion_frame_ts = None
        servo_controller.limpiar_cola()
        medidor_latencia.resetear()

    def obtener_conteo(self) -> dict[str, int]:
        """
        Retorna el conteo actual de granos únicos por clase.
        Cada track se resuelve por confianza acumulada por clase.

        Returns:
            dict: {clase: cantidad_granos_unicos}
        """
        with self.lock:
            return self._calcular_conteo_final()

    def _evidencia_suficiente(self, track_id: int) -> bool:
        """True cuando el track tiene respaldo para accionar el servo: al menos
        SERVO_MIN_FRAMES detecciones acumuladas, o una con confianza alta.
        Debe llamarse con self.lock adquirido."""
        dets = self.conteo_ids_confianza.get(track_id)
        if not dets:
            return False
        if len(dets) >= self.SERVO_MIN_FRAMES:
            return True
        return max(c for _, c in dets) >= self.SERVO_CONF_MIN

    def _encolar_evidencia(
        self,
        frame: np.ndarray,
        track_id: int,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        conf: float,
    ) -> None:
        """Recorta el objeto del frame SIN anotar y lo encola como JPEG.

        Se llama con self.lock adquirido y desde el hilo del tracker: aquí no se
        toca disco ni BD, solo memoria. Todo va en try/except — capturar
        evidencia jamás puede tumbar la clasificación.
        """
        try:
            alto, ancho = frame.shape[:2]
            p = self.EVIDENCIA_PADDING_PX
            recorte = frame[max(0, y1 - p):min(alto, y2 + p),
                            max(0, x1 - p):min(ancho, x2 + p)]
            if recorte.size == 0:
                return
            ok, buf = cv2.imencode(".jpg", recorte, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
            if not ok:
                return
            self._cola_evidencias.append({
                "track_id": track_id,
                "jpeg":     buf.tobytes(),
                "ancho_px": x2 - x1,
                "alto_px":  y2 - y1,
                "conf":     round(conf, 3),
            })
        except Exception as exc:
            print(f"[evidencia] Error recortando track #{track_id}: {exc}")

    def drenar_evidencias(self) -> list[dict[str, Any]]:
        """Vacía la cola de recortes pendientes. La consume tracker_service."""
        with self.lock:
            pendientes = list(self._cola_evidencias)
            self._cola_evidencias.clear()
        return pendientes

    def _clases_sanas(self) -> set[str]:
        """Clases que NO suman defectos equivalentes. Única fuente de verdad para
        distinguir grano bueno de defectuoso: la misma tabla que usa classifier.py
        y tracker_service (evita hardcodear 'verde' aquí)."""
        return {c for c, eq in self.EQUIVALENCIAS_DEFECTO.items() if eq == 0.0}

    def _resolver_clase(self, detecciones: list[tuple[str, float]]) -> str | None:
        """Clase de un track por confianza ACUMULADA por clase (suma de la conf
        de cada detección). Una detección aislada de alta confianza no voltea el
        veredicto de varias detecciones sostenidas: elimina el parpadeo
        sano→defecto que producía el 'gana el frame de mayor confianza'.

        Con MARGEN_DEFECTO > 1.0 el grano solo se marca como defecto si la
        confianza acumulada de defecto supera a la de la clase sana por ese
        factor."""
        if not detecciones:
            return None
        peso: defaultdict[str, float] = defaultdict(float)
        for clase, conf in detecciones:
            peso[clase] += conf
        clase_top = max(peso, key=peso.get)

        sanas = self._clases_sanas()
        if clase_top in sanas:
            return clase_top
        peso_sana = sum(p for c, p in peso.items() if c in sanas)
        if peso_sana > 0.0 and peso[clase_top] < peso_sana * self.MARGEN_DEFECTO:
            return max(sanas, key=lambda c: peso.get(c, 0.0))
        return clase_top

    def _resolver_clase_display(self, track_id: int, detecciones: list[tuple[str, float]]) -> str | None:
        """Clase para DIBUJAR, CONTAR y decidir el servo. Igual que _resolver_clase,
        pero devuelve 'desconocido' cuando el track nunca superó UMBRAL_CONF_CONOCIDO
        tras DESCONOCIDO_MIN_FRAMES observaciones: el modelo jamás estuvo medianamente
        seguro de que fuera un grano (piedra, pajilla, palito, mano, sombra).
        'desconocido' tiene equivalencia > 0 en EQUIVALENCIAS_DEFECTO, así que el
        servo lo desvía al canal DEFECTO igual que un grano defectuoso. Los granos
        normales caen a _resolver_clase (que aplica el sesgo MARGEN_DEFECTO).

        El chequeo usa self._conf_max_historico (máximo de TODA la vida del
        track), no max(detecciones): detecciones viene de conteo_ids_confianza,
        un deque(maxlen=30), así que una detección ruidosa vieja sale de la
        ventana y "nunca superó" dejaría de cumplirse aunque sí se superó antes
        — el track oscilaría entre 'desconocido' y una clase conocida."""
        if not detecciones:
            return None
        if (len(detecciones) >= self.DESCONOCIDO_MIN_FRAMES
                and self._conf_max_historico.get(track_id, 0.0) < self.UMBRAL_CONF_CONOCIDO):
            return self.CLASE_DESCONOCIDO
        return self._resolver_clase(detecciones)

    def _mejor_clase_para(self, track_id: int) -> str | None:
        """Clase del track para el servo. Llamado por servo_controller tras
        SERVO_DELAY_S, con más frames acumulados que en el primer avistamiento.
        Usa la resolución de display: un objeto extraño (rotulado 'desconocido')
        se desvía al canal DEFECTO vía EQUIVALENCIAS_DEFECTO['desconocido']."""
        with self.lock:
            detecciones = list(self.conteo_ids_confianza.get(track_id, []))
            clase = self._resolver_clase_display(track_id, detecciones)
        if Config.ML_DEBUG_SERVO:
            # Punto de decision real: lo que el servo ejecuta SERVO_DELAY_S
            # despues del primer avistamiento.
            # conf_hist es la que decide 'desconocido' (máximo de TODA la vida del
            # track); conf_win es el máximo dentro del deque(maxlen=30). Se imprimen
            # las dos: calibrar UMBRAL_CONF_CONOCIDO contra conf_hist, no contra la
            # ventana, que ya pudo haber descartado la detección que decidió.
            conf_hist = self._conf_max_historico.get(track_id, 0.0)
            conf_win = max((c for _, c in detecciones), default=0.0)
            accion = "DEFECTO" if self.EQUIVALENCIAS_DEFECTO.get(clase, 0.0) > 0.0 else "BUENO"
            print(f"[servo-debug] #{track_id} -> {clase} (n_det={len(detecciones)} "
                  f"conf_hist={conf_hist:.2f}/{self.UMBRAL_CONF_CONOCIDO} "
                  f"conf_win={conf_win:.2f}) servo={accion}")
        return clase

    def _calcular_conteo_final(self) -> dict[str, int]:
        """
        Calcula el conteo final por clase resolviendo cada track por confianza
        acumulada. Debe llamarse con self.lock adquirido.
        """
        conteo_por_clase: defaultdict[str, set] = defaultdict(set)

        for track_id, detecciones in self.conteo_ids_confianza.items():
            clase_final = self._resolver_clase_display(track_id, list(detecciones))
            if clase_final is not None:
                conteo_por_clase[clase_final].add(track_id)

        return {clase: len(ids) for clase, ids in conteo_por_clase.items()}

    def _actualizar_fps(self) -> None:
        """Registra el instante de un frame procesado."""
        self._fps_tiempos.append(time.monotonic())

    def obtener_fps(self) -> float:
        """Frames procesados en el último segundo (ventana deslizante): tras una
        pausa de la faja baja a 0 y no conserva el valor anterior."""
        ahora = time.monotonic()
        # list() copia la deque de una vez: el hilo de procesamiento puede
        # seguir agregando mientras la ruta de estado la lee.
        return float(sum(1 for t in list(self._fps_tiempos) if ahora - t <= 1.0))
