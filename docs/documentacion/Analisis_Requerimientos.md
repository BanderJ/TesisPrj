**UNIVERSIDAD CAT�LICA SANTO TORIBIO DE MOGROVEJO**

**FACULTAD DE INGENIER�A**

**ESCUELA DE INGENIER�A DE SISTEMAS Y COMPUTACI�N**

![Instituto de Estudios Toribianos: Santo Toribio de Mogrovejo Un haz de luz  y lealtad (Himno de la USAT, Chiclayo)](data:image/jpeg;base64...)

**SISTEMA AUTOM�TICO DE CLASIFICACI�N DE GRANOS DE CAF� VERDE MEDIANTE VISI�N ARTIFICIAL EN UNA COOPERATIVA DE AMAZONAS**

**AN�LISIS DE REQUERIMIENTOS**

**AUTOR**

**ANDERSON JHOMAR BACA CHUQUIMANCO**

**Chiclayo, 2026**

# 1. INTRODUCCI�N

El presente documento constituye el An�lisis de Requerimientos del sistema CoffeeRen, desarrollado como trabajo de tesis. CoffeeRen automatiza la clasificaci�n de granos de caf� verde mediante visi�n artificial, reemplazando el proceso manual actualmente empleado en la Cooperativa Agraria Line Coffee Mara��n, con sede en la regi�n Amazonas, Per�.

El documento sigue la estructura metodol�gica de CRISP-ML(Q) [3] para la fase de Comprensi�n del Negocio y los Datos, integrando tres niveles de criterios de �xito: empresarial, de aprendizaje autom�tico y econ�mico. Los requerimientos identificados son la entrada directa al Product Backlog del proyecto y vinculan cada historia de usuario con una necesidad operativa real de la cooperativa.

# 2. COMPRENSI�N DEL NEGOCIO

## 2.1 Contexto Organizacional

La Cooperativa Agraria Line Coffee Mara��n es una organizaci�n productora y exportadora de caf� verde ubicada en Lonya Grande, Utcubamba, Amazonas, Per�. Agrupa a caficultores de la zona que producen variedades de caf� ar�bico con valor comercial en mercados especializados.

El proceso de clasificaci�n de granos, denominado localmente �an�lisis�, es el eslab�n m�s cr�tico de la cadena de valor: determina la calidad del lote, el precio de compra al productor y la aptitud del caf� para exportaci�n. En la actualidad, este proceso es completamente manual, dependiente del criterio subjetivo del operario y de la norma NTP-ISO 10470:2014.

|  |  |
| --- | --- |
| Atributo | Descripci�n |
| Organizaci�n | Cooperativa Agraria Line Coffee Mara��n � Regi�n Amazonas, Per� |
| Producto principal | Caf� verde ar�bico (*Coffea arabica*) para exportaci�n a mercados especializados |
| Proceso impactado | Clasificaci�n f�sica de granos (�an�lisis�): separaci�n de granos buenos y defectuosos seg�n NTP-ISO 10470:2014 |
| Norma aplicable | NTP-ISO 10470:2014 (Caf� verde � Tabla de referencia de defectos) � NTP 209.027:2018 (Caf� verde � Requisitos) |
| Stakeholders clave | Gerente de la cooperativa � Operarios de clasificaci�n � Caficultores socios y externos |
| Unidad de an�lisis | Lote de caf� verde en pergamino. Unidad b�sica: muestra extra�da del lote seg�n NTP 209.027:2018 |

## 2.2 Identificaci�n del Problema Central

La identificaci�n del problema se realiz� mediante entrevistas al personal t�cnico de la cooperativa y encuestas aplicadas a caficultores asociados, siguiendo el protocolo de Comprensi�n del Negocio de CRISP-ML(Q). Los hallazgos revelan un problema multidimensional:

|  |  |  |  |
| --- | --- | --- | --- |
|  | Dimensi�n del problema | Evidencia identificada | Impacto en la cooperativa |
| 1 | Subjetividad en la clasificaci�n | El resultado var�a seg�n el an�lisis que realice el operario. Sin est�ndar reproducible. | Inconsistencia en la valoraci�n del lote. El an�lisis no es preciso. |
| 2 | Lentitud del proceso manual | Clasificar las muestras toma aproximadamente de 5 a 10 min por operario. Alta demanda en temporada de cosecha. | Cuellos de botella operativos. Tiempos de espera prolongados para el productor. |
| 3 | Error en el c�lculo del FR | El Factor de Rendimiento se calcula manualmente, propenso a errores aritm�ticos. | Errores de valoraci�n econ�mica del lote. Posible perjuicio al productor o a la cooperativa. |
| 4 | Desconocimiento del perfil de defectos del lote | No se registra el desglose por tipo de defecto (broca, negro, partido, etc.). | Sin datos para mejorar las pr�cticas agr�colas ni retroalimentar al caficultor. |

## 2.3 Descripci�n del Proceso Actual (AS-IS)

El flujo de trabajo actual de clasificaci�n manual comprende los siguientes pasos secuenciales, todos ejecutados de forma manual sin soporte tecnol�gico:

|  |  |  |  |
| --- | --- | --- | --- |
| Paso | Actividad | Descripci�n | Problema asociado |
| 1 | Recepci�n y pesaje inicial | El operario pesa los sacos de caf� del producto y extrae una muestra para el an�lisis | Registro manual susceptible a error de transcripci�n. |
| 2 | Trillado y tamizado | Se retira el pergamino del grano (trillado) y se aplica un tamiz para separar granos por tama�o. | Proceso est�ndar, bajo riesgo. |
| 3 | Clasificaci�n manual defecto a defecto | El operario extiende los granos sobre una mesa iluminada y separa manualmente los defectuosos por tipo (broca, negro, partido, etc.). | Alta variabilidad. Fatiga visual. Estimaci�n subjetiva. |
| 4 | Pesaje final y c�lculo del FR | Se pesa el conjunto de granos buenos y se calcula el Factor de Rendimiento (FR). | C�lculo manual mediante el uso de una calculadora. Sin automatizaci�n. |
| 5 | Registro en boleta | El resultado, FR y pesos de los granos seg�n etapa, se anota en un cuaderno f�sico sin formato estandarizado. | Sin trazabilidad digital. P�rdida de informaci�n hist�rica. |
| 6 | Comunicaci�n al productor | El operario informa verbalmente al caficultor el resultado del an�lisis y el precio resultante. | Se registra en un Excel. Posibles disputas por falta de evidencia. |

## 2.4 Proceso Propuesto (TO-BE) con CoffeeRen

El sistema CoffeeRen transforma el proceso manual en un flujo automatizado con los siguientes pasos, manteniendo la intervenci�n humana �nicamente en la carga f�sica del lote y la supervisi�n:

|  |  |  |  |
| --- | --- | --- | --- |
| Paso | Actividad | Descripci�n con CoffeeRen | Mejora respecto a AS-IS |
| 1 | Registro digital del lote | El operario ingresa datos del lote en la interfaz web (tipo de grano de caf�, peso total, peso trillado, tamiz). El sistema valida y genera un ID �nico UUIDv7. | Registro estructurado, validado y trazable. Sin error de transcripci�n. |
| 2 | Captura y clasificaci�n en tiempo real | Los granos fluyen sobre la faja transportadora. La c�mara global shutter captura fotogramas que el modelo procesa con latencia ? 500 ms por grano. | Reemplaza clasificaci�n manual. Velocidad y consistencia uniformes. |
| 3 | Actuaci�n mec�nica autom�tica | El servo activado por Arduino desv�a f�sicamente los granos defectuosos hacia una bandeja independiente, sincronizado con la detecci�n. | Separaci�n f�sica objetiva. Sin intervenci�n manual en la clasificaci�n. |
| 4 | Pesaje autom�tico y c�lculo del FR | La celda de carga HX711 mide el peso de los granos buenos. El sistema calcula el FR autom�ticamente. | C�lculo exacto (error ? �5 g). Sin error aritm�tico. Instant�neo. |
| 5 | Monitoreo en vivo y trazabilidad | La interfaz web muestra el stream de video con bounding boxes, contadores de defectos por tipo. Todo se persiste en BD PostgreSQL 18. | Supervisi�n visual continua. Registro autom�tico completo. Auditable. |
| 6 | Generaci�n autom�tica de reporte | Al finalizar el lote, el sistema genera un reporte PDF/CSV con: FR, desglose de defectos por clase y m�tricas del proceso. | Documentaci�n formal entregada al productor. Soporte para auditor�as y exportaci�n. |

