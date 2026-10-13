# 05 — Historial de cambios importantes

> Cronología resumida a partir de los commits de Git (rama `temporal`). Sirve para saber
> **cuándo y por qué** cambió algo sin tener que leer todo el `git log`. El detalle de cada
> problema está en [docs/incidencias/incidencia_proyecto.md](../incidencias/incidencia_proyecto.md)
> y la bitácora narrativa en [docs/registro-avances.md](../registro-avances.md).
> Agregar una entrada por cada cambio relevante, la más reciente al final.

## Marzo – abril 2026: base de la aplicación

| Fecha | Commit | Cambio |
|---|---|---|
| 03-18 | `789c1ec`, `44a51ea` | Repositorio inicial, login, TailwindCSS y plantillas base. |
| 04-06 | `4cafe53` | Autenticación JWT en cookie y plantillas. |
| 04-10 | `b412f1f` | Reestructuración a `src/` con capa de servicios (patrón de 4 capas). |
| 04-15 / 04-21 | `e036a73`, `7a1f10e` | Módulo de caficultores (API, modelos, BD). |
| 04-27 | `e4de58c` | Módulo Valor del Café (precios por rango). |

## Mayo 2026: evaluación, cámara e integración ML

| Fecha | Commit | Cambio |
|---|---|---|
| 05-04 | `2fe6b2a` | API de ubigeo y consulta de DNI (RENIEC/Factiliza). |
| 05-12 | `9e390ed` | API de evaluación, esquema de BD y primer firmware Arduino. |
| 05-15 | `b16084d` | Transmisión de cámara y guardas de estado monitoreo/análisis. |
| 05-26 | `1338ea6` … `fe26f53` | Integración completa ML + backend: `tracker_service`, rutas `/video`, streaming MJPEG corregido, cámara simulada, mapeo de clases corregido (`broca_ligero` ↔ `broca_severo`). |
| 05-27 | `6741e58` | Constantes por modelo (`models/{modelo}/constants.py`) cargadas dinámicamente. |

## Junio 2026: modelo binario, IDs globales, auditoría

| Fecha | Commit | Cambio |
|---|---|---|
| 06-01 | `cdbce98`, `927ccae` | Conexión UTF-8, soporte de nuevos pesos, KPIs de inicio. |
| 06-03 | `fcd4dbe` | Servicio Arduino y documentos técnicos. |
| 06-11 | `240f5a4` | Warmup de YOLO y mejor manejo del hardware. |
| 06-15 | `0c06b79` | Tracker: preferencia por ONNX, **IDs globales que no retroceden**, cascada de defectos (luego retirada). |
| 06-27 | `00ded44` | Sistema de auditoría (`AUDITORIA`). |

## Julio 2026: configuración, servo y simplificación del ML

| Fecha | Commit | Cambio |
|---|---|---|
| 07-04 | `dcf68a8` | `config.py` con `.env`, Arduino simplificado, calibración ML, se elimina `inference.py`. |
| 07-04 | `94d88b1`, `3b7df92`, `4198fca` | Reportes, cálculo de rendimiento y precio por factor de rendimiento. |
| 07-08 | `787a7ac` | **Se retira el modelo cascada de 14 clases** y `USE_MODELO_DEFECTOS`; queda solo `yolov26n_2cls`. Fixes del servo: delay desde el timestamp de captura, hold extendido con defectos consecutivos, reintentos de comando, `SERVO_DELAY_S=0.5` en `.env`. |
| 07-11 | `199e023`, `33d8584` | Manuales de instalación y mantenimiento; `DOCUMENTACION_SISTEMA.md`. |

## Septiembre 2026: cámara, GPU, robustez y documentación

