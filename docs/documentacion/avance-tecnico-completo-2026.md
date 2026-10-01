# Avance Técnico Completo — CoffeeRen 2026

**Proyecto:** Sistema de Visión Artificial para Clasificación de Café Verde  
**Autor:** Anderson Jhomar Baca Chuquimanco  
**Institución:** Universidad Católica Santo Toribio de Mogrovejo (USAT)  
**Empresa colaboradora:** Cooperativa Agraria Line Coffee Marañón  
**Última actualización:** 2026-06-01  
**Metodología:** CRISP-ML(Q) — Sprint 0 completado, Sprint 1 completado, Sprint 2 en curso

---

## 1. Resumen Ejecutivo

CoffeeRen es un sistema completo de clasificación automatizada de granos de café verde defectuoso mediante visión artificial en tiempo real. Combina un backend FastAPI, modelos YOLO para detección de defectos, integración con hardware Arduino para separación física de granos, y una interfaz web basada en Jinja2 + TailwindCSS.

El sistema cubre el flujo completo: registro de caficultores, ingreso de muestras, monitoreo en tiempo real con cámara, detección de defectos con YOLO + ByteTrack, cálculo automático de grado SCA, separación física mediante servo, y generación de reporte de pago al caficultor.

**Estado actual (2026-06-01):**
- Backend completo y funcional
- Dataset Dataset_1 con 3,480 imágenes en 17 clases normalizado
- Modelo YOLOv8n entrenado (mAP50: 0.767) y en producción
- Modelo yolo26n_2cls (binario: defecto/verde) activo en TrackerService
- Integración ML + cámara + Arduino + servo operativa
- Anotación completada con Roboflow (3× augmentación → 8,283 imágenes)

---

## 2. Contexto del Negocio y Problema

### 2.1 Problema identificado

La Cooperativa Agraria Line Coffee Marañón realiza la clasificación de café verde de forma manual. Un operario pasa los granos uno a uno por una bandeja y separa defectuosos visualmente. Este proceso tiene tres problemas:

1. **Lentitud:** Una muestra de 350g puede tomar 30–45 minutos en clasificarse manualmente.
2. **Subjetividad:** Distintos operarios aplican criterios distintos para el mismo defecto.
3. **Fatiga:** Errores aumentan con el tiempo de trabajo.

### 2.2 Solución propuesta

Sistema automatizado que:
- Captura video en tiempo real de granos pasando por una faja transportadora
- Detecta y clasifica 17 tipos de defectos con YOLO + ByteTrack
- Separa granos defectuosos físicamente mediante servo motor
- Calcula automáticamente el grado SCA (1, 2 o 3) y el pago al caficultor

### 2.3 Validación social

Encuestas realizadas a 10+ caficultores de la cooperativa: 80% de disposición favorable al uso del sistema automatizado.

---

## 3. Metodología CRISP-ML(Q) — Estado por Fase

| Fase | Nombre | Estado |
|------|--------|--------|
| 1 | Comprensión del negocio y los datos | Completada |
| 2 | Ingeniería de datos | Completada |
| 3 | Ingeniería de modelos ML | En curso |
| 4 | Garantía de calidad ML | Pendiente |
| 5 | Despliegue | Pendiente |
| 6 | Supervisión y mantenimiento | Pendiente |

### Sprint 0 — Fase 1: Comprensión del negocio (Enero–Abril 2026)
- Identificación de desafíos en la cooperativa
- Validación social con caficultores (80% favorable)
- Definición de criterios de éxito: empresarial, ML y económico
- Recopilación de datos híbrida: datasets públicos (USK-Coffee Kaggle + Roboflow) + dataset propio
- Dataset inicial: ~12,000 imágenes brutas
- Carta de aceptación de la cooperativa para ejecución de tesis

### Sprint 1 — Fase 2: Ingeniería de datos (Abril–Mayo 2026)
- Dataset_1: 3,480 imágenes normalizadas a 640×640 px en 17 clases
- Anotación en Roboflow: bounding boxes por defecto, 3× augmentación
- Dataset final tras augmentación: 8,283 imágenes (88% train / 8% val / 4% test)
- Infraestructura backend completa: FastAPI + PostgreSQL 18

### Sprint 2 — Fase 3: Ingeniería de modelos ML (Mayo–Junio 2026)
- YOLOv8n: entrenado 75 epochs en Google Colab A100, mAP50: 0.767, mAP50-95: 0.757
- yolo26n_2cls: modelo binario simplificado (defecto / verde), actualmente en producción
- YOLO11n: pendiente de entrenamiento
- yolo26n (17 clases): en entrenamiento

---

## 4. Arquitectura del Sistema

### 4.1 Stack tecnológico

| Componente | Tecnología |
|------------|-----------|
| Backend | Python 3.10+, FastAPI |
| Base de datos | PostgreSQL 18 con UUIDv7 |
| ORM | Ninguno — psycopg2 directo |
| Autenticación | JWT + Argon2id, httponly cookie |
| Frontend | Jinja2 templates + TailwindCSS |
| ML — Detección | YOLO (ultralytics) |
| ML — Tracking | ByteTrack |
| Streaming | MJPEG (multipart/x-mixed-replace) |
| Hardware — cámara | ELP AR0234 Global Shutter, 1920×1080, 90fps |
| Hardware — control | Arduino (servo + celda de carga + sensor distancia) |
| Comunicación serial | pyserial, 9600 baud |
| CSS compiler | TailwindCSS standalone |

### 4.2 Arquitectura de capas (Clean Architecture adaptada)

```
Routes (src/routes/)
    ↓ HTTP only — sin lógica de negocio
Services (src/services/)
    ↓ Lógica de negocio — orquesta modelos
Models (src/models/)
    ↓ SQL puro con psycopg2
Schemas (src/schemas/)
    Validación Pydantic de entradas/salidas
```

Reglas no negociables:
- Routes: solo HTTP, ningún SQL directo
- Services: lógica, sin SQL
- Models: solo SQL parametrizado — NUNCA f-strings
- Schemas: toda validación Pydantic aquí

### 4.3 Patrón de transacciones

Cuando un service necesita escribir en múltiples tablas atómicamente:
1. Crea un `Connection()` manualmente
2. Lo pasa a cada método de modelo (`db=db`)
3. Llama `db.commit()` al terminar, `db.rollback()` en excepción
4. `finally: db.close()`

---

## 5. Base de Datos — Esquema Completo

**Motor:** PostgreSQL 18  
**Codificación:** UTF-8  
**Ubicación esquema:** `src/database/script.sql`

### 5.1 Tablas maestras (PK: SERIAL)

