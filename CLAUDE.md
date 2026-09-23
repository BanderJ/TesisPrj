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

Configuration lives in [src/config.py](src/config.py) — `SECRET_KEY` reads from env, `DB_*` and other values are literals with env-var fallbacks.

**`src/config.py` is gitignored** (holds the real DB password and personal settings). The tracked, published file is [src/config-example.py](src/config-example.py) — a redacted template. **Rule: any change to `src/config.py` (new setting, renamed field, changed comment) MUST be mirrored to `src/config-example.py` in the same edit**, with secrets replaced by placeholders. The two files must stay structurally identical (same `Config` attributes). A fresh clone runs `cp src/config-example.py src/config.py`.

Schema is in [src/database/script.sql](src/database/script.sql).

### Authentication

JWT stored as an httponly cookie (`access_token: "Bearer <token>"`). Passwords hashed with Argon2. All routes except `/auth/login` depend on `obtener_usuario_actual()` from [src/utilities/jwt_required.py](src/utilities/jwt_required.py), which raises `RequerirLoginException` → global exception handler → redirect to `/auth/login`. Token payload contains `personal_id`, `usuario`, `rol`, `nombre`, `exp` (7-day TTL).

### Transaction Pattern

When a service needs to write to multiple tables atomically, it creates one `Connection`, passes it to each model call, then calls `db.commit()` (or `db.rollback()` on error). Models accept `db: Connection = None` for this purpose.

## ML Module Architecture (`src/ml/`)

### Models
Trained YOLO weights are loaded once inside `tracker.py` (there is no separate inference module — detection happens in the tracking loop).
- **Models location**: `src/ml/models/{model_name}/` con `best.pt` y `best.onnx` — NOT in Git, download from Google Drive. En GPU se carga `best.pt`; en CPU `best.onnx` (`_resolver_modelo(prefer_pt=cuda_ok)`)
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
- **Frame pipeline**: tracker.py (detection + ByteTrack) → web streaming; never skip steps
- **Type hints**: All ML functions use type hints (`ndarray`, `dict[str, int]`, etc.)
- **Defect equivalents**: Must match Line Coffee Marañón's official SCA table — always verify against [docs/documentacion/](docs/documentacion/) before deploying
- **Arduino communication**: `src/utilities/` handles serial protocol — ML modules call don't send directly
- **Performance**: Frame drops are acceptable at 90fps; graceful degradation > blocking. La detección corre con techo `ML_DETECTOR_FPS` + gate de movimiento, no en cada frame de cámara
- **Inference backend**: GPU → `best.pt` (PyTorch nativo); CPU → `best.onnx`. Sin TensorFlow. `half` condicional por compute capability

## Estado actual del ML Module (septiembre 2026)

### Migración a GPU + optimización de recursos (sept 2026)
Antes: `torch` y `onnxruntime` estaban instalados en build **solo-CPU**, así que
toda la inferencia corría en CPU y saturaba los 24 núcleos (~96%). La laptop RTX
5070 Ti estaba sin usar.

- **GPU real**: se reinstaló `torch==2.12.0+cu130` / `torchvision==0.27.0+cu130`
  desde `https://download.pytorch.org/whl/cu130` (ver `requirements.txt`). En GPU
  `_resolver_modelo(prefer_pt=cuda_ok)` carga **`best.pt`** directo con PyTorch
  nativo — sin `onnxruntime-gpu`/cuDNN. En CPU sigue prefiriendo `best.onnx`.
- **`self._half`**: FP16 automático cuando `torch.cuda.get_device_capability()[0] >= 7`
  (RTX 5070 Ti = 12.0 → FP16). GTX 1050 Mobile (6.1) y CPU → FP32. `half` ya **no**
  es `False` fijo; se decide por hardware. Se pasa a `predict()` y al warmup.
- **Tiles en un solo batch**: `_detectar()` arma la lista de los 9 crops y hace
  **una** llamada `self.model.predict(subs, ...)`. En GPU es una pasada; ya no son
  9 `predict()` sueltos. Medido en RTX 5070 Ti: 3×3 ≈ 40 ms, 2×2 ≈ 20 ms.
- **Grilla 3×3 / solape 200 px** (`constants.py`, antes 2×2/260): grano más grande
  en la inferencia → separa mejor los granos que se tocan. Con GPU es barato.
- **`_fusionar_cajas` consciente de costura**: cada caja lleva su `idx_tile` (7ª
  col). Solo funde cajas de **tiles distintos** — dos cajas del mismo tile ya las
  separó el NMS de YOLO, son granos distintos y no se tocan nunca. Además rechaza
  la fusión si la caja envolvente supera 1.6× a la mayor de las dos (evita pegar
  dos granos vecinos de la costura en una caja gigante). Arregla el subconteo de
  granos juntos.
