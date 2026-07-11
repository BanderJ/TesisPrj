#Conexion DATABASE_URI = 'postgresql://user:password@localhost:5432/mydatabase'
import os


def _cargar_env_file() -> None:
    """Carga variables del .env sin dependencias externas."""
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if not os.path.isfile(env_path):
        return
    with open(env_path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, _, value = line.partition('=')
            value = value.strip().strip("'\"")
            os.environ.setdefault(key.strip(), value)


_cargar_env_file()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key_here'
    USER = 'postgres'
    PASSWORD = 'And1150'
    HOST = 'localhost'
    PORT = '5432'
    DATABASE = 'tesis_prj'
    FACTILIZA_TOKEN: str = os.environ.get('API_FACTILIZA') or ''
    COOPERATIVA_DEFAULT_CODIGO: str = "LCM001"
    ARDUINO_PORT: str = os.environ.get('ARDUINO_PORT') or 'COM5'
    ARDUINO_BAUDRATE: int = int(os.environ.get('ARDUINO_BAUDRATE') or '9600')

    # Velocidad PWM de la faja — DEBE coincidir con VELOCIDAD en
    # arduino/logica_hardware/logica_hardware.ino. El tiempo de viaje del grano
    # de la cámara al servo depende de ella, por eso se declara también aquí.
    FAJA_VELOCIDAD_PWM: int = int(os.environ.get('FAJA_VELOCIDAD_PWM') or '150')

    # Calibración de referencia: a PWM=220 el grano tarda 0.5 s en llegar al servo.
    # El tiempo de viaje es inversamente proporcional a la velocidad de la faja,
    # así que SERVO_DELAY_S se recalcula solo al cambiar FAJA_VELOCIDAD_PWM y el
    # servo no vuelve a separar el grano equivocado por un delay desactualizado.
    # (Modelo de 1er orden — verificar en banco y, si hace falta, fijar el valor
    #  medido con SERVO_DELAY_S=<segundos> en .env, que tiene prioridad.)
    _FAJA_PWM_REF: float = 220.0
    _SERVO_DELAY_REF_S: float = 0.5
    _env_servo_delay = os.environ.get('SERVO_DELAY_S')
    SERVO_DELAY_S: float = (
        float(_env_servo_delay) if _env_servo_delay
        else round(_SERVO_DELAY_REF_S * _FAJA_PWM_REF / FAJA_VELOCIDAD_PWM, 3)
    )
    # Tiempo (s) que el servo permanece en posición DEFECTO antes de volver a BUENO.
    SERVO_HOLD_S: float = float(os.environ.get('SERVO_HOLD_S') or '0.3')
