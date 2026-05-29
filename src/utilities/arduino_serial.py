"""
Utilidad de comunicación serial con Arduino.

Protocolo (9600 baud):
  Lectura (Arduino → backend, cada 100 ms):
    LISTO:15.34    → tapa cerrada, muestra detectada
    NO_LISTO:45.21 → sin muestra o tapa abierta
  Escritura (backend → Arduino):
    ON  → iniciar faja
    OFF → detener faja
"""
import threading
from dataclasses import dataclass, field

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
        self._puerto: object | None = None  # serial.Serial cuando conectado
        self._lock = threading.Lock()
        self._ultimo_estado = EstadoArduino()

    def _conectar(self) -> None:
        if not _SERIAL_DISPONIBLE:
            self._ultimo_estado = EstadoArduino(error="pyserial no instalado")
            return
        try:
            self._puerto = serial.Serial(
                port=Config.ARDUINO_PORT,
                baudrate=Config.ARDUINO_BAUDRATE,
                timeout=0.35,
            )
            self._ultimo_estado = EstadoArduino(conectado=True)
        except Exception as exc:
            self._puerto = None
            self._ultimo_estado = EstadoArduino(error=str(exc))

    def obtener_estado(self) -> EstadoArduino:
        with self._lock:
            if self._puerto is None or not self._puerto.is_open:
                self._conectar()
                if self._puerto is None:
                    return self._ultimo_estado

            try:
                # Descartar lecturas acumuladas para obtener dato fresco
                self._puerto.reset_input_buffer()
                # Arduino envía cada 100ms; timeout=0.35s garantiza al menos una línea
                linea = self._puerto.readline().decode("utf-8", errors="ignore").strip()
                if linea:
                    self._ultimo_estado = self._parsear(linea)
            except Exception as exc:
                self._ultimo_estado = EstadoArduino(conectado=False, error=str(exc))
                self._puerto = None  # forzar reconexión en siguiente llamada

            return self._ultimo_estado

    def _parsear(self, linea: str) -> EstadoArduino:
        # Espera "LISTO:15.34" o "NO_LISTO:45.21"
        try:
            estado_str, dist_str = linea.split(":", 1)
            distancia = float(dist_str)
            listo = estado_str.strip() == "LISTO"
            return EstadoArduino(listo=listo, distancia=distancia, conectado=True)
        except (ValueError, AttributeError):
            return EstadoArduino(conectado=True, error=f"Línea no reconocida: {linea!r}")

    def enviar_comando(self, cmd: str) -> bool:
        """Envía un comando al Arduino (ON / OFF). Retorna True si se envió."""
        with self._lock:
            if self._puerto is None or not self._puerto.is_open:
                self._conectar()
                if self._puerto is None:
                    return False
            try:
                self._puerto.write(f"{cmd}\n".encode("utf-8"))
                return True
            except Exception:
                self._puerto = None
                return False

    def cerrar(self) -> None:
        with self._lock:
            if self._puerto and self._puerto.is_open:
                self._puerto.close()
            self._puerto = None


arduino_serial = ArduinoSerial()
