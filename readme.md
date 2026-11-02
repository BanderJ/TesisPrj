# CoffeeRen

Sistema integral de clasificación y gestión de muestras de café verde para la **Cooperativa Agraria Line Coffee Marañón** (Lonya Grande, Utcubamba, Amazonas, Perú).

> **¿Primera vez en el proyecto?** Empezar por [docs/guia/](docs/guia/README.md): contexto,
> estado del modelo, reentrenamiento pendiente con la cámara ELP y lista de pendientes.

## Descripción

CoffeeRen automatiza la evaluación de café verde mediante visión artificial:

- Registra muestras de caficultores (Socios y no-Socios)
- Procesa granos en una faja transportadora controlada por Arduino
- Captura video en tiempo real con cámara ELP AR0234 Global Shutter
- Detecta granos defectuosos con YOLO + ByteTrack (IDs únicos, sin doble conteo)
- **Separa físicamente** los granos defectuosos con un servo sincronizado a la velocidad de la faja
- Emite código de evaluación (EVA) correlativo al finalizar

## Tecnologías

| Componente | Detalles |
|---|---|
| **Backend** | FastAPI + Uvicorn (Python 3.11) |
| **Base de datos** | PostgreSQL + psycopg2 directo (sin ORM) |
| **Frontend** | Jinja2 templates + TailwindCSS + JavaScript vanilla |
| **Autenticación** | JWT en cookie httponly (Argon2 para contraseñas) |
| **ML** | YOLO26n binario (`defecto`/`verde`); GPU: PyTorch CUDA 13 con `best.pt` (FP16); CPU: `best.onnx` |
| **Tracking** | ByteTrack + mapeo propio de IDs globales (nunca retroceden) |
| **Hardware** | Arduino Uno: L298N + motor JGY370 (faja), HC-SR04 (tapa), servo separador |
| **Cámara** | ELP AR0234 global shutter, USB 2.0, 1920×1080 MJPEG ~90 fps |
| **Streaming** | MJPEG con OpenCV (headless) + polling de frames JPEG |

## Requisitos previos

- **Python 3.11** (con pip)
- **PostgreSQL 18** corriendo localmente (usuario `postgres`, base de datos `tesis_prj`; el esquema usa `uuidv7()` nativo)
- **Arduino IDE** (para cargar firmware en Arduino Uno)
- **Cámara ELP AR0234** (Global Shutter) — opcional para desarrollo sin visión
- GPU NVIDIA recomendada: el device se detecta automáticamente (`cuda` / `cpu`). Requiere `torch` con CUDA (ver `requirements.txt`)

## Instalación

```powershell
# 1. Crear y activar entorno virtual
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Copiar la plantilla de configuración y poner la contraseña de PostgreSQL
copy src\config-example.py src\config.py
#    y opcionalmente variables en .env (ver sección "Configuración")

# 4. Crear schema de base de datos
psql -U postgres -d tesis_prj -f src/database/script.sql

# 5. Pesos del modelo YOLO en src/ml/models/yolov26n_2cls/
# → best.onnx  ya viene en el repositorio (se usa en CPU)
# → best.pt    descargar de Google Drive (se usa en GPU, FP16)
```

## Ejecución

```powershell
# Terminal 1: Servidor FastAPI (recargas automáticas)
uvicorn src.main:app --reload

# Terminal 2: Compilar TailwindCSS (modo watch)
.\tailwindcss-windows-x64.exe -i src\static\css\input.css `
  -o src\static\css\tailwind.css --watch
```

La app está disponible en `http://localhost:8000`. La cámara se pre-conecta al arrancar el servidor (lifespan).

## Configuración

[src/config.py](src/config.py) carga un archivo `.env` en la raíz del proyecto (sin dependencias externas). Variables soportadas:

| Variable | Default | Descripción |
|---|---|---|
| `SECRET_KEY` | — | Firma JWT (cambiarla invalida los tokens existentes) |
| `API_FACTILIZA` | `''` | Token de la API Factiliza (consulta DNI) |
| `ARDUINO_PORT` | `COM5` | Puerto serial del Arduino |
| `ARDUINO_BAUDRATE` | `9600` | Baudios (clones con resonador cerámico fallan a 115200) |
| `FAJA_VELOCIDAD_PWM` | `255` | PWM de la faja — **debe coincidir** con `VELOCIDAD` en `logica_hardware.ino` |
| `SERVO_DELAY_S` | calculado | Tiempo cámara→servo; se deriva del PWM, o se fija medido en banco (tiene prioridad). Volver a medir al cambiar la velocidad o el motor |
| `SERVO_HOLD_S` | `0.3` | Tiempo que el servo sostiene la posición DEFECTO |
| `CAM_INDICE`, `CAM_WIDTH`, `CAM_HEIGHT`, `CAM_FPS` | auto, 1920, 1080, 90 | Selección y modo de la cámara |
| `CAM_EXPOSURE`, `CAM_WB_TEMP` | automáticos | Exposición y balance de blancos manuales |
| `ML_DETECTOR_FPS`, `ML_GATE_MOVIMIENTO`, `ML_GATE_UMBRAL` | 30, true, 1.0 | Cadencia de detección y gate de movimiento |
| `ML_MEDIR_LATENCIA` | `false` | Exporta CSV de latencia a `docs/evidencias/` |

Lista completa y comentada en [src/config-example.py](src/config-example.py) y [docs/guia/02-modulo-ml.md](docs/guia/02-modulo-ml.md).
`src/config.py` no se versiona (contiene la contraseña de PostgreSQL): todo cambio se replica en `src/config-example.py`.

## Arquitectura

El proyecto sigue un patrón de **4 capas**:

| Capa | Carpeta | Responsabilidad |
|---|---|---|
| **Routes** | `src/routes/` | Endpoints HTTP, delega a servicios, renderiza templates o JSON |
| **Services** | `src/services/` | Lógica de negocio, orquestación, transacciones (commit/rollback) |
| **Models** | `src/models/` | SQL crudo vía psycopg2, sin lógica |
| **Schemas** | `src/schemas/` | Validación Pydantic (request/response), no se mezcla con SQL |

### Estructura del proyecto

```
TesisPrj/
├── arduino/
│   ├── logica_hardware/        # Firmware de producción (faja + HC-SR04 + servo)
│   └── test_motor_2/           # Sketch de prueba aislada del motor (banco)
├── docs/
│   ├── guia/                   # Guía de contexto: empezar aquí
│   ├── manuales/               # Manual de usuario en Word y archivos de apoyo
│   ├── incidencias/            # Registro formal de incidencias
│   ├── evidencias/             # Ensayos de latencia (indicadores de tesis)
│   ├── DOCUMENTACION_SISTEMA.md
│   ├── API_VIDEO_STREAMING.md
│   ├── hardware-camara.md
│   └── documentacion/          # Documentos de tesis (referencia histórica)
├── src/
│   ├── database/
│   │   ├── bd.py               # Wrapper Connection (obtener, obtener_uno, ejecutar, commit, rollback)
│   │   └── script.sql          # Schema PostgreSQL
│   ├── ml/
│   │   ├── tracker.py          # CoffeeRenTracker: tiles + YOLO + ByteTrack + IDs globales + clase por confianza
│   │   ├── classifier.py       # Defectos equivalentes del lote
│   │   ├── bytetrack.yaml      # Configuración del tracker
│   │   └── models/
│   │       ├── yolov26n_2cls/
│   │       │   ├── best.onnx    # Modelo activo para CPU (versionado)
│   │       │   ├── best.pt      # Modelo activo para GPU — no en Git
│   │       │   └── constants.py # CLASES, COLORES, EQUIVALENCIAS_DEFECTO, tiles, umbrales
│   │       └── yolov26n_2cls_new/  # Notebook de fine-tuning v7 (pendiente)
│   ├── models/                 # SQL crudo: persona, caficultor, evaluacion, etc.
│   ├── routes/                 # Endpoints FastAPI (auth, evaluacion, video, arduino, etc.)
│   ├── schemas/                # Validación Pydantic
│   ├── services/               # Lógica: evaluacion, tracker, camara, arduino, etc.
│   ├── static/                 # CSS (TailwindCSS), JS vanilla, íconos
│   ├── templates/              # Plantillas Jinja2
│   ├── utilities/              # JWT, arduino_serial (protocolo), servo_controller (cola de separación)
│   ├── config.py               # Configuración + carga de .env
│   └── main.py                 # Punto de entrada FastAPI + lifespan
├── requirements.txt
└── readme.md
```

