# CoffeeRen — Documentación General del Sistema

> Última actualización: 30 de septiembre de 2026 · Basado en el estado real del código en la rama `temporal`.
> Contexto técnico, pendientes y reentrenamiento: [docs/guia/](guia/README.md).

CoffeeRen es un sistema de visión por computadora para la **clasificación automatizada de granos de café verde y detección de defectos en tiempo real**. Es un proyecto de tesis de la Universidad Católica Santo Toribio de Mogrovejo (USAT), desarrollado en colaboración con la **Cooperativa Agraria Line Coffee Marañón**.

El sistema reemplaza el conteo manual de defectos que hace un evaluador de la cooperativa: los granos pasan por una faja transportadora, una cámara los filma, un modelo YOLO los detecta y clasifica (sano/defecto), un servo los separa físicamente, y el sistema calcula automáticamente el grado del lote, el factor de rendimiento y el **pago al caficultor**.

---

## 1. ¿De qué trata el sistema? (visión general)

```
Caficultor entrega sacos de café
        ↓
[REGISTRO]  Evaluador registra la muestra (pesos, humedad, tamiz, tipo de grano)
        ↓
[MONITOREO] Granos pasan por la faja → cámara ELP → YOLO detecta defecto/verde
            → ByteTrack asigna ID único a cada grano (sin doble conteo)
            → Servo separa físicamente los defectuosos
            → Streaming MJPEG en vivo al navegador
        ↓
[ANÁLISIS]  Al finalizar: código EVA, conteo total, grado SCA, incidencias
            Evaluador ingresa peso bueno → sistema calcula factor de
            rendimiento, categoría, precio y pago
        ↓
[REPORTE]   Búsqueda por código EVA + reportes estadísticos del sistema
```

Componentes:

| Componente | Tecnología |
|---|---|
| Backend web | FastAPI (Python), Jinja2 (server-rendered), TailwindCSS |
| Base de datos | PostgreSQL con psycopg2 directo (sin ORM) |
| Visión artificial | YOLO26n (Ultralytics) + ByteTrack; GPU con PyTorch CUDA (`best.pt`), CPU con ONNX (`best.onnx`) |
| Cámara | ELP AR0234 Global Shutter, USB 2.0, 1920×1080 MJPEG ~90 fps |
| Hardware físico | Arduino: faja transportadora, servo separador, balanza (celda de carga) |
| Autenticación | JWT en cookie httponly + contraseñas Argon2 |

---

## 2. Clasificación de granos — cómo funciona

### 2.1 Detección con YOLO (modelo activo: `yolov26n_2cls`)

El modelo en producción es **binario de 2 clases**:

| Clase | Significado | Color en pantalla |
|---|---|---|
| `defecto` | Grano con cualquier defecto físico | Rojo |
| `verde` | Grano sano (café verde exportable) | Verde |

| `desconocido` | Objeto que el modelo nunca reconoce como grano (materia extraña). Clase derivada por el tracker, no la emite el modelo | Azul |

- Pesos en `src/ml/models/yolov26n_2cls/`: con GPU se carga `best.pt` (PyTorch, FP16 si la compute capability es ≥ 7.0); en CPU `best.onnx`. `best.onnx` está en Git; `best.pt` se descarga de Google Drive.
- El frame 1920×1080 se divide en una grilla de **3×3 recortes con solape de 200 px** que se infieren en un solo lote a `imgsz=640` (el modelo se entrenó con un grano por imagen; sobre el frame completo cada grano quedaba demasiado chico). Las cajas del mismo grano partidas entre recortes vecinos se fusionan.
- Piso de confianza: **0.15** (`CONF_THRESHOLD` en `tracker_service.py`). Es bajo a propósito: el filtrado lo hacen ByteTrack y la resolución de clase por confianza acumulada.
- Filtro de tamaño de bounding box: `GRANO_MIN_PX=50` a `GRANO_MAX_PX=480` píxeles.
- Detección limitada a 30 fps (`ML_DETECTOR_FPS`) y omitida cuando la imagen no cambia (gate de movimiento).
- Problema abierto: el modelo marca como defecto ~40 % de granos sanos en pruebas en vivo (dataset tomado con celular, producción con la ELP). Se mitiga con `MARGEN_DEFECTO`; la solución es el reentrenamiento descrito en [guia/03-reentrenamiento-camara-elp.md](guia/03-reentrenamiento-camara-elp.md).