# 3. OBJETIVOS DEL NEGOCIO

Los objetivos del negocio se definen en alineaci�n con los criterios de �xito empresarial de CRISP-ML(Q) (Studer et al., 2021, Secci�n 3.1.2). Cada objetivo es medible y verificable mediante el KPI asociado, y representa una necesidad expl�cita de la Cooperativa Agraria Line Coffee Mara��n.

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| OBN | Prioridad | Objetivo de Negocio | KPI de �xito | Justificaci�n operativa |
| OBN-01 | **ALTA** | Eliminar la subjetividad en la clasificaci�n de granos mediante un sistema reproducible y objetivo basado en visi�n artificial. | Variabilidad reducida a 0% (sistema determinista). Resultado id�ntico para la misma muestra en m�ltiples ejecuciones. | La subjetividad actual genera disputas con los productores sobre la valoraci�n del lote. Un sistema determinista garantiza transparencia y confianza. |
| OBN-02 | **ALTA** | Reducir el tiempo de an�lisis de un lote de caf� verde respecto al m�todo manual actual. | Tiempo de clasificaci�n de 300 g de muestra reducido en ? 20% respecto al m�todo manual. | Durante la campa�a de cosecha, la cooperativa procesa m�ltiples lotes por d�a. La reducci�n de tiempos disminuye la espera del productor y aumenta la capacidad operativa. |
| OBN-03 | **ALTA** | Automatizar el c�lculo del Factor de Rendimiento (FR) para eliminar errores aritm�ticos en la valoraci�n econ�mica del lote. | Error en el c�lculo del FR ? �5 % respecto al FR de referencia calculado con instrumentos calibrados. | El FR determina directamente el precio pagado al productor. Un error del 1% sobre un lote de 500 kg puede significar una diferencia de precio sustancial, generando conflictos. |
| OBN-04 | **MEDIA** | Establecer un sistema de trazabilidad digital de cada lote clasificado para soportar auditor�as de calidad y exportaci�n. | 100% de los lotes procesados con registro digital auditado en BD. Reporte PDF generado autom�ticamente por lote. | Los compradores (exportadores) exigen evidencia documental de la calidad de los lotes. La trazabilidad digital abre oportunidades de mercado. |
| OBN-05 | **MEDIA** | Proveer informaci�n desagregada por tipo de defecto (broca, negro, partido, etc.) para retroalimentar las pr�cticas agr�colas del productor. | Reporte con desglose de ? 5 tipos de defecto NTP-ISO 10470:2014 entregado al productor al finalizar el an�lisis del lote. | Conocer qu� defecto predomina en el lote permite al caficultor identificar problemas agr�colas espec�ficos (presencia de broca, manejo postcosecha deficiente, etc.) y corregirlos. |
| OBN-06 | **ALTA** | Lograr una tasa de aceptaci�n del sistema por parte de los operarios y socios de la cooperativa superior al 80%. | Score SUS (System Usability Scale) ? 70 en pruebas con ? 3 operarios reales. Acta de conformidad firmada por la gerencia. | La adopci�n tecnol�gica en entornos rurales depende cr�ticamente de la facilidad de uso. Un sistema rechazado por los operarios no genera valor independientemente de su precisi�n t�cnica. |