## Páginas

| URL | Template | Descripción | Acceso |
|---|---|---|---|
| `/` (alias `/inicio`) | `inicio.html` | Dashboard de inicio | JWT |
| `/auth/login` | `login.html` | Inicio de sesión | — |
| `/registro` | `registro.html` | Crear nueva evaluación (caficultor + muestra) | JWT |
| `/monitoreo/{id}` | `monitoreo.html` | Video en vivo + conteo + control de faja | JWT |
| `/analisis/{id}` | `analisis.html` | Resumen estadístico de la evaluación finalizada | JWT |
| `/nuevo-caficultor` | `caficultor.html` | Alta de caficultor + conversión a Socio | JWT |
| `/reporte` | `reporte.html` | Búsqueda de evaluaciones por código EVA | JWT |
| `/valor-cafe` | `valor_cafe.html` | Gestión de precios de café | Gerente/Admin |
| `/configuracion-cooperativa` | `cooperativa.html` | Datos de la cooperativa | Gerente/Admin |
| `/perfil` | `perfil.html` | Perfil propio y gestión de usuarios | JWT |
| `/prueba` | `prueba.html` | Prueba de detección en vivo sin evaluación | JWT |

Las páginas `/monitoreo/{id}` y `/analisis/{id}` tienen guards de estado: una evaluación finalizada redirige a análisis y viceversa.

## Flujo principal

```
1. REGISTRO
   /registro → POST /evaluacion/registrar → evaluacion_id (UUID), estado "activa"

2. MONITOREO EN TIEMPO REAL  (/monitoreo/{id})
   POST /video/iniciar          → carga YOLO + conecta cámara
   POST /arduino/motor/iniciar  → arranca la faja (solo tras confirmar primer frame)
   GET  /video/frame            → frame anotado JPEG (polling ~30 fps)
   GET  /video/lote/conteo      → conteo en vivo (polling cada 1.5 s)
   GET  /video/eventos          → bitácora del monitoreo (avisos, objetos desconocidos)
   [servo separa defectuosos en paralelo, sincronizado con SERVO_DELAY_S]

3. FINALIZAR
   POST  /video/lote/generar-reporte → defectos equivalentes
   PATCH /evaluacion/{id}/finalizar  → asigna código EVA correlativo + guarda EVENTO_MONITOREO

4. COMPLETAR (rendimiento)
   El evaluador pesa el grano bueno separado e ingresa el valor
   PATCH /evaluacion/{id}/completar  → factor de rendimiento + pago + categoría

5. ANÁLISIS
   /analisis/{id} → reporte completo + código EVA
```

## Módulo ML — Detección y separación de defectos

### Flujo

