# 03 — Reentrenamiento (fine-tuning v7) con imágenes de la cámara ELP

> **Estado al 30-sep-2026: PENDIENTE.** El notebook está listo
> (`src/ml/models/yolov26n_2cls_new/entrenamiento_yolo26n_v7_finetune.ipynb`), pero todavía no
> se han capturado ni etiquetado las fotos con la ELP, ni existe la versión 7 del dataset en
> Roboflow. Es el trabajo de mayor impacto esperado sobre la calidad de la clasificación.

## 1. Por qué hay que hacerlo

El modelo en producción (`yolov26n_2cls`, versión v6 del dataset) se entrenó con ~3 600 fotos
tomadas con un **celular Samsung S25 FE**: un grano por foto, fondo limpio, recortadas a mano.
En producción las imágenes vienen de la **cámara ELP AR0234** sobre la faja: otro sensor, otro
procesamiento de color, varios granos por recorte, granos que se tocan y fondo de faja.

Resultado observado: ~40 % de granos sanos marcados como defecto, de forma intermitente. Los
parches en código (`MARGEN_DEFECTO`, `CAM_WB_TEMP`, resolución por confianza acumulada) reducen
el síntoma pero no la causa. La literatura sobre *cross-sensor domain shift* indica que un
fine-tuning con **200–500 imágenes del dominio real** cierra la mayor parte de la brecha.