# 4. OBJETIVOS DEL MODELO DE MACHINE LEARNING

Los objetivos del modelo se derivan directamente de los objetivos del negocio, traduciendo las necesidades operativas de la cooperativa en criterios t�cnicos medibles. Esta traducci�n sigue el nivel de Criterios de �xito del Aprendizaje Autom�tico de CRISP-ML(Q) (Studer et al., 2021, Secci�n 3.1.2), que exige mensurabilidad y alineaci�n con los objetivos empresariales.

## 4.1 Criterios de �xito del Modelo

|  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- |
| OML | Tipo | Criterio del modelo | Umbral m�nimo aceptable | Umbral objetivo | Vinculaci�n con OBN |
| OML-01 | **Rendimiento** | Precisi�n global del modelo en la prueba (exactitud ponderada sobre las clases de defecto seg�n NTP-ISO 10470:2014 y las detectadas en la cooperativa). | **? 80%** | **? 85%** | OBN-01: reemplaza criterio subjetivo del operario |
| OML-02 | **Rendimiento** | mAP@50 (mean Average Precision con IoU ? 0.50) en el conjunto de test. M�trica est�ndar para evaluaci�n de detectores de objetos. | **? 0.80** | **? 0.85** | OBN-01: calidad de detecci�n verificable y reproducible |
| OML-03 | **Rendimiento** | F1-score ponderado sobre las clases en el test set. Balance entre precisi�n y recall para clases con diferente frecuencia. | **? 0.80** | **? 0.85** | OBN-01, OBN-05: clasificaci�n correcta de m�ltiples tipos de defecto |
| OML-04 | **Recall (cr�tico)** | Recall espec�fico para la clase 'broca' (Hypothenemus hampei). Defecto de mayor impacto econ�mico: un grano con broca contamina el sabor del lote completo y disminuye el peso de los lotes. | **? 0.80** | **? 0.85** | OBN-01, OBN-03: falsos negativos de broca son inaceptables econ�micamente |
| OML-05 | **Latencia** | Tiempo de respuesta total (P95) desde la captura del frame hasta la activaci�n del actuador mec�nico, medido en 50 iteraciones consecutivas. | **? 500 ms** | **? 350 ms** | OBN-02: requisito de operaci�n en tiempo real sobre la faja transportadora |
| OML-06 | **Tama�o** | Tama�o del modelo exportado (formato ONNX) para asegurar compatibilidad con hardware port�til (mini PC con GPU de baja gama). | **? 100 MB** | **? 70 MB** | RNF06: compatibilidad con hardware de campo de la cooperativa |
| OML-07 | **Explicabilidad** | Validaci�n cualitativa de mapas Grad-CAM por experto de la cooperativa: las regiones de atenci�n del modelo deben coincidir con la zona visible del defecto f�sico. | **? 80% de mapas validados** | **? 95%** | OBN-01: transparencia del modelo como condici�n de confianza institucional |

# 5. REQUERIMIENTOS FUNCIONALES (RF)

Los requerimientos funcionales definen las capacidades espec�ficas que el sistema CoffeeRen debe proveer para satisfacer los objetivos del negocio (OBN) y los objetivos del modelo (OML). Cada RF especifica qu� debe hacer el sistema, a qu� actor involucra, y qu� criterio de aceptaci�n permite verificarlo.

