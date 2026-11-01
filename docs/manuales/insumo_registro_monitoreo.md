# Insumo para el Manual de Usuario: registro de muestra, monitoreo y finalización

Material para ampliar las secciones 4.1.2 (Registro de muestra), 4.1.3 (Monitoreo en tiempo real),
4.1.4 (Finalización y peso de grano bueno) y 5.1 (Alertas de validación en pantalla) de
`Manual_Usuario_CoffeeRen.docx`.

- Fecha de extracción: 2026-10-29, rama `temporal`.
- Todo texto entre comillas o en negrita es **literal** del código, con su ubicación `archivo:línea`.
  Se respetan las tildes que faltan en el código (por ejemplo, el botón dice "clasificacion" sin tilde).
- Los mensajes de registro y finalización se comprobaron además en la aplicación en ejecución
  (Playwright contra la base de desarrollo).
- Las diferencias con el manual actual están al final, en la sección E.

---

## A. Registro de muestra

Página `/registro`. Plantilla `src/templates/registro.html`, lógica `src/static/js/registro.js`,
validación del servidor `src/schemas/evaluacion.py:7-47` y `src/services/evaluacion_service.py:34-66`.

Encabezado: **Registro de muestra** y "Completa la ficha tecnica para iniciar clasificacion. El
monitoreo se abrira en una vista dedicada." (`registro.html:10-11`). Dos tarjetas: **Datos del
caficultor** y **Datos de la muestra** (`registro.html:17`, `:44`).

### A.1 Tabla de campos

"Al escribir" significa que el texto de ayuda o error aparece debajo del campo mientras se escribe
(evento `input`). Los textos "Máximo: …" solo aparecen cuando el campo ya tiene un valor válido; con el
campo vacío no hay texto de ayuda.

| Etiqueta exacta | Control | Unidad | Valor por defecto o placeholder | Texto de ayuda visible | Regla en el navegador | Regla en el servidor |
|---|---|---|---|---|---|---|
| **Tipo documento** (`registro.html:20`) | Lista | — | Placeholder "Seleccionar un tipo". Al cargar la página queda elegido **DNI** (`registro.js:229-230`) | — | Obligatorio. Cambia la regla del número de documento | No se envía al servidor; el servidor solo valida el número |
| **Número de documento** (`registro.html:27`) | Texto | — | Placeholder según el tipo: DNI "Ingrese 8 digitos de DNI"; Pasaporte o Carnet "Ingrese 8-12 caracteres"; sin tipo "Ingrese documento (8 a 12 caracteres)" (`registro.js:105-128`) | Mientras el número está incompleto: "DNI: exactamente 8 digitos numericos." o "Pasaporte/Carnet: 8 a 12 caracteres alfanumericos." (`registro.js:109`, `:116`) | DNI: solo dígitos, máximo 8 (el resto se borra al escribir). Pasaporte/Carnet: letras y números, se pasan a mayúsculas, máximo 12. La búsqueda del caficultor se lanza sola al llegar a la longitud válida | Formato `^[A-Za-z0-9]{8,12}$` (`schemas/evaluacion.py:8`). El caficultor debe existir y estar activo (`evaluacion_service.py:44-49`) |
| **Nombre del caficultor** (`registro.html:33`) | Texto, solo lectura | — | Placeholder "Ejemplo: Juan Perez" | — | Se completa con la búsqueda; no se edita | — |
| **Tipo de caficultor** (`registro.html:38`) | Texto, solo lectura | — | Placeholder "Ejemplo: Socio" | — | Se completa con la búsqueda; no se edita | — |
| **Tipo de grano** (`registro.html:48`) | Lista | — | "Seleccionar tipo". Opciones de la tabla de tipos de grano | — | Obligatorio | Debe existir: "El tipo de grano seleccionado no existe." (`evaluacion_service.py:56`) |
| **Número de sacos** (`registro.html:55`) | Número | sacos | Placeholder "Ejemplo: 5" | — | Entero ≥ 1. El teclado no deja escribir `e`, `+`, `-`, `.` ni `,` (`registro.js:421`). Al salir del campo se quitan decimales (`registro.js:416`) | Entero ≥ 1 (`schemas/evaluacion.py:9`) |
| **Peso total (kg)** (`registro.html:63`) | Número | kg | Placeholder "Ejemplo: 275.50" | "Máximo: {sacos × 70} kg." (`registro.js:388`), por ejemplo "Máximo: 350 kg." | Mayor que 0; ≤ sacos × 70; mayor que la tara `round(sacos × 0.25)`. No deja escribir `e`, `+`, `-`. Al salir del campo se redondea a 2 decimales (`registro.js:71-76`) | Mayor que 0; ≤ sacos × 70; mayor que la tara (`schemas/evaluacion.py:10`, `:24-36`) |
| **Peso de muestra (gr.)** (`registro.html:69`) | Lista | g | "Seleccione...". Opciones "100 gr." a "300 gr." de 50 en 50 | — | Obligatorio | Debe ser 100, 150, 200, 250 o 300 (`schemas/evaluacion.py:18-20`, `:37-38`) |
| **Humedad (%)** (`registro.html:84`) | Número | % | Placeholder "Ejemplo: 13" | — | Entero de 1 a 100. No deja escribir `.`, `,`, `e`, `+`, `-` | Entero de 1 a 100 (`schemas/evaluacion.py:11`) |
| **Peso trillado (gr.)** (`registro.html:90`) | Número | g | Placeholder "Ejemplo: 930.00" | "Máximo: {83 % del peso de muestra} gr.", por ejemplo "Máximo: 249.00 gr." con muestra de 300 g (`registro.js:259`, `:405`) | Mayor que 0; distinto del peso de muestra; no mayor que él; ≤ 83 % de él. Redondeo a 2 decimales al salir | Mismas cuatro reglas (`schemas/evaluacion.py:12`, `:39-44`) |
| **Número de tamiz** (`registro.html:98`) | Lista | — | "Seleccionar tamiz". Opciones "N° 14" a "N° 20" | — | Obligatorio | Entero ≥ 1 (`schemas/evaluacion.py:14`) |
| **Peso tamizado (gr.)** (`registro.html:112`) | Número | g | Placeholder "Ejemplo: 870.00" | "Máximo: {peso trillado} gr.", por ejemplo "Máximo: 240.00 gr." (`registro.js:410`, `:414`) | Mayor que 0; no mayor que el peso trillado. Redondeo a 2 decimales al salir | Mayor que 0; no mayor que el trillado (`schemas/evaluacion.py:15`, `:45-46`) |

