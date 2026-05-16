import threading
import cv2


class CamaraService:
    """
    Hilo dedicado de captura: drena la cámara al máximo FPS del sensor
    y guarda solo el último frame. El streaming siempre entrega el frame
    más reciente, sin importar cuántos clientes haya o qué tan rápido lean.
    """

    def __init__(self) -> None:
        self._cap: cv2.VideoCapture | None = None
        self._cap_lock = threading.Lock()
        self._latest_jpeg: bytes | None = None
        self._frame_lock = threading.Lock()
        self._new_frame = threading.Event()
        self._running = False
        self._thread: threading.Thread | None = None
        self._passthrough = False

    # ── Ciclo de captura (hilo dedicado) ──────────────────────────────

    def _capture_loop(self) -> None:
        while self._running:
            cap = self._cap
            if cap is None or not cap.isOpened():
                break
            ret, frame = cap.read()
            if not ret or frame is None:
                continue
            if self._passthrough:
                jpeg = frame.tobytes()
            else:
                _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
                jpeg = buf.tobytes()
            with self._frame_lock:
                self._latest_jpeg = jpeg
            self._new_frame.set()

    # ── API pública ────────────────────────────────────────────────────

    def iniciar(self, indice: int = 0) -> bool:
        with self._cap_lock:
            if self._running:
                return True
            for idx in (indice, indice + 1):
                cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
                if not cap.isOpened():
                    cap.release()
                    continue
                cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                cap.set(cv2.CAP_PROP_FPS, 60)
                # Buffer mínimo: el hilo drena el sensor antes de que acumule
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                # Passthrough MJPEG: bytes nativos del sensor sin decodificar ni re-encodear
                cap.set(cv2.CAP_PROP_CONVERT_RGB, 0)
                ret, test = cap.read()
                if ret and test is not None and test.ndim == 1 and test.nbytes > 1000:
                    self._passthrough = True
                else:
                    cap.set(cv2.CAP_PROP_CONVERT_RGB, 1)
                    self._passthrough = False
                self._cap = cap
                self._running = True
                self._thread = threading.Thread(
                    target=self._capture_loop, daemon=True, name="camara-capture"
                )
                self._thread.start()
                return True
            return False

    def cerrar(self) -> None:
        self._running = False
        self._new_frame.set()  # desbloquea cualquier hilo esperando
        with self._cap_lock:
            if self._cap:
                self._cap.release()
                self._cap = None
        if self._thread:
            self._thread.join(timeout=2)
            self._thread = None

    def esta_disponible(self) -> bool:
        return self._running and self._cap is not None and self._cap.isOpened()

    def esperar_frame(self, timeout: float = 1.0) -> bytes | None:
        """Bloquea hasta que haya un frame nuevo o expire el timeout."""
        self._new_frame.wait(timeout)
        self._new_frame.clear()
        with self._frame_lock:
            return self._latest_jpeg


camara_service = CamaraService()
