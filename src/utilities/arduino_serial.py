"""
Utilidad de comunicación serial con Arduino.

Protocolo (9600 baud):
  Arduino → backend (lecturas continuas):
    LISTO:4.34    → tapa cerrada, muestra detectada (distancia < umbral)
    NO_LISTO:5.21 → sin muestra o tapa abierta
    PESO:1234.56   → lectura de la celda de carga en gramos (promedio deslizante)
    TARE:OK        → confirmación de tara completada
    SISTEMA:LISTO  → Arduino inicializado
  Backend → Arduino (comandos):
    ON             → iniciar faja
    OFF            → detener faja y resetear servo a BUENO
    SERVO:BUENO    → servo al canal de granos buenos
    SERVO:DEFECTO  → servo al canal de granos defectuosos
    TARE           → tarar la báscula (poner en cero)
    SCALE:<factor> → actualizar factor de calibración

Un hilo lector de fondo parsea todas las líneas entrantes y actualiza el
estado cacheado. obtener_estado() y obtener_peso() retornan siempre los
últimos valores recibidos, sin bloquear la solicitud HTTP.
"""
import threading
import time
from dataclasses import dataclass

try:
    import serial
    _SERIAL_DISPONIBLE = True
except ImportError:
    _SERIAL_DISPONIBLE = False

from src.config import Config


@dataclass
class EstadoArduino:
    listo: bool = False
    distancia: float | None = None
    conectado: bool = False
    error: str | None = None


class ArduinoSerial:
    def __init__(self) -> None:
        self._puerto: object | None = None
        self._write_lock = threading.Lock()   # solo para escritura al puerto
        self._state_lock = threading.Lock()   # para lectura/escritura del estado cacheado
        self._estado = EstadoArduino()
        self._peso: float | None = None
        self._reader_thread: threading.Thread | None = None
        self._activo = False
        self._ultimo_intento_reconexion: float = 0.0  # throttle: no reintentar antes de 10 s

    # ── Conexión ──────────────────────────────────────────────────────────────

    def _conectar(self) -> bool:
        """Abre el puerto serial y arranca el hilo lector. Retorna True si OK."""
        if not _SERIAL_DISPONIBLE:
            with self._state_lock:
                self._estado = EstadoArduino(error="pyserial no instalado")
            return False
        try:
            self._puerto = serial.Serial(
                port=Config.ARDUINO_PORT,
                baudrate=Config.ARDUINO_BAUDRATE,
                timeout=1.0,  # readline espera hasta 1 s por línea
            )
            self._activo = True
            with self._state_lock:
                self._estado = EstadoArduino(conectado=True)
            self._reader_thread = threading.Thread(
                target=self._reader_loop,
                daemon=True,
                name="arduino-reader",
            )
            self._reader_thread.start()
            return True
        except Exception as exc:
            self._puerto = None
            self._activo = False
            with self._state_lock:
                self._estado = EstadoArduino(error=str(exc))
            return False

    def _asegurar_conexion(self) -> bool:
        """Reconecta si el hilo lector está muerto. Retorna True si conectado.
        Throttlea reintentos a uno cada 10 s para no bloquear requests HTTP."""
        if self._activo and self._puerto and self._puerto.is_open:
            return True
        # Throttle: no reintentar si el último intento fue hace menos de 10 s
        ahora = time.time()
        if ahora - self._ultimo_intento_reconexion < 10.0:
            return False
        self._ultimo_intento_reconexion = ahora
        if self._puerto:
            try:
                self._puerto.close()
            except Exception:
                pass
            self._puerto = None
        self._activo = False
        return self._conectar()

    # ── Hilo lector ───────────────────────────────────────────────────────────

    def _reader_loop(self) -> None:
        """Lee líneas del Arduino de forma continua y actualiza el estado cacheado."""
        while self._activo and self._puerto and self._puerto.is_open:
            try:
                linea = self._puerto.readline().decode("utf-8", errors="ignore").strip()
                if linea:
                    self._procesar_linea(linea)
            except Exception as exc:
                with self._state_lock:
                    self._estado = EstadoArduino(conectado=False, error=str(exc))
                self._activo = False
                break

    def _procesar_linea(self, linea: str) -> None:
        if linea.startswith("LISTO:") or linea.startswith("NO_LISTO:"):
            try:
                prefijo, dist_str = linea.split(":", 1)
                distancia = float(dist_str)
                listo = prefijo == "LISTO"
                with self._state_lock:
                    self._estado = EstadoArduino(
                        listo=listo, distancia=distancia, conectado=True
                    )
            except (ValueError, AttributeError):
                pass

        elif linea.startswith("PESO:"):
            try:
                with self._state_lock:
                    self._peso = float(linea[5:])
            except ValueError:
                pass
        # TARE:OK, SISTEMA:LISTO, SCALE:OK → sin efecto en el estado cacheado

    # ── API pública ───────────────────────────────────────────────────────────

    def obtener_estado(self) -> EstadoArduino:
        """Retorna el último estado de distancia/tapa recibido del Arduino."""
        self._asegurar_conexion()
        with self._state_lock:
            return self._estado

    def obtener_peso(self) -> float | None:
        """Retorna el último peso (gramos) leído de la celda de carga, o None."""
        self._asegurar_conexion()
        with self._state_lock:
            return self._peso

    def enviar_comando(self, cmd: str) -> bool:
        """Envía un comando al Arduino. Retorna True si se envió correctamente."""
        self._asegurar_conexion()
        with self._write_lock:
            if self._puerto is None or not self._puerto.is_open:
                return False
            try:
                self._puerto.write(f"{cmd}\n".encode("utf-8"))
                return True
            except Exception:
                self._activo = False
                return False

    def cerrar(self) -> None:
        self._activo = False
        with self._write_lock:
            if self._puerto and self._puerto.is_open:
                self._puerto.close()
            self._puerto = None


arduino_serial = ArduinoSerial()
