# API Video Streaming y Análisis ML — Referencia

Endpoints del router `src/routes/video.py`. Todas las rutas cuelgan del prefijo
`/video`. El procesamiento (detección + ByteTrack) vive en `src/services/tracker_service.py`
y `src/ml/tracker.py`; el conteo de defectos equivalentes en `src/ml/classifier.py`.

Modelo activo: **`yolov26n_2cls`** (2 clases: `defecto`, `verde`, más la clase derivada
`desconocido` para materia extraña). Se carga una vez al arrancar desde
`src/ml/models/yolov26n_2cls/`: con GPU `best.pt` (FP16 si la tarjeta lo soporta), en CPU
`best.onnx`. Detalle del pipeline: [docs/guia/02-modulo-ml.md](guia/02-modulo-ml.md).

## Endpoints

### `GET /video/stream` — requiere sesión

Stream MJPEG en vivo con los frames anotados (cajas rojas para `defecto`, verdes
para `verde`, azules para `objeto desconocido`, etiqueta `#id clase conf% WxHpx` y
contador total). El frame se reduce a `ML_STREAM_ANCHO` (1280 px) con calidad JPEG
`ML_STREAM_JPEG_QUALITY` (80) antes de enviarlo.

- `Content-Type: multipart/x-mixed-replace; boundary=frame`
- Ritmo de entrega al cliente: ~30 fps (la captura de la cámara corre a 90 fps).
- Si la captura no está activa el generador termina y el `img` queda sin señal.

```html
<img id="cameraStream" alt="Feed en tiempo real">
<script>
  document.getElementById('cameraStream').src = '/video/stream?t=' + Date.now();
</script>
```

### `GET /video/frame` — requiere sesión

Último frame procesado como JPEG individual (`image/jpeg`). Alternativa al stream
para refrescos puntuales.

- `503` si todavía no hay frame disponible.

### `GET /video/status` — requiere sesión

Estado del sistema de monitoreo. El frontend lo consulta para detectar desconexión
de cámara. Desde el 2026-11-02 los tres endpoints de lectura de video exigen la cookie
`access_token`, como el resto de la API (`AGENTS.md`, sección 5.5); el navegador la envía
sola en `<img src="/video/stream">` y en `fetch` del mismo origen.

```json
{
  "activo": true,
  "modelo": "yolov26n_2cls",
  "fps": 17.4,
  "conteo_actual": { "defecto": 5, "verde": 12 },
  "evaluacion_id": "0199....",
  "camara_desconectada": false,
  "error": null
}
```

`evaluacion_id` es la evaluación dueña del lote en curso: el monitoreo lo compara con la
suya para no adoptar un lote que quedó activo de otra evaluación.

`fps` es la velocidad de procesamiento del modelo: frames procesados por YOLO en el último
segundo (ventana deslizante). Vale 0 si no se procesó ningún frame en ese segundo (faja
quieta con el gate de movimiento). Es el valor que muestra el indicador de la esquina del
video en el monitoreo; el texto amarillo del frame ya no incluye FPS.

### `POST /video/iniciar` — requiere JWT

Inicia captura y procesamiento. Si el mismo lote ya está activo, responde `200` sin
reiniciarlo. La validación se ejecuta en el servidor bajo el bloqueo de control.

El cuerpo opcional usa `ControlMonitoreoRequest`: `{"evaluacion_id": "<UUID>"}` asocia
el lote a una evaluación. Prueba no envía cuerpo y trabaja sin evaluación. Los UUID se
normalizan a minúsculas después de validar su formato.

- Si queda un lote asociado a una evaluación, activo o detenido, solo un Evaluador con
  ese mismo ID puede iniciarlo. Reanudarlo conserva el conteo y el registro de eventos.
- Sin ID o con otro ID, responde `409` sin borrar el conteo ni cambiar la asociación.
- Asociar una evaluación exige rol Evaluador (`403` para otros roles). Iniciar Prueba sin
  evaluación sigue disponible para toda sesión cuando no hay una evaluación asociada.
- Una Prueba activa no se convierte implícitamente en evaluación: iniciar con un ID
  distinto responde `409`; primero debe detenerse esa captura sin evaluación.

```json
{ "mensaje": "Monitoreo iniciado exitosamente", "activo": true }
```

- `500` — no se pudo abrir la cámara (USB desconectada u ocupada).

### `POST /video/detener` — requiere JWT

Detiene captura y streaming.

- Lote de evaluación: enviar `{"evaluacion_id": "<UUID de la evaluación>"}` con sesión
  de Evaluador. El ID debe coincidir con el lote del servidor.
