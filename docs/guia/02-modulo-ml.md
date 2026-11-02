# 02 — Módulo de visión artificial (estado al 30-sep-2026)

> Fuente de verdad: `src/ml/tracker.py`, `src/services/tracker_service.py`,
> `src/services/camara_service.py`, `src/ml/models/yolov26n_2cls/constants.py`,
> `src/ml/bytetrack.yaml`, `src/config.py`. Este documento resume su estado y el porqué
> de cada decisión. Cámara: ver además [docs/hardware-camara.md](../hardware-camara.md).

## 1. Modelo activo

| Dato | Valor |
|---|---|
| Nombre | `yolov26n_2cls` (YOLO26n, Ultralytics) |
| Clases | `defecto` (rojo), `verde` (verde). Clase sintética `desconocido` (azul) derivada por el tracker |
| Carpeta | `src/ml/models/yolov26n_2cls/` → `best.pt` (5.4 MB), `best.onnx` (9.8 MB), `constants.py` |
| Versión de pesos | Fechados 2026-07-08. Según el notebook de fine-tuning, corresponden a la versión **v6** del dataset Roboflow `andersonbacach/coffeeren_od` (fotos de celular) |
| Distribución | `best.onnx` **sí está versionado** en Git; `best.pt` está excluido (`.gitignore`: `*.pt`) y se descarga de Google Drive (`MyDrive/CoffeeRen/modelos/`). Sin `best.pt` la GPU usa el `.onnx` en FP32 |
| Entrada | `imgsz=640` siempre (coincide con el entrenamiento) |

**Lo que ya NO existe** (aparece en documentos antiguos): modelo de 17 clases, YOLOv8n/YOLO11n
como candidatos, modelo cascada `yolov26n` de 14 subtipos y `USE_MODELO_DEFECTOS`
(eliminados en `787a7ac`, 2026-07-08), `inference.py` (eliminado en `dcf68a8`).

`yolov26n_2cls_new/` contiene solo el notebook `entrenamiento_yolo26n_v7_finetune.ipynb`,
preparado para el reentrenamiento pendiente (ver [03-reentrenamiento-camara-elp.md](03-reentrenamiento-camara-elp.md)).

## 2. Backend de inferencia

- `torch.cuda.is_available()` decide el device (`0` o `"cpu"`); nunca se hardcodea.
- **GPU → `best.pt`** con PyTorch nativo (sin `onnxruntime-gpu` ni cuDNN). **CPU → `best.onnx`**.
  Lo decide `_resolver_modelo(prefer_pt=cuda_ok)`.
- `self._half = cap >= 7.0 and modelo .pt`. RTX 5070 Ti (12.0) → FP16; GTX 1050 Mobile (6.1)
  y CPU → FP32. **Nunca forzar FP16.**
- `torch==2.12.0+cu130` / `torchvision==0.27.0+cu130` desde
  `https://download.pytorch.org/whl/cu130` (instrucciones en `requirements.txt`). Si
  `torch.__version__` termina en `+cpu`, la GPU queda sin usar y la CPU se satura.
- `ML_MAX_THREADS_CPU` (4) limita hilos de OpenCV y torch.
- Exportación ONNX (para el fallback de CPU), parámetros fijos:
  `model.export(format="onnx", imgsz=640, half=False, dynamic=False, simplify=True)`.
- Warmup con `predict()` al cargar. **No** usar `track(persist=False)` en el warmup (reinicia IDs).

## 3. Hilos en ejecución

| Hilo (`name=`) | Dónde | Vida | Qué hace |
|---|---|---|---|
| `camara-capture` | `camara_service._capture_loop` | Desde el arranque de la app | `read()` continuo; guarda solo el último frame BGR + `time.monotonic()` y señaliza un `Event` |
| `tracker-processing` | `tracker_service._loop_procesamiento` | `POST /video/iniciar` → `/detener` | Espera frame, aplica techo de FPS y gate, llama `procesar_frame()`, guarda el JPEG anotado, persiste evidencias |
| `servo-controller` | `servo_controller._worker` | Desde el arranque | Revisa la cola cada ~10 ms; al vencer `t_referencia + SERVO_DELAY_S` envía `SERVO:DEFECTO`/`SERVO:BUENO` |
| `arduino-reader` | `arduino_serial._reader_loop` | Desde el arranque | Lee el puerto serie y cachea `LISTO:`, `PESO:`, `SISTEMA:LISTO` |
| `arduino-keepalive` | `arduino_serial._keep_alive_loop` | Desde el arranque | Mantiene vivo el puerto USB (Windows lo suspende por inactividad) |

Las rutas FastAPI no bloquean: solo leen el último estado (frame anotado, conteo, eventos)
bajo lock. Ningún hilo llama a otro directamente; se comunican por variables con lock,
`Event` y la cola del servo.

