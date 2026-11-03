# Guion del video de sustentación — CoffeeRen

**Objetivo:** recorrido único del sistema (software + hardware) que evidencia los 20 criterios
de la rúbrica de evaluación. Duración objetivo: **4:55 / máximo 5:00**.

> Los ítems que dependen de documentación (trazabilidad formal, artefactos de proceso) se
> tocan de pasada al cierre y se señalan como tales; no consumen tiempo de demostración.

---

## 1. Evaluación de la idea propuesta

**Veredicto: la idea es válida y se adopta casi completa.** Cubre por sí sola alrededor de
17 de los 20 criterios. Se reordena para que fluya en 5 minutos y se le añaden cuatro
elementos que faltaban, más dos ajustes de precisión.

### Lo que se conserva de tu idea (tal cual)

| Tu planteamiento | Criterio(s) que evidencia |
|---|---|
| Ingreso por ruta sin sesión → siempre redirige al login | 12 |
| URL inexistente → plantilla de error 404 | 8 |
| Credenciales inválidas → mensaje; válidas → entra | 5, 8 |
| Según el tipo de usuario se muestran unas u otras opciones | 12 |
| Intento de entrar a lo no permitido → no carga | 14 |
| Cambio de datos de perfil visible al instante y persistido en BD (no solo local) | 9 |
| La sesión tiene una duración determinada | 12 |
| Campos validados en el registro de muestra antes de pasar a monitoreo | 5, 8 |
| Clasificación automática según la confianza del modelo | 18, 19 |
| Tamaño específico de caja para los granos | 19 |
| Track ID para el seguimiento | 18 |
| Finalizar e ingresar datos para generar el reporte | 2, 3 |
| El reporte se guarda y se puede buscar después; no se puede editar | 9 |
| Auditoría (administrador): cambios de datos y eventos durante la clasificación | 8, 9, 20 |

### Lo que se añade (faltaba para llegar a los 20)

1. **Mostrar los valores del reporte y contrastarlos con lo esperado** — número de defectos,
   grado SCA, factor de rendimiento y pago. Criterio 3 pide "resultado obtenido vs. esperado".
2. **Señalar el indicador de FPS y la fluidez simultánea** de video y conteo. Criterios 10 y 11
   (desempeño y ejecución continua sin bloqueos).
3. **Ejecutar de verdad una operación no permitida y mostrar la respuesta 403** del sistema.
   Tu idea dice "no se le carga"; el criterio 14 pide ver la respuesta explícita.
4. **Cierre de 10 segundos con el repositorio, la estructura de 4 capas y `docs/arquitectura.md`.**
   Criterios 15 y 16 (evidencia de desarrollo). Documental: se enseña, no se demuestra.

### Ajustes de precisión

- **"Según el tipo de usuario se muestran los campos"** → en concreto es el **menú de
  navegación**: las opciones *Valor de café* y *Cooperativa* solo aparecen para Gerente
  (`tipo_personal_id = 2`) y Administrador (`tipo_personal_id = 3`); el Evaluador (`= 1`) no las ve.
- **"La sesión tiene una duración determinada"** → es el **token JWT con expiración** (campo
  `exp`, 7 días). No es demostrable en vivo; se menciona y, si se quiere prueba, se muestra el
  token decodificado. Al expirar, `verificar_token` devuelve `None` y toda ruta redirige al login.

---

## 2. Requisitos previos (antes de grabar)

- [ ] PostgreSQL en ejecución, base `tesis_prj` cargada con `src/database/script.sql`.
- [ ] Pesos del modelo en `src/ml/models/yolov26n_2cls/` (`best.onnx`).
- [ ] Cámara ELP conectada y Arduino conectado (faja + sensor de tapa + servo).
- [ ] **Precios de café del día ya registrados** (`/valor-cafe`) — sin ellos, el registro de
      muestra se bloquea a propósito.