### 2.2 Tracking con ByteTrack (conteo sin duplicados)

Cada grano recibe un **ID único que persiste entre frames** — así un grano que aparece en 40 frames se cuenta una sola vez.

- **Clase por confianza acumulada**: la clase final de cada grano suma la confianza por clase sobre su historial (últimas 30 detecciones). Para marcarlo defecto, la suma de `defecto` debe superar a la de `verde` por un factor `MARGEN_DEFECTO = 1.3`. Si el track nunca superó confianza 0.35 tras 3 cuadros, es `desconocido`.
- **Objeto desconocido**: se considera materia extraña (piedra, palito, pajilla): el servo lo desvía, suma 1.0 defecto equivalente y se guarda una foto recortada en `src/resources/desconocidos/{evaluacion}/`.
- **IDs globales**: ByteTrack reinicia su contador interno tras pausas sin detecciones; el tracker mantiene un mapeo propio (`_bytetrack_a_global`) que nunca retrocede, de modo que el conteo resiste pausas de la faja.
- Configuración en `src/ml/bytetrack.yaml` (`track_buffer: 10`, `match_thresh: 0.8`).

### 2.3 Modelos anteriores (retirados)

El plan inicial contemplaba un modelo de 17 clases de defecto y luego un modelo cascada (`yolov26n`, 14 subtipos) que clasificaría el tipo de defecto sobre el recorte del grano. El modelo de 17 clases no convergió a tiempo (INC-18) y la cascada se retiró del código en julio de 2026 (commit `787a7ac`). Hoy solo existe el modelo binario.

### 2.4 Separación física

Cuando el tracker confirma un grano defectuoso (al menos 2 detecciones o una con confianza ≥ 0.45), programa el servo (`servo_controller`) para desviarlo de la faja. El servo se agenda desde el **timestamp de captura** del primer cuadro en que se vio el grano, para descontar la latencia de inferencia. Comandos serie al Arduino: `SERVO:DEFECTO`, `SERVO:BUENO`, `ON`, `OFF` (faja), `PESO:` (balanza), `LISTO:`.

### 2.5 Entrenamiento (CRISP-ML(Q))

- Dataset: 3,451 imágenes originales → 8,283 con augmentación 3× en Roboflow (flip H/V, rotación ±15°, brillo ±15%, exposición ±5%, blur 0.5px, ruido 0.1%).
- Split: 88% train / 8% validation / 4% test. Transfer learning desde COCO, en Google Colab (A100).
- Resultados de referencia del primer entrenamiento: YOLOv8n — mAP50: 0.767, mAP50-95: 0.757 (75 épocas). El modelo en producción es YOLO26n de 2 clases (versión v6 del dataset en Roboflow).
- Pendiente: fine-tuning v7 con fotos de la cámara ELP y augmentation HSV (ver [guia/03-reentrenamiento-camara-elp.md](guia/03-reentrenamiento-camara-elp.md)).

---

## 3. Tipos de clasificación que existen en el sistema

El sistema clasifica en **cuatro dimensiones distintas**:

### 3.1 Clasificación por grado SCA (calidad del lote)

Calculada en `src/ml/classifier.py` a partir del conteo del tracker. Cada clase detectada tiene un **peso de equivalencia** (tabla SCA sobre muestra de 350 g). En el modelo binario actual: `defecto = 1` equivalente, `verde = 0` (no es defecto), `desconocido = 1.0` (materia extraña). Con el total de defectos equivalentes se asigna el grado — **solo existen 3 grados**:

| Grado | Defectos equivalentes | ¿Apto Specialty? |
|---|---|---|
| **Grado 1 (Specialty)** | 0 – 15 | Sí |
| **Grado 2** | 16 – 23 | No |
| **Grado 3** | 24 o más | No |

