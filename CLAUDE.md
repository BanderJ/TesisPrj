# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**CoffeeRen** — A computer vision system for automated classification of green coffee beans and defect detection in real time. Developed as a thesis project at Universidad Católica Santo Toribio de Mogrovejo (USAT) in collaboration with Cooperativa Agraria Line Coffee Marañón.

The project combines:
- **FastAPI backend** for managing coffee farmers ("caficultores") registration, document validation, and socio conversion workflows
- **ML vision module** using YOLO (YOLOv8n, YOLO11n, YOLO26n) for bean defect detection
- **Real-time video streaming** from ELP Global Shutter camera (AR0234, 1920x1080, 90fps)
- **Arduino integration** for physical separation actuators
- **Web UI** with server-rendered Jinja2 templates for local access

## Development Commands

```bash
# Install dependencies (activate venv first)
python -m venv .venv
source .venv/Scripts/activate   # Windows
pip install -r requirements.txt

# Run the development server
uvicorn src.main:app --reload

# Compile TailwindCSS (watch mode)
./tailwindcss-windows-x64.exe -i src/static/css/input.css -o src/static/css/tailwind.css --watch
```

App runs at `http://localhost:8000`. No test suite exists.

## Architecture

The project uses a four-layer pattern — every feature has a file in each layer:

| Layer | Path | Responsibility |
|---|---|---|
| **Routes** | `src/routes/` | HTTP endpoints, calls services, returns templates or JSON |
| **Services** | `src/services/` | Business logic, orchestrates models, owns transaction commit/rollback |
| **Models** | `src/models/` | Raw SQL via psycopg2, accepts optional `db` connection for shared transactions |
| **Schemas** | `src/schemas/` | Pydantic request/response models and input validation |

### Database

Direct psycopg2 (no ORM). The `Connection` class in [src/database/bd.py](src/database/bd.py) wraps a single connection per request with `autocommit=False` and `RealDictCursor`. Methods: `obtener()`, `obtener_uno()`, `ejecutar()`, `commit()`, `rollback()`.

Database credentials are hardcoded in [src/config.py](src/config.py) — `SECRET_KEY` reads from env, but `DB_*` values are literals.

Schema is in [src/database/script.sql](src/database/script.sql).

### Authentication

JWT stored as an httponly cookie (`access_token: "Bearer <token>"`). Passwords hashed with Argon2. All routes except `/auth/login` depend on `obtener_usuario_actual()` from [src/utilities/jwt_required.py](src/utilities/jwt_required.py), which raises `RequerirLoginException` → global exception handler → redirect to `/auth/login`. Token payload contains `personal_id`, `usuario`, `rol`, `nombre`, `exp` (7-day TTL).

### Transaction Pattern

When a service needs to write to multiple tables atomically, it creates one `Connection`, passes it to each model call, then calls `db.commit()` (or `db.rollback()` on error). Models accept `db: Connection = None` for this purpose.

## ML Module Architecture (`src/ml/`)

### `inference.py` — YOLO Model Inference
Loads trained YOLO model (`best.pt`) and performs inference on individual frames.
- **Class**: `CoffeeRenInference`
- **Key method**: `predecir(frame)` → returns YOLO result object
- **Key method**: `dibujar_detecciones(frame, result)` → returns annotated frame with bounding boxes
- **Models location**: `src/ml/models/{model_name}/best.pt` (NOT in Git — download from Google Drive)
- **Available models**:
  - `yolov8n/best.pt` — trained unseed, batch=16, mAP50: 0.767, mAP50-95: 0.757 (75 epochs)
  - `yolo26n/best.pt` — trained seed=42, batch=16 (in progress)
  - `yolo11n/best.pt` — pending training

### `tracker.py` — Real-time Video Capture & ByteTrack
Captures video from ELP camera and tracks beans using ByteTrack algorithm (unique ID persistence across frames).
- **Class**: `CoffeeRenTracker`
- **Camera**: ELP AR0234 Global Shutter, index=0, 1920×1080 @ 90fps
- **Key method**: `iniciar()` → starts capture in separate thread (non-blocking)
- **Key method**: `obtener_frame()` → returns latest annotated frame for MJPEG streaming
- **Key method**: `obtener_conteo()` → returns `{class: unique_bean_count}` dict
- **Key method**: `resetear_conteo()` → resets for new batch
- **Important**: Each bean gets a unique ID that persists to avoid double-counting

