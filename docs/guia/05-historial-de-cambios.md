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
