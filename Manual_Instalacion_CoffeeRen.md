# Manual de Instalación - CoffeeRen

**Versión:** 1.0  
**Fecha de actualización:** 26 de mayo de 2026  
**Público objetivo:** Técnicos de desarrollo, administradores de sistemas

---

## Tabla de Contenidos

1. [Introducción](#introducción)
2. [Requisitos Previos](#requisitos-previos)
3. [Instalación de PostgreSQL](#instalación-de-postgresql)
4. [Instalación del Entorno Python](#instalación-del-entorno-python)
5. [Instalación de Dependencias](#instalación-de-dependencias)
6. [Configuración de la Base de Datos](#configuración-de-la-base-de-datos)
7. [Configuración del Proyecto](#configuración-del-proyecto)
8. [Instalación del Firmware Arduino](#instalación-del-firmware-arduino)
9. [Compilación de Tailwind CSS](#compilación-de-tailwind-css)
10. [Ejecución de la Aplicación](#ejecución-de-la-aplicación)
11. [Verificación de la Instalación](#verificación-de-la-instalación)
12. [Solución de Problemas Comunes](#solución-de-problemas-comunes)
13. [Próximos Pasos](#próximos-pasos)

---

## Introducción

CoffeeRen es un sistema web integral de clasificación y gestión de muestras de café para cooperativas. El sistema se compone de tres capas principales:

- **Backend:** FastAPI con servidor Uvicorn
- **Base de datos:** PostgreSQL 12 o superior
- **Frontend:** Jinja2 templates con CSS/JavaScript vanilla
- **Hardware:** Arduino Uno controlando banda transportadora, sensor de peso y cámara

Este manual guía el proceso de instalación completo desde cero, incluyendo todos los componentes: base de datos, aplicación web y firmware del hardware.

**Tiempo estimado de instalación:** 45-90 minutos (según velocidad de conexión y experiencia previa)

---

## Requisitos Previos

### Hardware Recomendado

- Procesador: Intel Core i5 o equivalente
- RAM: Mínimo 8 GB
- Almacenamiento: 10 GB disponibles
- Conexión a internet: Requerida para descargas

### Software Obligatorio

| Software | Versión | Propósito | Descargar |
|----------|---------|----------|-----------|
| Python | 3.11.9 o superior | Runtime de la aplicación | https://www.python.org/downloads/ |
| PostgreSQL | 12 o superior | Base de datos | https://www.postgresql.org/download/ |
| Git | Última | Control de versiones (opcional) | https://git-scm.com/ |
| Arduino IDE | 2.0 o superior | Carga de firmware | https://www.arduino.cc/en/software |

### Software Opcional

- Visual Studio Code: Editor de código
- Postman o Insomnia: Pruebas de API
- pgAdmin: Herramienta visual para PostgreSQL

### Información para Configuración

Antes de comenzar, prepare la siguiente información:

- Nombre de usuario para PostgreSQL (por defecto: postgres)
- Contraseña para usuario PostgreSQL
- Puerto de PostgreSQL (por defecto: 5432)
- Nombre de la base de datos (por defecto: coffeeren)
- Clave secreta JWT (genere una cadena aleatoria segura)

---

## Instalación de PostgreSQL

### Windows

#### Paso 1: Descargar PostgreSQL

1. Visite https://www.postgresql.org/download/windows/
2. Descargue la versión más reciente del instalador (versión 15 o superior recomendada)
3. Guarde el archivo .exe en una ubicación accesible

#### Paso 2: Ejecutar el instalador

1. Haga doble clic en el archivo descargado
2. Si se le solicita, confirme que desea ejecutar el instalador
3. Siga el asistente de instalación

#### Paso 3: Configuración inicial

En la pantalla "Setup - PostgreSQL":
- **Installation Directory:** Deje la ruta predeterminada: `C:\Program Files\PostgreSQL\15`
- **Data Directory:** Deje la ruta predeterminada: `C:\Program Files\PostgreSQL\15\data`
- Haga clic en "Next"

En la pantalla "Password":
- Ingrese y confirme una contraseña segura para el usuario `postgres`
- **Anote esta contraseña: la necesitará para configurar la base de datos**
- Haga clic en "Next"

En la pantalla "Port":
- Deje el puerto predeterminado: `5432`
- Haga clic en "Next"

En la pantalla "Locale":
- Seleccione el idioma/región (use "Spanish, Spain" o "English, United States")
- Haga clic en "Next"

En la pantalla "Ready to Install":
- Revise la configuración
- Haga clic en "Install"
- Espere a que finalice la instalación (puede tomar 2-5 minutos)

#### Paso 4: Completar la instalación

En la pantalla final:
- Desmarque "Stack Builder" (no es necesario)
- Haga clic en "Finish"

#### Paso 5: Verificar instalación en Windows

Abra el símbolo del sistema (cmd.exe) e ingrese:

```cmd
psql --version
```

Debería ver una salida similar a:
```
psql (PostgreSQL) 15.2
```

Si obtiene un error "psql: command not found", agregue PostgreSQL al PATH:

1. Presione `Win + X` y seleccione "Símbolo del sistema (Administrador)"
2. Ejecute:
```cmd
setx PATH "%PATH%;C:\Program Files\PostgreSQL\15\bin"
```
3. Cierre y abra una nueva ventana de símbolo del sistema
4. Intente nuevamente con `psql --version`

---

### Linux (Ubuntu/Debian)

#### Paso 1: Actualizar repositorios

Abra una terminal y ejecute:

```bash
sudo apt update
sudo apt upgrade -y
```

#### Paso 2: Instalar PostgreSQL

```bash
sudo apt install postgresql postgresql-contrib -y
```

#### Paso 3: Iniciar el servicio

```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### Paso 4: Verificar instalación

```bash
psql --version
```

#### Paso 5: Establecer contraseña para usuario postgres

```bash
sudo -u postgres psql
```

En la consola psql:
```sql
ALTER USER postgres WITH PASSWORD 'tu_contraseña_segura';
\q
```

---

### macOS

#### Paso 1: Instalación con Homebrew (recomendado)

```bash
brew install postgresql
```

#### Paso 2: Iniciar el servicio

```bash
brew services start postgresql
```

#### Paso 3: Verificar instalación

```bash
psql --version
```

#### Paso 4: Crear usuario (si es necesario)

```bash
createuser -P postgres
```

---

## Instalación del Entorno Python

### Windows

#### Paso 1: Descargar Python 3.11.9

1. Visite https://www.python.org/downloads/release/python-3119/
2. Descargue el instalador "Windows installer (64-bit)"
3. Guarde el archivo en una ubicación accesible

#### Paso 2: Ejecutar el instalador

1. Haga doble clic en el archivo descargado
2. **IMPORTANTE:** En la primera pantalla, marque la casilla "Add Python 3.11 to PATH"
3. Haga clic en "Install Now"
4. Espere a que finalice la instalación

#### Paso 3: Verificar instalación

Abra el símbolo del sistema (cmd.exe):

```cmd
python --version
```

Debería ver:
```
Python 3.11.9
```

Si obtiene un error, verifique que marcó "Add Python 3.11 to PATH" durante la instalación.

### Linux y macOS

```bash
python3 --version
```

Si Python 3.11.9 no está disponible, use el gestor de versiones de su distribución:

**Linux (Ubuntu):**
```bash
sudo apt install python3.11 python3.11-venv python3.11-dev
```

**macOS:**
```bash
brew install python@3.11
```

---

## Instalación de Dependencias

### Paso 1: Clonar o descargar el repositorio

Navegue a una carpeta de trabajo y descargue el proyecto:

```bash
git clone <url-repositorio> TesisPrj
cd TesisPrj
```

O descargue el archivo ZIP desde el repositorio.

### Paso 2: Crear el entorno virtual

En Windows:
```cmd
python -m venv .venv
.venv\Scripts\activate
```

En Linux/macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Debería ver el prefijo `(.venv)` en su línea de comandos.

### Paso 3: Actualizar pip

```bash
python -m pip install --upgrade pip
```

### Paso 4: Instalar dependencias del proyecto

```bash
pip install -r requirements.txt
```

Este comando instala todas las librerías necesarias:
- FastAPI: Framework web
- Uvicorn: Servidor ASGI
- psycopg2-binary: Driver de PostgreSQL
- PyJWT: Manejo de tokens JWT
- python-argon2: Hash de contraseñas
- opencv-python: Procesamiento de imágenes
- Jinja2: Motor de templates (incluido en FastAPI)

La instalación puede tomar 3-5 minutos.

#### Verificación de instalación

```bash
pip list
```

Debería ver listadas las librerías mencionadas arriba.

---

## Configuración de la Base de Datos

### Paso 1: Crear la base de datos

Abra la consola psql:

En Windows:
```cmd
psql -U postgres
```

En Linux/macOS:
```bash
sudo -u postgres psql
```

Ingrese la contraseña de PostgreSQL cuando se solicite.

En la consola psql, cree la base de datos:
```sql
CREATE DATABASE coffeeren ENCODING 'UTF8' LC_COLLATE 'es_ES.UTF-8' LC_CTYPE 'es_ES.UTF-8';
```

Verificar que se creó correctamente:
```sql
\l
```

Debería ver `coffeeren` en la lista.

Salir de psql:
```sql
\q
```

### Paso 2: Cargar el schema de la base de datos

Desde la carpeta raíz del proyecto (TesisPrj), ejecute:

En Windows:
```cmd
psql -U postgres -d coffeeren -f src/database/script.sql
```

En Linux/macOS:
```bash
psql -U postgres -d coffeeren -f src/database/script.sql
```

Esto creará todas las tablas, relaciones e inserciones de datos iniciales (tipos de personal, documentos, café, defectos, etc.).

**Nota:** Si obtiene un error sobre encoding, ejecute primero:
```sql
CREATE DATABASE coffeeren ENCODING 'UTF8';
```

### Paso 3: Verificar que se crearon las tablas

Conéctese a la base de datos y verifique:

```bash
psql -U postgres -d coffeeren
```

En la consola psql:
```sql
\dt
```

Debería listar las tablas:
- persona
- personal
- tipo_personal
- caficultor
- evaluacion
- detalle_evaluacion
- categoria
- valor_cafe
- etc.

Salir:
```sql
\q
```

---

## Configuración del Proyecto

### Paso 1: Configurar variables de entorno

En Windows, abra una terminal de PowerShell:
```powershell
$env:SECRET_KEY = "tu-clave-secreta-aleatoria-aqui"
```

En Linux/macOS:
```bash
export SECRET_KEY="tu-clave-secreta-aleatoria-aqui"
```

**Nota:** Genere una clave segura. Puede usar:
```python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Paso 2: Verificar y ajustar configuración de base de datos

Abra el archivo `src/config.py`:

```bash
code src/config.py
```

Verifique que los parámetros coincidan con su instalación de PostgreSQL:

```python
DB_NAME = "coffeeren"
DB_USER = "postgres"
DB_PASSWORD = "tu_contraseña_de_postgres"
DB_HOST = "localhost"
DB_PORT = "5432"
```

Guarde los cambios.

### Paso 3: Instalar Tailwind CSS CLI (para desarrollo)

Descargue la herramienta Tailwind CSS para su sistema operativo desde:
https://github.com/tailwindlabs/tailwindcss/releases

**Windows:**
- Descargue `tailwindcss-windows-x64.exe`
- Colóquelo en la raíz del proyecto: `TesisPrj/tailwindcss-windows-x64.exe`

**Linux:**
- Descargue `tailwindcss-linux-x64`
- Colóquelo en la raíz del proyecto
- Otorgue permisos de ejecución: `chmod +x tailwindcss-linux-x64`

**macOS:**
- Descargue `tailwindcss-macos-arm64` (Apple Silicon) o `tailwindcss-macos-x64` (Intel)
- Colóquelo en la raíz del proyecto

---

## Instalación del Firmware Arduino

### Paso 1: Descargar Arduino IDE

1. Visite https://www.arduino.cc/en/software
2. Descargue Arduino IDE 2.0 o superior
3. Instale siguiendo el asistente para su sistema operativo

### Paso 2: Instalar el soporte para Arduino Uno

1. Abra Arduino IDE
2. Vaya a **Herramientas > Placa > Gestor de tarjetas**
3. Busque "Arduino AVR Boards"
4. Haga clic en "Instalar"

### Paso 3: Cargar el firmware CoffeeRen

1. Conecte la placa Arduino Uno a su computadora mediante cable USB
2. En Arduino IDE, vaya a **Archivo > Abrir**
3. Navegue a `TesisPrj/arduino/logica_hardware/` y abra el archivo del sketch
4. En **Herramientas**, configure:
   - **Placa:** Arduino Uno
   - **Puerto:** COM3 (o el puerto que aparezca en su sistema)
   - **Velocidad de subida:** 115200

5. Haga clic en el botón "Subir" (flecha hacia arriba)
6. Espere a que aparezca el mensaje "Subida completada" en la consola inferior

### Paso 4: Verificar comunicación

1. Abra el Monitor Serial (Herramientas > Monitor Serial)
2. Configure la velocidad a 9600 baud
3. Presione el botón RESET en la placa Arduino
4. Debería ver un mensaje de inicialización

---

## Compilación de Tailwind CSS

### Modo desarrollo (con observador automático)

Abra una terminal en la carpeta raíz del proyecto y ejecute:

**Windows:**
```cmd
.\tailwindcss-windows-x64.exe -i src\static\css\input.css -o src\static\css\tailwind.css --watch
```

**Linux/macOS:**
```bash
./tailwindcss-linux-x64 -i src/static/css/input.css -o src/static/css/tailwind.css --watch
```

Este proceso monitorea cambios en `input.css` y recompila automáticamente.

### Compilación única (producción)

```bash
# Windows
.\tailwindcss-windows-x64.exe -i src\static\css\input.css -o src\static\css\tailwind.css --minify

# Linux/macOS
./tailwindcss-linux-x64 -i src/static/css/input.css -o src/static/css/tailwind.css --minify
```

---

## Ejecución de la Aplicación

### Paso 1: Activar el entorno virtual

Si no está activado:

**Windows:**
```cmd
.venv\Scripts\activate
```

**Linux/macOS:**
```bash
source .venv/bin/activate
```

### Paso 2: Iniciar el servidor FastAPI

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Debería ver:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Started reloader process
INFO:     Application startup complete
```

### Paso 3: Acceder a la aplicación

Abra un navegador web y vaya a:
```
http://localhost:8000
```

Debería ver la página de inicio de CoffeeRen.

### Pasos alternativo: Ejecución sin recarga automática

Para producción, ejecute sin la opción `--reload`:

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

---

## Verificación de la Instalación

### Verificación 1: Acceso a la aplicación web

1. En navegador, vaya a `http://localhost:8000`
2. Debería ver la página de inicio de CoffeeRen
3. Verifique que todos los estilos se cargan correctamente (colores, tipografía)

### Verificación 2: Conexión a la base de datos

1. Vaya a `http://localhost:8000/auth/login`
2. Intente iniciar sesión con:
   - Usuario: `admin`
   - Contraseña: (la que generó en la inserción de datos)

Si accede al dashboard, la conexión a la base de datos es correcta.

### Verificación 3: Endpoints de API

Pruebe un endpoint de API usando curl o Postman:

```bash
curl -X GET http://localhost:8000/perfil/usuarios \
  -H "Authorization: Bearer <token_jwt>"
```

Debería recibir una respuesta JSON con la lista de usuarios.

### Verificación 4: Compilación de CSS

Verifique que el archivo `src/static/css/tailwind.css` existe y contiene CSS compilado:

```bash
ls -la src/static/css/tailwind.css
```

Debería mostrar un tamaño mayor a 100 KB.

### Verificación 5: Arduino (si está disponible)

1. Conecte la placa Arduino
2. En el Monitor Serial de Arduino IDE (9600 baud), debería ver mensajes de inicialización
3. Verifique que los sensores responden (envíe comando "PF" para probar celda de carga)

---

## Solución de Problemas Comunes

### Error: "psql: command not found"

**Causa:** PostgreSQL no está en la variable PATH del sistema

**Solución:**
- Windows: Agregue `C:\Program Files\PostgreSQL\15\bin` a las variables de entorno
- Linux: Instale nuevamente con `sudo apt install postgresql`
- macOS: Ejecute `brew install postgresql`

---

### Error: "FATAL: Ident authentication failed for user 'postgres'"

**Causa:** PostgreSQL está rechazando la contraseña

**Solución:**

1. Abra `pg_hba.conf` ubicado en:
   - Windows: `C:\Program Files\PostgreSQL\15\data\pg_hba.conf`
   - Linux: `/etc/postgresql/15/main/pg_hba.conf`
   - macOS: `/usr/local/var/postgres/pg_hba.conf`

2. Busque la línea con "local" e "peer"

3. Cámbiela de:
   ```
   local   all             all                                     peer
   ```
   A:
   ```
   local   all             all                                     md5
   ```

4. Reinicie PostgreSQL:
   - Windows: Services > PostgreSQL (reiniciar servicio)
   - Linux: `sudo systemctl restart postgresql`
   - macOS: `brew services restart postgresql`

5. Intente nuevamente con la contraseña

---

### Error: "psycopg2.OperationalError: FATAL: database 'coffeeren' does not exist"

**Causa:** La base de datos no fue creada o no se cargó el schema

**Solución:**

1. Verifique que la base de datos existe:
   ```bash
   psql -U postgres -l | grep coffeeren
   ```

2. Si no existe, créela:
   ```bash
   psql -U postgres -c "CREATE DATABASE coffeeren ENCODING 'UTF8';"
   ```

3. Cargue el schema nuevamente:
   ```bash
   psql -U postgres -d coffeeren -f src/database/script.sql
   ```

---

### Error: "Port 8000 is already in use"

**Causa:** Otro proceso está usando el puerto 8000

**Solución:**

**Windows:**
```cmd
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Linux/macOS:**
```bash
lsof -i :8000
kill -9 <PID>
```

O use un puerto diferente:
```bash
uvicorn src.main:app --reload --port 8001
```

---

### Error: "ModuleNotFoundError: No module named 'fastapi'"

**Causa:** Las dependencias no fueron instaladas correctamente

**Solución:**

1. Verifique que el entorno virtual está activado (debe ver `(.venv)` en el prompt)
2. Reinstale las dependencias:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. Verifique:
   ```bash
   pip list | grep -i fastapi
   ```

---

### Error: "Tailwind CSS: cannot find input.css"

**Causa:** El archivo `src/static/css/input.css` no existe

**Solución:**

1. Verifique que el archivo existe:
   ```bash
   ls -la src/static/css/input.css
   ```

2. Si no existe, créelo con contenido básico:
   ```css
   @tailwind base;
   @tailwind components;
   @tailwind utilities;
   ```

3. Intente la compilación nuevamente

---

### Error: "Arduino IDE no reconoce el puerto COM"

**Causa:** Driver USB del Arduino no está instalado

**Solución:**

**Windows:**
1. Desconecte el Arduino
2. Descargue e instale el driver CH340 desde: https://github.com/nodemcu/ch340/releases
3. Reinicie la computadora
4. Conecte el Arduino nuevamente

**Linux:**
1. Instale reglas udev:
   ```bash
   sudo apt install arduino
   ```

2. Agregue su usuario al grupo dialout:
   ```bash
   sudo usermod -a -G dialout $USER
   ```

3. Reinicie la sesión

---

### Página web carga pero sin estilos CSS

**Causa:** Tailwind CSS no fue compilado o está desactualizado

**Solución:**

1. Verifique que `src/static/css/tailwind.css` existe
2. Recompile manualmente:
   ```bash
   # Windows
   .\tailwindcss-windows-x64.exe -i src\static\css\input.css -o src\static\css\tailwind.css

   # Linux/macOS
   ./tailwindcss-linux-x64 -i src/static/css/input.css -o src/static/css/tailwind.css
   ```

3. Recargue la página en el navegador (Ctrl+F5)

---

### Error al iniciar sesión: "Credenciales incorrectas"

**Causa:** La contraseña hash en la base de datos no coincide

**Solución:**

1. Genere un nuevo hash de contraseña:
   ```python
   from src.utilities.security import hash_password
   print(hash_password("nueva_contraseña"))
   ```

2. Actualice la base de datos:
   ```sql
   UPDATE personal SET clave = 'nuevo_hash_aqui' WHERE usuario = 'admin';
   ```

3. Intente iniciar sesión nuevamente

---

### PostgreSQL no inicia después de reiniciar

**Solución:**

**Windows:**
1. Abra Servicios (Services.msc)
2. Busque "PostgreSQL Server"
3. Haga clic derecho > Iniciar

**Linux:**
```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**macOS:**
```bash
brew services start postgresql
```

---

## Próximos Pasos

Una vez completada la instalación:

1. **Crear usuarios:**
   - Visite `/nuevo-caficultor` para registrar caficultores
   - Visite `/perfil` para crear usuarios administrativos

2. **Configurar datos iniciales:**
   - Configure los precios de café en `/valor-cafe`
   - Verifique que los tipos de documentos estén en la base de datos

3. **Pruebas del hardware:**
   - Conecte los sensores Arduino
   - Realice pruebas de comunicación
   - Verifique que la banda transportadora funciona

4. **Capacitación:**
   - Revise el Manual de Usuario - CoffeeRen
   - Pruebe el flujo completo de evaluación

5. **Despliegue (producción):**
   - Genere una clave SECRET_KEY segura
   - Configure un servidor de aplicaciones (Gunicorn/Uvicorn)
   - Use un servidor proxy (Nginx)
   - Implemente certificados SSL/TLS

---

**Fin del Manual de Instalación**

Para soporte técnico o preguntas adicionales, contacte al equipo de desarrollo.
