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
    # Tiempo (s) entre detección por cámara y llegada del grano al servo.
    # Ajustar según velocidad de la faja y distancia física cámara → servo.
    SERVO_DELAY_S: float = float(os.environ.get('SERVO_DELAY_S') or '0.5')
    # Tiempo (s) que el servo permanece en posición DEFECTO antes de volver a BUENO.
    SERVO_HOLD_S: float = float(os.environ.get('SERVO_HOLD_S') or '0.3')
    # Cascada: clasificación fina de defectos con un segundo modelo YOLO.
    # Activar con USE_MODELO_DEFECTOS=true en .env cuando yolov26n esté disponible.
    USE_MODELO_DEFECTOS: bool = os.environ.get('USE_MODELO_DEFECTOS', 'false').lower() == 'true'
    MODELO_DEFECTOS_NAME: str = os.environ.get('MODELO_DEFECTOS_NAME') or 'yolov26n'
    MODELO_DEFECTOS_EVERY_N: int = int(os.environ.get('MODELO_DEFECTOS_EVERY_N') or '5')
    MODELO_DEFECTOS_CONF: float = float(os.environ.get('MODELO_DEFECTOS_CONF') or '0.35')
