# Ficha técnica de la cámara — CoffeeRen

Documento de referencia del hardware de captura. **Leer antes de modificar
`src/services/camara_service.py`, `src/ml/tracker.py`, el pipeline de streaming
o cualquier parámetro de inferencia que dependa de la resolución/FPS.**

La cámara es única y está fija en el prototipo (mirada cenital sobre la faja).
No hay presupuesto para reemplazarla, así que el software debe adaptarse a sus
límites, no al revés.

---

## 1. Identificación

| Campo | Valor |
|---|---|
| Marca / tipo | ELP — módulo USB UVC con lente varifocal |
| Sensor | onsemi (Aptina) **AR0234**, global shutter |
| Producto (Amazon) | ASIN **B0CXDS8F6Q** — "ELP Global Shutter USB Camera, Manual Zoom Telephoto UVC USB2.0 1080P 90fps ... Variable Focus AR0234" |
| Ficha oficial equivalente | ELP-USBGS1200P01 — <https://www.elpcctv.com/elp-2mp-ar0234-sensor-1200p-1080p-90fps-global-shutter-usb-camera-p-388.html> |
| Interfaz | **USB 2.0 High Speed** (no es USB 3.x) |
| Clase | UVC estándar (no requiere driver propietario) |

---

## 2. Sensor

| Parámetro | Valor | Nota |
|---|---|---|
| Modelo | AR0234CS | Sensor de visión industrial (mismo usado en cámaras estéreo tipo OAK/RealSense) |
| Tipo de obturador | **Global shutter** | Expone todo el cuadro a la vez: sin distorsión ni "skew" en objetos en movimiento. Es el motivo por el que esta cámara es adecuada para la faja. |
| Resolución máxima | 1920 x 1200 (2.3 MP) | Relación 16:10 |
| Tamaño de sensor | 1/2.6" | |
| Tamaño de píxel | 3.0 µm | |
| Rango dinámico | 70 dB | |
| Relación señal/ruido | 37 dB | |
| Iluminación mínima | 0.3 lux | Valor de fábrica; a 90fps el tiempo de exposición por cuadro es <=11 ms, así que en la práctica necesita mucha más luz. |
| Control de imagen | AEC (exposición auto), AGC (ganancia auto), AWB (balance de blancos auto) | Todos activos por defecto |

### El global shutter NO elimina el desenfoque por movimiento

El global shutter elimina la **distorsión geométrica** (rolling shutter skew),
no el **motion blur**. El blur depende del tiempo de exposición:

```
blur (px) ≈ velocidad_faja (px/s) x tiempo_exposicion (s)
```

Con AEC y luz insuficiente el sensor alarga la exposición (1/30–1/60 s) y el
grano sale con estela. Para congelarlo hace falta exposición corta
(~1/500 s o menos) **y** iluminación difusa, potente y sin parpadeo.

---

## 3. Modos de vídeo soportados

Todos a **90 fps**, en formato **MJPEG** o **YUY2 (YUYV)**:

| Resolución | Relación | FPS |
|---|---|---|
| 1920 x 1200 | 16:10 | 90 |
| **1920 x 1080** | 16:9 | 90 |
| 1600 x 1200 | 4:3 | 90 |
| 1280 x 960 | 4:3 | 90 |
| 1280 x 720 | 16:9 | 90 |
| 1024 x 768 | 4:3 | 90 |
| 960 x 720 | 4:3 | 90 |
| 800 x 600 | 4:3 | 90 |
| 640 x 480 | 4:3 | 90 |
| 320 x 240 | 4:3 | 90 |

---

## 4. Restricción de ancho de banda — MJPEG es obligatorio

USB 2.0 High Speed entrega ~40 MB/s útiles para vídeo isócrono UVC.

| Modo | Caudal necesario | ¿Entra en USB 2.0? |
|---|---|---|
| 1920x1080 YUY2 @ 90fps | ~373 MB/s | No (≈10x sobre el límite) |
| 1920x1080 YUY2 @ ~9fps | ~37 MB/s | Sí — **este es el modo de degradación** |
| 1920x1080 MJPEG @ 90fps | ~35–40 MB/s | Sí, al borde del límite |

