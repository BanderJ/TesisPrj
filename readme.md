# CoffeeRen

Sistema integral de clasificación y gestión de muestras de café verde para la **Cooperativa Agraria Line Coffee Marañón** (Lonya Grande, Utcubamba, Amazonas, Perú). Proyecto de tesis en la Universidad Católica Santo Toribio de Mogrovejo (USAT).

## Descripción

CoffeeRen automatiza la evaluación de café verde mediante visión artificial:
- Registra muestras de caficultores (Socios y no-Socios)
- Procesa granos en banda transportadora controlada por Arduino
- Captura video en tiempo real con cámara ELP AR0234 (90fps, 1920×1080)
- Detecta 17 clases de defectos usando YOLO con ByteTrack
- Calcula grado SCA, defectos equivalentes y pago automático
- Emite código de evaluación (EVA) correlativo al finalizar

## Tecnologías

| Componente | Detalles |
|---|---|
| **Backend** | FastAPI + Uvicorn (Python 3.11.9) |
| **Base de datos** | PostgreSQL + psycopg2 directo (sin ORM) |
| **Frontend** | Jinja2 templates + TailwindCSS + JavaScript vanilla |
| **Autenticación** | JWT en cookie httponly (Argon2 para contraseñas) |
| **ML** | YOLOv8n, YOLO26n (transfer learning COCO, augmentación Roboflow) |
| **Tracking** | ByteTrack (persistencia de IDs entre frames) |
| **Hardware** | Arduino Uno: HC-SR04, MX1508, HX711, Servo |
| **Streaming** | MJPEG con OpenCV (headless, sin ventanas) |

## Requisitos previos

- **Python 3.11.9** (con pip)
- **PostgreSQL** corriendo localmente (usuario `postgres`, base de datos configurada)
- **Arduino IDE** (para cargar firmware en Arduino Uno)
- **Cámara ELP AR0234** (Global Shutter, 90fps, 1920×1080) — opcional para desarrollo sin visión

## Instalación

```powershell
# 1. Crear y activar entorno virtual
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar credenciales de base de datos
# Editar src/config.py: reemplazar DB_HOST, DB_USER, DB_PASSWORD, DB_NAME
# (SECRET_KEY se lee de $env:SECRET_KEY)

# 4. Crear schema de base de datos
psql -U postgres -d coffeetest -f src/database/script.sql

# 5. (Opcional) Cargar modelos YOLO en src/ml/models/
# Descargar yolov8n/best.pt y yolo26n/best.pt desde Google Drive
# → src/ml/models/{yolov8n,yolo26n}/best.pt
```

## Ejecución

```powershell
# Terminal 1: Servidor FastAPI (recargas automáticas)
$env:SECRET_KEY = "tu-clave-secreta-fuerte-aqui"
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Compilar TailwindCSS (modo watch)
.\tailwindcss-windows-x64.exe -i src\static\css\input.css `
  -o src\static\css\tailwind.css --watch
```

La app está disponible en `http://localhost:8000`.

## Arquitectura

El proyecto sigue un patrón de **4 capas** (Clean Architecture):

| Capa | Carpeta | Responsabilidad |
|---|---|---|
| **Routes** | `src/routes/` | Endpoints HTTP, delega a servicios, renderiza templates o JSON |
| **Services** | `src/services/` | Lógica de negocio, orquestación, transacciones (commit/rollback) |
| **Models** | `src/models/` | SQL crudo via psycopg2, sin lógica |
| **Schemas** | `src/schemas/` | Validación Pydantic (request/response), no se mezcla con SQL |

### Estructura del proyecto

```
TesisPrj/
├── docs/
│   └── documentacion/          # Especificaciones SCA, equivalencias defectos
├── arduino/
│   └── logica_hardware/        # Firmware Arduino (HC-SR04 + MX1508 + HX711 + Servo)
├── src/
│   ├── database/
│   │   ├── bd.py               # Wrapper Connection (obtener, obtener_uno, ejecutar, commit, rollback)
│   │   └── script.sql          # Schema PostgreSQL (personas, caficultores, evaluaciones, etc.)
│   ├── ml/
│   │   ├── classifier.py        # Cálculo de defectos equivalentes y grado SCA (17 clases)
│   │   ├── tracker.py           # ByteTrack + YOLO + carga dinámica de constantes por modelo
│   │   └── models/
│   │       ├── yolov8n/
│   │       │   ├── best.pt      # Modelo YOLO entrenado (17 clases, 75 epochs, mAP50: 0.767)
│   │       │   └── constants.py # CLASES, COLORES, EQUIVALENCIAS_DEFECTO
│   │       └── yolo26n/
│   │           ├── best.pt      # Modelo YOLO entrenado (14 clases, fusionadas)
│   │           └── constants.py # CLASES, COLORES, EQUIVALENCIAS_DEFECTO
│   ├── models/                 # SQL crudo: persona, caficultor, evaluacion, etc.
│   ├── routes/                 # Endpoints FastAPI (auth, evaluacion, caficultor, video, etc.)
│   ├── schemas/                # Validación Pydantic (request/response models)
│   ├── services/               # Lógica: evaluacion_service, caficultor_service, etc.
│   ├── static/                 # CSS (TailwindCSS), JS vanilla, íconos
│   ├── templates/              # Plantillas Jinja2 (inicio, registro, monitoreo, análisis, etc.)
│   ├── utilities/              # JWT (jwt_required.py), Arduino serial, helpers
│   ├── config.py               # Configuración: DB_*, SECRET_KEY (env)
│   └── main.py                 # Punto de entrada FastAPI
├── requirements.txt
└── README.md
```

