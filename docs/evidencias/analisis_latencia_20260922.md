# Ensayo de latencia del pipeline completo

**Proyecto:** CoffeeRen — Sistema de clasificación automática de granos de café verde
**Fecha del ensayo:** 22 de septiembre de 2026, 16:25 h
**Datos fuente:** `latencia_20260922_162528.csv` (750 iteraciones, en esta misma carpeta)

---

## 1. Indicador evaluado

Del marco lógico del proyecto — **Objetivo específico 4, Resultado 01**:

> Comunicación estable entre la cámara, el sistema de iluminación, la faja transportadora y el módulo de procesamiento digital.
>
> **Indicador objetivamente verificable:** Latencia de comunicación ≤ 200 ms entre captura, procesamiento y registro en al menos 50 iteraciones consecutivas.

---

## 2. Definiciones operativas

Tres precisiones necesarias para interpretar la medición.

**2.1. Una "iteración"** es un cuadro de video que recorrió el trayecto completo: la cámara lo capturó, el modelo lo procesó y su resultado quedó registrado en el conteo del lote.

**2.2. "Registro"** significa que el conteo del lote quedó actualizado en memoria y que el grano ya solicitó su separación física. No corresponde al `INSERT` en PostgreSQL: la persistencia en base de datos ocurre una sola vez por lote, al finalizar la evaluación, no por cada cuadro procesado.

**2.3. La medición excluye el retardo de actuación del servomotor** (`SERVO_DELAY_S = 0.5 s`). Ese intervalo es el tiempo que el grano tarda en desplazarse físicamente desde el campo visual de la cámara hasta el separador mecánico: es una espera *programada* para sincronizar la actuación con el avance de la faja, no tiempo de cómputo del sistema. Incluirlo mediría la velocidad de la faja transportadora, no la latencia del pipeline de visión artificial.

Lo que se reporta es, por tanto, **latencia de decisión**: cuánto tarda el sistema en quedar listo para actuar desde el instante de captura.

---

## 3. Configuración del ensayo

| Componente | Configuración |
|---|---|
| GPU | NVIDIA GeForce RTX 5070 Ti Laptop (compute capability 12.0) |
| Framework | PyTorch 2.12.0+cu130, inferencia en GPU (`device=0`) |
| Modelo | `yolov26n_2cls` (`best.pt`), 2 clases, `imgsz=640` |
| Precisión numérica | FP16 (`half=True`, habilitado por compute capability ≥ 7.0) |
| Cámara | ELP Global Shutter, 1920×1080, ~96 fps reales |
| Estrategia de inferencia | Grilla de 3×3 recortes con solape de 200 px, inferidos en un solo lote |
| Umbral de confianza | 0.15 |
| Techo de detección | 30 fps (`ML_DETECTOR_FPS`) |

---

## 4. Tramos medidos

| Tramo | Desde → hasta |
|---|---|
| `espera_ms` | La cámara marca el cuadro → el hilo de procesamiento lo toma |
| `procesamiento_ms` | Inferencia YOLO sobre los nueve recortes |
| `decision_ms` | Seguimiento ByteTrack, resolución de clase, solicitud al servomotor y actualización del conteo |
| **`total_ms`** | **Captura → registro** (el tramo que evalúa el indicador) |

Los tres primeros suman exactamente el total.

---

## 5. Resultados

Estadísticos sobre 749 iteraciones. La iteración n.º 1 se analiza por separado en la sección 6.

| Tramo | mín | media | p50 | p95 | p99 | máx |
|---|---:|---:|---:|---:|---:|---:|
| `espera_ms` | 0 | 17.2 | 16 | 32 | 47 | 63 |
| `procesamiento_ms` | 31 | 66.7 | 63 | 79 | 93 | 172 |
| `decision_ms` | 0 | 5.7 | 0 | 16 | 16 | 16 |
| **`total_ms`** | **31** | **89.6** | **93** | **110** | **125** | **188** |

*Valores en milisegundos.*

### Distribución de la latencia total

```
   31 ms |   1 |
   46 ms |   2 |
   47 ms |   6 |
   62 ms |  28 | #####
   63 ms |  28 | #####
   78 ms | 204 | #####################################
   79 ms |  35 | ######
   93 ms |  79 | ##############
   94 ms | 216 | ########################################
  109 ms |  68 | ############
  110 ms |  59 | ##########
  125 ms |  20 | ###
  140 ms |   1 |
  157 ms |   1 |
  188 ms |   1 |
 1860 ms |   1 |   <- iteracion n.1, arranque en frio
```

### Estabilidad a lo largo del ensayo

| Iteraciones | Media | Mínimo | Máximo |
|---|---:|---:|---:|
| 1 – 150 | 104.8 | 62 | 1860 |
| 151 – 300 | 90.2 | 62 | 140 |
| 301 – 450 | 87.9 | 62 | 125 |
| 451 – 600 | 88.6 | 62 | 125 |
| 601 – 750 | 88.4 | 31 | 157 |

