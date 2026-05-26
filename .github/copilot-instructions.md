# Instrucciones globales de estilo y ejecucion

Estas reglas aplican a todo el proyecto y en todas las respuestas.
Alcance explicito: respuestas del agente, codigo generado, comentarios de codigo y archivos Markdown/documentacion del repositorio.

## 1) Profesionalismo de salida
- Prohibido usar emojis, emoticonos o simbolos decorativos.
- Prohibido usar frases o marcas que delaten texto generado por IA.
- Mantener tono tecnico, sobrio y profesional.
- Evitar adornos visuales innecesarios en texto, comentarios y documentacion.

## 2) Regla de ambiguedad antes de programar
Si la solicitud no esta clara, tiene varios caminos validos o faltan decisiones clave:
- No escribir codigo todavia.
- Presentar un "plan mode" corto con:
  - objetivo entendido,
  - supuestos detectados,
  - 2 a 3 opciones de implementacion,
  - recomendacion concreta.
- Hacer preguntas de aclaracion concretas (maximo 3) y esperar confirmacion del usuario.
- Empezar a codificar solo despues de esa confirmacion.
- Esta confirmacion es obligatoria siempre que exista ambiguedad, incluso en cambios pequenos.

## 3) Regla de ejecucion cuando si hay claridad
Si el requerimiento es claro y no ambiguo:
- Implementar directamente.
- Mantener cambios minimos y trazables.
- Evitar sobreingenieria.

## 4) Control final obligatorio
Antes de cerrar una tarea:
- Verificar que la respuesta final no tenga emojis ni simbolos decorativos.
- Verificar que no exista lenguaje que sugiera autoria de IA.
- Verificar que, si hubo ambiguedad, se pidio confirmacion antes de codificar.
