"""
TrackerService - Integración de Captura + Procesamiento ML
Coordina CamaraService (captura de frames) con CoffeeRenTracker (procesamiento YOLO).
"""

import os
import threading
import time

from src.config import Config
from src.services.camara_service import camara_service
from src.ml.tracker import CoffeeRenTracker
from src.ml.classifier import generar_reporte
from src.utilities.arduino_serial import arduino_serial
from src.utilities.eventos_monitoreo import registro_eventos
from src.utilities.servo_controller import servo_controller
from src.utilities.uuid_utils import uuid7

# Piso de confianza que YOLO usa para emitir una deteccion. Bajo a proposito:
# ByteTrack asocia y sostiene los tracks con sus propios umbrales (bytetrack.yaml)
# y el conteo final resuelve cada track por confianza acumulada por clase
# (MARGEN_DEFECTO) y marca 'desconocido' lo que nunca supera
# UMBRAL_CONF_CONOCIDO (tracker.py, _resolver_clase_display). Un piso
# alto aqui mataba la etapa de recuperacion de baja confianza de ByteTrack y hacia
# que los granos que se tocan (menor conf por ambiguedad) no se dibujaran.
# El servo se protege aparte con la compuerta de evidencia del tracker.
CONF_THRESHOLD = 0.15

# Raíz del proyecto: ML_EVIDENCIA_DIR relativo se resuelve desde aquí, no desde
# el directorio donde se lanzó uvicorn.
_RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TrackerService:
    """
    Servicio que gestiona la captura de video y procesamiento de defectos en tiempo real.
    - Captura frames desde CamaraService (resolución y fps de Config.CAM_*)
    - Procesa con CoffeeRenTracker (YOLO + ByteTrack)
    - Calcula los defectos equivalentes con classifier.py
    """

    def __init__(self, model_name: str = "yolov26n_2cls"):
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

        # Evaluación a la que pertenece el lote en curso: las evidencias de
        # materia extraña se archivan bajo su carpeta y los eventos se persisten
        # contra ella al finalizar.
        self._evaluacion_id: str | None = None
        self._evidencias_guardadas: int = 0

    def iniciar(self, evaluacion_id: str | None = None) -> bool:
        """
        Inicia el procesamiento YOLO. La cámara ya debe estar conectada desde el arranque.

        Args:
            evaluacion_id: evaluación dueña del lote, para archivar evidencias y
                eventos. None = monitoreo suelto (vista /prueba), sin persistencia.

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

            # La cámara se pre-conecta en el lifespan; reconectar solo si falló
            if not camara_service.esta_disponible():
                print("Cámara no disponible, intentando reconectar...")
                if not camara_service.iniciar():
                    print("No se pudo conectar la cámara")
                    return False

            print("Cámara disponible")

            # Resetear conteo y ByteTrack para nueva sesión (IDs empezarán desde 1)
            self.tracker.resetear_conteo()

            # Lote nuevo: el registro de eventos arranca su reloj aquí, de modo
            # que el segundo de cada evento sea relativo al inicio real del lote.
            self._evaluacion_id = evaluacion_id
            self._evidencias_guardadas = 0
            registro_eventos.iniciar_lote(evaluacion_id)
            registro_eventos.registrar(
                tipo="inicio",
                mensaje=f"Monitoreo iniciado — modelo {self.model_name}.",
                severidad="ok",
            )

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
        """Detiene el procesamiento YOLO. La cámara permanece conectada."""
        with self._lock:
            self.activo = False

        if self._thread:
            self._thread.join(timeout=2.0)
            self._thread = None

        with self._lock:
            self._frame_anotado = None  # limpiar frame viejo para próxima sesión

        # Fail-safe: al terminar monitoreo, forzar apagado de la faja desde backend.
        # Esto cubre casos donde el frontend no alcanza a enviar OFF.
        arduino_serial.enviar_comando("OFF")
        registro_eventos.registrar(
            tipo="fin",
            mensaje="Monitoreo detenido. Faja apagada.",
            severidad="info",
        )
        print("TrackerService detenido — cámara permanece conectada")

    def _on_camara_desconectada(self) -> None:
        """Reacción de emergencia ante pérdida de cámara."""
        self.activo = False
        self._camara_desconectada = True
        self._error_camara = "Desconexión con cámara. La clasificación se ha detenido."

        # Seguridad: sin cámara no debe seguir corriendo la faja.
        arduino_serial.enviar_comando("OFF")
        servo_controller.bloquear()
        arduino_serial.enviar_comando("SERVO:DEFECTO")
        print("Cámara desconectada — servo fijado en posición DEFECTO")

    def _loop_procesamiento(self) -> None:
        """Loop principal de procesamiento (corre en hilo separado).

        No corre YOLO en cada frame de la cámara (~90 fps): limita la detección
        a ML_DETECTOR_FPS y, si ML_GATE_MOVIMIENTO está activo, la omite cuando
        el frame casi no cambió (faja detenida). Menos inferencia = menos
        GPU/CPU sin perder precisión de conteo.
        """
        t_anterior = time.time()
        frame_count = 0
        intervalo_min = 1.0 / Config.ML_DETECTOR_FPS if Config.ML_DETECTOR_FPS > 0 else 0.0
        t_ultima_inferencia = 0.0

        while self.activo:
            # Detectar desconexión de cámara
            if not camara_service.esta_disponible():
                self._on_camara_desconectada()
                # El evento se emite aquí y no dentro de _on_camara_desconectada:
                # esa rutina es el modo de emergencia del hardware y no se toca.
                registro_eventos.registrar(
                    tipo="camara",
                    mensaje=self._error_camara or "Desconexión con cámara. La clasificación se detuvo.",
                    severidad="error",
                )
                break

            # Esperar nuevo frame y obtener BGR directo (sin ciclo JPEG). Si vence
            # el timeout no hay frame nuevo: no se reprocesa el anterior.
            if not camara_service.esperar_frame(timeout=1.0):
                continue
            frame, ts_frame = camara_service.obtener_frame_bgr()
            if frame is None:
                continue

            # Cadencia: no correr YOLO más rápido que ML_DETECTOR_FPS.
            ahora = time.monotonic()
            if intervalo_min and (ahora - t_ultima_inferencia) < intervalo_min:
                time.sleep(min(intervalo_min - (ahora - t_ultima_inferencia), 0.02))
                continue
            t_ultima_inferencia = ahora

            # Gate por movimiento: si la faja está quieta, saltarse la inferencia.
            if Config.ML_GATE_MOVIMIENTO and not self.tracker.hay_movimiento(frame):
                time.sleep(0.02)
                continue

            # Procesar con tracker
            frame_anotado_jpeg = self.tracker.procesar_frame(frame, ts_frame)

            # Archivar los objetos extraños que el tracker recortó en este frame.
            self._guardar_evidencias()

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

    def _guardar_evidencias(self) -> None:
        """Escribe a disco los recortes de materia extraña y emite su evento.

        El tracker solo recorta y encola (no toca disco). Aquí se archiva bajo la
        carpeta de la evaluación y se publica el aviso que verá el operario, con
        el segundo del lote y la miniatura.

        Todo va en try/except: un fallo de disco no puede romper el loop de
        procesamiento ni detener la clasificación.
        """
        try:
            pendientes = self.tracker.drenar_evidencias()
        except Exception as exc:
            print(f"[evidencia] Error drenando la cola: {exc}")
            return

        for ev in pendientes:
            imagen_url: str | None = None
            try:
                # El aviso al operario se emite SIEMPRE; lo que el flag y el tope
                # gobiernan es solo la foto. Sin evidencia archivada el operario
                # igual tiene que enterarse de que se desvió materia extraña.
                if (Config.ML_EVIDENCIA_DESCONOCIDOS
                        and self._evaluacion_id
                        and self._evidencias_guardadas < Config.ML_EVIDENCIA_MAX_POR_LOTE):
                    carpeta = os.path.join(_RAIZ, Config.ML_EVIDENCIA_DIR, self._evaluacion_id)
                    os.makedirs(carpeta, exist_ok=True)
                    nombre = f"{uuid7()}.jpg"
                    with open(os.path.join(carpeta, nombre), "wb") as f:
                        f.write(ev["jpeg"])
                    self._evidencias_guardadas += 1
                    imagen_url = f"/resources/desconocidos/{self._evaluacion_id}/{nombre}"
            except Exception as exc:
                print(f"[evidencia] Error guardando recorte: {exc}")

            registro_eventos.registrar(
                tipo="objeto_desconocido",
                mensaje="Objeto extraño detectado — desviado al canal de defecto.",
                severidad="alerta",
                imagen_url=imagen_url,
                datos={
                    "track_id": ev.get("track_id"),
                    "ancho_px": ev.get("ancho_px"),
                    "alto_px":  ev.get("alto_px"),
                    "conf":     ev.get("conf"),
                },
            )

    @property
    def evaluacion_id(self) -> str | None:
        """Evaluación dueña del lote en curso, o None si el monitoreo es suelto."""
        return self._evaluacion_id

    def obtener_eventos(self, desde: int = 0) -> dict:
        """Eventos del lote posteriores al cursor, para el panel de monitoreo."""
        eventos, cursor = registro_eventos.desde(desde)
        return {"eventos": eventos, "cursor": cursor}

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
        desc = self.tracker.CLASE_DESCONOCIDO
        # 'desconocido' (materia extraña: piedra, pajilla...) tiene equivalencia
        # > 0 → cuenta como defecto y se desvía al canal DEFECTO. Se reporta
        # además por separado para que el operario vea cuántos objetos extraños
        # se retiraron, distinto de los granos defectuosos.
        total_defectos = sum(v for k, v in conteo.items() if eq.get(k, 0.0) > 0.0)
        total_sanos    = sum(v for k, v in conteo.items() if eq.get(k, 0.0) == 0.0)
        total_desconocidos = conteo.get(desc, 0)
        conteo_agrupado = {
            grupo: sum(conteo.get(c, 0) for c in clases)
            for grupo, clases in self.tracker.GRUPOS_DISPLAY.items()
        }
        ts = self.tracker.ultima_deteccion_frame_ts
        segundos_sin_deteccion = round(time.time() - ts, 1) if ts is not None else None
        return {
            "conteo":                  conteo,
            # total_defectos + total_sanos = total_granos (categorías disjuntas).
            # total_desconocidos NO es una cuarta categoría: es el subconjunto de
            # total_defectos que fue materia extraña (no grano defectuoso). No
            # sumarlo aparte.
            "total_granos":            total_defectos + total_sanos,
            "total_defectos":          total_defectos,
            "total_sanos":             total_sanos,
            "total_desconocidos":      total_desconocidos,
            "conteo_agrupado":         conteo_agrupado,
            "clases_detectadas":       len(conteo),
            "segundos_sin_deteccion":  segundos_sin_deteccion,
        }

    def conteo_de_evaluacion(self, evaluacion_id: str) -> dict | None:
        """Conteo del lote en memoria si pertenece a esta evaluación; None si el
        tracker ya trabaja con otro lote o se reinició. Es la única fuente del
        conteo que se guarda al finalizar: el navegador no lo envía."""
        if self._evaluacion_id != evaluacion_id:
            return None
        return self.obtener_conteo_enriquecido()

    def generar_reporte_lote(self) -> dict:
        """
        Genera reporte de clasificación del lote actual. 'desconocido' (materia
        extraña) entra al conteo con equivalencia 1.0, como defecto primario SCA.

        Returns:
            dict: {total_granos_analizados, total_defectos, detalle_por_clase, resumen}
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



# Instancia global del servicio
tracker_service = TrackerService(model_name="yolov26n_2cls")