Este procedimiento cubre los bloques 2 (augmentation HSV) y 3 (fotos ELP) del plan descrito en
[02-modulo-ml.md](02-modulo-ml.md#8-problema-de-calidad-abierto-domain-gap).

## 2. Requisitos previos (antes de tomar una sola foto)

Las fotos nuevas deben parecerse a lo que el modelo verá **después** en producción. Si la
iluminación o el lente cambian tras la captura, se crea una brecha nueva.

- [ ] Iluminación definitiva instalada (difusa, sin parpadeo). Ver INC-57.
- [ ] Zoom y foco del lente ajustados y **bloqueados** con sus tornillos. Anotar distancia
      cámara–faja y ancho útil del cuadro. Ver INC-56 y [hardware-camara.md](../hardware-camara.md).
- [ ] `CAM_WB_TEMP` fijado en `.env` (balance de blancos manual). Anotar el valor.
- [ ] `CAM_EXPOSURE` fijado si se usa exposición manual. Anotar el valor.
- [ ] Log de arranque confirma `1920x1080, ~88-96 fps real` (MJPEG, no YUY2).
- [ ] Los mismos valores quedarán en el `.env` de producción. Si cambian después, repetir la captura.

## 3. Captura de imágenes

### 3.1 Qué capturar

| Criterio | Recomendación |
|---|---|
| Cantidad | 300–500 imágenes útiles (mínimo 200) **más** 50–100 apartadas para validación |
| Composición | Como en producción: varios granos por imagen, algunos tocándose, sobre la faja |
| Clases | Mezclar granos sanos y defectuosos en la misma imagen; equilibrar el total de cajas `verde` y `defecto` |
| Variedad | Varios lotes y caficultores, tipos de grano (pergamino/pilado), faja quieta y en marcha |
| Casos difíciles | Granos sanos de tono irregular, granos pegados, bordes del cuadro, defectos leves |
| Materia extraña | Si hay piedras/palitos disponibles, incluir algunas imágenes (ver 4.3) |

### 3.2 A qué escala: recortes iguales a los de producción

El modelo nunca ve el frame entero: `tracker._detectar()` lo corta en una grilla **3×3 con
solape de 200 px** y cada recorte se reescala a 640. En un frame 1920×1080 los recortes miden
entre 840×560 (esquinas) y 1040×760 (centro). Conviene entrenar con **esos mismos recortes**,
para que el grano tenga en entrenamiento el mismo tamaño relativo que en inferencia.

### 3.3 Cómo capturar

No usar `/video/frame` ni `/video/stream`: devuelven el frame **anotado** (cajas y etiquetas
dibujadas). Hay que guardar el frame crudo. Script sugerido (no existe aún en el repositorio;
crearlo como `scripts/capturar_dataset_elp.py` si se aprueba). Usa el mismo `camara_service`
de producción, así aplica la misma configuración `CAM_*` del `.env`:

```python
"""Captura frames crudos de la ELP y guarda los 9 recortes de la grilla de producción."""
import os
import sys
import time

import cv2

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.services.camara_service import camara_service  # noqa: E402

TILES_X, TILES_Y, SOLAPE = 3, 3, 200        # deben coincidir con constants.py
SALIDA = os.path.join("dataset_elp", time.strftime("sesion_%Y%m%d_%H%M%S"))
CADA_S = 2.0                                  # separación entre capturas (evita casi-duplicados)


def grilla(w: int, h: int) -> list[tuple[int, int, int, int]]:
    tw, th = w // TILES_X, h // TILES_Y
    return [(max(ix * tw - SOLAPE, 0), max(iy * th - SOLAPE, 0),
             min((ix + 1) * tw + SOLAPE, w), min((iy + 1) * th + SOLAPE, h))
            for iy in range(TILES_Y) for ix in range(TILES_X)]


os.makedirs(SALIDA, exist_ok=True)
if not camara_service.iniciar():
    sys.exit("No se pudo abrir la cámara ELP.")
print(f"Guardando en {SALIDA}. Ctrl+C para terminar.")
n = 0
try:
    while True:
        if not camara_service.esperar_frame(timeout=2.0):
            continue
        frame, _ = camara_service.obtener_frame_bgr()
        if frame is None:
            continue
        h, w = frame.shape[:2]
        cv2.imwrite(os.path.join(SALIDA, f"f{n:05d}_full.jpg"), frame)
        for i, (x0, y0, x1, y1) in enumerate(grilla(w, h)):
            cv2.imwrite(os.path.join(SALIDA, f"f{n:05d}_t{i}.jpg"), frame[y0:y1, x0:x1],
                        [cv2.IMWRITE_JPEG_QUALITY, 95])
        n += 1
        time.sleep(CADA_S)
finally:
    camara_service.cerrar()
    print(f"{n} frames guardados.")
```

Notas:

- Ejecutar con el servidor **detenido** (la cámara solo admite un proceso).
- Descartar recortes vacíos (solo faja) antes de subir; dejar unos pocos como ejemplos negativos.
- Cada carpeta `sesion_*` es una sesión de captura; anotar en un archivo de texto el lote,
  la fecha, `CAM_WB_TEMP` y `CAM_EXPOSURE` usados.
- `dataset_elp/` no debe subirse a Git (añadirlo a `.gitignore` si se crea dentro del repo).

### 3.4 Separar el conjunto de validación ELP (antes de etiquetar)

Apartar 50–100 imágenes de **sesiones completas distintas** (otros lotes, otro día) y
guardarlas en Google Drive en `MyDrive/CoffeeRen/validacion_elp/`. **No** se suben a Roboflow.
El paso 8 del notebook las usa para comprobar si el problema real mejoró, independiente del mAP.

Por qué por sesión y no al azar: frames consecutivos muestran los mismos granos. Si uno queda
en *train* y otro en *test*, la métrica sale inflada (fuga de datos; ver INC-62).

## 4. Etiquetado en Roboflow

Proyecto: workspace `andersonbacach`, proyecto `coffeeren_od`.

### 4.1 Reglas

- Dos clases, con los nombres **exactos** `defecto` y `verde`. El orden de clases del dataset
  debe seguir siendo `["defecto", "verde"]` (índice 0 y 1), igual que `CLASES` en `constants.py`.
  Un orden distinto invierte rojo/verde y el servo separa los granos equivocados (ya ocurrió con
  `broca_ligero`/`broca_severo`, commit `4ead7f0`).
- Una caja por grano visible, ajustada al contorno. Varias clases en la misma imagen es lo
  normal en detección YOLO; no requiere cambios en `data.yaml`.
- Granos cortados por el borde del recorte: etiquetarlos si se ve más de la mitad.
- El criterio de defecto es el de la cooperativa (SCA/INCAL). Ante duda, consultar con el
  evaluador de Line Coffee Marañón y anotar la decisión, no adivinar.
- Revisión cruzada: una segunda persona revisa el 10 % de las imágenes etiquetadas.

### 4.2 Generar la versión 7

- Partir de la versión 6 (fotos de celular) y **agregar** las fotos ELP: se combinan ambos
  dominios, no se reemplaza.
- Split: respetar la separación por sesión. Si Roboflow lo hace al azar, mover a mano a
  *valid/test* las imágenes de sesiones completas.
- Preprocesado: igual que v6 (resize a 640). Augmentation en Roboflow: la misma de v6
  (flip, rotación ±15°, brillo, exposición, blur, ruido). El jitter de tono lo aplica el
  notebook (`hsv_h`, `hsv_s`, `hsv_v`), no duplicarlo en Roboflow.
- Anotar en esta guía el número de imágenes por split y por dominio.

### 4.3 Materia extraña (decisión pendiente del usuario)

Hoy la materia extraña se detecta por **baja confianza** (clase sintética `desconocido`).
Una alternativa más robusta es entrenar una tercera clase explícita (p. ej. `cuerpo_extrano`)
con fotos reales de piedras, palitos y pajilla. Implica cambiar `CLASES`, `COLORES` y
`EQUIVALENCIAS_DEFECTO` en `constants.py` y revisar el frontend. **No hacerlo sin decisión
explícita del usuario.** Mientras tanto, no etiquetar piedras ni palitos como `defecto` ni como
`verde`: dejarlos sin caja.

## 5. Entrenamiento (Google Colab)

Abrir `entrenamiento_yolo26n_v7_finetune.ipynb` en Colab con GPU. Resumen de lo que hace:

| Celda | Acción |
|---|---|
| 1–2 | Verifica GPU, instala `ultralytics` y `roboflow` |
| 3 | Monta Google Drive (para el `best.pt` de v6) |
| 4 | Descarga la versión 7 del dataset. La API key va como secreto de Colab `ROBOFLOW_API_KEY`, nunca en texto plano |
| 5 | Muestra clases de `data.yaml`. **Verificar que diga `['defecto', 'verde']`** |
| 6 | Fine-tuning desde `MyDrive/CoffeeRen/modelos/yolo26n_resultados_v6_2cls/best.pt` |
| 7 | Evalúa en *test*, muestra curvas y matriz de confusión, guarda en `MyDrive/CoffeeRen/modelos/yolo26n_resultados_v7_2cls_ft_elp/` |
| 8 | Predice sobre `MyDrive/CoffeeRen/validacion_elp/` (solo ELP, fuera de Roboflow) |

Hiperparámetros del fine-tuning (no cambiar `imgsz`):

```python
epochs=50, imgsz=640, batch=32, patience=15, optimizer="AdamW", lr0=0.001, seed=42,
hsv_h=0.02, hsv_s=0.7, hsv_v=0.4
```

`lr0` bajo porque se afina un modelo ya entrenado, no se parte de COCO. Los `hsv_*` agregan la
variación de tono que faltaba en el entrenamiento original.

## 6. Evaluación: comparar v6 contra v7 antes de desplegar

Un mAP mayor en el *test* combinado **no basta**. Registrar, para v6 y v7:

| Métrica | Dónde | v6 | v7 |
|---|---|---|---|
| mAP50 / mAP50-95 (*test* combinado) | celda 7 | | |
| Precisión y recall por clase | `best_model.val(...)` | | |
| Matriz de confusión normalizada | celda 7 | | |
| % de granos sanos marcados `defecto` en `validacion_elp/` | celda 8, conteo manual | ~40 % (referencia) | |
| % de defectos reales marcados `verde` en `validacion_elp/` | celda 8, conteo manual | | |

Criterio sugerido para desplegar: v7 reduce claramente los falsos defectos en `validacion_elp/`
**sin** subir los defectos que pasan como sanos. El umbral exacto lo decide el usuario.

Esta tabla es además la evidencia de la Fase 4 de CRISP-ML(Q) que hoy falta (INC-63).

## 7. Despliegue

1. Respaldar el modelo actual:
   ```powershell
   New-Item -ItemType Directory -Force src\ml\models\yolov26n_2cls_backup_v6
   Copy-Item src\ml\models\yolov26n_2cls\best.pt, src\ml\models\yolov26n_2cls\best.onnx src\ml\models\yolov26n_2cls_backup_v6\
   ```
2. Copiar el `best.pt` de v7 a `src/ml/models/yolov26n_2cls/`.
3. Exportar el ONNX para CPU con los parámetros fijos y copiarlo a la misma carpeta:
   ```python
   from ultralytics import YOLO
   YOLO("best.pt").export(format="onnx", imgsz=640, half=False, dynamic=False, simplify=True)
   ```
4. Verificar el orden de clases del modelo nuevo:
   ```powershell
   python -c "from ultralytics import YOLO; print(YOLO('src/ml/models/yolov26n_2cls/best.pt').names)"
   ```
   Debe imprimir `{0: 'defecto', 1: 'verde'}`. Si no, **no desplegar**.
5. `constants.py` no cambia si las clases siguen siendo las mismas.
6. Arrancar la app y confirmar en el log: `Modelo YOLO cargado: yolov26n_2cls (best.pt, conf=0.15, device=0, half=True)`.
7. Commit: `best.onnx` sí se versiona; `best.pt` se sube a Google Drive en la carpeta v7.
   La carpeta de respaldo no debe versionarse.

Rollback: copiar de vuelta los archivos de `yolov26n_2cls_backup_v6/`.

## 8. Recalibración después de desplegar

Los parches actuales se ajustaron para el sesgo de v6. Con v7 hay que revisarlos con granos reales:

| Parámetro | Valor actual | Qué revisar |
|---|---|---|
| `MARGEN_DEFECTO` (`tracker.py`) | 1.3 | Si v7 ya no tiene sesgo a defecto, acercarlo a 1.0 |
| `UMBRAL_CONF_CONOCIDO` (`constants.py`) | 0.35 | Con un modelo más seguro, menos granos reales caen en `desconocido`; vigilar `total_desconocidos` |
| `GRANO_MIN_PX` / `GRANO_MAX_PX` | 50 / 480 | Con `ML_DEBUG_SERVO=true` revisar descartes por tamaño |
| `SERVO_CONF_MIN` / `SERVO_MIN_FRAMES` | 0.45 / 2 | Que ningún defecto real se quede sin servo |
| Latencia | p95 110 ms | Repetir el ensayo con `ML_MEDIR_LATENCIA=true` |

Cambiar cualquiera de estos valores requiere aprobación del usuario.

## 9. Documentar el resultado

- Llenar la tabla de la sección 6 en esta guía y actualizar la versión de pesos en la sección 1 de [02-modulo-ml.md](02-modulo-ml.md).
- Actualizar [02-modulo-ml.md](02-modulo-ml.md) (versión de pesos) y [04-pendientes.md](04-pendientes.md).
- Cerrar o actualizar en `docs/incidencias/incidencia_proyecto.md`: INC-63 (evaluación formal)
  e INC-65 (domain gap).
- Agregar una entrada en `docs/registro-avances.md` y en [05-historial-de-cambios.md](05-historial-de-cambios.md).
- Actualizar el Manual de Mantenimiento si el procedimiento cambió.
