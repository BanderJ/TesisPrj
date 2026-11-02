# Instrucciones para asistentes de IA — CoffeeRen

Este archivo es la **fuente única de instrucciones** para cualquier asistente de IA que trabaje en
este repositorio: Claude, ChatGPT/Codex, Gemini, GitHub Copilot u otro. Los archivos propios de
cada herramienta (`CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md`) solo remiten aquí.
Si cambias una regla, cámbiala **en este archivo**.

Léelo completo antes de hacer cualquier cambio.

---

## 1. Qué es el proyecto

CoffeeRen es un sistema de tesis (USAT, Perú) para la Cooperativa Agraria Line Coffee Marañón.
Clasifica granos de café verde en tiempo real:

1. Los granos pasan por una faja transportadora (Arduino).
2. Una cámara ELP AR0234 los filma.
3. Un modelo YOLO detecta cada grano y lo clasifica como `verde` (sano) o `defecto`.
4. ByteTrack le da un ID único a cada grano para no contarlo dos veces.
5. Un servo desvía los granos defectuosos.
6. El sistema cuenta los defectos equivalentes del lote y calcula el pago al caficultor.

Aplicación web: FastAPI + plantillas Jinja2 + PostgreSQL 18. Un solo desarrollador, en Windows 11.

## 2. Qué leer antes de empezar

| Si vas a… | Lee primero |
|---|---|
| Entender el proyecto | `docs/guia/README.md` y `docs/guia/01-contexto-del-proyecto.md` |
| Tocar el módulo de visión (`src/ml/`, `tracker_service.py`, `camara_service.py`) | `docs/guia/02-modulo-ml.md` y `docs/hardware-camara.md` |
| Reentrenar el modelo | `docs/guia/03-reentrenamiento-camara-elp.md` |
| Saber qué falta hacer | `docs/guia/04-pendientes.md` |
| Saber qué cambió y cuándo | `docs/guia/05-historial-de-cambios.md` |
| Escribir código backend | Sección 5 de este archivo y `.claude/skills/fastapi-architecture/SKILL.md` |
| Escribir HTML, CSS o JS | `.claude/skills/frontend-coffeeren/SKILL.md` |
| Redactar documentación o informes | `.claude/skills/documentacion-informes/SKILL.md` |

Los archivos `SKILL.md` de `.claude/skills/` son Markdown normal: cualquier IA puede leerlos
como guía, aunque la carpeta tenga el nombre de Claude.

`docs/documentacion/` es material académico de la etapa de planificación. **No describe el
código actual**: no lo uses como fuente técnica.

## 3. Cómo trabajar con el usuario

- **Idioma:** responder en español. El usuario escribe informal y con faltas de ortografía; eso
  no cambia lo que pide.
- **No inventar reglas de negocio ni umbrales.** Si una tarea necesita un valor que el usuario
  no dio (límites de peso, umbrales de confianza, equivalencias de defectos, rangos), pregunta
  antes, con opciones concretas. No "mejores" validaciones que nadie pidió.
- **Si la solicitud es ambigua:** no escribas código todavía. Explica en pocas líneas lo que
  entendiste, propone 2 o 3 opciones con una recomendación, haz como máximo 3 preguntas y
  espera la respuesta.
- **Si la solicitud es clara:** impleméntala directamente, con cambios mínimos y sin
  sobreingeniería.
- **Estilo de salida:** sin emojis ni adornos, tono técnico y sobrio, sin frases que delaten
  texto generado por IA. Aplica a respuestas, código, comentarios y documentación.
- **Calidad sobre cantidad:** nada de código duplicado ("espagueti"). Antes de crear algo,
  busca si ya existe y reutilízalo o parametrízalo.
- **Sin archivos inútiles:** no crees documentos nuevos si ya existe uno sobre el tema;
  actualiza el existente. Borra lo que quede superado.
- No hagas commit ni push salvo que el usuario lo pida.

## 4. Comandos

