# 01 — Contexto del proyecto

> Resumen orientado a quien llega sin contexto. El detalle funcional completo (fórmulas de
> pago, reglas de precios, reportes) está en [docs/DOCUMENTACION_SISTEMA.md](../DOCUMENTACION_SISTEMA.md).

## 1. Qué es CoffeeRen

Sistema de tesis de la **Universidad Católica Santo Toribio de Mogrovejo (USAT)**, autor
Anderson Jhomar Baca Chuquimanco, desarrollado con la **Cooperativa Agraria Line Coffee
Marañón** (Lonya Grande, Utcubamba, Amazonas, Perú).

Título de tesis: *Sistema automático de clasificación de granos de café verde mediante visión
artificial en una cooperativa de Amazonas*.

**Problema que resuelve.** Cuando un caficultor entrega su café, un evaluador de la cooperativa
toma una muestra, cuenta a mano los granos defectuosos y con eso (más pesos y humedad) se fija
la calidad y el pago. El conteo manual es lento y subjetivo. CoffeeRen lo automatiza:

1. Los granos de la muestra pasan por una **faja transportadora** (Arduino).
2. Una **cámara industrial ELP AR0234** los filma desde arriba.
3. Un modelo **YOLO** detecta cada grano y lo clasifica como `verde` (sano) o `defecto`.
4. **ByteTrack** asigna un ID único a cada grano para no contarlo dos veces.
5. Un **servo** desvía físicamente los granos defectuosos a otro canal.
6. El sistema cuenta los **defectos equivalentes** del lote y calcula el factor de rendimiento y el **pago** al caficultor.

## 2. Glosario del dominio

| Término | Significado |
|---|---|
| Caficultor | Productor de café evaluado. No es usuario del sistema. Puede ser **Socio** de la cooperativa o **Externo**. |
| Personal | Usuario del sistema: **Evaluador** (id 1), **Gerente** (id 2), **Administrador** (id 3) — tabla `TIPO_PERSONAL`. En el código Gerente y Administrador tienen los mismos permisos (`require_admin_o_gerente`): precios, cooperativa, usuarios, auditoría, reportes estadísticos. |
| Evaluación | Análisis completo del lote de un caficultor (tabla `EVALUACION`). Recibe un código correlativo `EVA0000001` al finalizar. |
| Muestra | Porción del lote que se analiza: 100/150/200/250/300 g. |
| Peso trillado / tamizado | Pesos de la muestra después de quitar cáscara y de pasar el tamiz. |
| Peso bueno | Peso del grano sano separado por el sistema; lo ingresa el evaluador al completar. |
| Factor de rendimiento | `peso_bueno / (peso_muestra / 100)`. Define el rango de precio. |
| Tara | 0.25 kg por saco. `peso_neto = peso_bruto − num_sacos × 0.25`. |
| Quintal (qq) | Unidad de pago. Kg por quintal según tipo de grano: Pergamino 55.20, Pilado 46.00, Coco 85.00. |
| Valor del café | Precio por quintal según rango de factor de rendimiento (tabla `VALOR_CAFE`), registrado a diario por Gerente/Admin. |
| SCA | Specialty Coffee Association. Su norma define defectos equivalentes y grados. |
| Defecto equivalente | Cada clase de defecto pesa distinto (p. ej. 1 grano negro = 1 defecto; 5 granos partidos = 1 defecto). |
| Grado | No se calcula: depende del tipo de defecto (primario/secundario) y el modelo solo distingue defecto/verde. |
| INCAL | Entidad de referencia que advierte sobre materia extraña en lotes (piedras, palitos, pajilla). |
| Materia extraña / "desconocido" | Objeto que el modelo nunca reconoce como grano. Se desvía a defecto y suma 1.0 a los defectos equivalentes. |
| Lote (en el ML) | Sesión de conteo del tracker entre un `resetear` y el reporte final. Coincide con una evaluación. |

## 3. Flujo de una evaluación

```
/registro                      Evaluador ingresa caficultor, sacos, peso bruto, humedad,
   │                           pesos de muestra/trillado/tamizado, tipo de grano.
   │  POST /evaluacion/registrar   → evaluación SIN código (estado "activa")
   ▼
/monitoreo/{id}                POST /video/iniciar  → cámara + YOLO + ByteTrack
   │                           POST /arduino/motor/iniciar → arranca la faja
   │                           GET  /video/stream | /video/frame   → video anotado
   │                           GET  /video/lote/conteo (1.5 s)     → conteo en vivo
   │                           GET  /video/eventos                  → bitácora del monitoreo
   │                           [servo separa defectos en paralelo]
   │  POST  /video/lote/generar-reporte → defectos equivalentes
   │  PATCH /evaluacion/{id}/finalizar  → código EVA + eventos a EVENTO_MONITOREO
   ▼
/analisis/{id}                 Evaluador pesa el grano bueno.
   │  PATCH /evaluacion/{id}/completar  → factor, categoría, precio, pago
   ▼
/reporte                       Búsqueda por código EVA, reportes estadísticos.
```

Guardas de navegación: una evaluación con código redirige de `/monitoreo` a `/analisis` y viceversa.

## 4. Páginas

