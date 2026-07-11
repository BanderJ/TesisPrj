**UNIVERSIDAD CAT�LICA SANTO TORIBIO DE MOGROVEJO**

**FACULTAD DE INGENIER�A**

**ESCUELA DE INGENIER�A DE SISTEMAS Y COMPUTACI�N**

![Instituto de Estudios Toribianos: Santo Toribio de Mogrovejo Un haz de luz  y lealtad (Himno de la USAT, Chiclayo)](data:image/jpeg;base64...)

**SISTEMA AUTOM�TICO DE CLASIFICACI�N DE GRANOS DE CAF� VERDE MEDIANTE VISI�N ARTIFICIAL EN UNA COOPERATIVA DE AMAZONAS**

**PRODUCT BACKLOG Y PLANIFICACI�N DE SPRINTS**

Metodolog�a H�brida SCRUM + CRISP-ML(Q)

**AUTOR**

**ANDERSON JHOMAR BACA CHUQUIMANCO**

**Chiclayo, 2026**

# 1. MARCO METODOL�GICO H�BRIDO

Metodolog�a h�brida **SCRUM + CRISP-ML(Q)**. Scrum provee el marco iterativo de gesti�n (Sprints, ceremonias, artefactos); CRISP-ML(Q) provee el rigor t�cnico y la garant�a de calidad en cada fase del ciclo de vida del sistema ML.

## 1.1 Correspondencia Sprint ? Fase CRISP-ML(Q)

Tabla de nombres de Sprints usada en todo el documento.

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| **Sprint** | **Nombre del Sprint** | **Fase CRISP-ML(Q)** | **Per�odo** | **SP** |
| **S0** | Comprensi�n del Negocio y los Datos | Comprensi�n del Negocio y los Datos | 23 Mar � 06 Abr | **17** |
| **S1** | Preparaci�n de los Datos | Preparaci�n de los Datos | 07 Abr � 20 Abr | **29** |
| **S2** | Preparaci�n de Datos y Modelado | Preparaci�n de Datos ? Modelado | 21 Abr � 02 May | **21** |
| **S3** | Ingenier�a del Modelo | Ingenier�a del Modelo | 03 May � 14 May | **19** |
| **S4** | Evaluaci�n del Modelo | Evaluaci�n del Modelo | 15 May � 26 May | **21** |
| **S5** | Despliegue del Modelo � Inferencia y Hardware | Despliegue del Modelo | 27 May � 07 Jun | **29** |
| **S6** | Despliegue del Modelo � Interfaz y Reportes | Despliegue del Modelo | 08 Jun � 19 Jun | **21** |
| **S7** | Supervisi�n y Mantenimiento | Supervisi�n y Mantenimiento | 20 Jun � 02 Jul | **16** |
| **S8** | Documentaci�n y Cierre Acad�mico | Cierre Acad�mico | 03 Jul � 10 Jul | **16** |
| **TOTAL** | **23 Mar � 10 Jul 2026** | **6 fases CRISP-ML(Q)** | **16 semanas** | **189 SP** |

**Nota:** S5 y S6 comparten la fase Despliegue del Modelo (50 SP combinados). S2 es Sprint de transici�n. S7 cierra el sistema operativo (2 jul). S8 finaliza la documentaci�n acad�mica (10 jul).

## 1.2 Roles del Scrum Team

|  |  |  |
| --- | --- | --- |
| **Rol Scrum** | **Responsable** | **Responsabilidades** |
| **Product Owner** | Anderson J. Baca Chuquimanco | Aprobaci�n de criterios DoD, validaci�n del incremento en cada Sprint Review, priorizaci�n del backlog t�cnico�acad�mico. |
| **Scrum Master / Developer** | Anderson J. Baca Chuquimanco | Facilitaci�n de ceremonias, desarrollo software (FastAPI, PostgreSQL, frontend), entrenamiento YOLO, integraci�n hardware (Arduino, HX711). Documentaci�n Bit�cora EXP. |

# 2. PRODUCT BACKLOG PRIORIZADO

Fuente �nica del trabajo del Scrum Team (Scrum Guide, 2020). **Objetivo del producto:** automatizar la clasificaci�n de granos de caf� verde con precisi�n ? 85 %, latencia ? 500 ms, cumpliendo la NTP-ISO 10470:2014, con sistema completo el 10 de julio de 2026.

