# Registro de Incidencias del Proyecto CoffeeRen

**Proyecto:** Sistema automático de clasificación de granos de café verde mediante visión artificial en una cooperativa de Amazonas (CoffeeRen)
**Autor:** Anderson Jhomar Baca Chuquimanco
**Institución:** Universidad Católica Santo Toribio de Mogrovejo (USAT) — Cooperativa Agraria Line Coffee Marañón
**Fecha de elaboración del registro:** 2026-09-01
**Última actualización:** 2026-09-30 (estados de INC-53 a INC-61 confirmados por commit; nuevas INC-65 a INC-68)
**Ámbito:** Base de datos, cámara, detección/ML, dataset, Arduino, servo separador, diseño/frontend, integración, autenticación e infraestructura.

---

## 1. Cómo leer este registro

Este documento consolida, de forma retrospectiva, los problemas técnicos que surgieron durante el desarrollo de CoffeeRen: qué pasó, qué se detectó, la causa raíz, la solución aplicada, su gravedad y su estado.

Las incidencias están agrupadas por los **cuatro Sprints del cronograma vigente** (`docs/CRONOGRAMA.xlsx`), y dentro de cada Sprint por la fase CRISP-ML(Q) correspondiente. El cronograma actual reencuadra en 4 Sprints un desarrollo que empezó antes (marzo 2026); por eso cada incidencia se ubica en el Sprint cuyo **objetivo** le corresponde (planificación, núcleo funcional, integración, finalización), no necesariamente por su fecha calendario. Como respaldo verificable se cita el **commit de Git** donde el problema se registró o se corrigió, con su fecha real.

### Leyenda de gravedad

| Nivel | Significado |
|---|---|
| **Crítica** | Bloquea el flujo principal, corrompe datos o pone en riesgo el hardware. |
| **Alta** | Degrada una funcionalidad central; existe rodeo temporal. |
| **Media** | Afecta una funcionalidad secundaria o la calidad del resultado. |
| **Baja** | Cosmético, menor o preventivo. |

### Leyenda de estado

| Estado | Significado |
|---|---|
| **Resuelta** | Corregida y verificada en el código actual. |
| **Resuelta con deuda técnica** | Corregida, pero deja un compromiso a saldar más adelante. |
| **Mitigada** | Bajo control parcial; requiere seguimiento. |
| **En curso** | Trabajo activo en la rama `temporal`, sin commit de cierre. |
| **Abierta** | Pendiente de acción. |
| **Pendiente de verificación** | Corregida en código, sin prueba en campo o con hardware real. |

---

## 2. Tabla resumen

| ID | Sprint | Área | Incidencia | Gravedad | Estado |
|---|---|---|---|---|---|
| INC-01 | 1 | Infraestructura | Clase `Connection` con `autocommit` e imports mal configurados | Alta | Resuelta |
| INC-02 | 1 | Infraestructura | Reestructuración de `app/` a `src/` a mitad del incremento inicial | Media | Resuelta |
| INC-03 | 1 | Base de datos | `DETALLE_EVALUACION.cantidad` admitía NULL | Baja | Resuelta |
| INC-04 | 1 | Base de datos | Modelo de `CAFICULTOR` / `EVALUACION` insuficiente para el negocio real | Media | Resuelta con deuda técnica |
| INC-05 | 1 | Base de datos | `UBIGEO` almacenaba solo el código, no los nombres | Media | Resuelta |
| INC-06 | 1 | Integración | Validación de identidad dependía de tipeo manual | Baja | Resuelta |
| INC-07 | 1 | Frontend / Diseño | Pantalla de monitoreo con datos simulados/estáticos | Baja | Resuelta con deuda técnica |
| INC-08 | 1 | Cámara | Primer streaming sin control de ciclo de vida | Media | Resuelta |
| INC-09 | 1 | Dataset | Nomenclatura y nombres de clase inconsistentes entre fuentes | Media | Resuelta |
| INC-10 | 1 | Dataset | Imágenes con desenfoque y reflejos especulares | Media | Resuelta |
| INC-11 | 1 | Seguridad | Credenciales de base de datos embebidas en el código | Media | Mitigada |
| INC-12 | 2 | Detección / ML | Archivo `classifer.py` mal nombrado | Baja | Resuelta |
| INC-13 | 2 | Detección / ML | Mapeo invertido de clases YOLO (`broca_ligero` ↔ `broca_severo`) | Alta | Resuelta |
| INC-14 | 2 | Detección / ML | Umbral de confianza alto: bajo recall de defectos | Alta | Resuelta |
| INC-15 | 2 | Detección / ML | Constantes de todos los modelos mezcladas en un solo archivo | Media | Resuelta |
| INC-16 | 2 | Detección / ML | `classifier.py` con 5 grados SCA en vez de 3 | Alta | Resuelta con deuda técnica |
| INC-17 | 2 | Detección / ML | Tabla de equivalencias SCA sin validación oficial | Alta | Abierta |
| INC-18 | 2 | Detección / ML | Modelo de 17 clases sin converger a tiempo | Media | Mitigada |
| INC-19 | 2 | Autenticación | Cookie JWT rota por comillas al llevar el prefijo `Bearer ` | Crítica | Resuelta |
| INC-20 | 2 | Base de datos | Consultas de `COOPERATIVA` usaban `cooperativa_id` en vez de `id` | Alta | Resuelta |
| INC-21 | 2 | Base de datos | Conexión sin `client_encoding=utf8`: acentos corruptos | Media | Resuelta |
| INC-22 | 2 | Base de datos | Schemas Pydantic no coincidían con la nulabilidad real de la BD | Media | Resuelta |
| INC-23 | 2 | Base de datos | `COOPERATIVA` con campos `NOT NULL` sin `DEFAULT`: todo INSERT fallaba | Alta | Resuelta |
| INC-24 | 2 | Autenticación | Dos dependencias de auth divergentes en las rutas de página | Media | Resuelta |
| INC-25 | 2 | Frontend / Diseño | BOM UTF-8 de PowerShell rompía la carga de JS | Alta | Resuelta |
| INC-26 | 2 | Frontend / Diseño | Errores de sintaxis JS que tumbaban el script completo | Alta | Resuelta |
| INC-27 | 2 | Frontend / Diseño | Acceso a campos de API con forma equivocada (anidado vs plano) | Media | Resuelta |
| INC-28 | 3 | Integración | Streaming MJPEG con ruido: se enviaban bytes BGR crudos | Crítica | Resuelta |
| INC-29 | 3 | Integración | `monitoreo.html` apuntaba a `/camara/stream` (vídeo sin YOLO) | Alta | Resuelta |
| INC-30 | 3 | Integración | Rutas de vídeo sin prefijo `/video/` y sin `Depends()` de auth | Alta | Resuelta |
| INC-31 | 3 | Integración | `NameError` por `Depends` no importado en `routes/video.py` | Crítica | Resuelta |
| INC-32 | 3 | Cámara | Sin cámara física el pipeline no se podía probar | Media | Resuelta con deuda técnica |
| INC-33 | 3 | Cámara | Cámara no se liberaba y quedaba bloqueada entre sesiones | Alta | Resuelta |
| INC-34 | 3 | Cámara | Doble decodificación/codificación JPEG en el pipeline | Media | Resuelta |
| INC-35 | 3 | Detección / ML | IDs de ByteTrack se reiniciaban a 1-2 tras pausas de la faja | Alta | Resuelta |
| INC-36 | 3 | Detección / ML | Crecimiento ilimitado de memoria en el acumulador de detecciones | Media | Resuelta |
| INC-37 | 3 | Detección / ML | Latencia alta en la primera inferencia | Media | Resuelta |
| INC-38 | 3 | Detección / ML | Filtro de tamaño de grano descalibrado | Media | Resuelta |
| INC-39 | 3 | Detección / ML | Pesos del modelo no versionables en Git | Media | Mitigada |
| INC-40 | 3 | Arduino / Hardware | Reset del Arduino por DTR al reabrir el puerto serial | Media | Mitigada |
| INC-41 | 3 | Arduino / Hardware | Windows suspendía el puerto USB serial por inactividad | Media | Resuelta |
| INC-42 | 3 | Frontend / Diseño | `bfcache` mostraba monitoreo ya finalizado | Media | Resuelta |
| INC-43 | 3 | Frontend / Diseño | `max-width` heredado de `perfil.css` dejaba layouts a medio ancho | Baja | Resuelta |
| INC-44 | 4 | Arduino / Hardware | Celda de carga HX711 inestable a 115200 baud en clones de Arduino | Alta | Resuelta con deuda técnica |
| INC-45 | 4 | Servo separador | Delay del servo mal calculado: separaba tarde | Alta | Resuelta |
| INC-46 | 4 | Servo separador | Servo atascado en DEFECTO por comando `SERVO:BUENO` perdido | Alta | Resuelta |
| INC-47 | 4 | Servo separador | Parpadeo DEFECTO→BUENO→DEFECTO con defectos consecutivos | Media | Resuelta |
| INC-48 | 4 | Base de datos | `script.sql`: `incidencias` añadida tarde e inserts con UUID fijos | Media | Resuelta |
| INC-49 | 4 | Base de datos | Historial de precios de café se sobrescribía al actualizar | Alta | Resuelta |
| INC-50 | 4 | Detección / ML | Módulo `inference.py` legacy y ramas muertas en el tracker | Baja | Resuelta |
| INC-51 | 4 | Infraestructura | `config.py` estaba en `.gitignore`: cada equipo con su copia | Media | Resuelta |
| INC-52 | 4 | Documentación | Manuales con datos obsoletos (nombre de BD, versión de PG, baudrate) | Media | Resuelta |
| INC-53 | 4 | Cámara | Cámara cae a YUY2 (~9 fps) por no fijar MJPEG antes del primer `read()` | Crítica | Resuelta |
| INC-54 | 4 | Detección / ML | Granos que se tocan no generan bounding box | Alta | Mitigada |
| INC-55 | 4 | Detección / ML | Detecciones débiles y efímeras accionaban el servo | Media | Mitigada |
| INC-56 | 4 | Cámara | Foco y zoom manuales del lente, sin repetibilidad | Media | Abierta |
| INC-57 | 4 | Cámara | Desenfoque por movimiento (motion blur) pese al global shutter | Media | Abierta |
| INC-58 | 4 | Base de datos | Renombrado de `COOPERATIVA.direccion` a `ubicacion` | Baja | Resuelta |
| INC-59 | 4 | Infraestructura | Endpoints y código muerto sin consumidor en las 4 capas | Baja | Resuelta |
| INC-60 | 4 | Integración | Mensajes de error divergentes entre backend y frontend | Media | Resuelta |
| INC-61 | 4 | Autenticación | Un usuario podía desactivar su propia cuenta y la sesión seguía viva tras desactivar a cualquiera | Alta | Resuelta |
| INC-62 | 2 | Detección / ML | Prácticas de calidad de dataset y trazabilidad de experimentos planificadas sin ejecutar (IRA, fuga de datos, MLflow) | Media | Mitigada |
| INC-63 | 3 | Detección / ML | Fase 4 CRISP-ML(Q) (validación formal, matriz de confusión, robustez) no se ejecutó | Alta | Abierta |
| INC-64 | 4 | Detección / ML / Integración | Monitoreo de calidad de detecciones y validación en campo con operarios reales sin implementar | Media | Abierta |
| INC-65 | 4 | Detección / ML / Dataset | Brecha de dominio: dataset tomado con celular, producción con la cámara ELP (~40 % de granos sanos marcados como defecto) | Alta | Abierta |
| INC-66 | 4 | Infraestructura / ML | `torch` y `onnxruntime` en build solo-CPU: inferencia saturaba los 24 núcleos con la GPU sin usar | Alta | Resuelta |
| INC-67 | 4 | Detección / ML | Parpadeo desconocido ↔ verde ↔ defecto por usar una ventana acotada como historial | Media | Resuelta |
| INC-68 | 4 | Integración / Negocio | Peso bruto menor o igual a la tara generaba peso neto ≤ 0 y pago negativo | Alta | Resuelta |