## Páginas

| URL | Template | Descripción | Autenticación |
|---|---|---|---|
| `/` `/inicio` | `inicio.html` | Dashboard de inicio y estado de la cooperativa | JWT required |
| `/auth/login` | `login.html` | Inicio de sesión (DNI + contraseña) | — |
| `/registro` | `registro.html` | Crear nueva evaluación (selecciona caficultor + café) | JWT required |
| `/monitoreo/{id}` | `monitoreo.html` | Stream MJPEG en tiempo real + gráficas en vivo | JWT required |
| `/nuevo-caficultor` | `nuevo_caficultor.html` | Alta de caficultor (Socio/no-Socio) + conversión | JWT required |
| `/valor-cafe` | — | Gestión de precios de café por tipo | Gerente/Admin solo |
| `/reporte` | — | Búsqueda de evaluaciones por código EVA | JWT required |

## Flujo principal

```
1. REGISTRO
   /registro (GET) → forma con lista de caficultores
   POST /evaluacion/registrar → evaluacion_id (UUID), status = "en_progreso"

2. MONITOREO EN TIEMPO REAL
   /monitoreo/{id} (GET) → plantilla + JavaScript
   GET /video/stream (MJPEG) → frames anotados (YOLO + ByteTrack)
   WebSocket /ws/{id} (opcional) → conteo vivo de defectos

3. COMPLETAR EVALUACIÓN
   PATCH /evaluacion/{id}/completar
   → classifier.generar_reporte(conteo_granos)
   → calcula defectos, grado SCA, pago
   → status = "completada"

4. FINALIZAR (genera código EVA)
   PATCH /evaluacion/{id}/finalizar
   → asigna eva_code correlativo
   → status = "finalizada"

5. ANÁLISIS
   /analisis/{id} (GET) → plantilla con reporte completo + código EVA
```

## Módulo ML — Detección de defectos en café verde

### Arquitectura y flujo

```
Cámara ELP (90fps, 1920×1080)
    ↓
src/ml/tracker.py: CoffeeRenTracker
    ├─ YOLO (modelo seleccionable)
    ├─ ByteTrack (persistencia de IDs)
    └─ obtener_conteo() → {clase: cantidad_unica}
    ↓
src/ml/classifier.py: generar_reporte(conteo)
    └─ cálculo de defectos equivalentes SCA
    └─ determinación de grado (1–5) + specialty-eligible
    ↓
Reporte JSON (defectos + grado + pago)
    ↓
/video/stream (MJPEG) → monitoreo en tiempo real
```

### Modelos disponibles

| Modelo | Clases | mAP50 | mAP50-95 | Epochs | Estado |
|---|---|---|---|---|---|
| **yolov8n** | 17 | 0.767 | 0.757 | 75 | ✅ Producción |
| **yolo26n** | 14 | — | — | en progreso | ✅ Listo para usar |
| **yolo11n** | — | — | — | pendiente | ⏳ Próximo |

**Nota:** Modelos en `src/ml/models/{nombre}/best.pt` — **no en Git**, descargar desde Google Drive.

### Clases detectadas (17 clases yolov8n)

```
agrio_ligero      agrio_severo      averanado         blanco
broca_ligero      broca_severo      cascarilla_cereza_seca
cascarilla_pergamino  cereza_seca   concha            deforme
inmaduro          negro             partido_maquina   partido_mitad
pergamino         verde
```

### Carga dinámica de constantes por modelo

Cada modelo tiene su propio directorio con `constants.py`:

```python
# src/ml/tracker.py
tracker = CoffeeRenTracker(conf=0.20, model_name="yolo26n")
# → Carga automáticamente src/ml/models/yolo26n/constants.py
# → tracker.CLASES, tracker.COLORES, tracker.EQUIVALENCIAS_DEFECTO
```

