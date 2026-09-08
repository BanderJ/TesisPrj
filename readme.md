# CoffeeRen

Sistema integral de clasificación y gestión de muestras de café verde para la **Cooperativa Agraria Line Coffee Marañón** (Lonya Grande, Utcubamba, Amazonas, Perú)).

## Descripción

CoffeeRen automatiza la evaluación de café verde mediante visión artificial:

- Registra muestras de caficultores (Socios y no-Socios)
- Procesa granos en una faja transportadora controlada por Arduino
- Captura video en tiempo real con cámara ELP AR0234 Global Shutter
- Detecta granos defectuosos con YOLO + ByteTrack (IDs únicos, sin doble conteo)
- **Separa físicamente** los granos defectuosos con un servo sincronizado a la velocidad de la faja
- Calcula grado SCA, defectos equivalentes y factor de rendimiento/pago
- Emite código de evaluación (EVA) correlativo al finalizar

## Tecnologías

| Componente | Detalles |
|---|---|
| **Backend** | FastAPI + Uvicorn (Python 3.11) |
| **Base de datos** | PostgreSQL + psycopg2 directo (sin ORM) |
| **Frontend** | Jinja2 templates + TailwindCSS + JavaScript vanilla |
| **Autenticación** | JWT en cookie httponly (Argon2 para contraseñas) |
| **ML** | YOLO26n exportado a ONNX (transfer learning COCO, augmentación Roboflow) |
| **Tracking** | ByteTrack + mapeo propio de IDs globales (nunca retroceden) |
| **Hardware** | Arduino Uno: puente H (faja), HC-SR04 (tapa), servo separador |
| **Streaming** | MJPEG con OpenCV (headless) + polling de frames JPEG |

## Requisitos previos

- **Python 3.11** (con pip)
- **PostgreSQL** corriendo localmente (usuario `postgres`, base de datos `tesis_prj`)
- **Arduino IDE** (para cargar firmware en Arduino Uno)
- **Cámara ELP AR0234** (Global Shutter) — opcional para desarrollo sin visión
- GPU NVIDIA opcional: el device se detecta automáticamente (`cuda` / `cpu`)

## Instalación

```powershell
# 1. Crear y activar entorno virtual
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables en .env (ver sección "Configuración")

# 4. Crear schema de base de datos
psql -U postgres -d tesis_prj -f src/database/script.sql

# 5. Cargar el modelo YOLO (no está en Git — descargar desde Google Drive)
# → src/ml/models/yolov26n_2cls/best.onnx  (preferido)
# → src/ml/models/yolov26n_2cls/best.pt    (respaldo)
```

Ver también [INSTALACION.md](INSTALACION.md) y [Manual_Instalacion_CoffeeRen.md](Manual_Instalacion_CoffeeRen.md) para la guía completa de despliegue.

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
| `FAJA_VELOCIDAD_PWM` | `150` | PWM de la faja — **debe coincidir** con `VELOCIDAD` en `logica_hardware.ino` |
| `SERVO_DELAY_S` | calculado | Tiempo cámara→servo; se deriva del PWM, o se fija medido en banco |
| `SERVO_HOLD_S` | `0.3` | Tiempo que el servo sostiene la posición DEFECTO |

Las credenciales de PostgreSQL están hardcodeadas en `src/config.py` (`USER`, `PASSWORD`, `HOST`, `PORT`, `DATABASE`).

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
│   └── test_motor/             # Sketch de prueba aislada del motor (banco)
├── docs/
│   ├── DOCUMENTACION_SISTEMA.md
│   ├── API_VIDEO_STREAMING.md
│   ├── defectos_sca_tabla_referencia.md
│   └── documentacion/          # Especificaciones SCA, equivalencias de defectos
├── src/
│   ├── database/
│   │   ├── bd.py               # Wrapper Connection (obtener, obtener_uno, ejecutar, commit, rollback)
│   │   └── script.sql          # Schema PostgreSQL
│   ├── ml/
│   │   ├── tracker.py          # CoffeeRenTracker: YOLO + ByteTrack + IDs globales + votación
│   │   ├── classifier.py       # Defectos equivalentes y grado SCA (3 grados)
│   │   ├── bytetrack.yaml      # Configuración del tracker
│   │   └── models/
│   │       └── yolov26n_2cls/
│   │           ├── best.onnx    # Modelo activo (2 clases) — no en Git
│   │           ├── best.pt      # Respaldo — no en Git
│   │           └── constants.py # CLASES, COLORES, EQUIVALENCIAS_DEFECTO, filtro de tamaño
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
| `/` `/inicio` | `inicio.html` | Dashboard de inicio | JWT |
| `/auth/login` | `login.html` | Inicio de sesión | — |
| `/registro` | `registro.html` | Crear nueva evaluación (caficultor + muestra) | JWT |
| `/monitoreo/{id}` | `monitoreo.html` | Video en vivo + conteo + control de faja | JWT |
| `/analisis/{id}` | `analisis.html` | Resumen estadístico de la evaluación finalizada | JWT |
| `/nuevo-caficultor` `/registro-socios` | `caficultor.html` | Alta de caficultor + conversión a Socio | JWT |
| `/reporte` | `reporte.html` | Búsqueda de evaluaciones por código EVA | JWT |
| `/valor-cafe` | `valor_cafe.html` | Gestión de precios de café | Gerente/Admin |
| `/configuracion-cooperativa` | `cooperativa.html` | Datos de la cooperativa | JWT |

