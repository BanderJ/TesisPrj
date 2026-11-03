# Librerías de CoffeeRen

Guía rápida de **todas** las librerías del proyecto: qué hace cada una y un ejemplo real de cómo se usa aquí.

---

## 1. Framework Web

### FastAPI
Framework web de Python. Define los endpoints HTTP, valida requests automáticamente con Pydantic y genera documentación en `/docs`.
```python
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(prefix="/reportes")

@router.get("/{codigo}")                      # GET /reportes/usuarios
async def obtener_reporte(codigo: str, usuario: dict = Depends(require_admin_o_gerente)):
    reporte = reporte_service.generar(codigo)
    if not reporte:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    return reporte                             # se convierte a JSON solo
```
- `Depends(...)` = inyección: ejecuta la función guard antes del endpoint (así se valida el JWT).
- `HTTPException` = respuesta de error con status y mensaje.

### Uvicorn
Servidor que ejecuta la app FastAPI. Es el comando con el que arranca todo:
```bash
uvicorn src.main:app --reload    # --reload reinicia al guardar archivos (solo dev)
```

### Pydantic
Validación de datos. Cada schema es una clase: si el JSON que llega no cumple, FastAPI responde 422 solo.
```python
from pydantic import BaseModel, Field, model_validator

class CompletarEvaluacionRequest(BaseModel):
    total_defectos: int = Field(..., ge=0)      # entero, mínimo 0, obligatorio (...)
    peso_bueno: int = Field(..., ge=0)          # rechaza negativos y decimales solo

    @model_validator(mode="after")              # validación entre campos
    def validar(self):
        if self.peso_bueno > 1000: raise ValueError("mensaje claro")
        return self
```

### Jinja2
Motor de plantillas HTML. El servidor rellena variables `{{ }}` y bloques `{% %}` antes de enviar la página.
```html
{% extends "main.html" %}                      <!-- hereda nav, header, modales -->
{% block content %} <h1>{{ user.nombre }}</h1> {% endblock %}
{% block script %} <script>const EVALUACION_ID = '{{ evaluacion_id }}';</script> {% endblock %}
```

### python-multipart
Soporte de formularios con archivos (`multipart/form-data`). Se usa al subir la imagen de la cooperativa:
```python
@router.post("/upload-imagen")
async def upload(file: UploadFile = File(...)):   # multipart hace esto posible
    contents = await file.read()
```

### Starlette
La base sobre la que está construido FastAPI. Solo se usa directo para personalizar los archivos estáticos:
```python
class _NoCacheStaticFiles(StaticFiles):        # main.py — el navegador siempre revalida CSS/JS
    async def get_response(self, path, scope):
        response = await super().get_response(path, scope)
        response.headers["Cache-Control"] = "no-cache"
        return response
```

---

## 2. Base de Datos

### psycopg2
Driver de PostgreSQL. No hay ORM: SQL directo envuelto en la clase `Connection` ([src/database/bd.py](../src/database/bd.py)).
```python
db = Connection()
try:
    fila = db.obtener_uno("SELECT nombre FROM persona WHERE id = %s", [persona_id])
    db.ejecutar("UPDATE personal SET estado = %s WHERE personal_id = %s", ["I", pid])
    db.commit()          # autocommit=False: nada se guarda sin commit()
except Exception:
    db.rollback()
    raise
finally:
    db.close()           # SIEMPRE, pase lo que pase
```
**Regla de oro:** valores siempre con `%s` (parametrizado) — nunca f-strings con datos del usuario (SQL injection).

---

## 3. Autenticación y Seguridad

### PyJWT (`import jwt`)
Crea y verifica los tokens de sesión. El token viaja en una cookie httponly (JS no puede leerla).
```python
import jwt
token = jwt.encode({"usuario": "jbecerrac", "rol": "Gerente", "exp": ...}, SECRET_KEY, algorithm="HS256")
payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])   # lanza error si expiró o fue alterado
```

### argon2-cffi
Hashing de contraseñas (ganador del Password Hashing Competition). Nunca se guarda la contraseña, solo su hash.
```python
from argon2 import PasswordHasher
ph = PasswordHasher()
hash_ = ph.hash("MiClave123!")        # guardar esto en BD
ph.verify(hash_, "MiClave123!")       # True, o lanza VerifyMismatchError
```

---

## 4. Visión Artificial y ML