Cada `constants.py` define:
- **CLASES**: mapeo `{índice: nombre}` exacto del modelo
- **COLORES**: paleta BGR `{clase: (B,G,R)}`
- **EQUIVALENCIAS_DEFECTO**: tabla SCA de 350g específica del modelo

### ByteTrack — Persistencia de IDs

- Cada grano recibe un ID único que persiste entre frames
- Evita conteos duplicados cuando el mismo grano se ve en múltiples frames
- `obtener_conteo()` retorna cantidad única por clase

### Parámetros de inferencia

- **CONF_THRESHOLD**: 0.20 (optimizado para production: alta recall en agrio y partido)
- **imgsz**: 1280 (resolución completa para detectar granos pequeños)
- **tracker**: bytetrack.yaml (configuración oficial ByteTrack)
- **persist**: True (reutiliza IDs en cada frame)

### Salida: Reporte SCA

```json
{
  "total_granos_analizados": 350,
  "total_defectos_equivalentes": 8.5,
  "grado": "Grado 1 (Specialty)",
  "apto_specialty": true,
  "detalle_por_clase": {
    "agrio_ligero": {
      "granos": 3,
      "defectos_equivalentes": 0.5
    },
    "agrio_severo": {
      "granos": 2,
      "defectos_equivalentes": 1.0
    },
    "negro": {
      "granos": 1,
      "defectos_equivalentes": 1.0
    }
  }
}
```

### Tabla de equivalencias defectos (SCA — 350g)

La tabla exacta se define en `constants.py` de cada modelo. Ejemplo (`yolov8n`):

| Clase | Defectos por grano | Nota |
|---|---|---|
| `agrio_ligero` | 1/3 | Semiácido |
| `agrio_severo` | 1/2 | Ácido |
| `broca_ligero` | 1/4 | Agujero < 2mm |
| `broca_severo` | 1/2 | Agujero ≥ 2mm |
| `negro` | 1 | Total |
| ... | ... | Ver `docs/documentacion/` |

**⚠️ Crítico:** Las equivalencias deben coincidir exactamente con estándares SCA de Line Coffee Marañón. Verificar en `docs/documentacion/` antes de producción.

## Base de datos

PostgreSQL + psycopg2 directo (sin ORM).

### Conexión y transacciones

- **Clase**: `Connection` en [src/database/bd.py](src/database/bd.py)
- **Métodos**: `obtener()`, `obtener_uno()`, `ejecutar()`, `commit()`, `rollback()`
- **Configuración**: `autocommit=False`, `RealDictCursor` (retorna dicts, no tuples)

### Patrón de transacciones multi-tabla

Cuando un servicio necesita escribir a múltiples tablas atomicamente:

```python
# En src/services/evaluacion_service.py
db = Connection()
try:
    # Pasar la misma conexión a cada modelo
    evaluacion = crear_evaluacion(data, db)
    actualizar_caficultor(cafe_id, db)
    db.commit()  # Ambas tablas se guardan juntas
except Exception as e:
    db.rollback()  # Si falla una, ambas se revierten
finally:
    db.close()
```

- Los modelos aceptan `db: Connection = None` para este propósito
- **Nunca** f-strings en SQL: usar parametrización `db.obtener("WHERE id=%s", [id])`

## Autenticación

- **JWT** almacenado como cookie httponly (`access_token: "Bearer <token>"`)
- **Contraseñas**: hasheadas con Argon2 (bcrypt alternative)
- **Rutas protegidas**: todas excepto `/auth/login`, que dependen de `obtener_usuario_actual()` en [src/utilities/jwt_required.py](src/utilities/jwt_required.py)
- **Token payload**: `personal_id`, `usuario`, `rol`, `nombre`, `exp` (7 días TTL)
- **Fallo**: `RequerirLoginException` → handler global → redirige a `/auth/login`

## Hardware — Arduino

El sketch en `arduino/logica_hardware/` controla:

| Componente | Pin(es) | Función |
|---|---|---|
| MX1508 (motor) | 5, 6 | Banda transportadora (velocidad variable) |
| HC-SR04 | 7 (TRIG), 8 (ECHO) | Detección ultrasónica de presencia |
| HX711 (celda de carga) | A0, A1 | Medición de peso en gramos |
| Servo | 9 | Desvío de granos defectuosos (180°) |

- **Baud rate**: 9600
- **Comando `PF`** (Peso Final): toma 20 muestras, retorna `{"tipo":"peso_final","g":X,"kg":X}`
- **Integración**: [src/utilities/](src/utilities/) maneja protocolo serial (no directo desde ML)

