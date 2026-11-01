# Cambios de código decididos por el responsable

Instrucciones para Claude Code (VS Code). Salen de `revision_manual_vs_codigo.md` y de las decisiones del responsable. El manual de usuario **ya se actualizó** con estas reglas: el código debe quedar igual a lo que dice el manual.

## Reglas

- Trabajar en la rama `temporal`.
- No tocar `servo_controller.py`, `arduino_serial.py` ni los parámetros calibrados.
- Después de cada cambio, ejecutar las pruebas existentes (`tests/caja_negra`, `tests/caja_blanca`) y corregir las que se rompan por el cambio de texto o de regla. Nunca debilitar una prueba para que pase.
- Al final, informar cada cambio con `archivo:línea`.

## 1. Máximo del peso de grano bueno = peso tamizado

- `src/static/js/analisis.js:63-68` y `src/services/evaluacion_service.py:160-164` deben usar el **peso tamizado**, igual que la ventana de finalización (`monitoreo.js:598-601`).
- Texto de ayuda en análisis: "Gramos enteros. Máximo: {N} g (peso tamizado)."
- Mensaje del servidor: "El peso de grano bueno ({peso} g) no puede superar el peso tamizado ({tamizado} g)."

## 2. Ingresar el peso después de "Continuar sin rendimiento"

- En **Buscar reportes**, si la evaluación encontrada no tiene factor de rendimiento, mostrar un botón **Calcular rendimiento** que abra `/analisis/{id}`.
- Reemplazar el texto actual que dice que el rendimiento se calcula desde la página de análisis.
- Comprobar que `/analisis/{id}` permite ingresar el peso de una evaluación ya finalizada que todavía no tiene peso.

## 3. Precio según la parte entera del factor de rendimiento

- Regla: un rango X-Y incluye todos los factores cuya **parte entera** está entre X e Y. Así, 60-65 cubre de 60.00 a 65.99, y "70" cubre de 70.00 a 70.99. Por ejemplo, 65.50 usa el precio de 60-65.
- Ajustar la búsqueda del precio (`src/models/valor_cafe.py:82-91`, `obtener_por_factor`, y donde se llame en `evaluacion_service.py:168-178`) para comparar `floor(factor)`.
- El factor que se guarda y se muestra sigue con sus 2 decimales; el mensaje de "sin rango" muestra el factor real.
- Las reglas de los rangos no cambian: enteros, sin solapamiento y precio no decreciente.

## 4. Nombre de usuario: una sola letra del apellido materno

- Servidor (`src/services/perfil_service.py:121-126`): inicial del nombre + apellido paterno + **inicial** del apellido materno, en minúsculas. Por ejemplo, Juan Cueva Pérez → `jcuevap`.
- Aplicar exactamente la misma limpieza que la vista previa de `cooperativa.js:593-601` (tildes, espacios, ñ), para que lo que se ve sea lo que se crea.
- En el aviso final de creación, mostrar el usuario creado.

## 5. Humedad máxima: 30 %

- Schema (`src/schemas/evaluacion.py:11`): entero de 1 a 30.
- Navegador (`registro.js` y validadores):
  - máximo 30;
  - mensaje bajo el campo: "La humedad no puede superar 30%.";
  - mensaje en la ventana: "La humedad no puede superar 30%.".
- Si el campo tiene el atributo `max`, ponerlo en 30.

## 6. Tildes en rótulos de la interfaz

Corregir **solo** estos rótulos visibles:

- "Precio minimo hoy" → "Precio mínimo hoy" (`inicio.html:94`).
- "Numero de documento" → "Número de documento", "Telefono" → "Teléfono" y "Conversion a Socio" → "Conversión a Socio" (`caficultor.html:26`, `:49`, `:84`, `:171`).
- "Gestión tipos de grano" → "Gestión de tipos de grano" (menú lateral, `cooperativa.html:31`).
- Botón "Iniciar clasificacion y monitoreo" → "Iniciar clasificación y monitoreo" (`registro.html:123`).

Actualizar los selectores de las pruebas de Playwright que usen esos textos.

## 7. Pruebas de caja blanca afectadas

- **PCB-05:**
  - El camino C2 ahora compara con el **tamizado**: usar peso tamizado = 230 g, peso bueno = 235 g, y el mensaje nuevo.
  - Agregar el camino **C4**: factor con decimales dentro de un rango. Con muestra de 300 g, peso bueno de 197 g y rangos 60-65 y 66-70, el FR es 65.67 y debe usar el precio de 60-65.
- **PCB-03:** agregar el límite de humedad (31 rechazado, 30 aceptado) si el validador está en la misma función. Si está en un Field, documentarlo como en C2.
- Volver a ejecutar las pruebas, regenerar sus evidencias y actualizar `Casos_Prueba_Caja_Blanca.xlsx`, `resultados.json` y `Pruebas_Caja_Blanca_CoffeeRen.docx` (carpeta `D:\Ciclo 10\Tesis1\Documentacion\Pruebas\CajaBlanca`). Mantener la portada y la guía del inicio del Word.
- Si una prueba de caja negra cambia de resultado, avisar sin modificarla.

## No incluido (pendiente de decisión del responsable)

- Eliminación física de tipos de grano.
- Enlace de WhatsApp del pie de página.
- Acceso de Evaluadores a `GET /caficultor/listar`.
- Crear usuarios para personas ya registradas.