```bash
python -m venv .venv
source .venv/Scripts/activate            # Windows (Git Bash); en PowerShell: .venv\Scripts\activate
pip install -r requirements.txt          # torch debe quedar en variante CUDA (+cu130), ver requirements.txt
cp src/config-example.py src/config.py   # y poner la contraseña real de PostgreSQL
uvicorn src.main:app --reload            # http://localhost:8000
./tailwindcss-windows-x64.exe -i src/static/css/input.css -o src/static/css/tailwind.css --watch
```

No hay suite de tests unitarios. Hay tres verificaciones: `tests/verificacion_incremento_1.py`, las
pruebas de caja negra de `tests/caja_negra/` (Playwright + pytest, casos PCN-XX de la tesis):
`python -m pytest tests/caja_negra` con la app corriendo, la cámara conectada (la precondición
abre y cierra un monitoreo para que el servidor tenga el conteo del lote) y precios de café con
fecha de hoy, y
`python -m tests.caja_negra.generar_fichas` para el Word de fichas. Crean usuarios y evaluaciones
de prueba: solo contra la base de desarrollo. Las pruebas de caja blanca de `tests/caja_blanca/`
(casos PCB-XX, pytest + pytest-cov) no usan BD ni hardware: `python -m tests.caja_blanca.ejecutar`
corre cada caso con cobertura de ramas y guarda la evidencia, y `python -m tests.caja_blanca.generar_fichas`
arma el Word. Los helpers comunes de las fichas están en `tests/fichas_word.py`. Verifica a mano que la app arranque, que el flujo
registro → monitoreo → análisis funcione y, para cambios de Python, `python -m py_compile <archivo>`.

## 5. Reglas del código

### 5.1 Cuatro capas (obligatorio)

Cada funcionalidad tiene un archivo en cada capa. No mezcles responsabilidades.

| Capa | Carpeta | Puede | No puede |
|---|---|---|---|
| Routes | `src/routes/` | Recibir HTTP, llamar a services, devolver plantilla o JSON | Lógica de negocio, SQL |
| Services | `src/services/` | Lógica de negocio, orquestar models, hacer `commit`/`rollback` | SQL |
| Models | `src/models/` | SQL crudo con psycopg2 | Lógica |
| Schemas | `src/schemas/` | Toda la validación con Pydantic | — |

Otras carpetas: `src/apis/` (cliente externo RENIEC/Factiliza), `src/utilities/` (JWT, UUIDv7,
serie Arduino, servo, validador de documentos, eventos, latencia), `src/ml/` (visión).

### 5.2 Reglas que no se negocian

- Type hints en toda función, sintaxis moderna: `list[dict]`, `str | None`.
- SQL siempre parametrizado: `db.obtener("SELECT ... WHERE id=%s", [id])`. Nunca f-strings en SQL.
- Si abres una conexión a mano: `try ... finally: db.close()`.
- Una función parametrizada en lugar de varias casi iguales.
- Nombres de archivos subidos con `uuid7()` de `src/utilities/uuid_utils.py`, nunca `uuid4()`.
- Los campos `NOT NULL` de la base de datos son obligatorios en el schema Pydantic, y los
  `max_length` coinciden con el `varchar(N)` de `src/database/script.sql`.

### 5.3 Base de datos

PostgreSQL 18, base `tesis_prj` (usa `uuidv7()` nativo). Sin ORM. La clase `Connection` de
`src/database/bd.py` tiene `obtener()`, `obtener_uno()`, `ejecutar()`, `commit()`, `rollback()`,
`close()`. Para escribir en varias tablas a la vez, el service crea **una** conexión, se la pasa
a cada model (`db: Connection = None`) y al final hace `commit()` o `rollback()`.

### 5.4 Configuración

`src/config.py` **no está en Git** (tiene la contraseña real). En Git está
`src/config-example.py`, una plantilla. **Todo cambio en `src/config.py` se copia en
`src/config-example.py` en el mismo momento**, con los secretos reemplazados por un texto de
ejemplo. Los dos archivos deben tener los mismos atributos en la clase `Config`. Las variables
de `.env` tienen prioridad sobre los valores por defecto. `SECRET_KEY` no tiene valor por
defecto: va en `.env` y la app no arranca si falta, si mide menos de 32 caracteres o si es un
texto de ejemplo (`validar_clave_secreta` en `src/utilities/jwt_utils.py`).