La misma escala existe en la BD como tabla maestra `CATEGORIA` (Grado 1 = 15, Grado 2 = 23, Grado 3 = 30) y se asigna a la evaluación (`categoria_id`) al completarla, según `total_defectos`.

> ⚠️ Las equivalencias deben coincidir con la tabla oficial SCA de Line Coffee Marañón (ver `docs/defectos_sca_tabla_referencia.md`).

### 3.2 Clasificación por rendimiento físico (precio)

Al completar la evaluación, el evaluador pesa el grano bueno y el sistema calcula el **factor de rendimiento** = `peso_bueno / (peso_muestra / 100)`. Ese factor cae en un **rango de precios** (`VALOR_CAFE`, ej. "70-75") registrado por Gerente/Administrador, y ese rango determina el **precio por quintal** para el pago.

### 3.3 Clasificación por tipo de grano

Tabla maestra `TIPO_GRANO` con el peso de referencia por quintal:

| Tipo | Peso por quintal (kg) |
|---|---|
| Pergamino | 55.20 |
| Pilado | 46.00 |
| Coco | 85.00 |

### 3.4 Clasificación por tipo de defecto (catálogo BD)

Tabla `TIPO_DEFECTO` (Broca, Cascarilla, Cereza seca, Concha, Hongo, Flotador, Palos, Piedra, Raja, Partido) usada por `DETALLE_EVALUACION` para desglosar defectos de una evaluación.

---

## 4. Usuarios y roles

### Personal del sistema (tabla `PERSONAL` + `TIPO_PERSONAL`)

| Rol | Uso principal |
|---|---|
| **Evaluador** | Registra muestras, opera el monitoreo, completa evaluaciones |
| **Gerente** | Además gestiona precios de café, cooperativa, usuarios, auditoría y reportes estadísticos |
| **Administrador** | Mismos permisos que Gerente (en el código ambos usan `require_admin_o_gerente`) |

- **Autenticación**: login en `/auth/login` → JWT (`personal_id`, `usuario`, `rol`, `nombre`, `exp` con TTL de 7 días) guardado como cookie httponly `access_token`. Contraseñas con hash Argon2. Toda ruta (excepto login) exige sesión; sin sesión redirige a login.
- **Gestión de usuarios** (`/perfil/usuarios/...`): crear usuario (documento validado por tipo — DNI exactamente 8 dígitos, Pasaporte/Carnet 8–12 alfanuméricos — con la misma regla compartida que usa el registro de caficultores, vía `src/utilities/documento_validador.py`), editar sus datos, y activar/desactivar (`estado`). El administrador cambia la contraseña de un usuario desde la propia edición (`clave_nueva`).
- **Perfil propio** (`/perfil`): datos personales y cambio de contraseña.

### Caficultores (tabla `CAFICULTOR` → referencia a `PERSONA`)

No son usuarios del sistema; son los productores evaluados. Se clasifican por `TIPO_CAFICULTOR`:
- **Socio** — miembro de la cooperativa.
- **Externo** — no socio. Puede convertirse en socio vía `PATCH /caficultor/convertir-socio/{num_documento}`.

Registro de caficultores (`/nuevo-caficultor`): datos de persona (nombre, apellidos, sexo, fecha de nacimiento, documento, teléfono, ubigeo, correo, caserío). Validación de documento: **DNI exactamente 8 dígitos**; Pasaporte/Carnet de Extranjería 8–12 alfanuméricos. Integración con **API RENIEC** (`/dni/consultar/{dni}`) para autocompletar datos por DNI.

---

## 5. Flujo principal: la Evaluación (núcleo de negocio)

Una **evaluación** es el análisis completo de un lote de café de un caficultor. Vive en la tabla `EVALUACION` y pasa por 3 fases con guardas de navegación:

### Fase 1 — Registro (`/registro`)