### Ultralytics (YOLO)
Framework de detección de objetos. Carga el modelo entrenado (`best.pt` en GPU, `best.onnx` en CPU) y detecta granos. Incluye ByteTrack para que cada grano conserve un ID entre frames (no contar dos veces). El tracker no usa `model.track()`: infiere los 9 recortes de la grilla en un solo `predict()`, fusiona las cajas y alimenta un `BYTETracker` propio.
```python
from ultralytics import YOLO
from ultralytics.trackers.byte_tracker import BYTETracker
model = YOLO("src/ml/models/yolov26n_2cls/best.pt")      # cargar UNA vez al inicio
resultados = model.predict(recortes, imgsz=640, conf=0.15, iou=0.80,
                           device=0, half=True, verbose=False)   # un batch con los 9 tiles
```

### PyTorch (torch / torchvision)
Motor de inferencia que YOLO usa por debajo. Debe instalarse la variante CUDA (`torch==2.12.0+cu130`, ver `requirements.txt`); la variante `+cpu` deja la GPU sin usar. En el proyecto se consulta directo para elegir device, FP16 y tope de hilos:
```python
import torch
device = 0 if torch.cuda.is_available() else "cpu"
half = torch.cuda.is_available() and torch.cuda.get_device_capability(0)[0] >= 7
torch.set_num_threads(4)                      # ML_MAX_THREADS_CPU
```

### OpenCV (`import cv2`)
Captura de video de la cámara ELP y manipulación de frames (dibujar cajas, codificar JPG para el streaming).
```python
cap = cv2.VideoCapture(0)                     # abrir cámara USB
ok, frame = cap.read()                        # frame = array NumPy (alto, ancho, 3)
cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)   # caja roja (BGR)
_, jpg = cv2.imencode(".jpg", frame)          # solo para el streaming MJPEG al navegador
```

### NumPy
Arrays numéricos. Cada frame de video **es** un array NumPy — YOLO los recibe directo, sin conversión.
```python
frame.shape       # (1080, 1920, 3) → alto, ancho, canales BGR
```

### Pillow
Procesamiento de imágenes. Dependencia interna de ultralytics — no se usa directo en el código propio.

### ONNX (onnx / onnxruntime / onnxslim)
Formato portable de modelos ML. Los `.pt` se exportan a `.onnx` para inferencia más rápida en CPU. `onnxruntime` (build CPU, sin CUDA ni DirectML) los ejecuta, `onnxslim` optimiza el grafo al exportar.
```python
YOLO("best.pt").export(format="onnx", imgsz=640, half=False, dynamic=False, simplify=True)
# tracker.py: con GPU carga best.pt primero; en CPU, best.onnx primero
```

---

## 5. Hardware

### pySerial (`import serial`)
Comunicación con el Arduino por puerto COM (faja, servo, sensor de tapa). Solo lo toca `arduino_serial.py` — un hilo lee líneas continuamente y cachea el estado.
```python
import serial
puerto = serial.Serial(port="COM5", baudrate=9600, timeout=1.0)
linea = puerto.readline().decode("utf-8").strip()   # "LISTO:4.32" o "NO_LISTO:-1.00"
puerto.write(b"SERVO:DEFECTO\n")                    # comando hacia el Arduino
```

---

## 6. Librería estándar de Python (viene incluida, no se instala)

### typing (`Any`, `Callable`, `Literal`)
Anotaciones de tipo. `Any` = "cualquier tipo" (para dicts de BD cuyo contenido varía); `Literal` = solo esos valores exactos.
```python
def obtener(self) -> list[dict[str, Any]]: ...     # lista de filas de BD
tipo: Literal["pie", "bar"]                        # Pydantic rechaza cualquier otro valor
```

### os
Interacción con el sistema operativo: variables de entorno y rutas.
```python
os.environ.get("ARDUINO_PORT") or "COM5"       # config con fallback
os.path.join(os.path.dirname(__file__), "templates")
os.makedirs("src/resources/cooperativa", exist_ok=True)
```

### datetime / date
Fechas y horas.
```python
from datetime import datetime, timedelta, date
exp = datetime.now() + timedelta(days=7)       # expiración del JWT
hoy = date.today()                             # precios de café del día
```

### decimal.Decimal
Números exactos para **dinero y pesos**. Los `float` acumulan errores binarios (0.1+0.2 ≠ 0.3); `Decimal` no.
```python
from decimal import Decimal, ROUND_DOWN
pago = (peso_por_qq * precio).quantize(Decimal("0.01"))            # redondeo a 2 decimales
peso_por_qq = (neto / ref).quantize(Decimal("0.01"), rounding=ROUND_DOWN)  # a favor de la coop.
# OJO: Decimal("0.83") desde string — Decimal * float da TypeError
```

