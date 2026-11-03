"""
Registro de eventos del monitoreo — retroalimentación al operario.

Durante el monitoreo (la función principal del sistema) el operario necesita
saber qué está haciendo el sistema y por qué: cuándo arrancó el modelo, cuándo
se perdió la cámara, cuándo apareció materia extraña y en qué segundo del lote.
Antes esos hechos ocurrían solo dentro del hilo del tracker y se perdían.

Este módulo es el buffer intermedio: el hilo del tracker escribe, la ruta HTTP
lee con un cursor incremental (`desde`) y el service los persiste al finalizar
la evaluación.

El SEGUNDO de cada evento se calcula con el reloj del backend contra el inicio
del lote, no con el cronómetro del navegador: así el dato que queda en BD es
auditable aunque el operario recargue la pestaña a mitad del lote.

Ningún método propaga excepciones al pipeline: registrar un evento jamás puede
tumbar la clasificación (mismo criterio que MedidorLatencia).
"""
import threading
import time
from collections import deque
from typing import Any

# Severidades admitidas. El frontend las usa como clase CSS (log-<severidad>)
# y la tabla EVENTO_MONITOREO las guarda tal cual.
SEVERIDADES: tuple[str, ...] = ("info", "ok", "alerta", "error")


class RegistroEventos:
    """Buffer acotado de eventos del lote en curso, seguro entre hilos.

    Productor: el hilo `tracker-processing` y los services del monitoreo.
    Consumidores: la ruta GET /video/eventos (cursor incremental) y
    evaluacion_service al finalizar (volcado completo).
    """

    def __init__(self, maxlen: int = 500) -> None:
        self._eventos: deque[dict[str, Any]] = deque(maxlen=maxlen)
        self._lock = threading.Lock()
        self._seq: int = 0
        self._t0: float | None = None
        self._evaluacion_id: str | None = None

    # ── Ciclo de vida del lote ────────────────────────────────────────────

    def iniciar_lote(self, evaluacion_id: str | None) -> None:
        """Arranca un lote nuevo: fija el t0, limpia el buffer y el cursor."""
        with self._lock:
            self._eventos.clear()
            self._seq = 0
            self._t0 = time.time()
            self._evaluacion_id = evaluacion_id

    @property
    def evaluacion_id(self) -> str | None:
        with self._lock:
            return self._evaluacion_id

    # ── Escritura ─────────────────────────────────────────────────────────

    def registrar(
        self,
        tipo: str,
        mensaje: str,
        severidad: str = "info",
        imagen_url: str | None = None,
        datos: dict[str, Any] | None = None,
    ) -> None:
        """Agrega un evento al lote en curso. Nunca lanza."""
        try:
            if severidad not in SEVERIDADES:
                severidad = "info"
            with self._lock:
                t0 = self._t0 if self._t0 is not None else time.time()
                self._seq += 1
                self._eventos.append({
                    "seq":        self._seq,
                    "segundo":    max(0, int(time.time() - t0)),
                    "tipo":       tipo,
                    "severidad":  severidad,
                    "mensaje":    mensaje,
                    "imagen_url": imagen_url,
                    "datos":      datos,
                })
        except Exception as exc:
            # Registrar jamás puede tumbar la clasificación.
            print(f"[eventos] Error registrando evento: {exc}")

    # ── Lectura ───────────────────────────────────────────────────────────

    def desde(self, cursor: int) -> tuple[list[dict[str, Any]], int]:
        """Eventos con seq > cursor y el cursor actualizado.

        Ambos salen bajo el MISMO lock a propósito: leer la lista y el cursor en
        dos llamadas dejaba pasar un evento registrado entre una y otra, que
        quedaba por debajo del cursor devuelto y no se mostraba nunca.
        """
        with self._lock:
            return [e for e in self._eventos if e["seq"] > cursor], self._seq

    def todos(self) -> list[dict[str, Any]]:
        """Volcado completo del lote (lo que se persiste al finalizar)."""
        with self._lock:
            return list(self._eventos)


# Instancia global — un solo lote a la vez, igual que el tracker.
registro_eventos = RegistroEventos()