El evaluador ingresa: documento del caficultor, número de sacos, peso bruto (máximo 70 kg por saco y **mayor que la tara** `round(num_sacos × 0.25)`, desde el 2026-09-30), humedad (**% entero, 1–30** — sin decimales, validada en el formulario y en el schema), peso de muestra, peso trillado, número de tamiz, peso tamizado y tipo de grano. Requisitos validados antes de crear:
- El caficultor debe existir y estar **activo**.
- Debe haber **precios de café registrados** (sin ellos no se puede calcular el pago al finalizar).

La evaluación se crea **sin código** (estado "activa").

### Fase 2 — Monitoreo (`/monitoreo/{evaluacion_id}`)

Pantalla en tiempo real: video MJPEG anotado (defectos en rojo, sanos en verde, objetos desconocidos en azul), conteo en vivo por clase, barra de estado (cámara, faja, Arduino, modelo), bitácora de avisos con marca de tiempo y control de la faja/motor. Endpoints usados: `POST /video/iniciar`, `GET /video/stream`, `GET /video/lote/conteo`, `GET /video/eventos`, `GET /video/status`, `POST /video/detener`, y `/arduino/*` (estado, peso, motor).

Al terminar, `PATCH /evaluacion/{id}/finalizar` genera el **código EVA** (secuencial `EVA0000001`) y guarda `total_defectos`, `total_buenos`, **incidencias** (JSONB) y los **eventos del monitoreo** en la tabla `EVENTO_MONITOREO` (misma transacción). `/analisis` y la búsqueda por código muestran esos eventos. Es **idempotente**: si la llamada se reintenta (timeout de red, doble clic) reutiliza el código ya asignado en vez de generar uno nuevo y dejar huérfano el anterior.

> Guardas: si la evaluación ya tiene código, `/monitoreo/{id}` redirige a `/analisis/{id}` y viceversa; UUID inexistente redirige a `/registro`.

### Fase 3 — Análisis y cálculo de pago (`/analisis/{evaluacion_id}`)

Resumen estadístico del lote. Al **completar** (`PATCH /evaluacion/{id}/completar`) el evaluador ingresa el peso de grano bueno, que no puede superar el peso tamizado, y el sistema deriva (con `Decimal`, redondeos a 2 decimales). El precio se busca con la parte entera del factor: 65.67 corresponde al rango 60-65 y un rango simple 70 comprende de 70.00 a 70.99. El factor guardado conserva sus dos decimales.

| Cálculo | Fórmula |
|---|---|
| Peso cáscara | `peso_muestra − peso_trillado` |
| Factor de rendimiento | `peso_bueno / (peso_muestra / 100)` |
| Peso malo | `peso_trillado − peso_bueno` |
| Tara total | `num_sacos × 0.25` |
| Peso neto | `peso_bruto − tara_total` |
| Castigo por humedad | si humedad > 12%: `peso_neto × exceso / (100 − humedad)` |
| Peso por quintal | `(peso_neto − castigo_humedad) / peso_qq_del_tipo_grano` — redondeo **hacia abajo** (nunca pagar de más) |
| **Pago** | `peso_por_qq × precio_del_rango` |

También asigna la **categoría** (Grado 1/2/3) según `total_defectos` y el **precio** según el rango de `VALOR_CAFE` que contiene el factor de rendimiento.

> La columna `evaluacion.peso_neto` es `numeric(7,2)` (antes era `int4` y Postgres redondeaba el valor calculado al guardarlo, aunque el pago mostrado ya se calculaba correctamente en memoria con el `Decimal` sin redondear). Requiere `ALTER TABLE evaluacion ALTER COLUMN peso_neto TYPE numeric(7,2)` en bases de datos creadas antes de este cambio.

---

## 6. Reportes y análisis

### Búsqueda de muestras (`/reporte`)

Búsqueda de una evaluación por su **código EVA** → devuelve el resumen completo (caficultor, pesos, factor, categoría, pago, incidencias).

Si aún no tiene rendimiento, el botón **Calcular rendimiento** abre `/analisis/{id}` para ingresar el peso de grano bueno de la evaluación finalizada.