- Lote de Prueba sin evaluación: cualquier sesión puede detenerlo sin cuerpo.
- `409` si hay evaluación asociada y falta su ID o se envía otro; `403` si el ID coincide
  pero el rol no es Evaluador; `422` si el UUID tiene formato inválido. El rechazo conserva
  estado, conteo, imagen y eventos, sin enviar comandos al hardware.

La asociación y el conteo se conservan después de detener, para poder finalizar la
evaluación. La comprobación y la operación comparten un bloqueo de control con el arranque
de otro lote. La parada interna al cerrar la aplicación y el modo de emergencia se conservan.

Para abandonar un lote pendiente, un Evaluador puede enviar
`{"evaluacion_id": "<UUID del lote abandonado>", "descartar_lote": true}`
(`DetenerMonitoreoRequest`). Con ID coincidente, se detiene, se descarta su conteo en memoria
y se libera la asociación. El valor predeterminado es `false`: una parada normal conserva
el lote. El descarte explícito permite iniciar después la evaluación nueva; un ID obsoleto
recibe `409` y un rol no autorizado recibe `403`.

`PATCH /evaluacion/{id}/finalizar` obtiene el conteo y persiste la finalización bajo el mismo
bloqueo de control. Solo después de guardar correctamente libera la asociación:
`GET /video/status` informa `evaluacion_id: null` y Prueba vuelve a funcionar sin reiniciar
el servidor. Un fallo de persistencia conserva ID y conteo para reintentar. Repetir una
finalización ya guardada conserva su código y no libera otro lote que haya empezado después.

```json
{ "mensaje": "Monitoreo detenido", "activo": false }
```

### `GET /video/lote/conteo` — requiere JWT

Conteo actual del lote, enriquecido. No genera reporte final.

```json
{
  "conteo": { "defecto": 8, "verde": 20 },
  "total_granos": 28,
  "total_defectos": 8,
  "total_sanos": 20,
  "total_desconocidos": 0,
  "conteo_agrupado": {},
  "clases_detectadas": 2,
  "segundos_sin_deteccion": 1.4
}
```

- `total_defectos` / `total_sanos` se derivan de `EQUIVALENCIAS_DEFECTO`
  (equivalencia > 0 cuenta como defecto; `verde` = 0 cuenta como sano).
  `desconocido` (equivalencia 1.0) **está incluido** en `total_defectos`;
  `total_desconocidos` lo informa aparte como subconjunto.
- `conteo_agrupado` queda vacío con el modelo de 2 clases (no hay subtipos).
- `segundos_sin_deteccion` es `null` si aún no hubo ninguna detección.

### `GET /video/eventos?desde=<seq>` — requiere JWT

Eventos del lote en curso con número de secuencia mayor que `desde` (bitácora del
monitoreo: inicio, primer grano, rachas sin granos, objetos desconocidos con su foto,
desconexión de cámara). El frontend lo consulta en el mismo ciclo que el conteo y acumula
las entradas. Al finalizar la evaluación los eventos se guardan en `EVENTO_MONITOREO`.

```json
{ "eventos": [ { "seq": 3, "segundo": 41, "tipo": "objeto_desconocido", "severidad": "alerta", "mensaje": "Objeto extraño detectado — desviado al canal de defecto.", "imagen_url": "/resources/desconocidos/<evaluacion>/<archivo>.jpg", "datos": { "track_id": 12, "conf": 0.21 } } ], "cursor": 3 }
```

### `POST /video/lote/generar-reporte` — requiere sesión de Evaluador

Reporte final del lote: total de defectos equivalentes (equivalencias del modelo cargado).

```json
{
  "total_granos_analizados": 28,
  "total_defectos": 8.0,
  "detalle_por_clase": {
    "defecto": { "granos": 8, "peso_por_grano": 1, "defectos_equivalentes": 8.0 }
  },
  "resumen": "Lote analizado: 28 granos — 8.0 defectos equivalentes"
}
```

No incluye grado SCA ni aptitud Specialty: el grado depende del tipo de defecto y el modelo actual
solo distingue `defecto`/`verde`.

### `POST /video/lote/resetear` — requiere JWT

Reinicia el conteo para un lote nuevo (limpia IDs de ByteTrack y el mapeo de IDs
globales).

Usa `ControlMonitoreoRequest` con las mismas condiciones de rol e ID que una parada normal.
Prueba no puede resetear un lote de evaluación, aunque el
procesamiento ya se haya detenido y el conteo esté esperando su finalización.

