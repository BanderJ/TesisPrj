# Arquitectura del proyecto

Este documento describe la arquitectura escogida para **CoffeeRen** y la
organización de carpetas del repositorio.

Se omiten de forma intencional las carpetas y archivos de soporte que **no
forman parte del sistema**: herramientas de asistentes de IA (`.claude/`,
`.codex/`, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`), integración con GitHub (`.github/`),
configuración del editor (`.vscode/`), documentación (`docs/`), scripts
auxiliares (`scripts/`), manuales y utilidades de generación de documentos.

---

## Estructura del repositorio

```text
TesisPrj/
│
├── arduino/                        # Firmware Arduino de los actuadores de separación física
│   ├── logica_hardware/            #   Sketch de producción: recibe comandos serial y mueve el servo
│
├── src/                            # Código de la aplicación: backend FastAPI + módulo ML + interfaz web
│   │
│   ├── routes/                     #   Capa 1 - Endpoints HTTP: reciben la petición y llaman a services
│   ├── services/                   #   Capa 2 - Lógica de negocio y control de transacciones (commit/rollback)
│   ├── models/                     #   Capa 3 - Acceso a datos: SQL crudo con psycopg2 (un archivo por entidad)
│   ├── schemas/                    #   Capa 4 - Validación de entrada/salida con Pydantic
│   │
│   ├── apis/                       #   Clientes de servicios externos (consulta de DNI a RENIEC)
│   ├── database/                   #   Conexión a PostgreSQL (bd.py) y esquema de la base (script.sql)
│   ├── ml/                         #   Módulo de visión por computadora
│   │   ├── tracker.py              #     Detección YOLO por tiles + IDs únicos por grano (ByteTrack) + clase por track
│   │   ├── classifier.py           #     Defectos equivalentes y grado SCA del lote
│   │   ├── bytetrack.yaml          #     Parámetros del algoritmo de seguimiento
│   │   └── models/                 #     Pesos YOLO + constants.py por modelo (best.onnx en Git, best.pt fuera)
│   ├── utilities/                  #   Utilidades transversales: JWT, hash Argon2, serial Arduino, servo, CSV de ubigeo
│   ├── resources/                  #   Imágenes y recursos internos usados por la aplicación
│   │
│   ├── templates/                  #   Vistas HTML (Jinja2) renderizadas por el servidor
│   ├── static/                     #   Recursos servidos al navegador
│   │   ├── css/                    #     Estilos por página + Tailwind compilado
│   │   ├── js/                     #     Scripts por página y validadores
│   │   └── icon/                   #     Íconos e imágenes de interfaz
│   │
│   ├── main.py                     #   Punto de entrada: crea la app FastAPI y registra los routers
│   ├── config.py                   #   Configuración real con credenciales (fuera de Git)
│   └── config-example.py           #   Plantilla de configuración publicada (se copia a config.py al instalar)
│
├── .venv/                          # Entorno virtual de Python con las dependencias instaladas (fuera de Git)
├── .env                            # Variables de entorno y secretos (fuera de Git)
├── .gitignore                      # Archivos y carpetas excluidos del control de versiones
└── requirements.txt                # Dependencias del proyecto (pip install -r requirements.txt)
```

---

## Arquitectura en capas (`src/`)

CoffeeRen sigue un patrón de **cuatro capas**. Cada funcionalidad tiene un
archivo en cada capa y las responsabilidades nunca se cruzan.

| Capa | Carpeta | Responsabilidad | No debe contener |
|---|---|---|---|
| 1. Routes | `src/routes/` | Definir endpoints HTTP, llamar a services, devolver plantilla o JSON | Lógica de negocio, SQL |
| 2. Services | `src/services/` | Lógica de negocio, orquestar models, hacer `commit` / `rollback` | SQL directo |
| 3. Models | `src/models/` | SQL crudo con psycopg2, siempre parametrizado | Lógica de negocio |
| 4. Schemas | `src/schemas/` | Validación de datos de entrada y salida con Pydantic | Todo lo demás |

**Flujo de una petición:**

```text
Navegador
   │  HTTP
   ▼
routes/  ──valida con──►  schemas/
   │
   ▼
services/  ──lógica de negocio, transacciones──
   │
   ▼
models/  ──SQL parametrizado──►  PostgreSQL
```

### Base de datos

Acceso directo con **psycopg2** (sin ORM). La clase `Connection` de
`src/database/bd.py` envuelve una conexión por petición con `autocommit=False`
y `RealDictCursor`. Cuando un service escribe en varias tablas de forma
atómica, crea una sola `Connection`, la pasa a cada model y llama a
`db.commit()` (o `db.rollback()` ante un error).

### Autenticación

JWT almacenado en una cookie `httponly`. Contraseñas con Argon2. Todas las
rutas salvo `/auth/login` dependen de la verificación del token
(`src/utilities/jwt_required.py`).

---

## Módulo de visión (`src/ml/`)

```text
Cámara ELP AR0234 (1920x1080, 90 fps)
   │
   ▼
tracker.py        Detección YOLO + ByteTrack (ID único y persistente por grano)
   │
   ▼
Streaming MJPEG   La interfaz web muestra el video anotado en tiempo real
   │
   ▼
classifier.py     Al cerrar el lote: defectos equivalentes y grado SCA (1-5)
   │
   ▼
Arduino           Acciona el actuador físico de separación
```

- Los pesos YOLO se cargan **una sola vez** al iniciar y quedan en memoria.
- El tracker corre en un hilo en segundo plano; las rutas consultan el último
  frame y el conteo sin bloquearse.
- La tabla de defectos equivalentes debe coincidir con el estándar SCA oficial
  de Line Coffee Marañón.