---

## 3. Sprint 1 — Planificación y primer incremento

**Cronograma:** Semana 2. **CRISP-ML(Q):** Fase 1 (Comprensión del Negocio y los Datos) e inicio de Fase 2 (Preparación de los Datos).
**Objetivo del Sprint:** revisar el proyecto aprobado, elaborar historias de usuario y backlog, diseñar la solución inicial, configurar el entorno y el repositorio, implementar las primeras historias, analizar requisitos con la cooperativa, seleccionar el stack tecnológico e iniciar la recopilación de imágenes.

### INC-01 · Clase `Connection` con `autocommit` e imports mal configurados
- **Área:** Infraestructura / Base de datos.
- **Qué se detectó:** el primer incremento no persistía datos y fallaban los imports del módulo de base de datos al arrancar.
- **Causa raíz:** el wrapper de psycopg2 quedó con el `autocommit` mal configurado y la ruta de import del módulo `bd.py` era incorrecta tras el andamiaje inicial del proyecto.
- **Solución:** se fijó `autocommit=False` con `commit()` / `rollback()` explícitos en `Connection`, se corrigieron los import paths y se añadieron `print` de depuración temporales para rastrear el fallo en la conexión.
- **Gravedad:** Alta. **Estado:** Resuelta.
- **Evidencia:** commits `9facab4` (2026-04-02), `4cafe53` (2026-04-06); `src/database/bd.py`.

### INC-02 · Reestructuración de `app/` a `src/` a mitad del incremento inicial
- **Área:** Infraestructura.
- **Qué se detectó:** la estructura de carpetas inicial (`app/`) no reflejaba el patrón de cuatro capas y complicaba imports y montaje de estáticos.
- **Causa raíz:** organización de carpetas improvisada antes de consolidar la arquitectura Routes / Services / Models / Schemas.
- **Solución:** migración completa a `src/`, actualización de todos los imports, del montaje de estáticos y de las rutas de Jinja2; se introdujo la capa de servicios y los schemas Pydantic.
- **Gravedad:** Media. **Estado:** Resuelta.
- **Evidencia:** commit `b412f1f` (2026-04-10).

### INC-03 · `DETALLE_EVALUACION.cantidad` admitía NULL
- **Área:** Base de datos.
- **Qué se detectó:** revisión del script SQL inicial: se podían registrar detalles de evaluación sin cantidad.
- **Causa raíz:** la columna se definió sin restricción `NOT NULL`.
- **Solución:** se añadió `NOT NULL` a `DETALLE_EVALUACION.cantidad` en `src/database/script.sql`.
- **Gravedad:** Baja. **Estado:** Resuelta.
- **Evidencia:** commit `b412f1f` (2026-04-10).

### INC-04 · Modelo de `CAFICULTOR` / `EVALUACION` insuficiente para el negocio real
- **Área:** Base de datos.
- **Qué se detectó:** al mapear el flujo real de evaluación de la cooperativa (pesos de muestra, trillado, tamiz, tara, tipo de grano, factor de rendimiento, pago) faltaban columnas y las relaciones no soportaban el caso.
- **Causa raíz:** el esquema inicial era mínimo; los requisitos de pesajes y cálculo de pago se detallaron después de las reuniones con la gerencia y el personal técnico.
- **Solución:** se agregaron las tablas `TIPO_GRANO` y `UBIGEO`, se amplió `EVALUACION` con unos quince campos nuevos, se llevó `CAFICULTOR` a PK compuesta `(caficultor_id, tipo_caficultor_id)` y se ajustaron las claves foráneas.
- **Gravedad:** Media. **Estado:** Resuelta con deuda técnica (la PK compuesta se revierte en Sprint 3 por complejidad innecesaria en las consultas).
- **Evidencia:** commits `b7b4bc8` (2026-04-30), `b16084d` (2026-05-15).

### INC-05 · `UBIGEO` almacenaba solo el código, no los nombres
- **Área:** Base de datos.
- **Qué se detectó:** los formularios de persona y cooperativa necesitaban mostrar departamento, provincia y distrito y solo se disponía del código numérico de seis dígitos.
- **Causa raíz:** diseño inicial de `UBIGEO` como catálogo de códigos sin descomposición textual.
- **Solución:** se rediseñaron las columnas de `UBIGEO` para almacenar `departamento`, `provincia` y `distrito`, y se cargó el CSV completo del INEI.
- **Gravedad:** Media. **Estado:** Resuelta.
- **Evidencia:** commit `2fe6b2a` (2026-05-04).

### INC-06 · Validación de identidad dependía de tipeo manual
- **Área:** Integración externa.
- **Qué se detectó:** el registro de caficultores era lento y propenso a errores al escribir nombres y apellidos a mano.
- **Causa raíz:** no había integración con una fuente oficial de identidad.
- **Solución:** se implementó el cliente `ReniecApi` (proveedor Factiliza) para consultar DNI y autocompletar los datos de la persona; el token se lee de `.env` (`API_FACTILIZA`). Se usó `urllib` de la librería estándar en lugar de `requests`.
- **Gravedad:** Baja. **Estado:** Resuelta.
- **Evidencia:** commit `2fe6b2a` (2026-05-04); `src/apis/reniec_api.py`.

### INC-07 · Pantalla de monitoreo con datos simulados/estáticos
- **Área:** Frontend / Diseño.
- **Qué se detectó:** la página de monitoreo mostraba barras de progreso y cálculos de rendimiento con valores aleatorios o fijos.
- **Causa raíz:** decisión deliberada para poder demostrar la interfaz antes de tener el pipeline de visión y el hardware.
- **Solución:** se mantuvo como marcador (deuda técnica reconocida) y se sustituyó por datos reales durante la integración del Sprint 3.
- **Gravedad:** Baja. **Estado:** Resuelta con deuda técnica.
- **Evidencia:** commits `b7b4bc8` (2026-04-30), `b16084d` (2026-05-15).

### INC-08 · Primer streaming de cámara sin control de ciclo de vida
- **Área:** Cámara.
- **Qué se detectó:** la cámara no se liberaba al apagar la aplicación y no existía verificación de estado antes de transmitir.
- **Causa raíz:** la primera versión de `CamaraService` no cerraba el dispositivo en el `lifespan` de la app.
- **Solución:** se añadió el cierre de cámara en el shutdown y el endpoint `GET /camara/estado`; se incorporó `opencv-python-headless` a `requirements.txt`.
- **Gravedad:** Media. **Estado:** Resuelta (se refuerza en INC-33).
- **Evidencia:** commit `b16084d` (2026-05-15).

### INC-09 · Nomenclatura y nombres de clase inconsistentes entre fuentes del dataset
- **Área:** Dataset (CRISP-ML(Q) Fase 2).
- **Qué se detectó:** al consolidar las carpetas `Own/` y `Public/` los nombres de clase no coincidían (`broca_servera` frente a `broca_severo`, `Concha` frente a `concha`, `cereza_seco` frente a `cereza_seca`).
- **Causa raíz:** etiquetado manual de distintas fuentes sin una convención común.
- **Solución:** `merge_dataset.py` con una tabla de mapeo a nombres canónicos y nomenclatura trazable con sufijos `_o_` (propias) y `_p_` (públicas) para auditoría posterior.
- **Gravedad:** Media. **Estado:** Resuelta.
- **Evidencia:** `docs/documentacion/etapa2_crisp_mlq.md`; `docs/DOCUMENTACION_SISTEMA.md`.

### INC-10 · Imágenes con desenfoque y reflejos especulares
- **Área:** Dataset (CRISP-ML(Q) Fase 1 y 2).
- **Qué se detectó:** durante la verificación de calidad de los datos se hallaron capturas del prototipo con blur y reflejos que falsearían el color real del grano.
- **Causa raíz:** condiciones de captura no controladas: iluminación variable y foco manual del lente.
- **Solución:** filtro de descarte manual por umbral de nitidez y eliminación de las capturas con reflejos especulares; se documentó el criterio de calidad.
- **Gravedad:** Media. **Estado:** Resuelta (la causa de fondo —iluminación y foco— reaparece con el hardware real; ver INC-56 e INC-57).
- **Evidencia:** `docs/documentacion/PreInforme_Tesis_2026-I.md`; `docs/registro-avances.md`.

### INC-11 · Credenciales de base de datos embebidas en el código
- **Área:** Seguridad.
- **Qué se detectó:** `src/config.py` contiene `USER`, `PASSWORD`, `HOST` y `DATABASE` como literales.
- **Causa raíz:** configuración pensada para el entorno local de desarrollo.
- **Solución parcial:** `SECRET_KEY` y `API_FACTILIZA` se movieron a `.env`; las credenciales de base de datos siguen como literales y se documentó que solo es aceptable para despliegue local.
- **Gravedad:** Media. **Estado:** Mitigada (pendiente de resolver antes de un despliegue fuera del entorno local).
- **Evidencia:** `src/config.py`; `CLAUDE.md`.

---

## 4. Sprint 2 — Desarrollo y cierre del núcleo funcional

**Cronograma:** Semanas 3-4. **CRISP-ML(Q):** Fase 2 (Preparación de los Datos, cierre) y Fase 3 (Modelado).
**Objetivo del Sprint:** desarrollar los componentes del escenario principal, implementar el flujo de inicio a fin, ejecutar pruebas funcionales, registrar y corregir errores, consolidar y etiquetar el dataset en 640×640, limpiarlo y aumentarlo, entrenar y comparar arquitecturas YOLO y exportar el modelo final a ONNX.

### INC-12 · Archivo `classifer.py` mal nombrado
- **Área:** Detección / ML.
- **Qué se detectó:** el módulo de clasificación SCA estaba escrito como `classifer.py` (falta una `i`), lo que rompía imports al normalizar el nombre.
- **Causa raíz:** error de tipeo al crear el archivo.
- **Solución:** renombrado a `classifier.py` y actualización de todos los imports (cambio marcado como *breaking* en el commit).
- **Gravedad:** Baja. **Estado:** Resuelta.
- **Evidencia:** commit `1338ea6` (2026-05-26).

### INC-13 · Mapeo invertido de clases YOLO (`broca_ligero` ↔ `broca_severo`)
- **Área:** Detección / ML.
- **Qué se detectó:** el sistema mostraba "broca severo" donde el grano tenía broca ligera y viceversa.
- **Causa raíz:** el array `CLASES` tenía los índices 4 y 5 intercambiados respecto al orden real con el que se entrenó el modelo (índice 4 = `broca_severo`, índice 5 = `broca_ligero`).
- **Solución:** se corrigió el orden del array `CLASES` en las constantes del modelo.
- **Gravedad:** Alta (afecta directamente la equivalencia de defectos y por tanto el grado del lote). **Estado:** Resuelta.
- **Evidencia:** commit `4ead7f0` (2026-05-26).