## 4. Pipeline por frame

```
camara_service._capture_loop          frame BGR + time.monotonic()
        │
tracker_service._loop_procesamiento   techo ML_DETECTOR_FPS (30) + gate de movimiento
        │
CoffeeRenTracker.procesar_frame(frame, ts_frame)
   1. _detectar(): grilla 3×3 con solape 320 px → UN predict() en batch (conf 0.15)
   2. _deduplicar_tile(): NMS sin clase dentro de cada tile (IoU 0.80 o caja contenida al 90 %)
   3. _fusionar_cajas(): une el mismo grano partido entre tiles VECINOS
   4. filtro de tamaño GRANO_MIN_PX..GRANO_MAX_PX (50..640)
   5. BYTETracker gestionado a mano (bytetrack.yaml) → ID ByteTrack → ID global
   5. clase por confianza acumulada del track (_resolver_clase / _resolver_clase_display)
   6. compuerta de evidencia → servo_controller.solicitar(t_referencia = primer avistamiento)
   7. recorte de evidencia si el track es "desconocido"
   8. dibujo (color = clase resuelta del track) → JPEG reducido a ML_STREAM_ANCHO
```

### 4.1 Detección por tiles

El modelo se entrenó con **un grano por imagen ocupando 40–77 % de un cuadro de 640 px**. En un
frame 1920×1080 reescalado a 640 cada grano queda diminuto y no se detecta. Se parte el frame en
`TILES_X × TILES_Y` (3×3) con `TILE_SOLAPE_PX` (320) y los 9 recortes se infieren en **un solo
batch**. Medido en RTX 5070 Ti: 3×3 ≈ 40 ms, 2×2 ≈ 20 ms. En CPU o GTX 1050 conviene 2×2.
Regla: `TILE_SOLAPE_PX ≥ lado máximo del grano / 2`.

### 4.2 Fusión consciente de costura

Cada caja lleva su `idx_tile`. `_fusionar_cajas()` solo une cajas de **tiles distintos**
(IoU ≥ `NMS_ENTRE_TILES` 0.5 o IoS ≥ 0.6) y rechaza la fusión si la envolvente supera 1.6× la
caja mayor. Dos cajas del mismo tile ya pasaron por `_deduplicar_tile()`: son granos distintos
que se tocan y nunca se funden. Esto corrigió el subconteo de granos juntos.

`yolov26n_2cls` es un modelo YOLO26 *end2end* (sin NMS): Ultralytics ignora el parámetro `iou`
y, si un grano queda cerca del 50/50, la cabeza emite la misma caja como `defecto` y como
`verde`. Sin `_deduplicar_tile()` ByteTrack recibía las dos: una alternaba la clase del track y
la otra abría un ID nuevo, con lo que el grano se contaba dos veces. Se conserva la caja más
confiada.

### 4.3 IDs globales

ByteTrack reinicia su contador interno tras pausas. `_bytetrack_a_global` mapea cada ID de
ByteTrack a un `_id_global` que **nunca retrocede**. `resetear_conteo()` limpia ambos y marca
`_reset_bytetrack`; el hilo de procesamiento recrea el `BYTETracker` en el frame siguiente.

### 4.4 Resolución de clase

- `_resolver_clase()`: suma la confianza por clase sobre el historial del track
  (`deque(maxlen=30)`). Para marcar defecto, la suma de defecto debe superar a la de la clase
  sana por `MARGEN_DEFECTO` (1.3) — parche del sesgo del modelo hacia "defecto".
  Las clases sanas se derivan de `EQUIVALENCIAS_DEFECTO == 0.0`, no se hardcodean.
- `_resolver_clase_display(track_id, ...)`: si tras `DESCONOCIDO_MIN_FRAMES` (3) el track
  **nunca** superó `UMBRAL_CONF_CONOCIDO` (0.35) en toda su vida (`_conf_max_historico`), es
  `desconocido`. Usa el máximo histórico, no la ventana de 30 (corrige el parpadeo
  desconocido↔verde↔defecto, 2026-09-22).
- El color dibujado sale de la clase resuelta del track, no de la detección del frame.

### 4.5 Objeto desconocido = materia extraña

`EQUIVALENCIAS_DEFECTO["desconocido"] = 1.0`: el servo lo desvía a DEFECTO y suma a los defectos
equivalentes como defecto primario SCA (criterio INCAL: piedras, pajilla, palitos). Se reporta aparte en
`total_desconocidos`. Cada desconocido se recorta del frame sin anotar y se guarda en
`src/resources/desconocidos/{evaluacion_id}/` (`ML_EVIDENCIA_*`, tope 30 por lote). El ML solo
recorta y encola (`drenar_evidencias()`); el service escribe a disco y emite el evento.

