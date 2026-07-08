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

### 4. Configurar variables de entorno

Crear archivo `.env` en la raíz del proyecto:
```bash
# Copia como base
cp .env.example .env

# O crea manualmente con:
SECRET_KEY=tu-clave-secreta-aqui
DATABASE_URL=postgresql://usuario:password@localhost:5432/cofferen
DEBUG=True
```

### 5. Preparar la base de datos

```bash
# Conectar a PostgreSQL y ejecutar el schema
psql -U postgres -d cofferen -f src/database/script.sql
```

O desde Python:
```bash
python -c "from src.database.bd import init_db; init_db()"
```

### 6. Descargar modelos YOLO

Los modelos entrenados NO están en Git por su tamaño (~6MB c/u).

**Ubicación esperada:**
```
src/ml/models/
├── yolov8n/best.pt       (mAP50: 0.767)
├── yolo26n/best.pt       (en progreso)
└── yolo11n/best.pt       (pendiente)
```

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
│   │   └── models/                # Pesos entrenados (.pt)
│   ├── utilities/
│   │   ├── jwt_required.py        # Middleware JWT
│   │   └── arduino.py             # Serial para actuadores
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── img/
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

### Error: `psycopg2.OperationalError: database "cofferen" does not exist`
```bash
# Crear la base de datos
createdb -U postgres cofferen
psql -U postgres -d cofferen -f src/database/script.sql
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