- [ ] Dos cuentas listas: una **Evaluador** y una **Administrador** (o Gerente).
- [ ] Un caficultor ya registrado para consultarlo por documento (ej. un DNI de prueba).
- [ ] Un puñado de granos preparados, con al menos uno claramente defectuoso.
- [ ] Ventana de `psql` o pgAdmin abierta en la tabla `PERSONA` para la escena de perfil.
- [ ] Servidor: `uvicorn src.main:app` — la cámara se pre-conecta en el arranque.
- [ ] Navegador en pantalla completa, en `http://localhost:8000`.

---

## 3. Guion por escenas

Locución = lo que se dice. Acción = lo que se hace en pantalla.

### Escena 1 — Apertura (0:00 – 0:20)

| | |
|---|---|
| **Locución** | "Buenas tardes. Presento CoffeeRen, un sistema de clasificación automática de granos de café verde por visión artificial. Combina un backend web, un módulo de visión con YOLO y hardware: cámara, faja transportadora y un servo separador." |
| **Acción** | Servidor arrancando en la terminal. Plano corto del hardware (faja + cámara + Arduino). Navegador en `http://localhost:8000`. |
| **Rutas** | `uvicorn src.main:app` · `http://localhost:8000` |
| **Criterios** | 1 (parcial), 18 |

### Escena 2 — Control de acceso (0:20 – 0:55)

| | |
|---|---|
| **Locución** | "Sin sesión no se entra. Si pido una ruta interna, el sistema me devuelve siempre al login. Si escribo una dirección que no existe, muestra una página de error 404. Con credenciales incorrectas, avisa; con las correctas, entra." |
| **Acción** | 1. En la barra de direcciones: `localhost:8000/inicio` → redirige a `/auth/login`.<br>2. `localhost:8000/ruta-que-no-existe` → plantilla `404.html`.<br>3. Login con usuario real y clave incorrecta → *"Credenciales incorrectas, intenta nuevamente."*<br>4. Login como **Evaluador** con credenciales válidas → entra a `/inicio`. |
| **Rutas** | `/inicio` · `/auth/login` (GET y POST) · cualquier ruta inválida → `404.html` |
| **Se ingresa** | usuario + clave (una vez mal, una vez bien) |
| **Criterios** | 5, 8, 12 |

### Escena 3 — Rol y operación no autorizada (0:55 – 1:20)

| | |
|---|---|
| **Locución** | "Este usuario es Evaluador. Su menú no incluye *Valor de café* ni *Cooperativa*: esas secciones son solo para Gerente y Administrador. Y si fuerzo una operación reservada, el sistema responde con un 403 y no entrega los datos." |
| **Acción** | 1. Señalar el menú superior: sin *Valor de café*.<br>2. En la barra de direcciones: `localhost:8000/auditoria` → respuesta JSON `{"detail":"No tienes permisos para acceder a esta sección"}` (HTTP 403).<br>3. Cerrar sesión (`/auth/logout`). |
| **Rutas** | menú en `templates/main.html` (`{% if user.tipo_personal_id in [2,3] %}`) · `GET /auditoria` → 403 · `/auth/logout` |
| **Criterios** | 12, 14 |

### Escena 4 — Perfil: cambio visible y persistido (1:20 – 1:50)

| | |
|---|---|
| **Locución** | "Ingreso ahora como Administrador. En mi perfil cambio el teléfono; al guardar, la vista se actualiza de inmediato y el dato queda en la base de datos, no solo en pantalla. La sesión, además, usa un token con caducidad." |
| **Acción** | 1. Login como **Administrador**.<br>2. Menú de usuario → *Perfil* (`/perfil`).<br>3. Editar teléfono/correo → *Guardar* → el valor se refleja al instante.<br>4. Cambiar a la ventana de `psql`/pgAdmin: `SELECT nombre, telefono, correo FROM persona WHERE ...` → el nuevo valor está en `PERSONA`.<br>5. Frase al pasar: contraseñas con Argon2, consultas SQL parametrizadas, credenciales fuera del repositorio. |
| **Rutas** | `GET /perfil` · `PATCH /perfil/datos-personales` (reescribe la cookie con token nuevo) · tabla `PERSONA` |
| **Se ingresa** | teléfono o correo nuevo |
| **Criterios** | 9, 12, 13 |