### INC-14 · Umbral de confianza alto: bajo recall de defectos
- **Área:** Detección / ML.
- **Qué se detectó:** granos defectuosos claros no se detectaban; el conteo del lote quedaba corto.
- **Causa raíz:** `CONF_THRESHOLD` se pasaba directo a `model.track(conf=...)` con un valor alto (0.30, antes incluso 0.50), descartando detecciones antes de que ByteTrack pudiera usar su banda de baja confianza.
- **Solución:** se bajó el umbral de forma escalonada (0.50 → 0.30 → 0.20 y, en el trabajo en curso, a 0.15 como piso), delegando el filtrado a ByteTrack y a la votación por mayoría del tracker. En control de calidad se prefiere un falso positivo (grano bueno rechazado) a un falso negativo (defecto que pasa).
- **Gravedad:** Alta. **Estado:** Resuelta (ajuste fino continúa en INC-54).
- **Evidencia:** commits `fe26f53` (2026-05-26), `4ead7f0`; `src/services/tracker_service.py`.

### INC-15 · Constantes de todos los modelos mezcladas en un solo archivo
- **Área:** Detección / ML.
- **Qué se detectó:** cambiar de modelo YOLO obligaba a editar un archivo compartido de clases, colores y equivalencias, con riesgo de arrastrar valores de otro modelo.
- **Causa raíz:** no había separación por modelo de la configuración de inferencia.
- **Solución:** se reorganizó `src/ml/models/{modelo}/constants.py` por modelo, con carga dinámica según el YOLO seleccionado en `tracker_service.py`.
- **Gravedad:** Media. **Estado:** Resuelta.
- **Evidencia:** commits `6741e58` (2026-05-27), `0c06b79` (2026-06-15).

### INC-16 · `classifier.py` con 5 grados SCA en vez de 3
- **Área:** Detección / ML.
- **Qué se detectó:** el reporte del lote asignaba grados 1 a 5 con límites (0-11, 12-23, 24-86, 87-153, 154+) que no corresponden a la norma aplicada por la cooperativa.
- **Causa raíz:** implementación basada en una interpretación incorrecta de la escala SCA.
- **Solución:** se reescribió a **3 grados** — Grado 1 / Specialty (0-15), Grado 2 (16-23), Grado 3 (24-30) — y se reorganizaron las equivalencias por categoría (grave, leve, mínimo). La tabla maestra `CATEGORIA` de la BD refleja la misma escala.
- **Gravedad:** Alta. **Estado:** Resuelta con deuda técnica (ver INC-17).
- **Evidencia:** `docs/defectos_sca_tabla_referencia.md`; `docs/documentacion/arquitectura-sistema-clasificacion.md`; memoria técnica del proyecto (2026-05-26).

### INC-17 · Tabla de equivalencias SCA sin validación oficial
- **Área:** Detección / ML.
- **Qué se detectó:** las equivalencias de defecto por grano usadas en `classifier.py` (y el valor 0.83 del modelo binario) provienen de bibliografía y de una ponderación propia, no de la tabla oficial de Line Coffee Marañón.
- **Causa raíz:** aún no se ha realizado la sesión de validación con el personal de calidad de la cooperativa.
- **Solución:** documentada como verificación obligatoria previa al despliegue; centralizada en `constants.py` por modelo para poder ajustarla sin tocar la lógica.
- **Gravedad:** Alta. **Estado:** Abierta.
- **Evidencia:** `docs/defectos_sca_tabla_referencia.md`; `CLAUDE.md` (regla de integración ML).

### INC-18 · Modelo de 17 clases sin converger a tiempo
- **Área:** Detección / ML (CRISP-ML(Q) Fase 3).
- **Qué se detectó:** el flujo de integración necesitaba un modelo estable y el YOLO de 17 clases (`yolo26n`) seguía en entrenamiento; el `yolov8n` de referencia daba mAP50 0.767 pero con clases confundibles.
- **Causa raíz:** entrenamiento comparativo de arquitecturas todavía en curso en Google Colab; dataset con clases minoritarias poco representadas.
- **Solución:** se adoptó como modelo de producción un YOLO **binario de 2 clases** (`yolov26n_2cls`: defecto / verde), suficiente para separar físicamente y calcular el grado, dejando el modelo de 17 clases como cascada opcional (`USE_MODELO_DEFECTOS`). La cascada se retiró del código el 2026-07-08 (commit `787a7ac`); el sistema opera solo con el modelo binario.
- **Gravedad:** Media. **Estado:** Mitigada (la clasificación por tipo de defecto queda fuera del alcance actual).
- **Evidencia:** `docs/documentacion/arquitectura-sistema-clasificacion.md`; commits `0c06b79` (2026-06-15) y `787a7ac` (2026-07-08).

### INC-19 · Cookie JWT rota por comillas al llevar el prefijo `Bearer `
- **Área:** Autenticación.
- **Qué se detectó:** tras iniciar sesión, el servidor no podía leer el token y expulsaba al usuario al login.
- **Causa raíz:** la cookie se guardaba como `"Bearer <token>"`; al contener un espacio, `SimpleCookie` envolvía el valor entre comillas y la lectura posterior del token fallaba.
- **Solución:** se guarda solo el token en la cookie; `jwt_required` y `auth_service` aceptan tanto el token puro como el formato legado `Bearer <token>`.
- **Gravedad:** Crítica (impedía usar el sistema autenticado). **Estado:** Resuelta.
- **Evidencia:** commit `a26310b` (2026-05-29).

### INC-20 · Consultas de `COOPERATIVA` usaban `cooperativa_id` en vez de `id`
- **Área:** Base de datos.
- **Qué se detectó:** la carga de la cooperativa fallaba con error de columna inexistente.
- **Causa raíz:** la tabla usa `id` como clave primaria, pero el modelo consultaba `cooperativa_id` (nombre que sí usan otras tablas).
- **Solución:** se corrigieron las consultas a `id` y se añadió alias `id AS cooperativa_id` para mantener compatibilidad con el schema Pydantic.
- **Gravedad:** Alta. **Estado:** Resuelta.
- **Evidencia:** commit `a26310b` (2026-05-29).

### INC-21 · Conexión sin `client_encoding=utf8`: acentos corruptos
- **Área:** Base de datos.
- **Qué se detectó:** nombres con tildes y "ñ" se guardaban o mostraban con caracteres corruptos.
- **Causa raíz:** la conexión psycopg2 y el script no fijaban explícitamente la codificación del cliente.
- **Solución:** se añadió `client_encoding="utf8"` a la `Connection` y `SET client_encoding` en `script.sql`.
- **Gravedad:** Media. **Estado:** Resuelta.
- **Evidencia:** commit `cdbce98` (2026-06-01).

### INC-22 · Schemas Pydantic no coincidían con la nulabilidad real de la BD
- **Área:** Base de datos / Schemas.
- **Qué se detectó:** campos `NOT NULL` en la BD (por ejemplo `COOPERATIVA.codigo`) estaban declarados como opcionales en el schema, permitiendo intentos de INSERT con NULL; algunos `max_length` no coincidían con el `varchar(N)`.
- **Causa raíz:** los schemas se escribieron sin contrastar campo por campo contra `script.sql`.
- **Solución:** revisión de cada schema contra el esquema; los campos obligatorios pasan a `Field(...)`, los nullables a `str | None`, y los `max_length` se alinearon con la BD. Los schemas de tipo PATCH quedan como excepción por diseño.
- **Gravedad:** Media. **Estado:** Resuelta.
- **Evidencia:** `cdbce98` (migración de validaciones de `valor_cafe` a Pydantic); memoria técnica del proyecto.

### INC-23 · `COOPERATIVA` con campos `NOT NULL` sin `DEFAULT`: todo INSERT fallaba
- **Área:** Base de datos.
- **Qué se detectó:** ningún alta de cooperativa completaba; el formulario no envía ubicación geográfica y el modelo omitía siempre `fecha_registro`.
- **Causa raíz:** `fecha_registro NOT NULL` sin `DEFAULT` y `ubigeo_id NOT NULL` no provistos por el modelo ni por el formulario.
- **Solución:** `fecha_registro` pasa a `DEFAULT NOW()` y `ubigeo_id` a nullable en `script.sql`; regla documentada de que todo campo `NOT NULL` debe tener `DEFAULT` o proveerse explícitamente en el INSERT.
- **Gravedad:** Alta. **Estado:** Resuelta.
- **Evidencia:** `a26310b` (2026-05-29), `cdbce98` (2026-06-01); memoria técnica del proyecto.

### INC-24 · Dos dependencias de auth divergentes en las rutas
- **Área:** Autenticación.
- **Qué se detectó:** algunas rutas de página usaban `jwt_token_requerido` (que lanza `HTTPException 401`) en lugar de `obtener_usuario_actual` (que redirige a `/auth/login`), produciendo errores 401 en pantalla en vez de redirección.
- **Causa raíz:** convivencia de dos helpers de autenticación con semánticas distintas sin criterio uniforme.
- **Solución:** se sustituyó `jwt_token_requerido` por `obtener_usuario_actual` en todas las rutas de página; el helper de API se reserva para endpoints JSON.
- **Gravedad:** Media. **Estado:** Resuelta.
- **Evidencia:** commit `cdbce98` (2026-06-01).

### INC-25 · BOM UTF-8 de PowerShell rompía la carga de JS
- **Área:** Frontend / Diseño.
- **Qué se detectó:** los combo box de `tipo_documento` y `tipo_grano` no cargaban datos; el JS fallaba de forma silenciosa.
- **Causa raíz:** `Set-Content -Encoding UTF8` en PowerShell 5.1 antepone un BOM (`EF BB BF`) que el navegador no tolera al inicio del archivo.
- **Solución:** escribir los archivos sin BOM (`[System.IO.File]::WriteAllText` con `UTF8Encoding($false)`), o directamente con el editor. Registrado como trampa recurrente.
- **Gravedad:** Alta. **Estado:** Resuelta.
- **Evidencia:** memoria técnica del proyecto (errores conocidos).

### INC-26 · Errores de sintaxis JS que tumbaban el script completo
- **Área:** Frontend / Diseño.
- **Qué se detectó:** un fallo puntual en una función dejaba sin funcionar todo el script de la página (combos, validaciones, botones).
- **Causa raíz:** dentro de un IIFE, (a) helpers declarados como `const` flecha se usaban antes de su definición (temporal dead zone) y (b) una función `async` sin su llave `}` de cierre absorbía el resto del código y producía un `SyntaxError` global.
- **Solución:** los helpers llamados desde varios puntos se declaran como `function nombre()` (hoisted); revisión de balanceo de llaves en funciones `async` con `try/catch`. Posteriormente se extrajo todo el JS inline a archivos externos en `src/static/js/`.
- **Gravedad:** Alta. **Estado:** Resuelta.
- **Evidencia:** memoria técnica del proyecto; memoria de arquitectura JS del frontend.

### INC-27 · Acceso a campos de API con forma equivocada
- **Área:** Frontend / Diseño.
- **Qué se detectó:** el autocompletado de persona y las cascadas de ubigeo quedaban vacíos.
- **Causa raíz:** el código accedía a `data.persona.nombre` y `dep.ubigeo` cuando las APIs devuelven campos planos (`data.nombres`, `data.apellido_paterno`) y objetos `{codigo, nombre}`.
- **Solución:** se ajustó el acceso a la forma real de cada respuesta y se fijó la regla de copiar literalmente la lógica entre páginas sin "adaptar" nombres de campos.
- **Gravedad:** Media. **Estado:** Resuelta.
- **Evidencia:** memoria técnica del proyecto (errores conocidos).