Consecuencias:

- **Si el driver no negocia MJPEG, la cámara cae a YUY2 y el FPS se desploma a
  ~5–9.** A esa tasa los granos saltan de posición entre cuadros y se pierden.
  Es la causa más probable de "no detecta todos los granos" con la faja en
  movimiento.
- En Windows el FOURCC MJPG hay que fijarlo **antes del primer `read()`**; si
  se setea después, el driver lo ignora.
- MJPEG es compresión con pérdida: introduce artefactos de bloque en bordes y
  texturas finas. Tolerable para el modelo de 2 clases (defecto/verde);
  limita la precisión del modelo de 14 clases (defectos sutiles: agrio,
  averanado, blanco).
- Al estar al borde del ancho de banda, un cable largo, un hub o un puerto
  USB 2.0 compartido provocan pérdida de cuadros. Usar cable corto y puerto
  dedicado.

---

## 5. Lente

| Parámetro | Valor | Nota |
|---|---|---|
| Tipo | Varifocal CCTV, **zoom y foco manuales** | No es un lente de visión artificial |
| Distancia focal | ~5–50 mm (verificar en la unidad física) | Teleobjetivo con amplio rango de zoom |
| Montura | M12 (board lens) | |
| Ajuste | Anillos de zoom y foco con tornillos de bloqueo | |

### Implicaciones para el prototipo

- **Foco manual sin repetibilidad**: si alguien roza el anillo, toda la
  detección se degrada. Bloquear el anillo con su tornillo una vez enfocado.
- **Profundidad de campo reducida** a distancia corta con tele: los granos
  parados y acostados tienen alturas distintas y parte de la escena puede
  quedar fuera de foco. Cerrar el diafragma (si el lente lo permite) aumenta
  la profundidad de campo a costa de necesitar más luz.
- **Nitidez y distorsión** de un varifocal barato son peores en los extremos
  del zoom. Un lente prima fijo M12 (p. ej. 8 o 12 mm) calculado para la
  distancia de trabajo sería más nítido y estable, pero no es prioritario.
- **Ajuste correcto**: fijar el zoom para que el **ancho útil de la faja
  llene el ancho del cuadro**. Así cada grano ocupa el máximo de píxeles
  posible sin recortar por software.

### Geometría de trabajo (completar con las medidas reales del prototipo)

| Medida | Valor | |
|---|---|---|
| Distancia cámara–faja | _pendiente_ mm | |
| Ancho útil de la faja (área donde caen los granos) | _pendiente_ mm | |
| Tamaño típico de grano | _pendiente_ mm | 5–8 mm aprox. para café verde |
| Píxeles por mm en el cuadro | _calcular_ | ancho_cuadro_px / ancho_faja_mm |
| Píxeles por grano | _calcular_ | debe ser >= 40–50 px para detección fiable |

---

## 6. Parámetros UVC ajustables

Expuestos por el estándar UVC y accesibles desde OpenCV (`cap.set(...)`):

`Brightness, Contrast, Saturation, Hue, Sharpness, Gamma, White Balance,
Backlight Compensation, Exposure`

### Exposición manual

- Por defecto: AEC (automática).
- Manual en backend DSHOW de Windows:
  - `CAP_PROP_AUTO_EXPOSURE = 0.25` → modo manual (algunos drivers UVC esperan
    `1` o `3`).
  - `CAP_PROP_EXPOSURE = N` donde `N = log2(segundos)`:
    `-5` ≈ 1/32 s, `-6` ≈ 1/64 s, `-7` ≈ 1/128 s, `-8` ≈ 1/256 s.
- Exposición corta congela el grano pero oscurece la imagen: compensar con
  iluminación, **no** subiendo la ganancia (AGC añade ruido que degrada la
  detección).

---

## 7. Cómo está integrada en el código

### `src/config.py` — clase `Config`