### Escena 5 — Registro de muestra con validación (1:50 – 2:30)

| | |
|---|---|
| **Locución** | "Antes de clasificar, registro la muestra. El documento se valida según su tipo: DNI, ocho dígitos. Consulto el caficultor y sus datos se completan solos. Los pesos tienen reglas: el peso trillado no puede superar al de muestra; si me equivoco, el sistema lo marca y no me deja continuar. Por último, el sensor exige que la tapa esté cerrada." |
| **Acción** | 1. Ir a *Registro de muestra* (`/registro`).<br>2. Tipo de documento **DNI**, escribir 8 dígitos → autoconsulta → nombre y tipo de caficultor se rellenan.<br>3. Escribir un **peso trillado mayor al peso de muestra** → mensaje de error bajo el campo; el botón no avanza.<br>4. Corregir los valores.<br>5. Pulsar *Iniciar clasificación y monitoreo*: si la tapa está abierta, aparece el aviso; cerrarla y continuar. |
| **Rutas** | `GET /registro` · `GET /caficultor/consultar/{num_documento}` · `GET /tipo-documento/listar` · `GET /arduino/estado` (sensor de tapa) · `POST /evaluacion/registrar` |
| **Se ingresa** | tipo de documento, número de documento, N.º sacos, peso bruto, humedad, peso de muestra, peso trillado, N.º tamiz, peso tamizado, tipo de grano |
| **Criterios** | 4, 5, 8 |

### Escena 6 — Monitoreo en tiempo real (2:30 – 3:50)

| | |
|---|---|
| **Locución** | "Arranca la faja y el video en vivo. Cada grano detectado lleva su caja con la clase, el porcentaje de confianza, su tamaño en píxeles y un identificador de seguimiento único, para no contarlo dos veces. Solo se consideran cajas dentro del rango de tamaño de un grano; las detecciones débiles se descartan. El conteo de defectos y sanos sube en tiempo real y el video se mantiene fluido: arriba se ve la tasa de cuadros por segundo. Cuando pasa un grano defectuoso, el servo lo desvía al canal de descarte." |
| **Acción** | 1. La página `/monitoreo/{id}` ya arrancó sola: video anotado + faja en marcha.<br>2. Pasar granos por la faja. Señalar en una caja: `#id`, clase, `%`, `NxN px`.<br>3. Señalar el indicador de **FPS** y los contadores *Defectos / Sanos* subiendo.<br>4. Mostrar el **servo separando** un grano defectuoso.<br>5. *(Opcional, si sobra tiempo)* desconectar la cámara un instante → aparece *"Desconexión con cámara. La clasificación se ha detenido."* y el servo queda fijo en descarte; reconectar. |
| **Rutas** | `GET /monitoreo/{evaluacion_id}` · `GET /video/frame` (stream) · `GET /video/lote/conteo` · `GET /video/status` · `POST /arduino/motor/iniciar` · lógica en `src/ml/tracker.py` y `src/utilities/servo_controller.py` |
| **Criterios** | 7, 10, 11, 18, 19, 20 |

### Escena 7 — Finalizar y generar el reporte (3:50 – 4:20)

