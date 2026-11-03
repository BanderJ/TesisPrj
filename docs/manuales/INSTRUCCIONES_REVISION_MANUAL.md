# Revisión del Manual de Usuario contra el código

Instrucciones para Claude Code (VS Code). Revisa `D:\TesisPrj\docs\manuales\Manual_Usuario_CoffeeRen.docx` comparándolo con el código real del sistema (templates HTML, JS, rutas, services y schemas). El manual se escribió sin acceso al código, salvo las secciones 4.1.2 a 4.1.4 y 5.1, que salieron de `insumo_registro_monitoreo.md`.

## Reglas

- **No modificar** el `.docx` ni el código. Solo generar el informe.
- Leer el manual con python-docx o pandoc.
- Cada diferencia debe citar `archivo:línea`.
- Textos de botones, menús, títulos y mensajes se comparan **literal** (tildes, mayúsculas, puntos).
- Si algo del manual no se puede comprobar en el código, márcalo como "No verificable" y explica por qué.

## Qué revisar (todo el manual, sección por sección)

1. **Roles y permisos (1.1.1, 1.1.2, 3.2.1, 4.x).** Qué puede ver y hacer cada rol (Evaluador, Gerente, Administrador). Revisar:
   - si Gerente y Administrador tienen realmente el mismo acceso;
   - qué opciones del menú se ocultan;
   - qué rutas niegan el acceso.
2. **Acceso y sesión (2.x).**
   - Dirección y puerto.
   - Duración de la sesión (7 días).
   - Máximo de caracteres de usuario y contraseña (30).
   - Botón del ojo.
   - Texto de "¿Olvidó su contraseña?".
   - Requisitos de la nueva contraseña.
   - Ruta y botones de la Prueba de detección (`/test`).
3. **Pantalla principal y navegación (3.x).** Nombres exactos de:
   - indicadores, paneles y pestañas (Hoy, Este mes, Este año);
   - elementos de la barra superior, del menú del usuario y del pie de página;
   - textos de Términos y condiciones.
4. **Registro de caficultor y conversión a socio (4.1.1, 4.2.1, 4.3.1).**
   - Campos, reglas y largos máximos.
   - Comportamiento con RENIEC.
   - Mensajes y casilla de confirmación.
   - Qué pasa con un caficultor ya registrado.
5. **Valor de café (4.1.5, 4.2.3, 4.3.3, 4.4).**
   - Formatos de rango válidos e inválidos. Revisar si un número único como "70" es válido.
   - Reglas de solapamiento y de precio no decreciente.
   - Botones y nombres de los paneles.
   - Si los mensajes de solapamiento y de precio decreciente se ven así en pantalla (están resaltados en amarillo en 5.1).
6. **Usuarios, tipos de grano y cooperativa (4.1.6, 4.1.7, 4.3.2, 4.3.4, 4.3.5, 4.4).**
   - Cómo se genera el nombre de usuario.
   - Campos editables y de solo lectura.
   - Límites de la imagen del banner (formatos y tamaño).
   - Beneficio de socio.
   - Activar o desactivar usuarios.
   - Eliminar tipos de grano.
7. **Reportes (4.5.x).**
   - Secciones del Resumen del análisis.
   - Formato de búsqueda del código EVA (7 dígitos, sin ceros a la izquierda).
   - Exportar PDF y Excel.
   - Filtros y paginación de la auditoría (10, 30 o 50).
   - Catálogo de reportes estadísticos.
8. **Errores y soporte (5.1, 5.2).** Revisar que cada mensaje y cada causa de la tabla de problemas correspondan al código.
9. **Cálculo del pago (6.2).**
   - Comparar cada fórmula con `evaluacion_service.py`: tara redondeada, descuento por humedad solo si pasa de 12 %, quintales truncados a 2 decimales y beneficio de socio.
   - Recalcular los dos ejemplos (humedad 13 % y 11 %) con la lógica real.
10. **Peso de grano bueno.** Confirmar que la ventana de finalización, la página de análisis y el servidor usan todos el **peso tamizado** como máximo. Es la regla decidida; si alguno todavía usa el trillado, indicarlo.
11. **Información que falta.** Indicar funciones o pantallas que existen en el sistema y el manual no menciona, o que menciona y ya no existen.
12. **Imágenes pendientes.** Comprobar que los nombres de archivo de los recuadros IMAGEN PENDIENTE correspondan a pantallas que existen.

## Salida

Crea `D:\TesisPrj\docs\manuales\revision_manual_vs_codigo.md` con:

1. **Resumen.** Cuántas diferencias encontraste, cuántas son graves (el manual dice algo falso) y cuántas menores (un texto o una tilde).
2. **Tabla de diferencias:** Sección del manual | El manual dice | El código hace | `archivo:línea` | Texto propuesto para el manual | Gravedad (Grave / Menor).
3. **Puntos no verificables**, con el motivo.
4. **Funciones no documentadas**, si las hay.
5. **Decisiones** que debe tomar el responsable, porque son reglas de negocio y no errores del manual.
