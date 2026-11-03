---
name: documentacion-informes
description: 'Crear y actualizar documentacion de avances tecnicos e informes del proyecto leyendo archivos primero, aclarando dudas, y solicitando permiso antes de modificar. Consulta referencias en docs/documentacion/.'
argument-hint: '[archivo] [seccion] [instruccion]'
---

# Documentacion de Avances e Informes — Versión Mejorada

## Objetivo
Crear y actualizar documentacion del proyecto de forma rigurosa: leyendo todo antes de actuar, preguntando ante dudas, planificando cambios, y pidiendo permiso explícito antes de modificar archivos existentes.

## Cuando usar esta skill
- Cuando el usuario diga "documenta lo realizado".
- Cuando el usuario escriba "documentar informe".
- Cuando pida "crear informe", "actualizar avance", "completar reporte" o "mejorar documento".
- Cuando indique un archivo existente en docs/ y una seccion para actualizar.
- Cuando quiera mejorar documentacion existente con contenido nuevo.

## Flujo obligatorio (SIN EXCEPCIONES)

### FASE 1: LECTURA Y COMPRENSIÓN
1. **Leer TODOS los archivos relevantes antes de cualquier acción**.
   - Si el usuario especifica archivo: leer ese archivo completo.
   - Si el usuario no especifica: leer `docs/registro-avances.md` (destino por defecto).
   - Leer archivos de referencia en `docs/documentacion/` relevantes al tema.
   - NUNCA asumir el contenido: leer primero.

2. **Comprender exactamente qué se ha hecho y qué se va a hacer**.
   - Analizar el estado actual del archivo.
   - Entender la estructura existente (secciones, formato, historial).
   - Identificar qué información falta o necesita mejora.

3. **Si hay ambigüedad o dudas: PREGUNTAR antes de continuar**.
   - No asumir interpretaciones.
   - Aclarar con el usuario qué exactamente quiere.
   - Ejemplos: "¿Debo agregar esto como nueva sección o actualizar la existente?", "¿Este cambio es adición o reemplazo?"

### FASE 2: PLANIFICACIÓN
4. **Usar EnterPlanMode si la modificación es no-trivial**.
   - Para cambios complejos que afecten múltiples secciones.
   - Para mejoras significativas de contenido existente.
   - Para actualizaciones que reorganicen la estructura.
   - Presentar el plan al usuario antes de ejecutar.

5. **Si el archivo ya tiene información y vas a mejorarlo**:
   - Leer la información existente completamente.
   - Identificar qué se mejorará y dónde.
   - Explicar al usuario: "Voy a [acción específica]. Esto [resultado esperado]. ¿De acuerdo?"
   - ESPERAR CONFIRMACIÓN antes de modificar.

### FASE 3: EJECUCIÓN (después de aprobación)
6. **Levantar evidencia real del trabajo** (si es aplicable).
   - Listar cambios técnicos concretos.
   - Incluir archivos modificados.
   - Incluir estado de validación (hecho, parcial, pendiente).

7. **Redactar con formato consistente**.
   - Usar plantilla base de [plantilla-informe](./assets/plantilla-informe.md).
   - Mantener terminología consistente con docs/documentacion/.
   - Respetar exactamente la sección y ubicación solicitadas.

8. **Control de calidad antes de guardar**.
   - Fecha incluida (si aplica).
   - Objetivo del bloque claro.
   - Cambios concretos y verificables.
   - Archivos impactados mencionados.
   - Pendientes y próximo paso registrados.
   - No sobrescribir secciones no solicitadas.

## Reglas no negociables
- **No inventar información**: si no sabes, pregunta.
- **No asumir estructura**: lee primero el archivo existente.
- **No modificar sin permiso**: si hay cambios significativos, pide aprobación explícita.
- **No eliminar información útil**: al actualizar, preservar historial y contexto.
- **Plan mode obligatorio**: para cambios que reorganicen o mejoren significativamente.
- **Respetar exactitud**: si el usuario dice "sección X", actualiza solo esa sección.

## Estructura recomendada del informe
1. Contexto
2. Trabajo realizado
3. Archivos impactados
4. Metricas
5. Validacion
6. Pendientes
7. Proximo paso

## Fuentes de referencia
- **docs/documentacion/** → Carpeta con documentos MD convertidos de Word. Leer para contexto, especificaciones técnicas y consistencia terminológica.
- **docs/registro-avances.md** → Archivo por defecto para documentar avances.

## Entradas esperadas del usuario
- Documento objetivo (opcional): ej. docs/informe-semanal.md
- Seccion objetivo (opcional): ej. "Trabajo realizado"
- Contenido o instrucción de mejora: ej. "agrega esto en Pendientes"
- Permiso explícito: "sí, hazlo" o similar, después de ver el plan.

## Resultado esperado
Documentacion actualizada o creada de forma rigurosa: planificada, consultada con el usuario, respaldada en información existente, y lista para reportes técnicos confiables.
