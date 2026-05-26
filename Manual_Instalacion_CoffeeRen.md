# Manual de Instalación - CoffeeRen

**Versión:** 2.0  
**Fecha de actualización:** 26 de mayo de 2026  
**Público objetivo:** Técnicos de desarrollo, administradores de sistemas  
**Tiempo estimado:** 60-90 minutos

---

## Tabla de Contenidos

1. [Introducción](#introducción)
2. [Checklist Preinstalación](#checklist-preinstalación)
3. [Instalación de PostgreSQL](#instalación-de-postgresql)
4. [Instalación de Python y Entorno Virtual](#instalación-de-python-y-entorno-virtual)
5. [Descarga y Configuración del Proyecto](#descarga-y-configuración-del-proyecto)
6. [Instalación de Dependencias Python](#instalación-de-dependencias-python)
7. [Configuración de la Base de Datos](#configuración-de-la-base-de-datos)
8. [Configuración del Proyecto CoffeeRen](#configuración-del-proyecto-coffeeren)
9. [Instalación del Firmware Arduino](#instalación-del-firmware-arduino)
10. [Configuración de Tailwind CSS](#configuración-de-tailwind-css)
11. [Ejecución y Verificación](#ejecución-y-verificación)
12. [Solución de Problemas](#solución-de-problemas)
13. [Próximos Pasos](#próximos-pasos)

---

## Introducción

CoffeeRen es un sistema web integral de clasificación automática de café verde desarrollado para la **Cooperativa Agraria Line Coffee Marañón** (Lonya Grande, Amazonas, Perú). El sistema integra:

- **Aplicación Web:** Backend en FastAPI + Frontend con Jinja2 templates
- **Base de Datos:** PostgreSQL para almacenamiento de datos
- **Hardware:** Arduino Uno que controla banda transportadora, celda de carga y servo motor
- **Visión Artificial:** Cámara ELP AR0234 para detección de defectos en tiempo real

Este manual proporciona instrucciones paso a paso para instalar todos los componentes desde cero, sin asumir experiencia previa con ninguna de estas tecnologías.

### Estructura del Manual

Cada sección incluye:
- **Comandos exactos** que puede copiar y pegar
- **Capturas de concepto** de qué esperar en cada paso
- **Verificaciones** para confirmar que cada paso funcionó
- **Alternativas** para diferentes sistemas operativos

---

## Checklist Preinstalación

Antes de comenzar, verifique que tiene:

- [ ] Conexión a internet estable (descargará ~500 MB)
- [ ] Acceso de administrador en su computadora
- [ ] Al menos 15 GB de espacio libre en disco
- [ ] Cable USB tipo A-B (para Arduino, si planea usar hardware)
- [ ] Un editor de texto (Notepad, VS Code, o similar)

### Información a Preparar

Antes de instalar, tenga a mano:

1. **Contraseña de PostgreSQL:** Cree una contraseña segura
   - Ejemplo: `Cafe2026!Seguro`
   - Anótela en un lugar seguro

2. **Clave Secreta JWT:** Genere una cadena aleatoria
   - Longitud mínima: 32 caracteres
   - Puede usar: https://www.random.org/strings/

3. **Puerto PostgreSQL:** Normalmente `5432` (verifique que no esté en uso)

4. **Ubicación del Proyecto:** Decida dónde clonar el repositorio
   - Recomendado: `C:\Proyectos\` (Windows) o `~/proyectos/` (Linux/Mac)

---

## Instalación de PostgreSQL

### Windows (Pasos Detallados)

#### Paso 1: Descargar PostgreSQL

1. Abra un navegador web
2. Visite: https://www.postgresql.org/download/windows/
3. Haga clic en el botón **"Download the installer"**
4. Seleccione la versión **15 o 16** (no use versiones más antiguas)
5. Elija **Windows x86-64** si su computadora es de 64 bits (lo más común)
6. Haga clic en **"Download"**
7. Guarde el archivo en su carpeta de Descargas

**Verificación:** El archivo descargado debe llamarse algo como `postgresql-16.0-1-windows-x64.exe`

#### Paso 2: Ejecutar el instalador

1. Abra la carpeta de Descargas
2. Haga doble clic en el archivo `postgresql-16.0-1-windows-x64.exe`
3. Si Windows solicita confirmación, haga clic en **"Sí"**
4. Se abrirá el asistente de instalación

#### Paso 3: Configurar la instalación

El asistente mostrará varias pantallas. Configure cada una así:

**Pantalla 1: Welcome**
- Haga clic en **"Next"**

**Pantalla 2: Installation Directory**
- Deje la ruta predeterminada: `C:\Program Files\PostgreSQL\16`
- Haga clic en **"Next"**

**Pantalla 3: Select Components**
- Mantenga seleccionadas todas las opciones (están bien así)
- Haga clic en **"Next"**

**Pantalla 4: Data Directory**
- Deje la ruta predeterminada: `C:\Program Files\PostgreSQL\16\data`
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
psql (PostgreSQL) 16.0
```

Si ve un error "psql: command not found", verifique que agregó PostgreSQL al PATH:

1. Presione `Win + X` y seleccione "Símbolo del sistema (Administrador)"
2. Ejecute:
```cmd
setx PATH "%PATH%;C:\Program Files\PostgreSQL\16\bin"
```
3. Cierre y abra un nuevo símbolo del sistema
4. Intente nuevamente: `psql --version`

---

### Linux (Ubuntu/Debian)

Abra una terminal (Ctrl+Alt+T) y ejecute:

```bash
# Actualizar lista de paquetes
sudo apt update

# Instalar PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Iniciar el servicio
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Verificar que funciona
psql --version
```

Si la instalación es exitosa, verá la versión de PostgreSQL.

---

### macOS

Opción 1: **Usando Homebrew** (recomendado):

```bash
# Instalar Homebrew si no lo tiene
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Instalar PostgreSQL
brew install postgresql

# Iniciar el servicio
brew services start postgresql

# Verificar
psql --version
```

Opción 2: **Usando el instalador visual:**

1. Visite: https://www.postgresql.org/download/macosx/
2. Descargue **PostgreSQL.app**
3. Arrastre la aplicación a la carpeta **Applications**
4. Abra PostgreSQL.app desde Applications

---

## Instalación de Python y Entorno Virtual

### Windows

#### Paso 1: Descargar Python 3.11.9

1. Visite: https://www.python.org/downloads/release/python-3119/
2. Scroll down hasta encontrar **"Windows installer (64-bit)"**
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

Ahora está en la carpeta `TesisPrj`. En Windows o Linux/Mac:

### Paso 1: Crear el entorno virtual

**Windows:**
```cmd
python -m venv .venv
.venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv .venv
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
- **FastAPI:** Framework web
- **Uvicorn:** Servidor de aplicaciones
- **psycopg2-binary:** Driver de PostgreSQL
- **PyJWT:** Manejo de tokens de autenticación
- **argon2-cffi:** Hash seguro de contraseñas
- **opencv-python:** Procesamiento de imágenes
- **jinja2:** Motor de plantillas HTML

La instalación puede tomar 2-5 minutos dependiendo de su conexión.

### Verificación

Para confirmar que todo se instaló correctamente:

```bash
pip list
```

Debería ver las librerías listadas arriba. Si alguna falta, repita el paso 3.

---

## Configuración de la Base de Datos

### Paso 1: Crear la base de datos

Abra una terminal o símbolo del sistema e ingrese a psql:

```bash
psql -U postgres
```

Ingrese la contraseña que configuró en la instalación de PostgreSQL.

Verá el prompt `postgres=#`

### Paso 2: Crear la base de datos CoffeeRen

En el prompt de psql, ejecute:

```sql
CREATE DATABASE coffeeren ENCODING 'UTF8' LC_COLLATE 'es_ES.UTF-8' LC_CTYPE 'es_ES.UTF-8';
```

Si obtiene un error sobre "collate", ejecute simplemente:

```sql
CREATE DATABASE coffeeren ENCODING 'UTF8';
```

### Paso 3: Verificar que se creó

```sql
\l
```

Debería ver `coffeeren` en la lista de bases de datos.

### Paso 4: Salir de psql

```sql
\q
```

---

### Paso 5: Cargar el schema (estructura de tablas)

Desde la carpeta raíz del proyecto (`TesisPrj`), en una terminal normal (no psql):

**Windows:**
```cmd
psql -U postgres -d coffeeren -f src/database/script.sql
```

**Linux/macOS:**
```bash
psql -U postgres -d coffeeren -f src/database/script.sql
```

Este comando crea todas las tablas, relaciones y datos iniciales (tipos de usuario, documentos, precios de café, clasificación de defectos, etc.).

### Verificación

Vuelva a entrar en psql y verifique que las tablas existen:

```bash
psql -U postgres -d coffeeren
```

En psql, ejecute:

```sql
\dt
```

Debería listar estas tablas:
- persona
- personal
- tipo_personal
- caficultor
- evaluacion
- detalle_evaluacion
- categoria
- valor_cafe
- tipo_defecto
- tipo_documento
- tipo_caficultor
- tipo_grano
- ubigeo

Si ve todas estas, la base de datos está lista.

```sql
\q
```

---

## Configuración del Proyecto CoffeeRen

### Paso 1: Configurar la variable de entorno SECRET_KEY

Este es el código secreto que firma los tokens de autenticación. Genere uno seguro:

**Windows (PowerShell):**
```powershell
$env:SECRET_KEY = "su-clave-secreta-aleatoria-de-32-caracteres"
```

O genere uno automáticamente:
```powershell
$env:SECRET_KEY = $(python -c "import secrets; print(secrets.token_urlsafe(32))")
```

**Linux/macOS:**
```bash
export SECRET_KEY="su-clave-secreta-aleatoria-de-32-caracteres"
```

O genere uno:
```bash
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
```

### Paso 2: Verificar archivo de configuración

Abra `src/config.py` en su editor:

```python
DB_NAME = "coffeeren"
DB_USER = "postgres"
DB_PASSWORD = "la_contraseña_que_uso_en_postgres"
DB_HOST = "localhost"
DB_PORT = "5432"
```

Verifique que **DB_PASSWORD** coincide con la contraseña que estableció en PostgreSQL.

Guarde los cambios.

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

Si planea usar los sensores físicos y la banda transportadora, siga estos pasos:

### Paso 1: Descargar Arduino IDE

1. Visite: https://www.arduino.cc/en/software
2. Descargue **Arduino IDE 2.0 o superior**
3. Instale siguiendo los pasos del instalador

### Paso 2: Conectar la placa Arduino

1. Conecte la placa Arduino Uno a su computadora con un cable USB
2. Espere a que Windows detecte el dispositivo (verá un mensaje)

### Paso 3: Instalar el soporte para Arduino Uno

1. Abra Arduino IDE
2. Vaya a **Herramientas > Placa > Gestor de tarjetas**
3. Busque "Arduino AVR Boards"
4. Haga clic en **"Instalar"**
5. Espere a que finalice

### Paso 4: Cargar el firmware CoffeeRen

1. En Arduino IDE, vaya a **Archivo > Abrir**
2. Navegue a la carpeta: `TesisPrj/arduino/logica_hardware/`
3. Abra el archivo `.ino` (archivo del sketch)
4. En la barra de herramientas, configure:
   - **Placa:** Arduino Uno
   - **Puerto:** COM3 o COM4 (el que vea en su sistema)
   - **Velocidad:** 115200

5. Haga clic en el botón **"Cargar"** (flecha hacia arriba)
6. Esperará a que compile y cargue

Cuando vea el mensaje "Subida completada", el firmware está instalado en Arduino.

### Paso 5: Verificar comunicación (opcional)

1. En Arduino IDE, vaya a **Herramientas > Monitor Serial**
2. Configure la velocidad a **9600 baud**
3. Presione el botón **RESET** en la placa Arduino
4. Debería ver mensajes de inicialización en la consola

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

Esta terminal compilará los estilos CSS y se quedará monitorando cambios. Déjela abierta mientras desarrolla.

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
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Verá algo como:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

**No cierre esta terminal.** Es el servidor ejecutándose.

### Paso 3: Acceder a la aplicación

Abra un navegador web y vaya a:
```
http://localhost:8000
```

Debería ver la página de inicio de CoffeeRen con todos los estilos cargados correctamente.

### Verificación 1: Página de inicio

- Verifique que ve el logo de CoffeeRen
- Verifique que los colores y tipografía se ven bien
- Verifique que el menú de navegación está visible

### Verificación 2: Login

1. Haga clic en el menú o vaya directamente a: `http://localhost:8000/auth/login`
2. Intente iniciar sesión con:
   - **Usuario:** admin
   - **Contraseña:** (la que fue generada en el script.sql)

Si accede al dashboard principal, la base de datos está funcionando.

### Verificación 3: Base de datos

Para confirmar que se están guardando datos:

1. Abra una terminal diferente
2. Ejecute:
```bash
psql -U postgres -d coffeeren
```

3. Ejecute:
```sql
SELECT COUNT(*) FROM persona;
```

Debería mostrar un número mayor a 0 (cantidad de personas registradas).

4. Salga:
```sql
\q
```

---

## Solución de Problemas

### Error: "psql: command not found"

**Problema:** PostgreSQL no está en la variable PATH

**Solución Windows:**
1. Presione `Win + X`, seleccione "Símbolo del sistema (Administrador)"
2. Ejecute:
```cmd
setx PATH "%PATH%;C:\Program Files\PostgreSQL\16\bin"
```
3. Cierre y abra una nueva terminal
4. Intente: `psql --version`

**Solución Linux:**
```bash
sudo apt reinstall postgresql
```

---

### Error: "FATAL: Ident authentication failed"

**Problema:** PostgreSQL rechaza la contraseña

**Solución:**
1. Encuentre el archivo `pg_hba.conf`:
   - Windows: `C:\Program Files\PostgreSQL\16\data\pg_hba.conf`
   - Linux: `/etc/postgresql/16/main/pg_hba.conf`

2. Abra el archivo con un editor
3. Busque la línea que dice: `local   all   all   peer`
4. Cámbiela a: `local   all   all   md5`
5. Reinicie PostgreSQL:
   - Windows: Servicios > PostgreSQL > Reiniciar
   - Linux: `sudo systemctl restart postgresql`

6. Intente nuevamente

---

### Error: "database 'coffeeren' does not exist"

**Problema:** La base de datos no fue creada

**Solución:**
```bash
psql -U postgres -c "CREATE DATABASE coffeeren ENCODING 'UTF8';"
psql -U postgres -d coffeeren -f src/database/script.sql
```

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

### Error: "ModuleNotFoundError: No module named 'fastapi'"

**Problema:** Las dependencias no se instalaron

**Solución:**
1. Verifique que el entorno virtual está activo (debe ver `(.venv)`)
2. Ejecute:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

3. Verifique:
```bash
pip list | grep fastapi
```

---

### Página sin estilos CSS (se ve fea)

**Problema:** Tailwind CSS no se compiló

**Solución:**
1. Verifique que compiló correctamente:
```bash
ls -la src/static/css/tailwind.css
```

2. Si no existe, compile manualmente:
   - Windows: `.\tailwindcss-windows-x64.exe -i src\static\css\input.css -o src\static\css\tailwind.css`
   - Linux: `./tailwindcss-linux-x64 -i src/static/css/input.css -o src/static/css/tailwind.css`

3. Recargue la página en el navegador (Ctrl+F5)

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

### Error: "Secret key must be set"

**Problema:** No configuró la variable de entorno SECRET_KEY

**Solución:**

**Windows:**
```powershell
$env:SECRET_KEY = "una-clave-aleatoria-de-32-caracteres"
```

**Linux/macOS:**
```bash
export SECRET_KEY="una-clave-aleatoria-de-32-caracteres"
```

Luego inicie el servidor nuevamente.

---

## Próximos Pasos

Una vez que la instalación está completa y funcional, realice las siguientes actividades para validar el sistema y prepararlo para la operación en la Cooperativa Agraria Line Coffee Marañón:

### 1. Explorar la Aplicación
- Visite todas las páginas principales
- Verifique que los menús funcionan
- Pruebe el formulario de inicio de sesión
- Valide que los estilos CSS se cargan correctamente

### 2. Registrar Datos de Prueba
- Cree un nuevo caficultor en `/nuevo-caficultor` (simule un socio de la cooperativa)
- Registre una evaluación de muestra en `/registro` con datos reales
- Verifique que los datos se guardan en la base de datos
- Genere reportes y códigos EVA

### 3. Pruebas del Hardware (si tiene Arduino)
- Conecte la placa Arduino a la banda transportadora
- Ejecute pruebas de comunicación: envíe comandos desde la terminal
- Verifique que los sensores responden correctamente
- Realice pruebas de carga con muestras de café real

### 4. Capacitación de Operarios
- Invite a operarios de la Cooperativa Agraria Line Coffee Marañón
- Realice sesiones de capacitación en el sistema (30 minutos mínimo)
- Valide que comprenden el flujo de clasificación
- Solicite retroalimentación sobre la usabilidad

### 5. Leer la Documentación
- Revise el **Manual de Usuario - CoffeeRen** para entender la operación
- Revise el **CLAUDE.md** para entender la arquitectura técnica del código
- Consulte los documentos de análisis de requerimientos para contexto

### 6. Validación de Datos
- Verifique que las clasificaciones del sistema coinciden con el criterio manual
- Valide que los cálculos de rendimiento y pago son precisos
- Genere reportes comparativos con el método anterior

### 7. Despliegue en Producción (cuando esté listo)
- Configure un servidor dedicado o VPS para la Cooperativa
- Obtenga un nombre de dominio apropiado
- Implemente certificados SSL/TLS para conexiones seguras
- Configure Nginx como proxy inverso
- Implemente copias de seguridad automáticas de la base de datos
- Establezca un plan de mantenimiento periódico

---

**Fin del Manual de Instalación**

Este manual fue desarrollado para la **Cooperativa Agraria Line Coffee Marañón** como parte del proyecto de tesis "Clasificación Automática de Café Verde Mediante Visión Artificial". Para soporte técnico adicional o consultas sobre la instalación, contacte al equipo de desarrollo de la Universidad Católica Santo Toribio de Mogrovejo (USAT).