**Riesgo abierto:** un grano real de baja confianza (granos que se tocan, mala luz) se marca
desconocido e infla el conteo de defectos. Pendiente calibrar `UMBRAL_CONF_CONOCIDO` con granos reales y
validar la equivalencia 1.0 con la cooperativa.

### 4.6 Servo

- Compuerta `_evidencia_suficiente()`: ≥ `SERVO_MIN_FRAMES` (2) detecciones o una con
  conf ≥ `SERVO_CONF_MIN` (0.45).
- El delay se cuenta desde el **timestamp de captura** del primer avistamiento, no desde el fin
  de la inferencia: la latencia de GPU/CPU no desplaza el disparo.
- `servo_controller` extiende el hold con defectos consecutivos y reintenta 3 veces cada comando.
- La cola del servo es un heap ordenado por `t_referencia + SERVO_DELAY_S` (2026-11-02): un grano
  visto antes se separa antes aunque haya juntado evidencia después que otro. Antes la cola seguía
  el orden de inserción y el grano adelantado esperaba al que tenía delante.
- Watchdog de la faja (2026-11-02): con el motor encendido `arduino_serial` escribe una línea vacía
  cada 1 s; el firmware apaga la faja si pasan 3 s sin recibir nada (backend caído o USB suelto).
- `SERVO_DELAY_S=0.3` (fijado en `.env`, motor JGY370 a PWM 255) y `SERVO_HOLD_S=0.3`: calibrados físicamente.

### 4.7 Cadencia y gate de movimiento

- `ML_DETECTOR_FPS` (30): techo; los frames intermedios se descartan. Bajarlo mucho hace que
  el grano se desplace demasiado entre detecciones y ByteTrack le asigne un ID nuevo (sobreconteo).
- `tracker.hay_movimiento()`: miniatura 160×90 en gris; si la diferencia media con el último
  frame **que pasó a inferencia** es menor que `ML_GATE_UMBRAL` (1.0) no se infiere (faja
  quieta = 0 % GPU). Hasta el 2026-11-02 se comparaba con el frame inmediatamente anterior y,
  con la faja lenta del JGY370, la diferencia entre dos frames seguidos podía no llegar nunca
  al umbral aunque la faja estuviera en marcha. El tracker loguea
  `gate: diff media=` cada 2 s para calibrar. Si el alimentador no es una faja continua:
  `ML_GATE_MOVIMIENTO=false`.

### 4.8 Streaming

`camara_service` ya no codifica cada frame. El único JPEG se arma en `tracker.py` sobre el
frame anotado, reducido a `ML_STREAM_ANCHO` (1280) con calidad `ML_STREAM_JPEG_QUALITY` (80).
`/video/stream` entrega MJPEG a ~30 fps; `/video/frame` el último JPEG.

## 5. Tabla de parámetros

| Parámetro | Valor | Dónde |
|---|---|---|
| `CONF_THRESHOLD` (piso de detección) | 0.15 | `tracker_service.py` |
| `IOU_NMS` (deduplicado sin clase por tile) | 0.80 | `tracker.py` |
| `IOS_CONTENIDA` (caja anidada = mismo grano) | 0.90 | `tracker.py` |
| `NMS_ENTRE_TILES` | 0.5 | `tracker.py` |
| `MARGEN_DEFECTO` | 1.3 | `tracker.py` |
| `SERVO_MIN_FRAMES` / `SERVO_CONF_MIN` | 2 / 0.45 | `tracker.py` |
| `TILES_X` × `TILES_Y`, `TILE_SOLAPE_PX` | 3 × 3, 320 | `constants.py` |
| `GRANO_MIN_PX` / `GRANO_MAX_PX` | 50 / 640 | `constants.py` |
| `UMBRAL_CONF_CONOCIDO` / `DESCONOCIDO_MIN_FRAMES` | 0.35 / 3 | `constants.py` |
| `EQUIVALENCIAS_DEFECTO` | defecto 1, verde 0.0, desconocido 1.0 | `constants.py` |
| ByteTrack | high 0.20, low 0.05, new 0.20, buffer 10, match 0.8 | `bytetrack.yaml` |
| `ML_DETECTOR_FPS` | 30 | `config.py` / `.env` |
| `ML_GATE_MOVIMIENTO` / `ML_GATE_UMBRAL` | true / 1.0 | `config.py` / `.env` |
| `ML_MAX_THREADS_CPU` | 4 | `config.py` / `.env` |
| `ML_STREAM_ANCHO` / `ML_STREAM_JPEG_QUALITY` | 1280 / 80 | `config.py` / `.env` |
| `ML_DEBUG_SERVO` | false | `config.py` / `.env` |
| `ML_EVIDENCIA_DESCONOCIDOS` / `_MAX_POR_LOTE` / `_DIR` | true / 30 / `src/resources/desconocidos` | `config.py` / `.env` |
| `ML_MEDIR_LATENCIA` / `_OBJETIVO_MS` / `_ITERACIONES` / `_DIR` | false / 200 / 50 / `docs/evidencias` | `config.py` / `.env` |
| `CAM_INDICE`, `CAM_WIDTH/HEIGHT/FPS`, `CAM_EXPOSURE`, `CAM_AUTO_EXPOSURE_MANUAL`, `CAM_WB_TEMP` | auto, 1920×1080@90, AEC, 0.25, AWB | `config.py` / `.env` |

