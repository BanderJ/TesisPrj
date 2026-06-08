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
        self._cola: list[_Solicitud] = []
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
    ) -> None:
        """
        Programa la evaluación y separación de un grano.

        Args:
            obtener_clase: callable que retorna la mejor clase detectada para
                           este track_id en el momento de ejecución (o None).
            equivalencias: EQUIVALENCIAS_DEFECTO del modelo activo.
        """
        ejecutar_en = time.monotonic() + Config.SERVO_DELAY_S
        with self._lock:
            self._cola.append(
                _Solicitud(
                    obtener_clase=obtener_clase,
                    equivalencias=equivalencias,
                    ejecutar_en=ejecutar_en,
                )
            )

    def _worker(self) -> None:
        """Procesa solicitudes pendientes cada 10 ms."""
        while self._activo:
            ahora = time.monotonic()
            pendiente: _Solicitud | None = None

            with self._lock:
                if not self._bloqueado and self._cola and self._cola[0].ejecutar_en <= ahora:
                    pendiente = self._cola.pop(0)

            if pendiente is not None:
                clase = pendiente.obtener_clase()
                es_defecto = clase is not None and pendiente.equivalencias.get(clase, 0.0) > 0.0

                if es_defecto:
                    arduino_serial.enviar_comando("SERVO:DEFECTO")
                    time.sleep(Config.SERVO_HOLD_S)
                    # Solo volver a BUENO si no estamos en modo emergencia
                    with self._lock:
                        if not self._bloqueado:
                            arduino_serial.enviar_comando("SERVO:BUENO")
                else:
                    arduino_serial.enviar_comando("SERVO:BUENO")
            else:
                time.sleep(0.01)

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
