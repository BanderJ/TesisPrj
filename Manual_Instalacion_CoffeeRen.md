# Manual de Instalación - CoffeeRen

**Versión:** 3.0
**Fecha de actualización:** 9 de julio de 2026
**Público objetivo:** Técnicos de desarrollo, administradores de sistemas
**Tiempo estimado:** 90-120 minutos

---

## Tabla de Contenidos

1. [Introducción](#introducción)
2. [Checklist Preinstalación](#checklist-preinstalación)
3. [Instalación de PostgreSQL 18](#instalación-de-postgresql-18)
4. [Instalación de Python y Entorno Virtual](#instalación-de-python-y-entorno-virtual)
5. [Descarga y Configuración del Proyecto](#descarga-y-configuración-del-proyecto)
6. [Instalación de Dependencias Python](#instalación-de-dependencias-python)
7. [Descarga de los Modelos YOLO](#descarga-de-los-modelos-yolo)
8. [Configuración de la Base de Datos](#configuración-de-la-base-de-datos)
9. [Configuración del Proyecto CoffeeRen](#configuración-del-proyecto-coffeeren)
10. [Instalación del Firmware Arduino](#instalación-del-firmware-arduino)
11. [Conexión de la Cámara](#conexión-de-la-cámara)
12. [Configuración de Tailwind CSS](#configuración-de-tailwind-css)
13. [Ejecución y Verificación](#ejecución-y-verificación)
14. [Solución de Problemas](#solución-de-problemas)
15. [Próximos Pasos](#próximos-pasos)

---

## Introducción

CoffeeRen es un sistema web integral de clasificación automática de café verde desarrollado para la **Cooperativa Agraria Line Coffee Marañón** (Lonya Grande, Amazonas, Perú). El sistema integra:

- **Aplicación Web:** Backend en FastAPI + Frontend con Jinja2 templates
- **Base de Datos:** PostgreSQL 18 para almacenamiento de datos
- **Visión Artificial:** Modelo YOLO (ONNX) + ByteTrack para detección y conteo de granos defectuosos en tiempo real, con cámara ELP AR0234 Global Shutter
- **Hardware:** Arduino Uno que controla la faja transportadora, la celda de carga (balanza) y el servo motor de separación

Este manual proporciona instrucciones paso a paso para instalar todos los componentes desde cero, sin asumir experiencia previa con ninguna de estas tecnologías.

### Estructura del Manual

Cada sección incluye:
- **Comandos exactos** que puede copiar y pegar
- **Verificaciones** para confirmar que cada paso funcionó
- **Alternativas** para diferentes sistemas operativos

---

## Checklist Preinstalación

Antes de comenzar, verifique que tiene:

- [ ] Conexión a internet estable (descargará **~3 GB**, principalmente PyTorch y las librerías de visión artificial)
- [ ] Acceso de administrador en su computadora
- [ ] Al menos **20 GB** de espacio libre en disco
- [ ] Cable USB tipo A-B (para Arduino, si planea usar hardware)
- [ ] Cámara ELP AR0234 con cable USB (si planea usar el monitoreo en vivo)
- [ ] Un editor de texto (Notepad, VS Code, o similar)
- [ ] Acceso a la carpeta de Google Drive del proyecto (para descargar los pesos del modelo YOLO)

### Hardware recomendado

| Componente | Mínimo | Recomendado |
|---|---|---|
| CPU | 4 núcleos | 8 núcleos |
| RAM | 8 GB | 16 GB |
| GPU | No requerida (inferencia en CPU) | NVIDIA con CUDA (ej. GTX 1050 o superior) |
| Disco | 20 GB libres | SSD |

> El sistema funciona en CPU gracias a los modelos exportados a ONNX. Una GPU NVIDIA solo mejora los FPS del monitoreo.

### Información a Preparar

Antes de instalar, tenga a mano:

1. **Contraseña de PostgreSQL:** Cree una contraseña segura
   - Ejemplo: `Cafe2026!Seguro`
   - Anótela en un lugar seguro

2. **Clave Secreta JWT:** Genere una cadena aleatoria
   - Longitud mínima: 32 caracteres
   - Puede generarla con Python (se indica más adelante)

3. **Puerto PostgreSQL:** Normalmente `5432` (verifique que no esté en uso)

4. **Puerto serial del Arduino:** En Windows suele ser `COM3`–`COM6` (el sistema usa `COM5` por defecto)

5. **Ubicación del Proyecto:** Decida dónde clonar el repositorio
   - Recomendado: `C:\Proyectos\` (Windows) o `~/proyectos/` (Linux/Mac)

---

## Instalación de PostgreSQL 18

> ⚠️ **IMPORTANTE:** El esquema de la base de datos usa la función nativa `uuidv7()`, disponible **solo desde PostgreSQL 18**. No instale versiones anteriores (15, 16 o 17): la carga del script fallará con el error `function uuidv7() does not exist`.

### Windows (Pasos Detallados)

#### Paso 1: Descargar PostgreSQL

1. Abra un navegador web
2. Visite: https://www.postgresql.org/download/windows/
3. Haga clic en el botón **"Download the installer"**
4. Seleccione la versión **18**
5. Elija **Windows x86-64** si su computadora es de 64 bits (lo más común)
6. Haga clic en **"Download"**
7. Guarde el archivo en su carpeta de Descargas

**Verificación:** El archivo descargado debe llamarse algo como `postgresql-18.x-x-windows-x64.exe`

#### Paso 2: Ejecutar el instalador

1. Abra la carpeta de Descargas
2. Haga doble clic en el archivo `postgresql-18.x-x-windows-x64.exe`
3. Si Windows solicita confirmación, haga clic en **"Sí"**
4. Se abrirá el asistente de instalación

#### Paso 3: Configurar la instalación

El asistente mostrará varias pantallas. Configure cada una así:

**Pantalla 1: Welcome**
- Haga clic en **"Next"**

**Pantalla 2: Installation Directory**
- Deje la ruta predeterminada: `C:\Program Files\PostgreSQL\18`
- Haga clic en **"Next"**

**Pantalla 3: Select Components**
- Mantenga seleccionadas todas las opciones (están bien así)
- Haga clic en **"Next"**

**Pantalla 4: Data Directory**
- Deje la ruta predeterminada: `C:\Program Files\PostgreSQL\18\data`
- Haga clic en **"Next"**

**Pantalla 5: Password**
- Ingrese la contraseña que preparó (ej: `Cafe2026!Seguro`)
- Escriba la misma contraseña en "Confirm password"
- **Anote esta contraseña: la necesitará en pasos posteriores**
- Haga clic en **"Next"**

**Pantalla 6: Port**
- Deje el puerto predeterminado: `5432`
- Haga clic en **"Next"**

**Pantalla 7: Locale**
- Seleccione **"Spanish, Spain"** o **"English, United States"** según su idioma
- Haga clic en **"Next"**

**Pantalla 8: Ready to Install**
- Revise que todo esté correcto
- Haga clic en **"Install"**
- Espere de 2 a 5 minutos a que se complete la instalación

**Pantalla 9: Finishing Setup**
- Desmarque la casilla "Stack Builder" (no lo necesitamos)
- Haga clic en **"Finish"**

#### Paso 4: Verificar que PostgreSQL funciona

Abra el **Símbolo del sistema** (busque "cmd" en el botón Inicio):

```cmd
psql --version
```

Debería ver algo como:
```
psql (PostgreSQL) 18.0
```

Si ve un error "psql: command not found", agregue PostgreSQL al PATH:

1. Presione `Win + X` y seleccione "Símbolo del sistema (Administrador)"
2. Ejecute:
```cmd
setx PATH "%PATH%;C:\Program Files\PostgreSQL\18\bin"
```
3. Cierre y abra un nuevo símbolo del sistema
4. Intente nuevamente: `psql --version`

---

### Linux (Ubuntu/Debian)

PostgreSQL 18 se instala desde el repositorio oficial PGDG (los repositorios de Ubuntu/Debian traen versiones anteriores):

```bash
# Agregar el repositorio oficial de PostgreSQL
sudo apt install -y postgresql-common
sudo /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh

# Instalar PostgreSQL 18
sudo apt install postgresql-18 postgresql-contrib -y

# Iniciar el servicio
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Verificar que funciona
psql --version
```

---

### macOS

Usando Homebrew:

```bash
# Instalar Homebrew si no lo tiene
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Instalar PostgreSQL 18
brew install postgresql@18

# Iniciar el servicio
brew services start postgresql@18

# Verificar
psql --version
```

---

## Instalación de Python y Entorno Virtual

El proyecto usa **Python 3.11.9**.

### Windows

#### Paso 1: Descargar Python 3.11.9

1. Visite: https://www.python.org/downloads/release/python-3119/
2. Baje hasta encontrar **"Windows installer (64-bit)"**
3. Haga clic para descargar
4. Guarde el archivo en su carpeta de Descargas

#### Paso 2: Ejecutar el instalador de Python

1. Haga doble clic en `python-3.11.9-amd64.exe`
2. **IMPORTANTE:** En la primera pantalla, marque la casilla **"Add Python 3.11 to PATH"**
3. Haga clic en **"Install Now"**
4. Espere a que finalice (1-2 minutos)
5. Cuando vea "Setup was successful", cierre el instalador

#### Paso 3: Verificar instalación de Python

Abra el Símbolo del sistema:

```cmd
python --version
```

Debería ver:
```
Python 3.11.9
```

Si obtiene un error, es porque no marcó "Add Python 3.11 to PATH". Desinstale y vuelva a instalar marcando esa casilla.

---

### Linux (Ubuntu/Debian)

```bash
# Verificar si Python 3.11 está disponible
python3.11 --version

# Si no está instalado:
sudo apt install python3.11 python3.11-venv python3.11-dev -y

# Verificar
python3.11 --version
```

---

### macOS

```bash
# Si usa Homebrew
brew install python@3.11

# Verificar
python3.11 --version
```

---

## Descarga y Configuración del Proyecto

### Opción A: Usando Git (recomendado para desarrolladores)

#### Paso 1: Instalar Git

**Windows:**
1. Visite: https://git-scm.com/download/win
2. Descargue e instale con las opciones predeterminadas

**Linux:**
```bash
sudo apt install git -y
```

**macOS:**
```bash
brew install git
```

#### Paso 2: Clonar el repositorio

Abra una terminal en la carpeta donde quiere el proyecto:

```bash
cd C:\Proyectos

git clone https://github.com/BanderJ/TesisPrj.git
cd TesisPrj
```

---

### Opción B: Descargar ZIP (más simple)

1. Visite el repositorio del proyecto
2. Haga clic en **"Code"** > **"Download ZIP"**
3. Extraiga el archivo ZIP en su carpeta de proyectos
4. Abra la carpeta extraída en una terminal

---

## Instalación de Dependencias Python

Ahora está en la carpeta `TesisPrj`.

### Paso 1: Crear el entorno virtual

**Windows:**
```cmd
python -m venv .venv
.venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

Después de ejecutar esto, verá `(.venv)` al inicio de su línea de comandos. Esto indica que el entorno virtual está activo.

### Paso 2: Actualizar pip

```bash
python -m pip install --upgrade pip
```

### Paso 3: Instalar todas las dependencias

```bash
pip install -r requirements.txt
```

Este paso descargará e instalará:

| Grupo | Librerías | Para qué |
|---|---|---|
| Framework web | `fastapi`, `uvicorn`, `python-multipart`, `pydantic` | Backend y validación |
| Frontend | `jinja2` | Plantillas HTML |
| Base de datos | `psycopg2` | Driver de PostgreSQL |
| Seguridad | `PyJWT`, `argon2-cffi` | Tokens de sesión y hash de contraseñas |
| Visión artificial | `ultralytics`, `torch`, `torchvision` | YOLO + ByteTrack |
| Video | `opencv-python-headless`, `numpy`, `pillow` | Captura de cámara y streaming MJPEG |
| Inferencia ONNX | `onnx`, `onnxruntime`, `onnxslim` | Ejecución de los modelos `best.onnx` |
| Hardware | `pyserial` | Comunicación serial con Arduino |

⏱️ **La instalación puede tomar de 10 a 30 minutos** dependiendo de su conexión — PyTorch y las librerías de visión pesan varios GB.

> **Nota (GPU NVIDIA opcional):** el `torch` de `requirements.txt` funciona en CPU. Si su equipo tiene GPU NVIDIA y quiere acelerar la inferencia, instale la variante CUDA siguiendo https://pytorch.org/get-started/locally/ (el código detecta CUDA automáticamente; no requiere cambios).

### Verificación

Para confirmar que todo se instaló correctamente:

```bash
pip list
```

Debería ver las librerías listadas arriba. Verificación rápida de las críticas:

```bash
python -c "import fastapi, psycopg2, cv2, ultralytics, onnxruntime, serial; print('OK')"
```

Si imprime `OK`, todo está instalado.

---

## Descarga de los Modelos YOLO

> ⚠️ **PASO OBLIGATORIO.** Los pesos del modelo de visión artificial **no están en el repositorio** (son archivos grandes). Sin ellos, **la aplicación no arranca**: al iniciar mostrará `FileNotFoundError: Modelo 'yolov26n_2cls' no encontrado`.

### Paso 1: Obtener los archivos

Descargue de la carpeta de **Google Drive del proyecto** (solicite acceso al equipo de desarrollo) los archivos del modelo activo:

- `best.onnx` (≈ 9.4 MB) — modelo principal, se usa en producción
- `best.pt` — respaldo (se usa solo si no existe el `.onnx`)

### Paso 2: Colocarlos en la carpeta correcta

Copie ambos archivos a:

```
TesisPrj/src/ml/models/yolov26n_2cls/
```

La carpeta ya contiene un archivo `constants.py` (clases, colores y equivalencias del modelo) — no lo borre ni lo modifique.

### Verificación

**Windows:**
```cmd
dir src\ml\models\yolov26n_2cls
```

**Linux/macOS:**
```bash
ls src/ml/models/yolov26n_2cls
```

Debe listar al menos: `best.onnx`, `constants.py` (y opcionalmente `best.pt`).

---

## Configuración de la Base de Datos

> El nombre de la base de datos debe ser **`tesis_prj`** — es el nombre configurado en `src/config.py`.

### Paso 1: Entrar a psql

Abra una terminal o símbolo del sistema e ingrese a psql:

```bash
psql -U postgres
```

Ingrese la contraseña que configuró en la instalación de PostgreSQL.

Verá el prompt `postgres=#`

### Paso 2: Crear la base de datos

En el prompt de psql, ejecute:

```sql
CREATE DATABASE tesis_prj ENCODING 'UTF8';
```

### Paso 3: Verificar que se creó

```sql
\l
```

Debería ver `tesis_prj` en la lista de bases de datos.

### Paso 4: Salir de psql

```sql
\q
```

---

### Paso 5: Cargar el schema (estructura de tablas)

Desde la carpeta raíz del proyecto (`TesisPrj`), en una terminal normal (no psql):

```bash
psql -U postgres -d tesis_prj -f src/database/script.sql
```

Este comando crea todas las tablas, relaciones y datos iniciales: roles de personal, tipos de documento, tipos de grano, categorías (grados), tipos de defecto, el catálogo completo de ubigeos del Perú, la cooperativa Line Coffee Marañón y usuarios de prueba.

> Nota: las primeras líneas del script intentan eliminar tablas previas (`DROP ... CASCADE`). En una base de datos recién creada verá advertencias de que esas tablas no existen — **es normal, ignórelas**.

### Verificación

Vuelva a entrar en psql y verifique que las tablas existen:

```bash
psql -U postgres -d tesis_prj
```

En psql, ejecute:

```sql
\dt
```

Debería listar estas 15 tablas:
- auditoria
- caficultor
- categoria
- cooperativa
- detalle_evaluacion
- evaluacion
- persona
- personal
- tipo_caficultor
- tipo_defecto
- tipo_documento
- tipo_grano
- tipo_personal
- ubigeo
- valor_cafe

Si ve todas estas, la base de datos está lista.

```sql
\q
```

### Usuarios iniciales creados por el script

El script crea tres usuarios de prueba (uno por rol):

| Usuario | Rol |
|---|---|
| `admin` | Administrador |
| `evaluador1` | Evaluador |
| `jbecerrac` | Gerente |

La contraseña de estos usuarios la proporciona el equipo de desarrollo. En producción, cámbielas desde **Perfil → Gestión de usuarios** después del primer inicio de sesión.

---

## Configuración del Proyecto CoffeeRen

### Paso 1: Ajustar las credenciales de la base de datos

Abra `src/config.py` en su editor y verifique la clase `Config`:

```python
USER = 'postgres'
PASSWORD = 'su_contraseña_de_postgres'   # ← cámbiela por la suya
HOST = 'localhost'
PORT = '5432'
DATABASE = 'tesis_prj'
```

Actualice **PASSWORD** con la contraseña que estableció al instalar PostgreSQL y guarde los cambios. (Existe un `src/config-example.py` de referencia.)

### Paso 2: Crear el archivo `.env`

En la **raíz del proyecto** (`TesisPrj/`), cree un archivo llamado `.env` (con punto inicial, sin extensión). El proyecto lo carga automáticamente al arrancar — no necesita configurar variables de entorno en el sistema.

Contenido mínimo:

```env
# Clave que firma los tokens de sesión (JWT) — obligatoria
SECRET_KEY=su-clave-secreta-aleatoria-de-32-caracteres

# Token de la API Factiliza para consulta de DNI en RENIEC — opcional
# (sin él, el autocompletado por DNI no funciona; el registro manual sí)
API_FACTILIZA=su_token_de_factiliza
```

Para generar una SECRET_KEY segura automáticamente:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copie el resultado como valor de `SECRET_KEY`.

#### Variables opcionales de hardware

Estas variables tienen valores por defecto razonables; agréguelas al `.env` solo si necesita cambiarlas:

```env
# Puerto serial del Arduino (por defecto: COM5)
ARDUINO_PORT=COM5

# Velocidad de comunicación serial (por defecto: 9600)
ARDUINO_BAUDRATE=9600

# Velocidad PWM de la faja transportadora (por defecto: 150)
# DEBE coincidir con la constante VELOCIDAD del firmware Arduino
FAJA_VELOCIDAD_PWM=150

# Calibración del servo separador — NO cambiar sin pruebas en banco.
# SERVO_DELAY_S se calcula automáticamente a partir de FAJA_VELOCIDAD_PWM;
# defínalo aquí solo si midió un valor distinto en pruebas físicas.
# SERVO_DELAY_S=0.5
# SERVO_HOLD_S=0.3
```

### Paso 3: Descargar Tailwind CSS CLI

Visite: https://github.com/tailwindlabs/tailwindcss/releases

Descargue el archivo para su sistema:

| Sistema | Archivo a Descargar |
|---------|------------------|
| Windows 64-bit | `tailwindcss-windows-x64.exe` |
| Linux 64-bit | `tailwindcss-linux-x64` |
| macOS Intel | `tailwindcss-macos-x64` |
| macOS Apple Silicon | `tailwindcss-macos-arm64` |

Coloque el archivo descargado en la **raíz del proyecto** (`TesisPrj/`)

**En Linux/macOS, otorgue permisos:**
```bash
chmod +x tailwindcss-linux-x64
```

---

## Instalación del Firmware Arduino

Si planea usar la faja transportadora, la balanza y el servo separador, siga estos pasos. (La aplicación web funciona sin el Arduino conectado, pero el monitoreo físico no.)

### Paso 1: Descargar Arduino IDE

1. Visite: https://www.arduino.cc/en/software
2. Descargue **Arduino IDE 2.0 o superior**
3. Instale siguiendo los pasos del instalador

### Paso 2: Conectar la placa Arduino

1. Conecte la placa Arduino Uno a su computadora con un cable USB
2. Espere a que Windows detecte el dispositivo (verá un mensaje)
3. Anote el puerto asignado (ej. `COM5`): puede verlo en el **Administrador de dispositivos → Puertos (COM y LPT)**

### Paso 3: Instalar el soporte para Arduino Uno

1. Abra Arduino IDE
2. Vaya a **Herramientas > Placa > Gestor de tarjetas**
3. Busque "Arduino AVR Boards"
4. Haga clic en **"Instalar"**
5. Espere a que finalice

### Paso 4: Cargar el firmware CoffeeRen

1. En Arduino IDE, vaya a **Archivo > Abrir**
2. Navegue a la carpeta: `TesisPrj/arduino/logica_hardware/`
3. Abra el archivo `logica_hardware.ino`
4. En la barra de herramientas, configure:
   - **Placa:** Arduino Uno
   - **Puerto:** el que anotó en el Paso 2 (ej. COM5)

5. Haga clic en el botón **"Cargar"** (flecha hacia la derecha)
6. Espere a que compile y cargue

Cuando vea el mensaje "Subida completada", el firmware está instalado en Arduino.

> **Importante:** la constante `VELOCIDAD` (PWM de la faja) dentro de `logica_hardware.ino` debe coincidir con `FAJA_VELOCIDAD_PWM` del `.env` (por defecto 150). Si cambia una, cambie la otra: de ella depende el tiempo de viaje del grano de la cámara al servo.

### Paso 5: Verificar comunicación (opcional)

1. En Arduino IDE, vaya a **Herramientas > Monitor Serial**
2. Configure la velocidad a **9600 baud** (la misma que usa el sistema)
3. Presione el botón **RESET** en la placa Arduino
4. Debería ver mensajes de inicialización en la consola

El protocolo que usa el sistema es por comandos de texto: `ON` / `OFF` (faja), `SERVO:DEFECTO` / `SERVO:BUENO` (separador), `PESO:` (balanza) y `LISTO:` (confirmaciones).

> En `TesisPrj/arduino/test_motor/` hay un sketch auxiliar (`test_motor.ino`) para probar el motor de la faja de forma aislada, sin el firmware completo.

### Paso 6: Configurar el puerto en el `.env`

Si el puerto de su Arduino **no** es `COM5`, agregue al `.env`:

```env
ARDUINO_PORT=COM3
```

(reemplace COM3 por el puerto real). **Cierre el Monitor Serial de Arduino IDE antes de iniciar CoffeeRen** — solo un programa puede usar el puerto a la vez.

---

## Conexión de la Cámara

El monitoreo en vivo usa una cámara **ELP AR0234 Global Shutter** conectada por USB, operando a 1280×720.

1. Conecte la cámara a un puerto **USB 3.0** (preferible) antes de iniciar la aplicación — el sistema pre-conecta la cámara al arrancar
2. Verifique que Windows la detecta: **Administrador de dispositivos → Cámaras**
3. Cierre cualquier otra aplicación que use la cámara (Zoom, OBS, la app Cámara de Windows): solo un programa puede usarla a la vez

> Si la cámara se desconecta durante un monitoreo, el sistema entra en modo de emergencia (detiene la faja) y lo indica en pantalla. Existe además el botón/endpoint "liberar cámara" si quedara bloqueada.

Sin cámara conectada la aplicación web funciona igualmente (registro, reportes, caficultores), pero el monitoreo en vivo mostrará error al iniciarlo.

---

## Configuración de Tailwind CSS

Abra una **segunda terminal** (no cierre la primera) en la carpeta raíz del proyecto:

**Windows:**
```cmd
.\tailwindcss-windows-x64.exe -i src\static\css\input.css -o src\static\css\tailwind.css --watch
```

**Linux/macOS:**
```bash
./tailwindcss-linux-x64 -i src/static/css/input.css -o src/static/css/tailwind.css --watch
```

Esta terminal compilará los estilos CSS y se quedará monitoreando cambios. Déjela abierta mientras desarrolla. (Para un despliegue sin desarrollo, basta ejecutarla una vez sin `--watch`.)

---

## Ejecución y Verificación

### Paso 1: Asegúrese de que el entorno virtual está activo

En su terminal principal, verifique que ve `(.venv)` al inicio de la línea. Si no, active:

**Windows:**
```cmd
.venv\Scripts\activate
```

**Linux/macOS:**
```bash
source .venv/bin/activate
```

### Paso 2: Iniciar el servidor FastAPI

En su terminal principal (no la del Tailwind), ejecute:

```bash
uvicorn src.main:app --reload
```

En el arranque verá mensajes como:
```
Modelo YOLO cargado: yolov26n_2cls (best.onnx, conf=0.5, device=cpu)
Calentando modelo YOLO (CUDA/ONNX)...
Modelo listo.
Application has started successfully!
INFO:     Uvicorn running on http://127.0.0.1:8000
```

- Si dice `device=0` en lugar de `device=cpu`, está usando la GPU NVIDIA.
- **No cierre esta terminal.** Es el servidor ejecutándose.

> Para acceder desde otras computadoras de la red local, use `uvicorn src.main:app --host 0.0.0.0 --port 8000`.

### Paso 3: Acceder a la aplicación

Abra un navegador web y vaya a:
```
http://localhost:8000
```

Como no ha iniciado sesión, será redirigido a la pantalla de login.

### Verificación 1: Login

1. En `http://localhost:8000/auth/login` inicie sesión con:
   - **Usuario:** `admin`
   - **Contraseña:** (la proporcionada por el equipo de desarrollo)

Si accede al dashboard de inicio (KPIs de lotes, defectos y rendimiento), la base de datos y la autenticación funcionan.

### Verificación 2: Páginas principales

Recorra el menú y verifique que cargan sin error:
- `/registro` — registro de muestras
- `/nuevo-caficultor` — registro de caficultores
- `/reporte` — búsqueda de muestras y reportes
- `/valor-cafe` — precios del café
- `/perfil` — perfil y gestión de usuarios

Verifique también que los estilos se ven correctamente (colores, tipografía, menús). Si la página se ve "sin diseño", revise la terminal de Tailwind.

### Verificación 3: Base de datos

Para confirmar que se están guardando datos:

```bash
psql -U postgres -d tesis_prj -c "SELECT COUNT(*) FROM persona;"
```

Debería mostrar un número mayor a 0 (personas de prueba creadas por el script).

### Verificación 4: Monitoreo con cámara (si tiene el hardware)

1. Registre precios del café en `/valor-cafe` (sin precios no se puede iniciar una evaluación)
2. Registre una muestra en `/registro` usando el documento de un caficultor de prueba (ej. `99988877`)
3. En la pantalla de monitoreo, inicie la captura: debe ver el video en vivo con los granos detectados (defectos en rojo, sanos en verde) y el conteo subiendo

---

## Solución de Problemas

### Error: "function uuidv7() does not exist" al cargar script.sql

**Problema:** Su versión de PostgreSQL es anterior a la 18 — `uuidv7()` es una función nativa introducida en PostgreSQL 18.

**Solución:** Instale PostgreSQL 18 (ver sección de instalación), cree de nuevo la base `tesis_prj` y vuelva a cargar `src/database/script.sql`.

---

### Error: "psql: command not found"

**Problema:** PostgreSQL no está en la variable PATH

**Solución Windows:**
1. Presione `Win + X`, seleccione "Símbolo del sistema (Administrador)"
2. Ejecute:
```cmd
setx PATH "%PATH%;C:\Program Files\PostgreSQL\18\bin"
```
3. Cierre y abra una nueva terminal
4. Intente: `psql --version`

---

### Error: "FATAL: Ident authentication failed" / contraseña rechazada

**Problema:** PostgreSQL rechaza la contraseña

**Solución:**
1. Encuentre el archivo `pg_hba.conf`:
   - Windows: `C:\Program Files\PostgreSQL\18\data\pg_hba.conf`
   - Linux: `/etc/postgresql/18/main/pg_hba.conf`

2. Abra el archivo con un editor
3. Busque la línea que dice: `local   all   all   peer`
4. Cámbiela a: `local   all   all   md5`
5. Reinicie PostgreSQL:
   - Windows: Servicios > PostgreSQL > Reiniciar
   - Linux: `sudo systemctl restart postgresql`

6. Intente nuevamente

---

### Error: "database 'tesis_prj' does not exist"

**Problema:** La base de datos no fue creada, o el nombre en `src/config.py` no coincide

**Solución:**
```bash
psql -U postgres -c "CREATE DATABASE tesis_prj ENCODING 'UTF8';"
psql -U postgres -d tesis_prj -f src/database/script.sql
```

Verifique además que `DATABASE = 'tesis_prj'` en `src/config.py`.

---

### Error al arrancar: "Modelo 'yolov26n_2cls' no encontrado"

**Problema:** No descargó los pesos del modelo YOLO (no están en el repositorio)

**Solución:** Descargue `best.onnx` (y opcionalmente `best.pt`) de la carpeta de Google Drive del proyecto y colóquelos en `src/ml/models/yolov26n_2cls/`. Reinicie el servidor.

---

### Error: "Port 8000 is already in use"

**Problema:** Otro programa está usando el puerto

**Solución Windows:**
```cmd
netstat -ano | findstr :8000
taskkill /PID <numero> /F
```

**Solución Linux/macOS:**
```bash
lsof -i :8000
kill -9 <PID>
```

O use un puerto diferente:
```bash
uvicorn src.main:app --reload --port 8001
```

---

### Error: "ModuleNotFoundError: No module named 'fastapi'" (u otro módulo)

**Problema:** Las dependencias no se instalaron, o el entorno virtual no está activo

**Solución:**
1. Verifique que el entorno virtual está activo (debe ver `(.venv)`)
2. Ejecute:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

3. Verifique:
```bash
pip list
```

---

### Página sin estilos CSS (se ve "fea")

**Problema:** Tailwind CSS no se compiló

**Solución:**
1. Verifique que el archivo existe: `src/static/css/tailwind.css`
2. Si no existe, compile manualmente:
   - Windows: `.\tailwindcss-windows-x64.exe -i src\static\css\input.css -o src\static\css\tailwind.css`
   - Linux: `./tailwindcss-linux-x64 -i src/static/css/input.css -o src/static/css/tailwind.css`
3. Recargue la página en el navegador (Ctrl+F5)

---

### La cámara no da imagen / "No se pudo iniciar la cámara"

**Problema:** La cámara no está conectada, está en uso por otro programa, o quedó bloqueada

**Solución:**
1. Conecte la cámara **antes** de iniciar el servidor (se pre-conecta al arrancar)
2. Cierre Zoom, OBS, la app Cámara de Windows o cualquier programa que la use
3. Use el botón de "liberar cámara" del sistema (o reinicie el servidor)
4. Pruebe otro puerto USB (preferible USB 3.0)

---

### El Arduino no responde / no separa granos

**Problema:** Puerto serial incorrecto u ocupado

**Solución:**
1. Verifique el puerto real en Administrador de dispositivos → Puertos (COM y LPT)
2. Configure `ARDUINO_PORT=COMx` en el `.env` con ese puerto
3. Cierre el Monitor Serial de Arduino IDE (solo un programa puede usar el puerto)
4. Verifique que `ARDUINO_BAUDRATE=9600` (o que no esté definido — 9600 es el default)
5. Reinicie el servidor

---

### Arduino IDE no detecta el puerto

**Problema:** Driver USB no instalado

**Solución Windows:**
1. Desconecte el Arduino
2. Descargue el driver CH340: https://github.com/nodemcu/ch340/releases
3. Instale el driver
4. Reinicie
5. Reconecte el Arduino

**Solución Linux:**
```bash
sudo usermod -a -G dialout $USER
```
(Cierre sesión y vuelva a iniciar)

---

### No puedo iniciar una evaluación: "No hay rangos de precios de café registrados"

**Problema:** No es un error de instalación — el sistema exige precios del día antes de iniciar un monitoreo, porque sin ellos no puede calcular el pago al finalizar.

**Solución:** Inicie sesión como Gerente o Administrador y registre los rangos de precios en `/valor-cafe`.

---

## Próximos Pasos

Una vez que la instalación está completa y funcional, realice las siguientes actividades para validar el sistema y prepararlo para la operación en la Cooperativa Agraria Line Coffee Marañón:

### 1. Explorar la Aplicación
- Visite todas las páginas principales
- Verifique que los menús funcionan
- Pruebe el formulario de inicio de sesión con los tres roles
- Valide que los estilos CSS se cargan correctamente

### 2. Registrar Datos de Prueba
- Registre los precios del café del día en `/valor-cafe`
- Cree un nuevo caficultor en `/nuevo-caficultor` (simule un socio de la cooperativa)
- Registre una evaluación de muestra en `/registro` con datos reales
- Complete el flujo: registro → monitoreo → análisis → código EVA
- Busque la evaluación por su código en `/reporte`

### 3. Pruebas del Hardware (si tiene Arduino)
- Pruebe el motor de la faja con `arduino/test_motor/test_motor.ino`
- Cargue el firmware completo y verifique la comunicación (faja ON/OFF, balanza, servo)
- Verifique con granos reales que el servo separa los defectuosos en el momento correcto
- Si ajusta la velocidad de la faja, actualice `FAJA_VELOCIDAD_PWM` en el `.env` y `VELOCIDAD` en el firmware

### 4. Capacitación de Operarios
- Invite a operarios de la Cooperativa Agraria Line Coffee Marañón
- Realice sesiones de capacitación en el sistema (30 minutos mínimo)
- Valide que comprenden el flujo de clasificación
- Solicite retroalimentación sobre la usabilidad

### 5. Leer la Documentación
- Revise el **Manual de Usuario - CoffeeRen** para entender la operación
- Revise **docs/DOCUMENTACION_SISTEMA.md** para la visión general del sistema
- Revise el **CLAUDE.md** para entender la arquitectura técnica del código

### 6. Validación de Datos
- Verifique que las clasificaciones del sistema coinciden con el criterio manual del evaluador
- Valide que los cálculos de rendimiento y pago son precisos
- Genere reportes comparativos con el método anterior

### 7. Despliegue en Producción (cuando esté listo)
- Configure un servidor dedicado para la Cooperativa
- Cambie las contraseñas de los usuarios de prueba y la SECRET_KEY
- Implemente certificados SSL/TLS para conexiones seguras
- Configure Nginx como proxy inverso
- Implemente copias de seguridad automáticas de la base de datos
- Establezca un plan de mantenimiento periódico

---

**Fin del Manual de Instalación**

Este manual fue desarrollado para la **Cooperativa Agraria Line Coffee Marañón** como parte del proyecto de tesis "Clasificación Automática de Café Verde Mediante Visión Artificial". Para soporte técnico adicional o consultas sobre la instalación, contacte al equipo de desarrollo de la Universidad Católica Santo Toribio de Mogrovejo (USAT).
