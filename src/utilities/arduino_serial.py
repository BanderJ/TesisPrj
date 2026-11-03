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

Latido: mientras la faja está encendida el backend escribe una línea vacía
cada LATIDO_FAJA_S. El firmware apaga la faja si deja de recibir bytes del
host (backend caído o USB desconectado). La línea vacía no es un comando
nuevo: el Arduino ya la ignoraba como keep-alive.
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

# Intervalo del latido con la faja encendida. El firmware apaga la faja tras
# MS_SIN_HOST_MAX (3 s) sin recibir nada: tres latidos perdidos seguidos.
LATIDO_FAJA_S = 1.0
# Con la faja apagada basta el keep-alive que evita la suspensión USB de Windows.
KEEP_ALIVE_S = 20.0
# Al abrir el puerto, un Uno/Nano se reinicia por DTR y su bootloader descarta lo
# que llega durante ~1.5-2 s. Se espera la primera línea del firmware (lo
# reporta cada 100 ms) antes de aceptar comandos.
ESPERA_ARRANQUE_S = 3.0
# El firmware informa la distancia cada 100 ms. Una lectura más vieja que esto
# indica que el Arduino dejó de reportar aunque el puerto siga abierto.
ESTADO_VIGENTE_S = 1.0


@dataclass
class EstadoArduino:
    listo: bool = False
    distancia: float | None = None
    conectado: bool = False
    error: str | None = None
    # time.monotonic() de la última lectura de distancia; None si no hubo.
    recibido_en: float | None = None