### Reportes estadísticos (`GET /reportes` y `GET /reportes/{codigo}`)

Sistema genérico y extensible (`reporte_service.py`): cada reporte declara columnas, filas y tipo de gráfico (ECharts en el frontend, `coffee-report.js`). Catálogo actual:

| Código | Título | Gráfico |
|---|---|---|
| `usuarios` | Usuarios del sistema — distribución de personal activo por rol + caficultores | Pie |
| `caficultores_tipo` | Caficultores por tipo — socios vs. externos | Barras |

Para agregar un reporte solo se crea la consulta en `models/reporte.py`, un builder `_reporte_<nombre>()` y su registro en `self._reportes` — la ruta y el frontend no cambian.

### KPIs de inicio (`/inicio`)

Total de lotes evaluados, total de defectos y rendimiento promedio (`obtener_kpis()`).

### Auditoría (`GET /auditoria`)

Tabla `AUDITORIA`: registra quién hizo qué (usuario, rol, acción, tabla afectada, registro, datos anteriores/nuevos en JSONB, IP y fecha). Filtrable por usuario y acción (`/auditoria/usuarios`, `/auditoria/acciones`).

---

## 7. Otros registros del sistema

| Registro | Página / API | Notas |
|---|---|---|
| **Caficultores** | `/nuevo-caficultor` — listar, consultar por documento, crear, convertir a socio | Validación de documento + RENIEC |
| **Cooperativa** | `/configuracion-cooperativa` — ver y editar la cooperativa propia + subida de imagen | Datos institucionales, ubigeo. Imagen: solo jpg/jpeg/png/webp/gif, máx. 5 MB |
| **Valor del café** | `/valor-cafe` — historial, máximo del día, cambios diarios, resumen por rangos, crear bloque, actualizar precio, eliminar rango | Solo Gerente/Administrador; los rangos determinan el precio del pago (ver reglas de validación abajo) |
| **Tipos de grano** | API `/tipo-grano` — CRUD | Nombre + peso por quintal |
| **Ubigeo** | API `/ubigeo` — departamentos/provincias/distritos del Perú | Tabla precargada completa |
| **Tablas maestras** | `/tipo-caficultor`, `/tipo-documento`, `/tipo-personal` — solo lectura | Sembradas en `script.sql` |

**Reglas de validación de rangos de precio** (`src/services/valor_cafe_service.py`, aplicadas tanto al crear un bloque de precios como al re-cotizar uno individual):
- **Sin solapamiento**: dos rangos no pueden compartir ningún valor de factor de rendimiento, ni siquiera un límite (`60-65` y `65-70` se consideran solapados porque ambos incluyen el 65). Evita que `obtener_por_factor()` tenga que elegir de forma ambigua entre dos precios para el mismo factor.
- **Precio no decreciente por rango**: el precio no puede bajar conforme sube el rango (un lote con mejor rendimiento nunca paga menos que uno con peor rendimiento). Se valida contra la tabla de precios vigente del día, no solo contra el lote que se está enviando.

---

## 8. Páginas del sistema

| URL | Template | Descripción |
|---|---|---|
| `/` (alias `/inicio`) | `inicio.html` | Dashboard con KPIs |
| `/auth/login` | `login.html` | Inicio de sesión |
| `/registro` | `registro.html` | Registro de muestras (fase 1) |
| `/monitoreo/{id}` | `monitoreo.html` | Monitoreo ML en vivo (fase 2) |
| `/analisis/{id}` | `analisis.html` | Resumen y cálculo de pago (fase 3) |
| `/reporte` | `reporte.html` | Búsqueda por código EVA + reportes |
| `/nuevo-caficultor` | `caficultor.html` | Registro/conversión de caficultores |
| `/valor-cafe` | `valor_cafe.html` | Precios del café (Gerente/Admin) |
| `/configuracion-cooperativa` | `cooperativa.html` | Datos de la cooperativa (Gerente/Admin) |
| `/perfil` | `perfil.html` | Perfil y gestión de usuarios |
| `/prueba` | `prueba.html` | Prueba de detección en vivo sin evaluación |