Nota: los placeholders de peso trillado (930.00) y tamizado (870.00) superan el máximo posible
(249 g con la muestra más grande de 300 g). No conviene copiarlos al manual como ejemplo de valor válido.

### A.2 Tabla de errores

Formas en que aparece un error:

- **Bajo el campo:** texto rojo mientras se escribe. No bloquea por sí solo; avisa.
- **Ventana:** modal con título **Atención**, el mensaje y el botón **Entendido**. Se cierra sola a los
  5,5 s (`main.js:61-64`, `:82`, `:120`). Aparece al pulsar **Iniciar clasificacion y monitoreo**, se
  muestra solo el primer error encontrado y el foco va al campo con el error (`registro.js:41-45`).
- **Bajo los botones:** texto rojo bajo la fila de botones (`registro.html:125`) cuando el servidor rechaza
  el registro (`registro.js:324`).

Al pulsar el botón, el orden de comprobación es: 1) precios del día, 2) campos vacíos, 3) caficultor
validado, 4) reglas de la muestra en el orden de la tabla, 5) sensor de la tapa, 6) servidor
(`registro.js:426-453`).

| Campo | Dato incorrecto de ejemplo | Mensaje exacto bajo el campo | Mensaje exacto en ventana o alerta | Momento |
|---|---|---|---|---|
| Cualquier campo obligatorio | Vacío | — | Globo del propio navegador junto al campo (`reportValidity()`, `registro.js:343`). El texto no sale del código: depende del navegador y su idioma (en Chrome en inglés, "Please fill out this field." / "Please select an item in the list.") | Al enviar |
| Número de sacos | 0 | "Debe ser un entero positivo (mínimo 1)." (`registro.js:372`) | "El número de sacos debe ser un entero positivo (mínimo 1)." (`registro.js:269`) | Al escribir / al enviar |
| Peso total | 0 (o negativo pegado desde el portapapeles; el teclado no deja escribir `-`) | "Debe ser un número positivo (kg)." (`registro.js:379`) | "El peso total debe ser un número positivo (en kg)." (`registro.js:270`) | Al escribir / al enviar |
| Peso total | 400 con 5 sacos (máximo 350) | "No puede superar 350 kg (5 sacos × 70 kg)." (`registro.js:384`) | "El peso total no puede superar 350 kg (5 sacos × 70 kg)." (`registro.js:272`) | Al escribir / al enviar |
| Peso total | 1 con 5 sacos (tara = 1 kg) | "Debe ser mayor a la tara de los sacos: 1 kg (5 sacos × 0.25 kg)." (`registro.js:386`) | "El peso total debe ser mayor a la tara de los sacos: 1 kg (5 sacos × 0.25 kg). Verifique el peso total o el número de sacos." (`registro.js:274`) | Al escribir / al enviar |
| Humedad | 0 | "Debe ser un número entero (sin decimales)." (`registro.js:398`) | "La humedad debe ser un número entero (sin decimales)." (`registro.js:275`) | Al escribir / al enviar |
| Humedad | 101 | "La humedad no puede superar 100%." (`registro.js:399`) | "La humedad no puede superar 100%." (`registro.js:276`) | Al escribir / al enviar |
| Humedad | 12.5 | El teclado no deja escribir el punto. Si se pega "12.5": "Debe ser un número entero (sin decimales)." y al salir del campo el valor pasa a 12 (`registro.js:64-69`) | No llega a mostrarse: el valor ya quedó entero | Al escribir / al salir del campo |
| Peso trillado | 0 | "Debe ser un número positivo (gr.)." (`registro.js:253`) | "El peso trillado debe ser un número positivo (en gr.)." (`registro.js:278`) | Al escribir / al enviar |
| Peso trillado | 300 con muestra de 300 g (igual) | "No puede superar el 83% del peso de muestra (249.00 gr.)" | "El peso trillado debe ser diferente al peso de muestra." (`registro.js:279`) | Al escribir / al enviar |
| Peso trillado | 310 con muestra de 300 g (mayor) | "No puede superar el 83% del peso de muestra (249.00 gr.)" | "El peso trillado no puede ser mayor al peso de muestra." (`registro.js:280`) | Al escribir / al enviar |
| Peso trillado | 260 con muestra de 300 g (> 83 %) | "No puede superar el 83% del peso de muestra (249.00 gr.)" (`registro.js:257`) | "El peso trillado no puede superar el 83% del peso de muestra." (`registro.js:281`) | Al escribir / al enviar |
| Peso tamizado | 245 con trillado de 240 | "No puede superar el peso trillado (240.00 gr.)" (`registro.js:257`) | "El peso tamizado no puede ser mayor al peso trillado." (`registro.js:284`) | Al escribir / al enviar |
| Número de documento | DNI con 7 dígitos | "DNI: exactamente 8 digitos numericos." (texto gris de ayuda, no rojo) (`registro.js:210`) | Globo junto al campo: "Debe consultar y validar un caficultor registrado para continuar" (`registro.js:346`) | Al escribir / al enviar |
| Número de documento | Pasaporte con 7 caracteres | "Pasaporte/Carnet: 8 a 12 caracteres alfanumericos." (gris) | El mismo globo anterior | Al escribir / al enviar |
| Caficultor | DNI 12345670, no registrado | "No existe un caficultor con ese documento. Se recomienda registrarlo para continuar con el proceso." seguido del enlace **Registrar caficultor** (rojo) (`routes/caficultor.py:40-43`, `registro.js:174`) | El mismo globo: "Debe consultar y validar un caficultor registrado para continuar" | Al completar el número / al enviar |
| Caficultor | Caficultor registrado pero inactivo | El mismo mensaje de "no existe": la búsqueda solo devuelve caficultores activos (`models/caficultor.py:32`) | El mismo globo | Al completar el número / al enviar |
| Precios del día | No hay precios de café con fecha de hoy | — | Ventana con título **Precios de café pendientes** (`main.js:188`). Evaluador: "No hay precios de café registrados hoy. Sin ellos no se puede registrar la muestra ni iniciar el monitoreo. Comunique al administrador o gerente que registre los precios del día para continuar." Gerente o Administrador: "No hay precios de café registrados hoy. Sin ellos no se puede registrar la muestra ni iniciar el monitoreo. Regístrelos en Valor de café para continuar." (`main.js:189-194`) | Al abrir la página (`registro.js:462`) y otra vez al pulsar el botón (`registro.js:429`) |