|  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- |
| **PBI** | **Sprint** | **Historia de Usuario** | **Fase CRISP-ML(Q)** | **RF / RNF** | **Prior.** | **SP** |
| **PBI-01** | **S0** | Como investigador, quiero definir los RF y RNF del sistema alineados a los objetivos de la cooperativa. | Comprensi�n del Negocio y los Datos | RF01�RF09 / RNF01�07 | **Must** | **3** |
| **PBI-02** | **S0** | Como investigador, quiero seleccionar el stack tecnol�gico (YOLOv8, FastAPI, PostgreSQL 18, Arduino) para garantizar la viabilidad t�cnica. | Comprensi�n del Negocio y los Datos | RNF03, RNF06 | **Must** | **2** |
| **PBI-03** | **S0** | Como PO, quiero el Product Backlog (24 PBIs) y los 9 Sprints planificados con fechas ajustadas al semestre acad�mico. | Comprensi�n del Negocio y los Datos | � | **Must** | **3** |
| **PBI-04** | **S1** | Como desarrollador, quiero BD PostgreSQL 18 con UUIDv7 en tablas transaccionales e INT en maestras, con migraciones Alembic. | Preparaci�n de los Datos | RNF03, RF09 | **Must** | **5** |
| **PBI-05** | **S1** | Como operario, quiero interfaz web (v1, 60 %) con login Argon2id+JWT para registrar datos del lote. | Preparaci�n de los Datos | RF01, RNF04, RNF07 | **Must** | **8** |
| **PBI-06** | **S1** | Como ML Engineer, quiero dataset h�brido (USK-Coffee + Kaggle + propio) etiquetado bajo NTP-ISO 10470:2014 con ? 5 000 im�genes. | Preparaci�n de los Datos | RF03 | **Must** | **8** |
| **PBI-07** | **S2** | Como ML Engineer, quiero aumentaci�n de datos y split estratificado train/val/test (70/20/10) con ? 8 000 im�genes en train. | Preparaci�n de Datos ? Modelado | RF03, RNF01 | **Must** | **5** |
| **PBI-08** | **S2** | Como ML Engineer, quiero entrenar ? 3 arquitecturas YOLOv8 bajo condiciones controladas con seguimiento MLflow. | Preparaci�n de Datos ? Modelado | RF03, RNF01, RNF06 | **Must** | **13** |
| **PBI-09** | **S3** | Como ML Engineer, quiero comparar modelos con tabla ponderada (mAP, F1, latencia, recall broca) y seleccionar el �ptimo. | Ingenier�a del Modelo | RNF01, RNF02 | **Must** | **5** |
| **PBI-10** | **S3** | Como ML Engineer, quiero ajustar hiperpar�metros (Optuna, ? 20 trials) si ning�n modelo supera los umbrales DoD. | Ingenier�a del Modelo | RNF01, RNF02 | **Should** | **8** |
| **PBI-11** | **S3** | Como ML Engineer, quiero exportar el modelo final a ONNX (opset=17) con variaci�n mAP < 0.01 respecto al modelo PyTorch. | Ingenier�a del Modelo | RNF05, RNF06 | **Must** | **3** |
| **PBI-12** | **S4** | Como investigador, quiero evaluar el modelo en el test set y obtener m�tricas formales aprobadas por el asesor. | Evaluaci�n del Modelo | RNF01 | **Must** | **5** |
| **PBI-13** | **S4** | Como investigador, quiero experimento controlado sistema vs. clasificaci�n manual (t-test, ? = 0.05, ? 5 lotes). | Evaluaci�n del Modelo | RF03 | **Must** | **8** |
| **PBI-14** | **S4** | Como investigador, quiero mapas Grad-CAM (? 10 im�genes/clase) validados cualitativamente por el experto de la cooperativa. | Evaluaci�n del Modelo | RNF01 | **Should** | **5** |
| **PBI-15** | **S5** | Como desarrollador, quiero POST /classify/frame con latencia P95 ? 500 ms integrando modelo ONNX v�a YOLOService. | Despliegue del Modelo | RF02, RF03, RNF02 | **Must** | **8** |
| **PBI-16** | **S5** | Como desarrollador, quiero comunicaci�n serial Arduino-FastAPI para activar servo actuador en ? 50 ms. | Despliegue del Modelo | RF04, RNF02 | **Must** | **8** |
| **PBI-17** | **S5** | Como operario, quiero integraci�n celda HX711 (error ? �2 g) para c�lculo autom�tico del Factor de Rendimiento. | Despliegue del Modelo | RF05, RF06 | **Must** | **8** |
| **PBI-18** | **S6** | Como operario, quiero dashboard en tiempo real con stream ? 15 FPS, bounding boxes y contadores via WebSocket. | Despliegue del Modelo | RF07, RNF07 | **Must** | **8** |
| **PBI-19** | **S6** | Como administrador, quiero reportes PDF y CSV exportables generados en < 3 s con FR y desglose de defectos. | Despliegue del Modelo | RF08, RF09 | **Must** | **5** |
| **PBI-20** | **S6** | Como administrador, quiero historial de lotes paginado con filtros, respuesta ? 500 ms con 100 registros. | Despliegue del Modelo | RF09, RNF03 | **Must** | **5** |
| **PBI-21** | **S7** | Como investigador, quiero validar el sistema en campo con ? 3 operarios reales, precisi�n ? 85 %, SUS ? 70 y acta firmada. | Supervisi�n y Mantenimiento | RF01�RF09 | **Must** | **8** |
| **PBI-22** | **S7** | Como ML Engineer, quiero dashboard de monitoreo con alerta si precisi�n < 80 % en 3 sesiones consecutivas. | Supervisi�n y Mantenimiento | RNF01, RNF05 | **Should** | **5** |
| **PBI-23** | **S8** | Como investigador, quiero Cap�tulos III y IV de la tesis completados y aprobados por el asesor (APA 7ma ed.). | Documentaci�n y Cierre Acad�mico | � | **Must** | **8** |
| **PBI-24** | **S8** | Como desarrollador, quiero el manual de mantenimiento y el plan de reentrenamiento semestral documentados. | Documentaci�n y Cierre Acad�mico | RNF05 | **Should** | **3** |
| **TOTAL** | **S0�S8** | **24 PBIs � 9 Sprints � 23 Mar � 10 Jul 2026** | **6 fases CRISP-ML(Q)** | � | **Must:20/Should:4** | **189 SP** |