```
Cámara ELP (hilo de captura dedicado — guarda solo el último frame + timestamp)
    ↓
tracker_service.py: techo ML_DETECTOR_FPS (30) + gate de movimiento
    ↓
tracker.py: CoffeeRenTracker
    ├─ Grilla 3×3 con solape 200 px → un solo predict() en batch (imgsz=640, conf=0.15)
    ├─ Fusión de cajas partidas entre tiles vecinos
    ├─ Filtro de tamaño de bounding box (GRANO_MIN_PX–GRANO_MAX_PX = 50–480)
    ├─ ByteTrack + mapeo a IDs globales (nunca retroceden tras pausas)
    ├─ Clase por confianza acumulada del track (MARGEN_DEFECTO = 1.3)
    └─ "Objeto desconocido" (materia extraña) si nunca supera conf 0.35 → defecto
    ↓
servo_controller.py: cola de separación
    ├─ Programa cada grano a t_captura + SERVO_DELAY_S (descuenta latencia de inferencia)
    ├─ SERVO:DEFECTO → hold SERVO_HOLD_S → SERVO:BUENO
    └─ Defectos consecutivos extienden el hold (sin parpadeo del servo)
    ↓
Fin de lote → classifier.py: generar_reporte(conteo)
    └─ defectos equivalentes SCA
```

### Modelo activo

| Modelo | Clases | Formato | Estado |
|---|---|---|---|
| **yolov26n_2cls** | 2 (`defecto`, `verde`) | `best.pt` en GPU / `best.onnx` en CPU | Producción |
| v7 fine-tuning con fotos ELP | 2 (`defecto`, `verde`) | — | Pendiente ([guía](docs/guia/03-reentrenamiento-camara-elp.md)) |

**Nota:** `best.onnx` está versionado; `best.pt` se descarga de Google Drive. Con GPU el tracker carga `best.pt` (FP16 si la compute capability es ≥ 7.0); en CPU prefiere `best.onnx`.

El modelo cascada de 14 subtipos de defecto que figuraba en versiones anteriores se retiró del código en julio de 2026.