**Reglas que existen solo en el servidor** (el usuario no las ve en uso normal porque el navegador las
detiene antes, o porque la pantalla no permite el dato):

- "El caficultor no se encuentra activo." (`evaluacion_service.py:49`): no se ve, porque un caficultor
  inactivo ya sale como "no existe" en la búsqueda.
- "No existe un caficultor registrado con ese numero de documento." (`evaluacion_service.py:46`) y
  "El tipo de grano seleccionado no existe." (`:56`): solo si el dato cambia entre la búsqueda y el envío.
  Se mostrarían en rojo bajo los botones.
- "El peso de muestra debe ser 100, 150, 200, 250 o 300 gr." (`schemas/evaluacion.py:38`): la lista no
  permite otro valor.
- El mensaje de precios del servidor (`evaluacion_service.py:62-66`) no se muestra tal cual: si llega, la
  página abre la misma ventana **Precios de café pendientes** (`registro.js:321-322`).
- Cualquier otra falla del servidor: "No se pudo procesar la solicitud." (`routes/evaluacion.py:55`) o
  "No se pudo registrar la evaluación." (`registro.js:314`), en rojo bajo los botones.

### A.3 Búsqueda del caficultor

- **Cómo se dispara:** sola, sin botón, 0,3 s después de que el número alcanza una longitud válida
  (DNI: 8; Pasaporte o Carnet: de 8 a 12) (`registro.js:197-215`). Cambiar el tipo de documento borra el
  resultado y vuelve a buscar (`registro.js:356-362`). Editar el número borra nombre y tipo de caficultor.
- **Mensajes** (debajo del número de documento, `registro.html:29`):

| Caso | Mensaje literal | Color |
|---|---|---|
| Número incompleto | "DNI: exactamente 8 digitos numericos." / "Pasaporte/Carnet: 8 a 12 caracteres alfanumericos." | Gris |
| Sin tipo de documento elegido | "Selecciona primero el tipo de documento." (`registro.js:205`) | Rojo |
| Buscando | "Buscando datos del caficultor..." (`registro.js:168`) | Gris |
| Encontrado | "Caficultor encontrado correctamente." (`routes/caficultor.py:46`). Se llenan nombre y tipo | Verde |
| No encontrado o inactivo | "No existe un caficultor con ese documento. Se recomienda registrarlo para continuar con el proceso." + enlace **Registrar caficultor** a `/nuevo-caficultor` | Rojo |
| Error del servidor | "No se pudo consultar el caficultor." (`routes/caficultor.py:50`) | Rojo |

La búsqueda solo consulta la base de datos de CoffeeRen. No consulta RENIEC (eso ocurre en Registrar
caficultor).

### A.4 Sensor de la tapa

Sí: el registro exige la tapa cerrada. Al pulsar el botón, después de validar el formulario, la página
consulta `GET /arduino/estado`; el botón cambia a "Verificando sensor..." (`registro.js:432-450`).
Si el sensor no confirma la tapa cerrada, se abre una ventana **Atención** y **no se registra la
evaluación**. Mensajes (vienen de `src/services/arduino_service.py:6-41`):

| Situación | Mensaje exacto | Qué debe hacer el evaluador |
|---|---|---|
| Tapa abierta o el sensor no ve la muestra | "Tapa abierta o sin muestra ({distancia} cm). Cierre la tapa para continuar." (`arduino_service.py:40`) | Cerrar la tapa y volver a pulsar el botón |
| Arduino desconectado | "Arduino no conectado (COM5). Verifique el cable USB." (`arduino_service.py:14`). El puerto sale de la configuración (`ARDUINO_PORT`); COM5 es el valor por defecto. Comprobado en la aplicación (captura `registro-sensor-sin-arduino.png`) | Revisar el cable USB del Arduino y volver a pulsar |
| Arduino conectado sin lectura del sensor | "No se recibió lectura del sensor. Verifique el Arduino." (`arduino_service.py:22`) | Revisar el Arduino y volver a pulsar |
| La consulta falla (servidor o red) | "No se pudo verificar el sensor Arduino. Revise la conexión USB." (`registro.js:446`) | Revisar la conexión y volver a pulsar |

Con la tapa cerrada, el servidor responde "Muestra detectada a {distancia} cm. Lista para iniciar."
(`arduino_service.py:33`), pero ese texto no se muestra: la página pasa directo al registro.
Existe un texto de respaldo, "Debe cerrar la tapa luego de haber ingresado los granos de café para
continuar al monitoreo." (`registro.js:440`), que no aparece en la práctica porque el servidor siempre
envía un mensaje.

### A.5 Botones

| Botón (texto exacto) | Qué hace | Confirmación |
|---|---|---|
| **Iniciar clasificacion y monitoreo** (`registro.html:123`, sin tilde en el código) | Hace las comprobaciones de A.2 y A.4, guarda la evaluación y abre `/monitoreo/{id}`. Mientras trabaja muestra "Verificando sensor..." y luego "Registrando..." (`registro.js:295`) | No |
| **Limpiar formulario** (`registro.html:122`) | Borra todos los campos, mensajes y el caficultor encontrado (`registro.js:331-339`). **Tipo documento** vuelve a "Seleccionar un tipo" (ya no queda DNI elegido; comprobado en la aplicación) y hay que elegirlo otra vez | No |