**Leyenda:** Must = cr�tico no negociable � Should = importante, timing flexible

# 3. DEFINICI�N DE TERMINADO (DOD) GLOBAL

Est�ndar de calidad m�nimo para la aceptaci�n de cada Incremento (Scrum Guide, 2020), integrando la dimensi�n Q de CRISP-ML(Q).

## 3.1 DoD de Software y Hardware

|  |  |  |
| --- | --- | --- |
| **Criterio** | **Evidencia requerida** | **RNF** |
| C�digo versionado en Git con mensaje de commit descriptivo | Branch mergeado a main sin conflictos pendientes | RNF05 |
| Tests unitarios e integraci�n sin errores | pytest: 0 failures, cobertura ? 80 % en m�dulos cr�ticos | RNF05 |
| GET /health retorna HTTP 200 con todos los m�dulos activos | Verificaci�n Postman antes de cada Sprint Review | RNF02 |
| Migraci�n Alembic sin errores en entorno de desarrollo | alembic upgrade head ? 0 errores | RNF03 |
| Latencia end-to-end ? 500 ms (captura ? detecci�n ? actuador) | 50 iteraciones consecutivas. P95 documentado | RNF02, RF04 |
| Autenticaci�n Argon2id + JWT funcional en rutas protegidas | HTTP 401 sin token. Login v�lido ? token 8 h | RNF04 |
| Incremento demostrable en vivo en Sprint Review | Aprobaci�n del PO (asesor) en la Sprint Review | Scrum Guide |

## 3.2 DoD del Modelo ML � Dimensi�n Q de CRISP-ML(Q)

