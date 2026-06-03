# Documentación CoffeeRen-Dataset

**Última actualización:** 2026-05-24

## 📌 Propósito del Proyecto

**CoffeeRen-Dataset** es un repositorio para el preprocesamiento y consolidación de imágenes de **granos de café verde defectuoso**. El objetivo es generar un dataset de entrenamiento estandarizado de **640 × 640 píxeles** para modelos de visión por computadora (YOLO, Faster R-CNN, etc.) que detecten y clasifiquen defectos en café según la norma **NTP-ISO 10470:2014** y criterios **SCA** (Specialty Coffee Association).

**Repositorio público:** https://github.com/BanderJ/PublicDatasetGreenCoffee

---

## 🔄 Contexto: CRISP-ML(Q) — Fase 2: Ingeniería de Datos

Este proyecto es parte de la **Fase 2 (Ingeniería de Datos / Data Engineering)** del ciclo **CRISP-ML(Q)** (Cross-Industry Standard Process for Machine Learning with Quality), una metodología iterativa para proyectos de Machine Learning de producción que incluye garantías de calidad.

### Las 6 Fases de CRISP-ML(Q)

1. **Fase 1: Comprensión de los Negocios y los Datos** ✓ Completada
   - Objetivo: Clasificar defectos en café verde
   - Stakeholders y requisitos definidos
   - Norma: NTP-ISO 10470:2014 / SCA
   - Datos identificados: Own/ y Public/
   
2. **Fase 2: Ingeniería de Datos (Preparación de datos)** 🔴 **EN CURSO (Este documento)**
   - Recopilación y consolidación de imágenes
   - Normalización y redimensionamiento (640 × 640 px)
   - Estandarización tonal (CambioTonos)
   - Validación de calidad y consistencia
   - **Crítica para el éxito del modelo**
   
3. **Fase 3: Ingeniería de Modelos de Aprendizaje Automático** ⏳ Siguiente
   - Anotación de imágenes (bounding boxes)
   - Entrenamiento comparativo: YOLOv8n, YOLOv11n, YOLOv26n
   - Validación cruzada
   - Ajuste de hiperparámetros
   - Selección de modelo basada en métricas
   
4. **Fase 4: Garantía de Calidad para Aplicaciones de ML** ⏳ Siguiente
   - Evaluación de métricas (precision, recall, mAP)
   - Pruebas de robustez y casos límite
   - Validación de sesgo y equidad
   - Auditoría del modelo
   
5. **Fase 5: Despliegue** ⏳ Siguiente
   - Implementación en producción
   - Configuración de endpoints/APIs
   - Integración con sistemas existentes
   
6. **Fase 6: Supervisión y Mantenimiento** ⏳ Siguiente
   - Monitoreo de desempeño del modelo
   - Detección de drift (cambios en datos)
   - Reentrenamiento periódico
   - Logs y auditoría en producción

### 🎯 ¿Por Qué es Crítica la Fase 2?

La **Ingeniería de Datos es el fundamento** de todo el ciclo CRISP-ML(Q). La calidad de esta fase determina directamente el éxito de las 4 fases posteriores:

- ✅ **Fase 3 (Modelado):** Imágenes uniformes (640 × 640) → entrenamiento más eficiente
- ✅ **Fase 4 (Calidad):** Normalización tonal evita sesgos → métricas confiables
- ✅ **Fase 5 (Despliegue):** Dataset validado → modelo de confianza para producción
- ✅ **Fase 6 (Supervisión):** Datos consistentes → detección de drift más precisa

### ⚠️ Consecuencias de Saltarse o Acelerar la Fase 2

| Problema | Causa | Fase afectada | Impacto |
|----------|-------|---------------|--------|
| **Modelo con baja precisión** | Imágenes sin normalizar, tamaños inconsistentes | Fase 3, 4 | Predicciones erróneas, métricas bajas |
| **Sesgos por iluminación** | Imágenes originales sin normalización tonal | Fase 3, 4 | El modelo memoriza artefactos de luz, no aprende características reales |
| **Duplicados o corrupción** | Consolidación sin validación | Fase 3, 4 | Dataset contamina métricas, validaciones falsas |
| **Anotación ineficiente** | Imágenes con tamaños diferentes | Fase 3 | Anotadores tardan más, errores aumentan, costo mayor |
| **Bajo recall de defectos raros** | Dataset desbalanceado | Fase 4 | Clases minoritarias no se detectan, validación falla |
| **Falla en Fase 4** | Problemas de calidad no detectados | Fase 4, 5 | Modelo no es certificable para producción |
| **Reentrenamiento costoso** | Descubrir problemas en Fase 5/6 | Fase 5, 6 | Modelo rechazado en producción, semanas perdidas, nuevo ciclo |