---

## B. Monitoreo

Página `/monitoreo/{id}`. Plantilla `src/templates/monitoreo.html`, lógica `src/static/js/monitoreo.js`.
El registro del monitoreo muestra cada mensaje con su minuto y segundo (mm:ss) y **el más reciente
arriba**; guarda hasta 80 mensajes (`monitoreo.js:183`, `:221-224`).

### B.1 Secuencia de arranque

Arranque normal (evaluación recién registrada), en orden cronológico:

| # | Mensaje literal | Origen |
|---|---|---|
| 1 | "Iniciando sistema..." | `monitoreo.js:824` |
| 2 | "Cargando modelo y conectando cámara..." | `monitoreo.js:469` |
| 3 | "Esperando primer frame de la cámara..." | `monitoreo.js:480` |
| 4 | "Cámara activa. Arrancando faja transportadora..." | `monitoreo.js:485` |
| 5 | "Faja iniciada." (verde) o "No se pudo iniciar la faja. Verifique la conexión Arduino." (rojo) | `arduino_service.py:71`, `monitoreo.js:431`, `:434` |
| 6 | "Faja en marcha. Captura YOLO activa." | `monitoreo.js:492` |
| 7 | "Monitoreo iniciado — modelo yolov26n_2cls." (llega del servidor con la primera consulta, 1,5 s después) | `tracker_service.py:100`, `monitoreo.js:361` |

El mensaje 6 aparece aunque la faja no haya arrancado (`monitoreo.js:486-492`); en ese caso el
indicador **Faja** queda en "Faja: detenida".

Variantes de arranque:

| Caso | Mensaje literal | Origen |
|---|---|---|
| Se recarga la pestaña con el monitoreo de esta evaluación en curso | "Cámara conectada. Monitoreo en curso." Luego se repiten los mensajes que el servidor ya tenía del lote | `monitoreo.js:149` |
| Había un monitoreo abierto de otra evaluación | "Había un monitoreo de otra evaluación en curso. Se cerró para iniciar este lote." y sigue la secuencia normal desde el paso 2 | `monitoreo.js:139` |
| No se pudo consultar el estado del servidor | "No se pudo verificar el servidor. Reintentando arranque..." y sigue desde el paso 2 | `monitoreo.js:154` |
| Falla el arranque | "Error: " + motivo, y aparece el botón **Reintentar captura**. Motivos: "No se pudo iniciar la cámara." (`routes/video.py:86`), "No se pudo iniciar el monitoreo." (`routes/video.py:83`), "La cámara no respondió a tiempo. Verifique la conexión." (15 s sin imagen, `monitoreo.js:482`), "No se pudo iniciar la captura." (respaldo, `monitoreo.js:476`) | `monitoreo.js:498-499` |

Mensajes en el recuadro del video (no en el registro):

| Mensaje literal | Cuándo | Origen |
|---|---|---|
| "Conectando cámara..." | Mientras llega la primera imagen | `monitoreo.html:75` |
| "Tiempo de espera agotado. Verifique la cámara." | 10 s sin la primera imagen | `monitoreo.js:110` |
| "No se pudo conectar con el stream de video" | Error al pedir la primera imagen | `monitoreo.js:105` |
| "Desconexión con cámara. La clasificación se ha detenido." | Cámara desconectada durante el lote | `tracker_service.py:141`, `monitoreo.js:392-393` |
| "Cámara no disponible" | Texto por defecto del recuadro de error | `monitoreo.html:82` |

### B.2 Indicadores de Cámara, Faja, Arduino y Modelo

Fila de etiquetas bajo la distribución de granos (`monitoreo.html:150-155`). Colores
(`src/static/css/monitoreo.css:276-301`, `input.css:18`, `:39`, `:41`): **verde** = funcionando,
**ámbar** = detenido, **rojo** = falla, **gris** = sin dato. Se actualizan cada 1,5 s mientras la captura
está activa (`monitoreo.js:373`); antes de la primera actualización muestran "—".

| Indicador | Texto | Color | Significado |
|---|---|---|---|
| Cámara | "Cámara: —" | Gris | Aún sin dato |
| | "Cámara: en vivo" | Verde | La clasificación está activa |
| | "Cámara: detenida" | Ámbar | La clasificación no está activa |
| | "Cámara: desconectada" | Rojo | Se perdió la cámara; la clasificación se detuvo (`monitoreo.js:241-243`) |
| Faja | "Faja: —" | Gris | Aún sin dato |
| | "Faja: en marcha" | Verde | El Arduino aceptó la orden de arranque |
| | "Faja: detenida" | Ámbar | No arrancó o ya se detuvo (`monitoreo.js:248`) |
| Arduino | "Arduino: —" | Gris | Aún sin dato |
| | "Arduino: conectado" | Verde | El Arduino responde |
| | "Arduino: sin conexión" | Rojo | El servidor no tiene conexión con el Arduino (cable USB) |
| | "Arduino: sin respuesta" | Rojo | La consulta del estado del Arduino falló (`monitoreo.js:407-410`) |
| Modelo | "Modelo: —" | Gris | Aún sin dato |
| | "Modelo: yolov26n_2cls" | Verde | Clasificación activa con ese modelo |
| | "Modelo: yolov26n_2cls" | Gris | Clasificación no activa (`monitoreo.js:244`) |

El indicador **Faja** cambia solo al arrancar y al detener la faja; no se consulta durante el lote.

### B.3 Tabla de mensajes del registro del monitoreo