- **Clase para dibujar = clase resuelta del track** (no la del frame): el color de
  la caja sale de `_resolver_clase_display(historial)`, no de la detección de ese
  frame — elimina el parpadeo rojo↔verde en el video.
- **Objeto desconocido = materia extraña** (`CLASE_DESCONOCIDO`, azul): un track
  que tras `DESCONOCIDO_MIN_FRAMES` (3) nunca superó `UMBRAL_CONF_CONOCIDO` (0.35)
  se marca "objeto desconocido" en azul. INCAL advierte piedras/pajilla/palitos en
  el lote → `EQUIVALENCIAS_DEFECTO["desconocido"] = 1.0` (materia extraña = defecto
  primario SCA): el **servo lo desvía al canal DEFECTO** (`_mejor_clase_para` →
  `_resolver_clase_display`; `servo_controller._es_defecto` ve equivalencia > 0) y
  **suma al grado** como un defecto. Se reporta además por separado
  (`total_desconocidos`) para que el operario distinga objetos extraños de granos
  defectuosos. Riesgo: un grano real de confianza baja mal rotulado infla el
  defecto — calibrar `UMBRAL_CONF_CONOCIDO`, vigilar `total_desconocidos`.
- **Cadencia + gate de movimiento** (`tracker_service._loop_procesamiento`):
  `ML_DETECTOR_FPS` (techo, def. 30) descarta frames intermedios; `tracker.hay_movimiento()`
  (la primitiva de imagen vive en `tracker.py`, el service solo la invoca) omite la
  inferencia si la miniatura 160×90 en gris casi no cambió (`ML_GATE_UMBRAL`, def.
  **1.0** — CALIBRAR: `tracker.py` loguea "gate: diff media=..." cada 2 s). Faja
  quieta = 0% GPU. Riesgo si el umbral queda alto o el alimentador no es faja:
  se saltan granos → subconteo; ahí `ML_GATE_MOVIMIENTO=false`.
- **`ML_MAX_THREADS_CPU`** (def. 4): `cv2.setNumThreads` + `torch.set_num_threads`.
  La inferencia va en GPU; sin el tope OpenCV reparte el `imencode`/`resize` entre
  los 24 núcleos. Medido: no afecta el FPS de inferencia (±5%).
- **`camara_service` ya no comprime cada frame**: el `cv2.imencode` de calidad 95 a
  90 fps sobre 1080p que nadie miraba se eliminó. `esperar_frame()` devuelve `bool`.
  El único JPEG se arma en `tracker.py` sobre el frame anotado, reducido a
  `ML_STREAM_ANCHO` (def. 1280) con calidad `ML_STREAM_JPEG_QUALITY` (def. 80).
- Resultado medido (frames sintéticos, RTX 5070 Ti): CPU total del sistema
  **~25%** (antes ~96%), ~20 fps de pipeline con 3×3.

### Cambios aplicados recientemente
- `conteo_ids_confianza`: cambiado de `defaultdict(list)` a `defaultdict(lambda: deque(maxlen=30))` — evita memoria ilimitada si la faja se pausa
- **Detección por tiles** (`_detectar()` + `_grilla_tiles()` + `_fusionar_cajas()`): el modelo se entrenó con 1 grano por imagen a ~640px; sobre un frame de cámara 1920×1080 con varios granos, cada grano queda demasiado chico al reescalar a 640 y no se detecta (o se detecta partido en la costura entre tiles). Se parte el frame en una grilla (`TILES_X`/`TILES_Y`/`TILE_SOLAPE_PX` en `constants.py`, def. **3×3/200px**), los tiles se infieren en **un batch** a `imgsz=640`, `_fusionar_cajas()` une los recortes del mismo grano **solo entre tiles vecinos** (IoU≥`NMS_ENTRE_TILES` o IoS≥0.6, y envolvente ≤1.6× → caja envolvente) y se alimenta un `BYTETracker` gestionado a mano (`self._bytetracker`) — `model.track()` no permite fusionar detecciones antes de trackear. `TILE_SOLAPE_PX` debe ser ≥ (lado máx. de un grano)/2 para que ningún grano se parta. `TILES_X = TILES_Y = 1` vuelve al frame completo. En CPU conviene bajar a 2×2 o 1×1.
- **Resolución de clase por confianza acumulada** (`_resolver_clase()` + `_clases_sanas()`, reemplaza la votación por mayoría anterior): suma la confianza por clase sobre el track; una detección suelta de alta confianza ya no voltea el veredicto (arregla el parpadeo sano→defecto). La clase "sana" se deriva de `EQUIVALENCIAS_DEFECTO` (equivalencia 0.0), no se hardcodea. `_resolver_clase_display()` la envuelve y añade el rótulo "desconocido". `MARGEN_DEFECTO` (def. 1.3): la confianza acumulada de defecto debe superar a la de la clase sana por ese factor para marcar defecto — parche parcial del sesgo del modelo a "defecto" (~40% de granos buenos mal clasificados en pruebas); el arreglo de fondo es reentrenar con clases balanceadas.
- `resetear_conteo()` marca `_reset_bytetrack`; el hilo de procesamiento resetea el `BYTETracker` en el frame siguiente (no se toca desde otro hilo).
- Limpieza de IDs inactivos al final de cada frame en `procesar_frame()`
- Modelo cascada de 14 clases preparado y activable con `USE_MODELO_DEFECTOS=True` en `config.py`
- `_resolver_modelo(prefer_pt)`: en GPU prueba `best.pt` primero; en CPU `best.onnx` primero
- Device automático: `torch.cuda.is_available()` → `0` (cuda) / `cpu`, nunca hardcodeado; avisa por consola si cae a CPU

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
- `half`: **condicional por hardware** (`self._half`) — FP16 en GPUs con compute
  capability ≥ 7.0, FP32 en GTX 1050 Mobile (6.1) y CPU. NO hardcodear a `False`.
