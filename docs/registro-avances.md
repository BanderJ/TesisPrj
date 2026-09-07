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

## 2026-09-04 - Inventario inicial de archivos potencialmente redundantes

### Contexto
Se inicio una auditoria minuciosa para identificar archivos sin uso, duplicados,
legado o generados. El objetivo de esta etapa es documentar evidencia y riesgos;
no se autoriza ni se realiza ninguna eliminacion en este bloque.

### Trabajo realizado
- Se reviso el inventario del repositorio incluyendo archivos rastreados por Git,
  no rastreados e ignorados, con exclusion funcional del entorno `.venv/`.
- Se identificaron 88 archivos Python rastreados, 13 templates HTML, 14 archivos
  JavaScript, 14 hojas CSS, 29 documentos Markdown, 6 documentos Word rastreados
  (tres aparecen eliminados en el estado actual del worktree), 2 sketches Arduino,
  1 SQL, 1 CSV, 1 YAML, 1 ONNX, 1 XLSX, 2 TXT y 1 script PowerShell.
- El analisis de archivos Python del workspace no reporto imports sin resolver.
- Se trazo el arranque desde `src/main.py`: los routers, servicios principales,
  utilidades, templates y recursos enlazados por las vistas forman parte del
  sistema activo y no deben marcarse como innecesarios por ausencia de referencias
  textuales simples.
- Se confirmo que `/test` esta conectado a `src/main.py`, `test.html`, `test.js`
  y `test.css`; es una vista de diagnostico autenticada y no un archivo huerfano.
- Se verificaron referencias del sketch `arduino/test_motor/test_motor.ino` en
  `readme.md` y `Manual_Instalacion_CoffeeRen.md`; es soporte de banco valido.

### Archivos impactados
- `docs/registro-avances.md`
- `src/main.py`
- `src/templates/test.html`
- `src/static/js/test.js`
- `src/static/css/test.css`
- `arduino/test_motor/test_motor.ino`
- `detectar_camaras.py`
- `scripts/detectar_camaras.py`
- `check_model.py`
- `generar_manual.py`
- `generar_manual_completo.py`
- `convert_md_to_docx.py`
- `scripts/generar_doc_video.py`
- `src/config-example.py`
- `src/database/inserts_valor_cafe.txt`
- `docs/API_VIDEO_STREAMING.md`
- archivos ignorados `.pyc`, `.env`, `best.pt` y `tailwindcss-windows-x64.exe`
- eliminaciones preexistentes observadas en Git: tres manuales `.docx`; no fueron
  restauradas ni modificadas durante esta auditoria

### Hallazgos preliminares

| Archivo o grupo | Evidencia observada | Clasificacion provisional | Riesgo |
|---|---|---|---|
| `detectar_camaras.py` en la raiz | No aparece citado por la documentacion; existe una segunda version en `scripts/detectar_camaras.py` y esta ultima es la citada por `docs/hardware-camara.md`. | Posible duplicado o legado | Medio: comparar comportamiento y confirmar cual se conserva. |
| `check_model.py` | No tiene referencias; apunta a `src/ml/models/yolov8n/best.pt`, peso que no aparece en el inventario actual. | Herramienta diagnostica posiblemente obsoleta | Medio: podria conservarse para diagnostico historico o actualizarse. |
| `generar_manual.py` y `generar_manual_completo.py` | Ambos generan manuales Word y no son llamados por la aplicacion. El segundo es una version mucho mas extensa. | Herramientas de generacion; posible solapamiento | Medio: revisar cual es fuente vigente antes de consolidar. |
| `convert_md_to_docx.py` | Convierte `Manual_Instalacion_CoffeeRen.md` a `.docx`; no participa en runtime. | Soporte valido de publicacion | Bajo: conservar si se mantiene el flujo Markdown a Word. |
| `scripts/generar_doc_video.py` | Genera documentacion Word del subsistema de video/Arduino y no participa en runtime. | Soporte documental no automatico | Bajo/medio: verificar si el documento de salida existe y si se requiere regenerarlo. |
| `src/config-example.py` | Es referenciado por el manual de instalacion, pero contiene valores historicos distintos a `src/config.py`. | Plantilla de configuracion desactualizada | Medio: actualizar o retirar despues de confirmar el procedimiento de instalacion. |
| `docs/API_VIDEO_STREAMING.md` | Conserva referencias a `yolov8n`, `best.pt` y resolucion 1280x720/60, mientras el estado actual documenta `yolov26n_2cls`, ONNX y 1920x1080/90. | Documentacion relevante pero desactualizada | Medio: no eliminar; corregir en una tarea documental separada. |
| `src/templates/test.html` y sus recursos | Ruta `/test` y referencias desde `main.html`; la vista reutiliza endpoints `/video/*`. | Activo de diagnostico | Alto: no eliminar sin decidir retirar la vista de pruebas. |
| `arduino/test_motor/test_motor.ino` | Referenciado por README y manual de instalacion; prueba aislada de hardware. | Soporte valido | Bajo: no eliminar. |
| `src/database/inserts_valor_cafe.txt` | Archivo de 314 lineas para datos SQL; no se encontro referencia automatica. | Soporte de carga manual, uso no confirmado | Medio: revisar contenido y relacion con `src/database/script.sql`. |
| `.pyc`, `.env`, `best.pt`, ejecutable Tailwind | Archivos ignorados o locales, generados/operativos y fuera del conjunto versionado. | Artefactos locales | Bajo para el codigo; no deben mezclarse con candidatos funcionales. |