| Mensaje literal | Cuándo aparece | Qué debe hacer el evaluador |
|---|---|---|
| "Primer grano detectado. Conteo en marcha." (`monitoreo.js:305`) | Al contarse el primer grano | Nada; confirma que el conteo funciona |
| "Tapa abierta — se registrará como incidencia." (`monitoreo.js:416`) | El sensor deja de ver la tapa cerrada. La faja **no** se detiene | Cerrar la tapa lo antes posible |
| "Tapa cerrada — estuvo abierta {N}s." (`monitoreo.js:421`), por ejemplo "Tapa cerrada — estuvo abierta 7s." | Al volver a cerrarse. Se guarda la incidencia (segundo de apertura, de cierre y duración) | Nada; la incidencia saldrá en el resumen |
| "Sin granos hace 10 s — si el lote terminó, presione Finalizar monitoreo." (`monitoreo.js:313`) | 10 s sin detectar granos después del primero. El botón **Finalizar monitoreo** empieza a parpadear (`monitoreo.js:316`). Si vuelven a pasar granos, el parpadeo se quita sin mensaje | Si ya pasó toda la muestra, pulsar **Finalizar monitoreo** |
| "Objeto extraño detectado — desviado al canal de defecto." (`tracker_service.py:248`) | El modelo ve un objeto que no reconoce como grano (piedra, palito, pajilla). Puede venir con una miniatura; al pulsarla se abre la foto ("Ver evidencia completa", `monitoreo.js:212`) | Nada; ya se desvió y cuenta como defecto |
| "Había un monitoreo de otra evaluación en curso. Se cerró para iniciar este lote." (`monitoreo.js:139`) | Al abrir el monitoreo con otro lote abierto | Nada; el lote anterior se cerró sin guardarse |
| "Desconexión con cámara. La clasificación se ha detenido." (`tracker_service.py:141`, `monitoreo.js:392-394`) | Se pierde la cámara. Se detiene la faja, el desviador queda fijo en el lado de defecto, aparece **Reintentar captura** | Revisar el cable USB de la cámara y pulsar **Reintentar captura**, o **Finalizar monitoreo** (ver B.4) |
| "Error: No se pudo iniciar la cámara." y demás de B.1 | Falla el arranque o el reintento | Revisar la cámara y pulsar **Reintentar captura** |
| "No se pudo iniciar la faja. Verifique la conexión Arduino." (`arduino_service.py:71`, `monitoreo.js:434`) | La faja no arrancó | Revisar cable y alimentación del Arduino |
| "No se pudo detener la faja. Verifique la conexión Arduino." (`monitoreo.js:444`) | Falla la orden de parada | Revisar el Arduino; apagar la faja a mano si sigue andando |
| Arduino sin conexión o sin respuesta | **No hay mensaje en el registro**: solo cambia el indicador a "Arduino: sin conexión" o "Arduino: sin respuesta". Mientras dure, no se registran aperturas de tapa (`monitoreo.js:407-409`) | Revisar el cable USB del Arduino |
| Error al cargar el modelo | **No hay mensaje en pantalla.** El modelo se carga una vez al arrancar el servidor; si falta el archivo, el servidor no arranca (`src/ml/tracker.py:93`, `:180`) y la página no abre | Avisar al responsable técnico (Manual de Mantenimiento) |
| "Generando reporte ..." (`monitoreo.js:515`) | Al finalizar | Queda detrás de la ventana de finalización |
| "Reporte: {N} defectos equiv." (`monitoreo.js:519`) | Al finalizar | Ídem |
| "Error al generar reporte: " + motivo (`monitoreo.js:521`) | Falla el reporte al finalizar | Ídem |
| "Evaluacion finalizada. Código: {código}" (`monitoreo.js:753`) | Evaluación guardada | Ídem |
| "Peso bueno: {peso} g — factor de rendimiento {factor}" (`monitoreo.js:645`) | Rendimiento calculado | Ídem |
| "Monitoreo detenido. Faja apagada." (`tracker_service.py:132`) | Al detener la captura. No se ve en vivo (la página ya dejó de consultar); queda en el registro del resumen del análisis | — |

Colores de las líneas (`monitoreo.css:351-353`): gris = información, verde = correcto, ámbar = alerta,
rojo = error.

Qué queda guardado: el registro del monitoreo que se ve después en **Resumen del análisis** contiene
solo los mensajes que emite el servidor (inicio, objetos extraños, cámara desconectada, detención)
(`evaluacion_service.py:281-284`). Los de primer grano, tapa y 10 s sin granos solo existen en la
pantalla del monitoreo; las aperturas de tapa se guardan aparte como incidencias.

### B.4 Botones

| Botón | Ventana de confirmación (texto exacto) | Qué pasa con los datos |
|---|---|---|
| **Finalizar monitoreo** (`monitoreo.html:166`) | Título "¿Finalizar monitoreo?", mensaje "¿Deseas detener la faja y generar el reporte final?", botones **Sí** / **No** (`monitoreo.js:808-811`, `main.js:136`) | Con **Sí** el botón cambia a "Finalizando...", se detienen faja y captura, se guarda el conteo y las incidencias de tapa, y se asigna el código EVA (sección C) |
| **Reintentar captura** (`monitoreo.html:69`) | Sin confirmación. Solo aparece si el arranque falló o se desconectó la cámara | Vuelve a lanzar la secuencia de B.1. **Tras una desconexión de cámara, el conteo del lote vuelve a 0** (el servidor reinicia el conteo al iniciar, `tracker_service.py:91`) y se borran los mensajes de servidor del lote (`tracker_service.py:97`). El cronómetro vuelve a 00:00. Las incidencias de tapa ya anotadas se conservan |
| **Volver a registro** (`monitoreo.html:165`) | Título "Salir del monitoreo", mensaje "Si sales ahora, la clasificación en curso se cancelará y los datos de esta sesión no se guardarán. ¿Deseas salir de todas formas?", botones **Sí** / **No** (`monitoreo.js:788-791`) | Se detienen faja y captura y se vuelve a `/registro`. El conteo y los mensajes se pierden. La muestra registrada **sí queda en la base de datos**, como evaluación sin código (no aparece en Buscar reportes) |

Si el evaluador intenta cerrar la pestaña o salir de la página por otro medio durante el monitoreo, el
navegador pide confirmación con su propio texto (`monitoreo.js:781-785`).

### B.5 Zonas de la pantalla

