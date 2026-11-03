"""
ServoController — separa granos buenos de defectuosos vía servo motor.

Flujo por grano:
  1. tracker.py detecta un nuevo track_id → llama solicitar()
  2. Después de SERVO_DELAY_S (tiempo que tarda el grano en llegar al servo),
     el worker evalúa la mejor clase acumulada para ese ID.
  3. Si la clase tiene equivalencia de defecto → SERVO:DEFECTO
     Si no (o si no hay detección) → SERVO:BUENO
  4. Tras SERVO_HOLD_S, el servo vuelve a BUENO (canal por defecto).

Ajustar SERVO_DELAY_S y SERVO_HOLD_S en src/config.py (o vía .env)
según velocidad de la faja y distancia cámara-servo.
"""
import heapq
import itertools
import threading
import time
from typing import Callable

from src.config import Config
from src.utilities.arduino_serial import arduino_serial


class _Solicitud:
    __slots__ = ("obtener_clase", "equivalencias", "ejecutar_en")

    def __init__(
        self,
        obtener_clase: Callable[[], str | None],
        equivalencias: dict[str, float],
        ejecutar_en: float,
    ) -> None:
        self.obtener_clase = obtener_clase
        self.equivalencias = equivalencias
        self.ejecutar_en = ejecutar_en


class ServoController:
    """
    Hilo de background que procesa la cola de granos pendientes de separación.
    """

    def __init__(self) -> None:
        # Heap ordenado por ejecutar_en: un grano visto antes se separa antes,
        # aunque haya juntado evidencia (y se haya encolado) después de otro.
        # El contador desempata instantes iguales sin comparar solicitudes.
        self._cola: list[tuple[float, int, _Solicitud]] = []
        self._secuencia = itertools.count()
        self._lock = threading.Lock()
        self._activo = True
        self._bloqueado = False  # True cuando la cámara se desconecta
        self._thread = threading.Thread(
            target=self._worker,
            daemon=True,
            name="servo-controller",
        )
        self._thread.start()

    def solicitar(
        self,
        obtener_clase: Callable[[], str | None],
        equivalencias: dict[str, float],
        t_referencia: float | None = None,
    ) -> None:
        """
        Programa la evaluación y separación de un grano.

        Args:
            obtener_clase: callable que retorna la mejor clase detectada para
                           este track_id en el momento de ejecución (o None).
            equivalencias: EQUIVALENCIAS_DEFECTO del modelo activo.
            t_referencia: time.monotonic() de captura del frame donde se vio el
                          grano por primera vez. Sin él, se usa el instante actual
                          (incluye la latencia de inferencia como error).
        """
        base = t_referencia if t_referencia is not None else time.monotonic()
        ejecutar_en = base + Config.SERVO_DELAY_S
        solicitud = _Solicitud(
            obtener_clase=obtener_clase,
            equivalencias=equivalencias,
            ejecutar_en=ejecutar_en,
        )
        with self._lock:
            heapq.heappush(self._cola, (ejecutar_en, next(self._secuencia), solicitud))

    def _worker(self) -> None:
        """Procesa solicitudes pendientes cada 10 ms."""
        while self._activo:
            pendiente = self._sacar_pendiente()

            if pendiente is not None:
                if self._es_defecto(pendiente):
                    self._separar_defecto()
            else:
                time.sleep(0.01)

    def _sacar_pendiente(self) -> _Solicitud | None:
        """Extrae la solicitud que vence primero, si ya venció; si no, None."""
        with self._lock:
            if not self._bloqueado and self._cola and self._cola[0][0] <= time.monotonic():
                return heapq.heappop(self._cola)[2]
        return None

    @staticmethod
    def _es_defecto(solicitud: _Solicitud) -> bool:
        clase = solicitud.obtener_clase()
        return clase is not None and solicitud.equivalencias.get(clase, 0.0) > 0.0

    @staticmethod
    def _enviar_con_reintento(cmd: str, intentos: int = 3) -> bool:
        """Envía un comando reintentando ante fallas del puerto serial.
        Sin esto, un SERVO:BUENO perdido deja el servo atascado en DEFECTO."""
        for _ in range(intentos):
            if arduino_serial.enviar_comando(cmd):
                return True
            time.sleep(0.05)
        return False

    def _separar_defecto(self) -> None:
        """
        Mueve el servo a DEFECTO y lo sostiene SERVO_HOLD_S. Si durante el hold
        vence otra solicitud que también es defecto, extiende el hold en lugar de
        volver a BUENO — evita el parpadeo DEFECTO→BUENO→DEFECTO que dejaba pasar
        granos defectuosos consecutivos, y evalúa la cola sin retraso acumulado.
        """
        self._enviar_con_reintento("SERVO:DEFECTO")
        fin_hold = time.monotonic() + Config.SERVO_HOLD_S

        while self._activo and time.monotonic() < fin_hold:
            siguiente = self._sacar_pendiente()
            if siguiente is None:
                time.sleep(0.005)
                continue
            if self._es_defecto(siguiente):
                fin_hold = time.monotonic() + Config.SERVO_HOLD_S
            # Si es bueno no hay acción posible: el servo ya está en DEFECTO
            # sosteniendo al grano anterior; volverá a BUENO al terminar el hold.

        # Mantener el lock durante el envío garantiza el orden frente a
        # bloquear(): si la emergencia gana el lock primero, no se envía BUENO.
        with self._lock:
            if not self._bloqueado:
                self._enviar_con_reintento("SERVO:BUENO")

    def bloquear(self) -> None:
        """
        Bloquea el servo en posición DEFECTO por emergencia (cámara desconectada).
        Descarta toda la cola. El worker no enviará SERVO:BUENO hasta desbloquear.
        """
        with self._lock:
            self._bloqueado = True
            self._cola.clear()

    def desbloquear(self) -> None:
        """Restaura operación normal (llamar al reiniciar el monitoreo)."""
        with self._lock:
            self._bloqueado = False

    def limpiar_cola(self) -> None:
        """Descarta solicitudes pendientes (llamar al resetear el lote)."""
        with self._lock:
            self._cola.clear()

    def cerrar(self) -> None:
        self._activo = False
        if self._thread.is_alive():
            self._thread.join(timeout=1.0)


servo_controller = ServoController()