### INC-62 · Prácticas de calidad de dataset y trazabilidad de experimentos planificadas sin ejecutar
- **Área:** Detección / ML (Dataset).
- **Qué se detectó:** el backlog original de Scrum definía criterios formales de aseguramiento de calidad para esta etapa — acuerdo inter-anotador (IRA) ≥85% con un experto, validación de duplicados/fuga de datos entre splits por hash MD5, y seguimiento de experimentos de entrenamiento con MLflow — que nunca se ejecutaron ni quedaron registrados en ningún artefacto del proyecto.
- **Causa raíz:** el etiquetado y la consolidación del dataset los realizó una sola persona (el propio tesista) sin un segundo experto disponible para calcular acuerdo inter-anotador, y no se incorporó herramienta de tracking de experimentos por el volumen de trabajo y los plazos del cronograma.
- **Solución (parcial):** se sustituyó por controles informales que sí quedaron documentados: nomenclatura trazable `_o_`/`_p_` por origen de imagen (INC-09) y descarte manual de imágenes borrosas o con reflejos (INC-10). Dan trazabilidad y calidad básica, pero no las métricas formales planificadas.
- **Gravedad:** Media. **Estado:** Mitigada (control informal en su lugar; sin cifra real de IRA ni validación de fuga por hash).
- **Evidencia:** `docs/documentacion/Product_Backlog_Sprints.md` (PBI-06 "IRA ≥85% con experto", PBI-07 "Split sin data leakage (MD5)", PBI-08 "entrenar con seguimiento MLflow"); ausencia de `mlflow` en `requirements.txt` y en el resto del repositorio (verificado por búsqueda).

---

## 5. Sprint 3 — Funcionalidades complementarias e integración

**Cronograma:** Semanas 5-6. **CRISP-ML(Q):** Fase 4 (Evaluación) e inicio de Fase 5 (Despliegue).
**Objetivo del Sprint:** desarrollar funcionalidades complementarias e integrarlas al núcleo, ejecutar pruebas de integración, mejorar el manejo de errores, revisar seguridad y persistencia, integrar el modelo validado dentro del backend (clasificación en tiempo real), establecer la comunicación software-hardware (cámara, microcontrolador, actuador) y hacer las primeras pruebas de latencia del pipeline completo.

### INC-28 · Streaming MJPEG con ruido: se enviaban bytes BGR crudos
- **Área:** Integración / Cámara.
- **Qué se detectó:** el `<img src="/video/stream">` mostraba pantalla negra o ruido.
- **Causa raíz:** el bucle de captura enviaba `frame.tobytes()` (datos BGR sin comprimir) en lugar de un JPEG; además convivían dos "modos" (passthrough y re-encode), uno de ellos roto.
- **Solución:** se codifica siempre a JPEG con `cv2.imencode()` y se eliminó el modo passthrough; una sola ruta de datos.
- **Gravedad:** Crítica (sin vídeo no hay monitoreo). **Estado:** Resuelta.
- **Evidencia:** commit `1fbff88` (2026-05-26).

### INC-29 · `monitoreo.html` apuntaba a `/camara/stream` (vídeo sin YOLO)
- **Área:** Integración.
- **Qué se detectó:** el monitoreo mostraba la cámara cruda, sin bounding boxes ni conteo de defectos.
- **Causa raíz:** el frontend consumía el endpoint de cámara sin procesar en lugar del endpoint del tracker.
- **Solución:** se cambió el stream a `/video/stream` (frames anotados por YOLO + ByteTrack).
- **Gravedad:** Alta. **Estado:** Resuelta.
- **Evidencia:** commit `da3b1b5` (2026-05-26).

### INC-30 · Rutas de vídeo sin prefijo `/video/` y sin `Depends()` de auth
- **Área:** Integración / Autenticación.
- **Qué se detectó:** las llamadas a `/lote/conteo` y `/lote/generar-reporte` daban 404 y los endpoints POST no validaban sesión.
- **Causa raíz:** el frontend usaba rutas sin el prefijo del router y en las firmas de los endpoints faltaba la inyección `= Depends(...)` de la dependencia de autenticación.
- **Solución:** se corrigieron las rutas a `/video/lote/...` y se añadió `Depends()` a todos los endpoints del router de vídeo.
- **Gravedad:** Alta. **Estado:** Resuelta.
- **Evidencia:** commit `da3b1b5` (2026-05-26).

### INC-31 · `NameError` por `Depends` no importado en `routes/video.py`
- **Área:** Integración.
- **Qué se detectó:** el arranque de la app fallaba tras añadir la autenticación a las rutas de vídeo.
- **Causa raíz:** se usó `Depends` sin importarlo desde `fastapi`.
- **Solución:** se añadió el import faltante.
- **Gravedad:** Crítica (la app no levantaba). **Estado:** Resuelta.
- **Evidencia:** commit `0f19b60` (2026-05-26).

### INC-32 · Sin cámara física el pipeline no se podía probar
- **Área:** Cámara / Integración.
- **Qué se detectó:** desarrollar y probar el pipeline YOLO exigía tener la cámara ELP conectada.
- **Causa raíz:** `CamaraService` solo abría dispositivos reales.
- **Solución:** se añadió `CamaraSimulada` como fallback automático (genera frames con granos sintéticos a 60 fps) cuando no hay hardware.
- **Gravedad:** Media. **Estado:** Resuelta con deuda técnica (la cámara simulada se retira en la simplificación del Sprint 4).
- **Evidencia:** commit `070bb4b` (2026-05-26).

### INC-33 · Cámara no se liberaba y quedaba bloqueada entre sesiones
- **Área:** Cámara.
- **Qué se detectó:** tras detener el monitoreo, reiniciar la captura fallaba porque el dispositivo seguía tomado.
- **Causa raíz:** cierre incompleto del `VideoCapture` y del hilo de captura.
- **Solución:** se mejoró el cierre de la cámara y se añadió `POST /video/liberar-camara` para forzar la liberación; más adelante la cámara queda preconectada durante toda la vida de la app y el tracker deja de cerrarla al detener.
- **Gravedad:** Alta. **Estado:** Resuelta.
- **Evidencia:** commits `6b8d3f4` (2026-05-26), `240f5a4` (2026-06-11).

### INC-34 · Doble decodificación/codificación JPEG en el pipeline
- **Área:** Cámara / Integración.
- **Qué se detectó:** consumo de CPU innecesario: la cámara codificaba a JPEG, el tracker lo decodificaba a BGR y volvía a codificar.
- **Causa raíz:** interfaz entre `CamaraService` y `TrackerService` basada en JPEG en ambos sentidos.
- **Solución:** `CamaraService` expone `obtener_frame_bgr()` con el último frame BGR crudo; el tracker lo consume directo y solo se codifica a JPEG el frame anotado final para el navegador. El endpoint de stream espera entre frames (~30 fps) y duerme cuando no hay frame para reducir CPU.
- **Gravedad:** Media. **Estado:** Resuelta.
- **Evidencia:** commit `8c2a4ee` (2026-06-08).

### INC-35 · IDs de ByteTrack se reiniciaban a 1-2 tras pausas de la faja
- **Área:** Detección / ML.
- **Qué se detectó:** el conteo de granos únicos del lote se quedaba en 1 o 2; cada pausa de la faja "reiniciaba" la numeración.
- **Causa raíz:** ByteTrack reinicia su contador interno cuando pasan varios frames sin detecciones.
- **Solución:** el tracker mantiene su propio mapeo `_bytetrack_a_global` que nunca retrocede; `resetear_conteo()` lo limpia al iniciar un lote nuevo. El `track_buffer: 10` de `bytetrack.yaml` es intencional: la resistencia a pausas la da el mapeo global, no el buffer.
- **Gravedad:** Alta (invalidaba el conteo del lote). **Estado:** Resuelta.
- **Evidencia:** commit `0c06b79` (2026-06-15); `src/ml/tracker.py`, `src/ml/bytetrack.yaml`.

### INC-36 · Crecimiento ilimitado de memoria en el acumulador de detecciones
- **Área:** Detección / ML.
- **Qué se detectó:** si la faja quedaba en marcha con un grano detenido bajo la cámara, `conteo_ids_confianza` crecía sin límite.
- **Causa raíz:** el historial de detecciones por track era una lista sin cota.
- **Solución:** se cambió a `defaultdict(lambda: deque(maxlen=30))` y se añadió limpieza de IDs inactivos al final de cada frame.
- **Gravedad:** Media. **Estado:** Resuelta.
- **Evidencia:** commit `0c06b79` (2026-06-15).

### INC-37 · Latencia alta en la primera inferencia
- **Área:** Detección / ML.
- **Qué se detectó:** el primer frame procesado tardaba mucho más que los siguientes (inicialización de ByteTrack y JIT de PyTorch), con salto visible al iniciar el monitoreo.
- **Causa raíz:** no había calentamiento del modelo.
- **Solución:** al cargar el tracker se hace un warmup con un frame negro 640×640; se detecta el dispositivo (`cuda` / `cpu`) automáticamente y se registra en el log. La cámara además se preconecta en el arranque de la app.
- **Gravedad:** Media. **Estado:** Resuelta.
- **Evidencia:** commits `8c2a4ee` (2026-06-08), `240f5a4` (2026-06-11), `0c06b79` (2026-06-15).

### INC-38 · Filtro de tamaño de grano descalibrado
- **Área:** Detección / ML.
- **Qué se detectó:** se contaban objetos que no eran granos (ruido, sombras) o se descartaban granos válidos según el tamaño del bounding box.
- **Causa raíz:** los límites `GRANO_MIN_PX` / `GRANO_MAX_PX` se fijaron sin medición de campo.
- **Solución:** calibración iterativa (`GRANO_MAX_PX` 200 → 500 → 300; `GRANO_MIN_PX` 8 → 50) y visualización de depuración con cajas grises para los granos filtrados, mostrando sus dimensiones. Valores actuales: 50 y 300 px.
- **Gravedad:** Media. **Estado:** Resuelta (sujeta a recalibración cuando se ajuste el zoom del lente).
- **Evidencia:** commits `8c2a4ee` (2026-06-08), `240f5a4` (2026-06-11), `dcf68a8` (2026-07-04); `src/ml/models/yolov26n_2cls/constants.py`.

### INC-39 · Pesos del modelo no versionables en Git
- **Área:** Detección / ML / Infraestructura.
- **Qué se detectó:** los archivos `best.pt` / `best.onnx` (varios MB) no deben ir al repositorio, pero sin ellos la app no arranca.
- **Causa raíz:** límite práctico de tamaño en Git para binarios que cambian con cada reentrenamiento.
- **Solución:** los pesos se distribuyen por Google Drive y se colocan en `src/ml/models/{modelo}/`; el tracker prueba `best.onnx` primero y cae a `best.pt`.
- **Gravedad:** Media. **Estado:** Mitigada (requiere paso manual en cada instalación).
- **Evidencia:** commit `0c06b79` (2026-06-15); `CLAUDE.md`; `docs/DOCUMENTACION_SISTEMA.md`.