| Zona | Contenido literal | Origen |
|---|---|---|
| Franja superior | "Monitoreo en tiempo real" y los datos **Caficultor**, **DNI**, **Tipo**, **Grano**, **Tamiz**, **Sacos**, **Peso bruto**. La etiqueta dice "DNI" aunque el documento sea pasaporte o carné. Si la página se abre en otra pestaña, los datos salen como "—" | `monitoreo.html:14-51`, `monitoreo.js:34-44` |
| Video | **En vivo**, **Análisis:** con el cronómetro mm:ss, y la velocidad "N FPS" en la esquina superior derecha. El rótulo **En vivo** es fijo: se muestra siempre, aunque la cámara esté desconectada | `monitoreo.html:61-67`, `:85` |
| **Análisis del lote** | Cuatro contadores: **Total granos**, **Defectos**, **Buenos**, **% Defecto** (= defectos / total, redondeado) | `monitoreo.html:94-111`, `monitoreo.js:251-264` |
| **Distribución de granos** | Dos barras, **Defectos** y **Buenos**; el largo de cada una es su porcentaje del total | `monitoreo.html:114-136` |
| **Objetos extraños** | Contador oculto mientras sea 0. Texto: "Enmarcados en azul sobre el video y desviados al canal de defecto. Ya están contados dentro de «Defectos»." | `monitoreo.html:140-147`, `monitoreo.js:272-275` |
| Estado del sistema | Indicadores de B.2 | `monitoreo.html:150-155` |
| **Registro del monitoreo** | Mensajes de B.1 y B.3 | `monitoreo.html:158-159` |

**Objetos extraños con el modelo de 2 clases:** sigue existiendo. El modelo solo tiene las clases
`defecto` y `verde`, pero el seguimiento marca como `desconocido` todo objeto que nunca alcanzó la
confianza mínima para ser grano (`src/ml/models/yolov26n_2cls/constants.py:41`, `:54`;
`src/ml/tracker.py:672-673`). Cada uno equivale a un defecto (`constants.py:80`), se desvía al canal de
defecto y suma en **Defectos**.

---

## C. Finalización y peso de grano bueno

Ventana sobre la página de monitoreo (`monitoreo.html:173-238`). No tiene botón de cerrar ni se cierra
con un clic fuera.

### C.1 Los tres pasos

Al abrirse: título "Finalizando monitoreo...", texto "Por favor espera mientras se guardan los datos y
se genera el reporte." y botón inferior "Procesando..." desactivado (`monitoreo.js:554-567`).

| Paso (texto literal) | Qué hace | Si falla |
|---|---|---|
| "Deteniendo faja y captura YOLO" (`monitoreo.html:190`) | Apaga la faja y la captura | Se marca como hecho antes de ejecutarse (`monitoreo.js:702-703`); un error aquí no se muestra |
| "Generando reporte del análisis" (`monitoreo.html:193`) | Calcula el resumen del lote. Mientras tanto el texto cambia a "Calculando resumen..." y luego "Calculando resumen... Peso capturado: 0.00 g" (`monitoreo.js:706`, `:718`) | Se marca como hecho igual; el error solo queda en el registro del monitoreo ("Error al generar reporte: …") (`monitoreo.js:520-521`, `:721`) |
| "Guardando evaluación en el sistema" (`monitoreo.html:196`) | Guarda conteo e incidencias y asigna el código EVA | Ícono ❌, título "Error al finalizar", el texto pasa a ser el motivo (por ejemplo "No se pudo finalizar la evaluación.", `routes/evaluacion.py:188`) y el botón inferior dice "Cerrar e intentar de nuevo": cierra la ventana y reactiva **Finalizar monitoreo** (`monitoreo.js:664-681`) |

Los íconos de estado son ⏳ (pendiente), ✅ (hecho) y ❌ (error) (`monitoreo.js:537-548`).

Al terminar bien: título "Evaluación completada", texto "Pesa el grano bueno separado e ingresa el
valor para calcular el factor de rendimiento.", recuadro **Resultado** con **Código** (por ejemplo
EVA0000021) y **Granos**, el campo del peso y el botón inferior "Registra el peso bueno para continuar",
desactivado (`monitoreo.js:570-585`).

El código tiene también un título "Clasificación finalizada automáticamente" con el texto "No se
detectaron nuevos granos en los últimos 10 segundos. El sistema detuvo el proceso y está guardando los
resultados." (`monitoreo.js:554-559`), pero **nunca se usa**: la finalización solo se llama en modo
manual (`monitoreo.js:815`). El sistema no finaliza solo.

### C.2 Campo "Peso de grano bueno (g)"

Etiqueta **Peso de grano bueno (g)**, placeholder "Ej: 420", número entero (`monitoreo.html:220-224`).
Texto de ayuda inicial: "Pesa el grano bueno separado e ingresa el valor en gramos enteros."; al cargar
el resumen cambia a "Gramos enteros. El peso de grano bueno no puede superar los {N} g (peso tamizado)."
(`monitoreo.js:600-601`).

**Regla exacta del máximo — hay tres criterios distintos:**

| Dónde | Máximo | Origen |
|---|---|---|
| Navegador, ventana de finalización (monitoreo) | **Peso tamizado** (parte entera). Es el que ve el usuario | `monitoreo.js:598-601`, `validators.js:320` |
| Navegador, página de análisis (al ingresar el peso después) | **Peso trillado**. Texto: "Gramos enteros. Máximo: {N} g (peso trillado)." | `analisis.js:63-68` |
| Servidor (`completar_evaluacion`) | **Peso trillado**. Mensaje: "El peso de grano bueno ({peso} g) no puede superar el peso trillado ({trillado} g)." | `evaluacion_service.py:160-164` |

Como el tamizado nunca supera al trillado, en la ventana de finalización manda el tamizado y el mensaje
del servidor no llega a verse. Un valor entre tamizado y trillado se rechaza en la ventana de
finalización pero se acepta en la página de análisis. **Es una regla de negocio: el responsable debe
decidir cuál es el máximo correcto** antes de escribirlo en el manual.

