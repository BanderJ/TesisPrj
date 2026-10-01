# Instalación y Setup — CoffeeRen

## Requisitos Previos

- **Python 3.10+** (verificar con `python --version`)
- **PostgreSQL 12+** (local o remoto)
- **Git**
- **Windows 11 / Linux / macOS** (tested en Windows 11)

---

## Pasos de Instalación

### 1. Clonar el repositorio
```bash
git clone <repo-url>
cd TesisPrj
```

### 2. Crear entorno virtual
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/macOS
python -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Nota:** Primera instalación puede tardar ~3-5 minutos porque torch + ultralytics (~2GB) se descargan.

### 4. Configurar credenciales

`src/config.py` está en `.gitignore` (credenciales propias). Cópialo desde la
plantilla publicada y ajústalo:
```bash
# Windows
copy src\config-example.py src\config.py
# Linux/macOS
cp src/config-example.py src/config.py
```
Edita `PASSWORD` y `DATABASE` en `src/config.py` según tu PostgreSQL (BD por
defecto: **`tesis_prj`**).

El `.env` de la raíz solo cubre `SECRET_KEY` y parámetros opcionales de
Arduino/cámara/servo (todos con default en `config.py`):
```bash
SECRET_KEY=tu-clave-secreta-aqui
# ARDUINO_PORT=COM5
# CAM_INDICE=
```

### 5. Preparar la base de datos

```bash
# Crear la base y ejecutar el schema
createdb -U postgres tesis_prj
psql -U postgres -d tesis_prj -f src/database/script.sql
```

Guía detallada en `Manual_Instalacion_CoffeeRen.md`.

### 6. Descargar modelos YOLO

Los pesos entrenados NO están en Git por su tamaño (~9 MB).

**Ubicación esperada:**
```
src/ml/models/
└── yolov26n_2cls/
    ├── best.onnx        (usado en producción)
    ├── best.pt          (respaldo)
    └── constants.py     (clases y equivalencias — sí versionado)
```

El tracker carga `best.onnx` y usa `best.pt` como fallback. Verifica con
`python check_model.py`.

**Descargar desde:**
- Google Drive (CoffeeRen/modelos/) → Copiar a `src/ml/models/`
- O entrenar localmente con Google Colab

### 7. Compilar Tailwind CSS (opcional, solo si editas CSS)

```bash
# Windows
.\tailwindcss-windows-x64.exe -i src/static/css/input.css -o src/static/css/tailwind.css --watch

# Linux
./tailwindcss-linux-x64 -i src/static/css/input.css -o src/static/css/tailwind.css --watch
```

---

## Ejecutar la Aplicación

### Development (con hot-reload)

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Abrir en navegador: **http://localhost:8000**

### Production (simulado)

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## Estructura de Archivos

```
TesisPrj/
├── src/
│   ├── main.py                    # Punto de entrada FastAPI
│   ├── config.py                  # Configuración y credenciales
│   ├── database/
│   │   ├── bd.py                  # Connection pool psycopg2
│   │   └── script.sql             # Schema PostgreSQL
│   ├── routes/                    # Endpoints HTTP
│   ├── services/                  # Lógica de negocio
│   ├── models/                    # Queries SQL
│   ├── schemas/                   # Validación Pydantic
│   ├── ml/
│   │   ├── tracker.py             # Captura USB + ByteTrack + carga del modelo YOLO
│   │   ├── classifier.py          # Cálculo de grados (SCA)
│   │   └── models/                # Pesos entrenados (best.onnx / best.pt)
│   ├── utilities/
│   │   ├── jwt_required.py        # Middleware JWT
│   │   ├── arduino_serial.py      # Serial con el Arduino
│   │   └── servo_controller.py    # Cadena de tiempos del servo separador
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── icon/
│   └── templates/                 # Jinja2 HTML
├── requirements.txt               # Dependencias Python
├── CLAUDE.md                      # Guía para Claude Code
├── INSTALACION.md                 # Este archivo
└── README.md                      # Documentación general
```

---

## Troubleshooting

### Error: `ModuleNotFoundError: No module named 'torch'`
```bash
# Reinstalar con versión específica compatible
pip install torch==2.0.0 torchvision==0.15.0 --no-cache-dir
```

### Error: `Could not find ELP camera at index 0`
- Verificar que la cámara ELP AR0234 está conectada (USB)
- Revisar `src/ml/tracker.py` línea con `cv2.VideoCapture(0)`

### Error: `Connection refused (PostgreSQL)`
```bash
# Verificar que PostgreSQL está ejecutándose
# Windows: Services → PostgreSQL
# Linux: sudo systemctl status postgresql
# macOS: brew services list | grep postgres
```

### Error: `psycopg2.OperationalError: database "tesis_prj" does not exist`
```bash
# Crear la base de datos
createdb -U postgres tesis_prj
psql -U postgres -d tesis_prj -f src/database/script.sql
```

### Torch/CUDA muy grande (~2GB)
Si no tienes GPU, usa CPU-only:
```bash
pip uninstall torch -y
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

---

## Comandos Útiles

```bash
# Ver versiones instaladas
pip list | grep -E "fastapi|ultralytics|torch|opencv"

# Limpiar cache pip
pip cache purge

# Actualizar todo
pip install --upgrade -r requirements.txt

# Desactivar venv
deactivate
```

---

## Notas para Desarrollo

- **Sin test suite:** Usar navegador para probar rutas
- **Credenciales hardcoded:** En `src/config.py` (cambiar antes de producción)
- **JWT 7 días TTL:** Configurado en `src/utilities/jwt_required.py`
- **No ORM:** Usar psycopg2 directo (control total, más rápido)

---

## Próximos Pasos Después de Instalar

1. ✅ Crear usuario admin: `/auth/login` → Formulario registro
2. ✅ Descargar modelos YOLO → Colocar en `src/ml/models/`
3. ✅ Conectar cámara ELP → Probar en `/monitoreo`
4. ✅ Calibrar Arduino → Conectar puerto serial
5. ✅ Validar equivalencias SCA → Con Line Coffee Marañón

---

**¿Problemas?** Revisar `CLAUDE.md` para estructura del proyecto o abrir issue en GitHub.