### INC-40 · Reset del Arduino por DTR al reabrir el puerto serial
- **Área:** Arduino / Hardware.
- **Qué se detectó:** comandos enviados justo después de reconectar el puerto se perdían aunque la librería reportara éxito.
- **Causa raíz:** al reabrir el puerto, la línea DTR reinicia el Arduino Uno (~2 s de bootloader).
- **Solución parcial:** al recibir `SISTEMA:LISTO` con el motor marcado como activo, `arduino_serial` reenvía `ON` automáticamente; se registran los errores de conexión/lectura/escritura y se descartan las escrituras cuando el puerto no está disponible.
- **Gravedad:** Media. **Estado:** Mitigada (el reenvío no cubre el estado del servo; `arduino_serial.py` y `servo_controller.py` son archivos restringidos, no se modifican sin autorización).
- **Evidencia:** commit `240f5a4` (2026-06-11); memoria de la cadena de tiempos del servo.

### INC-41 · Windows suspendía el puerto USB serial por inactividad
- **Área:** Arduino / Hardware.
- **Qué se detectó:** tras un rato sin tráfico, la comunicación con el Arduino se congelaba.
- **Causa raíz:** gestión de energía del puerto USB de Windows.
- **Solución:** hilo `arduino-keepalive` que escribe una línea vacía cada 20 s; reconexión automática con throttle de 5 s si el hilo lector cae.
- **Gravedad:** Media. **Estado:** Resuelta.
- **Evidencia:** commit `240f5a4` (2026-06-11).

### INC-42 · `bfcache` mostraba monitoreo ya finalizado
- **Área:** Frontend / Diseño.
- **Qué se detectó:** al volver atrás en el navegador se veía la pantalla de monitoreo de una evaluación que ya estaba finalizada.
- **Causa raíz:** el back/forward cache del navegador restaura la página sin recargar; las plantillas se cacheaban.
- **Solución:** cabeceras `Cache-Control: no-store` / `no-cache` para las plantillas de análisis y monitoreo, endpoint `GET /evaluacion/{id}/estado`, handler `pageshow` que detecta restauración desde bfcache y redirige, y navegación con `window.location.replace` para no ensuciar el historial.
- **Gravedad:** Media. **Estado:** Resuelta.
- **Evidencia:** commit `240f5a4` (2026-06-11).

### INC-43 · `max-width` heredado de `perfil.css` dejaba layouts a medio ancho
- **Área:** Frontend / Diseño.
- **Qué se detectó:** en páginas que extienden `perfil.css` (por ejemplo la configuración de cooperativa) el formulario quedaba centrado, dejando franjas de fondo a los lados.
- **Causa raíz:** `perfil.css` define `.perfil-layout { max-width: 1100px; margin: 0 auto; }` y gana por orden de carga sobre overrides sin `!important`.
- **Solución:** las páginas full-width sobrescriben `.perfil-container`, `.perfil-layout`, `.perfil-content` y `.perfil-section` con `max-width: none !important; margin: 0 !important; width: 100%`. Regla general adoptada: los layouts ocupan todo el ancho disponible salvo indicación contraria.
- **Gravedad:** Baja. **Estado:** Resuelta.
- **Evidencia:** memoria de estilo de código; memoria de errores conocidos.

### INC-63 · Fase 4 CRISP-ML(Q) (validación formal, matriz de confusión, pruebas de robustez) no se ejecutó
- **Área:** Detección / ML.
- **Qué se detectó:** el cronograma exige, en esta etapa, validar formalmente el modelo seleccionado sobre el conjunto de prueba nunca visto durante entrenamiento (precision, recall, F1-score y mAP por clase), analizar la matriz de confusión e interpretar los resultados, y probar robustez ante variaciones de iluminación y condiciones de captura. Solo se reportaron mAP50 y mAP50-95 del `yolov8n` (0.767 / 0.757); nunca se calcularon ni documentaron precision, recall o F1, no hay matriz de confusión y no se ejecutaron pruebas sistemáticas de robustez.
- **Causa raíz:** el proyecto pasó directamente de la Fase 3 (comparación de arquitecturas) a la integración en el backend (Fase 5) para poder demostrar el flujo completo dentro del cronograma, dejando la garantía de calidad formal de Fase 4 como pendiente declarado en la propia documentación del proyecto.
- **Solución (parcial):** el sesgo del modelo hacia "defecto" (~40% de granos buenos mal clasificados en pruebas) se detectó de forma indirecta al operar el pipeline en vivo, no mediante la Fase 4 planificada; se mitigó parcialmente con `MARGEN_DEFECTO` (exige que la confianza acumulada de defecto supere a la de la clase sana por un factor) en vez de una recalibración basada en una matriz de confusión real.
- **Gravedad:** Alta (una validación formal habría detectado el sesgo del modelo antes de integrarlo al flujo de separación física, que hoy puede desviar granos buenos por error). **Estado:** Abierta.
- **Evidencia:** `docs/documentacion/avance-tecnico-completo-2026.md` (tabla "Pendientes técnicos", fila "Fase 4 CRISP-ML(Q)"); `docs/registro-avances.md` (líneas 230 y 264, "Fase 4: Garantía de calidad (validación de métricas, robustez)" listada como pendiente); `CLAUDE.md` (sección del módulo ML, sesgo ~40% falsos defectos).

---

## 6. Sprint 4 — Finalización, estabilización y monitoreo

**Cronograma:** Semanas 7-8. **CRISP-ML(Q):** Fase 5 (Despliegue, cierre) y Fase 6 (Monitoreo y Mantenimiento).
**Objetivo del Sprint:** completar funcionalidades pendientes, integrar todos los componentes, ejecutar pruebas de todos los escenarios y de aceptación, corregir defectos finales, cerrar la interfaz de tiempo real (visualización, conteo, reportes exportables), ejecutar validación técnica local (iluminación, velocidad del transportador, muestras con defectos conocidos), implementar un mecanismo básico de monitoreo de la calidad de las detecciones y documentar la metodología.

### INC-44 · Celda de carga HX711 inestable a 115200 baud en clones de Arduino
- **Área:** Arduino / Hardware.
- **Qué se detectó:** lecturas de peso erráticas y pérdida de comunicación cuando se subía el baudrate para mejorar el muestreo.
- **Causa raíz:** los clones de Arduino Uno con resonador cerámico (en vez de cristal de cuarzo) no mantienen 115200 baud de forma fiable.
- **Solución:** se retiró el código del HX711 del firmware; el peso del grano bueno se ingresa manualmente en la interfaz. El enlace serie se mantiene a 9600 baud.
- **Gravedad:** Alta (elimina una entrada automática del flujo). **Estado:** Resuelta con deuda técnica (pesaje manual).
- **Evidencia:** commit `dcf68a8` (2026-07-04); `docs/LIBRERIAS.md`, `docs/DOCUMENTACION_SISTEMA.md`.

### INC-45 · Delay del servo mal calculado: separaba tarde
- **Área:** Servo separador.
- **Qué se detectó:** el servo desviaba el grano defectuoso demasiado tarde; el grano ya había pasado.
- **Causa raíz:** sin el valor en `.env`, `config.py` recalcula el delay con un modelo lineal PWM (referencia 220 → 0.5 s) que a `FAJA_VELOCIDAD_PWM = 150` daba 0.733 s, unos 0.23 s tarde. Además el delay se programaba después de la inferencia YOLO, sumando una latencia variable (30 ms en GPU frente a 150-300 ms en CPU).
- **Solución:** `.env` fija `SERVO_DELAY_S = 0.5` (calibrado físicamente y con prioridad sobre el cálculo); el delay se programa desde el timestamp de captura del frame (`time.monotonic()` en el bucle de la cámara), que se propaga por todo el pipeline hasta `servo_controller.solicitar(..., t_referencia=ts)`.
- **Gravedad:** Alta. **Estado:** Resuelta.
- **Evidencia:** commits `787a7ac` (2026-07-08), `199e023` (2026-07-11); memoria de la cadena de tiempos del servo.

### INC-46 · Servo atascado en DEFECTO por comando `SERVO:BUENO` perdido
- **Área:** Servo separador.
- **Qué se detectó:** tras separar un defecto, el servo se quedaba en la posición de defecto y desviaba también granos buenos.
- **Causa raíz:** si el `SERVO:BUENO` de retorno se perdía en el enlace serie, no había reintento.
- **Solución:** `_enviar_con_reintento()` con 3 intentos separados 50 ms.
- **Gravedad:** Alta. **Estado:** Resuelta.
- **Evidencia:** commit `787a7ac` (2026-07-08); memoria de la cadena de tiempos del servo.

### INC-47 · Parpadeo DEFECTO→BUENO→DEFECTO con defectos consecutivos
- **Área:** Servo separador.
- **Qué se detectó:** con granos defectuosos seguidos, el servo volvía a BUENO y regresaba a DEFECTO, con retraso acumulado por el `sleep` bloqueante del hold.
- **Causa raíz:** el hold no consideraba la cola de solicitudes pendientes.
- **Solución:** durante el hold el controlador sigue evaluando la cola; si otro defecto vence dentro del hold, lo extiende en lugar de volver a BUENO.
- **Gravedad:** Media. **Estado:** Resuelta.
- **Evidencia:** commit `787a7ac` (2026-07-08); memoria de la cadena de tiempos del servo.

### INC-48 · `script.sql`: `incidencias` añadida tarde e inserts con UUID fijos
- **Área:** Base de datos.
- **Qué se detectó:** la columna `incidencias jsonb` (eventos anómalos del monitoreo, apertura de tapa, etc.) no existía cuando el backend ya intentaba escribirla; los inserts de prueba usaban UUID codificados a mano que no correspondían a filas reales.
- **Causa raíz:** el esquema no se actualizó al mismo tiempo que la funcionalidad de registro de incidencias; datos semilla frágiles.
- **Solución:** se añadió `incidencias jsonb` (y más adelante `total_defectos` / `total_buenos`) a `EVALUACION`; los inserts de prueba pasan a usar subconsultas (`SELECT id FROM PERSONA WHERE num_documento = ...`) en lugar de UUID literales. Se eliminó `migration_auditoria.sql` obsoleto.
- **Gravedad:** Media. **Estado:** Resuelta.
- **Evidencia:** commits `4198fca` (2026-07-04), `758d35c` (2026-07-02), `dcf68a8` (2026-07-04).

### INC-49 · Historial de precios de café se sobrescribía al actualizar
- **Área:** Base de datos / Negocio.
- **Qué se detectó:** al corregir un precio se perdía el valor anterior, rompiendo la trazabilidad del pago histórico.
- **Causa raíz:** la actualización hacía `UPDATE` sobre la fila existente en lugar de registrar un nuevo precio con fecha.
- **Solución:** se preserva el historial (`VALOR_CAFE` acumula registros por rango y fecha); las consultas de pago usan el precio vigente a la fecha de la evaluación.
- **Gravedad:** Alta. **Estado:** Resuelta.
- **Evidencia:** commit `787a7ac` (2026-07-08).

### INC-50 · Módulo `inference.py` legacy y ramas muertas en el tracker
- **Área:** Detección / ML.
- **Qué se detectó:** `inference.py` ya no se usaba en el flujo (ByteTrack está integrado en `tracker.py`) y el tracker arrastraba fallback y cascada de constantes obsoletas.
- **Causa raíz:** acumulación de código de iteraciones anteriores.
- **Solución:** se eliminó `inference.py` y se simplificó `tracker.py` para usar solo `yolov26n_2cls`, quitando fallback/cascada y constantes muertas; se limpiaron endpoints y dependencias no usadas.
- **Gravedad:** Baja. **Estado:** Resuelta.
- **Evidencia:** commit `787a7ac` (2026-07-08).