### `classifier.py` — Defect Equivalents & SCA Grade
Calculates defect equivalents and determines batch grade per SCA standards.
- **Main function**: `generar_reporte(conteo_granos)` — receives output of `tracker.obtener_conteo()`
- **Returns**: total beans, equivalent defects, grade (1–5), specialty-eligible flag, per-class breakdown
- **⚠️ Critical**: Defect equivalence table must match Line Coffee Marañón's official standards

### Bean Defect Classes (17 total)
```
agrio_ligero, agrio_severo, averanado, blanco,
broca_ligero, broca_severo, cascarilla_cereza_seca,
cascarilla_pergamino, cereza_seca, concha, deforme,
inmaduro, negro, partido_maquina, partido_mitad,
pergamino, verde
```

## System Flow
```
ELP Camera (90fps)
    ↓
tracker.py — detection + ByteTrack (unique IDs)
    ↓
MJPEG streaming → web UI
    ↓
End of batch → classifier.py
    ↓
Report: grade + defects + specialty eligible
    ↓
Arduino → physical separation actuator
```

## Training Results (Validation)
| Model   | mAP50 | mAP50-95 | Epochs | Duration |
|---------|:-----:|:--------:|:------:|:--------:|
| YOLOv8n | 0.767 | 0.757    | 75     | 1.1h     |
| YOLO26n | —     | —        | in progress | — |
| YOLO11n | —     | —        | pending    | — |

### Training Context (CRISP-ML(Q))
- **Dataset**: 3,451 original images → 8,283 with 3× augmentation (Roboflow)
- **Split**: 88% train / 8% validation / 4% test
- **Augmentations**: flip H/V, rotate ±15°, brightness ±15%, exposure ±5%, blur 0.5px, noise 0.1%
- **Infrastructure**: Google Colab A100 GPU, transfer learning from COCO

### Key Business Rules

- Document validation: DNI must be exactly 8 digits; Pasaporte/Carnet must be 8–12 alphanumeric characters.
- `Caficultor` records reference a `Persona` (the person) and a `TipoCaficultor` (Socio vs. non-Socio).
- Conversion to "socio" status: `PATCH /caficultor/convertir-socio/{num_documento}`.

## Pages

| URL | Template |
|---|---|
| `/` or `/inicio` | `inicio.html` |
| `/auth/login` | `login.html` |
| `/nuevo-caficultor` | `nuevo_caficultor.html` |
| `/monitoreo` | `monitoreo.html` |
| `/registro` | `registro.html` |

## ML Integration Rules (always apply when modifying ML modules)

- **Model loading**: Always load once at startup, cache in memory — never reload per-request
- **Threading**: Tracker runs in background thread; routes poll `obtener_frame()` and `obtener_conteo()` (non-blocking)
- **Frame pipeline**: inference.py → tracker.py → web streaming; never skip steps
- **Type hints**: All ML functions use type hints (`ndarray`, `dict[str, int]`, etc.)
- **Defect equivalents**: Must match Line Coffee Marañón's official SCA table — always verify against [docs/documentacion/](docs/documentacion/) before deploying
- **Arduino communication**: `src/utilities/` handles serial protocol — ML modules call don't send directly
- **Performance**: Frame drops are acceptable at 90fps; graceful degradation > blocking
- **No TF/PT exports**: Model weights stay as `.pt` files, not TensorFlow exports

## Estado actual del ML Module (junio 2025)

### Cambios aplicados recientemente
- `conteo_ids_confianza`: cambiado de `defaultdict(list)` a `defaultdict(lambda: deque(maxlen=30))` — evita memoria ilimitada si la faja se pausa
- Votación por mayoría implementada en `_mejor_clase_para()`: con ≥5 detecciones usa clase mayoritaria con conf promedio ≥0.45; fallback a max confianza individual
- Limpieza de IDs inactivos al final de cada frame en `procesar_frame()`
- Modelo cascada de 14 clases preparado y activable con `USE_MODELO_DEFECTOS=True` en `config.py`
- `_resolver_modelo()`: prueba `best.onnx` primero, fallback a `best.pt`
- Device automático: `torch.cuda.is_available()` → `cuda` / `cpu`, nunca hardcodeado

### Modelos ONNX exportados (no modificar parámetros de exportación)
```python
# Parámetros exactos usados — no cambiar
model.export(format="onnx", imgsz=640, half=False, dynamic=False, simplify=True)
```
- `src/ml/models/yolov26n_2cls/best.onnx` ✅ (9.4 MB)
- `src/ml/models/yolov26n/best.onnx` ✅ (9.4 MB)

