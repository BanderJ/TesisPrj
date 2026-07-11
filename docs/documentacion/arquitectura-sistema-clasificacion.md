# Arquitectura del Sistema de Clasificación de Granos de Café

**Fecha:** Junio 2026
**Proyecto:** CoffeeRen — Tesis USAT / Line Coffee Marañón
**Estado actual:** Operativo con modelo binario (2 clases)

---

## 1. Qué hace el sistema actualmente

El sistema captura video en tiempo real de una faja transportadora de granos de café, detecta cada grano con un modelo YOLO, le asigna un ID único persistente (ByteTrack), y activa un servo motor para separar físicamente los granos defectuosos de los buenos.

Al finalizar el lote, calcula el grado de calidad del café según la norma SCA (Specialty Coffee Association) con base en el conteo de granos únicos detectados.

### Modelo en uso: `yolov26n_2cls`

El modelo activo en producción es **YOLO26n con 2 clases** (clasificación binaria). No distingue el tipo específico de defecto — solo determina si un grano es:

| Clase | Color en video | Equivalencia SCA |
|---|---|---|
| `defecto` | Rojo `(0, 0, 255)` | 0.83 defectos/grano |
| `verde` | Verde `(0, 200, 0)` | 0.0 (no es defecto) |

La equivalencia 0.83 para `defecto` es un promedio ponderado de los defectos SCA más comunes (agrio severo 1.0, cereza seca 1.0, broca severo 1.0, agrio ligero 0.33). Esto es una simplificación temporal mientras se completa el entrenamiento del modelo de 17 clases.

El modelo se carga al arrancar la app y su ruta física es:

```
src/ml/models/yolov26n_2cls/best.pt   ← pesos YOLO (no está en Git)
src/ml/models/yolov26n_2cls/constants.py ← clases, colores, equivalencias SCA
```

Para cambiar el modelo activo, editar la última línea de `src/services/tracker_service.py`:

```python
tracker_service = TrackerService(model_name="yolov26n_2cls")  # ← cambiar aquí
```

---

## 2. Arquitectura de hilos (multithreading)

El sistema corre con **4 hilos de fondo permanentes** más el event loop de FastAPI (async). Ningún hilo bloquea a otro directamente — se comunican por variables compartidas con locks o por colas.

```
Arranque de la app (main.py lifespan)
│
├── [hilo] camara-capture       ← activo desde el arranque, siempre
├── [hilo] arduino-reader       ← activo desde el arranque, siempre
├── [hilo] arduino-keepalive    ← activo desde el arranque, siempre
├── [hilo] servo-controller     ← activo desde el arranque, siempre
│
└── [hilo] tracker-processing   ← se activa con POST /video/iniciar
                                   se detiene con POST /video/detener
```

### Diagrama de comunicación entre hilos

```
┌─────────────────────────────────────────────────────────────────────┐
│  [camara-capture]                                                   │
│  cap.read() en loop → guarda _latest_frame (BGR) + _latest_jpeg    │
│  Señaliza threading.Event _new_frame cuando hay frame nuevo         │
└───────────────────────┬─────────────────────────────────────────────┘
                        │ Event.wait() / Event.set()
                        ▼
┌─────────────────────────────────────────────────────────────────────┐
│  [tracker-processing]                                               │
│  esperar_frame() → obtener_frame_bgr() → tracker.procesar_frame()  │
│  Resultado JPEG anotado → guarda en _frame_anotado (bajo Lock)      │
│  Detecta IDs nuevos → llama servo_controller.solicitar(...)         │
└───────────┬──────────────────────────────┬──────────────────────────┘
            │ Lock (lectura)               │ cola interna
            ▼                              ▼
┌───────────────────────┐    ┌────────────────────────────────────────┐
│  [FastAPI async loop] │    │  [servo-controller]                    │
│  GET /video/stream    │    │  _worker() despierta cada 10ms         │
│  Lee _frame_anotado   │    │  Al vencer el SERVO_DELAY_S (0.5s):    │
│  → MJPEG al browser   │    │    evalúa mejor clase del grano        │
└───────────────────────┘    │    envía SERVO:DEFECTO o SERVO:BUENO   │
                             └────────────────┬───────────────────────┘
                                              │ write_lock / serial.write()
                                              ▼
                             ┌────────────────────────────────────────┐
                             │  [arduino-reader]                      │
                             │  readline() continuo del puerto COM9   │
                             │  Parsea: LISTO:, PESO:, SISTEMA:LISTO  │
                             │  Cachea estado en EstadoArduino        │
                             └────────────────────────────────────────┘
```

---

## 3. Descripción detallada por componente

### 3.1 `CamaraService` — `src/services/camara_service.py`

