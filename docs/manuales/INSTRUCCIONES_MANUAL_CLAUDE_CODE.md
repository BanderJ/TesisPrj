# Insumo para el Manual de Usuario: registro de muestra y monitoreo

Instrucciones para Claude Code (VS Code). Tienes acceso al código de CoffeeRen. Extrae del código y de la aplicación en ejecución todo lo que ve y hace el usuario en tres pantallas: **Registro de muestra**, **Monitoreo** y **Finalización** (ventana del peso de grano bueno). Con eso se ampliarán las secciones 4.1.2, 4.1.3, 4.1.4 y 5.1 del manual `Manual_Usuario_CoffeeRen.docx`.

## Reglas

1. **No modificar** el código del sistema ni el manual `.docx`. Solo generar el archivo de insumo y las capturas.
2. **No inventar.** Cada texto de pantalla, botón o mensaje se copia **literal** del código (HTML, JS o Python), con su ubicación como referencia (`archivo:línea`).
3. **Lenguaje del usuario.** Si una regla existe solo en el backend y el usuario nunca la ve como mensaje en pantalla, indícalo.
4. **Base de datos.** Usar la BD de desarrollo para las capturas.

## Salida

1. `D:\TesisPrj\docs\manuales\insumo_registro_monitoreo.md`, con las secciones A, B, C y D de abajo.
2. Capturas en `D:\TesisPrj\docs\manuales\img\usuario\`, con los nombres indicados.

## A. Registro de muestra

1. **Tabla de campos** con estas columnas: etiqueta exacta | tipo de control (texto, número, lista) | unidad | valor por defecto o placeholder | texto de ayuda visible (por ejemplo, el "máximo permitido" al lado de los pesos) | regla en el navegador | regla en el servidor.
2. **Tabla de errores** con estas columnas: campo | dato incorrecto de ejemplo | mensaje exacto bajo el campo | mensaje exacto en ventana o alerta | en qué momento aparece (al escribir, al salir del campo o al enviar).
   - Incluir como mínimo:
     - peso total igual a 0 o negativo, y mayor que sacos × 70 kg o menor que la tara;
     - peso trillado ≤ 0, mayor o igual al peso de muestra, y mayor al 83 %;
     - peso tamizado mayor al trillado;
     - humedad fuera de 1–100 o con decimales;
     - sacos igual a 0;
     - documento con longitud inválida;
     - caficultor no encontrado;
     - caficultor inactivo;
     - sin precios del día.
3. **Búsqueda del caficultor:** cómo se dispara y qué mensajes muestra en cada caso.
4. **Sensor de la tapa:** si el registro exige que la tapa esté cerrada (en las pruebas de caja negra hubo que simular `GET /arduino/estado` = tapa cerrada para enviar el formulario), indicar:
   - qué ve el usuario si la tapa está abierta o el Arduino no responde;
   - el mensaje exacto;
   - qué debe hacer.
5. **Botones:** "Iniciar clasificación y monitoreo" y "Limpiar formulario" (texto exacto), qué hace cada uno y si piden confirmación.

## B. Monitoreo

1. **Secuencia de arranque:** cada mensaje del "Registro del monitoreo", en orden y literal.
2. **Indicadores de Cámara, Faja, Arduino y Modelo:** todos los estados posibles de cada uno (texto y color) y qué significan.
3. **Tabla de mensajes del registro del monitoreo** con estas columnas: mensaje literal | cuándo aparece | qué debe hacer el evaluador. Incluir:
   - primer grano detectado;
   - tapa abierta y tapa cerrada (con su duración);
   - 10 s sin granos;
   - objeto extraño;
   - cierre de otro monitoreo abierto;
   - cámara desconectada y reintento;
   - Arduino sin conexión o sin respuesta;
   - error al cargar el modelo;
   - cualquier otro mensaje que exista en el código.
4. **Botones:** Finalizar monitoreo, Reintentar captura y Volver a registro. Para cada uno, el texto exacto de su ventana de confirmación y qué pasa con los datos.
5. **Zonas de la pantalla:** qué muestra cada contador o barra. Confirmar si "Objetos extraños" sigue existiendo con el modelo actual de 2 clases.

## C. Finalización y peso de grano bueno

1. **Los tres pasos de la ventana de finalización** (texto literal) y qué pasa si uno falla.
2. **Campo "Peso de grano bueno (g)":**
   - Regla exacta: aclarar si el máximo es el **peso tamizado** o el **peso trillado**. El manual dice tamizado, pero el backend (`completar_evaluacion`) compara con el trillado. Indicar qué valida el navegador, qué valida el servidor y cuál es el máximo que ve el usuario.
   - Mensajes exactos para: valor mayor al máximo, decimales, vacío o 0, y factor sin rango de precio.
3. **"Peso capturado (báscula)":** indicar si esta función sigue existiendo o si es código de la antigua celda de carga.
4. **Botones** "Calcular rendimiento", "Continuar sin rendimiento" e "Ir al análisis": qué hace cada uno.

## D. Capturas

### Con Playwright (no necesitan el prototipo)

Guardar en `img\usuario\`. Si la tapa o el Arduino bloquean el formulario, simular la respuesta del sensor, como en caja negra, y anotarlo.

- `registro-vacio.png`: formulario sin datos.
- `registro-completo.png`: formulario completo y válido.
- `registro-error-peso-total.png`
- `registro-error-trillado.png`: trillado mayor al 83 %.
- `registro-error-tamizado.png`: tamizado mayor al trillado.
- `registro-caficultor-no-encontrado.png`
- `registro-sin-precios.png`
- `finalizacion-error-peso-bueno.png`: si se puede abrir sin el prototipo; si no, pasa a la lista manual.

### Manuales (requieren el prototipo)

Incluir al final del insumo una **lista de capturas que debe tomar el responsable**, con nombre de archivo y qué debe verse en cada una:

- `monitoreo-arranque.png`
- `monitoreo-en-curso.png`
- `monitoreo-tapa-abierta.png`
- `monitoreo-sin-granos.png`
- `monitoreo-camara-desconectada.png`
- `finalizacion-pasos.png`
- `finalizacion-peso-bueno.png`

## Al terminar

Informa al responsable:

- dónde quedó el insumo;
- qué capturas se generaron;
- qué capturas faltan, para tomarlas a mano;
- cualquier diferencia entre el código y lo que dice el manual actual.