|  |  |  |
| --- | --- | --- |
| **Criterio de Calidad ML** | **Evidencia requerida** | **Fase** |
| Precisi�n del modelo en test set ? 85 % | Tabla de m�tricas en Bit�cora EXP, firmada por asesor | Evaluaci�n del Modelo |
| Recall clase broca ? 0.90 | Matriz de confusi�n por clase en test set | Evaluaci�n del Modelo |
| F1-score ponderado ? 0.85 en test set | Reporte sklearn incluido en Cap�tulo IV | Evaluaci�n del Modelo |
| mAP@50 ? 0.85 en test set (datos nunca vistos) | results.csv de evaluaci�n YOLO + curva PR | Evaluaci�n del Modelo |
| Variaci�n mAP PyTorch ? ONNX < 0.01 | Script de comparaci�n, delta documentado | Ingenier�a del Modelo |
| Dataset cumple NTP-ISO 10470:2014 y NTP 209.027:2018 | Cat�logo validado por experto de cooperativa | Preparaci�n de los Datos |
| Bit�cora EXP completa por experimento | ID, arquitectura, hiperpar�metros, m�tricas, decisi�n | Ingenier�a del Modelo |
| Robustez: variaci�n ? 5 % en 4 escenarios adversos | Evaluaci�n: iluminaci�n, �ngulo, oclusi�n, movimiento | Evaluaci�n del Modelo |
| Sistema supera clasificaci�n manual (p-value < 0.05, t-test) | Informe estad�stico con scipy.stats | Evaluaci�n del Modelo |

# 4. PLANIFICACI�N DETALLADA DE SPRINTS

Sprints de duraci�n variable (8�14 d�as) ajustados para que el sistema completo finalice el **10 de julio de 2026**. Los nombres son los definidos en la Tabla 1.1 y no var�an en ning�n apartado del documento.

|  |
| --- |
| **S0 � Comprensi�n del Negocio y los Datos**  23 Mar � 06 Abr 2026 � Fase: Comprensi�n del Negocio y los Datos � 17 SP |

### Objetivo del Sprint � �Por qu�?

Establecer el marco investigativo, formalizar los requerimientos del sistema alineados a los objetivos de la Cooperativa Line Coffee Mara��n y definir los criterios de �xito ML, empresarial y econ�mico. Corresponde a la fase Comprensi�n del Negocio y los Datos de CRISP-ML(Q).

### PBIs del Sprint

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| **ID** | **Descripci�n del PBI** | **Tipo** | **Criterio DoD clave** | **SP** |
| **PBI-01** | An�lisis de RF/RNF mediante entrevistas y encuestas a la cooperativa | Investigaci�n | Documento de RF aprobado por el PO | **3 SP** |
| **PBI-02** | Selecci�n y justificaci�n del stack: YOLOv8, FastAPI, PostgreSQL 18, Arduino, OpenCV | Arquitectura | ADR con justificaci�n t�cnica documentado | **2 SP** |
| **PBI-03** | Product Backlog (24 PBIs) y planificaci�n de 9 Sprints con fechas ajustadas al semestre | Gesti�n �gil | Backlog priorizado aprobado en Sprint Review | **3 SP** |
| **PBI-03b** | Encuestas a caficultores y entrevistas al personal de la cooperativa | Investigaci�n | Informe con ? 80 % de aceptaci�n tecnol�gica | **5 SP** |
| **PBI-03c** | Definici�n de criterios de �xito ML (precisi�n, latencia, FR) | CRISP-ML(Q) �3.1.2 | Documento de objetivos ML firmado por asesor | **4 SP** |

### Incremento Verificable

An�lisis de Requerimientos v1.0 aprobado � Product Backlog 24 PBIs � Informe de encuestas � Criterios de �xito ML formalizados.

|  |
| --- |
| **S1 � Preparaci�n de los Datos**  07 Abr � 20 Abr 2026 � Fase: Preparaci�n de los Datos � 29 SP |

### Objetivo del Sprint � �Por qu�?

Construir la capa de datos del sistema (BD PostgreSQL 18 UUIDv7, API FastAPI M-S-R, autenticaci�n segura) y consolidar el dataset h�brido etiquetado bajo NTP-ISO 10470:2014. Corresponde a la fase Preparaci�n de los Datos de CRISP-ML(Q).

### PBIs del Sprint

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| **ID** | **Descripci�n del PBI** | **Tipo** | **Criterio DoD clave** | **SP** |
| **PBI-04** | BD PostgreSQL 18: UUIDv7, modelos SQLAlchemy, migraciones Alembic | Backend / BD | alembic upgrade head ? 0 errores. UUIDv7 verificado | **5 SP** |
| **PBI-05** | API FastAPI (M-S-R) + Argon2id+JWT + interfaz web v1 (60 %) | Backend / Frontend | GET /health ? HTTP 200. Login funcional | **8 SP** |
| **PBI-06** | Dataset h�brido ? 5 000 im�genes etiquetadas bajo NTP-ISO 10470:2014 | Ingenier�a de Datos | IRA ? 85 % con experto. data.yaml nc:7 | **8 SP** |
| **PBI-06b** | Validaci�n de calidad: nitidez (Laplaciano), duplicados (MD5), balance de clases | Ingenier�a de Datos | 0 im�genes duplicadas/borrosas. Reporte de distribuci�n | **5 SP** |
| **PBI-05b** | POST /batch/start con validaci�n peso\_trillado ? peso\_total | Backend | HTTP 201 + UUIDv7. HTTP 422 si peso inv�lido | **3 SP** |