Las páginas `/monitoreo/{id}` y `/analisis/{id}` tienen guards de estado: una evaluación finalizada redirige a análisis y viceversa.

## Flujo principal

```
1. REGISTRO
   /registro → POST /evaluacion → evaluacion_id (UUID), estado "activa"

2. MONITOREO EN TIEMPO REAL  (/monitoreo/{id})
   POST /video/iniciar          → carga YOLO + conecta cámara
   POST /arduino/motor/iniciar  → arranca la faja (solo tras confirmar primer frame)
   GET  /video/frame            → frame anotado JPEG (polling ~30 fps)
   GET  /video/lote/conteo      → conteo en vivo (polling cada 1.5 s)
   [servo separa defectuosos en paralelo, sincronizado con SERVO_DELAY_S]

3. FINALIZAR
   POST  /video/lote/generar-reporte → grado SCA + defectos equivalentes
   PATCH /evaluacion/{id}/finalizar  → asigna código EVA correlativo

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
tracker.py: CoffeeRenTracker
    ├─ YOLO (ONNX, imgsz=640, conf=0.50, device auto cuda/cpu)
    ├─ ByteTrack + mapeo a IDs globales (nunca retroceden tras pausas)
    ├─ Filtro de tamaño de bounding box (GRANO_MIN_PX–GRANO_MAX_PX)
    └─ Votación por mayoría por ID (≥5 detecciones, conf promedio ≥0.45)
    ↓
servo_controller.py: cola de separación
    ├─ Programa cada grano a t_captura + SERVO_DELAY_S (descuenta latencia de inferencia)
    ├─ SERVO:DEFECTO → hold SERVO_HOLD_S → SERVO:BUENO
    └─ Defectos consecutivos extienden el hold (sin parpadeo del servo)
    ↓
Fin de lote → classifier.py: generar_reporte(conteo)
    └─ defectos equivalentes SCA + grado + apto specialty
```

### Modelo activo

| Modelo | Clases | Formato | Estado |
|---|---|---|---|
| **yolov26n_2cls** | 2 (`defecto`, `verde`) | ONNX (respaldo `.pt`) | ✅ Producción |
| yolov26n (cascada) | 14 subtipos de defecto | ONNX | ⏳ Preparado, pendiente de activar |

**Nota:** Los pesos no están en Git — descargar desde Google Drive a `src/ml/models/{modelo}/`. El tracker prefiere `best.onnx` y cae a `best.pt` si no existe.

El modelo de cascada de 14 clases (`agrio`, `averanado`, `blanco`, `broca_ligero`, `broca_severo`, `cascarilla_cereza_seca`, `cascarilla_pergamino`, `cereza_seca`, `defecto_forma`, `inmaduro`, `negro`, `partido`, `pergamino`, `verde`) correrá sobre el crop de cada grano defectuoso para identificar el subtipo.

### Constantes por modelo

Cada modelo tiene su directorio con `constants.py` que define:

- **CLASES**: lista ordenada según los índices del modelo
- **COLORES**: paleta BGR `{clase: (B,G,R)}`
- **EQUIVALENCIAS_DEFECTO**: tabla SCA de 350 g específica del modelo
- **GRANO_MIN_PX / GRANO_MAX_PX**: filtro de tamaño de detecciones

El tracker las carga dinámicamente al instanciarse:

```python
tracker = CoffeeRenTracker(conf=0.50, model_name="yolov26n_2cls")
```

### Parámetros de inferencia (no cambiar sin recalibrar)