### 5.5 Autenticación y permisos

- JWT en cookie httponly `access_token` ("Bearer ..."), contraseñas con Argon2, sesión de 7 días.
- Toda ruta, salvo `/auth/login`, depende como mínimo de `obtener_usuario_actual`
  (`src/utilities/jwt_required.py`).
- Roles: 1 Evaluador, 2 Gerente, 3 Administrador. Lo restringido a Gerente o Administrador usa
  `Depends(require_admin_o_gerente)`. Ocultar un enlace en el menú **no** es control de acceso.

### 5.6 Frontend

Plantillas en `src/templates/` que extienden `main.html`. El JavaScript va en archivos de
`src/static/js/`, cargados con `{% block script %}`; solo las variables de Jinja2 van inline.
CSS propio por página en `src/static/css/`. Formularios con 2 campos por fila y validación en
vivo. Errores del backend con `CoffeeHttp.mensajeError()` (`http.js`). Detalle en
`.claude/skills/frontend-coffeeren/SKILL.md`.

## 6. Módulo de visión: lo esencial

El detalle completo está en `docs/guia/02-modulo-ml.md`. Lo mínimo:

- **Un solo modelo:** `yolov26n_2cls` en `src/ml/models/yolov26n_2cls/` (`best.pt`, `best.onnx`,
  `constants.py`). Clases `defecto` y `verde`; el tracker agrega `desconocido` (materia extraña).
- **No existen** y no deben volver a documentarse como si existieran: el modelo de 17 clases,
  el modelo cascada de 14 clases, `USE_MODELO_DEFECTOS`, `inference.py`.
- **GPU → `best.pt`; CPU → `best.onnx`.** FP16 solo en GPUs con compute capability ≥ 7.0.
  `best.onnx` está en Git; `best.pt` no (se descarga de Google Drive).
- El modelo se carga **una sola vez** al arrancar. Las rutas solo leen el último resultado; nunca
  bloquean ni recargan el modelo.
- El módulo ML no escribe al puerto serie, al disco ni a la base de datos: eso lo hacen los
  services y `src/utilities/`.
- Problema conocido: el modelo marca como defecto ~40 % de granos sanos porque se entrenó con
  fotos de celular y en producción se usa la cámara ELP. La solución planificada es el
  reentrenamiento de `docs/guia/03-reentrenamiento-camara-elp.md`.

### Prohibido cambiar sin permiso explícito del usuario

- `src/utilities/servo_controller.py` y `src/utilities/arduino_serial.py`.
- `SERVO_DELAY_S = 0.3` (en `.env`, motor JGY370) y `SERVO_HOLD_S = 0.3` (calibrados en el hardware).
- `TrackerService._on_camara_desconectada()` (modo de emergencia).
- `imgsz=640` y la estructura de hilos (cámara productora, tracker consumidor).
- `half`: solo condicional por hardware; nunca forzar FP16 (rompe la GTX 1050 Mobile).
- `track_buffer: 10` en `src/ml/bytetrack.yaml`.
- Protocolo con Arduino: `ON`, `OFF`, `SERVO:DEFECTO`, `SERVO:BUENO`, `PESO:`, `LISTO:`.
- Parámetros de exportación ONNX: `imgsz=640, half=False, dynamic=False, simplify=True`.
- Orden de clases del modelo: `["defecto", "verde"]`.
- Umbrales y equivalencias (`UMBRAL_CONF_CONOCIDO`, `MARGEN_DEFECTO`, `EQUIVALENCIAS_DEFECTO`).

## 7. Reglas de negocio vigentes

- Documento: DNI exactamente 8 dígitos; Pasaporte o Carnet de Extranjería 8 a 12 caracteres
  alfanuméricos (`src/utilities/documento_validador.py`).
- Peso bruto: como máximo `num_sacos × 70` kg y mayor que la tara `num_sacos × 0.25` kg. La tara
  no se redondea nunca (2 sacos = 0.50 kg): se resta tal cual del peso bruto. El peso por saco
  está en `TARA_POR_SACO_KG` (`src/schemas/evaluacion.py`).
