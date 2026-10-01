# 04 — Pendientes del proyecto (al 30-sep-2026)

> Lista única y priorizada. Cuando se cierre un ítem, marcarlo `[x]` con fecha y commit, y
> registrarlo en [05-historial-de-cambios.md](05-historial-de-cambios.md). Las referencias
> `INC-xx` apuntan a [docs/incidencias/incidencia_proyecto.md](../incidencias/incidencia_proyecto.md).
>
> Regla: los ítems que requieren un umbral o una regla de negocio nueva se **consultan con el
> usuario antes de implementarse**. Nada de esta lista autoriza a cambiar las restricciones
> absolutas de [02-modulo-ml.md](02-modulo-ml.md#9-restricciones-absolutas-no-cambiar-sin-permiso-explícito-del-usuario).

Prioridad: **A** = bloquea la calidad del resultado o la sustentación; **B** = necesario antes
del uso real en la cooperativa; **C** = mejora o deuda técnica.

## 1. Modelo y calidad de clasificación

| Prio | Pendiente | Detalle / siguiente paso | Ref. |
|---|---|---|---|
| A | [ ] **Reentrenamiento v7 con fotos de la cámara ELP** | Capturar 300–500 imágenes en condiciones de producción, etiquetar en Roboflow (versión 7), ejecutar el notebook, comparar v6 vs v7 y desplegar. Guía completa: [03-reentrenamiento-camara-elp.md](03-reentrenamiento-camara-elp.md) | INC-65 |
| A | [ ] Evaluación formal Fase 4 CRISP-ML(Q) | Precisión, recall, F1 y mAP por clase, matriz de confusión y prueba sobre fotos solo-ELP. Sale del paso 6 del reentrenamiento | INC-63 |
| A | [ ] Validar equivalencias SCA con la cooperativa | `defecto = 1`, `desconocido = 1.0` en `constants.py`. Sesión con el área de calidad de Line Coffee Marañón / tabla INCAL | INC-17 |
| B | [ ] Calibrar `UMBRAL_CONF_CONOCIDO` (0.35) | Con granos reales: granos que se tocan o mal iluminados no deben caer en `desconocido`. Vigilar `total_desconocidos` | — |
| B | [ ] Recalibrar `MARGEN_DEFECTO` (1.3) tras v7 | Si v7 ya no tiene sesgo hacia defecto, acercarlo a 1.0 | — |
| B | [ ] Recorte de ROI de la faja antes de inferir (Bloque 4) | Requiere una captura real de `/monitoreo` para fijar el ROI. Reduce área inútil y mejora granos que se tocan | INC-54 |
| C | [ ] Decidir clase explícita de materia extraña | Alternativa a la detección por baja confianza. Cambia `constants.py` y frontend. **Decisión del usuario** | — |
| C | [ ] Monitoreo de calidad / deriva en producción | Mecanismo mínimo de alerta por degradación (backlog original: `GET /monitoring/quality`) | INC-64 |
| C | [ ] Trazabilidad del dataset | Registrar splits y hashes de la versión 7; documentar IRA o por qué no aplica (anotador único) | INC-62 |

## 2. Calibración en banco con cámara y faja reales

| Prio | Pendiente | Detalle | Ref. |
|---|---|---|---|
| A | [ ] Iluminación difusa y exposición manual | Instalar luz sin parpadeo; fijar `CAM_EXPOSURE` (p. ej. -6 ≈ 1/64 s) para eliminar estela | INC-57 |
| A | [ ] Bloquear zoom y foco del lente | Anotar geometría de trabajo (distancia, ancho útil). Prerrequisito del reentrenamiento | INC-56 |
| B | [ ] Calibrar `ML_GATE_UMBRAL` (1.0) | Comparar el log `gate: diff media=` con faja parada y en marcha. Si salta granos: `ML_GATE_MOVIMIENTO=false` | — |
| B | [ ] Ajustar `ML_DETECTOR_FPS` / tiles a la velocidad real de la faja | Que ByteTrack no pierda granos entre detecciones (sobreconteo por ID nuevo) | — |
| B | [ ] Confirmar que los IDs globales no retroceden tras pausas | Prueba real con pausas largas entre granos | — |
| B | [ ] Medir FPS y CPU/GPU con cámara + faja en marcha | Lo medido de CPU (~25 %) fue con frames sintéticos | — |
| B | [ ] Confirmar MJPEG a ~90 fps en el equipo de demostración | Log de arranque; revisar cable y puerto USB | INC-53 |
| B | [ ] Equipo GTX 1050 Mobile | Instalar torch con CUDA compatible, confirmar `half=False`, bajar tiles a 2×2 y medir | — |
| C | [ ] Reset del Arduino por DTR al reabrir el puerto | El re-handshake reenvía `ON` pero no el estado del servo. Archivo restringido: requiere permiso | INC-40 |
| C | [ ] Báscula HX711 | Retirada temporalmente del firmware; el peso bueno se ingresa a mano. Decidir si vuelve | — |

## 3. Evidencias para la sustentación

| Prio | Pendiente | Detalle | Ref. |
|---|---|---|---|
| A | [ ] Analizar los ensayos de latencia del 29-sep | `docs/evidencias/latencia_20260929_143213.csv`, `_144417.csv`, `_150050.csv`. Redactar un análisis como el de `analisis_latencia_20260922.md` y anotar en qué condición se tomó cada uno | — |
| A | [ ] Validación en campo con operarios | ≥ 3 operarios, ≥ 2 lotes cada uno, encuesta SUS ≥ 70, acta firmada por la gerencia | INC-64 |
| B | [ ] Comparación conteo manual vs sistema | Mismo lote contado por el evaluador y por CoffeeRen; base para la validación de las equivalencias | — |

## 4. Backend, base de datos y seguridad

| Prio | Pendiente | Detalle | Ref. |
|---|---|---|---|
| B | [ ] Migrar bases existentes | Ejecutar el `CREATE TABLE EVENTO_MONITOREO` (+ índice y FK) y `ALTER TABLE evaluacion ALTER COLUMN peso_neto TYPE numeric(7,2)` en cada base creada antes del 22-sep | — |
| B | [ ] Credenciales de BD fuera del código | `src/config.py` ya no se versiona, pero la contraseña sigue como literal; moverla a `.env` antes de desplegar | INC-11 |
| C | [ ] Automatizar la descarga de `best.pt` | Hoy es manual desde Google Drive | INC-39 |
| C | [ ] Revisar visibilidad de reportes | `/reporte` (búsqueda EVA) es para toda sesión; `/reportes` (estadísticos) exige Gerente/Admin. Confirmar que es lo deseado | — |

## 5. Documentación y repositorio

| Prio | Pendiente | Detalle |
|---|---|---|
| B | [ ] Regenerar los `.docx` de los manuales | Las fuentes Markdown se movieron a `docs/manuales/` y se actualizaron; `convert_md_to_docx.py` ya apunta allí. `INSTALACION.md` se eliminó por duplicar el Manual de Instalación |
| C | [ ] Manual de Usuario sin fuente Markdown | Lo genera `generar_manual_completo.py` (ruta absoluta `d:\TesisPrj\...`); migrarlo a `docs/manuales/Manual_Usuario_CoffeeRen.md` |
| C | [x] Documentos citados que ya no están en el repo | Resuelto 2026-09-30: la sección de referencias del registro de incidencias y `docs/documentacion/README.md` indican el commit para recuperarlos |
| C | [x] Limpieza de la raíz (2026-09-30) | Eliminados `corrida.log` y `latencia.log` (volcados de consola) y `*.log` añadido a `.gitignore`. Se conservan `check_model.py`, `convert_md_to_docx.py` y `generar_manual_completo.py` (herramientas en uso); podrían moverse a `scripts/` |
| C | [ ] `docs/defectos_sca_tabla_referencia.md` | Tabla pensada para 17 clases; actualizar cuando la cooperativa valide la tabla oficial |