**Problema conocido:** el modelo actual confunde granos sanos con defecto (~40 % en pruebas en vivo) porque se entrenó con fotos de celular y producción usa la cámara ELP. Ver [docs/guia/02-modulo-ml.md](docs/guia/02-modulo-ml.md#8-problema-de-calidad-abierto-domain-gap).

### Constantes por modelo

Cada modelo tiene su directorio con `constants.py` que define:

- **CLASES**: lista ordenada según los índices del modelo
- **COLORES**: paleta BGR `{clase: (B,G,R)}`
- **EQUIVALENCIAS_DEFECTO**: tabla SCA de 350 g específica del modelo (`defecto` 1, `verde` 0, `desconocido` 1.0)
- **GRANO_MIN_PX / GRANO_MAX_PX**: filtro de tamaño de detecciones
- **TILES_X / TILES_Y / TILE_SOLAPE_PX**: grilla de inferencia
- **UMBRAL_CONF_CONOCIDO / DESCONOCIDO_MIN_FRAMES**: criterio de objeto desconocido

El tracker las carga dinámicamente al instanciarse:

```python
tracker = CoffeeRenTracker(conf=0.15, model_name="yolov26n_2cls")
```

### Parámetros de inferencia (no cambiar sin recalibrar)

- **conf**: 0.15 (`CONF_THRESHOLD` en `tracker_service.py`) — piso bajo a propósito: ByteTrack usa su banda de baja confianza y la clase se resuelve por confianza acumulada
- **imgsz**: 640 (coincide con el entrenamiento en Roboflow)
- **half**: automático — FP16 solo en GPU con compute capability ≥ 7.0 y `best.pt`; FP32 en GTX 1050 Mobile y CPU
- **ByteTrack**: instanciado a mano (`BYTETracker`) porque hay que fusionar los tiles antes de trackear
- Exportación ONNX: `model.export(format="onnx", imgsz=640, half=False, dynamic=False, simplify=True)`

Tabla completa de parámetros y restricciones: [docs/guia/02-modulo-ml.md](docs/guia/02-modulo-ml.md).

### Defectos equivalentes (classifier.py)

`classifier.py` suma los defectos equivalentes del lote con las equivalencias del modelo. No
asigna grado SCA ni aptitud Specialty: el grado depende del tipo de defecto (primario/secundario)
y el modelo actual solo distingue `defecto`/`verde`.

**Crítico:** Las equivalencias deben coincidir con los estándares SCA de Line Coffee Marañón. La validación con la cooperativa está pendiente (INC-17); referencia en [docs/defectos_sca_tabla_referencia.md](docs/defectos_sca_tabla_referencia.md).

## Hardware — Arduino

### Firmware de producción (`arduino/logica_hardware/`)

| Componente | Pin(es) | Función |
|---|---|---|
| L298N canal A (motor JGY370 12 V 10 RPM) | 5 (ENA, PWM), 4 (IN1), 3 (IN2) | Faja transportadora, PWM = 255 (máxima), sentido -1 (IN2 alto). Retirar el jumper ENA del módulo |
| HC-SR04 | 7 (TRIG), 8 (ECHO) | Verificación de tapa cerrada / muestra presente |
| Servo separador | 9 | 0° = BUENO (reposo), 15° = DEFECTO |

La báscula HX711 está **retirada temporalmente** (comandos `TARE`/`SCALE` deshabilitados en el firmware); el peso de grano bueno se ingresa manualmente al completar la evaluación.

### Protocolo serial (9600 baud)

```
Backend → Arduino:  ON | OFF | SERVO:BUENO | SERVO:DEFECTO | TARE | SCALE:<factor>
Arduino → Backend:  LISTO:<cm> | NO_LISTO:<cm> | PESO:<g> | TARE:OK | SISTEMA:LISTO
```

- `OFF` detiene la faja y resetea el servo a BUENO.
- Si el Arduino se reinicia (`SISTEMA:LISTO`) con la faja activa, el backend re-envía `ON` automáticamente.
- Un keep-alive cada 20 s previene la suspensión USB de Windows.
- [src/utilities/arduino_serial.py](src/utilities/arduino_serial.py) maneja el protocolo; los módulos ML nunca escriben al puerto directamente.

### Sketch de prueba (`arduino/test_motor_2/`)

Prueba aislada del motor L298N + JGY370 (mismos pines que producción) desde el Monitor Serie: adelante/reversa/parar, ajuste de PWM y una rampa automática para medir el PWM mínimo de arranque de la faja.

## Base de datos

PostgreSQL + psycopg2 directo (sin ORM).

- **Clase**: `Connection` en [src/database/bd.py](src/database/bd.py)
- **Métodos**: `obtener()`, `obtener_uno()`, `ejecutar()`, `commit()`, `rollback()`
- **Configuración**: `autocommit=False`, `RealDictCursor` (retorna dicts)

### Patrón de transacciones multi-tabla

```python
db = Connection()
try:
    evaluacion = crear_evaluacion(data, db)   # misma conexión a cada modelo
    actualizar_caficultor(caf_id, db)
    db.commit()                               # ambas tablas se guardan juntas
except Exception:
    db.rollback()                             # si falla una, ambas se revierten
finally:
    db.close()
```

- Los modelos aceptan `db: Connection = None` para este propósito
- **Nunca** f-strings en SQL: usar parametrización `db.obtener("WHERE id=%s", [id])`

## Autenticación

- **JWT** almacenado como cookie httponly (`access_token: "Bearer <token>"`)
- **Contraseñas** hasheadas con Argon2
- **Rutas protegidas**: todas excepto `/auth/login`, vía `obtener_usuario_actual()` en [src/utilities/jwt_required.py](src/utilities/jwt_required.py)
- **Token payload**: `personal_id`, `usuario`, `rol`, `nombre`, `exp` (7 días TTL)
- **Fallo**: `RequerirLoginException` → handler global → redirige a `/auth/login`

## Roles de usuario

| tipo_personal_id | Rol | Permisos |
|---|---|---|
| 1 | Evaluador | Registrar evaluaciones, monitorear, buscar por código EVA |
| 2 | Gerente | + Precios de café, cooperativa, usuarios, auditoría y reportes estadísticos |
| 3 | Administrador | Mismos permisos que Gerente (`require_admin_o_gerente`) |

## Validación de datos

| Campo | Regla | Ubicación |
|---|---|---|
| DNI (Persona) | Exactamente 8 dígitos | [src/utilities/documento_validador.py](src/utilities/documento_validador.py) |
| Pasaporte / Carnet | 8–12 caracteres alfanuméricos | [src/utilities/documento_validador.py](src/utilities/documento_validador.py) |
| Peso bruto | ≤ `num_sacos × 70` kg y mayor que la tara `round(num_sacos × 0.25)` | [src/schemas/evaluacion.py](src/schemas/evaluacion.py) |
| Humedad | Entero 1–100 | [src/schemas/evaluacion.py](src/schemas/evaluacion.py) |
| Peso de grano bueno | Entero en gramos, ≤ peso tamizado | backend valida en `/evaluacion/{id}/completar` |

## Entrenamiento de modelos

**Contexto CRISP-ML(Q):**

| Aspecto | Detalle |
|---|---|
| **Dataset** | 3,451 imágenes originales → 8,283 con 3× augmentación (Roboflow) |
| **Split** | 88% train / 8% validación / 4% test |
| **Augmentación** | Flip H/V, rotate ±15°, brightness ±15%, exposure ±5%, blur 0.5px, noise 0.1% |
| **Infraestructura** | Google Colab A100 GPU, transfer learning desde COCO |

El dataset original se capturó con un celular. El siguiente paso es un **fine-tuning (v7)** con
fotos de la cámara ELP y augmentation de tono (HSV): procedimiento completo en
[docs/guia/03-reentrenamiento-camara-elp.md](docs/guia/03-reentrenamiento-camara-elp.md) y
notebook en `src/ml/models/yolov26n_2cls_new/`.

## Documentación adicional

| Documento | Contenido |
|---|---|
| [docs/guia/](docs/guia/README.md) | Guía de contexto: proyecto, módulo ML, reentrenamiento, pendientes, historial |
| [docs/DOCUMENTACION_SISTEMA.md](docs/DOCUMENTACION_SISTEMA.md) | Documentación funcional del sistema |
| [docs/API_VIDEO_STREAMING.md](docs/API_VIDEO_STREAMING.md) | API de video y streaming |
| [docs/hardware-camara.md](docs/hardware-camara.md) | Ficha técnica y calibración de la cámara |
| [docs/incidencias/incidencia_proyecto.md](docs/incidencias/incidencia_proyecto.md) | Registro de incidencias |
| [docs/defectos_sca_tabla_referencia.md](docs/defectos_sca_tabla_referencia.md) | Tabla de referencia de defectos SCA |
| [Manual de usuario](docs/manuales/Manual_Usuario_CoffeeRen.docx) | Único manual de entrega, mantenido directamente en Word |
| [AGENTS.md](AGENTS.md) | Reglas de desarrollo para cualquier asistente de IA (Claude, GPT, Gemini, Copilot) |

## Testing

**No existe suite de tests automatizados** (solo `tests/verificacion_incremento_1.py`). Validar cambios manualmente:

- Servidor: `uvicorn src.main:app --reload` → `http://localhost:8000`
- Flujo completo: registro → monitoreo → finalizar → peso bueno → análisis
- ML/hardware: capturas reales con cámara ELP + faja y servo conectados
- Motor aislado: sketch `arduino/test_motor_2/` desde el Monitor Serie

## Contacto y colaboradores

- **Institución**: Universidad Católica Santo Toribio de Mogrovejo (USAT)
- **Socio**: Cooperativa Agraria Line Coffee Marañón
- **Ubicación**: Lonya Grande, Utcubamba, Amazonas, Perú
