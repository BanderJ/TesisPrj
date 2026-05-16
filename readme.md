# CoffeeRen

Sistema web de clasificación y gestión de muestras de café para la Cooperativa de Lonya Grande, Amazonas, Perú. Desarrollado como proyecto de tesis universitaria.

## Descripción

CoffeeRen digitaliza el proceso de recepción y clasificación de café: registra la muestra de un caficultor, la procesa en una banda transportadora controlada por Arduino, captura video con una cámara ELP AR0234, calcula el rendimiento y el pago automáticamente, y emite un código de evaluación (EVA) al finalizar.

## Tecnologías

| Componente | Tecnología |
|---|---|
| Backend | FastAPI + Uvicorn |
| Base de datos | PostgreSQL + psycopg2 (sin ORM) |
| Frontend | Jinja2 templates + CSS/JS vanilla |
| Auth | JWT en cookie httponly (Argon2 + PyJWT) |
| Hardware | Arduino Uno + HC-SR04 + MX1508 + HX711 + Servo |
| Cámara | OpenCV headless — ELP AR0234 (MJPEG streaming) |

## Requisitos previos

- Python 3.11.9
- PostgreSQL corriendo localmente
- Arduino IDE (para cargar el firmware)

## Instalación

```bash
# 1. Crear y activar el entorno virtual
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar la base de datos
# Editar src/config.py con las credenciales de PostgreSQL y ejecutar el schema:
psql -U <usuario> -d <base_de_datos> -f src/database/script.sql
```

## Ejecución

```bash
# Servidor de desarrollo (recarga automática)
uvicorn src.main:app --reload
```

La app queda disponible en `http://localhost:8000`.

```bash
# Compilar Tailwind CSS (modo watch)
.\tailwindcss-windows-x64.exe -i src\static\css\input.css -o src\static\css\tailwind.css --watch
```

## Estructura del proyecto

```
TesisPrj/
├── arduino/
│   └── logica_hardware/        # Firmware Arduino (HC-SR04 + MX1508 + HX711 + Servo)
├── src/
│   ├── database/
│   │   ├── bd.py               # Wrapper de conexión psycopg2
│   │   └── script.sql          # Schema de la base de datos
│   ├── models/                 # SQL crudo por entidad
│   ├── routes/                 # Endpoints FastAPI
│   ├── schemas/                # Modelos Pydantic (request/response)
│   ├── services/               # Lógica de negocio
│   ├── static/                 # CSS, JS, íconos
│   ├── templates/              # Plantillas Jinja2
│   ├── utilities/              # JWT, helpers
│   ├── config.py               # Configuración (DB, SECRET_KEY)
│   └── main.py                 # Punto de entrada de la app
└── requirements.txt
```

## Páginas

| URL | Descripción | Acceso |
|---|---|---|
| `/` | Dashboard de inicio | Todos |
| `/registro` | Registro de muestra de café | Todos |
| `/monitoreo/{id}` | Monitoreo en tiempo real de la clasificación | Todos |
| `/analisis/{id}` | Resumen estadístico y pago calculado | Todos |
| `/reporte` | Búsqueda de evaluaciones por código EVA | Todos |
| `/nuevo-caficultor` | Alta y conversión de caficultores a socios | Todos |
| `/valor-cafe` | Gestión de precios de café | Solo Gerente / Admin |
| `/auth/login` | Inicio de sesión | — |

## Flujo principal

```
Registro de muestra
       ↓
POST /evaluacion/registrar  →  evaluacion_id (UUID)
       ↓
/monitoreo/{id}  →  banda transportadora + cámara en tiempo real
       ↓
PATCH /evaluacion/{id}/completar  →  calcula peso_bueno, pago, categoría
       ↓
PATCH /evaluacion/{id}/finalizar  →  asigna código EVA correlativo
       ↓
/analisis/{id}  →  resumen completo + código EVA
```

## Hardware — Arduino

El sketch en `arduino/logica_hardware/` controla:

| Componente | Pin(es) | Función |
|---|---|---|
| MX1508 (motor) | 5, 6 | Banda transportadora |
| HC-SR04 | 7 (TRIG), 8 (ECHO) | Detección de presencia de granos |
| HX711 (celda de carga) | A0, A1 | Medición de peso |
| Servo | 9 | Desvío de granos defectuosos |

- Baud rate: 9600
- Comando `PF` → toma 20 muestras de peso y responde `{"tipo":"peso_final","g":X,"kg":X}`

## Roles de usuario

| tipo_personal_id | Rol | Permisos extra |
|---|---|---|
| 1 | Operario | Acceso estándar |
| 2 | Gerente | Crear/modificar precios de café |
| 3 | Administrador | Crear/modificar precios de café |

## Variables de entorno

La única variable leída desde el entorno es `SECRET_KEY` (firma JWT). Las credenciales de base de datos se configuran en `src/config.py`.

```powershell
$env:SECRET_KEY = "tu-clave-secreta-aqui"
```
