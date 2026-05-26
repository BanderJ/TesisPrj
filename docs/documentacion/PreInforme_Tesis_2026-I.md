**UNIVERSIDAD CAT�LICA SANTO TORIBIO DE MOGROVEJO**

**FACULTAD DE INGENIER�A**

**ESCUELA DE INGENIER�A DE SISTEMAS Y COMPUTACI�N**

![http://www.usat.edu.pe/images/usat/acerca_usat/escudo.jpg](data:image/jpeg;base64...)

**SISTEMA AUTOM�TICO DE CLASIFICACI�N DE GRANOS DE CAF� VERDE MEDIANTE VISI�N ARTIFICIAL EN UNA COOPERATIVA DE AMAZONAS**

**PRE INFORME DE TESIS**

**PARA EVIDENCIAR LA EJECUCI�N DE TESIS**

**EN EL CURSO DE SEMINARIO DE TESIS I**

**AUTOR**

**ANDERSON JHOMAR BACA CHUQUIMANCO**

**ASESOR**

**Mgtr. WILLIAM ALFREDO NOBLECILLA VINCES**

https://orcid.org/0000-0002-3531-2501

**Chiclayo, 2026**

**INFORMACI�N GENERAL**

1. **Facultad y Escuela**

Facultad de Ingenier�a � Escuela de Ingenier�a de Sistemas y Computaci�n

1. **T�tulo del informe de tesis**

Sistema autom�tico de clasificaci�n de granos de caf� verde mediante visi�n artificial en una cooperativa de Amazonas

1. **Autor(es) y firma(s)**

Anderson Jhomar Baca Chuquimanco

|  |
| --- |
|  |
| **Autor** |

1. **Asesor y firma**

Mgtr. William Alfredo Noblecilla Vinces

|  |
| --- |
|  |
| **Asesor** |

1. **L�nea y �rea de la investigaci�n**

Desarrollo e innovaci�n tecnol�gica - Ingenier�a y Tecnolog�a

1. **Fecha de presentaci�n**

28 de abril de 2026

**�NDICE**

[I. RESULTADOS 4](#_Toc228278185)

[1.1. En base a la metodolog�a utilizada 4](#_Toc228278186)

[1.1.1. Sprint 0: Comprensi�n del Negocio y los Datos 4](#_Toc228278187)

[1.1.2. Sprint 1: Preparaci�n de los Datos 5](#_Toc228278188)

[1.2. En base a los objetivos del proyecto 7](#_Toc228278189)

[1.2.1. Identificar las caracter�sticas f�sicas y los defectos m�s comunes de los granos de caf�, como base para definir criterios de clasificaci�n autom�tica. 7](#_Toc228278190)

[II. REFERENCIAS BIBLIOGR�FICAS 9](#_Toc228278191)

[III. ANEXOS 10](#_Toc228278192)

[3.1. Anexo N� 01. Carta de aceptaci�n para ejecutar la tesis 10](#_Toc228278193)

[3.2. Anexo N� 02. Formato de Encuesta 11](#_Toc228278194)

[3.3. Anexo N� 03. An�lisis de encuesta 13](#_Toc228278195)

[3.4. Anexo N� 04. Datasets P�blicos 14](#_Toc228278196)

[3.5. Anexo N� 05. Dataset Propio 15](#_Toc228278197)

[3.6. Anexo N� 06. Registro de Etiquetado 16](#_Toc228278198)

[3.7. Anexo N� 08. Esquema de la Base de Datos � PostgreSQL 18 con UUIDv7 (Sprint 1) 17](#_Toc228278199)

[3.8. Anexo N� 09. API FastAPI � Swagger UI y Capturas de Interfaz Web v1 (Sprint 1) 18](#_Toc228278200)

# RESULTADOS

## En base a la metodolog�a utilizada

Metodolog�a Scrum y CRISP-ML(Q)

### Sprint 0: Comprensi�n del Negocio y los Datos

Este Sprint se centra en definir los objetivos del negocio y traducirlos en objetivos de aprendizaje autom�tico (*machine learning*), recopilar y verificar la calidad de los datos. Por �ltimo, se eval�a la viabilidad del proyecto.

**Definir el alcance de la aplicaci�n de ML**

Siguiendo las mejores pr�cticas de CRISP-ML(Q), se han fusionado los requisitos del negocio con los requisitos de ML en un paso conjunto.

* **Identificaci�n de desaf�os:** La gerente y el personal t�cnico de la Cooperativa Agraria Line Coffee Mara��n han identificado que el proceso de "an�lisis" (clasificaci�n f�sica de granos) es el principal cuello de botella operativo. Actualmente, este proceso depende del criterio subjetivo y la experiencia del operario, lo que genera inconsistencias.
* **Validaci�n Social:** Mediante encuestas aplicadas a caficultores (ver **Anexo 02**), se evidenci� una disposici�n favorable hacia la tecnolog�a. Los resultados muestran que los productores buscan transparencia en el an�lisis para garantizar un pago justo, y la preferencia de un sistema autom�tico para el an�lisis de los granos de caf� verde (ver **Anexo 03**).

**Criterios de �xito**

Los criterios de �xito se eval�an en tres niveles para garantizar la mensurabilidad y alineaci�n del sistema.

|  |  |
| --- | --- |
| **Nivel** | **Descripci�n y metas** |
| **�xito Empresarial** | Eliminar la subjetividad en la clasificaci�n y reducir los tiempos de espera del productor. Se busca una tasa de aceptaci�n del sistema por parte de los socios superior al 80%. |
| **�xito de ML** | Lograr una precisi�n ? 85% y un F1-score ? 0.85 en la detecci�n de defectos seg�n la norma NTP-ISO 10470:2014. La latencia de respuesta debe ser ? 500 ms. |
| **�xito Econ�mico** | Definido mediante el KPI: "Ahorro de costos operativos por an�lisis automatizado" y "Reducci�n de p�rdidas por errores de valoraci�n manual". |

**Viabilidad**

Se ha evaluado la viabilidad para minimizar el riesgo de fallos prematuros.

* **Social:** Confirmada por la alta disposici�n de los caficultores a confiar en una validaci�n tecnol�gica objetiva frente al m�todo manual subjetivo.
* **T�cnica:** La disponibilidad de muestras reales en la cooperativa asegura el tama�o necesario para el conjunto de entrenamiento.
* **Legal:** El sistema se ajusta a las Normas T�cnicas Peruanas (NTP 209.027:2018 y NTP-ISO 10470:2014).

**Recopilaci�n de Datos**

Se ha finalizado la construcci�n del repositorio de datos utilizando una estrategia h�brida de fuentes externas e internas:

* **Datasets P�blicos:** Se integraron conjuntos de datos de USK-Coffe de Kaggle y Roboflow **(**Ver **Anexo 04)**.
* **Dataset Propio:** Se captur� muestras de granos de caf� verde. Para ello, se cont� con la asesor�a del personal experto de la cooperativa para la identificaci�n precisa de los defectos en granos reales de la zona (Ver **Anexo 05**).
* **Captura y Etiquetado:** Tras la identificaci�n de defectos, se procedi� a la captura fotogr�fica utilizando el prototipo de c�mara y el posterior etiquetado manual de las im�genes, generando una fuente de verdad de alta calidad (Ver **Anexo 06**).

**Verificaci�n de la Calidad de los Datos**

Los datos han sido verificados siguiendo el protocolo de CRISP-ML(Q):

* **An�lisis de Calidad:** Se descartaron im�genes con ruido excesivo o desenfoque que pudieran degradar el modelo.
* **Balanceo:** Se verific� la representaci�n de defectos cr�ticos (broca, agr�o y bola) para asegurar un entrenamiento equitativo.

**Revisi�n de los Resultados del Sprint 0**

Con el Sprint 0 concluido, se dispone de un dataset h�brido verificado y de la aprobaci�n de los interesados. El proyecto se encontr� listo para proceder al Sprint 1: Preparaci�n de los Datos.

### Sprint 1: Preparaci�n de los Datos

Bas�ndose en los resultados del Sprint 0 (Comprensi�n del Negocio y los Datos), el Sprint 1 establece la fundaci�n t�cnica del sistema y genera el conjunto de datos final y optimizado para la fase de modelado (Sprint 2). La preparaci�n de datos en CoffeeRen es una tarea iterativa fundamental para asegurar que el modelo de visi�n artificial sea robusto ante las condiciones variables de la cooperativa.

**Fundaci�n T�cnica del Sistema**

En paralelo a la preparaci�n de los datos, el Sprint 1 estableci� la fundaci�n t�cnica del sistema CoffeeRen:

* **Base de Datos:** PostgreSQL 18 con PKs UUIDv7 en tablas transaccionales e INT en maestra (ver **Anexo 08**).
* **API REST (FastAPI):** Arquitectura Models-Schemas-Services-Routes. Autenticaci�n Argon2id + JWT (ver **Anexo 09**).
* **Interfaz Web v1 (60%):** Pantallas de login y registro de lote. Validaci�n de pesos e ingreso de datos.

**Selecci�n de Datos**

Siguiendo la estrategia h�brida definida en la fase anterior, se ha consolidado el repositorio de datos seleccionando las muestras m�s representativas para el entrenamiento y validaci�n:

* **Integraci�n del Dataset H�brido:** Se seleccionaron 5,000 im�genes de alta calidad provenientes de las fuentes p�blicas (**USK-Coffe** y **Kaggle**) y del dataset capturado en las instalaciones de la cooperativa.
* **Selecci�n de Caracter�sticas:** Dado que se utilizar�n redes neuronales convolucionales (CNN), la selecci�n se centr� en la calidad del p�xel y la representaci�n clara de los defectos f�sicos (broca, agr�o y bola). Se descartaron aquellas im�genes donde el fondo o el ruido visual ocultaran la morfolog�a del grano.
* **Manejo de Clases Desequilibradas:** Se document� la proporci�n de cada defecto para aplicar estrategias de muestreo que eviten el sesgo del modelo hacia el grano "bueno".

**Limpieza de Datos**

La limpieza de datos garantiza que el modelo no aprenda de informaci�n err�nea o ruidosa:

* **Reducci�n de Ruido y Filtrado:** Se procesaron las im�genes capturadas con el prototipo para eliminar artefactos visuales. Se aplic� un filtro de descarte manual para todas las im�genes que presentaran un desenfoque (blur) superior al umbral tolerable para la inferencia de tiempo real.
* **Eliminaci�n de Muestras Inadecuadas:** Se eliminaron aquellas capturas donde la iluminaci�n generara reflejos especulares que distorsionaran el color real del grano, bas�ndose en los requisitos de calidad definidos en la Fase 1.

**Definici�n de Terminado (DoD) del Sprint 1**

Este Sprint se considera concluido al cumplir los siguientes criterios de calidad:

* Dataset balanceado y aumentado disponible en el entorno de desarrollo.

## En base a los objetivos del proyecto

### Identificar las caracter�sticas f�sicas y los defectos m�s comunes de los granos de caf�, como base para definir criterios de clasificaci�n autom�tica.

El cumplimiento de este objetivo se sustenta en el trabajo de campo y la investigaci�n t�cnica detallada en las fases de Comprensi�n del Negocio y de los Datos del proyecto CoffeeRen. Los resultados se consolidaron mediante las siguientes acciones:

**A. Identificaci�n T�cnica y Normativa**

Se realiz� una investigaci�n exhaustiva basada en la normativa nacional e internacional para estandarizar los criterios de clasificaci�n. Se adoptaron los par�metros definidos en la NTP 209.027:2018 y la NTP-ISO 10470:2014, los cuales permitieron catalogar los defectos en grupos de importancia t�cnica y comercial (defectos primarios y secundarios).

**B. Validaci�n con Expertos en el Dominio**

A trav�s de entrevistas y sesiones de trabajo presenciales con la gerencia y el personal t�cnico de la Cooperativa Agraria Line Coffee Mara��n, se identificaron los defectos f�sicos que tienen mayor impacto en el factor de rendimiento de la zona. Como resultado de esta colaboraci�n, se definieron las 12 categor�as de clasificaci�n para el modelo de visi�n artificial, priorizando:

* Granos defectuosos identificados: Broca (da�o por insecto), grano negro, grano agr�o, grano partido/quebrado, cereza seca (bola), entre otros.
* Caracter�sticas f�sicas clave: Se determinaron la colorimetr�a, morfolog�a (tama�o y forma) y textura superficial como los principales descriptores para el entrenamiento del algoritmo.

**C. Construcci�n y Etiquetado del Dataset**

La evidencia f�sica del cumplimiento se manifiesta en la creaci�n de un dataset propio capturado en las instalaciones de la empresa (Anexo 05). El personal experto particip� directamente en la clasificaci�n f�sica de los granos antes de su captura fotogr�fica, asegurando que el etiquetado manual (Anexo 06) represente fielmente la realidad del an�lisis de calidad del caf� verde.

# REFERENCIAS BIBLIOGR�FICAS

[1] Alvitres, V�ctor (2000): Metodolog�a de la investigaci�n cient�fica. Editorial Ciencia, Chiclayo, 2000.

[2] USAT (2024): Reglamento de elaboraci�n y sustentaci�n de trabajos de investigaci�n para optar el t�tulo profesional, Chiclayo, 2024.

[3] Studer, S., Bui, T. B., et al. (2021). Towards CRISP-ML(Q). Machine Learning and Knowledge Extraction, 3(2), 392�413. <https://doi.org/10.3390/make3020020>

[4] Schwaber, K. & Sutherland, J. (2020). La Gu�a de Scrum: Las Reglas del Juego. Scrum.org.

[5] Ultralytics. (2024). YOLOv8 Documentation. https://docs.ultralytics.com

# ANEXOS

## Anexo N� 01. Carta de aceptaci�n para ejecutar la tesis

![](data:image/png;base64...)

## Anexo N� 02. Formato de Encuesta

![](data:image/png;base64...)

**![](data:image/png;base64...)**

## Anexo N� 03. An�lisis de encuesta

Enlace de respuestas de la encuesta: <https://docs.google.com/spreadsheets/d/1se3-avHCY8IAgaYk-d4Ai31De5gO648ElN-ygcsDTrw/edit?usp=sharing>

![Gr�fico de las respuestas de Formularios. T�tulo de la pregunta: 11. �Estar�a dispuesto a que una m�quina clasifique autom�ticamente su caf� seg�n su calidad y rendimiento?. N�mero de respuestas: 10�respuestas.](data:image/png;base64...)

![Gr�fico de las respuestas de Formularios. T�tulo de la pregunta: 12. �Qu� beneficio esperar�a de un sistema automatizado? (Puede marcar m�s de uno). N�mero de respuestas: 10�respuestas.](data:image/png;base64...)

![Gr�fico de las respuestas de Formularios. T�tulo de la pregunta: 13. �Considera que la implementaci�n de una tecnolog�a de este tipo ser�a �til para la cooperativa?. N�mero de respuestas: 10�respuestas.](data:image/png;base64...)![Gr�fico de las respuestas de Formularios. T�tulo de la pregunta: 14. �Estar�a dispuesto a participar en pruebas o validaciones de un sistema automatizado de clasificaci�n?. N�mero de respuestas: 10�respuestas.](data:image/png;base64...)

## Anexo N� 04. Datasets P�blicos

|  |  |  |  |
| --- | --- | --- | --- |
| Fuente | Descripci�n | Imagen referencia | Enlace |
| Kaggle | 8000 im�genes de granos de caf� verde ar�bica. Divididas en 4 categor�as por cada conjunto (train, valid, test) para entrenamiento del modelo | ![](data:image/png;base64...) | <https://www.kaggle.com/datasets/berglingmurphy/coffeebean-usk> |
| Roboflow | 4964 im�genes de granos de caf� verde. Divididas en 3 conjuntos (train, valid, test) para entrenamiento del modelo | ![](data:image/png;base64...) | <https://universe.roboflow.com/new-workspace-cuswj/979-2/dataset/1> |

## Anexo N� 05. Dataset Propio

![](data:image/jpeg;base64...)

Ilustraci�n: Identificaci�n de defectos en la cooperativa

![](data:image/jpeg;base64...)

Ilustraci�n: Clasificaci�n de los defectos de caf� por categor�as

## Anexo N� 06. Registro de Etiquetado

![](data:image/png;base64...)

Ilustraci�n: Etiquetado de im�genes

## Anexo N� 08. Esquema de la Base de Datos � PostgreSQL 18 con UUIDv7 (Sprint 1)

![](data:image/jpeg;base64...)

## Anexo N� 09. API FastAPI � Swagger UI y Capturas de Interfaz Web v1 (Sprint 1)

*![](data:image/png;base64...)*

Ilustraci�n: Arquitectura de carpetas FastAPI

![](data:image/png;base64...)

Ilustraci�n: Swagger UI

![](data:image/png;base64...)

Ilustraci�n: Interfaz Login