Mensajes exactos (rojo bajo el campo, `monitoreo.html:230`; comprobados en la aplicación):

| Caso | Mensaje | Origen |
|---|---|---|
| Mayor al máximo (tamizado 240 g, se escribe 250) | "El peso no puede superar el máximo permitido (240 g)." | `validators.js:320` |
| Con decimales (120.5) | "El peso debe ser un número entero (gramos, sin decimales)." | `validators.js:318` |
| Vacío | "Ingresa el peso de grano bueno." | `validators.js:317` |
| Negativo | "El peso no puede ser negativo." | `validators.js:319` |
| 0 | El navegador y el servidor lo aceptan (`validators.js:319`, `schemas/evaluacion.py:94`). El factor sale 0.00 y, si ningún rango de precio lo contiene, aparece el mensaje de la fila siguiente con "(0.00)" | — |
| Factor sin rango de precio hoy | "No hay precio de café registrado hoy para el rango del factor de rendimiento ({factor}). Registra ese rango en 'Valor de café'." | `evaluacion_service.py:175-178` |
| Evaluación ya completada | "La evaluación ya fue completada; su pago no se puede recalcular." | `evaluacion_service.py:144` |
| Otra falla | "No se pudo calcular el rendimiento." o "No se pudo procesar la solicitud." | `monitoreo.js:637`, `routes/evaluacion.py:129` |

Pulsar Enter en el campo equivale a **Calcular rendimiento** (`monitoreo.js:660-662`).

### C.3 "Peso capturado (báscula)"

Es código de la antigua celda de carga, **inactivo con el hardware actual**. El firmware ya no envía el
peso (báscula HX711 retirada, `arduino/logica_hardware/logica_hardware.ino:90`; pendiente C de
`docs/guia/04-pendientes.md`). La página sigue pidiendo el peso (`monitoreo.js:707-717`), recibe vacío
y oculta la fila "Peso capturado (báscula)" cuando el valor es 0 (`monitoreo.js:580`). Lo único que
queda visible es el texto pasajero "Calculando resumen... Peso capturado: 0.00 g" durante el paso 2.

### C.4 Botones

| Botón (texto exacto) | Qué hace |
|---|---|
| **Calcular rendimiento** (`monitoreo.html:227`) | Valida el peso (C.2) y pide al servidor el cálculo. Mientras espera dice "Calculando...". Si sale bien: oculta el campo, muestra **Factor rendimiento** y **Pago (S/)**, cambia el texto a "Rendimiento calculado. Revisa el resumen antes de continuar al análisis." y activa **Ir al análisis →** (`monitoreo.js:640-646`). Si el servidor rechaza: muestra el motivo en rojo, deja el botón disponible para reintentar y activa **Continuar sin rendimiento →** |
| **Continuar sin rendimiento →** (`monitoreo.js:655`) | **Solo aparece después de que el servidor rechazó el cálculo** (por ejemplo, factor sin rango de precio). No está disponible si el campo está vacío o con un valor que el navegador rechaza. Abre `/analisis/{id}`; la evaluación ya tiene código y el peso se ingresa ahí después |
| **Ir al análisis →** (`monitoreo.js:611`) | Abre `/analisis/{id}` con el resultado (`monitoreo.js:683-689`) |

Mientras no hay peso calculado, el botón inferior dice "Registra el peso bueno para continuar" y está
desactivado.

---

## D. Capturas

### D.1 Generadas con Playwright

Carpeta `docs/manuales/img/usuario/`. Usuario de prueba `pcn_operario` (Evaluador), base de desarrollo,
ventana 1366 × 900, tema claro.

| Archivo | Qué muestra | Simulación |
|---|---|---|
| `registro-vacio.png` | Formulario sin datos; Tipo documento con DNI ya elegido | Precios de hoy simulados (la base de desarrollo no tenía precios del 2026-10-29); sin ella la ventana de precios tapa el formulario |
| `registro-completo.png` | Formulario válido: caficultor 99988877 encontrado, 5 sacos, 300 kg, humedad 12, muestra 300 g, trillado 240, tamiz N° 15, tamizado 230, con los textos "Máximo: …" | Precios simulados |
| `registro-error-peso-total.png` | Ventana "El peso total no puede superar 350 kg (5 sacos × 70 kg)." (400 kg con 5 sacos) | Precios simulados |
| `registro-error-trillado.png` | Ventana "El peso trillado no puede superar el 83% del peso de muestra." (260 g con muestra de 300 g) | Precios simulados |
| `registro-error-tamizado.png` | Ventana "El peso tamizado no puede ser mayor al peso trillado." (245 con trillado 240) | Precios simulados |
| `registro-caficultor-no-encontrado.png` | Mensaje rojo de caficultor inexistente con el enlace **Registrar caficultor** (DNI 12345670) | Precios simulados |
| `registro-sin-precios.png` | Ventana **Precios de café pendientes**, variante Evaluador | Ninguna: es el estado real de la base |
| `registro-sensor-sin-arduino.png` | Captura adicional para A.4: ventana "Arduino no conectado (COM5). Verifique el cable USB." | Precios simulados; la respuesta del Arduino es real (no estaba conectado) |
| `finalizacion-error-peso-bueno.png` | Ventana de finalización con los tres pasos hechos, código EVA0000021, 222 granos y el error "El peso no puede superar el máximo permitido (240 g)." | Se simularon cámara, conteo (222 granos: 42 defectos, 180 buenos), eventos, Arduino y reporte del lote. La finalización fue real: asignó el código **EVA0000021** a una evaluación de prueba de `pcn_operario` que estaba abierta en la base de desarrollo (`01a185f7-2c2b-71eb-95ed-8568f4dc2939`) |

Las capturas con ventana de error tapan con desenfoque el texto rojo bajo el campo; ese texto está en la
tabla A.2. Si el manual necesita mostrar el aviso bajo el campo, hay que tomar otra captura sin pulsar el
botón.

### D.2 Capturas que debe tomar el responsable (requieren el prototipo)

