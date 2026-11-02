# Revisión técnica — CoffeeRen

Fecha: 2026-11-02. Rama revisada: `temporal` (commit `1b70280`).
Alcance: lectura estática del código, del firmware, de la configuración y de la documentación.
No se ejecutó la aplicación, ni las pruebas, ni el hardware. Las líneas citadas corresponden a
ese commit.

Severidad:

- **Crítico:** compromete la seguridad, la integridad de los datos de pago o la validez del
  conteo que sustenta la tesis.
- **Medio:** error real o riesgo concreto, con impacto acotado o que depende de condiciones de
  operación.
- **Menor:** deuda técnica, incoherencia o mejora de mantenibilidad.

## Estado al 2026-11-02 (después de las correcciones)

Corregido en el código:

| Hallazgo | Qué se hizo |
|---|---|
| 1.1 Gate de movimiento | La referencia solo se actualiza cuando el frame pasa a inferencia. Falta validarlo en banco (pendiente A en `docs/guia/04-pendientes.md`). |
| 1.5 Reinicio de lote | Época de lote: un frame que empezó antes del reinicio no escribe en el lote nuevo; ByteTrack se reinicia solo desde su hilo. |
| 1.7 Log por frame | Resumen cada 2 s. |
| 1.9 Reproceso de frame | Se respeta el retorno de `esperar_frame()`. |
| 1.10 Comentarios | Corregidos el de `CONF_THRESHOLD` y los docstrings de resolución. El comentario de `EQUIVALENCIAS_DEFECTO` (0,83 frente a 1) sigue a la espera de la cooperativa. |
| 1.11 Constantes | Las constantes del modelo son obligatorias; si falta una, el arranque falla con su nombre. |
| 2.1 Credenciales | `src/config.py` fuera del índice; `SECRET_KEY` obligatoria (≥ 32 caracteres, no de ejemplo); contraseña retirada de `reset_db.ps1` y de `docs/registro-avances.md`. **Falta cambiar la contraseña**: sigue en el historial. |
| 2.2 Conteo desde el navegador | Al finalizar, el servidor toma el conteo de `tracker_service.conteo_de_evaluacion()`; si el lote no es el de la evaluación, responde 409. `/completar` ya no recibe `total_defectos`. |
| 2.3 Video sin sesión | `/video/stream`, `/frame` y `/status` exigen sesión. `/resources` sigue público (ver pendientes). |
| 2.4 Código EVA | `UNIQUE`, secuencia `evaluacion_codigo_seq`, `FOR UPDATE` y reintento sin reescribir la fila ni duplicar eventos. Estructura consolidada en el SQL único `src/database/script.sql`. |
| 2.5 Event loop | 59 rutas sin `await` pasaron a `def`. |
| 2.7 Cookie y login | `samesite="lax"`, `max_age` de 7 días, `datetime.now(timezone.utc)`, `cuenta_habilitada` falla cerrada. |
| 2.9 Humedad | Sin cambio de código: el responsable confirmó que se divide entre `100 − H` a propósito. Queda escrito en `AGENTS.md` sección 7. |
| 2.10 Precio en `float4` | Columna a `numeric(7, 2)` en `src/database/script.sql`; el schema limita el precio a 99 999,99. |
| 2.11 Códigos HTTP | En evaluación: 404 solo si no existe (`NoEncontradoError`), 400 reglas de negocio, 409 al finalizar sin conteo. |
| 2.12 Subida de imágenes | Lógica en `cooperativa_service`; formato verificado con Pillow; se lee como máximo 5 MB + 1 byte; se borra el logo reemplazado. |
| 3.8 Buffer serie | Tope de 32 caracteres con memoria reservada. |
| 2.9 Redondeo de la tara | El responsable confirmó que la tara no se redondea: `num_sacos × 0.25` kg tal cual (2 sacos = 0.50 kg). El SQL único `src/database/script.sql` define `tara_total` como `numeric(7, 2)`; schema, service y `registro.js` usan el mismo cálculo. La base de desarrollo existente conserva la columna entera hasta que el responsable la reconstruya. |
| 1.2 Cola del servo | Heap ordenado por instante de ejecución (permiso del responsable, 2026-11-02). |
| 2.8 Topes de lote | Máximo 30 sacos por lote (regla del responsable): schema (`MAX_SACOS_POR_LOTE`), formulario y `max` del input. Con 30 sacos el peso bruto y el pago caben en `numeric(7, 2)`. |
| 3.1 Watchdog de la faja | El backend escribe una línea vacía cada 1 s con la faja encendida; el firmware la apaga tras 3 s sin recibir nada. No es un comando nuevo: la línea vacía ya era el keep-alive. |
| 3.4 DTR | Al abrir el puerto se espera la primera línea del firmware (hasta 3 s) antes de enviar comandos. |
| 3.5 Estado sin hora | Cada lectura guarda su instante; un `LISTO` de más de 1 s ya no da la tapa por cerrada. |
| 3.6 Hilos de keep-alive | Un único hilo para todo el proceso y reconexión con lock. |
| 3.2 `pulseIn` | Timeout de 5000 µs (antes 30 000): el umbral de la tapa es 5.30 cm y el loop queda bloqueado como máximo 5 ms. Falta comprobar en el prototipo que siga apareciendo `LISTO:` con la tapa cerrada. |
| 4.3 / 4.4 Notebook y rutas | `deterministic=True`, `results.save_dir`, versiones impresas y `metadata.json` con SHA-256 de `best.pt`; rutas de `main.py` y de evidencias ancladas al proyecto. |

Pendiente, con el motivo:

| Hallazgo | Motivo |
|---|---|
| 1.3 Grano sano durante el hold | Queda como limitación física conocida (un solo servo); falta decidir si se registra como evento. |
| 1.4 Clase del servo frente a la del conteo | Cambia cómo se cuenta: decisión del responsable. |
| 1.6 Geometría de tiles | Hay que medir recall y latencia con la cámara real antes de cambiarla. |
| 1.8 Anotación a resolución completa | Mejora menor de rendimiento; se deja para después de medir. |
| 2.3 `/resources` público | Las evidencias necesitan una ruta autenticada propia; el logo de la cooperativa se usa también fuera de sesión. |
| 2.6 Pool de conexiones | Necesita prueba de carga para fijar el tamaño del pool sin agotar conexiones. |
| 2.7 Rol leído del JWT y límite de intentos | El rol desde la BD cambia la prueba PCB-02; el límite de intentos necesita un número que debe fijar el responsable. |
| 3.3 Velocidad de la faja | Ya registrado como pendiente A (recalibrar `SERVO_DELAY_S` a PWM 90). |
| 4.1 Versiones fijadas | Hay que hacer `pip freeze` en la laptop de producción con el `torch+cu130` real. |
| 4.2, 4.5 Notebook v6 y métricas sobre fotos ELP | Requieren archivos y etiquetas que están en Google Drive. |
| 5.1 Pruebas nuevas | Solo se ajustaron PCB-09 y la precondición de caja negra; las pruebas nuevas quedan para después. |

---

Varios hallazgos tocan elementos que `AGENTS.md` (sección 6) declara intocables sin permiso
(`servo_controller.py`, `arduino_serial.py`, protocolo serie, umbrales). Se marcan con
**[requiere permiso]**: la sugerencia queda para que el autor decida, no para aplicarla
directamente.

---

## 0. Aclaración sobre el alcance pedido

La solicitud menciona `inference.py`, un modelo de 14 clases y la lectura del HX711. En el
código actual:

- `inference.py` no existe (eliminado en `dcf68a8`).
- El modelo cascada de 14 clases y `USE_MODELO_DEFECTOS` no existen (eliminados en `787a7ac`).
  El único modelo es `yolov26n_2cls` (`defecto`, `verde`) más la clase sintética `desconocido`.
- El firmware no lee ningún HX711: la báscula está retirada
  (`arduino/logica_hardware/logica_hardware.ino:90`).

Por eso la sección 1 revisa `tracker.py`, `classifier.py`, `constants.py` y los services de
visión, y en lugar de "coherencia binario vs. 14 clases" revisa los restos del diseño multiclase
que quedan en el código. La sección 3 revisa el firmware vigente y señala lo que queda del
protocolo de la báscula.

---

## 1. Módulo de visión

### 1.1 El gate de movimiento compara contra el frame anterior, no contra el último inferido — Crítico (verificar en banco)

- **Dónde:** `src/ml/tracker.py:346-355`.
- **Problema:** `hay_movimiento()` reemplaza `self._gris_movimiento` en **cada** llamada,
  también cuando decide saltarse la inferencia. Así se compara siempre el frame actual contra
  el inmediatamente anterior. Con la faja JGY370 a 10 RPM, el grano se desplaza muy poco entre
  dos frames consecutivos (a 30 fps y en una miniatura de 160x90, menos de un píxel), y la
  diferencia media de todo el cuadro puede quedar por debajo de `ML_GATE_UMBRAL = 1.0` aunque
  la faja esté en marcha. El movimiento lento nunca se acumula y la inferencia se omite de forma
  sistemática: los granos pasan sin contarse y sin accionar el servo.
- **Sugerencia:** actualizar la referencia solo cuando el gate deja pasar el frame (comparar
  contra el último frame **inferido**), o forzar una inferencia cada N ms aunque no haya cambio.
  Verificar en banco con la faja en marcha y `ML_GATE_MOVIMIENTO=false` frente a `true`, y
  comparar el conteo con un lote de cantidad conocida.

### 1.2 Cola del servo ordenada por inserción, no por instante de ejecución — Medio [requiere permiso]

- **Dónde:** `src/utilities/servo_controller.py:73-80` (`append`) y `:96`
  (`self._cola[0].ejecutar_en <= time.monotonic()`); el origen está en
  `src/ml/tracker.py:442-448`.
- **Problema:** `ejecutar_en` se calcula desde el **primer avistamiento** del track, pero la
  solicitud se encola cuando el track junta evidencia suficiente, que puede llegar uno o dos
  frames más tarde según el grano. Si el grano B (visto después) junta evidencia antes que el
  grano A (visto antes), B queda primero en la cola y A, que vence antes, espera a que venza B.
  El servo actúa tarde para A y desvía el grano equivocado.
- **Sugerencia:** usar `heapq` ordenado por `ejecutar_en`, o insertar ordenado (`bisect`). Es un
  cambio de pocas líneas, pero el archivo es intocable sin permiso.

### 1.3 Un grano sano que vence durante el hold se desvía igual a defecto — Menor [requiere permiso]

- **Dónde:** `src/utilities/servo_controller.py:125-133`.
- **Problema:** durante el hold, una solicitud "bueno" se saca de la cola y se descarta: ese
  grano cae al canal de defecto. El comentario lo reconoce. El efecto no se refleja en el
  conteo: el sistema cuenta el grano como sano, pero físicamente lo separó como defecto.