- Humedad: número entero de 1 a 30; más de 12 % aplica descuento:
  `peso_neto × (H − 12) / (100 − H)`. Se divide entre `100 − H` (no `100 − 12`) a propósito:
  regla confirmada por el responsable el 2026-11-02.
- Conteo del lote: al finalizar, el servidor guarda el conteo de su tracker
  (`tracker_service.conteo_de_evaluacion`); el navegador no lo envía. Si el lote en memoria no
  es el de esa evaluación, la finalización se rechaza.
- Código EVA: correlativo de la secuencia `evaluacion_codigo_seq`, único (`UNIQUE`).
- Rangos de precio del café: no se pueden solapar y el precio no puede bajar cuando sube el rango.
- Precios del día: una muestra solo se registra si hay precios de café con fecha de hoy, y el pago
  usa el precio de hoy del rango que contiene el factor de rendimiento. Los rangos son enteros y
  el rango se busca con la parte entera del factor, sin redondear (65.52 cae en 60-65 porque no
  llega a 66); el factor guardado conserva sus decimales. Si ese rango no tiene precio hoy,
  completar la evaluación falla hasta que se registre.
- Grado SCA: **no se calcula ni se muestra.** Depende del tipo de defecto (primario/secundario) y
  el modelo actual solo distingue `defecto`/`verde`. `EVALUACION.categoria_id` queda en NULL; la
  tabla `CATEGORIA` se conserva para cuando el modelo clasifique por tipo de defecto.
- Caficultor Socio o Externo; conversión con `PATCH /caficultor/convertir-socio/{num_documento}`.
- Beneficio de socio: monto fijo por entrega (inicial S/ 10) que se suma al pago de un socio. Lo
  cambian Gerente y Administrador en Cooperativa → Beneficio de socio (`POST /bono-socio`). La
  tabla `BONO_SOCIO` es de solo inserción (el vigente es el más reciente) y cada evaluación guarda
  el monto aplicado en `EVALUACION.bono_socio`; `pago` es el total. Un cambio nunca altera
  evaluaciones ya completadas. Se decide con el tipo de caficultor registrado en la evaluación.

## 8. Documentación: dónde va cada cosa

| Qué | Dónde |
|---|---|
| Estado del sistema, pendientes, historial | `docs/guia/` |
| Bitácora de avances por fecha | `docs/registro-avances.md` |
| Incidencias formales (leerlo entero antes de editarlo) | `docs/incidencias/incidencia_proyecto.md` |
| API de video | `docs/API_VIDEO_STREAMING.md` |
| Cámara | `docs/hardware-camara.md` |
| Único manual de entrega: usuario (solo Word, sin fuente Markdown ni conversión) | `docs/manuales/Manual_Usuario_CoffeeRen.docx` |
| Evidencias de indicadores de tesis | `docs/evidencias/` |

Al terminar un cambio relevante: agrega una línea a `docs/guia/05-historial-de-cambios.md`,
marca el ítem en `docs/guia/04-pendientes.md` y, si cambió un parámetro del ML, actualiza la
tabla de `docs/guia/02-modulo-ml.md`.

## 9. Lista de control antes de dar por terminado

Si tocaste `src/routes`, `src/services`, `src/models`, `src/schemas`, `src/apis`, `src/ml`,
`src/templates` o `src/static`, revisa tu cambio contra la lista de
`.claude/agents/architecture-compliance-auditor.md` (Claude lo hace con un subagente; otras
IA, leyendo esa lista). Como mínimo:

- [ ] Cada capa hace solo lo suyo (sección 5.1).
- [ ] Type hints, SQL parametrizado, conexiones cerradas.
- [ ] Nada duplicado: se reutilizó lo existente.
- [ ] No se tocó nada de la lista de prohibidos (sección 6).
- [ ] Si cambió `src/config.py`, también cambió `src/config-example.py`.
- [ ] No se inventó ningún umbral ni regla de negocio.
- [ ] La documentación afectada quedó actualizada (sección 8).
- [ ] La respuesta final está en español, sin emojis, y dice con claridad qué se verificó y qué no.