---

## 9. Arquitectura de código

Patrón de **4 capas** — cada feature tiene un archivo en cada capa:

| Capa | Ruta | Responsabilidad |
|---|---|---|
| Routes | `src/routes/` | HTTP puro: endpoints, llama a services, devuelve template o JSON |
| Services | `src/services/` | Lógica de negocio, orquesta models, es dueña del commit/rollback |
| Models | `src/models/` | SQL crudo parametrizado (psycopg2), acepta `db` opcional para transacción compartida |
| Schemas | `src/schemas/` | Validación Pydantic de request/response |

- **BD**: clase `Connection` (`src/database/bd.py`), una conexión por request, `autocommit=False`, `RealDictCursor`. Métodos: `obtener()`, `obtener_uno()`, `ejecutar()`, `commit()`, `rollback()`. Esquema en `src/database/script.sql`.
- **Transacciones multi-tabla**: el service crea una `Connection`, la pasa a cada model, y hace `commit()`/`rollback()` al final, siempre con `try…finally: db.close()`.
- **ML**: `camara_service` (captura) → `tracker_service` (hilo de procesamiento) → `CoffeeRenTracker` (YOLO+ByteTrack) → `classifier.py` (grado SCA). El modelo se carga **una sola vez** al arranque con warmup; el tracking corre en hilo aparte y las rutas solo hacen polling no bloqueante.
- **Ciclo de vida** (`main.py` lifespan): al arrancar pre-conecta la cámara; al apagar detiene tracker, apaga la faja (`OFF`), cierra cámara, servo y serial.
- **Restricciones calibradas físicamente** (no tocar sin permiso): `servo_controller.py`, `arduino_serial.py`, `SERVO_DELAY_S=0.3`, `SERVO_HOLD_S=0.3`, `imgsz=640`, `half` solo condicional por hardware, `track_buffer: 10`, modo emergencia `_on_camara_desconectada()`.

### Tablas de la base de datos

`PERSONA` (datos personales) · `PERSONAL` (usuarios del sistema) · `TIPO_PERSONAL` (roles) · `CAFICULTOR` · `TIPO_CAFICULTOR` · `COOPERATIVA` · `UBIGEO` · `EVALUACION` (lote evaluado con todos los pesos y el pago) · `DETALLE_EVALUACION` · `TIPO_DEFECTO` · `TIPO_GRANO` · `TIPO_DOCUMENTO` · `CATEGORIA` (grados) · `VALOR_CAFE` (precios por rango) · `AUDITORIA` · `EVENTO_MONITOREO` (bitácora del monitoreo por evaluación).

---

## 10. Ejecución en desarrollo

```bash
python -m venv .venv
source .venv/Scripts/activate   # Windows (Git Bash)
pip install -r requirements.txt
uvicorn src.main:app --reload   # → http://localhost:8000

# TailwindCSS en modo watch
./tailwindcss-windows-x64.exe -i src/static/css/input.css -o src/static/css/tailwind.css --watch
```

No existe suite de tests (solo `tests/verificacion_incremento_1.py`). `best.onnx` viene en el repositorio; `best.pt` se descarga de Google Drive a `src/ml/models/yolov26n_2cls/`.

## Documentación relacionada

- `docs/guia/` — guía de contexto: módulo ML, reentrenamiento con la ELP, pendientes, historial
- `docs/API_VIDEO_STREAMING.md` — detalle de la API de video
- `docs/hardware-camara.md` — cámara ELP y calibración
- `docs/defectos_sca_tabla_referencia.md` — tabla de equivalencias SCA (pendiente de validación oficial)
- `docs/documentacion/` — documentos de tesis (referencia histórica: describen el plan de mayo-junio)
- `docs/manuales/Manual_Usuario_CoffeeRen.docx` — único manual de entrega, mantenido directamente en Word
- `AGENTS.md` — reglas de desarrollo para cualquier asistente de IA (`CLAUDE.md` y `GEMINI.md` lo importan)
