# Guía de contexto de CoffeeRen

> Punto de entrada para cualquier persona o asistente de IA que llegue al proyecto sin
> contexto previo. Última revisión: 30 de septiembre de 2026 (rama `temporal`, commit `4f38d55`).

Esta carpeta reúne, en pocos documentos, **qué es el sistema, cómo está hecho hoy, qué
falta y cómo continuar**. Está escrita a partir del código real, no del plan original:
si algo de aquí contradice a un documento más antiguo, manda lo que dice esta carpeta
(y, por encima de todo, el código).

## Orden de lectura

| # | Documento | Para qué sirve |
|---|---|---|
| 1 | [01-contexto-del-proyecto.md](01-contexto-del-proyecto.md) | Qué problema resuelve, para quién, flujo de una evaluación, glosario, arquitectura en 4 capas. |
| 2 | [02-modulo-ml.md](02-modulo-ml.md) | Estado actual de la visión artificial: modelo activo, tiles, ByteTrack, clase "desconocido", GPU, parámetros y restricciones. |
| 3 | [03-reentrenamiento-camara-elp.md](03-reentrenamiento-camara-elp.md) | Procedimiento paso a paso para reentrenar (fine-tuning v7) con fotos tomadas con la cámara ELP. **Trabajo pendiente prioritario.** |
| 4 | [04-pendientes.md](04-pendientes.md) | Lista única y priorizada de todo lo que falta (ML, hardware, validación, backend, documentación). |
| 5 | [05-historial-de-cambios.md](05-historial-de-cambios.md) | Cronología de los cambios importantes (marzo–septiembre 2026) con su commit. |

Reglas de trabajo obligatorias para cualquier asistente de IA (Claude, ChatGPT/Codex, Gemini,
Copilot): [AGENTS.md](../../AGENTS.md). `CLAUDE.md` y `GEMINI.md` lo importan y
`.github/copilot-instructions.md` remite a él. Las reglas se cambian solo en `AGENTS.md`.

## Mapa de la documentación del repositorio

### Vigente (refleja el código actual)

| Ubicación | Contenido |
|---|---|
| `docs/guia/` | Esta guía de contexto. |
| [docs/DOCUMENTACION_SISTEMA.md](../DOCUMENTACION_SISTEMA.md) | Documentación funcional general: clasificación, roles, flujo de evaluación, reportes, tablas. |
| [docs/arquitectura.md](../arquitectura.md) | Arquitectura de 4 capas y organización de carpetas. |
| [docs/API_VIDEO_STREAMING.md](../API_VIDEO_STREAMING.md) | Referencia de los endpoints `/video/*` (stream, conteo, reporte, eventos). |
| [docs/hardware-camara.md](../hardware-camara.md) | Ficha técnica de la cámara ELP AR0234, variables `CAM_*` y checklist de calibración física. **Leer antes de tocar `camara_service.py`.** |
| [docs/LIBRERIAS.md](../LIBRERIAS.md) | Qué hace cada librería del `requirements.txt` y dónde se usa. |
| [docs/incidencias/incidencia_proyecto.md](../incidencias/incidencia_proyecto.md) | Registro formal de incidencias INC-01…INC-68 organizado por los 4 sprints de `CRONOGRAMA.xlsx`. |
| [docs/evidencias/](../evidencias/) | Evidencia de indicadores de tesis: ensayo de latencia (≤ 200 ms) y CSV crudos. |
| [docs/manuales/](../manuales/) | Manual de Usuario: solo [Manual_Usuario_CoffeeRen.docx](../manuales/Manual_Usuario_CoffeeRen.docx), sin fuente Markdown ni conversión. Instalación y mantenimiento: fuentes Markdown de los `.docx`, convertidas con `convert_md_to_docx.py`. |
| [docs/registro-avances.md](../registro-avances.md) | Bitácora de avances por fecha (destino por defecto de la skill `documentacion-informes`). |
| [docs/guion-video-sustentacion.md](../guion-video-sustentacion.md) | Guion del video de sustentación (rúbrica de 20 criterios). |
| `docs/CRONOGRAMA.xlsx` | Cronograma vigente: 4 sprints, 8 semanas, hitos 30/50/100 %. |

### Referencia académica o histórica (no describe el código actual)

| Ubicación | Advertencia |
|---|---|
| `docs/documentacion/` | Proyecto de tesis (`.docx` oficial + versión Markdown) y preparación del dataset (CRISP-ML(Q) fase 2). Útiles para objetivos, marco lógico, indicadores y terminología; **sus datos técnicos son de la planificación** (17 clases). |
| [docs/defectos_sca_tabla_referencia.md](../defectos_sca_tabla_referencia.md) | Tabla SCA de equivalencias pensada para el modelo de 17 clases. Hoy el modelo es binario; la tabla que se aplica está en `src/ml/models/yolov26n_2cls/constants.py`. |

## Datos rápidos

- **Modelo en producción:** `yolov26n_2cls` (YOLO26n, 2 clases: `defecto`, `verde`), en
  `src/ml/models/yolov26n_2cls/` (`best.pt` + `best.onnx` + `constants.py`). `best.onnx` está en Git;
  `best.pt` no (se descarga de Google Drive).
- **No existe** el modelo cascada de 14 clases ni `USE_MODELO_DEFECTOS`: se retiró del código el
  2026-07-08 (commit `787a7ac`). Cualquier documento que lo mencione está desactualizado.
- **Inferencia:** GPU (RTX 5070 Ti, `torch 2.12.0+cu130`) con `best.pt` en FP16; CPU con `best.onnx`.
- **Cámara:** ELP AR0234 global shutter, USB 2.0, 1920×1080 MJPEG ~90 fps, backend Media Foundation.
- **Base de datos:** PostgreSQL 18, BD `tesis_prj`, UUIDv7 nativo. Esquema en `src/database/script.sql`.
- **Configuración:** `src/config.py` (gitignored) ↔ `src/config-example.py` (publicado). Todo cambio se replica en ambos.
- **Problema abierto principal:** el modelo confunde granos sanos con defecto (~40 % en pruebas en vivo)
  por *domain gap* entre las fotos de entrenamiento (celular) y la cámara de producción (ELP).
  La solución planificada es el reentrenamiento descrito en [03-reentrenamiento-camara-elp.md](03-reentrenamiento-camara-elp.md).

## Cómo mantener esta guía

- Al cerrar un cambio relevante: actualizar [05-historial-de-cambios.md](05-historial-de-cambios.md)
  y tachar o mover el ítem correspondiente en [04-pendientes.md](04-pendientes.md).
- Si cambia un parámetro del ML (`constants.py`, `config.py`, `bytetrack.yaml`), actualizar la
  tabla de parámetros de [02-modulo-ml.md](02-modulo-ml.md).
- No duplicar aquí lo que ya documenta bien otro archivo vigente: enlazarlo.