**En resumen:** Omitir o acelerar Fase 2 causa **cascada de fallos desde Fase 3 hasta Fase 6**, obligando a reiniciar el ciclo completo CRISP-ML(Q) con costo exponencial.

### 📌 Cómo Este Documento Apoya la Fase 2

Este archivo documenta:
- ✅ **Qué se ha hecho:** Estado de recopilación y procesamiento
- ✅ **Cómo se hace:** Scripts y flujos estandarizados
- ✅ **Qué falta:** Identificación de tareas pendientes
- ✅ **Trazabilidad:** Nomenclatura de archivos para auditoría de Fase 4

**Resultado esperado de Fase 2:** Dataset de 3,480+ imágenes normalizadas, validadas y documentadas, listas para anotación en Fase 3.

---

## 🗂️ Estructura General del Proyecto

```
CoffeeRen-dataset/
├── Own/                    # Imágenes propias — crop centrado
├── Public/                 # Imágenes públicas — resize con padding
├── CambioTonos/           # Normalización de tonalidad (opcional)
├── Dataset_1/             # Dataset multi-clase consolidado
├── CLAUDE.md              # Instrucciones del proyecto
├── README.md              # Resumen técnico
└── DOCUMENTACION.md       # Este archivo
```

---

## 📊 Estado Actual del Proyecto

### Estadísticas de Datos

| Carpeta | Imágenes | Estado | Descripción |
|---------|----------|--------|-------------|
| **Dataset_1** | 3,480 | ✅ Producción | Dataset multi-clase consolidado (17 clases) |
| **Own** (todas) | 4,451 | ⚙️ Procesamiento | Imágenes propias originales + _aux procesadas |
| **Public** (todas) | 2,067 | ⚙️ Procesamiento | Imágenes públicas originales + _aux procesadas |
| **CambioTonos** | 0 | ⏸️ Pendiente | Normalización de tonos (sin imágenes de entrada aún) |

**Total de imágenes consolidadas en Dataset_1:** 3,480 (listas para entrenamiento YOLO)

---

## 📁 Descripción de Carpetas Principales

### 1️⃣ **Own/** — Imágenes Propias

**Propósito:** Procesar imágenes tomadas internamente o de fuentes propias.

**Estructura:**
```
Own/
├── crop.py              # Script principal de procesamiento
├── {clase}/             # Imágenes originales por clase
└── {clase}_aux/         # Salida del crop (generada)
```

**Caractéristicas del procesamiento:**
- **Recorte centrado** de tamaño configurable (defecto: 1500 px)
- **Redimensionamiento** a 640 × 640 px
- **Nomenclatura de salida:** `{clase}_o_{n:04d}.jpg`
  - Ejemplo: `verde_o_0042.jpg`
- **Previsualización:** Genera `preview_crop.jpg` antes de procesar en lote

**Configuración en `crop.py`:**
```python
INPUT_DIR = "dataset"       # Carpeta de entrada (ajustable)
OUTPUT_SUFFIX = "_aux"      # Sufijo para carpeta de salida
CROP_SIZE = 1500            # Tamaño del recorte en píxeles (0 = usar ratio)
CROP_RATIO = 0.60           # Fracción del lado menor si CROP_SIZE = 0
OUTPUT_SIZE = 640           # Resolución final
```

**Uso:**
```bash
python Own/crop.py
```

---

### 2️⃣ **Public/** — Imágenes Públicas

**Propósito:** Procesar imágenes de fuentes públicas o externas.

**Estructura:**
```
Public/
├── resize.py            # Script principal de procesamiento
├── {clase}/             # Imágenes originales por clase
└── {clase}_aux/         # Salida del resize (generada)
```

**Caractéristicas del procesamiento:**
- **Resize con padding negro** (letterbox) para preservar aspect ratio
- **Ajustes suaves de color** (normalización)
- **Redimensionamiento** a 640 × 640 px
- **Nomenclatura de salida:** `{clase}_p_{n:04d}.jpg`
  - Ejemplo: `verde_p_0007.jpg`