|  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- |
| **ID** | **Actor** | **Descripci�n del requerimiento** | **Criterio de aceptaci�n** | **Vinculaci�n** | **Notas t�cnicas** |
| **RF01** | Operario | El sistema permite registrar los datos del lote antes de iniciar la clasificaci�n: c�digo de lote, peso total de la muestra y peso del caf� trillado y tamizado. | POST /batch/start retorna HTTP 201 con UUID del lote. Validaci�n: peso\_trillado ? peso\_total. | OBN-03, OBN-04 | PK UUIDv7 generado autom�ticamente. Estado inicial: 'en\_proceso'. Tabla: batch\_sessions. |
| **RF02** | Sistema | Adquisici�n continua de im�genes del flujo de granos sobre la faja transportadora utilizando una c�mara de obturaci�n global (global shutter) bajo iluminaci�n LED controlada a 5500 K. | Stream de video activo a ? 15 FPS sin p�rdida de frames en condici�n est�ndar de operaci�n. | OML-05, OML-06 | C�mara global shutter evita el efecto rolling shutter en objetos en movimiento. Iluminaci�n difusa. |
| **RF03** | Sistema | Detecci�n y clasificaci�n autom�tica de granos en 7 clases (bueno, broca, negro/vinagre, partido/mordido, cascarilla, inmaduro, bola) mediante el modelo YOLOv8 con bounding box. | mAP@50 ? 0.85 en test set. Recall broca ? 0.90. Latencia inferencia ? 100 ms. | OML-01 a OML-08 | Endpoint: POST /classify/frame. YOLOService carga el modelo ONNX en startup (singleton). Cada detecci�n se persiste en tabla grain\_detections con UUIDv7. |
| **RF04** | Sistema / HW | Activaci�n de servo actuador para desviar f�sicamente los granos defectuosos hacia una bandeja independiente, sincronizado con la detecci�n del modelo ML. | Servo activa dentro de los 500 ms post-detecci�n. Latencia serial Arduino ? 50 ms. Reconexi�n autom�tica si se pierde el puerto. | OBN-02, OML-05 | Comunicaci�n: pyserial-asyncio. Protocolo: byte �nico ('D' = desviar, 'N' = normal). Sketch Arduino con servo por 300 ms. Responde 'OK\n'. |
| **RF05** | Sistema / HW | Medici�n del peso final de los granos clasificados como buenos mediante la celda de carga HX711 conectada al sistema, con calibraci�n verificada. | Error de medici�n ? �2 g respecto a balanza de referencia calibrada. Verificado con 5 pesas de referencia. | OBN-03 | HX711 conectado a Arduino. Endpoint: GET /scale/current. Datos persistidos en tabla scale\_readings con timestamp UUIDv7. |
| **RF06** | Sistema | C�lculo autom�tico del Factor de Rendimiento (FR) al finalizar el lote usando los datos de RF01 (peso trillado) y RF05 (peso buenos): FR = (peso\_buenos / peso\_trillado) � 100. | FR calculado con precisi�n de 2 decimales. Verificado contra c�lculo manual de referencia: error ? �0.1%. | OBN-03 | PATCH /batch/{id}/finalize calcula y almacena el FR en la tabla reports con UUIDv7. |
| **RF07** | Operario | Visualizaci�n en tiempo real del proceso de clasificaci�n: stream de video con bounding boxes coloreados por clase, contadores de detecciones por tipo de defecto y Factor de Rendimiento parcial. | Stream ? 15 FPS. Contadores actualizados con latencia ? 1 s. SUS ? 70 con operarios reales. | OBN-06, OML-05 | Stream MJPEG v�a FastAPI StreamingResponse + WebSocket para contadores. Interfaz debe ser usable sin formaci�n t�cnica (RNF07). |
| **RF08** | Administrador | Generaci�n autom�tica de reportes exportables en formato PDF y CSV al finalizar cada lote, con: c�digo de lote, operario, fecha, pesos, FR, conteo total de buenos/defectuosos y desglose por tipo de defecto. | Reporte PDF generado en ? 3 s. CSV con headers correctos. Almacenado en BD con ruta del archivo. | OBN-04, OBN-05 | GET /report/{id}/pdf y GET /report/{id}/csv. ReportLab para PDF con membrete institucional. Ruta almacenada en tabla reports. |
| **RF09** | Administrador | Almacenamiento de todos los procesos de clasificaci�n en la base de datos local para auditor�as de calidad. Historial de lotes paginado consultable por fecha y operario. | 0 registros hu�rfanos. GET /batch/history retorna lista paginada en ? 500 ms con 100 lotes en BD. | OBN-04 | Tablas: batch\_sessions (UUIDv7), grain\_detections (UUIDv7), scale\_readings, reports. �ndice en created\_at para rendimiento de consultas. |