### Incremento Verificable

BD PostgreSQL 18 operativa � API FastAPI con /health y autenticaci�n � Interfaz web 60 % � Dataset ? 5 000 im�genes versionadas en Git LFS (tag: coffee\_v1).

|  |
| --- |
| **S2 � Preparaci�n de Datos y Modelado**  21 Abr � 02 May 2026 � Fase: Preparaci�n de Datos ? Modelado � 21 SP |

### Objetivo del Sprint � �Por qu�?

Aplicar aumentaci�n de datos sistem�tica para ampliar el conjunto de entrenamiento a ? 8 000 im�genes, y ejecutar los 3 experimentos de entrenamiento YOLOv8 bajo condiciones controladas. Sprint de transici�n entre Preparaci�n de Datos y la fase Ingenier�a del Modelo.

### PBIs del Sprint

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| **ID** | **Descripci�n del PBI** | **Tipo** | **Criterio DoD clave** | **SP** |
| **PBI-07** | Aumentaci�n de datos (rotaci�n �30�, flip, brillo �20 %, ruido gaussiano, recorte). Split 70/20/10 estratificado. ? 8 000 im�genes en train. | Preparaci�n de Datos | Split sin data leakage (MD5). data.yaml validado | **5 SP** |
| **PBI-08a** | EXP-001: YOLOv8n � epochs=100 � imgsz=640 � batch=16 � seed=42 � pesos COCO | Modelado | best.pt + MLflow run registrado | **4 SP** |
| **PBI-08b** | EXP-002: YOLOv8s � mismas condiciones que EXP-001 | Modelado | best.pt + gr�fica de convergencia | **4 SP** |
| **PBI-08c** | EXP-003: YOLOv8m � imgsz=1280 � batch=8 � mismas condiciones base | Modelado | best.pt + matriz de confusi�n val | **5 SP** |
| **PBI-08d** | Bit�cora EXP: documentar 3 experimentos (ID, hiperpar�metros, m�tricas, decisi�n) | CRISP-ML(Q) | Tabla EXP en Word aprobada por asesor | **3 SP** |

|  |
| --- |
| **S3 � Ingenier�a del Modelo**  03 May � 14 May 2026 � Fase: Ingenier�a del Modelo � 19 SP |

### Objetivo del Sprint � �Por qu�?

Seleccionar el modelo de mayor rendimiento mediante tabla de puntaje ponderado (5 criterios). Optimizar hiperpar�metros (Optuna) si ning�n candidato supera los umbrales DoD. Exportar el modelo final a ONNX. Completa la fase Ingenier�a del Modelo y activa la decisi�n Go/No-Go.

### PBIs del Sprint

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| **ID** | **Descripci�n del PBI** | **Tipo** | **Criterio DoD clave** | **SP** |
| **PBI-09** | Comparaci�n ponderada EXP-001/002/003. Selecci�n del modelo �ptimo. Decisi�n Go/No-Go aprobada por PO. | Modelado | Tabla comparativa + acta Sprint Review firmada | **5 SP** |
| **PBI-10** | Ajuste de hiperpar�metros Optuna (? 20 trials) si ning�n modelo supera umbrales DoD. (Condicional) | Modelado | EXP-004 documentado. Mejora en val set verificable | **8 SP** |
| **PBI-11** | Exportaci�n a ONNX (opset=17). Verificaci�n variaci�n mAP < 0.01. Almacenado en /models/v1/. | MLOps | best.pt y best.onnx con delta < 0.01 | **3 SP** |
| **PBI-11b** | Interfaz web al 100 %: pantallas inicio de lote y monitoreo b�sico. | Frontend | Demo en Sprint Review. SUS aplicado a 1 usuario | **3 SP** |