- **Interfaz interactiva:** Permite seleccionar carpeta o procesar todas

**Dependencias:** `Pillow` (PIL)

**Uso:**
```bash
python Public/resize.py
```

---

### 3️⃣ **CambioTonos/** — Normalización de Tonalidad (Opcional)

**Propósito:** Normalizar tonos cálidos (naranja, amarillo) hacia el verde en imágenes con desviación de color.

**Estructura:**
```
CambioTonos/
├── calido_frio.py                # Normalización simple
├── calido_frio_sharpness.py       # Normalización + nitidez
├── {carpeta}/                     # Imágenes originales
├── calidos_aux/                   # Salida de calido_frio.py (generada)
└── calidos_aux_aa/                # Salida de calido_frio_sharpness.py (generada)
```

**Características:**
- **Ajuste de saturación:** Reduce la saturación de tonos cálidos
- **Ajuste de temperatura:** Desplaza el balance de blancos hacia verde
- **Nitidez adicional (versión _aa):** Aplica unsharpmask para mejorar detalles
- **Nomenclatura de salida:** `{carpeta}_v_{n:04d}.jpg`
  - Ejemplo: `granos_v_0001.jpg`

**Scripts disponibles:**

| Script | Descripción | Salida |
|--------|-------------|--------|
| `calido_frio.py` | Normalización simple (saturación + temperatura) | `calidos_aux/` |
| `calido_frio_sharpness.py` | Normalización + unsharpmask (nitidez) | `calidos_aux_aa/` |

**Uso:**
```bash
python CambioTonos/calido_frio.py
python CambioTonos/calido_frio_sharpness.py
```

**Estado actual:** Pendiente de imágenes de entrada (carpeta `granos_naranja_amarillo/` vacía).

---

### 4️⃣ **Dataset_1/** — Dataset Multi-Clase Consolidado ✅

**Propósito:** Dataset principal de entrenamiento con todas las clases de defectos.

**Estructura:**
```
Dataset_1/
├── merge_dataset.py       # Script de consolidación
├── augmentation.py        # Script de aumento de datos (opcional)
└── {clase}/               # Clases consolidadas
    ├── agrio_ligero/
    ├── agrio_severo/
    ├── averanado/
    ├── blanco/
    ├── broca_ligero/
    ├── broca_severo/
    ├── cascarilla_cereza_seca/
    ├── cascarilla_pergamino/
    ├── cereza_seca/
    ├── concha/
    ├── deforme/
    ├── inmaduro/
    ├── negro/
    ├── partido_mitad/
    ├── partido_maquina/
    ├── pergamino/
    └── verde/
```

**Características:**
- **17 clases** de defectos según estándares SCA/NTP-ISO 10470:2014
- **Imágenes consolidadas** de `Own/{clase}_aux/` y `Public/{clase}_aux/`
- **Mapeo de nombres:** Reconcilia nombres diferentes entre fuentes
- **Validación automática:** Verifica existencia de carpetas antes de consolidar
- **Confirmación interactiva:** Pide aprobación antes de proceder

**Estadísticas:**
- **Total de imágenes:** 3,480
- **Clases:** 17 (lista abajo)
- **Resolución:** 640 × 640 px
- **Formato:** JPEG (calidad 95)

**Mapeo de nombres entre fuentes:**

| Dataset_1 (Canónico) | Own/ | Public/ |
|---|---|---|
| `broca_severo` | `broca_servera` | `broca_severo` |
| `cascarilla_cereza_seca` | `cascarilla_cerezo_seco` | `cascarilla_cereza_seca` |
| `cereza_seca` | `cereza_seco` | `cereza_seca` |
| `concha` | `concha` | `Concha` |
| `deforme` | `deforme` | `Deforme` |
| `mitad` | `mitad` | `Mitad` |
| `verde` | `verde` | `Verde` |
| **Resto** | Mismo nombre | Mismo nombre |

**Uso:**
```bash
python Dataset_1/merge_dataset.py
```

---

## 🏷️ Clases de Defectos (Dataset_1)

Las 17 clases siguen la norma **NTP-ISO 10470:2014** y criterios SCA:

| Clase | Descripción | Criterio |
|-------|-------------|----------|
| **agrio_ligero** | Fermentación ligera del grano | Fermentación incipiente |
| **agrio_severo** | Fermentación severa del grano | Fermentación avanzada |
| **averanado** | Daño por sequía o maduración irregular | Daño ambiental |
| **blanco** | Decoloración por daño ambiental | Decoloración |
| **broca_ligero** | Perforación superficial por broca (insecto) | Daño de plaga (superficial) |
| **broca_severo** | Perforación profunda por broca | Daño de plaga (profundo) |
| **cascarilla_cereza_seca** | Restos de pulpa seca adherida | Beneficio incompleto |
| **cascarilla_pergamino** | Capa de pergamino adherida | Beneficio incompleto |
| **cereza_seca** | Fruto seco sin beneficiar | Beneficio incompleto |
| **concha** | Deformación tipo caracol o espiral | Malformación |
| **deforme** | Malformación por estrés o desarrollo anómalo | Malformación |
| **inmaduro** | Cosecha prematura, grano sin desarrollar | Cosecha deficiente |
| **negro** | Oxidación severa del grano | Oxidación |
| **partido_mitad** | Grano partido exactamente por la mitad | Defecto mecánico |
| **partido_maquina** | Fractura mecánica por máquina de trilla | Defecto mecánico |
| **pergamino** | Trilla incompleta, capa de pergamino | Beneficio incompleto |
| **verde** | Grano no desarrollado completamente | Grano sano (referencia) |

---

## 🔄 Flujo de Procesamiento Recomendado

### Paso 1: Procesar Imágenes Propias
```bash
python Own/crop.py
```
- Crea `Own/{clase}_aux/` con nombres `{clase}_o_{n:04d}.jpg`
- Permite seleccionar clases o procesar todas
- Genera previsualización `preview_crop.jpg`

### Paso 2: Procesar Imágenes Públicas
```bash
python Public/resize.py
```
- Crea `Public/{clase}_aux/` con nombres `{clase}_p_{n:04d}.jpg`
- Interfaz interactiva para seleccionar carpetas

### Paso 3 (Opcional): Normalizar Tonos
```bash
python CambioTonos/calido_frio.py
python CambioTonos/calido_frio_sharpness.py
```
- Para imágenes con desviación de color (tonos naranja/amarillo)
- Crea `CambioTonos/calidos_aux/` o `CambioTonos/calidos_aux_aa/`

### Paso 4: Consolidar en Dataset_1
```bash
python Dataset_1/merge_dataset.py
```
- Consolida `Own/{clase}_aux/` + `Public/{clase}_aux/`
- Genera `Dataset_1/{clase}/` con imágenes de ambas fuentes
- Aplica mapeo de nombres automático

### Paso 5 (Opcional): Aumentar Datos
```bash
python Dataset_1/augmentation.py
```
- Multiplica imágenes con transformaciones (flip, rotación, etc.)
- Genera archivos con sufijo `_aug_`
- Mantiene proporción de clases

---

## 📝 Nomenclatura de Archivos

La nomenclatura permite rastrear el origen de cada imagen:

| Origen | Patrón | Ejemplo | Nota |
|--------|--------|---------|------|
| **Own** | `{clase}_o_{n:04d}.jpg` | `verde_o_0042.jpg` | Crop centrado |
| **Public** | `{clase}_p_{n:04d}.jpg` | `verde_p_0007.jpg` | Resize letterbox |
| **CambioTonos** | `{carpeta}_v_{n:04d}.jpg` | `granos_v_0001.jpg` | Normalización tonal |
| **Aumentadas** | `{original}_aug_{transform}_{i}.jpg` | `agrio_o_0001_aug_flip_h_1.jpg` | Aumento de datos |

**Todos los archivos de salida:** JPEG 640 × 640 px, calidad 95.

---

## 🛠️ Dependencias

### Requisitos del Proyecto

```bash
pip install -r requirements.txt
```

| Script | Dependencias |
|--------|--------------|
| `Own/crop.py` | `opencv-python`, `numpy` |
| `Public/resize.py` | `Pillow` |
| `CambioTonos/` | `opencv-python`, `numpy`, `scikit-image` |
| `Dataset_1/merge_dataset.py` | Librería estándar (sin dependencias) |
| `Dataset_1/augmentation.py` | `Pillow` |