## 6. Clasificación del lote (`classifier.py`)

`generar_reporte(conteo, equivalencias)` multiplica cada clase por su equivalencia y suma el
total de defectos equivalentes. Las equivalencias vienen del `constants.py` del modelo cargado.
**No asigna grado SCA ni aptitud Specialty** (retirado el 2026-10-13): el grado depende del tipo
de defecto (primario/secundario) y el modelo solo distingue `defecto`/`verde`. La tabla
`CATEGORIA` se conserva en la BD y `EVALUACION.categoria_id` queda en NULL hasta que el modelo
clasifique por tipo de defecto.

## 7. Rendimiento medido

| Medición | Resultado | Fuente |
|---|---|---|
| CPU del sistema | ~96 % (todo en CPU) → ~25 % (GPU + optimizaciones) | Frames sintéticos, 2026-09-22 |
| Latencia captura → registro | media 89.6 ms, p95 110 ms, p99 125 ms, máx 188 ms (749 iteraciones) — cumple el indicador ≤ 200 ms | [docs/evidencias/analisis_latencia_20260922.md](../evidencias/analisis_latencia_20260922.md) |
| Nuevos ensayos de latencia | 3 CSV del 2026-09-29 (14:32, 14:44, 15:00) | `docs/evidencias/` — **sin analizar todavía** |

## 8. Problema de calidad abierto: domain gap

En pruebas en vivo el modelo marca como defecto ~40 % de granos sanos, de forma intermitente.
Causas investigadas (2026-09-16), en orden de peso:

1. **Cámara distinta entre entrenamiento y producción.** Las ~3 600 fotos se tomaron con un
   celular Samsung S25 FE (ISP con HDR, saturación y color propios); producción usa la ELP, que
   entrega el frame casi crudo. La literatura de *cross-sensor domain shift* indica que basta un
   fine-tuning con 200–500 imágenes del dominio real.
2. **Sin augmentation de tono.** Roboflow solo variaba brillo/exposición, no hue/saturación.
3. **Composición distinta.** Entrenamiento: 1 grano por foto, fondo limpio, recortado.
   Producción: varios granos por tile, a veces tocándose, sobre la faja.
4. Tamaño del dataset (~1 800 por clase): factor menor.

Plan por bloques: **Bloque 1** (aplicado) `CAM_WB_TEMP` para fijar el balance de blancos;
**Bloque 2** augmentation HSV y **Bloque 3** fine-tuning con fotos ELP — ambos en el notebook v7,
pendientes de ejecutar; **Bloque 4** recorte de ROI de la faja antes de inferir.
Procedimiento completo en [03-reentrenamiento-camara-elp.md](03-reentrenamiento-camara-elp.md).

Sobre el dataset público USK-Coffee: no priorizarlo. Su clase "defect" sigue la norma indonesia
SNI 01-2907-2008, no SCA; si se usa, solo como ejemplos extra de `verde` y con augmentation HSV.

## 9. Restricciones absolutas (no cambiar sin permiso explícito del usuario)

- `src/utilities/servo_controller.py` y `src/utilities/arduino_serial.py`: no modificar.
- `SERVO_DELAY_S=0.3`, `SERVO_HOLD_S=0.3`: calibrados físicamente.
- `TrackerService._on_camara_desconectada()`: modo emergencia, no tocar.
- `imgsz=640` y la estructura de hilos productor (cámara) / consumidor (tracker).
- `half` solo condicional por compute capability.
- `track_buffer: 10` en `bytetrack.yaml` (el conteo resiste pausas por el mapeo global, no por el buffer).
- Protocolo Arduino: `ON`, `OFF`, `SERVO:DEFECTO`, `SERVO:BUENO`, `PESO:`, `LISTO:`.
- El ML nunca escribe al puerto serie, al disco ni a la BD directamente.
- La limpieza de IDs inactivos al final de `procesar_frame()` define qué se cuenta:
  `_calcular_conteo_final()` itera `conteo_ids_confianza`, así que un track que sale del cuadro
  sin haber reunido evidencia (no está en `_ids_servados`) se descarta del conteo, y uno que
  accionó el servo se conserva. Cambiar ese criterio altera el conteo del lote.