class ArduinoSerial:
    def __init__(self) -> None:
        self._puerto: object | None = None
        self._write_lock = threading.Lock()   # solo para escritura al puerto
        self._state_lock = threading.Lock()   # para lectura/escritura del estado cacheado
        self._estado = EstadoArduino()
        self._peso: float | None = None
        self._reader_thread: threading.Thread | None = None
        self._activo = False
        self._ultimo_intento_reconexion: float = 0.0  # throttle: no reintentar antes de 5 s
        self._motor_activo: bool = False  # último estado comandado del motor
        self._conexion_lock = threading.Lock()  # una sola reconexión a la vez
        self._firmware_listo = threading.Event()  # primera línea recibida tras abrir
        self._keep_alive_thread: threading.Thread | None = None
        self._cerrado = False

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
            self._firmware_listo.clear()
            with self._state_lock:
                self._estado = EstadoArduino(conectado=True)
            self._reader_thread = threading.Thread(
                target=self._reader_loop,
                daemon=True,
                name="arduino-reader",
            )
            self._reader_thread.start()
            # Un único hilo de keep-alive para toda la vida del proceso: antes se
            # creaba uno por reconexión y los anteriores podían seguir vivos.
            if self._keep_alive_thread is None or not self._keep_alive_thread.is_alive():
                self._keep_alive_thread = threading.Thread(
                    target=self._keep_alive_loop,
                    daemon=True,
                    name="arduino-keepalive",
                )
                self._keep_alive_thread.start()
            if not self._firmware_listo.wait(ESPERA_ARRANQUE_S):
                print(f"[ArduinoSerial] Sin respuesta del firmware en {ESPERA_ARRANQUE_S} s tras abrir el puerto")
            return True
        except Exception as exc:
            self._puerto = None
            self._activo = False
            with self._state_lock:
                self._estado = EstadoArduino(error=str(exc))
            return False

    def _asegurar_conexion(self) -> bool:
        """Reconecta si el hilo lector está muerto. Retorna True si conectado.
        Throttlea reintentos a uno cada 5 s para no bloquear requests HTTP.
        El lock evita que dos hilos abran el puerto a la vez."""
        if self._activo and self._puerto and self._puerto.is_open:
            return True
        with self._conexion_lock:
            if self._activo and self._puerto and self._puerto.is_open:
                return True  # otro hilo ya reconectó mientras se esperaba el lock
            # Throttle: no reintentar si el último intento fue hace menos de 5 s
            ahora = time.time()
            if ahora - self._ultimo_intento_reconexion < 5.0:
                return False
            self._ultimo_intento_reconexion = ahora
            print(f"[ArduinoSerial] Reconectando (motor_activo={self._motor_activo})...")
            if self._puerto:
                try:
                    self._puerto.close()
                except Exception:
                    pass
                self._puerto = None
            self._activo = False
            return self._conectar()

    # ── Keep-alive USB ───────────────────────────────────────────────────────

    def _keep_alive_loop(self) -> None:
        """Escribe una línea vacía al Arduino: cada LATIDO_FAJA_S con la faja
        encendida (latido del watchdog del firmware) y cada KEEP_ALIVE_S con la
        faja apagada (Windows suspende el puerto USB serie si el host no escribe
        en ~5-30 s). El Arduino ignora las líneas vacías como comando."""
        ultimo_envio = 0.0
        while not self._cerrado:
            time.sleep(LATIDO_FAJA_S)
            intervalo = LATIDO_FAJA_S if self._motor_activo else KEEP_ALIVE_S
            if time.monotonic() - ultimo_envio < intervalo:
                continue
            try:
                with self._write_lock:
                    if self._puerto and self._puerto.is_open:
                        self._puerto.write(b"\n")  # línea vacía — Arduino la ignora
                        ultimo_envio = time.monotonic()
            except Exception:
                pass

    # ── Hilo lector ───────────────────────────────────────────────────────────

    def _reader_loop(self) -> None:
        """Lee líneas del Arduino de forma continua y actualiza el estado cacheado."""
        while self._activo and self._puerto and self._puerto.is_open:
            try:
                linea = self._puerto.readline().decode("utf-8", errors="ignore").strip()
                if linea:
                    self._procesar_linea(linea)
            except Exception as exc:
                print(f"[ArduinoSerial] Error en hilo lector: {exc}")
                with self._state_lock:
                    self._estado = EstadoArduino(conectado=False, error=str(exc))
                self._activo = False
                break
        print("[ArduinoSerial] Hilo lector terminado")

    def _procesar_linea(self, linea: str) -> None:
        if linea.startswith("LISTO:") or linea.startswith("NO_LISTO:"):
            try:
                prefijo, dist_str = linea.split(":", 1)
                distancia = float(dist_str)
                listo = prefijo == "LISTO"
                with self._state_lock:
                    self._estado = EstadoArduino(
                        listo=listo, distancia=distancia, conectado=True,
                        recibido_en=time.monotonic(),
                    )
                self._firmware_listo.set()
            except (ValueError, AttributeError):
                pass

        elif linea.startswith("PESO:"):
            try:
                with self._state_lock:
                    self._peso = float(linea[5:])
            except ValueError:
                pass

        elif linea == "SISTEMA:LISTO":
            self._firmware_listo.set()
            # Arduino acaba de arrancar (reset inesperado). Si la faja debía estar
            # encendida, re-enviar ON para que el motor retome sin intervención manual.
            if self._motor_activo and self._puerto and self._puerto.is_open:
                try:
                    with self._write_lock:
                        self._puerto.write(b"ON\n")
                    print("[ArduinoSerial] Arduino reiniciado — faja re-activada automáticamente")
                except Exception:
                    pass
        # TARE:OK, SCALE:OK → sin efecto en el estado cacheado

    # ── API pública ───────────────────────────────────────────────────────────

    def obtener_estado(self) -> EstadoArduino:
        """Retorna el último estado de distancia/tapa recibido del Arduino. Si la
        última lectura tiene más de ESTADO_VIGENTE_S, la tapa no se da por
        cerrada: el Arduino dejó de reportar y ese LISTO ya no es confiable."""
        self._asegurar_conexion()
        with self._state_lock:
            estado = self._estado
        if estado.listo and (
            estado.recibido_en is None
            or time.monotonic() - estado.recibido_en > ESTADO_VIGENTE_S
        ):
            return EstadoArduino(
                listo=False, distancia=None, conectado=estado.conectado,
                error="Sin lecturas recientes del sensor.",
            )
        return estado

    def obtener_peso(self) -> float | None:
        """Retorna el último peso (gramos) leído de la celda de carga, o None."""
        self._asegurar_conexion()
        with self._state_lock:
            return self._peso

    def enviar_comando(self, cmd: str) -> bool:
        """Envía un comando al Arduino. Retorna True si se envió correctamente."""
        if cmd in ("ON", "OFF"):
            print(f"[ArduinoSerial] Motor comando: {cmd}")
        if cmd == "ON":
            self._motor_activo = True
        elif cmd == "OFF":
            self._motor_activo = False

        self._asegurar_conexion()
        with self._write_lock:
            if self._puerto is None or not self._puerto.is_open:
                print(f"[ArduinoSerial] Puerto no disponible — comando ignorado: {cmd}")
                return False
            try:
                self._puerto.write(f"{cmd}\n".encode("utf-8"))
                return True
            except Exception as exc:
                print(f"[ArduinoSerial] Error escribiendo '{cmd}': {exc}")
                self._activo = False
                return False

    def cerrar(self) -> None:
        self._cerrado = True
        self._activo = False
        with self._write_lock:
            if self._puerto and self._puerto.is_open:
                self._puerto.close()
            self._puerto = None


arduino_serial = ArduinoSerial()