|  |
| --- |
| **S4 � Evaluaci�n del Modelo**  15 May � 26 May 2026 � Fase: Evaluaci�n del Modelo � 21 SP |

### Objetivo del Sprint � �Por qu�?

Evaluar el modelo seleccionado en el conjunto de test (datos nunca vistos), ejecutar el experimento comparativo sistema vs. clasificaci�n manual y generar los mapas Grad-CAM. Produce las evidencias cient�ficas del Cap�tulo IV.

### PBIs del Sprint

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| **ID** | **Descripci�n del PBI** | **Tipo** | **Criterio DoD clave** | **SP** |
| **PBI-12** | Evaluaci�n formal en test set: P, R, F1, mAP@50, mAP@50:95 por clase. Reporte PDF firmado por asesor. | Evaluaci�n | mAP@50 ? 0.85. Recall broca ? 0.90. PDF aprobado | **5 SP** |
| **PBI-13** | Experimento controlado: sistema vs. ? 3 operarios sobre ? 5 lotes ground truth. t-test ? = 0.05. | Investigaci�n | p-value documentado. Tabla comparativa en informe | **8 SP** |
| **PBI-14** | Grad-CAM: ? 10 im�genes/clase. Validaci�n cualitativa por experto de la cooperativa. | Evaluaci�n | Galer�a PNG + acta de validaci�n del experto | **5 SP** |
| **PBI-14b** | Robustez: 4 escenarios adversos (iluminaci�n, �ngulo, oclusi�n, movimiento). Variaci�n ? 5 %. | Evaluaci�n | Gr�fico de radar por escenario en informe | **3 SP** |

|  |
| --- |
| **S5 � Despliegue del Modelo � Inferencia y Hardware**  27 May � 07 Jun 2026 � Fase: Despliegue del Modelo � 29 SP |

### Objetivo del Sprint � �Por qu�?

Integrar el modelo validado en la API FastAPI con latencia garantizada y completar la integraci�n hardware: Arduino-servo y celda HX711. Al finalizar, el pipeline f�sico completo (c�mara ? modelo ? actuador ? balanza) debe estar operativo.

### PBIs del Sprint

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| **ID** | **Descripci�n del PBI** | **Tipo** | **Criterio DoD clave** | **SP** |
| **PBI-15** | POST /classify/frame: YOLOService ONNX en startup. Latencia P95 ? 500 ms. Persistencia en grain\_detections. | Backend / ML | 50 peticiones: media ? 500 ms. BD actualizada | **8 SP** |
| **PBI-16** | Comunicaci�n serial Arduino: pyserial-asyncio, protocolo byte 'D'/'N', latencia ? 50 ms, reconexi�n autom�tica. | Embedded / HW | Servo activa f�sicamente ? 500 ms post-detecci�n | **8 SP** |
| **PBI-17** | HX711: error ? �2 g. GET /scale/weight. FR = (peso\_buenos/peso\_trillado)�100. | Embedded / HW | 5 pesas de referencia OK. FR calculado correctamente | **8 SP** |
| **PBI-17b** | Test integraci�n E2E: frame ? inferencia ? actuador ? pesaje ? FR. Pipeline completo. | QA / Integraci�n | Video del pipeline completo. Latencia documentada | **5 SP** |

|  |
| --- |
| **S6 � Despliegue del Modelo � Interfaz y Reportes**  08 Jun � 19 Jun 2026 � Fase: Despliegue del Modelo � 21 SP |

### Objetivo del Sprint � �Por qu�?

Completar la interfaz de usuario con dashboard en tiempo real, generaci�n de reportes e historial de lotes. Al finalizar, CoffeeRen es un producto completo demostrable extremo-a-extremo, listo para la validaci�n en campo.

### PBIs del Sprint

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| **ID** | **Descripci�n del PBI** | **Tipo** | **Criterio DoD clave** | **SP** |
| **PBI-18** | Dashboard: stream MJPEG ? 15 FPS, bboxes por clase, contadores WebSocket. SUS ? 70 con operarios. | Frontend | FPS medido en UI. Test con 2 usuarios no t�cnicos | **8 SP** |
| **PBI-19** | Reportes PDF (< 3 s) y CSV. Membrete, m�tricas y gr�fico circular de defectos. | Backend | GET /report/{id}/pdf descarga en ? 3 000 ms | **5 SP** |
| **PBI-20** | Historial de lotes paginado. Filtros fecha/operario. GET /batch/history ? 500 ms con 100 registros. | Backend | Test con 100 lotes. Tiempo documentado | **5 SP** |
| **PBI-20b** | Interfaz web 100 %: integrar dashboard, historial y reportes en flujo de usuario completo. | Frontend | Demo completa en Sprint Review con operario simulado | **3 SP** |