```json
{ "mensaje": "Lote reseteado. Listo para nuevo análisis.", "conteo": {} }
```

## Flujo típico

1. `POST /auth/login` → JWT en cookie `access_token`.
2. `POST /video/iniciar` con el ID de evaluación → abre cámara e inicia tracker YOLO + ByteTrack.
3. El frontend muestra `GET /video/stream` y consulta `GET /video/lote/conteo`
   cada 1–2 s; también revisa `GET /video/status` para detectar desconexión.
4. Al cerrar el lote: `POST /video/detener` con su ID y `POST /video/lote/generar-reporte`.
5. Finalizar y calcular el rendimiento mediante las rutas de evaluación.

Prueba conserva iniciar, resetear y detener sin ID para sus propios lotes. Si detecta
una evaluación en monitoreo, no la adopta y muestra el aviso. Al abrir otra evaluación,
Monitoreo pide confirmación antes de detener y descartar el lote pendiente. Muestra el
caficultor y la fecha de registro del resumen; si no se obtiene, usa «una evaluación anterior». Cancelar no envía
órdenes de control; aceptar envía detener con el ID del lote anterior y `descartar_lote: true`,
y después inicia el nuevo. Una captura de Prueba sin evaluación se detiene antes de iniciar
un monitoreo asociado.

Patrón de consumo (vanilla JS, como en `src/static/js/test.js` y `monitoreo.js`):

```javascript
async function refrescarConteo() {
  const res = await fetch('/video/lote/conteo');
  if (!res.ok) return;
  const data = await res.json();
  // data.total_granos, data.total_defectos, data.total_sanos ...
}
```

## Solución de problemas

### El stream no muestra imagen
La captura no está iniciada. Llamar `POST /video/iniciar` antes de fijar el `src`
del `img`.

### `500` al iniciar
Cámara no detectada u ocupada. Verificar el cable USB de la ELP AR0234, cerrar
otras apps que usen la cámara y confirmar el índice con
`python scripts/detectar_camaras.py`.

### Conteo siempre vacío
Modelo sin cargar o umbral de confianza. Verificar con `python check_model.py`.
El piso de confianza (`CONF_THRESHOLD` en `tracker_service.py`) es 0.15 a
propósito: ByteTrack asocia con sus propios umbrales y la clase se resuelve por
confianza acumulada del track. Si la faja está quieta, el gate de movimiento omite la
inferencia (`ML_GATE_UMBRAL`); con `ML_GATE_MOVIMIENTO=false` se desactiva.

### FPS bajo
Procesamiento en CPU. Verificar CUDA con
`python -c "import torch; print(torch.__version__, torch.cuda.is_available())"`
(debe mostrar `+cu130` y `True`). En CPU conviene bajar la grilla a 2×2 en `constants.py`. Bajar
`CAM_WIDTH`/`CAM_HEIGHT` en `.env` alivia el bus USB y el encode, pero no cambia
el detalle que ve YOLO (siempre reescala a 640).

## Especificaciones técnicas

| Parámetro | Valor | Origen |
|---|---|---|
| Resolución de captura | 1920×1080 (configurable) | `Config.CAM_WIDTH/CAM_HEIGHT` |
| FPS de captura | 90 (configurable) | `Config.CAM_FPS` |
| FPS de entrega al cliente | ~30 | `video.py` (`asyncio.sleep(0.033)`) |
| Codec de streaming | MJPEG | `video.py` |
| Tamaño de inferencia | 640 | `tracker.py` (`imgsz=640`) |
| Modelo | yolov26n_2cls (`best.pt` en GPU, `best.onnx` en CPU) | `tracker_service.py` |
| Clases | `defecto`, `verde` (+ `desconocido` derivada) | `models/yolov26n_2cls/constants.py` |
| Grilla de inferencia | 3×3, solape 200 px, un batch | `constants.py` |
| Tracker | ByteTrack (`BYTETracker` manual) | `src/ml/bytetrack.yaml` |
| Confianza mínima de detección | 0.15 | `tracker_service.CONF_THRESHOLD` |
| Confianza mínima para servo | 0.45 (o 2 detecciones) | `tracker.py` |
| Umbral de objeto desconocido | 0.35 | `constants.py` |
| Filtro de tamaño de caja | 50–480 px | `constants.py` (`GRANO_MIN/MAX_PX`) |
| Techo de detección | 30 fps | `Config.ML_DETECTOR_FPS` |
| Device | `cuda` si disponible, si no `cpu`; FP16 si compute capability ≥ 7.0 | `tracker.py` (automático) |