Tomarlas con la cámara ELP, el Arduino conectado y precios de café registrados hoy.

| Archivo | Qué debe verse |
|---|---|
| `monitoreo-arranque.png` | Primeros segundos del lote: registro con "Iniciando sistema...", "Cargando modelo y conectando cámara...", "Esperando primer frame de la cámara...", "Cámara activa. Arrancando faja transportadora...", "Faja iniciada.", "Faja en marcha. Captura YOLO activa." y "Monitoreo iniciado — modelo yolov26n_2cls."; indicadores en verde |
| `monitoreo-en-curso.png` | Video con granos enmarcados, contadores con valores, barras de distribución, cronómetro corriendo, indicadores Cámara "en vivo", Faja "en marcha", Arduino "conectado", Modelo "yolov26n_2cls", y "Primer grano detectado. Conteo en marcha." en el registro. Si es posible, con un objeto extraño (recuadro azul, tarjeta **Objetos extraños** y su miniatura en el registro) |
| `monitoreo-tapa-abierta.png` | Registro con "Tapa abierta — se registrará como incidencia." y, tras cerrarla, "Tapa cerrada — estuvo abierta {N}s." |
| `monitoreo-sin-granos.png` | "Sin granos hace 10 s — si el lote terminó, presione Finalizar monitoreo." en el registro y el botón **Finalizar monitoreo** resaltado |
| `monitoreo-camara-desconectada.png` | Tras desconectar el USB de la cámara: recuadro del video con "Desconexión con cámara. La clasificación se ha detenido.", indicador "Cámara: desconectada" en rojo, el mismo mensaje en el registro y el botón **Reintentar captura** |
| `finalizacion-pasos.png` | Ventana "Finalizando monitoreo..." con los pasos en curso (difícil de captar: dura pocos segundos; puede servir una grabación de pantalla) |
| `finalizacion-peso-bueno.png` | Ventana "Evaluación completada" después de pulsar **Calcular rendimiento** con un peso válido: **Factor rendimiento**, **Pago (S/)** y el botón **Ir al análisis →** activo |

---

## E. Diferencias entre el código y el manual actual

| # | Sección del manual | El manual dice | El código hace |
|---|---|---|---|
| 1 | 4.1.4 paso 3 y diccionario ("Peso de grano bueno") | No puede superar el peso tamizado | La ventana de finalización limita al tamizado; la página de análisis y el servidor, al trillado (C.2). Decisión pendiente del responsable |
| 2 | 4.1.4 | "Si en ese momento no tiene el peso, puede pulsar **Continuar sin rendimiento**" | Ese botón solo aparece después de que el servidor rechaza el cálculo (C.4). Sin peso, el evaluador no puede pasar al análisis desde la ventana |
| 3 | 4.1.4 paso 2 | Muestra el "peso capturado (báscula)" si la balanza envió datos | Con el firmware actual nunca se muestra (C.3) |
| 4 | 4.1.2 | Pulsar el botón guarda la evaluación y abre el monitoreo | Antes exige la tapa cerrada y el Arduino conectado (A.4). El manual no lo menciona |
| 5 | 4.1.2 paso 3 | "Al lado de cada peso se muestra el máximo permitido" | Se muestra debajo del campo y solo después de escribir un valor válido en ese campo |
| 6 | 4.1.2 paso 2 | "Si aparece **Caficultor no encontrado**" | El texto real es "No existe un caficultor con ese documento. Se recomienda registrarlo para continuar con el proceso." Un caficultor inactivo recibe el mismo mensaje |
| 7 | 4.1.3, tabla de zonas | "**En vivo** indica que la captura está activa" | **En vivo** es un rótulo fijo; se ve aunque la cámara esté desconectada |
| 8 | 4.1.3, primer párrafo | La página "carga el modelo" | El modelo se carga al arrancar el servidor; el mensaje "Cargando modelo y conectando cámara..." se mantiene, pero un fallo del modelo impide arrancar el servidor y no tiene mensaje en pantalla |
| 9 | 4.1.3 | Si la faja no arranca, el indicador de Arduino muestra sin conexión o sin respuesta | Si la faja no arranca, el registro dice "No se pudo iniciar la faja. Verifique la conexión Arduino." y el indicador **Faja** queda en "detenida"; aun así aparece "Faja en marcha. Captura YOLO activa." |
| 10 | 4.1.3 | Ante desconexión de cámara, revisar el cable y pulsar **Reintentar captura** | Correcto, pero el reintento reinicia el conteo del lote a 0 (B.4). El manual no lo advierte. Cómo debe actuar el evaluador en ese caso (reintentar o finalizar con lo contado) es una decisión de operación que el responsable debe definir |
| 11 | 4.1.3 | Volver a registro: "los datos de esa sesión no se guardan" | El conteo no se guarda, pero la muestra queda en la base como evaluación sin código |
| 12 | 4.1.3 paso 2 | Al cerrar la tapa se anota cuánto estuvo abierta | Si se pulsa **Finalizar monitoreo** con la tapa todavía abierta, esa apertura no se guarda como incidencia (solo se guarda al cerrarse, `monitoreo.js:417-421`) |
| 13 | 5 (Resumen del análisis) | El registro del monitoreo muestra los mensajes del sistema | Solo se guardan los mensajes del servidor; los de primer grano, tapa y 10 s sin granos no aparecen en el resumen (B.3) |
| 14 | 4.1.2 | (no lo menciona) | **Limpiar formulario** deja Tipo documento en "Seleccionar un tipo"; hay que volver a elegir DNI |

Observaciones del código que no contradicen el manual pero conviene conocer:

- Humedad 0 muestra "La humedad debe ser un número entero (sin decimales)." aunque 0 ya es entero.
- En la franja del monitoreo la etiqueta del documento siempre dice "DNI".
- Si falla el reporte del paso 2 y hubo defectos, el paso 3 envía un total de buenos negativo y el
  servidor lo rechaza con "total_buenos: debe ser mayor o igual a 0." (`monitoreo.js:730`, `:745`;
  `src/main.py:151-152`).
