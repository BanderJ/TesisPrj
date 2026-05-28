# Registro de Avances - Tesis CoffeeRen 2026

**Última actualización:** 25 de mayo de 2026

---

## Sprint 0: Comprensión del Negocio y los Datos ✅ COMPLETADO

**Periodo:** Enero - Abril 2026  
**Estado:** Completado con éxito

### Hitos Alcanzados

- ✅ Identificación de desafíos operativos en la Cooperativa Agraria Line Coffee Marañón
- ✅ Validación social mediante encuestas a 10+ caficultores (80% de disposición favorable)
- ✅ Definición de criterios de éxito en 3 niveles: empresarial, ML y económico
- ✅ Recopilación de datos híbrida: datasets públicos (USK-Coffee Kaggle + Roboflow) + dataset propio

### Entregables

- Carta de aceptación para ejecución de tesis
- Análisis de encuestas (disponible en Google Sheets)
- Dataset híbrido inicial: ~12,000 imágenes brutas

---

## Sprint 1: Preparación de los Datos (Fase 2 CRISP-ML(Q)) ✅ COMPLETADO

**Periodo:** Abril - Mayo 2026  
**Estado:** Completado con validación de calidad

### Contexto

Este sprint implementó la **Fase 2 (Ingeniería de Datos) del ciclo CRISP-ML(Q)**, estableciendo el fundamento técnico del sistema CoffeeRen tanto en infraestructura backend como en preparación de datos para ML.

### 1. Fundación Técnica del Sistema

#### Base de Datos
- **PostgreSQL 18** con UUIDv7 en tablas transaccionales (personal, caficultor, evaluacion) e INT en tablas maestras
- Esquema normalizado con relaciones de integridad referencial
- Soporte para JWT + roles (admin, caficultor, personal técnico)

#### API REST (FastAPI)
- **Arquitectura Models-Schemas-Services-Routes** (4 capas limpias)
- **Autenticación:** Argon2id para hashing, JWT httponly cookies (7 días TTL)
- **Endpoints implementados:**
  - `/auth/login` - Autenticación JWT
  - `/caficultor/*` - Gestión de caficultores (CRUD, búsqueda, validación)
  - `/evaluacion/*` - Evaluación de lotes y defectos
  - `/tipo-documento/*` - Catálogos (DNI, Pasaporte, Carnet)
  - `/reniec/*` - Integración con API RENIEC (validación de documentos)
  - `/ubigeo/*` - Integración UBIGEO (ubicaciones geográficas)
  - `/valor-cafe/*` - Cotización internacional de café
  - `/camara/*` - Streaming de cámara (ELP AR0234) y capturas
  - `/arduino/*` - Comunicación serial con hardware

#### Interfaz Web (Jinja2 + Tailwind CSS)
- **Login y registro** - Autenticación JWT con validaciones Pydantic
- **Monitoreo de lotes** - Búsqueda, filtrado por rango de pesos e ingreso de datos
- **Nuevo caficultor** - Formulario con validación RENIEC integrada
- **Evaluación** - Interfaz para clasificación de defectos con streaming Arduino
- **Análisis** - Reportes con métricas de calidad

### 2. Preparación de Dataset para ML (Dataset_1)

#### Consolidación de Imágenes