## Entrenamiento de modelos

**Contexto CRISP-ML(Q):**

| Aspecto | Detalle |
|---|---|
| **Dataset** | 3,451 imágenes originales → 8,283 con 3× augmentación (Roboflow) |
| **Split** | 88% train / 8% validación / 4% test |
| **Augmentación** | Flip H/V, rotate ±15°, brightness ±15%, exposure ±5%, blur 0.5px, noise 0.1% |
| **Infraestructura** | Google Colab A100 GPU, transfer learning desde COCO |

**Resultados validación:**

| Modelo | mAP50 | mAP50-95 | Epochs | Duración |
|---|---|---|---|---|
| YOLOv8n | 0.767 | 0.757 | 75 | 1.1h |
| YOLO26n | — | — | en progreso | — |
| YOLO11n | — | — | pendiente | — |

**Proceso:**
1. Anotar imágenes con defectos (roboflow.com)
2. Augmentar dataset
3. Entrenar en Google Colab (`yolo detect train data=... epochs=75 ...`)
4. Descargar `best.pt` → `src/ml/models/{modelo}/best.pt`
5. Actualizar `constants.py` con mapeo de clases

Ver `docs/documentacion/` para detalles de entrenamiento y especificaciones SCA.

## Roles de usuario

| tipo_personal_id | Rol | Permisos |
|---|---|---|
| 1 | Operario | Registrar evaluaciones, consultar reportes |
| 2 | Gerente | + Crear/editar precios de café |
| 3 | Administrador | + Crear/editar precios de café |

Control de acceso en las rutas; verificar `rol` en payload JWT.

## Validación de datos

| Campo | Regla | Ubicación |
|---|---|---|
| DNI (Persona) | Exactamente 8 dígitos | [src/schemas/persona.py](src/schemas/persona.py) |
| Pasaporte / Carnet | 8–12 caracteres alfanuméricos | [src/schemas/persona.py](src/schemas/persona.py) |
| Email | RFC 5322 (Pydantic EmailStr) | [src/schemas/persona.py](src/schemas/persona.py) |

## Variables de entorno

Solo `SECRET_KEY` se lee del entorno (firma JWT). Las credenciales DB son hardcodeadas en [src/config.py](src/config.py):

```powershell
$env:SECRET_KEY = "tu-clave-muy-secreta-y-fuerte-aqui"
```

Si cambia: servidor debe reiniciarse; tokens existentes se invalidan.

## Reglas de desarrollo backend

### Disciplina de capas (nunca cruzar límites)

```
Routes   → llama servicios, retorna templates/JSON
Services → lógica, orquesta modelos, maneja transacciones
Models   → SQL crudo solamente
Schemas  → validación Pydantic solamente
```

### No-negociables

- **Type hints** en toda función (Python 3.10+: `list[dict]`, `str | None`)
- **SQL parametrizado**: `db.obtener("SELECT … WHERE id=%s", [id])` — nunca f-strings
- **Transacciones**: `try: … finally: db.close()` al abrir Connection manualmente
- **Sin duplicados**: una función parametrizada > tres casi idénticas
- **Sin lógica en Models**: SQL puro, validación va en Schemas

### Patrones de reutilización

Antes de crear algo nuevo:
1. ¿Ya existe? → Reutilizar
2. ¿Variación pequeña? → Parametrizar
3. ¿Sin valor único? → Eliminar

## Documentación adicional

| Documento | Ubicación | Contenido |
|---|---|---|
| **Especificaciones SCA** | `docs/documentacion/` | Tabla de equivalencias defectos, grados, standards |
| **Constantes por modelo** | `src/ml/models/{modelo}/constants.py` | CLASES, COLORES, EQUIVALENCIAS_DEFECTO |
| **Schema DB** | [src/database/script.sql](src/database/script.sql) | Crear tablas: personas, caficultores, evaluaciones, etc. |
| **Configuración** | [src/config.py](src/config.py) | DB_HOST, DB_USER, DB_PASSWORD, SECRET_KEY (env) |
| **Instrucciones desarrollo** | [CLAUDE.md](CLAUDE.md) | Patrones, reglas, arquitectura |

## Testing

**No existe suite de tests automatizados.** Validar cambios:
- Servidor: `uvicorn src.main:app --reload`
- Browser: `http://localhost:8000`
- Flujo: registro → monitoreo → completar → finalizar → análisis
- ML: capturas reales con cámara ELP

## Contacto y colaboradores

- **Institución**: Universidad Católica Santo Toribio de Mogrovejo (USAT)
- **Socio**: Cooperativa Agraria Line Coffee Marañón
- **Ubicación**: Lonya Grande, Utcubamba, Amazonas, Perú
