import threading
import cv2
import os


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
        self._simulada = False
        self._cap_simulada = None

    # ── Ciclo de captura (hilo dedicado) ──────────────────────────────

    def _capture_loop(self) -> None:
        while self._running:
            cap = self._cap
            if cap is None or not cap.isOpened():
                break
            ret, frame = cap.read()
            if not ret or frame is None:
                continue
            # Siempre codificar a JPEG (nunca pasar bytes crudos)
            success, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
            if not success:
                continue
            jpeg = buf.tobytes()
            with self._frame_lock:
                self._latest_jpeg = jpeg
            self._new_frame.set()

    def _capture_loop_simulada(self) -> None:
        """Loop para cámara simulada (fallback sin hardware)."""
        if not self._cap_simulada:
            return
        self._cap_simulada.iniciar()
        while self._running:
            jpeg = self._cap_simulada.esperar_frame(timeout=1.0)
            if jpeg is None:
                continue
            with self._frame_lock:
                self._latest_jpeg = jpeg
            self._new_frame.set()

    # ── API pública ────────────────────────────────────────────────────

    def iniciar(self, indice: int = 0) -> bool:
        with self._cap_lock:
            if self._running:
                return True
            for idx in (indice, indice + 1, 1, 2):
                try:
                    cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
                    if not cap.isOpened():
                        print(f"⚠️  Cámara índice {idx} no disponible")
                        cap.release()
                        continue
                    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                    cap.set(cv2.CAP_PROP_FPS, 60)
                    # Buffer mínimo: el hilo drena el sensor antes de que acumule
                    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                    # Passthrough MJPEG: bytes nativos del sensor sin decodificar ni re-encodear
                    cap.set(cv2.CAP_PROP_CONVERT_RGB, 1)
                    self._cap = cap
                    self._running = True
                    self._thread = threading.Thread(
                        target=self._capture_loop, daemon=True, name="camara-capture"
                    )
                    self._thread.start()
                    print(f"✅ Cámara iniciada (índice {idx}, passthrough={self._passthrough})")
                    return True
                except Exception as e:
                    print(f"❌ Error inicializando cámara índice {idx}: {e}")
                    continue
            print("❌ No se encontró ninguna cámara disponible en índices 0-1")
            print("⚠️  Usando cámara simulada (frames de prueba) para desarrollo")

            try:
                from src.services.camara_simulada import camara_simulada
                self._simulada = True
                self._cap_simulada = camara_simulada
                self._running = True
                self._thread = threading.Thread(
                    target=self._capture_loop_simulada, daemon=True, name="camara-simulada-wrapper"
                )
                self._thread.start()
                print("✅ Cámara simulada iniciada")
                return True
            except Exception as e:
                print(f"❌ No se pudo iniciar cámara simulada: {e}")
                return False

    def cerrar(self) -> None:
        self._running = False
        self._new_frame.set()  # desbloquea cualquier hilo esperando
        if self._simulada and self._cap_simulada:
            self._cap_simulada.cerrar()
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
