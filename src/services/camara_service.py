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
        errores_consecutivos = 0
        MAX_ERRORES = 10  # ~10 lecturas fallidas → cámara desconectada
        while self._running:
            cap = self._cap
            if cap is None or not cap.isOpened():
                self._running = False
                break
            ret, frame = cap.read()
            if not ret or frame is None:
                errores_consecutivos += 1
                if errores_consecutivos >= MAX_ERRORES:
                    self._running = False  # señal de desconexión
                    break
                continue
            errores_consecutivos = 0
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

            # Intentar con índices 0 y 1
            for idx in (indice, indice + 1):
                try:
                    # Intentar abrir con CAP_ANY primero (más flexible)
                    cap = cv2.VideoCapture(idx)

                    if not cap.isOpened():
                        cap.release()
                        continue

                    # NO forzar resolución específica - usar lo que la cámara soporta
                    # Setear buffer mínimo para bajo latency
                    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

                    # Intentar MJPEG si la cámara lo soporta
                    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))

                    # Obtener resolución y FPS reales
                    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    fps = cap.get(cv2.CAP_PROP_FPS)

                    # Leer frame de prueba para verificar que funciona
                    ret, test = cap.read()
                    if not ret or test is None:
                        print(f"Cámara índice {idx} no devuelve frames")
                        cap.release()
                        continue

                    # Detectar si passthrough MJPEG funciona
                    cap.set(cv2.CAP_PROP_CONVERT_RGB, 0)
                    ret, test2 = cap.read()
                    if ret and test2 is not None and test2.ndim == 1 and test2.nbytes > 1000:
                        self._passthrough = True
                    else:
                        cap.set(cv2.CAP_PROP_CONVERT_RGB, 1)
                        self._passthrough = False

                    # Iniciar captura
                    self._cap = cap
                    self._running = True
                    self._thread = threading.Thread(
                        target=self._capture_loop, daemon=True, name="camara-capture"
                    )
                    self._thread.start()

                    print(f"Cámara iniciada (índice {idx}, {w}x{h} @ {fps}fps, passthrough={self._passthrough})")
                    return True

                except Exception as e:
                    print(f"Error inicializando cámara índice {idx}: {e}")
                    continue

            print("No se encontró cámara disponible en índices 0-1")
            return False

    def cerrar(self) -> None:
        self._running = False
        self._new_frame.set()
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