### INC-51 · `config.py` estaba en `.gitignore`
- **Área:** Infraestructura.
- **Qué se detectó:** cada entorno mantenía su propia copia de la configuración; los cambios de parámetros (delays de servo, switches de modelo) no se compartían.
- **Causa raíz:** `config.py` se excluyó del control de versiones por contener credenciales.
- **Solución:** se incorporó `src/config.py` al repositorio con configuración centralizada; los secretos reales siguen en `.env` (con fallback a literales solo para desarrollo local — ver INC-11).
- **Gravedad:** Media. **Estado:** Resuelta.
- **Evidencia:** commit `dcf68a8` (2026-07-04).

### INC-52 · Documentación de infraestructura con datos obsoletos
- **Área:** Documentación.
- **Qué se detectó:** la documentación refería la base de datos como `coffeeren`, no exigía PostgreSQL 18 y omitía la descarga de los pesos del modelo.
- **Causa raíz:** la documentación no se actualizó al ritmo de los cambios de infraestructura.
- **Solución:** se corrigió: la BD es `tesis_prj`, se requiere PostgreSQL 18 (el esquema usa `uuidv7()` nativo), baudrate Arduino 9600, y la instalación debe incluir la descarga de `best.onnx` a `src/ml/models/yolov26n_2cls/` (sin él la app no arranca). Se añadió `docs/DOCUMENTACION_SISTEMA.md`.
- **Gravedad:** Media. **Estado:** Resuelta.
- **Evidencia:** commits `199e023` (2026-07-11), `33d8584` (2026-07-11); `docs/DOCUMENTACION_SISTEMA.md`.

### INC-53 · Cámara cae a YUY2 (~9 fps) por no fijar MJPEG antes del primer `read()`
- **Área:** Cámara (CRISP-ML(Q) Fase 6, validación técnica local).
- **Qué se detectó:** con la faja en movimiento no se detectan todos los granos: saltan de posición entre frames.
- **Causa raíz:** la cámara ELP AR0234 es USB 2.0; 1080p a 90 fps solo cabe en el bus en formato MJPEG. Si el driver no negocia MJPEG (o si el FOURCC se fija después del primer `read()`), cae a YUY2 y el FPS se desploma a ~5-9. También influyen cable largo, hub o puerto USB compartido.
- **Solución:** `camara_service.py` abre con **Media Foundation** (`CAP_MSMF`, luego `CAP_ANY` y `CAP_DSHOW`): con `opencv-python-headless` en Windows, DirectShow entregaba YUY2 a ~5 fps incluso para la ELP. Se fija `OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS=0` antes de importar `cv2`, y `_configurar_captura()` fija FOURCC MJPG → resolución → FPS antes del primer `read()`. Como MSMF no reporta el FOURCC, el formato se verifica midiendo el FPS real. La cámara se elige por nombre de dispositivo ("Global Shutter Camera", vía `pygrabber`) porque la webcam interna también negocia MJPEG. Configuración en `config.py`: `CAM_INDICE/WIDTH/HEIGHT/FPS/EXPOSURE/AUTO_EXPOSURE_MANUAL/WB_TEMP` con override por `.env`.
- **Gravedad:** Crítica (compromete la exhaustividad del conteo). **Estado:** Resuelta (el ensayo de latencia del 2026-09-22 registró la ELP a 1920×1080 con ~96 fps reales).
- **Evidencia:** commits `1553477` (2026-09-03) y `93cd39a` (2026-09-22); `docs/hardware-camara.md`; `docs/evidencias/analisis_latencia_20260922.md`.

### INC-54 · Granos que se tocan no generan bounding box
- **Área:** Detección / ML (CRISP-ML(Q) Fase 4 y 6).
- **Qué se detectó:** granos que salen juntos de la faja a veces no dibujan caja; granos aislados a veces sí y a veces no.
- **Causa raíz:** el umbral de confianza que se pasaba a `model.track(conf=...)` descartaba detecciones antes de que ByteTrack usara su banda de baja confianza; y el NMS por defecto suprimía cajas de granos contiguos.
- **Solución (en curso):** `CONF_THRESHOLD` bajado a 0.15 como piso; `model.track(iou=0.80)` (NMS permisivo); umbrales de `bytetrack.yaml` bajados (`track_high_thresh` 0.25 → 0.20, `track_low_thresh` 0.1 → 0.05, `new_track_thresh` 0.25 → 0.20). Después (2026-09-22): detección por grilla de 3×3 recortes con solape de 200 px inferidos en un solo lote (cada grano llega al modelo a una escala cercana a la de entrenamiento) y fusión de cajas consciente de la costura (solo une cajas de recortes distintos y rechaza envolventes mayores a 1.6×), lo que corrigió el subconteo de granos juntos. Pendiente: recorte de un ROI de la faja antes de la inferencia.
- **Gravedad:** Alta. **Estado:** Mitigada (falta el ROI y la validación con faja real).
- **Evidencia:** commits `1553477` (2026-09-03) y `93cd39a` (2026-09-22); `src/ml/tracker.py`, `src/ml/bytetrack.yaml`, `src/ml/models/yolov26n_2cls/constants.py`.

### INC-55 · Detecciones débiles y efímeras accionaban el servo
- **Área:** Detección / ML / Servo separador.
- **Qué se detectó:** con el piso de confianza bajo (INC-54), un track de un solo frame y baja confianza podía disparar la separación física de un grano.
- **Causa raíz:** el servo se solicitaba en cuanto aparecía un `track_id` nuevo, sin exigir respaldo estadístico.
- **Solución (en curso):** compuerta `_evidencia_suficiente(track_id)` antes de `servo_controller.solicitar()`: al menos `SERVO_MIN_FRAMES` (2) detecciones acumuladas o una con confianza ≥ `SERVO_CONF_MIN` (0.45). Se guarda `_ts_primer_avistamiento[track_id]` para que la referencia temporal del servo siga siendo el primer frame del track aunque la solicitud se posponga (no se degrada la precisión del delay).
- **Gravedad:** Media. **Estado:** Mitigada (pendiente verificar en prueba real que la compuerta no deja defectos legítimos sin separar; `ML_DEBUG_SERVO=true` lista los tracks que salen sin servo).
- **Evidencia:** commit `1553477` (2026-09-03); `src/ml/tracker.py`.

### INC-56 · Foco y zoom manuales del lente, sin repetibilidad
- **Área:** Cámara / Hardware.
- **Qué se detectó:** cualquier roce del anillo de foco o zoom degrada toda la detección y obliga a recalibrar el filtro de tamaño de grano (INC-38).
- **Causa raíz:** el lente es un varifocal CCTV barato con zoom y foco manuales, no un lente de visión artificial. Cámara única y fija en el prototipo, sin presupuesto de reemplazo.
- **Solución propuesta:** bloquear los anillos de zoom y foco con sus tornillos una vez ajustados; ajustar el zoom para que el ancho útil de la faja llene el cuadro; documentar las medidas de geometría de trabajo. Candidato de reemplazo a futuro: AR0234 en USB 3.x con lente prima fijo M12.
- **Gravedad:** Media. **Estado:** Abierta (checklist de calibración física en `docs/hardware-camara.md`).
- **Evidencia:** `docs/hardware-camara.md`.

### INC-57 · Desenfoque por movimiento pese al global shutter
- **Área:** Cámara / Hardware.
- **Qué se detectó:** con la faja en marcha los granos salen con estela.
- **Causa raíz:** el global shutter elimina la distorsión geométrica (rolling shutter skew), no el motion blur, que depende del tiempo de exposición. Con AEC y luz insuficiente el sensor alarga la exposición (1/30-1/60 s).
- **Solución propuesta:** exposición manual corta (`CAM_EXPOSURE` en `.env`, p. ej. -6 ≈ 1/64 s) más iluminación difusa, potente y sin parpadeo; no compensar con ganancia (el ruido de AGC degrada la detección más de lo que ayuda el brillo).
- **Gravedad:** Media. **Estado:** Abierta (depende de instalar iluminación adecuada en el prototipo).
- **Evidencia:** `docs/hardware-camara.md`; `src/config.py` (`CAM_EXPOSURE`).

### INC-58 · Renombrado de `COOPERATIVA.direccion` a `ubicacion`
- **Área:** Base de datos.
- **Qué se detectó:** el término "dirección" no reflejaba bien el dato capturado (localidad / referencia geográfica) y generaba inconsistencia con la UI.
- **Causa raíz:** nombre de columna elegido en el diseño inicial.
- **Solución:** `script.sql` cambia `direccion varchar(255) NOT NULL UNIQUE` por `ubicacion`; se actualizan modelo, schema, servicio y plantilla de cooperativa, y los inserts de prueba.
- **Gravedad:** Baja. **Estado:** Resuelta (las bases creadas antes del cambio requieren renombrar la columna).
- **Evidencia:** commit `1553477` (2026-09-03); `src/database/script.sql`, `src/models/cooperativa.py`, `src/schemas/cooperativa.py`, `src/services/cooperativa_service.py`, `src/templates/cooperativa.html`.

### INC-59 · Endpoints y código muerto acumulado sin consumidor
- **Área:** Infraestructura / Backend.
- **Qué se detectó:** auditoría de las 4 capas (routes/services/models/schemas) cruzando cada endpoint contra sus consumidores reales (`fetch` en JS, `action`/`href` en plantillas, redirecciones, llamadas internas del backend). 13 endpoints más 1 alias sin ningún consumidor, con su cascada de métodos de servicio, métodos de modelo y schemas también sin uso.
- **Causa raíz:** scaffolding de CRUD completo que la UI nunca llegó a consumir (cooperativas), endpoints reemplazados que no se borraron (`/camara/*` → `/video/*`, ver INC-29), un endpoint JSON de login paralelo al formulario, y utilidades que quedaron sin cablear (tara de báscula, resolución de ubigeo por código completo).
- **Solución:** eliminados `POST /auth/api/login`, el router `/camara` completo (`GET /camara/stream`, `GET /camara/estado`), `POST /video/liberar-camara`, el alias `GET /registro-socios`, el CRUD sin uso de cooperativas (`GET`/`GET {id}`/`POST`/`DELETE`), `GET /perfil/usuarios/personas-disponibles`, `PATCH /perfil/usuarios/{id}/cambiar-contrasena`, `GET /ubigeo/{codigo}` y `POST /arduino/tare`, junto con su cascada en servicios, modelos y schemas. `camara_service` se conserva (lo usan el ciclo de vida de la app y el tracker); `arduino_serial.py` no se tocó. Verificado con `pyflakes` y `compileall` limpios, carga completa de la app (`/health` 200) y auditoría de arquitectura de 4 capas sin hallazgos.
- **Gravedad:** Baja. **Estado:** Resuelta.
- **Evidencia:** commit `46f1452` (2026-09-08); `src/main.py`, `src/routes/` (`auth_login`, `cooperativa`, `perfil`, `ubigeo`, `arduino`, `video`; `camara.py` eliminado), `src/services/` y `src/models/` (`cooperativa`, `perfil`, `persona`, `ubigeo`, `arduino`), `src/schemas/` (`auth`, `cooperativa`, `perfil`, `ubigeo`); documentación en `docs/API_VIDEO_STREAMING.md`, `docs/DOCUMENTACION_SISTEMA.md`, `docs/documentacion/arquitectura-sistema-clasificacion.md`, `docs/documentacion/avance-tecnico-completo-2026.md`.

