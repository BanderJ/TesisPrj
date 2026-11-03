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
| A | [x] Tiempo de viaje cámara → servo con el motor JGY370 (2026-10-25) | `SERVO_DELAY_S = 0.3` en `.env` (antes 0.5, del motor anterior) | — |
| A | [ ] Recalibrar `SERVO_DELAY_S` tras bajar la velocidad de la faja a PWM 90 | El valor de 0.3 s se midió a PWM 255. El responsable debe medir con el prototipo el tiempo de viaje cámara → servo a PWM 90 para recalibrar `SERVO_DELAY_S`. | — |
| A | [ ] Validar el gate de movimiento corregido (2026-11-02) y calibrar `ML_GATE_UMBRAL` (1.0) | Ahora compara contra el último frame inferido. Pasar un lote de cantidad conocida con `ML_GATE_MOVIMIENTO=true` y `false` y comparar el conteo; revisar el log `gate: diff media=` con faja parada y en marcha | `REVISION.md` 1.1 |
| B | [ ] Ajustar `ML_DETECTOR_FPS` / tiles a la velocidad real de la faja | Que ByteTrack no pierda granos entre detecciones (sobreconteo por ID nuevo) | — |
| B | [ ] Confirmar que los IDs globales no retroceden tras pausas | Prueba real con pausas largas entre granos | — |
| B | [ ] Medir FPS y CPU/GPU con cámara + faja en marcha | Lo medido de CPU (~25 %) fue con frames sintéticos | — |
| B | [ ] Confirmar MJPEG a ~90 fps en el equipo de demostración | Log de arranque; revisar cable y puerto USB | INC-53 |
| B | [ ] Equipo GTX 1050 Mobile | Instalar torch con CUDA compatible, confirmar `half=False`, bajar tiles a 2×2 y medir | — |
| C | [x] Reset del Arduino por DTR al reabrir el puerto (2026-11-02) | Al abrir el puerto `arduino_serial` espera la primera línea del firmware (hasta 3 s) antes de enviar comandos, así el `ON` no se pierde en el bootloader | INC-40 |
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
| C | [x] Distribución circular en el resumen de evaluación (2026-11-03; sin commit) | Barras reemplazadas por dona SVG con total, cantidades y porcentajes en Análisis, Reportes y detalle de Cooperativa. Estados sin conteo, cero y una sola categoría; ajuste móvil y colores por tema. Aprobados 324 escenarios de presentación con datos simulados, capturas claro/oscuro y PDF A4 de dos páginas sin recortes. | — |
| B | [x] Incorporar mínimos de peso en el registro de muestras (2026-11-03; sin commit) | Trillado >60 % y ≤83 % de la muestra; tamizado >80 % y ≤100 % del trillado. Schema con hasta dos decimales, porcentajes compartidos con la plantilla y avisos reutilizados al escribir/enviar. Aprobadas 80 pruebas de caja blanca y 164 escenarios de navegador con respuestas simuladas, sin BD ni hardware. | — |
| B | [ ] Reconstruir la base de desarrollo para las pruebas del responsable | Ejecutar `reset_db.ps1` o el SQL único `src/database/script.sql` cuando el responsable decida reiniciar sus datos. Incluye eventos, beneficio de socio, código EVA único con secuencia, precios decimales, estado activo de precios y tara decimal. La base actual no se ha reiniciado. | — |
| A | [ ] Cambiar la contraseña de PostgreSQL | `src/config.py` se retiró del índice de Git el 2026-11-02 (seguía versionado pese al `.gitignore`) y `reset_db.ps1` ya no la contiene, pero la contraseña anterior sigue en el historial. Cambiarla en PostgreSQL y en el `src/config.py` local | INC-11, `REVISION.md` 2.1 |
| A | [ ] Comprobar tara decimal en la base de desarrollo después de reconstruirla | `src/database/script.sql` define `EVALUACION.tara_total` como `numeric(7, 2)`. Verificado en una base temporal con 1, 2 y 5 sacos; la base actual todavía conserva el tipo entero y las evaluaciones históricas. | `REVISION.md` 2.9 |
| A | [ ] Cargar `logica_hardware.ino` y comprobar sensor, watchdog y servo | Timeout del eco a 5000 µs, buffer serie acotado y watchdog de la faja (2026-11-02). Ángulo DEFECTO actualizado a 30° y hold de producción probado en 0.2 s y devuelto a 0.3 s por el responsable porque el servo actuaba muy rápido para los defectos (2026-11-03); comprobar el desvío tras cargar el firmware y reiniciar el backend. Con la tapa cerrada debe seguir llegando `LISTO:`; con la faja en marcha, detener `uvicorn` (Ctrl+C no basta: cerrar la ventana o desconectar el USB) y comprobar que la faja se apaga en ~3 s | `REVISION.md` 3.2, 3.8 |
| A | [x] Aplicar revisión de código EVA y precios en la base de desarrollo (2026-11-02) | Código EVA `UNIQUE` con secuencia y `VALOR_CAFE.precio` a `numeric(7, 2)`. Para nuevas reconstrucciones, ambos cambios están integrados en `src/database/script.sql`. | `REVISION.md` 2.4, 2.10 |
| B | [ ] Pendientes de la revisión técnica | Ver la sección «Estado» de `REVISION.md`: clase del servo frente a la del conteo, tiles, pool de conexiones, `/resources` público, versiones fijadas | `REVISION.md` |
| B | [x] Alinear código con las decisiones del manual (2026-10-30; revisión 2026-10-31) | Peso bueno limitado por tamizado; cálculo pendiente accesible desde reportes; precio por `floor(FR)`; usuario con una inicial materna, normalización y límite de 30 caracteres sin truncar; humedad 1–30; tildes y ayuda corregidas. Revisión: C5 incluye 0 y 12.5, PCB-05 aclara el doble y la comprobación SQL; Word de caja negra sincronizado con el 30/10 sin repetir sus pruebas y con portada, guía y pendientes conservados. | `docs/manuales/INSTRUCCIONES_CAMBIOS_CODIGO.md` |
| C | [ ] Automatizar la descarga de `best.pt` | Hoy es manual desde Google Drive | INC-39 |
| C | [x] Actualizar la plantilla y la ruta de prueba renombradas (2026-11-01; sin commit) | La ruta autenticada `/prueba` carga `prueba.html`; referencias documentales actualizadas y recursos JS/CSS comprobados. | — |
| C | [x] Acceso a prueba desde Registro de muestra (2026-11-01; sin commit) | Botón «Prueba» a la derecha del título, enlazado a `/prueba`, ampliado a 132 × 52 px, texto de 16 px y fondo marrón de la paleta existente. Disposición y contraste verificados en vista previa a 1280, 390 y 320 px, en claro y oscuro; navegación verificada antes del ajuste visual. | — |
| C | [x] Saludo personalizado tras iniciar sesión (2026-11-01; sin commit) | Inicio muestra «Bienvenido, nombre» una sola vez tras autenticar; espera el cierre del saludo antes del aviso de precios pendientes. Sintaxis JS y 11 escenarios simulados aprobados; pendiente verificar el login en la aplicación. | — |
| C | [x] Recomendación de prueba una vez por inicio de sesión (2026-11-01; sin commit) | Para todos los roles: el login habilita la recomendación y la primera visita a Registro consume una marca compartida entre pestañas. Al volver o recargar no se repite; los precios se consultan siempre. Sintaxis JS y comportamiento simulado aprobados; sin ejecutar el login real. | — |
| C | [ ] Revisar visibilidad de reportes | `/reporte` (búsqueda EVA) es para toda sesión; `/reportes` (estadísticos) exige Gerente/Admin. Confirmar que es lo deseado | — |
| B | [x] Reportes de Cooperativa por período y caficultor (2026-11-02; sin commit) | Resumen de evaluaciones completadas con kilos brutos, pagos y beneficios históricos; historial paginado con búsqueda por nombre/documento, fechas y tipo en la entrega. «Ver detalle» abre el resumen compartido en modal. Verificados 28 escenarios de API con tablas temporales PostgreSQL y navegación con datos de prueba a 1280/390 px, claro/oscuro; sin ejecutar el arranque completo con ML/hardware. | — |
| C | [ ] Mostrar aviso visual al denegar acceso | Mostrar «No tienes permisos para acceder a esta sección» al navegar a una página restringida; actualmente el 403 HTML redirige silenciosamente a Inicio. Pendiente por decisión del responsable. | — |
| A | [x] Autenticar consultas y restringir la operación de muestras al Evaluador (2026-11-02; sin commit) | DNI, persona, catálogos y ubigeo exigen sesión; login verificado sin dependencia de ellos. Registrar, finalizar, completar, generar reporte de lote, iniciar motor y abrir monitoreo exigen Evaluador. Consultas, Prueba y parada del motor conservan sesión. Cálculo oculto para Gerente/Administrador en reportes y análisis, con aviso pendiente y scripts adaptados. Caja blanca 38/38, 127 comprobaciones HTTP y diez escenarios de navegador aprobados sobre copia de la BD y hardware simulado. Tabla 1.1.2 del manual conservada porque ya describe estos accesos. | — |
| A | [x] Proteger detener/resetear de Prueba frente a un lote de evaluación (2026-11-02; sin commit) | Propuesta aprobada e implementada: schema de control con ID opcional, guard de rol/ID en el service y 409/403 sin alterar el lote. Bloqueo de control compartido con iniciar, conteo protegido también después de detener; Prueba no adopta evaluaciones y Monitoreo conserva otro lote asociado. Pasaron 38 pruebas de caja blanca y 34 regresiones, 187 comprobaciones HTTP y 14 escenarios de navegador sobre copia de BD con hardware simulado. Precondición de caja negra adaptada al contrato, sin ejecutar esa suite. | — |
| A | [x] Completar el ciclo de protección del lote (2026-11-03; sin commit) | Inicio validado en servidor con ID/rol bajo bloqueo, incluso después de detener; reanudación conserva conteo. Finalización libera la asociación solo tras persistir y conserva el lote ante fallos. Recuperación de lote abandonado con confirmación y descarte explícito de Evaluador. Pasaron 38 pruebas de caja blanca y 52 regresiones de control, 88 comprobaciones HTTP y 16 escenarios de navegador sobre copia de BD y hardware simulado; cancelar no envía controles y Prueba funciona después de finalizar sin reiniciar el servidor. | — |
| B | [ ] Definir el tratamiento de las evaluaciones descartadas | Quedan sin código EVA, en estado activa y sin conteo. El responsable decidirá si se anulan o cómo se muestran. | — |
| C | [ ] Decidir acceso a `GET /caficultor/listar` | Único consumidor encontrado en `cooperativa.js:818`, sección Caficultores de Cooperativa, accesible para Gerente/Administrador. La ruta conserva su autenticación de sesión y no se cambió. | — |
| B | [x] Corregir carga de Cooperativa para Gerente al restringir usuarios al Administrador (2026-11-02; sin commit) | El JavaScript comprueba que exista `navUsuarios` antes de mostrarlo: Jinja omite el enlace para Gerente. Reproducido el error previo y verificados ocho escenarios en navegador con roles 2/3, escritorio/móvil y claro/oscuro; sin BD ni hardware. Permisos de escritura del servidor conservados. | — |
| B | [x] Unificar la reconstrucción de la base (2026-11-02; sin commit) | Conservado un único `script.sql`, retiradas cuatro migraciones redundantes y actualizado `reset_db.ps1` con parada ante errores y ruta independiente del directorio actual. Verificadas 19 comprobaciones en PostgreSQL: base vacía, segunda ejecución, tara decimal, datos iniciales y reversión completa ante fallo. Base temporal eliminada; registros y tipos de la base original sin cambios. | — |
| B | [x] Desactivar rangos de precio conservando historial (2026-11-02; sin commit) | Confirmación explícita, retiro de todas las versiones de hoy y reemplazo permitido sin solapamientos. UUID, precios y pagos históricos conservados; las pendientes pueden completarse después. Comprobados 44 casos SQL/API y cuatro flujos de interfaz en escritorio/móvil y claro/oscuro, incluida la edición concurrente. Columna `activo` incorporada al SQL único y aplicada a la base actual sin reiniciarla ni alterar los valores previos de sus 30 precios y 30 evaluaciones. | — |