### Validacion
- Estado: parcial
- Evidencia: `git ls-files`, `git status --short --ignored`, listado del
  workspace de Pylance, analisis de imports, busquedas de referencias en
  templates, documentos y codigo, y revision manual de los candidatos.
- No se modifico ni elimino ningun archivo funcional.
- La ausencia de referencias no se considero suficiente para declarar un archivo
  innecesario.

### Pendientes
- Completar el grafo de llamadas de todos los services, models, schemas y
  utilidades, incluyendo imports dinamicos y dependencias de base de datos.
- Comparar semanticamente las dos versiones de `detectar_camaras.py`.
- Revisar el contenido completo y la procedencia de cada generador de documentos,
  sus salidas Word y los documentos historicos en `docs/documentacion/`.
- Determinar si `check_model.py`, `src/config-example.py` e
  `src/database/inserts_valor_cafe.txt` siguen siendo necesarios para operacion,
  instalacion o recuperacion.
- Actualizar las referencias obsoletas de `docs/API_VIDEO_STREAMING.md` despues de
  cerrar el inventario, sin borrar evidencia historica.
- Presentar una lista final separada en conservar, consolidar, archivar y revisar
  con el usuario antes de cualquier eliminacion.

### Proximo paso
Completar la verificacion de cada candidato y preparar una matriz final de
decisiones con confianza, impacto funcional y procedimiento seguro de retiro.

## 2026-09-06 - Correcciones aplicadas tras la auditoria

### Contexto
Se verifico cada hallazgo del inventario del 2026-09-04 contra el codigo real.
Todos resultaron ciertos. Con las decisiones del usuario se aplicaron las
correcciones de duplicados y referencias obsoletas. No se cambio logica de
runtime, hardware ni ML.

### Trabajo realizado
- `detectar_camaras.py` (raiz): eliminado. Era version legada y sin referencias;
  la vigente es `scripts/detectar_camaras.py` (mide FPS real, detecta la ELP,
  citada por `docs/hardware-camara.md`).
- `generar_manual.py`: eliminado. Borrador corto superado por
  `generar_manual_completo.py`, que se conserva como unico generador del Manual
  de Usuario (no existe fuente `.md` para ese manual).
- `check_model.py`: reescrito. Apuntaba a `src/ml/models/yolov8n/best.pt`
  (carpeta inexistente). Ahora resuelve `yolov26n_2cls` con preferencia
  `best.onnx` sobre `best.pt`, igual que `src/ml/tracker.py`, y acepta el nombre
  del modelo como argumento.
- `src/config-example.py`: regenerado como plantilla fiel de `src/config.py`
  (estructura completa: DB, Arduino, servo, camara) con `PASSWORD` como
  placeholder y encabezado que explica su uso.
- `docs/API_VIDEO_STREAMING.md`: actualizado al estado real. Rutas con prefijo
  `/video`, modelo `yolov26n_2cls` (2 clases, ONNX), resolucion 1920x1080 a
  90 fps, tabla SCA de 3 grados, cuerpos de respuesta reales, endpoints
  `GET /video/frame` y `POST /video/liberar-camara` documentados, patron de
  consumo vanilla JS y sin emojis.
- Manuales `.docx` (Instalacion, Mantenimiento, Usuario): se confirma la
  eliminacion ya presente en el worktree. Se conservan los `.md` como fuente;
  los `.docx` se regeneran cuando se necesiten para entrega.
- `INSTALACION.md`: corregidas referencias obsoletas del mismo tipo (no estaba en
  el inventario original pero comparte el defecto). Nombre de BD `cofferen` ->
  `tesis_prj` (el correcto segun `src/config.py` y el manual completo); bloque
  `.env` reescrito (no existe `.env.example` ni se usa `DATABASE_URL`); se quito
  `from src.database.bd import init_db` (funcion inexistente); arbol de `src/`
  actualizado (`arduino.py` -> `arduino_serial.py` + `servo_controller.py`,
  `img/` -> `icon/`, `.pt` -> `best.onnx / best.pt`).

### Archivos impactados
- eliminados: `detectar_camaras.py`, `generar_manual.py`
- eliminados (confirmacion): `Manual_Instalacion_CoffeeRen.docx`,
  `Manual_Mantenimiento_CoffeeRen.docx`, `Manual_Usuario_CoffeeRen_Completo.docx`
- reescritos: `check_model.py`, `src/config-example.py`,
  `docs/API_VIDEO_STREAMING.md`
- corregido: `INSTALACION.md`
- limpiado: `.claude/settings.local.json` (entrada de permiso del script eliminado)
- este registro