| Variable | Default | Override `.env` |
|---|---|---|
| `CAM_INDICE` | vacío (autodetección por nombre) | `CAM_INDICE=1` o `CAM_INDICE=Global Shutter` |
| `CAM_WIDTH` | 1920 | `CAM_WIDTH=` |
| `CAM_HEIGHT` | 1080 | `CAM_HEIGHT=` |
| `CAM_FPS` | 90 | `CAM_FPS=` |
| `CAM_EXPOSURE` | `''` (AEC) | `CAM_EXPOSURE=-6` |
| `CAM_AUTO_EXPOSURE_MANUAL` | 0.25 | `CAM_AUTO_EXPOSURE_MANUAL=1` |
| `CAM_WB_TEMP` | `''` (AWB) | `CAM_WB_TEMP=4500` |

### Selección de la cámara correcta

En una laptop el índice 0 es la webcam interna, no la ELP. **La webcam interna
también negocia MJPEG**, así que el formato no sirve para distinguirlas: hay
que mirar el nombre del dispositivo.

La ELP se enumera en Windows como **"Global Shutter Camera"**. El servicio
(`_orden_indices()` en `camara_service.py`) resuelve así, usando `pygrabber`
para leer los nombres DirectShow:

1. `CAM_INDICE` = número → usa ese índice.
2. `CAM_INDICE` = texto → primera cámara cuyo nombre lo contenga
   (ej. `CAM_INDICE=Global Shutter`).
3. `CAM_INDICE` vacío → **autodetección**: busca un nombre que contenga
   `global shutter` / `ar0234` / `elp` y que NO sea `facing` / `integrated` /
   `internal` / `ir` / `virtual` / `obs` / `depth`.
4. Sin coincidencia de nombre → escaneo con las virtuales/internas al final,
   filtrando por MJPEG.

Sin coincidencia de nombre → escaneo, y se acepta la primera cámara cuyo
**FPS real** sea >= 30 (indicador de MJPEG; ver abajo por qué no se mira el
FOURCC).

Diagnóstico:

```
python scripts/detectar_camaras.py
```

Lista los dispositivos por nombre y mide el FPS real de cada índice con cada
backend. La ELP es la que da `FPS_real` alto (>50) a 1920x1080.

> `pygrabber` (en `requirements.txt`) es solo-Windows y opcional: si falta, la
> autodetección por nombre se desactiva y el servicio cae al escaneo por FPS.
> En ese caso conviene fijar `CAM_INDICE` con el número.

### Backend de captura: Media Foundation, no DirectShow

En este equipo, con `opencv-python-headless`, **`CAP_DSHOW` por índice está
roto**: abre la cámara pero entrega YUY2 a ~5 fps (ni siquiera la ELP negocia
MJPEG por ese backend). El único que funciona es **Media Foundation
(`CAP_MSMF`)**, que sí da 1920x1080 a ~88 fps reales.

Requisitos para que MSMF funcione bien:

- `os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"` **antes de
  importar `cv2`** (lo hace `camara_service.py` en las primeras líneas). Sin
  esto MSMF puede devolver frames negros o lentos.
- MSMF **no reporta el FOURCC** de forma fiable (`CAP_PROP_FOURCC` devuelve 0),
  por eso la detección de MJPEG se hace **midiendo el FPS real** (`_medir_fps`),
  no leyendo el formato.

### `src/services/camara_service.py`

- `_abrir_captura()`: prueba `CAP_MSMF` → `CAP_ANY` → `CAP_DSHOW` (en Windows).
- `_orden_indices()`: decide qué índices probar y cuáles son "confiables"
  (elegidos por nombre / forzados) usando `pygrabber`.
- `_medir_fps()`: 15 lecturas cronometradas; distingue MJPEG (>=30 fps) de
  YUY2 (~5 fps).
- `_configurar_captura()`: fija FOURCC MJPG → resolución → FPS antes del primer
  `read()`, buffer de 1 cuadro, y exposición manual si `CAM_EXPOSURE` tiene valor.