El sistema converge a un régimen estable en torno a 88 ms tras las primeras 150 iteraciones y se mantiene allí sin degradación. No se observa acumulación de latencia ni fugas de rendimiento durante la corrida.

---

## 6. La iteración n.º 1: arranque en frío

Una sola iteración de las 750 superó el umbral: la primera, con **1860 ms**, de los cuales 1844 ms correspondieron a la inferencia.

Se trata del costo de inicialización de los núcleos CUDA en la primera inferencia sobre un cuadro real de la cámara. El sistema ya ejecuta un precalentamiento con un tensor sintético al cargar el modelo, lo que redujo este costo pero no lo eliminó por completo: la primera inferencia sobre datos reales activa rutas de ejecución que el precalentamiento no cubre.

**No afecta el cumplimiento del indicador**, que exige 50 iteraciones consecutivas: el evento es único, ocurre antes de que ingrese el primer grano al campo visual y no vuelve a presentarse en las 749 iteraciones restantes. La segunda iteración ya registró 188 ms y la tercera, 109 ms.

---

## 7. Veredicto

| Criterio | Exigido | Obtenido | Resultado |
|---|---|---|---|
| Latencia captura → registro | ≤ 200 ms | 89.6 ms (media), 110 ms (p95) | Cumple |
| Iteraciones consecutivas conformes | ≥ 50 | **749** (iteraciones n.º 2 a 750) | Cumple |
| Proporción total dentro del umbral | — | 749 / 750 = 99.87 % | — |

**El indicador se cumple.** La racha de iteraciones consecutivas conformes es **quince veces** la exigida, y la latencia media representa el **45 % del presupuesto** disponible.

El tramo dominante es la inferencia del modelo (66.7 ms de media, 74 % del total). Con ese costo, el rendimiento sostenido del pipeline se sitúa en torno a 11 cuadros por segundo, por debajo del techo configurado de 30 fps: el factor limitante es la inferencia, no la cadencia programada.

---

## 8. Limitaciones del ensayo

**8.1. Resolución del reloj.** La instrumentación empleó `time.monotonic()`, que en Windows se implementa sobre `GetTickCount64()` con una resolución de **15.625 ms**. Todas las mediciones quedaron cuantizadas a múltiplos de ese valor, lo que se refleja en la escasa variedad de valores registrados:

| Tramo | Valores distintos en 750 muestras |
|---|---:|
| `espera_ms` | 7 |
| `procesamiento_ms` | 13 |
| `decision_ms` | 3 |
| `total_ms` | 16 |

Consecuencias:

- **Sobre el veredicto: ninguna.** El margen entre la latencia observada (110 ms en p95) y el umbral (200 ms) es de 90 ms, muy superior al error de cuantización de ±15.6 ms. La conclusión es robusta.
- **Sobre el desglose por tramos: sí las hay.** `decision_ms` solo adopta tres valores (0, 15 y 16 ms), de modo que su media real no puede determinarse con esta instrumentación. Lo mismo ocurre, en menor grado, con `espera_ms`.

Para caracterizar los tramos individuales con precisión sería necesario repetir la medición empleando `time.perf_counter()`, cuya resolución es de 0.0001 ms. Dicha repetición no modificaría el veredicto del indicador.

**8.2. Requerimiento no funcional relacionado.** Los requerimientos no funcionales del proyecto establecen, por separado, una "latencia de respuesta ≤ 200 ms entre detección y actuación". Entre esos dos puntos se sitúa el retardo de sincronización con la faja (`SERVO_DELAY_S = 0.5 s`) descrito en la sección 2.3. Ese retardo es una espera deliberada del diseño, no un tiempo de cómputo. Se recomienda precisar la redacción de dicho requerimiento como "latencia de decisión", o bien dejar constancia explícita de que la actuación se sincroniza intencionalmente con el avance del transporte.

---

## 9. Conclusión

El sistema cumple el indicador del Objetivo específico 4, Resultado 01, con un margen amplio: 749 iteraciones consecutivas por debajo de 200 ms frente a las 50 exigidas, y una latencia media de 89.6 ms.

El pipeline se mantiene estable durante toda la corrida, sin degradación acumulativa. El único evento fuera de umbral corresponde a la inicialización de la GPU y no se repite.

Queda pendiente, si se desea caracterizar los tramos individuales con precisión, repetir la medición con un reloj de alta resolución.

---

## Anexo — Reproducción del ensayo

```
ML_MEDIR_LATENCIA = true          # en .env
ML_LATENCIA_OBJETIVO_MS = 200
ML_LATENCIA_ITERACIONES = 50
```

```
.venv\Scripts\python.exe -u -m uvicorn src.main:app
```

Ejecutar un lote desde `/monitoreo` con la faja en marcha. La instrumentación vuelca automáticamente el CSV en `docs/evidencias/` y emite un resumen por consola cada 50 iteraciones.

Implementación de la medición: `src/utilities/latencia.py`; sondas en `src/ml/tracker.py`, método `procesar_frame`.