### Validacion
- Estado: hecho para los items anteriores; parcial para el inventario global.
- Evidencia: `grep` de referencias antes de cada eliminacion (sin usos en codigo,
  solo menciones en este registro y una entrada de permiso en
  `.claude/settings.local.json`); contraste de `docs/API_VIDEO_STREAMING.md`
  contra `src/routes/video.py`, `src/services/tracker_service.py`,
  `src/ml/tracker.py` y `src/ml/classifier.py`; `src/config-example.py`
  comparado linea a linea con `src/config.py`.
- No se modifico `servo_controller.py`, `arduino_serial.py`, la estructura de
  hilos ni parametros de exportacion ONNX.

### Pendientes
- `generar_manual_completo.py` (1748 lineas de python-docx hardcodeado): evaluar
  migrar el Manual de Usuario a un `Manual_Usuario_CoffeeRen.md` y generar el
  `.docx` con `convert_md_to_docx.py`, para tener un unico flujo md -> docx.
- `convert_md_to_docx.py`: hoy fija `Manual_Instalacion_CoffeeRen.md`; podria
  aceptar el nombre del archivo o recorrer todos los `Manual_*.md`.
- `INSTALACION.md` vs `Manual_Instalacion_CoffeeRen.md`: son dos guias de
  instalacion. La corta quedo saneada, pero decidir si se mantiene como
  quick-start o se elimina dejando solo el manual completo (readme apunta a
  ambas).
- `src/database/inserts_valor_cafe.txt`: datos semilla de prueba para
  `valor_cafe`; decidir si se referencia desde `script.sql` o se documenta.
- `.claude/settings.local.json` tiene mas entradas de permiso muertas
  (`crear_preinforme_actualizado.py`, `src/ml/constants.py`, `src/ml/inference.py`).

### Proximo paso
Cerrar la decision sobre los generadores de manual y consolidar el flujo
md -> docx.

## 2026-09-06 - Separacion config.py / config-example.py

### Contexto
Decision del usuario: `src/config.py` deja de publicarse (contiene la contrasena
real de PostgreSQL y ajustes propios). Se publica solo `src/config-example.py`
como plantilla; al instalar se copia a `src/config.py`.

### Trabajo realizado
- `.gitignore`: agregada la regla `src/config.py` (antes estaba comentada).
- `git rm --cached src/config.py`: deja de rastrearse. El archivo sigue en disco
  y la app arranca igual; en el proximo commit se retira del repositorio.
- `src/config-example.py`: ya tenia paridad completa de atributos con
  `src/config.py` (verificado). Encabezado ajustado para indicar que es la
  plantilla a copiar.
- `CLAUDE.md` (seccion Database): documentada la regla — todo cambio estructural
  en `src/config.py` debe replicarse en `src/config-example.py` con los secretos
  como placeholder; ambos deben tener los mismos atributos de `Config`.
- Hook `PostToolUse` (Write/Edit) en `.claude/settings.json` +
  `.claude/hooks/config_example_reminder.py`: al editar `src/config.py` recuerda
  espejar el cambio en la plantilla. Probado (pipe-test + disparo real).
- `Manual_Instalacion_CoffeeRen.md` e `INSTALACION.md`: el Paso 1 ahora indica
  copiar `config-example.py` a `config.py` antes de editar credenciales.

### Archivos impactados
- `.gitignore`, `src/config.py` (untrack), `src/config-example.py`, `CLAUDE.md`
- `.claude/settings.json`, `.claude/hooks/config_example_reminder.py` (nuevo)
- `Manual_Instalacion_CoffeeRen.md`, `INSTALACION.md`, este registro

### Validacion
- Estado: hecho.
- Evidencia: `git check-ignore src/config.py` confirma el ignore;
  `from src.config import Config` sigue funcionando; comparacion de atributos
  `Config` entre ambos archivos = identicos; hook disparado en edicion real de
  `src/config.py` (system-reminder de additionalContext).

### Limpieza aplicada (2026-09-06, continuacion)
- `.claude/settings.json`: eliminada la regla de permiso que contenia
  `$env:PGPASSWORD = 'And1150'` (query psql puntual de introspeccion, sin valor
  para conservar). El working tree ya no tiene la contrasena en `.claude/`.
- `.claude/settings.local.json`: agregado a `.gitignore` y `git rm --cached`
  (ajustes personales de permisos; no debe compartirse). El archivo sigue local.
  Nota: su unica referencia a "password" era el literal `clave=password` en un
  curl de prueba, no la contrasena real.
- `.claude/hooks/config_example_reminder.py`: agregado al indice (`git add`) para
  que el hook viaje en el commit.

### Pendientes
- La contrasena `And1150` sigue en el HISTORIAL de Git (`src/config.py` y
  `.claude/settings.json` en commits anteriores). Retirarla requiere reescribir
  historia (git filter-repo / BFG) y force-push; disruptivo con ramas y remoto
  compartido — decidir por separado.
- Rotar la contrasena de PostgreSQL despues de esa limpieza (o ya, si el repo es
  privado y se asume el historial como comprometido internamente).

### Proximo paso
Decidir si se reescribe el historial + se rota la contrasena, o si basta con que
el repositorio permanezca privado y no se publiquen nuevos cambios de credenciales.