| Tabla | Columnas clave | Datos iniciales |
|-------|----------------|-----------------|
| `TIPO_CAFICULTOR` | id, nombre | Socio, Externo |
| `TIPO_DOCUMENTO` | id, nombre | DNI, Pasaporte, Carnet de Extranjería |
| `TIPO_PERSONAL` | id, nombre | Evaluador, Gerente, Administrador |
| `TIPO_DEFECTO` | id, nombre, descripcion | Broca, Cascarilla, Cereza seca, Concha, Hongo, Flotador, Palos, Piedra, Raja, Partido |
| `TIPO_GRANO` | id, nombre, peso_qq | Pergamino (55.20 kg/qq), Pilado (46.00 kg/qq), Coco (85.00 kg/qq) |
| `CATEGORIA` | id, nombre, cantidad_defectos | Grado 1 (≤15), Grado 2 (≤23), Grado 3 (≤30) |
| `UBIGEO` | ubigeo (char 6), departamento, provincia, distrito | Todos los distritos del Perú |

### 5.2 Tablas transaccionales (PK: UUID v7)

#### `PERSONA`
```sql
id uuid DEFAULT uuidv7()
nombre varchar(50), ape_paterno varchar(30), ape_materno varchar(30)
sexo char(1), fecha_nacimiento date
tipo_documento_id int2 FK → TIPO_DOCUMENTO
num_documento varchar(12) UNIQUE
telefono char(9), ubigeo char(6) FK → UBIGEO
estado char(1)  -- 'A' activo, 'I' inactivo
cooperativa_id uuid FK → COOPERATIVA
correo varchar(100)
```

#### `PERSONAL`
```sql
personal_id uuid DEFAULT uuidv7() FK → PERSONA (id)
tipo_personal_id int2 FK → TIPO_PERSONAL  -- 1=Evaluador, 2=Gerente, 3=Admin
usuario varchar(30) UNIQUE
clave varchar(255)  -- Argon2id hash
estado char(1)
fecha_registro timestamp
```

#### `CAFICULTOR`
```sql
caficultor_id uuid DEFAULT uuidv7() FK → PERSONA (id)
tipo_caficultor_id int2 FK → TIPO_CAFICULTOR
fecha_registro timestamp
cacerio varchar(50)
```

#### `COOPERATIVA`
```sql
id uuid DEFAULT uuidv7()
nombre varchar(100), codigo varchar(20)
direccion varchar(255) UNIQUE
telefono char(9), correo varchar(255)
descripcion varchar(255)
imagen_url varchar(255)
estado char(1)
fecha_registro timestamp
ubigeo_id char(6) FK → UBIGEO
```

#### `EVALUACION`
```sql
id uuid DEFAULT uuidv7()
codigo char(10)  -- NULL mientras activa, EVA0000001... al finalizar
personal_id uuid FK → PERSONAL
caficultor_id uuid FK → CAFICULTOR
tipo_caficultor_id int2 FK → TIPO_CAFICULTOR
valor_cafe_id uuid FK → VALOR_CAFE  -- precio asignado al completar
num_sacos int2
peso_bruto numeric(7,2)  -- kg totales
humedad int2  -- porcentaje
peso_muestra numeric(7,2)  -- gramos de muestra
peso_trillado numeric(7,2)  -- gramos tras trilla
peso_cascara numeric(7,2)  -- calculado: muestra - trillado
peso_cascara_total numeric(7,2)  -- extrapolado a 100%
num_tamiz int2, peso_tamizado numeric(7,2)
peso_bueno numeric(7,2)  -- ingresado desde báscula Arduino
peso_malo numeric(7,2)  -- calculado: trillado - bueno
factor_rendimiento numeric(7,2)  -- bueno/divisor
tara_saco numeric(3,2) = 0.25 kg, tara_total int2
peso_neto int4  -- bruto - tara_total
peso_por_qq numeric(7,2)  -- quintales resultantes (redondeo DOWN)
pago numeric(7,2)  -- peso_por_qq × precio_cafe
fecha timestamp
tipo_grano_id int4 FK → TIPO_GRANO
categoria_id int4 FK → CATEGORIA  -- asignada por total_defectos
total_defectos int4  -- suma de defectos equivalentes SCA
```

#### `VALOR_CAFE`
```sql
id uuid DEFAULT uuidv7()
rango varchar(20)  -- ej: "Especial", "Convencional"
precio float4  -- USD por quintal
fecha timestamp
```

#### `DETALLE_EVALUACION`
```sql
id uuid DEFAULT uuidv7()
cantidad int4
evaluacion_id uuid FK → EVALUACION
tipo_defecto_id int2 FK → TIPO_DEFECTO
```

### 5.3 Clase Connection (`src/database/bd.py`)

```python
class Connection:
    # autocommit=False — transacciones manuales
    # RealDictCursor — resultados como dicts
    
    obtener(query, params)     → list[dict]   # SELECT múltiples
    obtener_uno(query, params) → dict | None  # SELECT uno
    ejecutar(query, params)    → cursor       # INSERT/UPDATE/DELETE
    commit()
    rollback()
    close()
```

---

## 6. Autenticación y Autorización

### 6.1 Flujo de autenticación

1. `POST /auth/login` — recibe usuario y contraseña
2. `auth_service.py` verifica hash Argon2id
3. Genera JWT con payload: `{personal_id, usuario, rol, nombre, exp}`
4. JWT almacenado como cookie httponly: `access_token: "Bearer <token>"`
5. TTL: 7 días

### 6.2 Protección de rutas

Todas las rutas excepto `/auth/login` y APIs públicas requieren `Depends(obtener_usuario_actual)`.

`obtener_usuario_actual()` (`src/utilities/jwt_required.py`):
- Lee la cookie `access_token`
- Decodifica el JWT con `SECRET_KEY`
- Retorna el payload como dict
- Si falla → lanza `RequerirLoginException`

`RequerirLoginException` es capturada por el exception handler global → redirect a `/auth/login`

### 6.3 Roles del sistema

| ID | Nombre | Acceso |
|----|--------|--------|
| 1 | Evaluador | Registro, monitoreo, análisis |
| 2 | Gerente | Todo + gestión de precios de café |
| 3 | Administrador | Todo |

### 6.4 Hashing

Algoritmo: Argon2id (memoria adaptativa, resistente a GPU)  
Implementado en: `src/utilities/security.py`

---

## 7. Módulo Backend — Rutas y Servicios Completos

### 7.1 Rutas de autenticación (`/auth`)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/auth/login` | Página de login (template) |
| POST | `/auth/login` | Autentica, genera JWT cookie, redirige a `/` |
| GET | `/auth/logout` | Elimina cookie, redirige a login |