| Fecha | Commit | Cambio |
|---|---|---|
| 09-01 | — | Registro formal de incidencias (`docs/incidencias/incidencia_proyecto.md`). |
| 09-03 | `1553477` | Captura de cámara reforzada (MJPEG antes del primer `read()`, Media Foundation, selección por nombre de dispositivo) y página `/test`. |
| 09-06 | `c9b609f` | `src/config.py` sale de Git; se publica `src/config-example.py`. |
| 09-08 | `46f1452` | Eliminación de 13 endpoints sin consumidor (INC-59), mensajes de error unificados y `http.js` (INC-60), sesión invalidada al desactivar una cuenta (INC-61). |
| 09-16 | — | Investigación del *domain gap* celular vs ELP; `CAM_WB_TEMP` (balance de blancos fijo); notebook de fine-tuning v7 preparado. |
| 09-22 | `93cd39a` | **Migración de la inferencia a GPU** (`torch+cu130`, `best.pt`, FP16 condicional): CPU ~96 % → ~25 %. Tiles 3×3 en un batch, fusión consciente de costura, clase por confianza acumulada, objeto desconocido (materia extraña, equivalencia 1.0) con evidencia fotográfica, gate de movimiento y techo de FPS, tabla `EVENTO_MONITOREO` y bitácora del monitoreo, medidor de latencia (indicador ≤ 200 ms: p95 110 ms), permisos por rol en páginas, validaciones (documento 8–12, mayoría de edad, humedad entera, rangos de precio sin solape). |
| 09-22 | — | Corrección del parpadeo desconocido ↔ verde ↔ defecto (`_conf_max_historico`). |
| 09-29 | — | Tres ensayos nuevos de latencia (CSV en `docs/evidencias/`, sin analizar). |
| 09-30 | `4f38d55` | El peso bruto debe superar la tara de los sacos (`round(num_sacos × 0.25)`): evitaba peso neto ≤ 0 y pago negativo (caso EVA0000002). Ajustes de `test_motor_2.ino`. |
| 09-30 | — | Reorganización de la documentación: carpeta `docs/guia/`, manuales en `docs/manuales/`; eliminados por redundantes `INSTALACION.md`, `docs/documentacion/{avance-tecnico-completo-2026, arquitectura-sistema-clasificacion, registro-avances}.md`; `BACA CHUQUIMANCO_PROY.md` regenerado sin caracteres dañados; actualización de `readme.md` y documentos técnicos al estado real del código. `AGENTS.md` pasa a ser la fuente única de instrucciones para cualquier IA (en español); `CLAUDE.md` y `GEMINI.md` lo importan, `.github/copilot-instructions.md` remite a él; eliminado `.github/agents/fast-api-arquitecto.md`. `check_model.py` elige el peso igual que el tracker (GPU → `best.pt`) y verifica el orden de clases. |
| 10-06 | — | Motor de la faja nuevo: JGY370 12 V 10 RPM con driver L298N (ENA D5, IN1 D4, IN2 D3, sentido -1), validado con `test_motor_2.ino` y llevado a `logica_hardware.ino`. Velocidad máxima: `VELOCIDAD` y `FAJA_VELOCIDAD_PWM` pasan de 150 a 255. |
| 10-09 | — | Sistema de diseño del frontend: tokens de estado (`--success`, `--danger`, `--warning`, `--info`) y de movimiento (`--ease-out`, `--dur-*`) en `input.css`, que reemplazan los hex sueltos de las hojas de página; foco con `:focus-visible`, botones con respuesta al presionar, selección/scrollbar con la paleta, `prefers-reduced-motion` global; CoffeeModal pasa de estilos en línea a clases `.cm-*` (sin rebote, salida más rápida); "Cerrar sesión" es la única opción roja del menú de usuario; keyframes `spin` unificado en `main.css` (estaba repetido en `cooperativa.css` y en un `<style>` de `monitoreo.html`). Tailwind escanea solo `src/templates` y `src/static/js`. La skill `frontend-coffeeren` se reescribe con criterio visual y de movimiento adaptado de impeccable, emilkowalski/skills y taste-skill (`referencias/`). |
| 10-12 | — | Rediseño visible de la interfaz (misma marca): cabecera verde bosque con texto crema (`--shell`), lienzo cálido liso en lugar de la foto de fondo (`--canvas`), títulos de página sin tarjeta. Inicio: banner de 220 px con el nombre de la cooperativa sobre la imagen, indicadores en una franja con divisores, panel de precios sin tarjetas anidadas y accesos como enlaces con icono (sin numeración 01–04). Registro pasa a `.page-hero`. Monitoreo: indicadores en una superficie dividida, barras sin caja, rojos con `--danger` (antes ilegibles en oscuro), textos de 12 px como mínimo y altura ajustada a la nueva cabecera. Verificado con capturas de Playwright (1366 px y 390 px, claro y oscuro). |
| 10-12 | — | Beneficio de socio editable con historial: tabla `BONO_SOCIO` (solo inserción) y columna `EVALUACION.bono_socio` (migración `src/database/migracion_bono_socio.sql`, ya incluida en `script.sql`); módulo `bono_socio` en las cuatro capas (`GET`/`POST /bono-socio`, cambio restringido a Gerente/Administrador y auditado); `completar_evaluacion` suma el monto vigente a los socios y lo congela en la fila; análisis y reporte muestran el desglose (base + beneficio) y lo exportan a Excel; sección nueva en Cooperativa; el aviso de conversión a socio lee el monto vigente (antes decía S/ 20.00 fijo). Una evaluación ya completada no se puede volver a completar (antes `PATCH /evaluacion/{id}/completar` recalculaba y sobrescribía el pago). Banner de inicio a todo el ancho con alto fluido. |
| 10-13 | — | Doble caja y doble ID en un mismo grano: el modelo es end2end (sin NMS, `iou` se ignoraba) y emitía la misma caja como `defecto` y `verde`; ByteTrack alternaba la clase del track y abría un ID nuevo con la caja sobrante. Nuevo `_deduplicar_tile()` en `tracker.py`: NMS sin clase por tile (IoU ≥ `IOU_NMS` 0.80 o caja contenida ≥ `IOS_CONTENIDA` 0.90), se conserva la más confiada. |
| 10-13 | — | Reporte y análisis comparten la misma vista: plantilla `partials/resumen_evaluacion.html` y render `resumen-evaluacion.js` (`CoffeeResumen`), que reemplazan el HTML y el JS duplicados en `analisis.html`/`reporte.html` y sus dos exportaciones a Excel. El reporte pasa a la distribución del análisis (datos de la muestra y granos detectados lado a lado, rendimiento en una fila) con la búsqueda y la exportación en la barra superior. Al recargar `/analisis` los indicadores salen de la BD (antes quedaban en "—"); tiempo, specialty y peso de báscula, que solo existen en la sesión del monitoreo, se ocultan si no hay sesión. Tabla de incidencias alineada; barras sin curva con rebote. |
| 10-13 | — | Se retira el grado SCA (Grado 1/2/3, Specialty y Categoría): depende del tipo de defecto y el modelo solo distingue defecto/verde. `classifier.py` solo suma defectos equivalentes; `completar_evaluacion` ya no asigna `categoria_id` (queda NULL, `migracion_sin_grado.sql`) y el resumen no devuelve `categoria`. Quitado de monitoreo, análisis, reporte, Excel y documentación. La tabla `CATEGORIA` se conserva para cuando el modelo clasifique por tipo de defecto. |
| 10-13 | — | Filtro de tamaño ajustado a la altura actual de la cámara sobre la faja JGY370: un grano grande mide ~455 px y con `GRANO_MAX_PX` 480 se detectaba quieto pero se descartaba en movimiento (desenfoque y caja fusionada entre tiles), sin pedir servo. `GRANO_MAX_PX` 480 → 640 y `TILE_SOLAPE_PX` 200 → 320 (regla solape ≥ máximo / 2). |
| 10-13 | — | Precios del día obligatorios: el registro de la muestra validaba con el precio más reciente de cualquier fecha (`obtener_mas_reciente`, eliminado), así que se podía monitorear sin precios de hoy. Ahora `registrar_evaluacion` exige precios con fecha de hoy y `obtener_por_factor` filtra por la fecha del día al completar. Aviso con modal (`CoffeePrecios` en `main.js`, una sola consulta a `/valor-cafe/resumen-rangos`) al entrar a inicio, al entrar a `/registro` y al intentar pasar al monitoreo; el evaluador lee que debe comunicarlo al administrador o gerente. Corregido el gráfico de precios de inicio con un solo precio (eje con `lo === hi` daba NaN). |
| 10-13 | — | `arduino/servito/servito.ino`: prueba aislada del servo separador. Modo manual por Monitor Serie (posiciones, pulso de producción, ciclo de 10 pulsos, ángulo libre) y modo backend (acepta `SERVO:DEFECTO`/`SERVO:BUENO` y enciende el LED D13 al recibir un defecto) para distinguir falla física de comando que no llega. |
| 10-13 | — | Anexo N° 12 del informe (ensayo de latencia, una hoja): `docs/evidencias/Anexo_12_ensayo_latencia.docx`. `analisis_latencia_20260922.md` queda como detalle técnico (desviación estándar, participación por tramo, limitación por el cambio posterior de `TILE_SOLAPE_PX`).