| | |
|---|---|
| **Locución** | "Al finalizar, el sistema detiene la faja, cierra el conteo y me pide el peso del grano bueno separado. Con ese dato calcula el factor de rendimiento, la categoría, el grado SCA y el pago al caficultor. Todo queda guardado con un código de evaluación." |
| **Acción** | 1. Botón *Finalizar monitoreo* → confirmar.<br>2. El overlay muestra los pasos (detener, calcular, guardar).<br>3. Ingresar el **peso bueno** en gramos → *Calcular rendimiento*.<br>4. Leer en voz alta: total de defectos, grado, factor de rendimiento, categoría y pago. Comentar que coinciden con lo esperado para la muestra.<br>5. Aparece el **código `EVAxxxxxxx`**. |
| **Rutas** | `PATCH /evaluacion/{id}/finalizar` · `PATCH /evaluacion/{id}/completar` · `POST /video/lote/generar-reporte` · `GET /evaluacion/{id}/resumen` · cálculo en `src/services/evaluacion_service.py`, grado en `src/ml/classifier.py` |
| **Se ingresa** | peso del grano bueno (gramos) |
| **Criterios** | 2, 3, 5, 9, 19 |

### Escena 8 — Búsqueda del reporte y auditoría (4:20 – 4:45)

| | |
|---|---|
| **Locución** | "El reporte se puede recuperar después por su código. Se abre en solo lectura: se puede exportar a Excel, pero no editar. Y en el panel de administración, la auditoría registra quién hizo cada cambio, con su IP, además de los eventos ocurridos durante la clasificación, como las aperturas de tapa." |
| **Acción** | 1. Ir a *Buscar reportes* (`/reporte`), escribir el código `EVAxxxxxxx` → aparece el resumen completo. Señalar: no hay botón de edición, solo *Exportar a Excel*.<br>2. Menú de usuario → *Cooperativa* (`/configuracion-cooperativa`) → pestaña **Auditoría**.<br>3. Mostrar los registros recientes: `LOGIN`, `LOGIN_FALLIDO`, `ACTUALIZAR_PERFIL`, `CREAR_EVALUACION`, `FINALIZAR_EVALUACION`, con usuario, fecha e IP.<br>4. En el reporte, señalar la tabla de **incidencias de tapa** capturadas durante el monitoreo. |
| **Rutas** | `GET /reporte` · `GET /evaluacion/buscar?codigo=EVAxxxxxxx` · `GET /configuracion-cooperativa` · `GET /auditoria` (como Administrador) |
| **Se ingresa** | código de evaluación `EVAxxxxxxx` |
| **Criterios** | 3, 4, 9, 20 |

### Escena 9 — Cierre: evidencia de desarrollo (4:45 – 4:55)

| | |
|---|---|
| **Locución** | "El sistema es reproducible desde el repositorio, con una arquitectura en cuatro capas y su documentación de proceso por sprints. Gracias." |
| **Acción** | Plano rápido de: repositorio Git, árbol de carpetas `src/routes · services · models · schemas`, y `docs/arquitectura.md`. |
| **Rutas** | repositorio · `docs/arquitectura.md` · `docs/documentacion/Product_Backlog_Sprints.md` · `docs/incidencias/incidencia_proyecto.md` |
| **Criterios** | 15, 16, 17 (documental) · 1 (trazabilidad, documental) |

---

## 4. Mapa de cobertura: criterio → escena