### INC-60 · Mensajes de error divergentes entre backend y frontend
- **Área:** Integración / Frontend.
- **Qué se detectó:** el mismo error se veía con textos distintos según el origen. Ejemplo del disparador: el login mostraba "Credenciales incorrectas, intenta nuevamente." en pantalla pero un endpoint JSON paralelo (ya eliminado, INC-59) decía "Credenciales inválidas". Al cambiar un mensaje en el backend no siempre se reflejaba en la UI. Además, redacción heterogénea entre rutas ("No se pudo…" / "Error al…" / "Error al cargar…"), tildes faltantes y fugas de excepción (`detail=f"Error al iniciar: {str(e)}"`).
- **Causa raíz:** (1) los errores de validación de Pydantic llegaban como `detail: [{...}]` (lista de objetos) y el frontend los renderizaba como `[object Object]`, así que cada llamada `fetch` traía su propio literal de respaldo (`throw new Error(err.detail || 'texto fijo')`) que ganaba cuando `detail` no era una cadena; (2) cada ruta redactaba su 500/404 a mano, sin una convención; (3) algún `catch` descartaba `error.message` y mostraba un literal.
- **Solución:**
  - Backend — arreglo de raíz: handler `RequestValidationError` en `main.py` que aplana el 422 a `{"detail": "<frase en español>"}`. Traduce los códigos nativos de Pydantic (`string_too_short`, `greater_than`, `string_pattern_mismatch`, …) y deja intactos los mensajes de los validadores del schema (`raise ValueError("…")`), quitando el prefijo `"Value error, "`. Con esto, **cualquier** mensaje del backend llega al frontend como texto legible; cambiarlo donde se lanza se refleja en la UI sin tocar nada más.
  - Backend — consistencia: los mensajes son **literales en español en el sitio donde se lanzan** (`raise HTTPException(...)` / `raise ValueError(...)`), con una sola convención: "No se pudo &lt;verbo&gt; &lt;objeto&gt;." para 500, "No se encontró &lt;entidad&gt;." para 404, frase completa con tilde y punto, sin filtrar trazas ni `str(e)`. Se descartó un catálogo central en `utilities/` porque cada mensaje aparece una sola vez (sin duplicación real) y forzaba a saltar de archivo para leerlo.
  - Backend — dedup real: el validador de teléfono, repetido 3× idéntico en `schemas/perfil.py`, se unificó en un `Annotated`/`AfterValidator` local del propio archivo. La dependencia de permisos `verificar_admin` de `routes/tipo_grano.py` (copia de `require_admin_o_gerente`) se reemplazó por la compartida.
  - Frontend: `src/static/js/http.js` (`CoffeeHttp.mensajeError(res, fallback)`) como único extractor de mensajes de error; los ~25 sitios `fetch` de 8 archivos JS pasan a `throw new Error(await CoffeeHttp.mensajeError(res, 'respaldo'))`. Se eliminó el helper local duplicado `mensajeHttpError` de `valor_cafe.js` y una función muerta (`consultarCaficultor`) en `caficultor.js`. El literal del frontend queda solo como respaldo si el backend no envía nada legible.
- **Gravedad:** Media. **Estado:** Resuelta.
- **Evidencia:** commit `46f1452` (2026-09-08); `src/main.py`, `src/static/js/http.js` (nuevo), `src/templates/main.html`, todas las rutas de `src/routes/`, los servicios con `raise ValueError` de `src/services/`, `src/schemas/perfil.py`, `src/utilities/jwt_required.py`, y `src/static/js/{caficultor,registro,perfil,monitoreo,analisis,cooperativa,valor_cafe,test}.js`. Verificado: login/403/422 (nativo y custom) devuelven `detail` como cadena en español; `pyflakes`/`compileall`/`node --check` limpios; suite `verificacion_incremento_1` 3/3; auditoría de arquitectura sin hallazgos.

### INC-61 · Auto-desactivación de cuenta y sesión que sobrevive a la desactivación
- **Área:** Autenticación.
- **Qué se detectó:** desde `PATCH /perfil/usuarios/{id}/estado` un Gerente/Administrador podía desactivar su propia cuenta. Peor aún: desactivar a **cualquier** usuario (uno mismo u otro) no tenía efecto sobre una sesión ya iniciada — el JWT en cookie sigue siendo válido 7 días, así que la cuenta desactivada seguía operando con normalidad hasta que el token expiraba.
- **Causa raíz:** (1) `perfil_service.cambiar_estado_usuario` solo protegía al usuario `jbecerrac`, no al solicitante; (2) `obtener_usuario_actual` (`utilities/jwt_required.py`) validaba únicamente la firma y expiración del token, nunca el estado real de la cuenta en la BD.
- **Solución:**
  - Guard de auto-desactivación en el servicio: `cambiar_estado_usuario` recibe `solicitante_id`; si el destino es uno mismo y el nuevo estado no es 'A', lanza `ValueError("No puedes desactivar tu propia cuenta.")` (→ HTTP 400). La ruta pasa `user.get("personal_id")`.
  - Sesión atada al estado: `obtener_usuario_actual`, tras validar el token, llama `auth_service.cuenta_habilitada(personal_id)` (nuevo), que delega en `Personal.esta_activo(...)` (nuevo, `SELECT estado FROM personal WHERE personal_id=%s`). Si la cuenta no está activa → `RequerirLoginException` → redirect a `/auth/login`. Ante fallo de BD devuelve `True` (fail-open, para no expulsar a todos por un error transitorio; el token sigue siendo criptográficamente válido). Una petición extra de una columna con índice de PK por request autenticada.
  - `AuthService` gana un singleton de módulo `auth_service` (mismo patrón que `auditoria_service`); `auth_login.py` deja de instanciarlo localmente.
  - Frontend: `cooperativa.html` inyecta `MI_PERSONAL_ID`; en la tabla de usuarios, la fila propia muestra "Tu cuenta" en vez del botón Desactivar (afordancia; la regla vive en el backend).
- **Gravedad:** Alta. **Estado:** Resuelta.
- **Evidencia:** commit `46f1452` (2026-09-08); `src/models/personal.py`, `src/services/auth_service.py`, `src/services/perfil_service.py`, `src/utilities/jwt_required.py`, `src/routes/auth_login.py`, `src/routes/perfil.py`, `src/templates/cooperativa.html`, `src/static/js/cooperativa.js`. Verificado con TestClient: auto-desactivación → 400; un admin desactiva a otro usuario → la siguiente petición de ese usuario redirige a `/auth/login` (página y endpoint JSON); reactivar → vuelve a funcionar; `jbecerrac` sigue protegido. `pyflakes`/`compileall` limpios, `verificacion_incremento_1` 3/3, auditoría de arquitectura sin hallazgos.

### INC-64 · Monitoreo de calidad de detecciones (Fase 6) y validación en campo con operarios reales sin implementar
- **Área:** Detección / ML / Integración.
- **Qué se detectó:** el cronograma exige, en el cierre del proyecto, implementar un mecanismo básico de monitoreo de la calidad de las detecciones a lo largo del tiempo y ejecutar validación técnica local. El backlog original además preveía una alerta de deriva de datos (data drift) si la precisión caía por debajo de 80% en 3 sesiones consecutivas (`GET /monitoring/quality`) y una validación de campo con al menos 3 operarios reales, ≥2 lotes cada uno, encuesta SUS ≥70 y acta firmada por la gerencia de la cooperativa. Ninguno de los dos existe: no hay ningún endpoint ni lógica de monitoreo de calidad en `src/` (verificado por búsqueda en el código), y no hay evidencia de sesiones de validación con operarios de Line Coffee Marañón.
- **Causa raíz:** el desarrollo del Sprint 4 se concentró en cerrar el pipeline técnico (cámara, tiles, servo, IDs globales — INC-53 a INC-58) y en estabilizar la capa backend (INC-59 a INC-61); el mecanismo de monitoreo de calidad y la validación de campo quedaron fuera de alcance por tiempo.
- **Solución:** pendiente. Es el tramo final del cronograma (semana 8, cierre y entrega) sin cubrir.
- **Gravedad:** Media (no bloquea el flujo técnico, pero impide detectar degradación del modelo en producción y deja sin evidencia formal la aceptación del sistema por parte de la cooperativa). **Estado:** Abierta.
- **Evidencia:** `docs/documentacion/Product_Backlog_Sprints.md` (PBI-21 "Validación en campo: ≥3 operarios... SUS ≥70. Acta firmada"; PBI-22 "Monitoreo: alerta si precisión < 80% en 3 sesiones consecutivas... GET /monitoring/quality"); búsqueda en `src/` sin resultados de un endpoint o módulo de monitoreo de calidad.

### INC-65 · Brecha de dominio entre el dataset (celular) y la cámara de producción (ELP)
- **Área:** Detección / ML / Dataset (CRISP-ML(Q) Fases 2, 4 y 6).
- **Qué se detectó:** en pruebas en vivo, de forma intermitente, el modelo marca como `defecto` granos verdes sanos (~40 % en las pruebas).
- **Causa raíz:** (1) las ~3 600 imágenes de entrenamiento se tomaron con un celular Samsung S25 FE, cuyo procesamiento de imagen (HDR, saturación, color propio) difiere del de la ELP AR0234, que entrega el cuadro casi crudo (*cross-sensor domain shift*); (2) la augmentation de Roboflow variaba brillo y exposición pero no tono ni saturación; (3) las fotos de entrenamiento tienen un grano por imagen con fondo limpio, mientras que en producción cada recorte trae varios granos, a veces en contacto, sobre la faja; (4) en menor medida, el tamaño del dataset (~1 800 imágenes por clase). El balance de blancos automático de la cámara agravaba el problema al variar el color cuadro a cuadro.
- **Solución:** por bloques. Aplicado: `CAM_WB_TEMP` (balance de blancos manual, 2026-09-16), resolución de clase por confianza acumulada con `MARGEN_DEFECTO = 1.3` y dibujo por clase del track (93cd39a), que reducen el síntoma. Pendiente: fine-tuning v7 desde los pesos v6 con 300-500 fotos de la ELP y augmentation HSV (`hsv_h=0.02`, `hsv_s=0.7`, `hsv_v=0.4`); el notebook está preparado. Procedimiento en `docs/guia/03-reentrenamiento-camara-elp.md`. Se descartó sumar el dataset público USK-Coffee como fuente de defectos (su clase "defect" sigue la norma indonesia SNI 01-2907-2008, no SCA).
- **Gravedad:** Alta (un grano sano desviado reduce el peso bueno y por tanto el pago al caficultor). **Estado:** Abierta.
- **Evidencia:** commit `93cd39a` (2026-09-22; `CAM_WB_TEMP`, `MARGEN_DEFECTO`, notebook `src/ml/models/yolov26n_2cls_new/entrenamiento_yolo26n_v7_finetune.ipynb`); `docs/guia/02-modulo-ml.md` sección 8.