| Fuente | Cantidad | Características |
|--------|----------|-----------------|
| **Own/** | 2,413 imágenes | Crop centrado (1500px → 640×640), etiquetado: `{clase}_o_{n:04d}.jpg` |
| **Public/** | 1,067 imágenes | Resize letterbox (640×640), etiquetado: `{clase}_p_{n:04d}.jpg` |
| **Total Dataset_1** | **3,480 imágenes** | ✅ Normalizadas, validadas, listas para anotación |

#### 17 Clases de Defectos (NTP-ISO 10470:2014 + SCA)

| Clase | Descripción |
|-------|-------------|
| agrio_ligero | Fermentación ligera |
| agrio_severo | Fermentación severa |
| averanado | Daño por sequía |
| blanco | Decoloración ambiental |
| broca_ligero | Perforación superficial |
| broca_severo | Perforación profunda |
| cascarilla_cereza_seca | Restos de pulpa |
| cascarilla_pergamino | Capa pergaminosa |
| cereza_seca | Fruto sin beneficio |
| concha | Deformación espiral |
| deforme | Malformación |
| inmaduro | Cosecha prematura |
| negro | Oxidación severa |
| partido_mitad | Partición exacta |
| partido_maquina | Fractura mecánica |
| pergamino | Trilla incompleta |
| verde | Grano sano (referencia) |

#### Procesamiento Implementado

- ✅ **Own/crop.py** - Recorte centrado configurable con previsualización
- ✅ **Public/resize.py** - Resize con padding negro (letterbox) para aspect ratio
- ✅ **Dataset_1/merge_dataset.py** - Consolidación con mapeo de nombres automático
- ✅ **Nomenclatura trazable** - Sufijos `_o_` (own) y `_p_` (public) para auditoría

#### Validación de Calidad

- ✅ Descarte de imágenes con blur > umbral tolerable
- ✅ Eliminación de capturas con reflejos especulares
- ✅ Verificación de balance entre clases
- ✅ Validación de integridad de archivos

### 3. Scripts de Apoyo (Fase 2)

| Script | Propósito | Estado |
|--------|-----------|--------|
| `CambioTonos/calido_frio.py` | Normalización de tonos cálidos | ⏸️ Pendiente (sin imágenes entrada) |
| `CambioTonos/calido_frio_sharpness.py` | Normalización + nitidez | ⏸️ Pendiente |
| `Dataset_1/augmentation.py` | Aumento de datos (flip, rotación) | ⏸️ Reservado para balance |

### Archivos Impactados

```
src/
├── database/bd.py          # Clase Connection (psycopg2 wrapper)
├── database/script.sql     # Esquema PostgreSQL 18
├── main.py                 # Inicialización FastAPI
├── config.py               # Variables de entorno
├── routes/                 # 9 módulos de rutas
├── services/               # 8 módulos de lógica de negocio
├── models/                 # 7 módulos de persistencia (SQL)
├── schemas/                # 6 módulos de validación Pydantic
├── utilities/              # JWT, validadores, helpers
├── static/                 # CSS Tailwind, iconos, JS
└── templates/              # 5 templates Jinja2

docs/documentacion/
├── DOCUMENTACION.md        # Guía completa Fase 2 (Dataset)
├── Analisis_Requerimientos.md
└── Product_Backlog_Sprints.md
```

### Métricas Sprint 1

| Métrica | Valor |
|---------|-------|
| Imágenes consolidadas | 3,480 |
| Clases de defectos | 17 |
| Resolución estándar | 640 × 640 px |
| Endpoints API | 9+ rutas activas |
| Templates | 5 (login, registro, monitoreo, nuevo-caficultor, analisis) |
| Tasa de cobertura de clases | 100% |
| Imágenes validadas | 3,480 (100%) |

### Validación del Sprint 1

- ✅ Dataset balanceado y aumentado disponible en desarrollo
- ✅ Infraestructura backend (BD + API + UI) funcional
- ✅ Integración Arduino → API → UI completada
- ✅ Autenticación JWT + roles implementada
- ✅ Documentación técnica completa (DOCUMENTACION.md)

**DoD (Definition of Done):** Sprint 1 completado con éxito. Sistema listo para fase de anotación (Fase 3).

---

## Sprint 2: Ingeniería de Modelos ML (Fase 3 CRISP-ML(Q)) 🔄 EN CURSO

**Periodo:** Mayo - Junio 2026  
**Estado:** Fase inicial - Preparación para anotación

### Contexto

Iniciamos **Fase 3 (Ingeniería de Modelos ML)** del ciclo CRISP-ML(Q), que incluye:
1. Anotación de imágenes (bounding boxes)
2. Entrenamiento comparativo: YOLOv8n, YOLOv11n, YOLOv26n
3. Validación cruzada y ajuste de hiperparámetros
4. Selección del modelo base en desempeño y velocidad

### Tareas Completadas

- ✅ Dataset_1 validado y listo para anotación (3,480 imágenes)
- ✅ Infraestructura backend completa (BD, API, UI)
- ✅ Integración con Arduino y cámara (ELP AR0234) funcional
- ✅ Documentación técnica de Fase 2 completa

### Tareas Pendientes

- ⏳ Anotación de imágenes en herramienta (Roboflow/Label Studio/CVAT)
  - Estrategia: 70% train, 15% val, 15% test
  - Criterio: Bounding boxes alrededor de defectos clave
  - Validación inter-anotador: agreement > 95%

- ⏳ Entrenamiento de modelos candidatos
  - YOLOv8n (baseline)
  - YOLOv11n (mejorado)
  - YOLOv26n (más reciente)
  - Métrica de evaluación: mAP@50, mAP@50-95, precision, recall

- ⏳ Evaluación comparativa
  - Latencia de inferencia
  - Consumo de recursos (GPU/CPU)
  - Desempeño por clase de defecto
  - Robustez ante variaciones (iluminación, ángulo)

### Dependencia Crítica

**Fase 2 → Fase 3 → Fase 4 → Fase 5 → Fase 6**

No avanzar a Fase 3 sin completar Fase 2. Dataset_1 (3,480 imágenes) es el fundamento para todo el ciclo.

---

## Resumen de Objetivos Completados

### Objetivo 1: Identificar características físicas y defectos ✅

**Cumplimiento:**
- ✅ Investigación exhaustiva NTP 209.027:2018 y NTP-ISO 10470:2014
- ✅ Validación con expertos de la cooperativa (gerencia + personal técnico)
- ✅ Identificación de 17 categorías de defectos
- ✅ Dataset propio capturado y etiquetado en cooperativa
- ✅ Características clave documentadas: colorimetría, morfología, textura

### Objetivo 2: Desarrollar sistema de visión artificial ⏳ EN CURSO

**Progreso actual:**
- ✅ Ingeniería de datos completa (Fase 2 CRISP-ML(Q))
- ✅ Backend FastAPI + BD PostgreSQL 18 funcional
- ✅ Interfaz web con Jinja2 y Tailwind CSS
- ✅ Integración Arduino para captura de datos
- ⏳ Modelos ML en preparación para entrenamiento (Fase 3)
- ⏳ Validación de calidad (Fase 4)
- ⏳ Despliegue en producción (Fase 5)

---

## Estadísticas Generales

| Componente | Status | Detalles |
|------------|--------|----------|
| Dataset | ✅ | 3,480 imágenes, 17 clases, 640×640 px |
| Base de Datos | ✅ | PostgreSQL 18, UUIDv7, normalizado |
| API REST | ✅ | 9+ endpoints, autenticación JWT |
| Frontend | ✅ | 5 templates, integración API completa |
| Arduino/Cámara | ✅ | Streaming MJPEG, serial 9600 baud |
| Documentación | ✅ | DOCUMENTACION.md, CLAUDE.md, este archivo |
| Modelos ML | ⏳ | Preparados para anotación y entrenamiento |

---

## Próximos Pasos Críticos

### Corto Plazo (Mayo - Junio)
1. Configurar herramienta de anotación (Roboflow/Label Studio)
2. Crear guía visual para anotadores
3. Iniciar anotación: 70% train, 15% val, 15% test
4. Validación inter-anotador (agreement > 95%)

### Mediano Plazo (Junio - Julio)
1. Entrenamiento: YOLOv8n vs YOLOv11n vs YOLOv26n
2. Evaluación comparativa (mAP, latencia, recursos)
3. Análisis de desempeño por clase
4. Selección de modelo óptimo

### Largo Plazo (Julio - Agosto)
1. **Fase 4:** Garantía de calidad (validación de métricas, robustez)
2. **Fase 5:** Despliegue en producción
3. **Fase 6:** Monitoreo y mantenimiento sostenible

---

## Información de Contacto

**Autor:** Anderson Jhomar Baca Chuquimanco  
**Email:** ander.jbc115@gmail.com  
**Asesor:** Mgtr. William Alfredo Noblecilla Vinces  
**ORCID Asesor:** https://orcid.org/0000-0002-3531-2501  
**Institución:** Universidad Católica Santo Toribio de Mogrovejo  
**Escuela:** Ingeniería de Sistemas y Computación

---

**Fecha de actualización:** 25 de mayo de 2026  
**Versión:** 2.0 (Sprint 1 completado + Sprint 2 iniciado)