- `imgsz=640` siempre — coincide con entrenamiento en Roboflow
- Frames van directo como array NumPy a YOLO — sin conversión JPG en inferencia
- JPG solo al final para streaming MJPEG al navegador (reducido a `ML_STREAM_ANCHO`)

### Restricciones absolutas — nunca cambiar sin permiso explícito
- `servo_controller.py` y `arduino_serial.py`: no modificar
- `SERVO_DELAY_S=0.5s` y `SERVO_HOLD_S=0.3s`: calibrados físicamente
- `_on_camara_desconectada()`: modo emergencia, no tocar
- `imgsz=640`, estructura de hilos (productor cámara / consumidor tracker): no cambiar
- `half`: solo condicional por compute capability — nunca forzar FP16 en la GTX 1050
- Protocolo Arduino: `SERVO:DEFECTO`, `SERVO:BUENO`, `ON`, `OFF`, `PESO:`, `LISTO:`

### Pendiente de verificar
- Confirmar en prueba real que IDs globales suben sin retroceder tras pausas entre granos
- Activar `USE_MODELO_DEFECTOS=True` cuando se confirme estabilidad del modelo de 14 clases
- **Medir FPS y CPU/GPU reales con cámara y faja en marcha** (lo medido hasta ahora es con frames sintéticos)
- Verificar en la GTX 1050 Mobile: instalar torch+CUDA compatible, confirmar `self._half=False` y bajar `TILES` a 2×2
- Ajustar `ML_DETECTOR_FPS` / `TILES` si a la velocidad real de faja ByteTrack pierde granos entre frames (desplazamiento por frame)
- **Validar `EQUIVALENCIAS_DEFECTO["desconocido"] = 1.0`** contra la tabla oficial Line Coffee Marañón / INCAL (INC-17). Riesgo: el sesgo del modelo (~40% falsos defectos) + granos que se tocan generan tracks de baja confianza que hoy suman 1.0 al grado cada uno → un lote apto puede caer a Grado 2-3 por artefactos de detección, no por defectos reales. Calibrar `UMBRAL_CONF_CONOCIDO` con granos reales antes de confiar en el grado; considerar equivalencia < 1.0 o solo desvío físico sin penalizar el grado si los falsos "desconocido" son frecuentes.
- **Calibrar `ML_GATE_UMBRAL`** con faja parada vs en marcha (log "gate: diff media="); confirmar que no salta granos reales, o poner `ML_GATE_MOVIMIENTO=false`

### Nota sobre la sección "No TF/PT exports" en Backend Rules
Regla desactualizada. En **GPU** se usa `best.pt` directo (PyTorch nativo, sin
`onnxruntime-gpu`/cuDNN). En **CPU** se prefiere `best.onnx` (más rápido que `.pt`
en CPU). El `onnxruntime` del `requirements.txt` es CPU puro — no trae DirectML
ni CUDA.

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

**Compliance gate:** after any change to `src/routes`, `src/services`, `src/models`, `src/schemas`, `src/apis`, `src/ml`, `src/templates` or `src/static`, delegate to the `architecture-compliance-auditor` subagent (`.claude/agents/architecture-compliance-auditor.md`) before reporting the work as done — it verifies the rules above (and the ML/hardware restrictions below) were actually followed, since they don't always get checked in practice.