### INC-66 · `torch` y `onnxruntime` en build solo-CPU: la inferencia saturaba el procesador
- **Área:** Infraestructura / Detección / ML.
- **Qué se detectó:** durante la clasificación los 24 núcleos lógicos de la laptop quedaban al ~96 % de uso, mientras la GPU RTX 5070 Ti permanecía sin carga.
- **Causa raíz:** estaban instalados `torch==2.12.0+cpu` y `onnxruntime` (que no incluye CUDA ni DirectML), así que el device caía a `cpu` en silencio. ONNX Runtime, PyTorch y OpenCV usan por defecto todos los núcleos, y la inferencia por recortes multiplicaba la carga. Además `camara_service` codificaba a JPEG cada cuadro a 90 fps aunque nadie lo consumía.
- **Solución:** reinstalación de `torch==2.12.0+cu130` / `torchvision==0.27.0+cu130` (instrucciones en `requirements.txt`); en GPU se carga `best.pt` con PyTorch nativo y FP16 condicional por compute capability, en CPU se mantiene `best.onnx`; los 9 recortes se infieren en un solo lote; tope de hilos de CPU (`ML_MAX_THREADS_CPU`); techo de detección (`ML_DETECTOR_FPS`) y gate de movimiento; un único JPEG por cuadro anotado y reducido. Aviso en consola si PyTorch no detecta CUDA.
- **Gravedad:** Alta. **Estado:** Resuelta (CPU del sistema ~96 % → ~25 %, medido con cuadros sintéticos; pendiente medir con faja en marcha y en la GTX 1050 Mobile).
- **Evidencia:** commit `93cd39a` (2026-09-22); `requirements.txt`; `src/ml/tracker.py`; `src/services/tracker_service.py`; `src/services/camara_service.py`.

### INC-67 · Parpadeo desconocido ↔ verde ↔ defecto en objetos ajenos al modelo
- **Área:** Detección / ML.
- **Qué se detectó:** al probar con un objeto que no es un grano, su caja alternaba entre "objeto desconocido", verde y defecto sin que nada cambiara en la escena.
- **Causa raíz:** el criterio "nunca superó `UMBRAL_CONF_CONOCIDO`" se evaluaba sobre `conteo_ids_confianza[track_id]`, un `deque(maxlen=30)`: una sola detección ruidosa de confianza alta hacía que el track dejara de ser desconocido mientras estaba en la ventana, y volvía a serlo cuando salía.
- **Solución:** `_conf_max_historico` guarda el máximo de confianza de toda la vida del track, independiente de la ventana, y se limpia en los mismos puntos que el historial. Límite que persiste: si un objeto ajeno supera 0.35 en un cuadro, queda clasificado de forma estable en una clase conocida (inherente a un umbral de confianza; la alternativa es entrenar una clase explícita de materia extraña).
- **Gravedad:** Media. **Estado:** Resuelta.
- **Evidencia:** commit `93cd39a` (2026-09-22); `src/ml/tracker.py` (`_resolver_clase_display`).

### INC-68 · Peso bruto menor o igual a la tara: peso neto ≤ 0 y pago negativo
- **Área:** Integración / Reglas de negocio.
- **Qué se detectó:** la evaluación EVA0000002 se completó con peso neto negativo y el pago se calculó negativo.
- **Causa raíz:** el registro validaba el máximo del peso bruto (`num_sacos × 70 kg`) pero no que superara la tara (`num_sacos × 0.25 kg`), que `EvaluacionService` resta al completar.
- **Solución:** `RegistrarEvaluacionRequest.validar_pesos` rechaza un peso bruto menor o igual a `round(num_sacos × 0.25)` (el mismo cálculo que el servicio), con validación equivalente en `registro.js`. Un primer intento que agregaba además un mínimo de 10 kg por saco se revirtió por no haber sido solicitado: los umbrales de negocio se consultan antes de implementarse.
- **Gravedad:** Alta (afecta el pago). **Estado:** Resuelta.
- **Evidencia:** commit `4f38d55` (2026-09-30); `src/schemas/evaluacion.py`; `src/static/js/registro.js`.

---

## 7. Incidencias abiertas y en curso (consolidado)

| ID | Área | Incidencia | Acción pendiente |
|---|---|---|---|
| INC-11 | Seguridad | Credenciales de BD en el código | Mover a `.env` / gestor de secretos antes de desplegar. |
| INC-17 | Detección / ML | Equivalencias SCA sin validar | Sesión de validación con calidad de Line Coffee Marañón. |
| INC-18 | Detección / ML | Modelo fino de 17 clases | La cascada se retiró del código (787a7ac). Reconsiderar la clasificación por tipo de defecto solo después de cerrar INC-65. |
| INC-39 | Infraestructura | Pesos fuera de Git | Automatizar la descarga en el instalador. |
| INC-40 | Arduino | Reset por DTR | El re-handshake no cubre el estado del servo; revisar con autorización sobre archivos restringidos. |
| INC-54 | Detección / ML | Granos que se tocan sin caja | Implementar recorte de ROI de la faja antes de la inferencia; validar con captura real de `/monitoreo`. |
| INC-55 | Detección / ML | Servo por detecciones débiles | Verificar en prueba real (con `ML_DEBUG_SERVO=true`) que la compuerta de evidencia no pierde defectos legítimos. |
| INC-56 | Cámara | Foco/zoom manual | Bloquear anillos, anotar geometría de trabajo, seguir checklist de calibración. |
| INC-57 | Cámara | Motion blur | Instalar iluminación difusa potente y fijar exposición manual. |
| INC-62 | Detección / ML | Calidad de dataset y experimentos sin trazar | Medir un IRA real o documentar por qué no aplica (anotador único); registrar splits/hashes si el dataset se reentrena. |
| INC-63 | Detección / ML | Fase 4 (evaluación formal) sin ejecutar | Calcular precision/recall/F1/mAP por clase y matriz de confusión sobre el test set antes de ampliar el despliegue. |
| INC-64 | Detección / ML / Integración | Monitoreo de calidad y validación en campo sin implementar | Definir el mecanismo mínimo de alerta por degradación y programar la sesión de validación con operarios de la cooperativa. |
| INC-65 | Detección / ML / Dataset | Brecha de dominio celular vs ELP | Capturar y etiquetar fotos con la ELP, ejecutar el fine-tuning v7 y comparar v6 vs v7 (`docs/guia/03-reentrenamiento-camara-elp.md`). |
| — | Detección / ML | Verificación en hardware | Confirmar que los IDs globales no retroceden tras pausas; medir FPS y CPU/GPU con la faja en marcha; en la GTX 1050 Mobile instalar torch con CUDA, confirmar FP32 y probar la grilla 2×2; calibrar `ML_GATE_UMBRAL` y `UMBRAL_CONF_CONOCIDO`. |

---

## 8. Lecciones aprendidas

1. **El esquema de base de datos y los schemas Pydantic deben revisarse campo por campo juntos.** Varias incidencias (INC-03, INC-22, INC-23, INC-48) nacieron de una divergencia entre `script.sql` y el código.
2. **La cámara es el eslabón que condiciona todo el pipeline de visión.** El límite de USB 2.0, el formato MJPEG, el reescalado a 640 y el lente manual determinan qué puede y qué no puede detectar el modelo (INC-08, INC-10, INC-38, INC-53, INC-56, INC-57). Bajar la resolución de captura no mejora el detalle que ve YOLO.
3. **En separación física, el tiempo importa tanto como la clase.** La cadena de tiempos del servo (INC-45 a INC-47) exigió medir desde el timestamp de captura del frame, no desde después de la inferencia, porque el mismo código corre en GPU y en CPU.
4. **Umbrales de confianza bajos + filtros posteriores (ByteTrack, votación por mayoría, compuerta de evidencia) dan mejor recall que un umbral alto.** En control de calidad se prefiere el falso positivo (INC-14, INC-54, INC-55).
5. **El hardware de bajo costo impone su realidad.** Los clones de Arduino con resonador cerámico forzaron el pesaje manual (INC-44); el lente varifocal barato obliga a un protocolo de bloqueo y calibración (INC-56).
6. **PowerShell en Windows introduce trampas propias** (BOM UTF-8, codificaciones): preferir herramientas que escriban UTF-8 sin BOM (INC-21, INC-25).
7. **La documentación se desactualiza rápido.** Nombre de la BD, versión de PostgreSQL, baudrate y la necesidad de descargar los pesos del modelo estuvieron mal documentados hasta el Sprint 4 (INC-52).
8. **El código muerto se acumula por capas.** Scaffolding de CRUD que la UI nunca usó, endpoints reemplazados sin borrar y utilidades sin cablear se arrastraron hasta que una auditoría cruzada de endpoints contra consumidores los sacó (INC-50, INC-59). Conviene revisar "¿esto lo llama alguien?" al cerrar cada funcionalidad, no solo al final.
9. **Un catálogo central de mensajes no siempre ayuda (INC-60).** Un módulo `utilities/mensajes.py` con constantes y helpers solo paga si los textos se repiten de verdad; si cada mensaje aparece una sola vez, agrega indirección (leer la ruta + saltar al catálogo + reconstruir la plantilla) sin quitar duplicación. Lo que sí escala es el handler que normaliza el formato de salida (`RequestValidationError` → `detail` string) y un único extractor en el frontend; el texto se queda como literal donde se lanza.
10. **Los criterios de calidad y gobierno de ML definidos en la planificación no sobreviven automáticamente a un cronograma ajustado con un solo desarrollador.** IRA con experto, control de fuga de datos por hash, seguimiento de experimentos con MLflow, la Fase 4 formal (matriz de confusión, pruebas de robustez) y el monitoreo de deriva en producción quedaron todos planificados en el backlog inicial pero sin ejecutar (INC-62, INC-63, INC-64): sin un responsable dedicado a QA, estas actividades se posponen frente a las que bloquean la demo funcional. Quedan como deuda de aseguramiento de calidad a saldar antes de un despliegue real con la cooperativa.
11. **Verificar el entorno antes de optimizar el código (INC-66).** Un uso de CPU al 96 % parecía un problema de programación y era un paquete instalado en su variante sin CUDA. `torch.__version__` y `torch.cuda.is_available()` son la primera comprobación en cualquier equipo nuevo.
12. **Entrenar con la cámara con la que se va a operar (INC-65).** Un dataset tomado con otro sensor y otra composición (un grano, fondo limpio) produce un modelo que funciona en validación y falla en producción. Unos cientos de imágenes del dominio real valen más que miles de un dominio distinto.

---

## 9. Referencias

- `docs/CRONOGRAMA.xlsx` — Sprints 1-4 y mapeo con las 6 fases CRISP-ML(Q).
- `docs/registro-avances.md` — bitácora de avances por fecha.
- `docs/guia/` — estado actual del sistema, módulo ML (incluye la arquitectura de hilos), pendientes e historial.
- `docs/documentacion/avance-tecnico-completo-2026.md`, `arquitectura-sistema-clasificacion.md`, `Product_Backlog_Sprints.md` y `PreInforme_Tesis_2026-I.md` se citan como evidencia pero ya no están en el repositorio (se eliminaron por redundantes u obsoletos; su contenido vigente pasó a `docs/guia/`). Se recuperan del historial: `git show 4f38d55:docs/documentacion/<archivo>` (los dos últimos: `git show 93cd39a^:docs/documentacion/<archivo>`).
- `docs/hardware-camara.md` — ficha técnica de la cámara ELP AR0234 y checklist de calibración.
- `docs/defectos_sca_tabla_referencia.md` — tabla de equivalencias SCA (pendiente de validación oficial).
- `docs/DOCUMENTACION_SISTEMA.md` — documentación general basada en el estado real del código.
- `CLAUDE.md` — reglas de arquitectura y estado del módulo ML.
- Historial de Git (`git log`) — evidencia de fechas y commits citados en cada ficha.

---

*Documento elaborado el 2026-09-01 de forma retrospectiva a partir del historial de Git, la documentación en `docs/` y la memoria técnica del proyecto. Actualizar a medida que se cierren las incidencias en curso o surjan nuevas.*