|  |
| --- |
| **S7 � Supervisi�n y Mantenimiento**  20 Jun � 02 Jul 2026 � Fase: Supervisi�n y Mantenimiento � 16 SP |

### Objetivo del Sprint � �Por qu�?

Ejecutar la validaci�n del sistema con operarios reales en la Cooperativa Line Coffee Mara��n (SUS, precisi�n en campo, acta). Implementar el m�dulo de monitoreo de calidad del modelo. Al finalizar el Sprint 7 (2 julio), el sistema operativo est� completo.

### PBIs del Sprint

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| **ID** | **Descripci�n del PBI** | **Tipo** | **Criterio DoD clave** | **SP** |
| **PBI-21** | Validaci�n en campo: ? 3 operarios, ? 2 lotes/operario. Precisi�n ? 85 %. SUS ? 70. Acta firmada por gerente. | Supervisi�n | Informe de validaci�n. Acta institucional. SUS documentado | **8 SP** |
| **PBI-22** | Monitoreo: alerta si precisi�n < 80 % en 3 sesiones consecutivas (data drift). | Supervisi�n | GET /monitoring/quality. Alerta disparada en test | **5 SP** |
| **PBI-22b** | Prueba robustez hardware: desconexi�n Arduino, reinicio API, recuperaci�n ante fallos. | QA | Sistema se recupera en ? 30 s sin p�rdida de datos | **3 SP** |

|  |
| --- |
| **S8 � Documentaci�n y Cierre Acad�mico**  03 Jul � 10 Jul 2026 � Fase: Cierre Acad�mico � 16 SP |

### Objetivo del Sprint � �Por qu�?

Integrar todos los resultados en los Cap�tulos III (Desarrollo del Sistema) y IV (Resultados y Discusi�n) de la tesis, redactar el manual de mantenimiento y obtener la aprobaci�n final del asesor para la presentaci�n del 10 de julio. Cierra el ciclo CRISP-ML(Q).

### PBIs del Sprint

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| **ID** | **Descripci�n del PBI** | **Tipo** | **Criterio DoD clave** | **SP** |
| **PBI-23a** | Cap�tulo III: arquitectura del sistema, pipeline completo, integraci�n hardware-software. Aprobado por asesor. | Documentaci�n | Cap�tulo aprobado con correcciones incorporadas | **5 SP** |
| **PBI-23b** | Cap�tulo IV: m�tricas formales, comparativa estad�stica, Grad-CAM, robustez, validaci�n en campo. APA 7ma ed. | Documentaci�n | Cap�tulo aprobado. Referencias completas | **5 SP** |
| **PBI-24** | Manual de mantenimiento: reentrenamiento semestral, checklist mensual, FAQ 10 problemas. | Supervisi�n | Documento aprobado. Archivado en repositorio | **3 SP** |
| **PBI-24b** | Cierre repositorio: README actualizado, setup guide, documentaci�n t�cnica p�blica. | DevOps | Repositorio listo. CONTRIBUTING disponible | **3 SP** |

# 5. CRONOGRAMA DE EJECUCI�N

Cronograma de los 9 Sprints en el per�odo acad�mico **23 de marzo � 10 de julio de 2026**. El sistema funcional completo (S7) finaliza el **2 de julio**; la documentaci�n acad�mica (S8) concluye el **10 de julio**.