| # | Dimensión / criterio | Escena(s) | Cómo se evidencia |
|---|---|---|---|
| 1 | Núcleo corresponde al objetivo | 1, 9 | Enunciado del objetivo + flujo completo + repo. Trazabilidad formal: documental. |
| 2 | Función principal completable de inicio a fin | 5, 6, 7 | Registro → monitoreo → reporte sin funciones ausentes. |
| 3 | Resultados coherentes con lo esperado | 7, 8 | Valores del reporte leídos y contrastados con lo esperado para la muestra. |
| 4 | Interfaz clara para las acciones | 5, 6, 8 | Navegación por pantallas dedicadas y botones de cada paso. |
| 5 | Retroalimentación comprensible | 2, 5, 7 | Mensaje de credenciales, errores inline, overlay de finalización con pasos. |
| 6 | El usuario completa el escenario sin trabas | 5–7 | Recorrido continuo sin bloqueos lógicos. *(Registrar aparte una prueba con un evaluador real.)* |
| 7 | Ejecución estable en la demostración | 6 | Monitoreo corriendo de forma sostenida. Mencionar que se repitió varias veces. |
| 8 | Control de errores previsibles | 2, 5, 6 | 404, credenciales inválidas, pesos inválidos, sensor de tapa, (opcional) desconexión de cámara. |
| 9 | La información se conserva | 4, 7, 8 | Perfil → cambio en `PERSONA`; reporte guardado y recuperado por código. |
| 10 | Tiempo de respuesta aceptable | 6 | Indicador de FPS visible; respuesta inmediata de los formularios. |
| 11 | Responde en ejecución continua sin bloqueos | 6 | Video + conteo simultáneos, fluidos. |
| 12 | Acceso y operaciones controladas | 2, 3, 4 | Redirección sin sesión, menú por rol, token con expiración. |
| 13 | Protección de datos acorde a su naturaleza | 4 | Argon2, SQL parametrizado, secretos fuera del repositorio (narrado + hash en BD). |
| 14 | Evita operaciones no autorizadas | 3 | `GET /auditoria` como Evaluador → 403 con mensaje. |
| 15 | Versión ejecutable / reproducible | 9 | Repositorio + `requirements.txt` + `script.sql`. |
| 16 | Organización técnica coherente | 9 | Estructura de 4 capas + `docs/arquitectura.md`. |
| 17 | Relación con artefactos de proceso | 9 | Backlog, sprints, registro de incidencias. Documental. |
| 18 | Componente de IA integrado y operativo | 1, 6 | Cámara → inferencia YOLO → conteo → grado → servo, en vivo. |
| 19 | Resultado de IA pertinente + controles | 6, 7 | Umbral de confianza, filtro de tamaño de caja, voto por mayoría; resultado validado en el reporte. |
| 20 | Riesgos del componente inteligente gestionados | 5, 6, 8 | Sensor de tapa, servo, (opcional) modo emergencia por cámara; incidencias registradas en auditoría. |

---

## 5. Plan B y recortes

Si el cronómetro aprieta, recortar en este orden:

1. **Quitar** la desconexión de cámara de la escena 6 (es opcional).
2. **Acortar** la escena 4: mostrar solo el cambio en pantalla y decir "y queda en la base de
   datos" sin abrir `psql` (pierde algo de fuerza en el criterio 9, pero la escena 8 lo respalda).
3. **Fundir** las escenas 8 y 9: enseñar auditoría y repositorio en la misma toma final.

Si algo del hardware falla durante la grabación:

- La ruta `/prueba` abre el video con detección en vivo **sin registrar** muestra ni evaluación:
  sirve para evidenciar los criterios 18 y 19 aunque no se pueda cerrar el flujo completo.
- El reporte de una evaluación anterior ya guardada cubre los criterios 3, 9 y 20 desde
  `/reporte` sin depender de la faja.

---

## 6. Notas técnicas honestas (para no exponerse en preguntas)

- **Duración de sesión:** el token dura 7 días; no se "ve" expirar en el video. Si preguntan,
  mostrar el `exp` del token decodificado.
- **Guardas de página vs. de API:** el bloqueo por rol está en los **endpoints de datos**
  (`require_admin_o_gerente` → 403). Algunas *páginas* reservadas (`/valor-cafe`,
  `/configuracion-cooperativa`) cargan el armazón para cualquier usuario autenticado y es la
  llamada de datos la que devuelve 403. Por eso la escena 3 muestra la respuesta 403 directa y
  no "la página en blanco". Conviene endurecer esas rutas de página antes de la sustentación.
- **Tabla de equivalencias SCA (modelo de 2 clases):** aún sin validación oficial de Line
  Coffee Marañón (incidencia abierta). No afirmar en el video que el grado es "oficial";
  decir "según la tabla SCA adaptada".
- **Métricas del modelo activo:** el `yolov26n_2cls` es el que corre; las cifras de mAP de la
  documentación corresponden al modelo de 17 clases. No mezclar ambas al hablar.
