# API Video Streaming y Análisis ML — Referencia

Endpoints del router `src/routes/video.py`. Todas las rutas cuelgan del prefijo
`/video`. El procesamiento (detección + ByteTrack) vive en `src/services/tracker_service.py`
y `src/ml/tracker.py`; la clasificación por grado SCA en `src/ml/classifier.py`.

Modelo activo: **`yolov26n_2cls`** (2 clases: `defecto`, `verde`). Se carga una vez
al arrancar. Peso preferido `best.onnx`, con fallback a `best.pt`, en
`src/ml/models/yolov26n_2cls/`.

## Endpoints

### `GET /video/stream` — sin autenticación

Stream MJPEG en vivo con los frames anotados (cajas rojas para `defecto`, verdes
para `verde`, etiqueta `#id clase conf% WxHpx` y contador total).

- `Content-Type: multipart/x-mixed-replace; boundary=frame`
- Ritmo de entrega al cliente: ~30 fps (la captura de la cámara corre a 90 fps).
- Si la captura no está activa el generador termina y el `img` queda sin señal.

```html
<img id="cameraStream" alt="Feed en tiempo real">
<script>
  document.getElementById('cameraStream').src = '/video/stream?t=' + Date.now();
</script>
```

### `GET /video/frame` — sin autenticación

Último frame procesado como JPEG individual (`image/jpeg`). Alternativa al stream
para refrescos puntuales.

- `503` si todavía no hay frame disponible.

### `GET /video/status` — sin autenticación

Estado del sistema de monitoreo. Se usa sin token para diagnóstico y para que el
frontend detecte desconexión de cámara.

```json
{
  "activo": true,
  "modelo": "yolov26n_2cls",
  "conteo_actual": { "defecto": 5, "verde": 12 },
  "camara_desconectada": false,
  "error": null
}
```

### `POST /video/iniciar` — requiere JWT

Inicia captura y procesamiento. Idempotente: si ya está activo responde `200` con
el mismo cuerpo.

```json
{ "mensaje": "Monitoreo iniciado exitosamente", "activo": true }
```

- `500` — no se pudo abrir la cámara (USB desconectada u ocupada).

### `POST /video/detener` — requiere JWT

Detiene captura y streaming.

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
  "conteo_agrupado": {},
  "clases_detectadas": 2,
  "segundos_sin_deteccion": 1.4
}
```

- `total_defectos` / `total_sanos` se derivan de `EQUIVALENCIAS_DEFECTO`
  (`defecto` > 0 cuenta como defecto; `verde` = 0 cuenta como sano).
- `conteo_agrupado` queda vacío con el modelo de 2 clases (no hay subtipos).
- `segundos_sin_deteccion` es `null` si aún no hubo ninguna detección.

### `POST /video/lote/generar-reporte` — requiere JWT

Reporte final del lote según norma SCA (base 350 g).

```json
{
  "total_granos_analizados": 28,
  "total_defectos": 8.0,
  "grado": "Grado 1 (Specialty)",
  "apto_specialty": true,
  "detalle_por_clase": {
    "defecto": { "granos": 8, "peso_por_grano": 1, "defectos_equivalentes": 8.0 }
  },
  "resumen": "Lote analizado: 28 granos — 8.0 defectos equivalentes — Grado 1 (Specialty) — APTO para Specialty"
}
```

Tabla de grados (`src/ml/classifier.py`, 3 grados):

| Defectos equivalentes | Grado |
|---|---|
| 0 – 15 | Grado 1 (Specialty) |
| 16 – 23 | Grado 2 |
| 24 o más | Grado 3 |

`apto_specialty` es `true` cuando `total_defectos <= 15`.

### `POST /video/lote/resetear` — requiere JWT

Reinicia el conteo para un lote nuevo (limpia IDs de ByteTrack y el mapeo de IDs
globales).

```json
{ "mensaje": "Lote reseteado. Listo para nuevo análisis.", "conteo": {} }
```

## Flujo típico

1. `POST /auth/login` → JWT en cookie `access_token`.
2. `POST /video/iniciar` → abre cámara e inicia tracker YOLO + ByteTrack.
3. El frontend muestra `GET /video/stream` y consulta `GET /video/lote/conteo`
   cada 1–2 s; también revisa `GET /video/status` para detectar desconexión.
4. Al cerrar el lote: `POST /video/lote/generar-reporte`.
5. `POST /video/lote/resetear` para el siguiente lote, o `POST /video/detener`.

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
propósito: ByteTrack asocia con sus propios umbrales y la votación por mayoría
(`_mejor_clase_para`) filtra después con conf promedio ≥ 0.45.

### FPS bajo
Procesamiento en CPU. Verificar CUDA con
`python -c "import torch; print(torch.cuda.is_available())"`. Bajar
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
| Modelo | yolov26n_2cls (ONNX, fallback .pt) | `tracker_service.py` |
| Clases | `defecto`, `verde` | `models/yolov26n_2cls/constants.py` |
| Tracker | ByteTrack | `src/ml/bytetrack.yaml` |
| Confianza mínima de detección | 0.15 | `tracker_service.CONF_THRESHOLD` |
| Confianza mínima para votación / servo | 0.45 | `tracker.py` |
| Filtro de tamaño de caja | 50–300 px | `constants.py` (`GRANO_MIN/MAX_PX`) |
| Device | `cuda` si disponible, si no `cpu` | `tracker.py` (automático) |