Hilo dedicado de captura. Drena la cámara al máximo FPS del sensor y siempre expone el frame más reciente.

**Qué hace:**
- Abre la cámara con `cv2.VideoCapture` (intenta índice 0, luego 1 como fallback)
- Configura buffer mínimo (`CAP_PROP_BUFFERSIZE=1`) para baja latencia
- Activa MJPEG en el sensor si está disponible (`FOURCC=MJPG`)
- Guarda `_latest_frame` (BGR puro para YOLO) y `_latest_jpeg` (JPEG calidad 95)
- Dispara `threading.Event._new_frame` en cada frame nuevo

**Sincronización con el tracker:**
```python
# En CamaraService:
self._new_frame.set()   # notifica que hay frame

# En TrackerService._loop_procesamiento():
camara_service.esperar_frame(timeout=1.0)  # bloquea hasta Event o timeout
frame = camara_service.obtener_frame_bgr()  # lee BGR sin pasar por JPEG
```

**Detección de desconexión:** 10 errores consecutivos de `cap.read()` → `_running = False` → `esta_disponible()` retorna `False` → el `TrackerService` detecta y activa modo emergencia.

---

### 3.2 `CoffeeRenTracker` — `src/ml/tracker.py`

Núcleo del sistema ML. Recibe frames BGR y retorna JPEG anotado con bounding boxes y estadísticas.

**Inicialización:**
1. Carga el modelo YOLO desde `src/ml/models/{model_name}/best.pt`
2. Carga dinámicamente `constants.py` del modelo (CLASES, COLORES, EQUIVALENCIAS_DEFECTO, GRANO_MIN/MAX_PX)
3. Realiza warmup con un frame negro `640x640` para inicializar ByteTrack + JIT de PyTorch
4. Detecta GPU con `torch.cuda.is_available()` — usa CUDA si hay, sino CPU

**`procesar_frame(frame)` — el método central:**

```
frame BGR (1280x720)
        ↓
model.track(source=frame, imgsz=640, tracker="bytetrack.yaml", persist=True)
        ↓
Por cada detección con ID asignado por ByteTrack:
  1. Filtro de tamaño: descarta si bounding box < 8px o > 300px
  2. Acumula conteo_ids_confianza[track_id].append((clase, conf))
  3. Si track_id es NUEVO → servo_controller.solicitar(lambda_clase, equivalencias)
  4. Dibuja bounding box + etiqueta "#ID clase conf%" en el frame
        ↓
Dibuja estadísticas: "Granos: N | FPS: X | Detecciones: Y"
        ↓
cv2.imencode(".jpg", frame_anotado, calidad=85) → bytes JPEG
```

**Persistencia de clase por grano:**
Cada grano puede aparecer en docenas de frames mientras cruza la cámara. La clase final se determina tomando la detección con **mayor confianza** entre todas las acumuladas, no la primera ni un promedio:

```python
def _mejor_clase_para(self, track_id: int) -> str | None:
    detecciones = self.conteo_ids_confianza.get(track_id, [])
    return max(detecciones, key=lambda x: x[1])[0]  # max por confianza
```

Esto se llama de forma lazy desde el `ServoController` en el momento de activación, cuando ya hay más frames acumulados que en la primera detección.

---

### 3.3 `TrackerService` — `src/services/tracker_service.py`

Orquestador que une `CamaraService` con `CoffeeRenTracker`. Expone la API pública que usan las rutas HTTP.

**Loop de procesamiento (`_loop_procesamiento`):**
```python
while self.activo:
    if not camara_service.esta_disponible():
        self._on_camara_desconectada()   # emergencia
        break
    camara_service.esperar_frame(timeout=1.0)
    frame = camara_service.obtener_frame_bgr()
    frame_anotado_jpeg = self.tracker.procesar_frame(frame)
    with self._lock:
        self._frame_anotado = frame_anotado_jpeg
```

**Modo emergencia por desconexión de cámara:**
```python
def _on_camara_desconectada(self):
    self.activo = False
    self._camara_desconectada = True
    servo_controller.bloquear()                    # descarta cola completa
    arduino_serial.enviar_comando("SERVO:DEFECTO") # fija servo en defecto
```

Ante pérdida de cámara, el servo queda fijo en posición DEFECTO (canal seguro) hasta que el operador reinicie el monitoreo.

**Conteo enriquecido (`obtener_conteo_enriquecido`):**
Usado por el polling del frontend (GET /video/lote/conteo). Calcula en una sola pasada:
- `total_granos`, `total_defectos`, `total_sanos`
- `conteo_agrupado` por categorías de display (negro, brocado, partido)
- `segundos_sin_deteccion` — tiempo desde la última detección real