### Sistema de IDs globales (problema resuelto: IDs siempre 1 o 2)
ByteTrack reinicia su contador interno cuando no hay detecciones por varios frames.
Solución implementada en `tracker.py`: mapeo propio `_bytetrack_a_global` que nunca retrocede.
```python
# Al inicializar:
self._id_global = 0
self._bytetrack_a_global: dict[int, int] = {}

# En procesar_frame():
bytetrack_id = int(box.id[0])
if bytetrack_id not in self._bytetrack_a_global:
    self._id_global += 1
    self._bytetrack_a_global[bytetrack_id] = self._id_global
track_id = self._bytetrack_a_global[bytetrack_id]
```
`resetear_conteo()` limpia `_bytetrack_a_global` e `_id_global` para nuevos lotes.

### Configuración ByteTrack (`src/ml/bytetrack.yaml`)
```yaml
tracker_type: bytetrack
track_high_thresh: 0.25
track_low_thresh: 0.1
new_track_thresh: 0.25
track_buffer: 10       # calibrado — el contador global hace el conteo resistente a pausas
match_thresh: 0.8
fuse_score: True
```
`track_buffer: 10` es intencional. El sistema es resistente a pausas largas gracias al mapeo global de IDs, no al buffer.

### Modelo cascada de 14 clases (`yolov26n`)
```python
# En config.py — activar cuando se confirme estabilidad:
USE_MODELO_DEFECTOS = False
MODELO_DEFECTOS_NAME = "yolov26n"
MODELO_DEFECTOS_EVERY_N = 5    # corre cada N frames por track_id
MODELO_DEFECTOS_CONF = 0.35
```
Clases del modelo secundario:
```python
CLASES = [
    "agrio", "averanado", "blanco", "broca_ligero", "broca_severo",
    "cascarilla_cereza_seca", "cascarilla_pergamino", "cereza_seca",
    "defecto_forma", "inmaduro", "negro", "partido", "pergamino", "verde"
]
```
Cuando activo: corre sobre crop del grano defectuoso con padding 4px. Si devuelve "verde", NO sobreescribe la clase del modelo 1. Resultado cacheado en `_cache_tipo_defecto[track_id]`.

### Hardware objetivo
- RTX 5070 Ti Mobile y GTX 1050 Mobile — mismo código en ambas
- `half=False` siempre — GTX 1050 Mobile tiene soporte FP16 limitado
- `imgsz=640` siempre — coincide con entrenamiento en Roboflow
- Frames van directo como array NumPy a YOLO — sin conversión JPG en inferencia
- JPG solo al final para streaming MJPEG al navegador

### Restricciones absolutas — nunca cambiar sin permiso explícito
- `servo_controller.py` y `arduino_serial.py`: no modificar
- `SERVO_DELAY_S=0.5s` y `SERVO_HOLD_S=0.3s`: calibrados físicamente
- `_on_camara_desconectada()`: modo emergencia, no tocar
- `imgsz=640`, `half=False`, estructura de hilos: no cambiar
- Protocolo Arduino: `SERVO:DEFECTO`, `SERVO:BUENO`, `ON`, `OFF`, `PESO:`, `LISTO:`

### Pendiente de verificar
- Confirmar en prueba real que IDs globales suben sin retroceder tras pausas entre granos
- Activar `USE_MODELO_DEFECTOS=True` cuando se confirme estabilidad del modelo de 14 clases
- Verificar FPS en GTX 1050 Mobile vs RTX 5070 Ti con modelos ONNX
- Confirmar que PyTorch detecta CUDA correctamente en ambas laptops (`torch.cuda.is_available()`)

### Nota sobre la sección "No TF/PT exports" en Backend Rules
Esta regla quedó desactualizada. Los modelos ahora se exportan a ONNX (`best.onnx`) para mejor rendimiento en CPU y GPU. Los `.pt` se mantienen como respaldo pero no se usan en producción.

## Backend Rules (always apply when writing Python/FastAPI code)

**Before creating anything new:** Does it already exist? → Reuse. Minor variation? → Parametrize. No unique value? → Delete.

**Layer discipline** (never cross boundaries):
- Routes: HTTP only, no business logic, no SQL
- Services: orchestration and business logic, no SQL
- Models: raw SQL only, no logic
- Schemas: all Pydantic validation here, nowhere else

**Non-negotiables:**
- Type hints on every function (Python 3.10+ syntax: `list[dict]`, `str | None`)
- SQL always parametrized: `db.obtener("SELECT … WHERE id=%s", [id])` — never f-strings
- Always `try … finally: db.close()` when opening a Connection manually
- No duplicate methods — one flexible parametrized method beats three near-identical ones
