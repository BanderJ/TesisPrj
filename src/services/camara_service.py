import os
import re
import sys
import threading
import time

# Debe fijarse ANTES de importar cv2. Sin esto, el backend Media Foundation de
# OpenCV (el único que negocia MJPEG con la ELP en esta laptop — DSHOW en el
# build headless entrega YUY2 a 5fps) puede devolver frames negros o lentos por
# las transformaciones por hardware D3D.
os.environ.setdefault("OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS", "0")

import numpy as np
import cv2

from src.config import Config

# Nombre de dispositivo que identifica a la ELP (reporta "Global Shutter Camera").
_PATRON_ELP = re.compile(r"global\s*shutter|ar0234|\belp\b", re.I)
# Cámaras a descartar en la autodetección: webcam interna de la laptop y virtuales.
_PATRON_DESCARTE = re.compile(r"facing|integrated|internal|\bir\b|virtual|\bobs\b|depth", re.I)


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
        self._latest_frame: np.ndarray | None = None
        self._latest_ts: float | None = None  # time.monotonic() de captura del frame
        self._frame_lock = threading.Lock()
        self._new_frame = threading.Event()
        self._running = False
        self._thread: threading.Thread | None = None

    # ── Ciclo de captura (hilo dedicado) ──────────────────────────────

    def _capture_loop(self) -> None:
        errores_consecutivos = 0
        MAX_ERRORES = 10  # ~10 lecturas fallidas → cámara desconectada
        while self._running:
            cap = self._cap
            if cap is None or not cap.isOpened():
                self._running = False
                print("[CamaraService] cap cerrado inesperadamente — loop terminado")
                break
            ret, frame = cap.read()
            if not ret or frame is None:
                errores_consecutivos += 1
                if errores_consecutivos >= MAX_ERRORES:
                    self._running = False  # señal de desconexión
                    print(f"[CamaraService] {MAX_ERRORES} errores consecutivos — cámara desconectada")
                    break
                continue
            errores_consecutivos = 0
            _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
            with self._frame_lock:
                self._latest_jpeg = buf.tobytes()
                self._latest_frame = frame
                self._latest_ts = time.monotonic()
            self._new_frame.set()

    # ── Helpers de apertura ────────────────────────────────────────────

    @staticmethod
    def _abrir_captura(idx: int) -> "cv2.VideoCapture | None":
        """Abre la cámara. En Windows prueba Media Foundation primero: es el
        único backend que negocia MJPEG con la ELP en el build headless de
        OpenCV (DSHOW por índice entrega YUY2 a 5fps). CAP_ANY y DSHOW quedan
        de respaldo para otros equipos."""
        backends = (
            [cv2.CAP_MSMF, cv2.CAP_ANY, cv2.CAP_DSHOW]
            if sys.platform == "win32" else [cv2.CAP_ANY]
        )
        for backend in backends:
            cap = cv2.VideoCapture(idx, backend)
            if cap.isOpened():
                return cap
            cap.release()
        return None

    @staticmethod
    def _medir_fps(cap: "cv2.VideoCapture", n: int = 15) -> float:
        """FPS real de captura sobre n lecturas. Distingue MJPEG (>=30 fps a
        1080p, en la práctica ~88) de YUY2 sin comprimir (~5 fps en USB 2.0),
        ya que Media Foundation no reporta el FOURCC de forma fiable."""
        t0 = time.monotonic()
        leidos = sum(1 for _ in range(n) if cap.read()[0])
        dt = time.monotonic() - t0
        return leidos / dt if dt > 0 else 0.0

    @staticmethod
    def _configurar_captura(cap: "cv2.VideoCapture") -> None:
        """Aplica formato y parámetros ANTES del primer read(): en Windows el
        driver solo respeta FOURCC/resolución/FPS si se fijan antes de capturar.
        El orden importa: FOURCC → resolución → FPS."""
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, Config.CAM_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, Config.CAM_HEIGHT)
        cap.set(cv2.CAP_PROP_FPS, Config.CAM_FPS)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # mínima latencia: solo el último frame

        if Config.CAM_EXPOSURE:
            # Exposición manual: congela el grano en movimiento. Exige buena luz.
            cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, Config.CAM_AUTO_EXPOSURE_MANUAL)
            cap.set(cv2.CAP_PROP_EXPOSURE, float(Config.CAM_EXPOSURE))
        # Sin CAM_EXPOSURE no se toca la exposición: queda el AEC de fábrica.

    @staticmethod
    def _dispositivos() -> list[str]:
        """Nombres de las cámaras en orden de índice OpenCV/DirectShow.
        Devuelve [] si pygrabber no está disponible o falla la enumeración."""
        try:
            from pygrabber.dshow_graph import FilterGraph
            return FilterGraph().get_input_devices()
        except Exception as e:
            print(f"[CamaraService] no se pudo enumerar dispositivos (pygrabber): {e}")
            return []

    def _orden_indices(self, indice_base: int) -> tuple[list[int], set[int]]:
        """Calcula el orden de índices a probar y cuáles son 'confiables'
        (elegidos por nombre o forzados por el usuario: se aceptan aunque no
        negocien MJPEG). La webcam interna también da MJPEG, así que el formato
        no alcanza para distinguirla — hay que mirar el nombre del dispositivo."""
        val = Config.CAM_INDICE.strip()
        nombres = self._dispositivos()
        if nombres:
            print(f"[CamaraService] cámaras detectadas: {list(enumerate(nombres))}")

        todos = list(range(max(len(nombres), indice_base + 4)))

        # 1. Índice numérico explícito en .env
        if val.lstrip("-").isdigit():
            n = int(val)
            return [n] + [i for i in todos if i != n], {n}

        # 2. Texto explícito en .env → coincidencia por nombre
        if val:
            for i, nombre in enumerate(nombres):
                if val.lower() in nombre.lower():
                    print(f"[CamaraService] CAM_INDICE='{val}' → índice {i} ('{nombre}')")
                    return [i] + [x for x in todos if x != i], {i}
            print(f"[CamaraService] CAM_INDICE='{val}' no coincide con ninguna cámara; autodetectando")

        # 3. Autodetección: nombre tipo ELP y que no sea webcam interna / virtual
        elp = [i for i, nombre in enumerate(nombres)
               if _PATRON_ELP.search(nombre) and not _PATRON_DESCARTE.search(nombre)]
        if elp:
            print(f"[CamaraService] ELP detectada por nombre en índice(s) {elp}")
            return elp + [i for i in todos if i not in elp], set(elp)

        # 4. Sin pistas de nombre: escaneo con las virtuales/internas al final
        descartables = {i for i, nombre in enumerate(nombres) if _PATRON_DESCARTE.search(nombre)}
        reales = [i for i in todos if i not in descartables]
        return reales + [i for i in todos if i in descartables], set()

    def _activar(self, cap: "cv2.VideoCapture", idx: int, fps_medido: float) -> bool:
        """Fija el cap como activo, arranca el hilo de captura y loguea el
        estado real (FPS medido, no el nominal que el driver reporta de más)."""
        self._cap = cap
        self._running = True
        self._thread = threading.Thread(
            target=self._capture_loop, daemon=True, name="camara-capture"
        )
        self._thread.start()

        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        exp = cap.get(cv2.CAP_PROP_EXPOSURE)
        print(f"Cámara iniciada (índice {idx}, {w}x{h}, ~{fps_medido:.0f} fps real, "
              f"exposición={exp})")
        if fps_medido < 30:
            print("  ADVERTENCIA: FPS bajo — el driver está entregando formato sin "
                  "comprimir (YUY2), no MJPEG. En USB 2.0 eso limita a ~5fps. Revisá "
                  "que sea la ELP y que el cable/puerto sean USB 2.0 o superior.")
        return True

    # ── API pública ────────────────────────────────────────────────────

    def iniciar(self, indice: int = 0) -> bool:
        with self._cap_lock:
            if self._running:
                return True

            orden, confiables = self._orden_indices(indice)

            fallback = None  # (idx, cap, fps) de la primera cámara sin MJPEG, de respaldo
            for idx in orden:
                cap = None
                try:
                    cap = self._abrir_captura(idx)
                    if cap is None:
                        continue

                    self._configurar_captura(cap)

                    ret, test = cap.read()
                    if not ret or test is None:
                        print(f"[CamaraService] índice {idx}: abre pero no entrega frames")
                        cap.release()
                        continue

                    fps_medido = self._medir_fps(cap)
                    # Aceptar si la cámara es 'confiable' (ELP por nombre o índice
                    # forzado), o si el FPS real indica MJPEG (>=30). Media
                    # Foundation no reporta FOURCC, por eso se mide el FPS.
                    if idx in confiables or fps_medido >= 30:
                        if fallback is not None:
                            fallback[1].release()
                        return self._activar(cap, idx, fps_medido)

                    print(f"[CamaraService] índice {idx}: ~{fps_medido:.0f} fps (sin comprimir) — se descarta")
                    if fallback is None:
                        fallback = (idx, cap, fps_medido)
                    else:
                        cap.release()

                except Exception as e:
                    print(f"[CamaraService] error en índice {idx}: {e}")
                    if cap is not None and (fallback is None or cap is not fallback[1]):
                        cap.release()
                    continue

            if fallback is not None:
                idx, cap, fps_medido = fallback
                return self._activar(cap, idx, fps_medido)

            print(f"[CamaraService] no se encontró cámara utilizable (índices probados: {orden})")
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

    def obtener_frame_bgr(self) -> tuple[np.ndarray | None, float | None]:
        """Retorna el último frame BGR crudo y su timestamp de captura
        (time.monotonic()). El timestamp permite programar el servo desde el
        momento real de captura, sin el sesgo de la latencia de inferencia."""
        with self._frame_lock:
            return self._latest_frame, self._latest_ts


camara_service = CamaraService()