| URL | Template | Acceso |
|---|---|---|
| `/` (alias `/inicio`) | `inicio.html` | Sesión |
| `/auth/login` | `login.html` | Público |
| `/registro` | `registro.html` | Sesión |
| `/monitoreo/{id}` | `monitoreo.html` | Sesión |
| `/analisis/{id}` | `analisis.html` | Sesión |
| `/reporte` | `reporte.html` | Sesión |
| `/nuevo-caficultor` | `caficultor.html` | Sesión |
| `/perfil` | `perfil.html` | Sesión |
| `/prueba` | `prueba.html` | Sesión — prueba de detección en vivo sin evaluación |
| `/valor-cafe` | `valor_cafe.html` | Gerente / Administrador |
| `/configuracion-cooperativa` | `cooperativa.html` | Gerente / Administrador |

## 5. Stack y arquitectura

| Componente | Tecnología |
|---|---|
| Backend | FastAPI + Uvicorn, Python 3.11 |
| Frontend | Jinja2 server-rendered, TailwindCSS + CSS por página, JS vanilla en `src/static/js/` |
| Base de datos | PostgreSQL 18 (BD `tesis_prj`), psycopg2 directo sin ORM, UUIDv7 nativo |
| Autenticación | JWT en cookie httponly `access_token`, Argon2, TTL 7 días |
| Visión | Ultralytics YOLO26n + ByteTrack, PyTorch CUDA 13 (GPU) / ONNX Runtime (CPU) |
| Cámara | ELP AR0234 global shutter, USB 2.0, MJPEG 1920×1080 ~90 fps |
| Hardware | Arduino Uno: faja (L298N + motor JGY370: ENA 5, IN1 4, IN2 3; PWM 255), HC-SR04 (7/8), servo (9). Serie 9600 baud |

**Cuatro capas obligatorias** (cada feature tiene un archivo en cada una):

| Capa | Ruta | Regla |
|---|---|---|
| Routes | `src/routes/` | Solo HTTP. Sin lógica ni SQL. |
| Services | `src/services/` | Lógica de negocio y orquestación; dueño de `commit`/`rollback`. Sin SQL. |
| Models | `src/models/` | SQL crudo parametrizado (`%s`), acepta `db: Connection = None`. Sin lógica. |
| Schemas | `src/schemas/` | Toda la validación Pydantic. |

Además: `src/apis/` (cliente RENIEC/Factiliza), `src/utilities/` (JWT, UUIDv7, serie Arduino,
servo, validador de documentos, eventos de monitoreo, medidor de latencia), `src/ml/` (tracker
y classifier). Detalle de carpetas en [docs/arquitectura.md](../arquitectura.md).

**Hilos del módulo ML** (no cambiar su estructura):

```
camara_service  (hilo productor: captura, guarda solo el último frame + timestamp)
      │
tracker_service (hilo consumidor: cadencia, gate de movimiento, evidencias, eventos)
      │
CoffeeRenTracker.procesar_frame()  (tiles → YOLO → fusión → ByteTrack → clase → servo)
      │
servo_controller (cola temporal) → arduino_serial → Arduino
```

## 6. Base de datos

Tablas: `PERSONA`, `PERSONAL`, `TIPO_PERSONAL`, `CAFICULTOR`, `TIPO_CAFICULTOR`, `COOPERATIVA`,
`UBIGEO`, `EVALUACION`, `DETALLE_EVALUACION`, `TIPO_DEFECTO`, `TIPO_GRANO`, `TIPO_DOCUMENTO`,
`CATEGORIA`, `VALOR_CAFE`, `AUDITORIA`, `EVENTO_MONITOREO` (añadida 2026-09-22: bitácora del
monitoreo por evaluación, escrita en la misma transacción que el código EVA).

## 7. Reglas de negocio que no se deben inventar

- Documento: DNI exactamente 8 dígitos; Pasaporte/Carnet de Extranjería 8–12 alfanuméricos
  (`src/utilities/documento_validador.py`, compartido por caficultor y persona).
- Mayoría de edad (18) para registrar personas.
- Humedad: entero 1–30. Más de 12 % aplica castigo proporcional al peso neto.
- Peso bruto ≤ `num_sacos × 70 kg` y **mayor que la tara** `round(num_sacos × 0.25)` (desde 2026-09-30).
- Rangos de precio sin solapamiento y con precio no decreciente.
- Ante cualquier umbral o regla que el usuario no haya dado: **preguntar antes de implementar**.

## 8. Entorno de desarrollo

```bash
python -m venv .venv && source .venv/Scripts/activate
pip install -r requirements.txt            # incluye instrucciones del build CUDA de torch
cp src/config-example.py src/config.py     # y poner la contraseña real de PostgreSQL
psql -U postgres -d tesis_prj -f src/database/script.sql
uvicorn src.main:app --reload              # http://localhost:8000
./tailwindcss-windows-x64.exe -i src/static/css/input.css -o src/static/css/tailwind.css --watch
```

Pesos del modelo: `best.onnx` viene con el repositorio; `best.pt` (necesario para usar la GPU en
FP16) se descarga de Google Drive a `src/ml/models/yolov26n_2cls/`. Sin ningún peso la app no arranca. No hay suite de tests automatizados (solo `tests/verificacion_incremento_1.py`).

Equipos objetivo: laptop con RTX 5070 Ti (desarrollo y demostración) y laptop con GTX 1050
Mobile (mismo código, FP32). Windows 11, PowerShell.