- **conf**: 0.50 (`CONF_THRESHOLD` en `tracker_service.py` — preferir falsos positivos antes que defectos sin detectar)
- **imgsz**: 640 (coincide con el entrenamiento en Roboflow)
- **half**: False (la GTX 1050 Mobile tiene soporte FP16 limitado)
- **persist**: True (mantiene estado de ByteTrack entre frames)
- Exportación ONNX: `model.export(format="onnx", imgsz=640, half=False, dynamic=False, simplify=True)`

### Grados SCA (classifier.py)

| Grado | Defectos equivalentes (350 g) |
|---|---|
| Grado 1 (Specialty) | 0 – 15 |
| Grado 2 | 16 – 23 |
| Grado 3 | 24 o más |

**⚠️ Crítico:** Las equivalencias deben coincidir con los estándares SCA de Line Coffee Marañón. Verificar contra `docs/documentacion/` y [docs/defectos_sca_tabla_referencia.md](docs/defectos_sca_tabla_referencia.md) antes de producción.

## Hardware — Arduino

### Firmware de producción (`arduino/logica_hardware/`)

| Componente | Pin(es) | Función |
|---|---|---|
| Puente H (motor faja) | 5, 6 | Faja transportadora, PWM = 150 |
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

### Sketch de prueba (`arduino/test_motor/`)

Prueba aislada del motor (mismos pines que producción) desde el Monitor Serie: adelante/reversa/parar, ajuste de PWM y una rampa automática para medir el PWM mínimo de arranque de la faja.

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
| 1 | Operario | Registrar evaluaciones, consultar reportes |
| 2 | Gerente | + Crear/editar precios de café |
| 3 | Administrador | + Crear/editar precios de café |

## Validación de datos

| Campo | Regla | Ubicación |
|---|---|---|
| DNI (Persona) | Exactamente 8 dígitos | [src/schemas/persona.py](src/schemas/persona.py) |
| Pasaporte / Carnet | 8–12 caracteres alfanuméricos | [src/schemas/persona.py](src/schemas/persona.py) |
| Peso de grano bueno | Entero en gramos, ≤ peso tamizado | backend valida en `/evaluacion/{id}/completar` |

## Entrenamiento de modelos

**Contexto CRISP-ML(Q):**

| Aspecto | Detalle |
|---|---|
| **Dataset** | 3,451 imágenes originales → 8,283 con 3× augmentación (Roboflow) |
| **Split** | 88% train / 8% validación / 4% test |
| **Augmentación** | Flip H/V, rotate ±15°, brightness ±15%, exposure ±5%, blur 0.5px, noise 0.1% |
| **Infraestructura** | Google Colab A100 GPU, transfer learning desde COCO |

**Proceso:**
1. Anotar imágenes en Roboflow y augmentar el dataset
2. Entrenar en Google Colab (`yolo detect train data=... imgsz=640 ...`)
3. Exportar a ONNX con los parámetros exactos de la sección de inferencia
4. Copiar `best.onnx` (+ `best.pt` de respaldo) a `src/ml/models/{modelo}/`
5. Crear/actualizar `constants.py` con el mapeo de clases y equivalencias

## Documentación adicional

| Documento | Contenido |
|---|---|
| [docs/DOCUMENTACION_SISTEMA.md](docs/DOCUMENTACION_SISTEMA.md) | Documentación técnica del sistema |
| [docs/API_VIDEO_STREAMING.md](docs/API_VIDEO_STREAMING.md) | API de video y streaming |
| [docs/defectos_sca_tabla_referencia.md](docs/defectos_sca_tabla_referencia.md) | Tabla de referencia de defectos SCA |
| [INSTALACION.md](INSTALACION.md) | Guía de instalación |
| [CLAUDE.md](CLAUDE.md) | Patrones, reglas y arquitectura para desarrollo |

## Testing

**No existe suite de tests automatizados.** Validar cambios manualmente:

- Servidor: `uvicorn src.main:app --reload` → `http://localhost:8000`
- Flujo completo: registro → monitoreo → finalizar → peso bueno → análisis
- ML/hardware: capturas reales con cámara ELP + faja y servo conectados
- Motor aislado: sketch `arduino/test_motor/` desde el Monitor Serie

## Contacto y colaboradores

- **Institución**: Universidad Católica Santo Toribio de Mogrovejo (USAT)
- **Socio**: Cooperativa Agraria Line Coffee Marañón
- **Ubicación**: Lonya Grande, Utcubamba, Amazonas, Perú