|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Sprint / Nombre** | | **Mar** | | **Abr** | | | | **May** | | | | **Jun** | | | | **Jul** | |
| **Sprint** | **Nombre del Sprint** | 23M | 30M | 6A | 13A | 20A | 27A | 4My | 11M | 18M | 25M | 1Jn | 8Jn | 15J | 22J | 29J | 7Jl |
| **S0** | Comprensi�n del Negocio y los Datos |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| **S1** | Preparaci�n de los Datos |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| **S2** | Preparaci�n de Datos y Modelado |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| **S3** | Ingenier�a del Modelo |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| **S4** | Evaluaci�n del Modelo |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| **S5** | Despliegue del Modelo � Inferencia y Hardware |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| **S6** | Despliegue del Modelo � Interfaz y Reportes |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| **S7** | Supervisi�n y Mantenimiento |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| **S8** | Documentaci�n y Cierre Acad�mico |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| **Sprint** | **Nombre del Sprint** | **Per�odo** | **Fase CRISP-ML(Q)** | **SP** |
| **S0** | Comprensi�n del Negocio y los Datos | 23 Mar � 06 Abr | Comprensi�n del Negocio y los Datos | **17** |
| **S1** | Preparaci�n de los Datos | 07 Abr � 20 Abr | Preparaci�n de los Datos | **29** |
| **S2** | Preparaci�n de Datos y Modelado | 21 Abr � 02 May | Preparaci�n de Datos ? Modelado | **21** |
| **S3** | Ingenier�a del Modelo | 03 May � 14 May | Ingenier�a del Modelo | **19** |
| **S4** | Evaluaci�n del Modelo | 15 May � 26 May | Evaluaci�n del Modelo | **21** |
| **S5** | Despliegue del Modelo � Inferencia y Hardware | 27 May � 07 Jun | Despliegue del Modelo | **29** |
| **S6** | Despliegue del Modelo � Interfaz y Reportes | 08 Jun � 19 Jun | Despliegue del Modelo | **21** |
| **S7** | Supervisi�n y Mantenimiento | 20 Jun � 02 Jul | Supervisi�n y Mantenimiento | **16** |
| **S8** | Documentaci�n y Cierre Acad�mico | 03 Jul � 10 Jul | Cierre Acad�mico | **16** |
| **TOTAL** | **23 Mar � 10 Jul 2026** | **109 d�as calendario** | **6 fases CRISP-ML(Q)** | **189 SP** |

# 6. CEREMONIAS SCRUM Y ARTEFACTOS

## 6.1 Ceremonias por Sprint

|  |  |  |  |
| --- | --- | --- | --- |
| **Ceremonia** | **Frecuencia** | **Duraci�n** | **Prop�sito en CoffeeRen** |
| **Sprint Planning** | Inicio de Sprint | ? 2 h | Seleccionar PBIs, definir Objetivo del Sprint y descomponer en tareas. El PO confirma prioridades. |
| **Daily Scrum** | Diario | ? 15 min | Registro en bit�cora: qu� hice ayer, qu� har� hoy, qu� impedimentos. Actualizaci�n del tablero Kanban. |
| **Sprint Review** | Fin de Sprint | ? 2 h | Demostraci�n en vivo del Incremento al asesor (PO). Verificaci�n del DoD. Ajuste del backlog si aplica. |
| **Sprint Retrospective** | Fin de Sprint | ? 1 h | Mejoras t�cnicas y metodol�gicas. Actualizaci�n Bit�cora EXP con lecciones aprendidas. |

## 6.2 Artefactos y Compromisos

|  |  |  |
| --- | --- | --- |
| **Artefacto Scrum** | **Compromiso** | **Materializaci�n en CoffeeRen** |
| **Product Backlog** | Objetivo del Producto | Este documento. 24 PBIs priorizados. Actualizable en Sprint Review con aprobaci�n del PO. |
| **Sprint Backlog** | Objetivo del Sprint | Tablero Kanban (To Do / In Progress / Done). Disponible en repositorio Git como PROJECT.md. |
| **Increment** | Definici�n de Terminado | Software funcional demostrable + Bit�cora EXP actualizada + m�tricas del DoD verificadas. |
| **Bit�cora EXP (CRISP-ML(Q))** | Reproducibilidad del modelo | Registro por experimento: ID, arquitectura, dataset (tag Git LFS), hiperpar�metros, m�tricas, decisi�n. |

# 7. REFERENCIAS

[1] Schwaber, K. & Sutherland, J. (2020). La Gu�a de Scrum: Las Reglas del Juego. Scrum.org.

[2] Studer, S., Bui, T. B., et al. (2021). Towards CRISP-ML(Q). Machine Learning and Knowledge Extraction, 3(2), 392�413.

[3] Ultralytics. (2024). YOLOv8 Documentation. https://docs.ultralytics.com

[4] INACAL. (2014). NTP-ISO 10470:2014 � Caf� verde: Tabla de referencia de defectos.

[5] INACAL. (2018). NTP 209.027:2018 � Caf� verde: Requisitos.
