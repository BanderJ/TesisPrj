# Capturas pendientes del Manual de Usuario

Instrucciones para Claude Code (VS Code). Toma con Playwright las capturas que no necesitan el prototipo. Guárdalas en `D:\TesisPrj\docs\manuales\img\usuario\` con el nombre exacto de la lista.

## Reglas

- No modificar el código ni el manual `.docx`.
- Usar la base de datos de desarrollo, con la ventana a 1366 × 900 y el tema claro.
- Si una pantalla necesita datos (precios del día, una evaluación completada, usuarios), crearlos solo en la base de desarrollo y anotarlo.
- No mostrar contraseñas reales en ninguna captura.
- Si algo bloquea una pantalla (precios del día, sensor de la tapa), simúlalo como en las capturas anteriores y anótalo.

## Capturas

| Archivo | Usuario | Qué debe verse |
|---|---|---|
| `perfil-seguridad.png` | Cualquiera | Perfil, sección Seguridad, con la nueva contraseña a medio escribir y los requisitos marcados o sin marcar |
| `inicio-precios.png` | Gerente | Página de inicio: panel Precio del café según rendimiento con el gráfico y accesos del Flujo operativo |
| `caficultor-nuevo-registro.png` | Evaluador | Registrar caficultor, Nuevo Registro, con los datos completados (usar un DNI de prueba, no el de una persona real) |
| `valor-cafe-registro.png` | Gerente | Valor de café con 2 o 3 rangos escritos antes de pulsar Registrar Bloque |
| `usuario-crear.png` | Administrador | Cooperativa, Gestión de usuarios, ventana Agregar usuario con datos de prueba |
| `caficultor-conversion-socio.png` | Evaluador | Conversión a Socio con un caficultor externo encontrado y el botón Convertir a Socio habilitado |
| `cooperativa-informacion.png` | Gerente | Configuración de la cooperativa, sección Información básica |
| `analisis-resumen.png` | Evaluador | Resumen del análisis de una evaluación completada con factor de rendimiento y pago (puede ser EVA0000021 si ya tiene peso) |
| `buscar-reporte.png` | Evaluador | Buscar reportes con un código encontrado y el resumen visible |
| `cooperativa-auditoria.png` | Administrador | Auditoría con un filtro aplicado y la tabla con registros |

## Al terminar

Indica qué capturas se tomaron, qué datos de prueba creaste y qué simulaste.

Estas capturas las toma el responsable con el prototipo, no tú: `prueba-deteccion.png`, `monitoreo-en-curso.png`, `monitoreo-camara-desconectada.png`, `finalizacion-peso-bueno.png`.