---

## 📊 Estadísticas Detalladas

### Dataset_1 por Clase

**Total:** 3,480 imágenes en 17 clases

El balance entre clases depende de las imágenes disponibles en `Own/` y `Public/`. Para consultar el balance actual:

```bash
# Linux/Mac
find Dataset_1 -type d ! -name Dataset_1 -exec bash -c 'echo -n "{}: "; ls -1 {} | wc -l' \;

# Windows PowerShell
Get-ChildItem -Directory -Path Dataset_1 | ForEach-Object { 
    $count = @(Get-ChildItem -File -Path $_.FullName).Count
    Write-Host "$($_.Name): $count"
}
```

---

## 🚀 Próximos Pasos — Cierre de Fase 2 y Transición a Fase 3

### Tareas Pendientes de Fase 2 (Ingeniería de Datos)

1. **✅ Completar procesamiento de Own/ y Public/**
   - Verificar que todas las clases están procesadas
   - Validar calidad visual de crop y resize
   - Regenerar `_aux` si hay imágenes nuevas

2. **⏳ Procesar CambioTonos (si aplica)**
   - Si hay imágenes con tonalidad deficiente (naranja/amarillo), procesar:
   ```bash
   python CambioTonos/calido_frio.py
   python CambioTonos/calido_frio_sharpness.py
   ```
   - Incorporar a Dataset_1 si mejoran consistencia

3. **📊 Balance de clases**
   - Verificar distribución del dataset
   - Si hay clases con <50 imágenes, considerar aumento:
   ```bash
   python Dataset_1/augmentation.py
   ```

4. **🔍 Validación visual y de calidad**
   - Revisar 5-10 muestras aleatorias de cada clase
   - Buscar: distorsión, corrupción, errores de nombres
   - Reportar y corregir anomalías
   - **Criticidad:** Defectos aquí afectan precisión del modelo

5. **📋 Documentar estado final de Etapa 2**
   - Total de imágenes por clase
   - Cualidad de imágenes (iluminación, nitidez)
   - Clases con bajo balance
   - Problemas encontrados y resueltos

### Preparación para Fase 3 (Ingeniería de Modelos ML)

Una vez completada y validada la Fase 2:

1. **Exportar Dataset_1 a formato de anotación**
   - Crear estructura compatible con herramientas de anotación (Roboflow, Label Studio, CVAT)
   - Separar en train/val/test (70/15/15 recomendado)

2. **Establecer convención de anotación**
   - Definir clases en YOLO format
   - Crear guía visual para anotadores
   - Establecer criterios de validación

3. **Configurar pipelines de etiquetado**
   - Asignar anotadores
   - Configurar revisión de calidad
   - Establecer métricas de inter-anotador agreement

### Estrategia de Evaluación de Modelos (Fase 3)

En lugar de asumir una versión específica de YOLO, se **evaluarán y compararán múltiples arquitecturas**:

| Modelo | Tamaño | Velocidad | Precisión | Caso de Uso |
|--------|--------|-----------|-----------|------------|
| **YOLOv8n** | Nano (pequeño) | ⚡ Muy rápida | Media | Despliegue en edge/móvil |
| **YOLOv11n** | Nano (mejorado) | ⚡ Rápida | Media-Alta | Balance velocidad-precisión |
| **YOLOv26n** | Nano (última) | ⚡ Rápida | Posiblemente más alta | Modelo más reciente |

**Proceso de evaluación:**
1. Entrenar cada versión con el mismo Dataset_1
2. Evaluar métricas comparativas: precision, recall, mAP@50, mAP@50-95
3. Medir tiempo de inferencia y consumo de recursos
4. Analizar desempeño por clase de defecto
5. **Seleccionar la versión que mejor equilibre precisión y velocidad** para el caso de uso (producción o edge)

**Nota:** La selección final dependerá de:
- Requisitos de latencia (¿tiempo real?)
- Recursos disponibles (GPU, CPU, memoria)
- Métrica crítica (¿precisión o recall para defectos raros?)
- Mantenibilidad futura (soporte y updates)

### Dependencia Crítica: Fase 2 → Fase 3 → Fase 4

```
Fase 2 (Ingeniería de Datos)
  ↓
Dataset_1 validado: 3,480+ imágenes 640×640 normalizadas
  ↓
Fase 3 (Ingeniería de Modelos ML)
  ↓
Anotación + Entrenamiento comparativo (YOLOv8n, YOLOv11n, YOLOv26n)
  ↓
Fase 4 (Garantía de Calidad)
  ↓
Validación de métricas y robustez
  ↓
Fase 5 (Despliegue)
  ↓
Modelo en producción
  ↓
Fase 6 (Supervisión)
  ↓
Monitoreo y mantenimiento
```

**Nota crítica:** No avanzar a Fase 3 sin completar y validar Fase 2. La calidad de Dataset_1 determina directamente el éxito de las Fases 3, 4 y 5. Una Fase 2 deficiente causa fracaso en cascada de todo el ciclo CRISP-ML(Q).

---

## 📌 Notas Importantes

- ✅ **Dataset_1 es el dataset de producción** — 3,480 imágenes listas para entrenamiento YOLO.
- ⚙️ **Own/ y Public/ son carpetas de procesamiento** — Contienen tanto originales como _aux.
- ⏸️ **CambioTonos está pendiente** — Requiere imágenes de entrada en `granos_naranja_amarillo/`.
- 🗑️ **Las carpetas `_aux` son generadas** — No editar manualmente, regenerar si es necesario.
- 🔒 **Mapeo de nombres es automático** — No requiere intervención manual en `merge_dataset.py`.
- 📐 **Todas las imágenes son 640 × 640** — Formato estándar para arquitecturas YOLO (v8, v11, v26).

---

## 📚 Documentación Relacionada

- **CLAUDE.md** — Instrucciones técnicas del proyecto para Claude Code
- **README.md** — Resumen técnico y guía rápida
- **requirements.txt** — Dependencias Python del proyecto
- **Repositorio público:** https://github.com/BanderJ/PublicDatasetGreenCoffee

---

## 🎯 Conclusión: La Importancia de Dedicar Tiempo a Fase 2

**CoffeeRen-Dataset es mucho más que "un conjunto de imágenes."**

Esta **Fase 2 (Ingeniería de Datos) de CRISP-ML(Q)** es el **pilar fundamental** de todo el proyecto. Sin dedicar el tiempo y atención adecuados aquí, el modelo entrenado en Fase 3 y validado en Fase 4 será:

- 📉 **Poco confiable** — Predicciones inconsistentes en Fase 6
- 🎯 **Sesgado** — Memoriza artefactos (iluminación, angulación) en lugar de características reales
- ⚡ **Ineficiente** — Converge lentamente en Fase 3, requiere más iteraciones
- 💰 **Costoso** — Requiere reentrenamiento en Fase 6, pérdida de recursos
- 🚫 **No-producible** — Fracasa validaciones de Fase 4, rechazado en Fase 5

### Lo que Hemos Construido en Fase 2

✅ **Normalización consistente:** Todas las imágenes a 640 × 640 px  
✅ **Dos fuentes de datos:** Own (crop centrado) + Public (resize letterbox)  
✅ **Consolidación limpia:** 3,480 imágenes en 17 clases bien organizadas  
✅ **Trazabilidad:** Nomenclatura clara (`_o_` y `_p_`) para auditoría de calidad en Fase 4  
✅ **Flexibilidad:** Normalización tonal opcional (CambioTonos) para casos especiales  
✅ **Aumento seguro:** Augmentation.py para balance de clases en Fase 3  
✅ **Documentación:** Este archivo y CLAUDE.md para continuidad en todo el ciclo CRISP-ML(Q)  

### El Camino Adelante

**Fase 2 es un compromiso** con la calidad. Dedicarle tiempo ahora:
- **Acelera Fase 3** — Anotación es más rápida con imágenes uniformes, entrenamiento converge faster
- **Facilita Fase 4** — Validación de calidad es más rigurosa, métricas más confiables
- **Reduce Fase 6** — Monitoreo detecta menos deviaciones, menos reentrenamiento necesario

**Resultado:** Un modelo de producción confiable, eficiente y escalable que pueda ser supervisado y mantenido sosteniblemente en Fase 6.

---

**Autor:** Anderson Baca Chuiquimacno | **Email:** ander.jbc115@gmail.com  
**Licencia:** Ver LICENSE (si aplica)  
**Última actualización:** 2026-05-24