### 7.2 Evaluaciones (`/evaluacion`)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/evaluacion/registrar` | Crea evaluación sin código (estado activa). Retorna `evaluacion_id` UUID |
| GET | `/evaluacion/{id}/resumen` | Datos completos de la evaluación para análisis |
| GET | `/evaluacion/{id}/estado` | `activa` / `finalizada` / `null` — usado por los guards de página |
| PATCH | `/evaluacion/{id}/completar` | Calcula y guarda: peso_bueno, peso_malo, factor_rendimiento, peso_neto, peso_por_qq, pago, categoría. Genera código EVA correlativo |
| PATCH | `/evaluacion/{id}/finalizar` | Cierra el monitoreo: guarda total de defectos/buenos e incidencias de tapa abierta |
| GET | `/evaluacion/buscar?codigo=EVA...` | Busca evaluación por código EVA |
| GET | `/evaluacion/kpis` | Totales: lotes procesados, defectos acumulados |

**Lógica de cálculo (`completar_evaluacion`):**
```
divisor = peso_muestra / 100
peso_cascara = peso_muestra - peso_trillado
peso_cascara_total = peso_cascara / divisor
factor_rendimiento = peso_bueno / divisor
peso_malo = peso_trillado - peso_bueno
tara_total = num_sacos × 0.25
peso_neto = peso_bruto - tara_total
si humedad > 12%:
    peso_neto_humedad = peso_neto × (humedad-12) / (100-humedad)
peso_por_qq = (peso_neto - peso_neto_humedad) / peso_qq_ref  [ROUND_DOWN]
pago = peso_por_qq × precio_cafe
```

**Código EVA correlativo:** Formato `EVA0000001` hasta `EVA9999999`, se calcula con MAX(CAST(SUBSTRING(codigo FROM 4) AS INTEGER)) + 1.

**Estado de evaluación:**
- `activa` → código NULL, en monitoreo
- `finalizada` → código asignado (EVA...)
- Guard en `/monitoreo/{id}` y `/analisis/{id}` redirigen según estado

### 7.3 Caficultores (`/caficultor`)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/caficultor/listar` | Lista de caficultores registrados |
| GET | `/caficultor/consultar/{num_documento}` | Busca caficultor por documento |
| POST | `/caficultor/registrar` | Alta de caficultor (crea Persona + Caficultor) |
| PATCH | `/caficultor/convertir-socio/{num_documento}` | Cambia tipo_caficultor_id a "Socio" |

**Validaciones de documento:**
- DNI: exactamente 8 dígitos numéricos
- Pasaporte: 8–12 caracteres alfanuméricos
- Carnet de Extranjería: 8–12 caracteres alfanuméricos

La captura de cámara la gestiona `CamaraService` (singleton con hilo dedicado): drena la cámara al máximo FPS del sensor y guarda solo el último frame; si detecta MJPEG passthrough nativo lo usa directamente (sin re-encodear); detecta desconexión tras 10 lecturas fallidas consecutivas. No expone rutas HTTP propias — el frontend consume el video siempre a través de `/video/*` (con procesamiento YOLO).

### 7.4 Video y ML (`/video`, `/lote`)

| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| GET | `/video/stream` | No | MJPEG con anotaciones YOLO en tiempo real |
| POST | `/video/iniciar` | Sí | Inicia TrackerService (cámara + YOLO + ByteTrack) |
| POST | `/video/detener` | Sí | Detiene TrackerService |
| GET | `/video/frame` | No | Último frame como JPEG individual |
| GET | `/video/status` | No | Estado: activo, modelo, conteo, error de cámara |
| GET | `/video/lote/conteo` | Sí | `{conteo: {clase: n}, total_granos, clases_detectadas}` |
| POST | `/video/lote/generar-reporte` | Sí | Reporte SCA: grado, defectos, apto_specialty, detalle |
| POST | `/video/lote/resetear` | Sí | Limpia conteo para nuevo lote |

### 7.5 Arduino (`/arduino`)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/arduino/estado` | Estado serial: listo, distancia, conectado, error |
| GET | `/arduino/peso` | Peso en gramos desde celda de carga |
| POST | `/arduino/motor/iniciar` | Inicia faja (`ON`) |
| POST | `/arduino/motor/detener` | Detiene faja (`OFF`) |

### 7.6 Valor Café (`/valor-cafe`)

| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| GET | `/valor-cafe/historial` | Pública | Precios del día (opcional `fecha`, `rango`) |
| GET | `/valor-cafe/maximo-dia` | Pública | Precio máximo del día (opcional `fecha`) |
| GET | `/valor-cafe/cambios-diarios` | Pública | Máximo por día en un rango de fechas |
| GET | `/valor-cafe/resumen-rangos` | Pública | Último precio vigente por rango |
| PATCH | `/valor-cafe/actualizar-precio` | Gerente/Admin | Registra un nuevo precio para un rango (no borra históricos) |
| DELETE | `/valor-cafe/eliminar-rango` | Gerente/Admin | Elimina los registros de un rango en el día actual |
| POST | `/valor-cafe/crear-bloque` | Gerente/Admin | Alta de varios rangos y precios en una sola operación |

### 7.7 Cooperativa (`/cooperativas`)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/cooperativas/mi-cooperativa` | Cooperativa del usuario autenticado (asigna la de por defecto si no tiene) |
| PATCH | `/cooperativas/{id}` | Actualiza nombre, ubicación, teléfono, correo, descripción, imagen (Gerente/Admin) |
| POST | `/cooperativas/upload-imagen` | Sube el logo y devuelve su URL (Gerente/Admin) |

### 7.8 APIs de catálogos (todas públicas)

- `GET /tipo-documento/listar` → `[{id, nombre}]`
- `GET /tipo-grano/listar` → `[{id, nombre, peso_qq}]` (+ `POST /tipo-grano/crear`, `PATCH /tipo-grano/{id}`, `DELETE /tipo-grano/{id}` para Gerente/Admin)
- `GET /tipo-caficultor/listar` → `[{id, nombre}]`
- `GET /tipo-personal/listar` → `[{id, nombre}]`
- `GET /ubigeo/departamentos` → `[{codigo, nombre}]`
- `GET /ubigeo/provincias?departamento=NN` → `[{codigo, nombre}]`
- `GET /ubigeo/distritos?provincia=NNNN` → `[{codigo, nombre}]`

### 7.9 Perfil y usuarios (`/perfil`)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/perfil/` | Página de perfil del usuario autenticado (template) |
| PATCH | `/perfil/datos-personales` | Actualiza nombre, apellidos, teléfono, correo (reemite el JWT) |
| PATCH | `/perfil/cambiar-contrasena` | Cambia la contraseña propia (requiere clave actual) |
| GET | `/perfil/usuarios` | Lista de usuarios del sistema (Gerente/Admin) |
| GET | `/perfil/usuarios/{id}` | Datos de un usuario (Gerente/Admin) |
| POST | `/perfil/usuarios/crear` | Alta de usuario + Persona (Gerente/Admin) |
| PATCH | `/perfil/usuarios/{id}` | Edita datos del usuario; `clave_nueva` opcional (Gerente/Admin) |
| PATCH | `/perfil/usuarios/{id}/estado` | Activa/desactiva un usuario (Gerente/Admin) |