| B | [x] Actualizar accesos por rol en el Manual de Usuario (2026-11-02; sin commit) | Tabla general de secciones en 1.1.2, página 4, con columnas Evaluador/Gerente/Administrador; corregidos los apartados de usuarios, tipos de grano, beneficio de socio y recuperación de cuenta. Índice actualizado, 31 páginas revisadas, 21 imágenes idénticas por SHA-256 y 25 pies conservados. Reglas sincronizadas en AGENTS.md; sin cambios de código. |

## 5. Documentación y repositorio

| Prio | Pendiente | Detalle |
|---|---|---|
| C | [x] Reservar una hoja para cada evidencia pendiente de caja negra (2026-11-03; sin commit) | Páginas vacías y editables tras PCN-16–21, verificadas en PDF: 34, 36, 38, 40, 42 y 44; documento de 44 a 50 páginas. Textos, fichas e imágenes existentes conservados. Generador adaptado y comprobado dos veces en copia temporal, sin duplicar reservas. Las pruebas físicas y sus evidencias siguen pendientes; no se ejecutó caja negra. |
| B | [x] Sincronizar caja blanca y textos delimitados del Manual de Usuario (2026-11-03; sin commit) | PCB-03 ampliado a C1–C14 y fragmentos PCB-03/06/08/09/11 actualizados; generadores ejecutados: 12 casos y 47 caminos aprobados, 12 capturas usadas con SHA-256 coincidente y firmas conservadas. Manual respaldado, corregido solo en cinco celdas y dos alertas nuevas: 32 páginas, 21 imágenes y 25 pies; resto del texto, estilos y ejemplos de 4 sacos idénticos al respaldo. |
| B | [ ] Aprobar ampliación de caja negra y observaciones SQL | Ocho propuestas PCN-25–32 en la hoja `Propuestas_pendientes` y revisión estática de 15 models/76 llamadas en `Revision_SQL`, dentro del Excel de caja negra. Catálogo vigente de 24 casos y resultados conservados; no se ejecutaron pruebas nuevas. Cuatro construcciones SQL con f-strings en auditoria.py, cooperativa.py y tipo_grano.py componen cláusulas fijas y pasan los valores por `%s`, pero incumplen AGENTS.md 5.2; corrección pendiente de decisión. |
| B | [x] Conservar solo el Manual de Usuario como manual de entrega (2026-11-01; sin commit) | Retirados los otros manuales, su conversor y las referencias asociadas. Se conserva el Word de usuario, su respaldo y sus archivos de apoyo. |
| C | [x] Manual de Usuario sin fuente Markdown | Resuelto: el Manual de Usuario se mantiene solo en Word (`docs/manuales/Manual_Usuario_CoffeeRen.docx`), sin fuente Markdown ni conversión; `generar_manual_completo.py` eliminado el 2026-10-27. |
| C | [x] Documentos citados que ya no están en el repo | Resuelto 2026-09-30: la sección de referencias del registro de incidencias y `docs/documentacion/README.md` indican el commit para recuperarlos |
| C | [x] Limpieza de la raíz (2026-09-30) | Eliminados `corrida.log` y `latencia.log` (volcados de consola) y `*.log` añadido a `.gitignore`. Se conserva `check_model.py` como herramienta de diagnóstico. `generar_manual_completo.py` se eliminó el 2026-10-27. |
| C | [ ] `docs/defectos_sca_tabla_referencia.md` | Tabla pensada para 17 clases; actualizar cuando la cooperativa valide la tabla oficial |