# 6. REQUERIMIENTOS NO FUNCIONALES (RNF)

Los requerimientos no funcionales definen las restricciones de calidad, rendimiento, seguridad y arquitectura del sistema. Son las condiciones bajo las cuales el sistema debe operar, independientemente de la funcionalidad espec�fica.

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| ID | Categor�a | Descripci�n | M�trica verificable | Justificaci�n t�cnica |
| RNF01 | **Rendimiento ML** | El modelo de IA debe alcanzar una precisi�n m�nima del 85% y mAP@50 ? 0.85 en la detecci�n y clasificaci�n de defectos de granos de caf� verde en el conjunto de test. | Reporte de m�tricas firmado por asesor. mAP@50 ? 0.85. Recall broca ? 0.90. | Umbral definido en los criterios de �xito ML de CRISP-ML(Q) y alineado al OBN-01. Por debajo de este umbral, el sistema no supera la clasificaci�n manual experta. |
| RNF02 | **Latencia** | El tiempo de respuesta total (captura ? detecci�n ? actuaci�n mec�nica) debe ser ? 500 ms para garantizar la correcta desviaci�n del grano defectuoso sobre la faja transportadora. | Medida en 50 iteraciones consecutivas. P80 ? 500 ms. Benchmarking documentado. | La velocidad de la faja transportadora determina el margen temporal disponible para la actuaci�n. A 5 cm/s, un grano tarda ~600 ms en pasar el actuador: el sistema debe actuar antes. |
| RNF03 | **Arquitectura BD** | La base de datos se implementa en PostgreSQL 18. Las tablas transaccionales (batch\_sessions, grain\_detections, reports) usan PKs UUIDv7. Las tablas maestras (users, defect\_types) usan PKs de tipo INT. | alembic upgrade head sin errores. SELECT id FROM batch\_sessions: tipo uuid. SELECT id FROM users: tipo int4. | UUIDv7 incluye timestamp en los bits m�s significativos, garantizando orden cronol�gico y facilitando consultas temporales sin �ndices adicionales. |
| RNF04 | **Seguridad** | El acceso al sistema requiere autenticaci�n con usuario y contrase�a. Las contrase�as se almacenan usando el algoritmo Argon2id. La sesi�n se gestiona con JWT con expiraci�n de 8 horas. Bloqueo tras 3 intentos fallidos. | POST /auth/login: HTTP 200 con token v�lido.  Token sin autenticar en rutas protegidas: HTTP 401. | Argon2id es el algoritmo ganador del Password Hashing Competition 2015, recomendado por OWASP para resistencia a ataques de fuerza bruta por GPU/ASIC. |
| RNF05 | **Modularidad** | El software sigue la arquitectura Models-Services-Routes (FastAPI). Permite agregar nuevas clases de defecto, sensores o m�dulos sin redise�ar la capa de negocio existente. | 0 l�gica de negocio en capa Routes. 0 queries SQL en capa Services. Code review aprobado por asesor. | La separaci�n de capas reduce el acoplamiento. Agregar una nueva clase de defecto solo requiere actualizar el modelo ML y la tabla defect\_types, sin modificar la API ni el frontend. |
| RNF06 | **Hardware** | El sistema debe ser ejecutable en equipos port�tiles equipados con GPU dedicada (m�nimo 6 GB VRAM) para soportar la inferencia del modelo YOLOv8. Debe ser compatible con ONNX Runtime para CPU si no hay GPU. | Inferencia en GPU RTX 5070 Ti: latencia ? 100 ms/frame. Inferencia en CPU (ONNX): latencia ? 500 ms/frame. | La cooperativa opera en campo. El sistema debe poder funcionar sin conexi�n a internet y con hardware de costo accesible para la instituci�n. |
| RNF07 | **Usabilidad** | La interfaz de usuario debe ser accesible para operarios sin formaci�n t�cnica en computaci�n. El flujo principal (inicio de lote ? clasificaci�n ? reporte) debe completarse sin asistencia tras una sesi�n de entrenamiento de ? 30 min. | Score SUS ? 70 (�Aceptable� seg�n escala SUS). Validado con ? 3 operarios reales de la cooperativa. | El SUS (System Usability Scale, Brooke 1996) es el est�ndar internacional para evaluaci�n r�pida de usabilidad. Un score ? 70 corresponde a �Bueno� en la escala adjective rating. |