### threading
Hilos: tareas en paralelo dentro del mismo proceso. La cámara y el lector serial corren en hilos para no bloquear las peticiones HTTP.
```python
hilo = threading.Thread(target=self._reader_loop, daemon=True)   # daemon: muere con la app
hilo.start()
with self._state_lock:          # Lock: evita que dos hilos escriban a la vez
    self._estado = nuevo_estado
```

### time
Pausas y marcas de tiempo.
```python
time.sleep(2.0)                      # esperar (el Arduino se resetea al abrir el puerto)
if time.time() - ultimo < 5.0: ...   # throttle de reconexión
```

### re (expresiones regulares)
Validar formatos de texto.
```python
_UUID_RE = re.compile(r"^[0-9a-fA-F]{8}-...$")
if not _UUID_RE.match(evaluacion_id): return RedirectResponse("/registro")
```

### json
Convertir entre dict de Python y texto JSON (para columnas `jsonb` y la API externa).
```python
incidencias_json = json.dumps(incidencias)     # dict → texto (guardar en BD)
data = json.loads(respuesta_texto)             # texto → dict
```

### dataclasses
Clases de datos sin boilerplate — define los campos y listo.
```python
@dataclass
class EstadoArduino:
    listo: bool = False
    distancia: float | None = None
    conectado: bool = False
```

### collections (`deque`, `defaultdict`)
Estructuras especializadas. `deque(maxlen=N)` descarta lo viejo solo (memoria acotada); `defaultdict` crea el valor inicial al primer acceso.
```python
conteo_ids = defaultdict(lambda: deque(maxlen=30))   # tracker: últimas 30 confianzas por grano
conteo_ids[track_id].append(conf)                    # sin verificar si la clave existe
```

### contextlib (`asynccontextmanager`)
Crea contextos con setup/teardown. Define el ciclo de vida de la app:
```python
@asynccontextmanager
async def lifespan(app):
    camara_service.iniciar()     # antes del yield: al arrancar
    yield
    arduino_serial.cerrar()      # después del yield: al apagar
```

### urllib.request
Cliente HTTP de la librería estándar. Con él se consulta la API de Factiliza (RENIEC) en `src/apis/reniec_api.py`:
```python
req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
with urllib.request.urlopen(req, timeout=8) as resp:
    data = json.loads(resp.read())
```
> Nota: se usa `urllib` (estándar, sin instalar nada) en vez de `requests`, por eso `requests` no está en `requirements.txt`.

### Otros de uso puntual
| Módulo | Uso en el proyecto |
|---|---|
| `asyncio` | generadores async del streaming MJPEG |
| `unicodedata` | quitar tildes al generar nombres de usuario |
| `math` | cálculos del tracker |
| `sys`, `importlib` | carga dinámica en el módulo ML |
| `uuid_utils.py` (propio) | genera UUID v7 (ordenables por tiempo) para las PK |

---

## 7. Frontend (JavaScript)

### ECharts (vendorizada en `static/js/lib/echarts.min.js`)
Gráficos interactivos. Se usa a través de la librería propia `CoffeeReport` — no se llama directo en las páginas.
```javascript
const chart = echarts.init(divContenedor);
chart.setOption({ series: [{ type: 'pie', data: [{name: 'Admin', value: 4}] }] });
chart.resize();   // al cambiar el tamaño de la ventana
```

### SheetJS / xlsx (CDN en reporte.html y analisis.html)
Genera archivos Excel en el navegador, sin backend.
```javascript
const ws = XLSX.utils.aoa_to_sheet([['Código', 'EVA0000001'], ['Granos', 200]]);
const wb = XLSX.utils.book_new();
XLSX.utils.book_append_sheet(wb, ws, 'Resumen');
XLSX.writeFile(wb, 'reporte.xlsx');   // descarga directa
```

### Librerías propias (en `static/js/`)
| Librería | Qué hace | Ejemplo |
|---|---|---|
| `CoffeeModal` (main.js) | Modales globales — nunca usar `alert()` | `CoffeeModal.error(msg, 'Título')` / `await CoffeeModal.confirm({message})` |
| `CoffeeValidators` (validators.js) | Validaciones reutilizables de formularios | `CoffeeValidators.pesoBueno(valor, max)` → `{valido, peso, mensaje}` |
| `CoffeeReport` (coffee-report.js) | Renderiza cualquier reporte (tabla + gráfico) del endpoint `/reportes/{codigo}` | `CoffeeReport.render(contenedor, reporte)` |