---

### 3.4 `ServoController` — `src/utilities/servo_controller.py`

Hilo de fondo que separa físicamente los granos defectuosos aplicando un delay calibrado.

**Flujo por cada grano detectado por primera vez:**

```
Tracker detecta track_id nuevo
        ↓
servo_controller.solicitar(
    obtener_clase = lambda: tracker._mejor_clase_para(track_id),
    equivalencias = EQUIVALENCIAS_DEFECTO,
    ejecutar_en   = time.monotonic() + SERVO_DELAY_S  # 0.5s por defecto
)
        ↓
[hilo servo-controller, 10ms después]:
  while time.monotonic() < ejecutar_en: esperar
        ↓
  clase = obtener_clase()           # evalúa lambda AHORA (más frames acumulados)
  es_defecto = equivalencias[clase] > 0.0
        ↓
  Si es_defecto:
    arduino → "SERVO:DEFECTO"
    sleep(SERVO_HOLD_S = 0.3s)    # tiempo que el servo permanece desviando
    arduino → "SERVO:BUENO"
  Si no:
    arduino → "SERVO:BUENO"
```

**Parámetros calibrables (via `.env` o `src/config.py`):**

| Variable | Valor actual | Descripción |
|---|---|---|
| `SERVO_DELAY_S` | `0.5s` | Tiempo que tarda el grano en viajar de la cámara al servo |
| `SERVO_HOLD_S` | `0.3s` | Tiempo que el servo mantiene posición DEFECTO |

**Estados especiales:**
- `bloquear()` → descarta toda la cola, el worker no enviará más comandos (emergencia por desconexión de cámara)
- `desbloquear()` → restaura operación normal al reiniciar monitoreo
- `limpiar_cola()` → descarta pendientes al resetear un lote

---

### 3.5 `ArduinoSerial` — `src/utilities/arduino_serial.py`

Gestiona la comunicación serial bidireccional con el Arduino en `COM9` a 9600 baud.

**Protocolo:**

```
Arduino → Backend (lecturas continuas):
  LISTO:4.34    → tapa cerrada, grano detectado (distancia < umbral)
  NO_LISTO:5.21 → sin grano o tapa abierta
  PESO:1234.56  → lectura de celda de carga en gramos
  TARE:OK       → confirmación de tara
  SISTEMA:LISTO → Arduino recién reiniciado (inesperado)

Backend → Arduino (comandos):
  ON            → encender faja transportadora
  OFF           → apagar faja + resetear servo a BUENO
  SERVO:BUENO   → servo al canal de granos buenos
  SERVO:DEFECTO → servo al canal de granos defectuosos
  TARE          → tarar báscula
  SCALE:<factor>→ actualizar calibración de celda de carga
```

**Reconexión automática:** Si el hilo `arduino-reader` cae (error serial), `_asegurar_conexion()` reintenta cada 5 segundos (throttle). Si el Arduino se reinicia mientras la faja estaba activa (`SISTEMA:LISTO` recibido con `_motor_activo=True`), envía `ON` automáticamente para retomar sin intervención manual.

**Keep-alive USB:** El hilo `arduino-keepalive` envía `\n` vacío cada 20 segundos para prevenir que Windows suspenda el puerto USB serial.

---

### 3.6 `classifier.py` — `src/ml/classifier.py`

No corre en tiempo real. Se invoca al final del lote cuando el operador solicita el reporte.

**Entrada:** `{clase: n_granos_unicos}` — output de `tracker.obtener_conteo()`
**Salida:**
```python
{
    "total_granos_analizados": 312,
    "total_defectos": 18.7,          # equivalentes SCA
    "grado": "Grado 2",
    "apto_specialty": False,
    "detalle_por_clase": {
        "defecto": {
            "granos": 22,
            "peso_por_grano": 0.83,
            "defectos_equivalentes": 18.26
        }
    },
    "resumen": "Lote analizado: 312 granos — 18.7 defectos — Grado 2 — NO APTO para Specialty"
}
```

**Tabla de grados SCA (3 niveles):**

| Grado | Defectos equivalentes en 350g |
|---|---|
| Grado 1 (Specialty) | 0 – 15 |
| Grado 2 | 16 – 23 |
| Grado 3 | 24 o más |

---

## 4. Rutas HTTP del sistema ML

Todas bajo `src/routes/video.py`:

| Método | Ruta | Qué hace |
|---|---|---|
| `GET` | `/video/stream` | MJPEG streaming continuo con bounding boxes en tiempo real |
| `GET` | `/video/frame` | Último frame JPEG individual (para refresh manual) |
| `GET` | `/video/status` | Estado del sistema + conteo actual + errores de cámara |
| `POST` | `/video/iniciar` | Inicia hilo tracker-processing (requiere auth) |
| `POST` | `/video/detener` | Detiene hilo tracker-processing (requiere auth) |
| `GET` | `/video/lote/conteo` | Conteo enriquecido en tiempo real (para polling frontend) |
| `POST` | `/video/lote/generar-reporte` | Genera reporte SCA final del lote |
| `POST` | `/video/lote/resetear` | Limpia conteo para nuevo lote |
| `POST` | `/video/liberar-camara` | Fuerza liberación de cámara si está bloqueada |

---

## 5. Ciclo de vida de una sesión completa

```
1. App arranca (main.py lifespan)
   ├── camara_service.iniciar()  → [camara-capture] empieza a capturar
   ├── arduino_serial conecta   → [arduino-reader] + [arduino-keepalive] inician
   └── servo_controller inicia  → [servo-controller] queda en espera

2. Operador abre /registro y crea evaluación → obtiene evaluacion_id

3. Operador navega a /monitoreo/{evaluacion_id}
   ├── Presiona "Iniciar" → POST /video/iniciar
   │   └── [tracker-processing] arranca
   ├── Browser conecta a <img src="/video/stream"> → MJPEG en vivo
   └── JS hace polling GET /video/lote/conteo cada N segundos → actualiza contadores

4. En cada frame del [tracker-processing]:
   ├── CamaraService.esperar_frame() → desbloquea con Event
   ├── CoffeeRenTracker.procesar_frame() → YOLO + ByteTrack
   │   ├── Por cada ID nuevo → servo_controller.solicitar(lambda_clase, delay=0.5s)
   │   └── Retorna JPEG anotado
   └── _frame_anotado = jpeg  (bajo lock)

5. Por cada grano en cola del [servo-controller]:
   ├── Espera 0.5s (SERVO_DELAY_S)
   ├── Evalúa mejor clase del grano (con más frames acumulados que al inicio)
   └── arduino → "SERVO:DEFECTO" o "SERVO:BUENO"

6. Operador presiona "Finalizar lote" → POST /video/lote/generar-reporte
   └── classifier.generar_reporte(conteo, EQUIVALENCIAS_DEFECTO) → grado SCA

7. Operador presiona "Detener" → POST /video/detener
   └── [tracker-processing] se detiene, conteo se resetea

8. App cierra (CTRL+C / shutdown)
   ├── tracker_service.detener()
   ├── arduino_serial.enviar_comando("OFF")
   ├── camara_service.cerrar()
   ├── servo_controller.cerrar()
   └── arduino_serial.cerrar()
```

---

## 6. Archivos clave del módulo ML

```
src/
├── main.py                          ← lifespan: inicia/cierra todo
├── config.py                        ← SERVO_DELAY_S, SERVO_HOLD_S, ARDUINO_PORT
├── ml/
│   ├── tracker.py                   ← CoffeeRenTracker (YOLO + ByteTrack + conteo)
│   ├── classifier.py                ← Cálculo SCA al fin del lote
│   ├── inference.py                 ← LEGACY — no usado en flujo actual
│   └── models/
│       ├── yolov8n/
│       │   ├── best.pt              ← pesos (no en Git)
│       │   └── constants.py         ← 17 clases, colores, equivalencias SCA
│       ├── yolov26n/
│       │   ├── best.pt
│       │   └── constants.py
│       └── yolov26n_2cls/           ← MODELO ACTIVO
│           ├── best.pt
│           └── constants.py         ← 2 clases: defecto, verde
├── services/
│   ├── camara_service.py            ← Hilo de captura, gestión de desconexión
│   └── tracker_service.py           ← Orquestador: integra cámara + tracker
├── routes/
│   └── video.py                     ← Rutas HTTP: stream, iniciar, conteo, reporte
└── utilities/
    ├── arduino_serial.py            ← Serial bidireccional, reconexión automática
    └── servo_controller.py          ← Cola de separación con delay calibrado
```

---

## 7. Modelo activo vs. modelos disponibles

| Modelo | Clases | Estado | mAP50 |
|---|---|---|---|
| `yolov8n` | 17 clases (defectos específicos) | Entrenado — 75 épocas | 0.767 |
| `yolov26n` | 17 clases | En progreso | — |
| `yolov26n_2cls` | **2 clases (defecto / verde)** | **ACTIVO** | — |
| `yolo11n` | 17 clases | Pendiente | — |

El modelo `yolov26n_2cls` es una versión simplificada de 2 clases usada mientras el modelo de 17 clases completa entrenamiento. Para activar el modelo de 17 clases cambiar `model_name` en `tracker_service.py` a `"yolov8n"` o `"yolov26n"`.