- `_activar()`: arranca el hilo de captura y loguea `~N fps real`; advierte si
  el FPS < 30 (formato sin comprimir).
- Hilo dedicado de captura que solo guarda el último cuadro (el streaming y el
  tracker siempre leen el más reciente).

### `src/ml/tracker.py`

- Reescala cada cuadro a `imgsz=640` para YOLO. Con captura a 1920 de ancho eso
  es una reducción de 3x: **la resolución de captura no cambia el detalle que
  ve el modelo** (se preserva la proporción grano/cuadro). Solo mejoran el
  detalle: (a) recortar un ROI de la faja antes de inferir, o (b) acercar el
  zoom del lente.
- `imgsz=640` y `half=False` están fijados y el ONNX se exportó con
  `dynamic=False`: **el modelo ONNX solo acepta entrada 640x640**. Cambiar
  `imgsz` requiere reexportar.

---

## 8. Qué tener en cuenta al hacer cambios

1. **No subir `CAM_WIDTH/HEIGHT` esperando "más detalle"** para la inferencia:
   YOLO reescala a 640 igual. Más resolución solo sirve para el ROI recortado
   o para el streaming al navegador.
2. **No pasar a YUY2** a 1080p: USB 2.0 no lo soporta a FPS usable.
3. **No subir la ganancia (AGC/`gain`)** para compensar poca luz: el ruido
   degrada la detección más que lo que ayuda el brillo. Resolver con luz.
4. **Verificar siempre el log de arranque**: debe decir la ELP por nombre
   ("Global Shutter Camera") y `~85-90 fps real`. Si dice `~5 fps` o menos, el
   driver está en YUY2: revisar backend (debe ser MSMF), el canal USB
   (cable/hub/puerto) o que se haya elegido la cámara equivocada.
5. **El foco y el zoom son físicos y no repetibles**: cualquier ajuste del
   lente invalida las medidas de la sección 5. Documentar y bloquear los
   anillos.
6. Si algún día se reemplaza la cámara, el candidato correcto es una **AR0234
   en USB 3.x con lente prima fijo M12** — mantiene el global shutter y elimina
   la compresión MJPEG y el lente varifocal.

---

## 9. Checklist de calibración física

- [ ] Cámara perpendicular a la faja, montaje rígido sin vibración.
- [ ] Zoom ajustado: el ancho útil de la faja llena el ancho del cuadro.
- [ ] Foco nítido sobre la superficie de la faja (verificar con el stream al
      100 % de zoom del navegador sobre un grano quieto).
- [ ] Anillos de zoom y foco bloqueados con sus tornillos.
- [ ] Iluminación difusa, sin parpadeo (LED DC o de alta frecuencia), potente.
- [ ] Log de arranque confirma la ELP por nombre y `~85-90 fps real`.
- [ ] Con la faja en marcha, un grano se ve nítido (sin estela) en el stream.
      Si hay estela, bajar `CAM_EXPOSURE` y añadir luz.
- [ ] `CAM_WB_TEMP` fijado (no vacío): el AWB automático deriva el tono cuadro
      a cuadro según lo que entra al encuadre, y eso puede hacer que un grano
      verde cruce al lado "defecto" del modelo solo por el tono del instante,
      no por el grano. Fijar un valor constante y volver a capturar/entrenar
      con la cámara en ese mismo estado si el dataset se toma con la ELP.
- [ ] Medidas de la sección 5 anotadas en este documento.

---

## Fuentes

- Amazon — ELP Global Shutter USB Camera (ASIN B0CXDS8F6Q):
  <https://www.amazon.com/ELP-Global-Shutter-USB-Webcam/dp/B0CXDS8F6Q>
- ELP — 2MP AR0234 1200P/1080P 90FPS Global Shutter USB Camera (ficha técnica):
  <https://www.elpcctv.com/elp-2mp-ar0234-sensor-1200p-1080p-90fps-global-shutter-usb-camera-p-388.html>
- onsemi AR0234CS — datasheet del sensor (referencia general del fabricante).