- **Sugerencia:** registrar esos casos como evento de monitoreo (por ejemplo, "grano sano
  desviado por solape") para que la cifra de separación física sea auditable en la evidencia
  de la tesis.

### 1.4 La clase que decide el servo y la clase que se cuenta pueden diferir — Medio

- **Dónde:** `src/ml/tracker.py:676-697` (servo) y `:699-711` (conteo final).
- **Problema:** el servo resuelve la clase `SERVO_DELAY_S` después del primer avistamiento.
  El conteo la vuelve a resolver al final del lote sobre las últimas 30 detecciones
  (`deque(maxlen=30)`, línea 127). Si el track sigue en cuadro después de que actuó el servo,
  su clase puede cambiar: el grano se separó físicamente como sano y se cuenta como defecto, o
  al revés. La precisión de separación y la del conteo dejan de medir lo mismo.
- **Sugerencia:** congelar la clase en el momento en que el servo la consulta (guardar
  `clase_servo[track_id]`) y usar esa misma clase para el conteo, o reportar las dos y su
  discrepancia.

### 1.5 Reinicio del lote con el hilo de inferencia en marcha — Medio

- **Dónde:** `src/ml/tracker.py:377-379` y `:540-557`; lo dispara `POST /video/lote/resetear`
  (`src/routes/video.py:137-150`).
- **Problema:** `resetear_conteo()` vacía `_bytetrack_a_global` desde el hilo HTTP, pero
  ByteTrack solo se reinicia al **siguiente** frame (`_reset_bytetrack`). Si el reinicio cae
  mientras `procesar_frame` está en curso, los tracks del lote anterior que siguen vivos en
  ByteTrack reciben IDs globales nuevos y se cuentan en el lote nuevo. Además
  `_reset_bytetrack` se escribe fuera del lock.
- **Sugerencia:** hacer el reinicio completo (mapeo y ByteTrack) dentro del hilo de
  procesamiento mediante una sola bandera atendida al inicio de `procesar_frame`, o descartar
  el resultado del frame en curso cuando cambió una "época" de lote.

### 1.6 Geometría de tiles con solape excesivo — Medio (rendimiento)

- **Dónde:** `src/ml/models/yolov26n_2cls/constants.py:29-31` y `src/ml/tracker.py:206-220`.
- **Problema:** con 1920x1080, una grilla 3x3 y `TILE_SOLAPE_PX = 320`, el tile central mide
  1280x1000 px y los de borde 960x680. Cada tile cubre entre la mitad y dos tercios del cuadro,
  y un punto central cae en hasta 6 tiles. Se corren 9 inferencias por frame (270 por segundo a
  30 fps) para una ganancia de escala modesta (factor 0,5 a 0,67 frente a 0,33 del cuadro
  completo). El solape también multiplica las cajas duplicadas que luego hay que fusionar con
  `_fusionar_cajas`.
- **Sugerencia:** medir el recall y la latencia con 2x2 y 3x2 con el mismo solape, o reducir el
  solape a lo que exige el grano más grande (~230 px si el lado máximo real es ~455 px). Dejar
  la medición en `docs/evidencias/`.

### 1.7 E/S de consola en cada frame dentro del hilo de inferencia — Medio (rendimiento)

- **Dónde:** `src/ml/tracker.py:480-485` (y `:354`, `src/services/tracker_service.py:209`).
- **Problema:** con detecciones, cada frame recalcula el conteo final de todos los tracks bajo
  el lock (`_calcular_conteo_final`) e imprime una línea; sin detecciones imprime otra. A 30 fps
  son 30 escrituras síncronas por segundo en el hilo que se está cronometrando para el
  indicador de latencia (≤ 200 ms). En la consola de Windows la escritura es lenta y puede
  inflar la medición.
- **Sugerencia:** pasar a `logging` con nivel `DEBUG` y limitar estos mensajes a uno cada N
  segundos, igual que ya se hace con el log del gate.

### 1.8 Copia y anotación a resolución completa antes de reducir — Menor (rendimiento)

- **Dónde:** `src/ml/tracker.py:389` y `:523-529`.
- **Problema:** se copia el cuadro de 1920x1080 y se dibuja sobre él para luego reducirlo a
  1280 px de ancho.
- **Sugerencia:** reducir primero y escalar las coordenadas de las cajas al dibujar.

### 1.9 Se puede reprocesar el mismo frame — Menor

- **Dónde:** `src/services/tracker_service.py:176-179`; `src/services/camara_service.py:259-264`.
- **Problema:** se ignora el valor de retorno de `esperar_frame()`. Si vence el timeout, se
  procesa otra vez el último frame. Con el gate activo se descarta por diferencia nula; con
  `ML_GATE_MOVIMIENTO=false` se infiere dos veces sobre la misma imagen.
- **Sugerencia:** `if not camara_service.esperar_frame(timeout=1.0): continue`.

### 1.10 Umbrales y comentarios incoherentes — Menor

- `src/services/tracker_service.py:19-24`: el comentario dice que el conteo final filtra "por
  voto de mayoría + conf promedio (>= 0.45)". El código no hace eso: resuelve por confianza
  acumulada con `MARGEN_DEFECTO` y marca `desconocido` por `UMBRAL_CONF_CONOCIDO`
  (`tracker.py:631-674`).
- `src/ml/models/yolov26n_2cls/constants.py:66-67`: el comentario calcula un promedio ≈ 0,83
  y el valor es `1`. No se cambia el valor (es una regla de negocio); hay que confirmar con la
  cooperativa cuál rige y alinear el comentario.
- `src/ml/tracker.py:47-48`, `:53-67`: `SERVO_MIN_FRAMES`, `SERVO_CONF_MIN`, `IOU_NMS`,
  `IOS_CONTENIDA`, `NMS_ENTRE_TILES` y `MARGEN_DEFECTO` están fijos en `__init__`, mientras que
  el resto de los parámetros del modelo vive en `constants.py`. Para la trazabilidad de los
  experimentos conviene que todos los parámetros del pipeline estén en un solo lugar y se
  registren junto con cada corrida de medición.
- `src/ml/tracker.py:357-362` y `tracker_service.py:33`: los docstrings dicen 1280x720 a 60 fps;
  la configuración vigente es 1920x1080 a 90 fps.

### 1.11 Restos del diseño multiclase — Menor

- `src/ml/tracker.py:193-195`: los valores por defecto de `getattr` (`GRANO_MAX_PX = 200`,
  `GRANO_MIN_PX = 8`, `TILE_SOLAPE_PX = 96`) no coinciden con los de `constants.py` (640, 50,
  320). Si alguien quita una constante, el sistema arranca en silencio con valores de otra
  configuración de cámara.
- `src/ml/tracker.py:195` y `src/services/tracker_service.py:294-297`: `GRUPOS_DISPLAY` y
  `conteo_agrupado` siempre salen vacíos con el modelo binario.
- `src/ml/classifier.py:31-33`: una clase sin equivalencia se descarta en silencio del total de
  defectos, pero sí entra en `total_granos_analizados` (línea 62).
- **Sugerencia:** exigir las constantes (sin valores por defecto) y lanzar un error claro si
  faltan; eliminar `GRUPOS_DISPLAY`; en `calcular_defectos`, avisar cuando una clase no tenga
  equivalencia.

---

## 2. Backend FastAPI

### 2.1 Credenciales versionadas y clave JWT por defecto — Crítico

- **Dónde:** `src/config.py:25-27`. El archivo está en `.gitignore`, pero **sigue versionado**
  (`git ls-files src/config.py` lo lista; aparece en 8 commits, el último `1b70280`).
- **Problema:** la contraseña real de PostgreSQL está en el historial público del repositorio.
  Además, si falta `.env`, `SECRET_KEY` vale `'your_secret_key_here'` (también en
  `config-example.py`): cualquiera que lea el repositorio puede firmar un JWT con
  `tipo_personal_id = 3` y entrar como Administrador.
- **Sugerencia:**
  1. Cambiar la contraseña del usuario `postgres`.
  2. `git rm --cached src/config.py` y commit (el `.gitignore` ya lo excluye).
  3. Leer `PASSWORD` y `SECRET_KEY` de `.env` y abortar el arranque si `SECRET_KEY` falta o
     coincide con el texto de ejemplo.
  4. Si el repositorio es público, considerar limpiar el historial (`git filter-repo`); como
     mínimo, dar la contraseña filtrada por comprometida.

### 2.2 El conteo de defectos lo envía el navegador — Crítico (integridad de datos)

- **Dónde:** `src/services/evaluacion_service.py:218` y `:264-280`;
  `src/schemas/evaluacion.py:79-81`, `:92`; origen en `src/static/js/monitoreo.js:728-745`
  y `:634`, `src/static/js/analisis.js:64`, `:92`.
- **Problema:** `total_defectos` y `total_buenos` (el resultado de la clasificación, que es la
  variable central de la tesis) llegan en el cuerpo del `PATCH`. El servidor tiene esos datos en
  `tracker_service` y no los usa. Cualquier usuario autenticado puede registrar el número que
  quiera. Además:
  - `/finalizar` y `/completar` escriben `total_defectos` dos veces, con valores que el
    frontend toma de lecturas distintas (`/lote/conteo` y `/lote/generar-reporte` en momentos
    distintos), así que `total_buenos = total_granos - total_defectos` puede salir incoherente
    o negativo si las dos lecturas no coinciden.
  - El campo se guarda como entero, pero `classifier.py` lo define como "defectos
    equivalentes" (decimal). Hoy coinciden porque todas las equivalencias valen 1; si la
    cooperativa fija otra equivalencia, la base guardará el número de granos con el nombre de
    defectos equivalentes.
- **Sugerencia:** en `finalizar_evaluacion`, tomar el conteo de `tracker_service` en el servidor
  (verificando que `tracker_service.evaluacion_id == evaluacion_id`) y guardar granos
  defectuosos y defectos equivalentes en campos separados. `/completar` no debería volver a
  aceptar `total_defectos`.

### 2.3 Endpoints de video sin autenticación — Medio (seguridad)

- **Dónde:** `src/routes/video.py:24` (`/video/stream`), `:157` (`/video/frame`), `:173`
  (`/video/status`).
- **Problema:** incumplen la regla 5.5 de `AGENTS.md`: cualquiera en la red ve la cámara en vivo,
  el conteo y el ID de la evaluación en curso. `/resources` también está montado sin control
  (`src/main.py:82`), así que las fotos de evidencia de cada evaluación son públicas.
- **Sugerencia:** agregar `Depends(obtener_usuario_actual)` a los tres endpoints (la etiqueta
  `<img>` del MJPEG envía la cookie al mismo origen) y servir las evidencias con una ruta
  autenticada.

### 2.4 Código EVA correlativo sin bloqueo ni restricción `UNIQUE` — Medio

- **Dónde:** `src/models/evaluacion.py:9-19` (`MAX(...) + 1`) y `:266-301`;
  `src/database/script.sql:49` (`codigo char(10)` sin `UNIQUE`).
- **Problema:** dos finalizaciones simultáneas leen el mismo máximo y guardan el mismo código. La
  base no lo impide. El `SELECT` previo tampoco bloquea la fila, y volver a llamar a
  `/finalizar` sobre una evaluación ya completada sobrescribe `fecha`, `total_defectos` y
  `total_buenos` de un registro cerrado.
- **Sugerencia:** `ALTER TABLE evaluacion ADD CONSTRAINT uq_evaluacion_codigo UNIQUE (codigo)`;
  generar el número con una `SEQUENCE`; `SELECT ... FOR UPDATE` en `asignar_codigo` y rechazar
  la sobrescritura si `factor_rendimiento IS NOT NULL`.

### 2.5 Rutas `async def` que bloquean el event loop — Medio (rendimiento)

- **Dónde:** todas las rutas de `src/routes/` y `src/main.py:245-297` llaman a services
  síncronos (psycopg2) desde `async def`. El caso más pesado es `src/routes/auth_login.py:22`,
  que corre Argon2 (64 MiB, `time_cost=3`) dentro del loop.
- **Problema:** mientras dura una consulta o un hash, el servidor no atiende otras peticiones, y
  eso incluye el stream MJPEG y el sondeo del conteo durante el monitoreo.
- **Sugerencia:** declarar con `def` las rutas que no hacen `await` (FastAPI las corre en un
  threadpool). Es un cambio mecánico, sin tocar la lógica.

### 2.6 Una conexión nueva a PostgreSQL por consulta y por petición — Medio (rendimiento)

- **Dónde:** `src/database/bd.py:12-23`; `src/utilities/jwt_required.py:31` llama a
  `cuenta_habilitada` en cada petición, que abre su propia conexión
  (`src/models/personal.py:34-43`).
- **Problema:** el sondeo del monitoreo abre y cierra una conexión TCP por petición, e imprime
  "Conexión a PostgreSQL establecida" cada vez.
- **Sugerencia:** `psycopg2.pool.ThreadedConnectionPool` dentro de `Connection` (la interfaz
  pública no cambia) y quitar el `print`.

### 2.7 Cookie de sesión y login — Medio (seguridad)

- `src/routes/auth_login.py:40`: la cookie no tiene `samesite`, `secure` ni `max_age`. Sin
  `samesite="lax"` o `"strict"` quedan expuestas a CSRF las rutas que cambian estado
  (`PATCH /evaluacion/.../completar`, `POST /arduino/motor/iniciar`, `POST /bono-socio`). Sin
  `max_age`, la cookie muere al cerrar el navegador pero el JWT sigue valiendo 7 días.
- `src/routes/auth_login.py:21-52`: no hay límite de intentos de login.
- `src/services/auth_service.py:42-47` (`cuenta_habilitada`): ante un error de base de datos
  devuelve `True` (falla abierta).
- `src/services/auth_service.py:72-79` y `src/utilities/jwt_required.py:39`: el rol se lee del
  JWT. Si se le baja el rol a alguien, conserva los permisos anteriores hasta 7 días.
- `src/utilities/jwt_utils.py:8`: `datetime.utcnow()` está obsoleto desde Python 3.12.
- **Sugerencia:** `set_cookie(..., samesite="strict", max_age=7*24*3600, secure=<según
  despliegue>)`; contador de intentos por usuario e IP; que `cuenta_habilitada` devuelva
  también el rol vigente y se use ese; `datetime.now(timezone.utc)`.

### 2.8 Rangos de los schemas frente a los tipos de la base — Medio

- **Dónde:** `src/schemas/evaluacion.py:9`, `:10`, `:14` frente a `src/database/script.sql:49`.
- **Problema:** `num_sacos` no tiene tope y la columna es `int2` (máximo 32 767); `peso_bruto` y
  `pago` son `numeric(7, 2)` (máximo 99 999,99). Un lote de unos 100 sacos de 70 kg ya supera
  ese máximo en `peso_bruto`, y el pago de un lote grande puede pasar de S/ 99 999,99. En ambos
  casos PostgreSQL rechaza el valor y el usuario recibe un 500 genérico al completar la
  evaluación, después de haber hecho todo el monitoreo.
- **Sugerencia:** decidir con la cooperativa el tamaño máximo de lote (no se inventa aquí) y
  alinear `le=` en el schema con la precisión de las columnas, o ampliar las columnas.

### 2.9 Fórmula de humedad y redondeo de la tara — Medio (confirmar con la cooperativa)

- **Dónde:** `src/services/evaluacion_service.py:183-188` y `src/schemas/evaluacion.py:31`.
- **Problema 1:** el descuento usa `peso_neto × (H − 12) / (100 − H)`. La fórmula habitual de
  merma por secado es `peso × (H_inicial − H_final) / (100 − H_final)`, es decir, se divide
  entre `100 − 12`. La diferencia es pequeña (para H = 15: 3,53 % frente a 3,41 %), pero
  cambia el pago. Puede ser una regla propia de la cooperativa; hay que confirmarlo y dejarlo
  documentado en `AGENTS.md` sección 7.
- **Problema 2:** `round()` de Python redondea al par más cercano: `round(0.5) = 0`,
  `round(2.5) = 2`. Con 2 sacos la tara sale 0 kg y con 10 sacos sale 2 kg (no 3). Si la regla
  de la cooperativa es redondear 0,5 hacia arriba, hoy se calcula mal.
- **Sugerencia:** confirmar las dos reglas y, si corresponde, usar
  `Decimal(...).quantize(Decimal("1"), rounding=ROUND_HALF_UP)` en un único helper compartido
  por el schema y el service (hoy el cálculo de la tara está duplicado).

### 2.10 Dinero en `float4` — Medio

- **Dónde:** `src/database/script.sql:59` (`VALOR_CAFE.precio float4`).
- **Problema:** el precio entra en el cálculo del pago con `Decimal(str(float))`. `float4` tiene
  unos 7 dígitos significativos: un precio de 4 dígitos con decimales queda al borde de su
  precisión, y si el valor guardado no es exacto, el pago se calcula sobre otro precio.
- **Sugerencia:** migrar la columna a `numeric(7, 2)`.

### 2.11 Códigos HTTP y manejo de errores — Menor

- `src/routes/evaluacion.py:126-127` y `:185-186`: todo `ValueError` se responde como 404,
  incluidos los errores de validación de negocio ("peso bueno supera el tamizado", "ya fue
  completada"). Deberían ser 400 o 409.
- 46 bloques `except Exception` en `src/routes/` responden 500 sin registrar el traceback. No
  hay `logging` en todo `src/`: el diagnóstico depende de `print`.
- **Sugerencia:** excepciones de dominio propias (`NoEncontradoError`, `ReglaNegocioError`)
  convertidas a HTTP en un solo `exception_handler`, y `logging.exception(...)` en los 500.

### 2.12 Subida de imágenes — Menor

- **Dónde:** `src/routes/cooperativa.py:60-87`.
- **Problema:** la escritura a disco está en la ruta (incumple la regla de 4 capas), se lee el
  archivo completo antes de comprobar el tamaño, el tipo se decide por `content_type` y
  extensión (ambos los controla el cliente) y las imágenes reemplazadas nunca se borran (hay 8
  en `src/resources/cooperativa/`).
- **Sugerencia:** mover la lógica a `cooperativa_service`, verificar la firma del archivo con
  Pillow (`Image.open(...).verify()`) y borrar la imagen anterior al reemplazarla.

### 2.13 SQL dinámico revisado — sin hallazgo

Los f-strings de `src/models/tipo_grano.py:54`, `auditoria.py:95-110`, `cooperativa.py:86` y
`valor_cafe.py:156` solo interpolan fragmentos fijos del código (nombres de columna,
marcadores `%s`). Los valores siempre van parametrizados. No hay inyección SQL. Detalle menor:
`auditoria.py:89` filtra `fecha_hora <= 'AAAA-MM-DD 23:59:59'` y deja fuera los registros del
último segundo con fracción; es mejor `fecha_hora < fecha_hasta + 1 día`.

---

## 3. Firmware Arduino y comunicación serie

### 3.1 Sin parada de seguridad si el backend deja de responder — Medio

- **Dónde:** `arduino/logica_hardware/logica_hardware.ino:45-73`.
- **Problema:** después de `ON`, la faja gira hasta recibir `OFF`. Si el backend se cae, se
  cuelga o se desconecta el USB sin un cierre ordenado, la faja sigue corriendo y los granos
  pasan sin clasificar con el servo en `BUENO`. El modo de emergencia
  (`_on_camara_desconectada`) solo cubre la pérdida de cámara con el backend vivo.
- **Sugerencia:** watchdog en el firmware. El backend ya envía `\n` cada 20 s
  (`arduino_serial.py:114-127`); bastaría con que envíe algo cada 1-2 s mientras la faja esté
  encendida y que el Arduino ejecute el equivalente de `OFF` si no recibe nada en ~3 s.
  **[requiere permiso]**: toca el protocolo y `arduino_serial.py`.

### 3.2 `pulseIn` bloquea el loop hasta 30 ms — Medio (temporización del servo)

- **Dónde:** `arduino/logica_hardware/logica_hardware.ino:114`.
- **Problema:** cada 100 ms el loop puede quedar bloqueado hasta 30 ms esperando el eco. Un
  `SERVO:DEFECTO` que llega en ese lapso se ejecuta tarde. A eso se suma la transmisión a
  9600 baudios: `SERVO:DEFECTO\n` son 14 bytes, unos 15 ms. Frente a `SERVO_DELAY_S = 0.3`,
  el retardo variable puede llegar a ~45 ms (15 %) y no lo compensa ningún parámetro.
- **Sugerencia:** bajar el timeout de `pulseIn` a lo que exige la distancia real (unos 2000 µs
  alcanzan ~34 cm, de sobra para una tapa a 5 cm), o medir con interrupción en `ECHO_PIN`. Si
  se acepta cambiar el protocolo, usar comandos de un byte para el servo o subir a 57 600
  baudios (el comentario de la línea 30 descarta 115 200 por los clones con resonador, no
  57 600). **[requiere permiso]** para el cambio de protocolo; el timeout de `pulseIn` solo
  toca el firmware.

### 3.3 Velocidad de la faja duplicada e inconsistente — Medio

- **Dónde:** `arduino/logica_hardware/logica_hardware.ino:15` (`VELOCIDAD = 90`) frente a
  `src/config.py:39` (`FAJA_VELOCIDAD_PWM` por defecto `255`, con el comentario "DEBE
  coincidir").
- **Problema:** no coinciden. Hoy no afecta porque `.env` fija `SERVO_DELAY_S=0.3`, pero si
  alguien quita esa línea, `SERVO_DELAY_S` se recalcula con 255 (0,431 s) en lugar de 90
  (1,222 s) y el servo actúa a destiempo. Además, con el motor JGY370 la relación lineal
  PWM-velocidad calibrada con el motor anterior ya no es válida.
- **Sugerencia:** que el backend envíe la velocidad (`VEL:<n>`) o que el Arduino la anuncie al
  arrancar (`SISTEMA:LISTO:90`), para tener una sola fuente. Mientras tanto, alinear el valor
  por defecto en `config.py` y en `config-example.py`, y documentar que `SERVO_DELAY_S` del
  `.env` es obligatorio.

### 3.4 Primer comando perdido al abrir el puerto — Medio [requiere permiso]

- **Dónde:** `src/utilities/arduino_serial.py:65-69`, `:192-212`.
- **Problema:** en un Arduino Uno o Nano, abrir el puerto activa DTR y reinicia la placa. Durante
  ~1,5-2 s el bootloader descarta lo que llega. Un `ON` enviado justo después de una
  reconexión se pierde. El backend lo compensa en parte reenviando `ON` al recibir
  `SISTEMA:LISTO` (`:166-175`).
- **Sugerencia:** después de `_conectar()`, esperar `SISTEMA:LISTO` (con timeout) antes de
  aceptar comandos, o abrir con `dsrdtr=False` y `dtr=False` si la placa lo admite.

### 3.5 Estado del sensor sin marca de tiempo — Medio [requiere permiso]

- **Dónde:** `src/utilities/arduino_serial.py:146-157`, `:180-184`.
- **Problema:** si el Arduino se cuelga sin cerrar el puerto, `obtener_estado()` sigue
  devolviendo el último `LISTO` indefinidamente, y la interfaz deja iniciar el monitoreo con
  una lectura de tapa vieja.
- **Sugerencia:** guardar `time.monotonic()` de la última línea y considerar el estado no
  válido si pasaron más de ~1 s (el firmware informa cada 100 ms).

### 3.6 Hilos de keep-alive acumulados y reconexión sin lock — Menor [requiere permiso]

- **Dónde:** `src/utilities/arduino_serial.py:79-83`, `:92-110`.
- **Problema:** cada reconexión arranca un hilo de keep-alive nuevo. El anterior solo termina si
  ve `_activo = False` al despertar de su `sleep(20)`; si la reconexión ocurre dentro de esos
  20 s, sigue vivo y los hilos se acumulan. `_asegurar_conexion` se llama desde varios hilos
  sin lock y puede intentar abrir el puerto dos veces.
- **Sugerencia:** un único hilo de keep-alive creado en `__init__`, y un lock alrededor de
  `_asegurar_conexion`.

### 3.7 Restos del protocolo de la báscula — Menor

- `src/utilities/arduino_serial.py:8-17` documenta `PESO:`, `TARE` y `SCALE`. El firmware no
  implementa ninguno (`logica_hardware.ino:90`). `GET /arduino/peso`
  (`src/routes/arduino.py:16-18`) siempre responde "Esperando lectura de la báscula...".
- **Sugerencia:** marcar el endpoint y el docstring como fuera de servicio, o retirarlos hasta
  que vuelva la celda de carga. Cuando vuelva el HX711: leer con `is_ready()` sin bloquear,
  filtrar con mediana más promedio móvil, guardar el factor de calibración en EEPROM y
  responder `TARE:OK`.

### 3.8 Buffer serie sin límite — Menor

- **Dónde:** `arduino/logica_hardware/logica_hardware.ino:27`, `:49-58`.
- **Problema:** `String lineaSerial` crece sin tope si llega basura sin `\n`, y la concatenación
  de `String` fragmenta los 2 KB de SRAM del ATmega328.
- **Sugerencia:** `char buf[24]` con índice y descarte al llenarse.

### 3.9 Re-arranque automático de la faja tras un reinicio del Arduino — Menor

- **Dónde:** `src/utilities/arduino_serial.py:166-175`.
- **Problema:** si el Arduino se reinicia por una caída de tensión (por ejemplo, el servo
  alimentado desde el pin de 5 V, como advierte `arduino/servito/servito.ino:12-15`), el
  backend vuelve a encender la faja sin que el operario intervenga y sin registrar un evento
  en el monitoreo.
- **Sugerencia:** registrar un evento `registro_eventos` de severidad "alerta" cuando ocurra.

---

## 4. Reproducibilidad

### 4.1 Dependencias sin fijar — Medio

- **Dónde:** `requirements.txt` (todas con `>=`) y la celda 4 del notebook
  (`!pip install ultralytics roboflow -q`, sin versión).
- **Problema:** `tracker.py` usa la API interna de Ultralytics (`ultralytics.trackers.byte_tracker.BYTETracker`,
  `ultralytics.utils.IterableSimpleNamespace`, `Boxes`, líneas 14-17) y depende de que
  YOLO26 sea end2end sin NMS (línea 49). Un `pip install` futuro puede instalar otra versión que
  cambie esas interfaces o la salida del modelo, y los resultados de la tesis dejan de poder
  reproducirse. Tampoco queda registrada la versión de Ultralytics con la que se entrenó v6.
- **Sugerencia:** `pip freeze > requirements.lock` en la máquina de producción (con el
  `torch+cu130` real) y fijar con `==` al menos `ultralytics`, `torch`, `onnxruntime`,
  `opencv-python-headless` y `numpy`. En el notebook: `!pip install ultralytics==<versión>`
  e imprimir `ultralytics.__version__` en la salida.

### 4.2 El entrenamiento del modelo en producción no está en el repositorio — Medio

- **Dónde:** `src/ml/models/yolov26n_2cls_new/` solo tiene el notebook de fine-tuning v7, que
  parte de `MyDrive/.../yolo26n_resultados_v6_2cls/best.pt`. El notebook de v6, que generó el
  modelo en producción, no está. `best.pt` tampoco se versiona.
- **Problema:** no se puede reconstruir el modelo que produjo las métricas de la tesis. Tampoco
  se puede comprobar que el `best.pt` descargado de Drive sea el mismo con el que se midió.
- **Sugerencia:**
  1. Agregar el notebook de v6, aunque sea el último ejecutado tal cual.
  2. Guardar junto a cada modelo un `model_card.md` (o `metadata.json`) con: versión del
     dataset Roboflow, hash SHA-256 de `best.pt` y `best.onnx`, versiones de Ultralytics y
     Torch, hiperparámetros, semilla, métricas de *test* y fecha.
  3. Verificar el hash en `check_model.py` al arrancar.

### 4.3 Semillas y determinismo — Menor

- **Dónde:** notebook v7, celda 12: `seed=42` sin `deterministic=True`.
- **Problema:** la semilla fija el orden de los datos, pero en GPU los resultados varían entre
  corridas igual. Con un solo entrenamiento por versión, una diferencia de mAP entre v6 y v7
  puede ser ruido.
- **Sugerencia:** `deterministic=True` y, para comparar v6 contra v7, entrenar 3 veces con
  semillas distintas y reportar media y desviación.

### 4.4 Rutas fijas y dependencia de Colab — Menor

- Notebook v7, celda 14: `base = "/content/runs/detect/coffeeren/..."` asume dónde guarda
  Ultralytics cuando se pasa `project="coffeeren"`, y eso cambió entre versiones. Usar
  `results.save_dir` que devuelve `model.train(...)`.
- Notebook v7, celdas 6, 12 y 16: rutas de Google Drive fijas (`/content/drive/MyDrive/...`).
  Conviene concentrarlas en una celda de parámetros.
- `reset_db.ps1:2`: ruta fija a `C:\Program Files\PostgreSQL\18\bin\psql.exe`; mejor usar
  `psql` del `PATH` o una variable.
- `src/services/tracker_service.py:236`, `src/routes/cooperativa.py:77`, `src/main.py:81-82`,
  `:92`: rutas relativas al directorio de trabajo (`src/resources/...`). Si `uvicorn` se lanza
  desde otra carpeta, fallan. Resolverlas desde `os.path.dirname(__file__)`, como ya hace
  `templates_dir` (`src/main.py:84`).

### 4.5 La validación sobre fotos de la ELP no produce métricas — Medio

- **Dónde:** notebook v7, celda 16 y `docs/guia/03-reentrenamiento-camara-elp.md:188-200`.
- **Problema:** la celda 16 solo guarda predicciones para revisarlas a ojo. El criterio de
  despliegue ("reduce claramente los falsos defectos en `validacion_elp/`") no tiene número.
  Es justo la métrica que importa para el problema conocido del ~40 % de falsos defectos.
- **Sugerencia:** etiquetar `validacion_elp/` (aunque sea por carpeta, `verde/` y `defecto/`) y
  calcular precisión, recall y tasa de falsos defectos para v6 y v7 con el mismo `conf`. Dejar
  la tabla en `docs/evidencias/`.

### 4.6 Parámetros de la medición de latencia — Menor

- **Dónde:** `src/utilities/latencia.py` y `src/config.py:153-156`.
- **Problema:** el CSV del indicador de latencia no guarda la configuración con la que se midió
  (tiles, `ML_DETECTOR_FPS`, gate, dispositivo, `half`, resolución), y esos valores cambian el
  resultado.
- **Sugerencia:** escribir una cabecera con esos parámetros en cada CSV exportado.

---

## 5. Calidad general

### 5.1 Pruebas — Medio

- Las pruebas de caja blanca (`tests/caja_blanca/`, PCB-01 a PCB-12) cubren autenticación,
  cálculo de pago, rangos de precio, `_resolver_clase`, el filtro de tamaño y la compuerta de
  evidencia del servo. Faltan pruebas para las partes con más riesgo de regresión:
  - `_deduplicar_tile` y `_fusionar_cajas` (`tracker.py:261-337`): lógica geométrica no trivial
    que se prueba bien con cajas sintéticas.
  - `hay_movimiento` con desplazamiento lento (cubriría el hallazgo 1.1).
  - Orden de la cola del servo con solicitudes fuera de orden (hallazgo 1.2).
  - `_procesar_linea` de `arduino_serial.py` con líneas válidas, truncadas y con basura.
  - Que las rutas exijan autenticación: recorrer `app.routes` y comprobar que todas, salvo una
    lista blanca (`/auth/login`, `/health`, `/static`), tengan `obtener_usuario_actual` en
    sus dependencias. Habría detectado el hallazgo 2.3.
- No hay integración continua. Las pruebas de caja blanca no usan base de datos ni hardware, así
  que pueden correr en un workflow de GitHub Actions en cada push (instalando torch CPU).

### 5.2 Estructura y estado global — Menor

- Los singletons se crean al importar el módulo: `tracker_service`
  (`src/services/tracker_service.py:345`) carga YOLO y hace el warmup en cuanto algo importa
  el módulo, y `servo_controller` (`src/utilities/servo_controller.py:166`) arranca un hilo. Esto
  hace más lentas las pruebas y obliga a tener el modelo para importar cualquier ruta.
  Inicializarlos en el `lifespan` de `src/main.py:52-63`.
- Lógica de evaluación en `src/main.py:245-297`: las páginas `/analisis` y `/monitoreo` viven
  en `main.py` en vez de en `src/routes/`.
- Archivos sueltos en la raíz: `promt_gruia.md` (con errata en el nombre) y `check_model.py`
  (mejor en `scripts/`). Hay `readme.md` y además `docs/DOCUMENTACION_SISTEMA.md` y
  `docs/arquitectura.md` que se solapan con `docs/guia/`; revisar si siguen vigentes o se
  pueden fusionar, según la regla de "sin archivos inútiles".

### 5.3 Documentación — Menor

- `docs/incidencias/incidencia_proyecto.md:267` dice que el modelo binario es suficiente "para
  separar físicamente y calcular el grado". El grado SCA ya no se calcula (`AGENTS.md`
  sección 7). Al ser un registro histórico, conviene agregar una nota en vez de reescribirlo.
- `src/utilities/arduino_serial.py:4-17`: el protocolo documentado no coincide con el firmware
  (hallazgo 3.7).
- `docs/guia/02-modulo-ml.md` sí documenta los parámetros del tracker; al corregir 1.1, 1.2 o
  1.6 hay que actualizar su tabla en el mismo cambio (`AGENTS.md` sección 8).

---

## 6. Las 5 mejoras más importantes, en orden de prioridad

1. **Sacar las credenciales del repositorio y exigir `SECRET_KEY`** (hallazgo 2.1). Cambiar la
   contraseña de PostgreSQL, `git rm --cached src/config.py` y no arrancar sin una clave JWT
   real. Hoy cualquiera con acceso al repositorio puede firmar un token de Administrador.
2. **Corregir el gate de movimiento y validarlo con un lote de cantidad conocida**
   (hallazgo 1.1). Con la faja lenta puede estar omitiendo granos, y eso afecta directamente al
   conteo, a la separación y a las métricas de la tesis. Acompañarlo con la prueba unitaria de
   la sección 5.1.
3. **Calcular el conteo de defectos en el servidor** (hallazgo 2.2) y proteger el código EVA
   con `UNIQUE` y una secuencia (hallazgo 2.4). El resultado de la clasificación no puede
   depender de lo que envíe el navegador.
4. **Ordenar la cola del servo por instante de ejecución y congelar la clase decidida**
   (hallazgos 1.2 y 1.4), y agregar el watchdog de la faja en el firmware (hallazgo 3.1). Las
   dos cosas requieren permiso explícito porque tocan archivos protegidos, pero son las que
   determinan si la separación física corresponde a lo que el sistema reporta.
5. **Hacer reproducible el modelo** (hallazgos 4.1, 4.2 y 4.5): fijar versiones, versionar el
   notebook de v6, registrar el hash y los metadatos de cada `best.pt`, y medir con números la
   tasa de falsos defectos sobre fotos de la ELP antes de desplegar v7.

Inmediatamente después: autenticar los endpoints de video (2.3) y pasar las rutas a `def`
(2.5). Son cambios pequeños con buen retorno.
