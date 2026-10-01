# Manual de Mantenimiento - CoffeeRen

**Versión:** 1.1
**Fecha de elaboración:** 9 de julio de 2026
**Última actualización:** 30 de septiembre de 2026 (inferencia en GPU, fine-tuning con fotos de la cámara ELP)
**Público objetivo:** Técnicos de mantenimiento, administradores del sistema, equipo de desarrollo
**Alcance:** Mantenimiento preventivo mensual, reentrenamiento semestral del modelo de visión artificial y resolución de problemas frecuentes de operación

---

## Tabla de Contenidos

1. [Introducción](#introducción)
2. [Calendario de Mantenimiento](#calendario-de-mantenimiento)
3. [Procedimiento de Reentrenamiento Semestral](#procedimiento-de-reentrenamiento-semestral)
4. [Checklist Mensual de Verificación](#checklist-mensual-de-verificación)
5. [Respaldos de la Base de Datos](#respaldos-de-la-base-de-datos)
6. [FAQ - Problemas Frecuentes](#faq---problemas-frecuentes)
7. [Registro de Mantenimiento](#registro-de-mantenimiento)

---

## Introducción

CoffeeRen combina software (aplicación web + modelo de visión artificial) y hardware (cámara, faja transportadora, servo separador, balanza y Arduino). Cada componente se degrada de forma distinta:

- **El modelo YOLO** pierde precisión con el tiempo porque las condiciones cambian: nuevas variedades de café, iluminación distinta, desgaste de la faja (color de fondo), nuevas campañas de cosecha. Por eso se **reentrena cada 6 meses**.
- **El hardware** se desalinea y ensucia con el uso diario: lente de la cámara, tensión de la faja, calibración de la balanza. Por eso existe un **checklist mensual**.
- **La base de datos** crece con cada evaluación y registro de auditoría. Por eso se respalda y depura periódicamente.

Este manual asume que el sistema ya está instalado y operativo (ver **Manual de Instalación - CoffeeRen**) y que el lector conoce la operación básica (ver **Manual de Usuario - CoffeeRen**).

---

## Calendario de Mantenimiento

| Frecuencia | Actividad | Responsable | Duración estimada |
|---|---|---|---|
| Diaria | Registrar precios del café en `/valor-cafe` | Gerente | 5 min |
| Semanal | Limpieza superficial de lente y faja | Operario | 10 min |
| Mensual | Checklist completo de verificación (sección 4) | Técnico | 60-90 min |
| Mensual | Respaldo de la base de datos (sección 5) | Administrador | 15 min |
| Semestral | Reentrenamiento del modelo YOLO (sección 3) | Equipo de desarrollo | 2-3 días |
| Semestral | Cambio de contraseñas de usuarios | Administrador | 15 min |

---

## Procedimiento de Reentrenamiento Semestral

### ¿Cuándo reentrenar?

- **Calendario regular:** cada 6 meses, idealmente al inicio de cada campaña de cosecha.
- **Reentrenamiento anticipado** si se detecta cualquiera de estas señales:
  - El conteo del sistema difiere en más de **10%** del conteo manual del evaluador (verificación mensual, sección 4).
  - Cambió el hardware: cámara nueva, iluminación distinta, faja de otro color.
  - Se procesan variedades o presentaciones de café que el modelo no conoció en el entrenamiento.

> **Procedimiento detallado vigente:** [docs/guia/03-reentrenamiento-camara-elp.md](../guia/03-reentrenamiento-camara-elp.md).
> Esta sección es el resumen operativo; ante cualquier diferencia, manda la guía.

### Resumen del ciclo (CRISP-ML(Q))

```
1. Recolectar imágenes nuevas  →  2. Etiquetar en Roboflow
        →  3. Augmentar y versionar dataset  →  4. Entrenar en Google Colab
        →  5. Validar métricas y prueba real  →  6. Exportar a ONNX
        →  7. Desplegar con respaldo  →  8. Verificar en producción
```

### Paso 1: Recolección de imágenes nuevas

1. Use la **misma cámara, montaje y configuración** del sistema en producción (ELP AR0234 sobre la faja, 1920×1080, mismos `CAM_WB_TEMP` y `CAM_EXPOSURE` del `.env`) — las imágenes de entrenamiento deben parecerse a lo que el modelo verá en operación. Guarde los recortes de la grilla 3×3 que usa el tracker, no solo el frame completo (ver la guía).
2. Capture granos representativos de la campaña actual:
   - Mínimo **300-500 imágenes nuevas** por sesión de reentrenamiento.
   - Incluya ambas clases: granos sanos (`verde`) y defectuosos (`defecto`), en proporción realista.
   - Varíe condiciones dentro de lo normal: distintas horas del día, densidades de granos sobre la faja, lotes de distintos caficultores.
3. Guarde las imágenes originales en la carpeta de Google Drive del proyecto (`dataset/campaña_<año>-<semestre>/`).

> **Consejo:** guarde frames **crudos** (sin cajas dibujadas): `/video/frame` y `/video/stream` entregan el frame anotado y no sirven para entrenar. Aparte 50-100 imágenes de sesiones distintas en `validacion_elp/` (Google Drive) sin subirlas a Roboflow: sirven para comprobar el modelo nuevo con datos que nunca vio.

### Paso 2: Etiquetado en Roboflow

1. Ingrese al proyecto de Roboflow del equipo (solicite acceso si no lo tiene).
2. Suba las imágenes nuevas al dataset existente (no cree un proyecto nuevo — se pierde el histórico).
3. Etiquete cada grano con un bounding box ajustado y su clase:
   - `defecto` — grano con cualquier defecto físico
   - `verde` — grano sano
4. **Control de calidad del etiquetado:** una segunda persona revisa una muestra del 10% de las imágenes etiquetadas. Los criterios de defecto deben coincidir con la tabla SCA de la cooperativa (`docs/defectos_sca_tabla_referencia.md`).

### Paso 3: Generación del dataset (augmentación y split)

Genere una **nueva versión** del dataset en Roboflow con exactamente esta configuración (es la usada en el entrenamiento original — mantenerla hace comparables las métricas):

| Parámetro | Valor |
|---|---|
| Split | 88% train / 8% validation / 4% test |
| Augmentación | 3× |
| Flip | Horizontal y vertical |
| Rotación | ±15° |
| Brillo | ±15% |
| Exposición | ±5% |
| Blur | 0.5 px |
| Ruido | 0.1% |
| Resolución | 640×640 |

El jitter de tono y saturación (HSV) **no** se configura en Roboflow: lo aplica el entrenamiento (`hsv_h`, `hsv_s`, `hsv_v`, Paso 4). El split debe hacerse por sesión de captura, no al azar, para que frames casi idénticos no queden a la vez en train y test.

Exporte la versión en formato **YOLO** y anote el número de versión del dataset (se registra en la bitácora, sección 7).

### Paso 4: Entrenamiento en Google Colab

1. Abra en Google Colab el notebook del proyecto: `src/ml/models/yolov26n_2cls_new/entrenamiento_yolo26n_v7_finetune.ipynb` (la API key de Roboflow va como secreto de Colab `ROBOFLOW_API_KEY`).
2. Seleccione GPU (**A100** si está disponible; T4 funciona pero tarda más).
3. Se hace **fine-tuning** desde los pesos del modelo en producción (no desde COCO). Parámetros de referencia:

```python
from ultralytics import YOLO

model = YOLO("/content/drive/MyDrive/CoffeeRen/modelos/<version_actual>/best.pt")
model.train(
    data="data.yaml",                # versión nueva del dataset de Roboflow
    epochs=50,
    imgsz=640,                       # NO cambiar — debe coincidir con producción
    batch=32,
    patience=15,
    optimizer="AdamW",
    lr0=0.001,                       # bajo: se afina, no se entrena desde cero
    seed=42,                         # reproducibilidad
    hsv_h=0.02, hsv_s=0.7, hsv_v=0.4 # variación de tono y saturación
)
```

4. Verifique que `data.yaml` declare las clases en el orden `['defecto', 'verde']`; un orden distinto invierte la clasificación.
5. Al finalizar, descargue la carpeta `runs/detect/train/` completa (pesos + métricas + curvas).

### Paso 5: Validación del modelo nuevo

**El modelo nuevo solo reemplaza al actual si lo supera.** Valide en dos niveles:

**a) Métricas de validación** (las genera el propio entrenamiento):

| Métrica | Criterio de aceptación |
|---|---|
| mAP50 | ≥ que el modelo en producción (referencia histórica: 0.767) |
| mAP50-95 | ≥ que el modelo en producción (referencia histórica: 0.757) |
| Precision / Recall por clase | Sin caídas notorias en la clase `defecto` (es la crítica: un defecto no detectado llega al lote bueno) |
| Fotos de `validacion_elp/` | Menos granos sanos marcados como defecto que el modelo actual, sin más defectos marcados como sanos |

**b) Prueba real en banco** (obligatoria antes de desplegar):

1. Prepare 2-3 muestras de café con conteo manual conocido (que el evaluador cuente defectos a mano).
2. Pase las muestras por el sistema con el modelo nuevo cargado en un entorno de prueba.
3. Compare: la diferencia entre conteo del sistema y conteo manual debe ser **≤ 10%**.
4. Verifique además que el servo separa los granos correctos (el modelo no debe introducir latencia extra notoria).

### Paso 6: Exportación a ONNX

El sistema usa `best.pt` cuando hay GPU NVIDIA (FP16 automático en GPUs con compute capability ≥ 7.0) y `best.onnx` cuando corre en CPU. Exporte el ONNX con **exactamente estos parámetros**:

```python
from ultralytics import YOLO

model = YOLO("best.pt")
model.export(format="onnx", imgsz=640, half=False, dynamic=False, simplify=True)
```

- `half=False` en la exportación es obligatorio: el ONNX es el respaldo de CPU y de equipos sin FP16 (GTX 1050 Mobile). El FP16 en GPU lo decide el sistema al cargar `best.pt`, no la exportación.
- `imgsz=640` debe coincidir con el tamaño de entrenamiento.

El resultado es un archivo `best.onnx` (~9-10 MB).

### Paso 7: Despliegue con respaldo

1. **Detenga el servidor** CoffeeRen (Ctrl+C en la terminal de uvicorn).
2. **Respalde el modelo actual** — nunca lo sobrescriba directamente:

```cmd
cd d:\TesisPrj\src\ml\models
mkdir yolov26n_2cls_backup_2026-07
copy yolov26n_2cls\best.onnx yolov26n_2cls_backup_2026-07\
copy yolov26n_2cls\best.pt   yolov26n_2cls_backup_2026-07\
```

3. Copie los archivos nuevos (`best.onnx` y `best.pt`) a `src/ml/models/yolov26n_2cls/` y confirme el orden de clases:
   `python -c "from ultralytics import YOLO; print(YOLO('src/ml/models/yolov26n_2cls/best.pt').names)"` debe mostrar `{0: 'defecto', 1: 'verde'}`.
4. **No modifique `constants.py`** salvo que hayan cambiado las clases del modelo (con el modelo binario defecto/verde, normalmente no cambia). Si cambió la distancia de la cámara a la faja, recalibre `GRANO_MIN_PX` / `GRANO_MAX_PX`.
5. Suba también los pesos nuevos a la carpeta de Google Drive del proyecto (es el origen oficial para nuevas instalaciones).

### Paso 8: Verificación en producción

1. Inicie el servidor y confirme en la consola:
```
Modelo YOLO cargado: yolov26n_2cls (best.pt, conf=0.15, device=0, half=True)
Modelo listo.
```
   En un equipo sin GPU aparece `best.onnx` y `device=cpu`.
2. Corra un lote de prueba corto y verifique conteo, colores (defectos en rojo, sanos en verde, objetos desconocidos en azul) y separación física.
3. Revise con el equipo de desarrollo si conviene recalibrar `MARGEN_DEFECTO` y `UMBRAL_CONF_CONOCIDO` para el modelo nuevo.
4. Registre el reentrenamiento en la bitácora (sección 7).

### Rollback (si el modelo nuevo falla en producción)

1. Detenga el servidor.
2. Restaure los archivos del respaldo:
```cmd
copy yolov26n_2cls_backup_2026-07\best.onnx src\ml\models\yolov26n_2cls\
copy yolov26n_2cls_backup_2026-07\best.pt   src\ml\models\yolov26n_2cls\
```
3. Reinicie el servidor y verifique el mensaje de carga del modelo.
4. Documente en la bitácora qué falló, para corregirlo en el siguiente ciclo.

---

## Checklist Mensual de Verificación

Ejecute este checklist una vez al mes, idealmente el mismo día (ej. primer lunes). Duración estimada: 60-90 minutos. Marque cada ítem y registre las observaciones en la bitácora (sección 7).

### A. Hardware — Cámara

- [ ] Limpiar el lente con paño de microfibra (sin líquidos abrasivos)
- [ ] Verificar que la cámara está firme en su montaje (no se movió ni giró)
- [ ] Verificar el cable USB: sin dobleces, conectado a USB 3.0
- [ ] Iniciar un monitoreo de prueba y verificar imagen nítida y bien iluminada
- [ ] Verificar que la iluminación del gabinete funciona (sin sombras ni reflejos nuevos)

### B. Hardware — Faja transportadora y motor

- [ ] Limpiar la superficie de la faja (restos de café, polvo, manchas)
- [ ] Verificar tensión y alineación de la faja (no se desliza ni roza los bordes)
- [ ] Encender la faja desde el sistema (`ON`/`OFF`) y verificar arranque suave
- [ ] Verificar que la velocidad no cambió (si se ajustó el PWM, actualizar `FAJA_VELOCIDAD_PWM` en el `.env` y `VELOCIDAD` en el firmware — deben coincidir)
- [ ] Revisar ruidos anormales del motor (rodamientos, vibración)

### C. Hardware — Servo separador

- [ ] Verificar tornillos y fijación del brazo del servo
- [ ] Pasar granos de prueba y confirmar que separa defectuosos en el momento correcto
- [ ] Si separa el grano equivocado (adelantado/atrasado): recalibrar el tiempo de viaje (ver FAQ #2)
- [ ] Verificar que el servo vuelve a posición BUENO tras cada separación

### D. Hardware — Balanza (celda de carga) y Arduino

- [ ] Hacer tara desde el sistema y verificar lectura en 0
- [ ] Colocar un peso patrón conocido (ej. pesa de 500 g) y verificar la lectura (tolerancia ±2%)
- [ ] Verificar conexiones del Arduino (cables dupont firmes, sin corrosión)
- [ ] Verificar que el estado del Arduino aparece como conectado en el sistema

### E. Software — Aplicación

- [ ] Reiniciar el servidor y verificar arranque limpio (mensajes de modelo cargado, sin errores en consola)
- [ ] Verificar FPS del monitoreo en vivo (fluido, sin congelamientos)
- [ ] Iniciar sesión con cada rol (Evaluador, Gerente, Administrador) y verificar accesos
- [ ] Completar un flujo corto de prueba: registro → monitoreo → análisis → código EVA
- [ ] Buscar la evaluación de prueba por código en `/reporte`

### F. Software — Precisión del modelo (control de deriva)

- [ ] Preparar una muestra pequeña con conteo manual conocido (ej. 50 granos: 40 sanos, 10 defectuosos)
- [ ] Pasarla por el sistema y comparar el conteo
- [ ] Registrar el % de diferencia en la bitácora
- [ ] Si la diferencia supera el **10%** en dos meses consecutivos → programar reentrenamiento anticipado (sección 3)

### G. Base de datos

- [ ] Ejecutar el respaldo mensual (sección 5) y verificar que el archivo se creó y tiene tamaño razonable
- [ ] Verificar espacio libre en disco (mínimo 10 GB)
- [ ] Revisar el crecimiento de la tabla de auditoría:
```sql
SELECT COUNT(*), MIN(fecha_hora), MAX(fecha_hora) FROM auditoria;
```
- [ ] Ejecutar mantenimiento de PostgreSQL:
```sql
VACUUM ANALYZE;
```

### H. Seguridad y datos

- [ ] Revisar usuarios activos en `/perfil` → Gestión de usuarios (desactivar personal que ya no labora)
- [ ] Revisar el registro de auditoría en busca de acciones inusuales
- [ ] Verificar que los precios del café están actualizados en `/valor-cafe`
- [ ] Verificar que el archivo `.env` no fue modificado sin autorización (SECRET_KEY, calibraciones del servo)

---

## Respaldos de la Base de Datos

### Crear un respaldo (mensual, o antes de cualquier cambio grande)

**Windows (símbolo del sistema, desde cualquier carpeta):**

```cmd
pg_dump -U postgres -d tesis_prj -F c -f "D:\Respaldos\tesis_prj_2026-07.backup"
```

**Linux/macOS:**

```bash
pg_dump -U postgres -d tesis_prj -F c -f ~/respaldos/tesis_prj_2026-07.backup
```

Recomendaciones:
- Nombre el archivo con la fecha (`tesis_prj_AAAA-MM.backup`).
- Guarde una copia **fuera de la computadora** (Google Drive del proyecto o disco externo).
- Conserve al menos los últimos **6 respaldos** mensuales.

### Restaurar un respaldo

```cmd
pg_restore -U postgres -d tesis_prj --clean --if-exists "D:\Respaldos\tesis_prj_2026-07.backup"
```

> ⚠️ La restauración **sobrescribe** los datos actuales de la base. Úsela solo tras confirmar que los datos actuales están dañados o perdidos, y de preferencia haga antes un respaldo del estado actual.

### Verificar un respaldo (sin restaurarlo)

```cmd
pg_restore --list "D:\Respaldos\tesis_prj_2026-07.backup"
```

Debe listar las 15 tablas del sistema. Si el comando falla, el archivo está corrupto — genere el respaldo de nuevo.

---

## FAQ - Problemas Frecuentes

### 1. El conteo del sistema no coincide con el conteo manual

**Causas probables y solución, en orden:**
1. **Lente sucio o cámara movida** — limpie el lente y verifique el encuadre (checklist A).
2. **Iluminación cambió** — ¿se quemó una luz del gabinete? ¿entra luz externa nueva?
3. **Granos muy juntos en la faja** — reduzca la densidad de alimentación; granos encimados se cuentan como uno.
4. **Deriva del modelo** — si la diferencia supera 10% de forma sostenida, reentrene (sección 3).

### 2. El servo separa el grano equivocado (se adelanta o se atrasa)

El tiempo entre que la cámara ve el grano y el servo actúa depende de la **velocidad de la faja**. El sistema lo calcula automáticamente a partir de `FAJA_VELOCIDAD_PWM` (calibración de referencia: a PWM 220, el grano tarda 0.5 s en llegar al servo).

**Solución:**
1. Verifique que `FAJA_VELOCIDAD_PWM` en el `.env` coincide con la constante `VELOCIDAD` del firmware Arduino. Si alguien cambió una sin la otra, este es el problema.
2. Si coinciden y aun así falla, mida el tiempo real en banco (grano desde la cámara hasta el servo) y fíjelo manualmente en el `.env`:
```env
SERVO_DELAY_S=0.55
```
3. Reinicie el servidor tras cualquier cambio en el `.env`.

> ⚠️ No modifique `servo_controller.py` ni `arduino_serial.py` — la calibración se hace solo por `.env`.

### 3. El monitoreo va lento (FPS bajos, video entrecortado)

1. Verifique que no hay otras aplicaciones pesadas abiertas (navegador con muchas pestañas, actualizaciones de Windows).
2. Verifique en el arranque qué dispositivo usa el modelo: `device=0` (GPU) es más rápido que `device=cpu`.
3. Con GPU debe usarse `best.pt` con `device=0`; si el arranque muestra `device=cpu` en un equipo con tarjeta NVIDIA, PyTorch quedó instalado sin CUDA (ver `requirements.txt`). Sin GPU el sistema usa `best.onnx`; en ese caso conviene bajar la grilla de tiles a 2×2 (`constants.py`, con el equipo de desarrollo).
4. Los frames descartados a alta velocidad son normales y aceptables — el sistema prefiere degradarse con elegancia antes que bloquearse. Preocúpese solo si el conteo se vuelve impreciso.

### 4. La cámara se desconectó a mitad de un lote

El sistema entra en **modo de emergencia**: detiene la faja automáticamente para no dejar pasar granos sin analizar.

1. Reconecte la cámara (preferible el mismo puerto USB).
2. Reinicie el monitoreo desde la pantalla o, si no se recupera, reinicie el servidor.
3. El conteo del lote **no se pierde** — el mapeo interno de IDs es resistente a pausas y reconexiones; al reanudar, los IDs continúan sin retroceder.
4. Si se repite con frecuencia: cambie el cable USB (causa más común) o el puerto.

### 5. La balanza da lecturas erráticas o no vuelve a cero

1. Haga tara desde el sistema con la plataforma vacía.
2. Verifique que nada roza la plataforma de pesaje (cables, bordes del gabinete).
3. Verifique los cables de la celda de carga al módulo HX711/Arduino.
4. Valide con un peso patrón (checklist D). Si la desviación persiste tras la tara, la celda de carga puede requerir recalibración en el firmware o reemplazo.

### 6. La aplicación no arranca después de una actualización

1. Lea el error en la consola — casi siempre es uno de estos:
   - `Modelo 'yolov26n_2cls' no encontrado` → faltan `best.onnx`/`best.pt` en `src/ml/models/yolov26n_2cls/` (se descargan de Google Drive).
   - `ModuleNotFoundError` → dependencias nuevas: active el venv y ejecute `pip install -r requirements.txt`.
   - Error de conexión a la BD → ¿PostgreSQL está corriendo? ¿la contraseña de `src/config.py` sigue siendo válida?
2. Si nada funciona, vuelva a la versión anterior del código (`git log` / `git checkout`) y reporte al equipo de desarrollo.

### 7. "No hay rangos de precios de café registrados hoy" al iniciar una evaluación

No es una falla: el sistema **bloquea a propósito** el inicio del monitoreo si no hay precios, porque sin ellos no puede calcular el pago al finalizar.

**Solución:** un Gerente o Administrador debe registrar los rangos de precios del día en `/valor-cafe`. Hágalo parte de la rutina de apertura diaria.

### 8. Una evaluación quedó "a medias" (sin código EVA)

Una evaluación sin código sigue **activa**: al abrirla, el sistema redirige a la pantalla de monitoreo para continuarla. El código EVA se genera recién al finalizar el monitoreo.

- Para terminarla: abra `/monitoreo/<id>` (o desde el listado), finalice el monitoreo y complete el análisis.
- Las evaluaciones finalizadas no pueden volver a monitoreo (el sistema redirige a su análisis) — esto es intencional.

### 9. El disco se está llenando / el sistema se siente lento con el tiempo

1. Revise el tamaño de la base de datos y de la tabla de auditoría (checklist G).
2. Ejecute `VACUUM ANALYZE;` en PostgreSQL.
3. Depure respaldos antiguos (conserve los últimos 6).
4. Si la auditoría supera varios millones de filas, archive los registros de más de 1 año en un respaldo y elimínelos de la tabla (coordinar con el equipo de desarrollo).

### 10. ¿Puedo cambiar el umbral de confianza o los parámetros del modelo?

**No sin autorización del equipo de desarrollo.** Los siguientes valores están calibrados y probados en conjunto:

| Parámetro | Valor | Dónde vive |
|---|---|---|
| Piso de confianza de detección | 0.15 | `tracker_service.py` |
| Tamaño de inferencia | 640 | exportación ONNX + tracker |
| Precisión FP16 | Automática: solo en GPU con compute capability ≥ 7.0 | `tracker.py` |
| Grilla de tiles | 3×3 con solape de 200 px | `constants.py` del modelo |
| Umbral de objeto desconocido | 0.35 | `constants.py` del modelo |
| Margen hacia defecto | 1.3 | `tracker.py` |
| Delay del servo | 0.5 s (fijado en `.env`) | `.env` / `config.py` |
| Hold del servo | 0.3 s | `.env` / `config.py` |
| Filtro de tamaño de grano | 50-480 px | `constants.py` del modelo |

La tabla completa de parámetros está en [docs/guia/02-modulo-ml.md](../guia/02-modulo-ml.md).

Cambiar uno sin ajustar los demás degrada la precisión del conteo o la separación física.

---

## Registro de Mantenimiento

Lleve una bitácora de cada intervención. Puede usar esta plantilla (una fila por actividad):

| Fecha | Actividad | Resultado / Observaciones | % diferencia conteo (si aplica) | Responsable |
|---|---|---|---|---|
| 2026-07-06 | Checklist mensual | OK — lente limpiado, faja tensada | 4% | (nombre) |
| 2026-07-06 | Respaldo BD | tesis_prj_2026-07.backup (verificado) | — | (nombre) |
| | | | | |
| | | | | |

Para el reentrenamiento semestral, registre además:

| Campo | Valor |
|---|---|
| Fecha de reentrenamiento | |
| Versión del dataset (Roboflow) | |
| Imágenes nuevas agregadas | |
| mAP50 / mAP50-95 obtenidos | |
| Resultado de la prueba en banco (% diferencia) | |
| Carpeta de respaldo del modelo anterior | |
| ¿Desplegado o rechazado? ¿Por qué? | |

---

**Fin del Manual de Mantenimiento**

Este manual fue desarrollado para la **Cooperativa Agraria Line Coffee Marañón** como parte del proyecto de tesis "Clasificación Automática de Café Verde Mediante Visión Artificial". Complementa al Manual de Instalación y al Manual de Usuario de CoffeeRen. Para intervenciones no cubiertas por este documento, contacte al equipo de desarrollo de la Universidad Católica Santo Toribio de Mogrovejo (USAT).
