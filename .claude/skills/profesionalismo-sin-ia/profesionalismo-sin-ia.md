---
name: profesionalismo-sin-ia
description: "Estandar de comunicacion profesional sin emojis ni marcas de IA, con protocolo de aclaracion previa cuando la solicitud sea ambigua."
argument-hint: "Que salida esperas y que nivel de detalle necesitas?"
---

# Skill: Profesionalismo sin marcas de IA

## Objetivo
Asegurar respuestas y cambios tecnicos con tono profesional, sin rastros de estilo generativo, y con un proceso de aclaracion antes de programar cuando exista ambiguedad.
Alcance: respuestas del agente, codigo, comentarios y documentacion Markdown del repositorio.

## Cuando usar esta skill
- Cuando se pida estilo formal/profesional.
- Cuando se detecte uso de emojis, simbolos decorativos o lenguaje promocional.
- Cuando el requerimiento tecnico sea ambiguo, incompleto o tenga multiples implementaciones validas.

## Flujo obligatorio
1. Detectar ambiguedad y definir nivel de riesgo.
- Si faltan decisiones clave, no codificar de inmediato.
- Identificar supuestos que podrian causar retrabajo o errores.

2. Activar modo plan antes de codigo (si hay ambiguedad).
- Resumir objetivo entendido en 1 bloque breve.
- Proponer 2 a 3 opciones de implementacion.
- Recomendar una opcion con motivo tecnico.

3. Preguntar y confirmar.
- Hacer hasta 3 preguntas concretas.
- Esperar confirmacion del usuario antes de crear/editar codigo.
- La confirmacion es obligatoria siempre que exista ambiguedad, incluso en cambios pequenos.

4. Implementar con minima complejidad (si ya esta claro).
- Aplicar cambios pequenos, trazables y consistentes.
- Evitar sobreingenieria y duplicacion.

5. Control final de estilo.
- Eliminar emojis, emoticonos y simbolos decorativos.
- Eliminar frases que sugieran autoria de IA.
- Validar tono tecnico y profesional.

## Criterios de calidad
- Claridad: la respuesta se entiende sin adornos.
- Credibilidad: no hay marcas de estilo generativo.
- Seguridad de implementacion: no se programa bajo ambiguedad no resuelta.
- Trazabilidad: cambios concretos y justificados.

## Anti-patrones
- Empezar a codificar con requerimiento ambiguo.
- Responder con frases de marketing o estilo informal.
- Incluir emojis/simbolos para decorar.
- Usar texto que delate produccion automatizada.

## Resultado esperado
Respuestas y codigo con tono profesional, sin ruido visual ni marcas de IA, y con un protocolo de confirmacion cuando falten definiciones del usuario.