### 7.10 Validación DNI — RENIEC (`/dni`, `/persona`)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/dni/consultar/{dni}` | Consulta la API externa (Factiliza) para validar un DNI |
| GET | `/persona/consultar/{num_documento}` | Busca una Persona ya registrada en la BD por documento |

### 7.11 Reportes y auditoría

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/reportes` | Catálogo de reportes disponibles (Gerente/Admin) |
| GET | `/reportes/{codigo}` | Reporte completo: columnas + filas + gráfico (Gerente/Admin) |
| GET | `/auditoria` | Registros de auditoría paginados y filtrables (Gerente/Admin) |
| GET | `/auditoria/usuarios` | Usuarios que aparecen en la auditoría (Gerente/Admin) |
| GET | `/auditoria/acciones` | Acciones registrables disponibles (Gerente/Admin) |

---

## 8. Módulo ML — Arquitectura Completa

### 8.1 Visión general del pipeline ML

```
Cámara USB ELP AR0234
    ↓ cv2.VideoCapture (hilo dedicado en CamaraService)
    ↓ JPEG @ 60fps
TrackerService._loop_procesamiento()
    ↓ decodifica JPEG → frame BGR
CoffeeRenTracker.procesar_frame(frame)
    ├─ YOLO.track(source, tracker="bytetrack.yaml", persist=True)
    ├─ Actualiza conteo_ids_confianza por track_id
    ├─ Para IDs nuevos: ServoController.solicitar(lambda)
    └─ Dibuja bounding boxes con label (#ID clase confianza%)
    ↓ JPEG anotado (85% quality)
GET /video/stream → MJPEG streaming (navegador)
GET /video/lote/conteo → JSON por clase
POST /video/lote/generar-reporte → JSON grado SCA
```

### 8.2 `inference.py` — CoffeeRenInference (modo legacy)

Carga modelo YOLO por nombre (`yolov8n`, `yolo26n`, `yolo11n`) desde `src/ml/models/{name}/best.pt`.

**Estado:** Funcional pero no usado en el flujo actual. ByteTrack está integrado directamente en `tracker.py`. Se mantiene para referencia y pruebas aisladas.

**Métodos:**
- `predecir(frame)` → resultado YOLO con bounding boxes
- `dibujar_detecciones(frame, result)` → frame BGR anotado con colores por clase

Carga dinámicamente `constants.py` del modelo usando `importlib`, accediendo a `CLASES`, `COLORES`.

### 8.3 `tracker.py` — CoffeeRenTracker

El núcleo del procesamiento en tiempo real. Recibe frames externos (de CamaraService vía TrackerService) y produce JPEG anotados.

**Algoritmo de conteo sin duplicados:**
- Cada grano detectado recibe un `track_id` único (ByteTrack)
- Por track_id se acumula lista de `(clase, confianza)` a lo largo de todos los frames donde aparece
- Al calcular conteo final, se usa la clase con **mayor confianza acumulada** para ese ID
- Esto evita contar el mismo grano dos veces y reduce errores de clasificación por oclusión parcial

```python
conteo_ids_confianza: dict[int, list[(str, float)]]
# {track_id: [(clase, conf), (clase, conf), ...]}

_calcular_conteo_final() → dict[str, int]
# Para cada track_id: clase = max(detecciones, key=lambda x: x[1])[0]
# Agrupa IDs por clase final → conteo
```

**Integración con ServoController:**
- Cuando aparece un `track_id` nuevo: `servo_controller.solicitar(lambda_clase, equivalencias)`
- El lambda captura el `track_id` y llama `_mejor_clase_para(tid)` cuando el servo lo evalúa
- Esto permite que el servo evalúe la mejor clase DESPUÉS de acumular más detecciones

**Configuración:**
```python
CAMARA_WIDTH  = 1280
CAMARA_HEIGHT = 720
CAMARA_FPS    = 60
imgsz         = 1280  # mayor resolución para granos pequeños
conf          = 0.50  # umbral de confianza (definido en TrackerService)
```

**Estadísticas en pantalla:**
```
"Granos: {total} | FPS: {fps:.1f} | Detecciones: {n}"
```
Renderizadas en amarillo (0, 255, 255) en esquina superior izquierda.

### 8.4 `classifier.py` — Generador de reportes SCA

Calcula defectos equivalentes según la norma SCA (Specialty Coffee Association).

**Tabla de grados (3 niveles):**

| Grado | Rango de defectos equivalentes |
|-------|-------------------------------|
| Grado 1 (Specialty) | 0 – 15 |
| Grado 2 | 16 – 23 |
| Grado 3 | 24 – ∞ |

**Función principal:**
```python
generar_reporte(conteo_granos: dict, equivalencias: dict) → dict
# Retorna: {
#   total_granos_analizados, total_defectos,
#   grado, apto_specialty (bool),
#   detalle_por_clase: {clase: {granos, peso_por_grano, defectos_equivalentes}},
#   resumen: str
# }
```

Las equivalencias se cargan del modelo activo (`EQUIVALENCIAS_DEFECTO` en `constants.py`), no están hardcodeadas en `classifier.py`. Esto permite cambiar el modelo sin tocar la lógica de clasificación.

### 8.5 `tracker_service.py` — TrackerService (Orquestador)

Coordina CamaraService, CoffeeRenTracker y classifier. Es el punto de entrada de toda la integración ML desde las rutas HTTP.

**Singleton global:** `tracker_service = TrackerService(model_name="yolov26n_2cls")`

**Flujo `iniciar()`:**
1. Llama `servo_controller.desbloquear()`
2. Llama `camara_service.iniciar()` → abre cámara USB
3. Espera 1 segundo para que la cámara estabilice
4. Verifica `camara_service.esta_disponible()`
5. Arranca `_loop_procesamiento()` en hilo daemon

**`_loop_procesamiento()` (hilo separado):**
- Detecta desconexión: si `!camara_service.esta_disponible()` → llama `_on_camara_desconectada()`
- Obtiene frame JPEG de `camara_service.esperar_frame(timeout=1.0)`
- Decodifica JPEG → frame BGR
- Envía a `tracker.procesar_frame(frame)`
- Guarda frame anotado en `_frame_anotado`
- Log cada 30 frames (~1 seg)

**Manejo de emergencia por desconexión de cámara:**
- `activo = False`
- `_camara_desconectada = True`
- `servo_controller.bloquear()` → congela servo en DEFECTO
- `arduino_serial.enviar_comando("SERVO:DEFECTO")` → posición segura
- Al reiniciar: `servo_controller.desbloquear()` restablece operación

### 8.6 Modelos disponibles

#### `yolov8n` — 17 clases (producción)
- Entrenado: Google Colab A100, transfer learning desde COCO
- Dataset: 8,283 imágenes (3× Roboflow augmentation desde Dataset_1 de 3,480)
- Augmentaciones: flip H/V, rotate ±15°, brightness ±15%, exposure ±5%, blur 0.5px, noise 0.1%
- Split: 88% train / 8% val / 4% test
- Epochs: 75, batch: 16
- Seed: sin seed fijo
- mAP50: **0.767**, mAP50-95: **0.757**, duración: 1.1 horas

#### `yolo26n_2cls` — 2 clases (activo en producción)
Modelo simplificado binario: `defecto` o `verde`.
- `defecto`: equivalencia SCA = 0.83 (promedio ponderado de defectos principales)
- `verde`: equivalencia SCA = 0.0 (grano sano, no suma defectos)

#### `yolo26n` — 17 clases (en entrenamiento)
- Arquitectura más reciente
- Seed: 42, batch: 16
- Estado: en progreso

#### `yolo11n` — 17 clases (pendiente)
- No iniciado aún

### 8.7 Tabla de equivalencias SCA — yolov8n (17 clases)

| Clase | Equivalencia por grano |
|-------|----------------------|
| negro | 1.0 |
| agrio_severo | 1.0 |
| cereza_seca | 1.0 |
| broca_severo | 1.0 |
| agrio_ligero | 1/3 ≈ 0.333 |
| pergamino | 1/5 = 0.20 |
| inmaduro | 1/5 = 0.20 |
| averanado | 1/5 = 0.20 |
| concha | 1/5 = 0.20 |
| partido_maquina | 1/5 = 0.20 |
| partido_mitad | 1/5 = 0.20 |
| cascarilla_cereza_seca | 1/5 = 0.20 |
| cascarilla_pergamino | 1/5 = 0.20 |
| broca_ligero | 1/10 = 0.10 |
| blanco | No catalogado (sin equivalencia) |
| deforme | No catalogado (sin equivalencia) |
| verde | No catalogado (grano sano) |

---

## 9. Hardware e Integración Arduino

### 9.1 Protocolo serial (`src/utilities/arduino_serial.py`)

**Puerto:** COM9 (configurable via .env `ARDUINO_PORT`)  
**Baudrate:** 9600 (configurable via .env `ARDUINO_BAUDRATE`)  
**Timeout:** 1.0 segundos por readline

**Arduino → Backend (lectura continua):**
```
LISTO:15.34       → tapa cerrada, muestra detectada (distancia < umbral)
NO_LISTO:45.21    → sin muestra o tapa abierta
PESO:1234.56      → lectura de celda de carga en gramos (promedio deslizante)
TARE:OK           → confirmación de tara completada
SISTEMA:LISTO     → Arduino inicializado
```

**Backend → Arduino (comandos):**
```
ON               → iniciar faja transportadora
OFF              → detener faja y resetear servo a BUENO
SERVO:BUENO      → servo al canal de granos buenos
SERVO:DEFECTO    → servo al canal de granos defectuosos
TARE             → tarar la báscula
SCALE:<factor>   → actualizar factor de calibración
```

**ArduinoSerial implementa:**
- Hilo lector daemon (`_reader_loop`) que parsea todas las líneas
- Estado cacheado (`EstadoArduino`) actualizado por el hilo
- Reconexión automática: `_asegurar_conexion()` reinicia si el hilo muere
- API no-bloqueante: `obtener_estado()`, `obtener_peso()`, `enviar_comando()`

### 9.2 ServoController (`src/utilities/servo_controller.py`)

Separa la decisión de clasificación (cuándo y qué grano) del momento de actuación del servo.

**Parámetros:**
```python
SERVO_DELAY_S = 0.5  # segundos desde detección hasta que el grano llega al servo
SERVO_HOLD_S  = 0.3  # segundos que el servo permanece en DEFECTO antes de volver a BUENO
```
Ambos configurables via .env.

**Flujo por grano:**
1. `tracker.py` detecta nuevo `track_id` → llama `servo_controller.solicitar(lambda_clase, equivalencias)`
2. El lambda captura el `track_id`; se ejecutará DESPUÉS de `SERVO_DELAY_S` segundos
3. Worker `_worker()` (hilo daemon): revisa cola cada 10ms
4. Cuando `solicitud.ejecutar_en <= ahora`: evalúa `obtener_clase()` (el lambda)
5. Si clase está en `equivalencias` → `SERVO:DEFECTO`, luego espera `SERVO_HOLD_S`, luego `SERVO:BUENO`
6. Si no es defecto → `SERVO:BUENO` directamente

**Modo emergencia:**
- `bloquear()`: descarta cola, el worker no envía SERVO:BUENO, servo queda en DEFECTO
- `desbloquear()`: restaura operación normal
- `limpiar_cola()`: descarta pendientes al resetear lote

### 9.3 CamaraService (`src/services/camara.py`)

Hilo dedicado de captura que drena la cámara al máximo FPS del sensor. No procesa los frames (eso es del tracker).

**Características técnicas:**
- Intenta índices 0 y 1 al iniciar
- Configura `CAP_PROP_BUFFERSIZE = 1` para mínima latencia
- Intenta MJPEG codec (`MJPG`)
- Detecta MJPEG passthrough nativo: si el sensor entrega JPEG directamente, lo usa sin re-encodear
- Si re-encode necesario: JPEG quality 95
- `esperar_frame(timeout)` bloquea con `threading.Event` hasta nuevo frame
- Detecta desconexión: 10 lecturas fallidas consecutivas → `_running = False`

---

## 10. Frontend — Páginas y Comportamiento

### 10.1 Estructura general

- **Motor:** Jinja2 templates
- **CSS:** TailwindCSS (compilado con `tailwindcss-windows-x64.exe`)
- **Template base:** `src/templates/main.html` (navbar, sidebar, estilos comunes)

### 10.2 Páginas implementadas

#### `/` o `/inicio` → `inicio.html`
Dashboard principal. Muestra KPIs: total de lotes procesados, total de defectos detectados. Acceso rápido a registro y monitoreo.

#### `/auth/login` → `login.html`
Formulario de autenticación. Maneja errores de credenciales con mensajes inline. Limpia cookie al cargar si hay sesión caducada.

#### `/registro` → `registro.html`
Formulario de ingreso de muestra nueva. Dos cards:

**Card "Datos del caficultor":**
- `tipoDocumento` (select, carga desde `GET /tipo-documento/listar`)
- `numDocumento` (texto con validación según tipo)
- Auto-lookup al escribir: `GET /caficultor/consultar/{num_documento}`
- `nombreCaficultor` (readonly, llenado por lookup)
- `tipoCaficultor` (readonly, llenado por lookup)

**Card "Datos de la muestra":**
- `tipoGrano` (select, carga desde `GET /tipo-grano/listar`)
- `numSacos` (int ≥ 1)
- `pesoBruto` (float > 0, kg)
- `humedad` (float, 0 < x ≤ 100)
- `pesoMuestra` (float > 0, gr)
- `pesoTrillado` (float > 0, gr, ≤ pesoMuestra)
- `numTamiz` (int ≥ 1)
- `pesoTamizado` (float > 0, gr, ≤ pesoTrillado)

Todos los campos numéricos tienen validación inline (evento `input`) con hints debajo del campo.

Al enviar: `POST /evaluacion/registrar` → redirige a `/monitoreo/{evaluacion_id}`

#### `/monitoreo/{evaluacion_id}` → `monitoreo.html`
Página de monitoreo en tiempo real. Guard: si evaluación ya finalizada (tiene código), redirige a `/analisis/{id}`.

Muestra:
- Stream MJPEG: `<img src="/video/stream">`
- Conteo en tiempo real por clase (polling `GET /video/lote/conteo`)
- Estado Arduino: peso, distancia, si está listo
- Botones: Iniciar/Detener monitoreo, Resetear lote, Completar análisis
- Panel de KPIs de defectos acumulados
- Al completar: envía `PATCH /evaluacion/{id}/completar` con `peso_bueno` y `total_defectos`

#### `/analisis/{evaluacion_id}` → `analisis.html`
Resumen post-clasificación. Guard: si evaluación aún activa, redirige a `/monitoreo/{id}`.

Muestra:
- Código EVA asignado
- Datos del caficultor y la muestra
- Grado SCA calculado
- Defectos equivalentes totales
- Factor de rendimiento
- Peso en quintales
- Pago calculado (S/. o USD)
- Apto para specialty (sí/no)

#### `/nuevo-caficultor` → `caficultor.html`
Alta y conversión de caficultores. Dos modos:
- **Alta nueva:** llena datos de Persona + Caficultor, consulta RENIEC para autocompletar nombre
- **Convertir a socio:** búsqueda por documento, `PATCH /caficultor/convertir-socio/{num_documento}`

#### `/reporte` → `reporte.html`
Búsqueda de muestras por código EVA (`GET /evaluacion/buscar?codigo=EVA-XXX`). Muestra resumen completo de la evaluación encontrada.

#### `/valor-cafe` → `valor_cafe.html`
Gestión de precios de café. Solo accesible para Gerente y Administrador. Permite registrar nuevos precios, ver historial y cambios diarios.

#### `/configuracion-cooperativa` → `configuracion_cooperativa.html`
Panel de configuración de la cooperativa. Permite actualizar nombre, dirección, teléfono, correo, imagen de logo.

#### `/perfil` → `perfil.html`
Perfil del usuario autenticado. Permite actualizar datos personales y cambiar contraseña.

---

## 11. Dataset CoffeeRen-Dataset

### 11.1 Fuentes de datos

| Fuente | Imágenes | Procesamiento |
|--------|----------|---------------|
| Own/ (propias) | 2,413 | Crop centrado 1500px → 640×640, sufijo `_o_` |
| Public/ (públicas) | 1,067 | Resize letterbox → 640×640, sufijo `_p_` |
| **Total Dataset_1** | **3,480** | Normalizadas, validadas |

Repositorio público del dataset: https://github.com/BanderJ/PublicDatasetGreenCoffee

### 11.2 17 clases de defectos (NTP-ISO 10470:2014 + SCA)

| Clase | Tipo de defecto | Origen |
|-------|----------------|--------|
| agrio_ligero | Fermentación ligera | Biológico |
| agrio_severo | Fermentación severa | Biológico |
| averanado | Daño por sequía/maduración irregular | Ambiental |
| blanco | Decoloración ambiental | Ambiental |
| broca_ligero | Perforación superficial (insecto broca) | Plaga |
| broca_severo | Perforación profunda (insecto broca) | Plaga |
| cascarilla_cereza_seca | Restos de pulpa seca adherida | Beneficio incompleto |
| cascarilla_pergamino | Capa de pergamino adherida | Beneficio incompleto |
| cereza_seca | Fruto seco sin beneficiar | Beneficio incompleto |
| concha | Deformación tipo caracol/espiral | Malformación |
| deforme | Malformación por estrés | Malformación |
| inmaduro | Cosecha prematura | Cosecha deficiente |
| negro | Oxidación severa | Oxidación |
| partido_mitad | Grano partido por la mitad exactamente | Mecánico |
| partido_maquina | Fractura por máquina de trilla | Mecánico |
| pergamino | Trilla incompleta, capa pergaminosa visible | Beneficio incompleto |
| verde | Grano no desarrollado completamente | Grano sano (referencia) |

### 11.3 Scripts de procesamiento de datos

| Script | Propósito | Estado |
|--------|-----------|--------|
| `Own/crop.py` | Crop centrado configurable + preview | Completado |
| `Public/resize.py` | Resize letterbox con ajuste de color | Completado |
| `Dataset_1/merge_dataset.py` | Consolida Own + Public con mapeo de nombres | Completado |
| `Dataset_1/augmentation.py` | Aumento de datos (flip, rotación) | Disponible |
| `CambioTonos/calido_frio.py` | Normalización tonal (tonos cálidos → verde) | Pendiente entrada |
| `CambioTonos/calido_frio_sharpness.py` | Normalización + unsharpmask | Pendiente entrada |

### 11.4 Nomenclatura trazable de archivos

| Origen | Patrón | Ejemplo |
|--------|--------|---------|
| Own | `{clase}_o_{n:04d}.jpg` | `verde_o_0042.jpg` |
| Public | `{clase}_p_{n:04d}.jpg` | `negro_p_0007.jpg` |
| CambioTonos | `{carpeta}_v_{n:04d}.jpg` | `granos_v_0001.jpg` |
| Aumentadas | `{original}_aug_{transform}_{i}.jpg` | `agrio_o_0001_aug_flip_h_1.jpg` |

### 11.5 Resultados de entrenamiento YOLOv8n

| Métrica | Valor |
|---------|-------|
| mAP50 | **0.767** |
| mAP50-95 | **0.757** |
| Epochs | 75 |
| Batch size | 16 |
| Duración | 1.1 horas |
| GPU | Google Colab A100 |
| Imágenes de entrenamiento | 8,283 (con 3× augmentación Roboflow) |
| Split | 88% train / 8% val / 4% test |

---

## 12. Configuración del sistema (`src/config.py`)

```python
class Config:
    SECRET_KEY        = os.environ.get('SECRET_KEY') or 'your_secret_key_here'
    USER              = 'postgres'
    PASSWORD          = 'And1150'
    HOST              = 'localhost'
    PORT              = '5432'
    DATABASE          = 'tesis_prj'
    FACTILIZA_TOKEN   = os.environ.get('API_FACTILIZA') or ''
    ARDUINO_PORT      = os.environ.get('ARDUINO_PORT') or 'COM9'
    ARDUINO_BAUDRATE  = int(os.environ.get('ARDUINO_BAUDRATE') or '9600')
    SERVO_DELAY_S     = float(os.environ.get('SERVO_DELAY_S') or '0.5')
    SERVO_HOLD_S      = float(os.environ.get('SERVO_HOLD_S') or '0.3')
```

Carga variables de `.env` sin dependencias externas (parser manual). `SECRET_KEY` y `FACTILIZA_TOKEN` deben estar en `.env` en producción. Las credenciales de BD están hardcodeadas (solo para desarrollo local).

---

## 13. Estructura de archivos del proyecto

```
d:\TesisPrj\
├── src/
│   ├── main.py                    # Aplicación FastAPI, lifespan, routers
│   ├── config.py                  # Variables de configuración
│   ├── __init__.py
│   │
│   ├── database/
│   │   ├── bd.py                  # Clase Connection (psycopg2 wrapper)
│   │   └── script.sql             # Esquema PostgreSQL 18 completo
│   │
│   ├── routes/                    # Capa HTTP — 16 módulos
│   │   ├── auth_login.py
│   │   ├── caficultor.py
│   │   ├── camara.py
│   │   ├── cooperativa.py
│   │   ├── evaluacion.py
│   │   ├── dni.py
│   │   ├── perfil.py
│   │   ├── persona.py
│   │   ├── tipo_caficultor.py
│   │   ├── tipo_documento.py
│   │   ├── tipo_grano.py
│   │   ├── tipo_personal.py
│   │   ├── ubigeo.py
│   │   ├── valor_cafe.py
│   │   ├── video.py               # MJPEG streaming + endpoints de lote ML
│   │   └── arduino.py
│   │
│   ├── services/                  # Capa lógica de negocio — 12 módulos
│   │   ├── auth_service.py
│   │   ├── caficultor_service.py
│   │   ├── camara.py              # CamaraService (singleton, hilo captura)
│   │   ├── cooperativa_service.py
│   │   ├── evaluacion_service.py
│   │   ├── dni_service.py
│   │   ├── perfil_service.py
│   │   ├── persona_service.py
│   │   ├── tipo_caficultor_service.py
│   │   ├── tipo_documento_service.py
│   │   ├── tipo_grano_service.py
│   │   ├── tipo_personal_service.py
│   │   ├── ubigeo_service.py
│   │   ├── valor_cafe_service.py
│   │   └── tracker_service.py     # TrackerService (orquestador ML)
│   │
│   ├── models/                    # Capa SQL puro — 12 módulos
│   │   ├── caficultor.py
│   │   ├── cooperativa.py
│   │   ├── evaluacion.py
│   │   ├── personal.py
│   │   ├── persona.py
│   │   ├── tipo_caficultor.py
│   │   ├── tipo_documento.py
│   │   ├── tipo_grano.py
│   │   ├── tipo_personal.py
│   │   ├── ubigeo.py
│   │   └── valor_cafe.py
│   │
│   ├── schemas/                   # Pydantic validation — 12 módulos
│   │   ├── auth.py
│   │   ├── caficultor.py
│   │   ├── cooperativa.py
│   │   ├── dni.py
│   │   ├── evaluacion.py
│   │   ├── perfil.py
│   │   ├── persona.py
│   │   ├── tipo_caficultor.py
│   │   ├── tipo_documento.py
│   │   ├── tipo_grano.py
│   │   ├── tipo_personal.py
│   │   ├── ubigeo.py
│   │   └── valor_cafe.py
│   │
│   ├── utilities/                 # Herramientas transversales
│   │   ├── arduino_serial.py      # ArduinoSerial (singleton, hilo lector)
│   │   ├── jwt_required.py        # obtener_usuario_actual, RequerirLoginException
│   │   ├── jwt_utils.py           # Generación/decodificación de JWT
│   │   ├── security.py            # Argon2id hash/verify
│   │   └── servo_controller.py    # ServoController (singleton, hilo worker)
│   │
│   ├── ml/                        # Módulo de Machine Learning
│   │   ├── __init__.py
│   │   ├── inference.py           # CoffeeRenInference (legacy, referencia)
│   │   ├── tracker.py             # CoffeeRenTracker (YOLO + ByteTrack)
│   │   ├── classifier.py          # Cálculo de grado SCA
│   │   └── models/
│   │       ├── yolov8n/
│   │       │   ├── best.pt        # NO en Git — descargar de Google Drive
│   │       │   └── constants.py   # CLASES (17), COLORES, EQUIVALENCIAS_DEFECTO
│   │       ├── yolov26n/
│   │       │   ├── best.pt        # NO en Git
│   │       │   └── constants.py
│   │       ├── yolov26n_2cls/
│   │       │   ├── best.pt        # NO en Git — MODELO ACTIVO EN PRODUCCIÓN
│   │       │   └── constants.py   # CLASES (2: defecto/verde), EQUIVALENCIAS
│   │       └── yolo11n/
│   │           └── constants.py   # Pendiente de entrenamiento
│   │
│   ├── apis/
│   │   └── reniec_api.py          # Cliente HTTP para API RENIEC/Factiliza
│   │
│   ├── templates/                 # Jinja2 templates — 11 archivos
│   │   ├── main.html              # Template base (navbar, sidebar)
│   │   ├── login.html
│   │   ├── inicio.html
│   │   ├── registro.html
│   │   ├── monitoreo.html
│   │   ├── analisis.html
│   │   ├── reporte.html
│   │   ├── nuevo_caficultor.html
│   │   ├── valor_cafe.html
│   │   ├── perfil.html
│   │   └── configuracion_cooperativa.html
│   │
│   ├── static/
│   │   ├── css/
│   │   │   ├── input.css          # Fuente TailwindCSS (con directivas @tailwind)
│   │   │   └── tailwind.css       # Compilado (generado por CLI)
│   │   ├── icon/
│   │   │   └── coffee-bean_icon.png
│   │   └── js/                    # Scripts frontend
│   │
│   └── resources/
│       └── cooperativa/           # Imágenes de logos de cooperativa
│
├── docs/
│   ├── registro-avances.md        # Sprints y estado del proyecto
│   ├── API_VIDEO_STREAMING.md     # Referencia de endpoints de video
│   ├── defectos_sca_tabla_referencia.md
│   └── documentacion/
│       ├── DOCUMENTACION.md       # Guía técnica de Dataset
│       ├── avance-tecnico-completo-2026.md  # Este documento
│       ├── Analisis_Requerimientos.md
│       ├── Product_Backlog_Sprints.md
│       ├── BACA CHUQUIMANCO_PROY.md
│       └── PreInforme_Tesis_2026-I.md
│
├── CLAUDE.md                      # Guía de arquitectura para Claude Code
├── requirements.txt               # Dependencias Python
├── tailwindcss-windows-x64.exe    # Compilador TailwindCSS standalone
└── .env                           # Variables de entorno (no en Git)
```

---

## 14. Flujo de negocio completo — Evaluación de un lote

```
1. Operario accede a /registro
2. Selecciona tipo de documento + ingresa N° documento
   → Auto-lookup caficultor desde BD
   → Campos nombre y tipo se llenan automáticamente
3. Completa datos de muestra (sacos, pesos, humedad, tamiz)
4. Envía formulario → POST /evaluacion/registrar
   → Se crea registro en BD sin código (estado "activa")
   → Retorna evaluacion_id (UUID)
5. Redirige a /monitoreo/{evaluacion_id}
6. Operario hace click en "Iniciar monitoreo"
   → POST /video/iniciar
   → CamaraService abre cámara ELP AR0234 (1280×720 @ 60fps)
   → TrackerService inicia hilo de procesamiento
7. Los granos pasan por la faja transportadora
   → YOLO + ByteTrack detecta y asigna ID único por grano
   → ServoController recibe solicitud con lambda por cada grano nuevo
   → Después de SERVO_DELAY_S: evalúa mejor clase → SERVO:DEFECTO o SERVO:BUENO
   → Servo separa granos físicamente
8. El stream MJPEG muestra en tiempo real:
   → Bounding boxes con color por clase
   → Label: #ID, nombre defecto, confianza %
   → Estadísticas: total granos, FPS, detecciones activas
9. Operario registra peso de granos buenos (desde celda de carga)
   → GET /arduino/peso → peso en tiempo real
10. Al terminar la muestra: "Completar análisis"
    → PATCH /evaluacion/{id}/completar con peso_bueno y total_defectos
    → EvaluacionService calcula: peso_cascara, factor_rendimiento, peso_neto,
      peso_por_qq, pago, categoría SCA, código EVA correlativo
11. Redirige a /analisis/{evaluacion_id}
    → Muestra resumen: grado, apto specialty, defectos, pago al caficultor
12. POST /video/lote/resetear → limpia conteo para próxima muestra
```

---

## 15. Cambios en la rama `temporal` (en curso)

La rama `temporal` contiene modificaciones en progreso sobre los siguientes archivos:

| Archivo | Tipo de cambio |
|---------|---------------|
| `src/ml/inference.py` | Modificado |
| `src/ml/tracker.py` | Modificado |
| `src/services/camara.py` | Modificado |
| `src/services/tracker_service.py` | Modificado |
| `src/templates/monitoreo.html` | Modificado |
| `src/resources/cooperativa/3313270a-08bd-4e4d-9f50-e2fd6182b234.png` | Nuevo archivo |

Commits recientes en la rama:
1. `927ccae` — Añadir compatibilidad con nuevos pesos, KPIs y ajustes de UI
2. `cdbce98` — BD UTF-8, refactorización de autenticación, actualizaciones coop/service
3. `4d56ecb` — Actualizar frontend, ML tracker, Arduino y utilidades
4. `a26310b` — Corregir carga de cooperativa y autenticación por cookie
5. `6e7e015` — Añadir TipoGrano CRUD y refactorización de UI de Perfil

---

## 16. Reglas críticas de implementación

### ML
- Modelo cargado UNA SOLA VEZ al startup, cacheado en memoria — nunca recargar por frame
- Tracker en hilo daemon separado — routes solo hacen polling no-bloqueante
- Defect equivalences solo se pueden cambiar verificando con Line Coffee Marañón y NTP-ISO 10470:2014
- Weights en `src/ml/models/{name}/best.pt` — NO en Git — descargar desde Google Drive

### Backend
- SQL siempre parametrizado: `db.obtener("SELECT … WHERE id=%s", [id])` — nunca f-strings en SQL
- `try … finally: db.close()` cuando se abre Connection manualmente
- Un método flexible parametrizado > tres métodos casi idénticos
- No cruzar capas: routes no hacen SQL, models no tienen lógica de negocio

### Hardware
- Arduino: enviar comandos con `arduino_serial.enviar_comando("CMD")`, no directamente desde ML
- Servo: usar `servo_controller.solicitar()` con el lambda de clase — no llamar direct a arduino desde tracker
- Si cámara desconectada: servo queda en DEFECTO (posición segura) hasta que se reinicie el monitoreo

---

## 17. Pendientes técnicos

| Item | Prioridad | Descripción |
|------|-----------|-------------|
| Entrenamiento yolo26n 17 clases | Alta | En progreso en Google Colab A100 |
| Entrenamiento yolo11n | Media | Pendiente |
| Verificar equivalencias SCA con cooperativa | Alta | Tabla en yolov8n/constants.py requiere validación oficial |
| Probar hardware completo | Alta | Cámara ELP + Arduino + servo en banco de pruebas |
| Calibrar SERVO_DELAY_S y SERVO_HOLD_S | Alta | Depende de velocidad real de la faja |
| Evaluación comparativa modelos | Media | mAP, latencia, recursos (yolov8n vs yolo26n vs yolo11n) |
| Fase 4 CRISP-ML(Q) | Media | Garantía de calidad: pruebas de robustez, sesgo, casos límite |

---

## 18. Métricas generales del proyecto

| Componente | Cantidad |
|------------|---------|
| Imágenes en Dataset_1 | 3,480 |
| Imágenes tras augmentación (Roboflow) | 8,283 |
| Clases de defectos | 17 |
| Tablas en base de datos | 13 |
| Módulos de routes | 16 |
| Módulos de services | 15 |
| Módulos de models | 11 |
| Módulos de schemas | 13 |
| Templates Jinja2 | 11 |
| Modelos YOLO disponibles | 3 (yolov8n, yolo26n, yolov26n_2cls) |
| mAP50 mejor modelo (yolov8n) | 0.767 |
| Endpoints API registrados en FastAPI | 50+ |

---

**Autor:** Anderson Jhomar Baca Chuquimanco  
**Email:** ander.jbc115@gmail.com  
**Asesor:** Mgtr. William Alfredo Noblecilla Vinces  
**ORCID Asesor:** https://orcid.org/0000-0002-3531-2501  
**Escuela:** Ingeniería de Sistemas y Computación — USAT  
**Última actualización:** 2026-06-01
