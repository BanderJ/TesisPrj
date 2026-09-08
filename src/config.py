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

    # ── Cámara (ELP AR0234 global shutter, USB 2.0) ──────────────────────
    # USB 2.0: 90fps a 1080p SOLO funciona en MJPEG. Sin MJPEG el driver cae a
    # YUY2 (~5fps) y los granos saltan de posición entre frames capturados.
    # Modos soportados por la ELP: 1920x1080, 1280x720, 800x600, 640x480 — todos
    # a 90fps MJPEG. Bajar la resolución NO mejora el detalle que ve YOLO
    # (se reescala a 640 igual); solo alivia el bus USB y la CPU del encode.
    CAM_WIDTH: int = int(os.environ.get('CAM_WIDTH') or '1920')
    CAM_HEIGHT: int = int(os.environ.get('CAM_HEIGHT') or '1080')
    CAM_FPS: int = int(os.environ.get('CAM_FPS') or '90')

    # Selección de la cámara ELP frente a la webcam interna de la laptop:
    #   vacío  → autodetección por nombre de dispositivo (busca "global shutter" /
    #            "ar0234" / "elp" y descarta la webcam interna y cámaras virtuales).
    #   número → índice fijo de OpenCV (ej. CAM_INDICE=1).
    #   texto  → coincidencia por nombre de dispositivo (ej. CAM_INDICE=Global Shutter).
    # La webcam interna también negocia MJPEG, así que la selección por nombre es
    # la única forma fiable de no encender la cámara equivocada.
    CAM_INDICE: str = os.environ.get('CAM_INDICE') or ''

    # Exposición: '' = automática (AEC de fábrica, sin cambios). Un número activa
    # exposición manual: en el backend DSHOW de Windows el valor es log2(segundos)
    # — -6 ≈ 1/64s, -7 ≈ 1/128s, -8 ≈ 1/256s. Exposición corta congela el grano
    # en movimiento (el global shutter NO borra el motion blur), pero exige
    # iluminación difusa y sin parpadeo suficiente para esa velocidad.
    CAM_EXPOSURE: str = os.environ.get('CAM_EXPOSURE') or ''
    # Valor de CAP_PROP_AUTO_EXPOSURE que pone el driver en modo manual.
    # DSHOW usa 0.25; algunos drivers UVC esperan 1 o 3. Solo se aplica si
    # CAM_EXPOSURE tiene valor.
    CAM_AUTO_EXPOSURE_MANUAL: float = float(os.environ.get('CAM_AUTO_EXPOSURE_MANUAL') or '0.25')
