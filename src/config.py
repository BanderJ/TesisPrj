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
    FAJA_VELOCIDAD_PWM: int = int(os.environ.get('FAJA_VELOCIDAD_PWM') or '255')

    # Calibración de referencia: a PWM=220 el grano tarda 0.5 s en llegar al servo.
    # Medida con el motor anterior. Con el JGY370 10 RPM (oct 2026) el valor se fija
    # en .env: SERVO_DELAY_S=0.3.
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

    # Balance de blancos: '' = automático (AWB de fábrica, sin cambios). Un
    # número fija la temperatura de color en Kelvin (según el driver, suele
    # aceptar ~2800-6500) y desactiva el AWB. El AWB automático deriva el
    # color cuadro a cuadro según lo que entra al encuadre; el dataset de
    # entrenamiento (fotos fijas) no tiene ese drift, así que un grano verde
    # puede cruzar al lado "defecto" del modelo solo por el tono que le
    # asignó el AWB en ese instante, no por el grano mismo. Fijar un valor
    # constante elimina esa variable en producción.
    CAM_WB_TEMP: str = os.environ.get('CAM_WB_TEMP') or ''

    # ── Rendimiento del módulo ML ───────────────────────────────────────
    # La cámara entrega ~90 fps, pero no hace falta correr YOLO en cada frame.
    # Este es un TECHO de fps para la detección: los frames intermedios se
    # descartan. Bajarlo alivia la GPU, pero si se baja demasiado el grano se
    # desplaza mucho entre frames y ByteTrack puede perderle el rastro (lo
    # recupera como ID nuevo → sobreconteo). 30 deja margen a la GPU sin
    # arriesgar el tracking. 0 = sin techo. El ahorro real entre lotes lo da
    # ML_GATE_MOVIMIENTO, no este techo.
    ML_DETECTOR_FPS: float = float(os.environ.get('ML_DETECTOR_FPS') or '30')

    # Gate por movimiento: si el frame es casi idéntico al anterior (faja
    # detenida, sin granos nuevos) se omite la inferencia por completo. Ahorra
    # 100% de GPU entre lotes. Umbral = diferencia media de intensidad (0-255)
    # sobre una miniatura 160x90 en gris; por debajo se considera "sin cambios".
    # CALIBRAR en banco: con la faja parada tracker.py loguea la diferencia media
    # cada ~2 s ("gate: diff media=..."). El umbral va entre ese valor (ruido del
    # sensor, típico 0.1-0.5) y el de la faja en marcha (>> 1). Si se pusiera muy
    # alto se saltarían granos reales → subconteo. Si el alimentador NO es faja
    # (granos sueltos uno a uno) conviene ML_GATE_MOVIMIENTO=false.
    ML_GATE_MOVIMIENTO: bool = (os.environ.get('ML_GATE_MOVIMIENTO') or 'true').lower() == 'true'
    ML_GATE_UMBRAL: float = float(os.environ.get('ML_GATE_UMBRAL') or '1.0')

    # Tope de hilos de CPU para OpenCV y las operaciones de glue de PyTorch.
    # La inferencia va en la GPU; sin este tope OpenCV reparte el imencode y los
    # resize entre los 24 núcleos y satura la CPU igual. 0 = sin tope.
    ML_MAX_THREADS_CPU: int = int(os.environ.get('ML_MAX_THREADS_CPU') or '4')

    # Resolución del frame anotado que se envía al navegador (MJPEG). La
    # detección corre a resolución completa; solo se reduce lo que se transmite.
    # 0 = enviar a resolución nativa de la cámara.
    ML_STREAM_ANCHO: int = int(os.environ.get('ML_STREAM_ANCHO') or '1280')
    ML_STREAM_JPEG_QUALITY: int = int(os.environ.get('ML_STREAM_JPEG_QUALITY') or '80')

    # Diagnostico de la cadena deteccion -> servo. Con true, tracker.py imprime
    # una linea por cada grano que pide separacion, por cada uno que muere sin
    # pedirla (evidencia insuficiente) y por cada caja descartada por tamaño.
    # Sirve para saber por que un grano defectuoso no movio el servo. Ruidoso:
    # dejar en false fuera de calibracion.
    ML_DEBUG_SERVO: bool = (os.environ.get('ML_DEBUG_SERVO') or 'false').lower() == 'true'

    # ── Evidencia de materia extraña ───────────────────
    # Cada objeto que el modelo nunca reconoció como grano (piedra, palito,
    # pajilla) se recorta del frame y se archiva bajo la carpeta de su
    # evaluación, para que el operario pueda verificar después qué se desvió.
    # Pasado el tope por lote se sigue avisando en el monitoreo, pero sin foto.
    ML_EVIDENCIA_DESCONOCIDOS: bool = (os.environ.get('ML_EVIDENCIA_DESCONOCIDOS') or 'true').lower() == 'true'
    ML_EVIDENCIA_MAX_POR_LOTE: int = int(os.environ.get('ML_EVIDENCIA_MAX_POR_LOTE') or '30')
    ML_EVIDENCIA_DIR: str = os.environ.get('ML_EVIDENCIA_DIR') or 'src/resources/desconocidos'

    # ── Medición de latencia del pipeline ───────────────────
    # Evidencia del indicador de tesis (Obj. específico 4, Resultado 01):
    # latencia captura->registro <= 200 ms en >= 50 iteraciones consecutivas.
    # Con true, tracker.py cronometra cada frame y cada ML_LATENCIA_ITERACIONES
    # imprime el resumen y exporta un CSV a ML_LATENCIA_DIR.
    ML_MEDIR_LATENCIA: bool = (os.environ.get('ML_MEDIR_LATENCIA') or 'false').lower() == 'true'
    ML_LATENCIA_OBJETIVO_MS: float = float(os.environ.get('ML_LATENCIA_OBJETIVO_MS') or '200')
    ML_LATENCIA_ITERACIONES: int = int(os.environ.get('ML_LATENCIA_ITERACIONES') or '50')
    ML_LATENCIA_DIR: str = os.environ.get('ML_LATENCIA_DIR') or 'docs/evidencias'