# 7. VIABILIDAD DEL PROYECTO

La evaluaci�n de viabilidad sigue el marco de CRISP-ML(Q) Secci�n 3.1.3, que exige comprobar la viabilidad t�cnica, legal, social y de datos antes de proceder con el desarrollo.

|  |  |  |  |
| --- | --- | --- | --- |
| Dimensi�n | Evaluaci�n | Resultado | Evidencia |
| Viabilidad social | Disposici�n de los caficultores y operarios a adoptar la tecnolog�a. | **VIABLE** | > 80% de caficultores encuestados (N ? 15) manifiestan preferencia por validaci�n tecnol�gica objetiva (Encuesta, Anexo 02�03 del Pre-informe). |
| Viabilidad t�cnica | Disponibilidad del stack tecnol�gico y hardware requerido. | **VIABLE** | YOLO, FastAPI, PostgreSQL 18, Arduino, OpenCV y RTX 5070 Ti disponibles. Trabajos similares en clasificaci�n de granos de caf� con YOLO confirman la aplicabilidad. |
| Viabilidad de datos | Disponibilidad de datos suficientes y de calidad para entrenar el modelo. | **VIABLE** | Dataset h�brido de 5 000+ im�genes consolidado (USK-Coffee, Kaggle + dataset propio). Etiquetado con IRA ? 85% validado por experto de la cooperativa (Sprint 1). |
| Viabilidad legal | Cumplimiento normativo nacional. | **VIABLE** | El sistema se ajusta a NTP-ISO 10470:2014 y NTP 209.027:2018. Carta de aceptaci�n firmada por la gerencia de la cooperativa (Anexo 01 del Pre-informe). |
| Viabilidad econ�mica | KPI econ�mico del sistema. | **POSITIVO** | KPI definido: Ahorro de costos operativos por an�lisis automatizado y Reducci�n de p�rdidas por errores de valoraci�n. Estimaci�n preliminar: reducci�n > 20% en tiempo de an�lisis. |

# 8. REFERENCIAS NORMATIVAS Y BIBLIOGR�FICAS

[1] INACAL. (2014). NTP-ISO 10470:2014. Caf� verde � Tabla de referencia de defectos. Instituto Nacional de Calidad, Per�.

[2] INACAL. (2018). NTP 209.027:2018. Caf� verde � Requisitos. Instituto Nacional de Calidad, Per�.

[3] Studer, S., Bui, T. B., Drescher, C., Hanuschkin, A., Winkler, L., Peters, S., & M�ller, K.-R. (2021). Towards CRISP-ML(Q): A Machine Learning Process Model with Quality Assurance Methodology. Machine Learning and Knowledge Extraction, 3(2), 392�413. https://doi.org/10.3390/make3020020

[4] Ultralytics. (2024). YOLOv8 Documentation. https://docs.ultralytics.com
