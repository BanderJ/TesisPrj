**UNIVERSIDAD CATÓLICA SANTO TORIBIO DE MOGROVEJO**

**FACULTAD DE INGENIERÍA**

**ESCUELA DE INGENIERÍA DE SISTEMAS Y COMPUTACIÓN**



**Sistema automático de clasificación de granos de café verde mediante visión artificial en una cooperativa de Amazonas**

**AUTOR**

**Anderson Jhomar Baca Chuquimanco**

**Chiclayo, 2025**

****

# **INTRODUCCIÓN**

En el Perú la evaluación del rendimiento y la calidad del café es clave para su valor en el mercado y para el ingreso de los productores [1]. Tradicionalmente, este proceso se realiza mediante inspección visual, lo que genera una dependencia del criterio subjetivo del evaluador [2]. Esta situación genera variabilidad, dificulta la estandarización y afecta la confianza en la comercialización [3], además requiere tiempo y experiencia que aumentan el riesgo de errores en la detección de granos defectuosos [4].

En Tailandia, la selección manual de granos de café verde sigue siendo un reto, pues la fatal de detección de los defectos afectan directamente su presencia en el mercado [5]. En el Perú, la clasificación del café presenta limitaciones, como la variabilidad entre operarios, la fatiga, la inconsistencia en la detección de defectos y la baja velocidad de procesamiento, lo que afecta la calidad final del producto [6]. En Amazonas, especialmente en cooperativas de Lonya Grande, la clasificación se realiza manualmente, un proceso lento y subjetivo que genera errores frecuentes, comprometiendo la calidad del producto y debilitando la confianza de los productores en la comercialización [7].

La precisión en la clasificación de los granos de café depende de varios factores, tanto de las características físicas del grano como de las condiciones del proceso de evaluación. Aspectos como el color, el tamaño o la morfología, junto con defectos generados por plagas, humedad o fallas en el secado, afectan directamente la calidad [1], [4], [8]. A ello se suman factores humanos como la experiencia del evaluador, el cansancio visual y la ausencia de protocolos estandarizados, que incrementan la subjetividad y elevan la probabilidad de error en la selección [9].

La dependencia de la inspección visual y manual hace que el proceso sea subjetivo, lento y propenso a errores [3]. Esta situación empeora con la variabilidad en el criterio de los evaluadores, la fatiga y el cansancio derivados de tareas repetitivas [10]. Además, las condiciones laborales exigentes y la deficiente iluminación limitan la detección de defectos [1], [7].

Si la clasificación manual se mantiene como práctica predominante, se seguirá enfrentando baja eficiencia y errores constantes debido a la subjetividad humana, la fatiga laboral y las condiciones deficientes de trabajo [11]. La dificultad para identificar defectos sutiles, como el caracolillo, o daños causados por la broca del café generará pérdidas económicas significativas [9], [5]. Además, la falta de precisión, junto con la limitada adopción de tecnologías y el no cumplimiento de normas estandarizadas, restringirá el acceso a certificaciones y a mercados especializados que demandan estándares internacionales más rigurosos [7].

Diversos estudios han demostrado la eficacia de la visión artificial en la clasificación de café. Yonar y Özaltın [2] alcanzaron un 99.75 % de precisión en el reconocimiento de variedades con arquitecturas como ShuffleNet y MobileNet. Arwatchananukul et al. [5]. lograron un 98.38 % de exactitud y un F1 de 98.24 % en la detección de defectos en café arábica tailandés. Muchtar et al. [12] desarrollaron el dataset USK-Coffee (8,000 imágenes en 4 clases), destacando FocalNet con un 92 % de precisión en la identificación de granos defectuosos. En el contexto peruano, León et al. [8] reportaron un 91.8 % de eficiencia en la detección de la broca del café con YOLOv8m y en otro trabajo Leon et al. [1], lograron una efiencia de 92 % en la identificación de defectos físicos en granos verdes. A nivel local, Llauce y Vera [7] propusieron un clasificador de granos basado en CNN, que obtuvo una exactitud del 95.86%.

Ante esta situación, la investigación se centrará en la Cooperativa Agraria Line Coffee Marañón, ubicada en Lonya Grande (Amazonas), dedicada a la compra, venta y tostado de café. Aunque más del 90 % de sus ingresos depende de la adquisición de grano a productores y socios, el rendimiento y la calidad aún se miden manualmente, un proceso lento, subjetivo y propenso a errores frecuentes. La cooperativa es consciente de que esta dependencia del criterio del evaluador y factores humanos como la fatiga aumentan la probabilidad de error, lo cual es crítico dado que la clasificación manual conlleva un alto riesgo en la detección de defectos sutiles, especialmente los causados por la broca del café, una plaga que puede reducir la producción hasta en un 16 % y causar pérdidas económicas significativas (Ver Anexo N°2).

Por ello, surge la pregunta de investigación: ¿En qué medida un prototipo de clasificación automática basado en visión artificial mejora la precisión, rapidez y objetividad del proceso de clasificación de granos de café verde en una cooperativa de Amazonas?

# **JUSTIFICACIÓN DE LA INVESTIGACIÒN**

Desde el enfoque tecnológico, la visión artificial y el aprendizaje automático han demostrado gran efectividad en la automatización agrícola, alcanzando precisiones superiores al 95% en la detección de defectos en granos [10]. El uso de modelos ligeros como MobileNetV2, ResNet-50 o DenseNet [4], permite obtener alta exactitud con bajo costo computacional, haciendo posible su implementación en cooperativas con recursos limitados. Esta investigación resulta importante porque promueve la aplicación de estas tecnologías para mejorar la evaluación de la calidad y el rendimiento del café, contribuyendo al fortalecimiento tecnológico y productivo del sector cafetalero.

Desde el enfoque social, esta investigación busca mejorar las condiciones de los productores de café, quienes aún dependen de procesos manuales de clasificación lentos, subjetivos y con alto margen de error. En el Perú, más de 223,000 familias viven directamente de este cultivo, y cerca del 85% se encuentran en zonas rurales con acceso limitado a tecnología [13]. En Cajamarca, que representa el 16.5% de la producción nacional [14], la falta de estandarización en la evaluación del grano genera desconfianza y desigualdad en los pagos. La automatización del proceso no pretende reemplazar al trabajador, sino brindar una herramienta de apoyo que reduzca el esfuerzo físico, garantice una valoración más justa y fortalezca la confianza entre productores y cooperativas.

Desde el aspecto económico, esta investigación es relevante porque plantea un sistema de visión artificial de bajo costo, utilizando cámaras accesibles, iluminación LED y microprocesadores eficientes. Esta alternativa busca reducir las pérdidas de hasta un 15% en el rendimiento del café ocasionadas por errores humanos en la clasificación manual [8]. Al reducir el tiempo de evaluación, minimizar el procesamiento y garantizar pagos más justos, la cooperativa incrementará su eficiencia operativa y los productores verán fortalecidos sus ingresos, generando así un impacto positivo en la competitividad del café cajamarquino en mercados nacionales e internacionales.

# **OBJETIVOS DE LA INVESTIGACIÒN**

## **Objetivo general**

* Crear un prototipo de clasificación automática de granos de café verde mediante visión artificial y redes neuronales convolucionales, integrando hardware especializado y procesamiento digital para mejorar la precisión, objetividad y eficiencia del proceso en una cooperativa de Amazonas.

## **Objetivos específicos**

* Identificar las características físicas y los defectos más comunes de los granos de café, como base para definir criterios de clasificación automática.
* Aplicar un modelo de visión artificial apoyado en procesamiento de imágenes y redes neuronales convolucionales que permita identificar y clasificar granos según estándares de calidad.
* Desarrollar la arquitectura física del prototipo, incorporando los componentes de hardware necesarios para la clasificación automática de granos de café.
* Integrar el hardware con el sistema de visión artificial, garantizando la comunicación y sincronización entre los componentes físicos y el modelo de clasificación.
* Validar el rendimiento del sistema mediante la medición de precisión, velocidad de clasificación por grano y robustez ante variaciones de iluminación y condiciones ambientales.

# **REVISIÓN DE LITERATURA**

***Antecedentes***

En Turquía, A. Yonar y Ö. Özaltın [2] señalaron que la clasificación manual de granos de café es lenta, subjetiva y propensa a errores, afectando la consistencia de la calidad y el valor del producto. Para abordar este problema, emplearon cinco arquitecturas de redes neuronales convolucionales preentrenadas (AlexNet, Inception\_v1, MobileNetV2, ShuffleNet y SqueezeNet) sobre un conjunto de 1,600 imágenes de cuatro variedades de café. El modelo ShuffleNet alcanzó una precisión del 99.75 % en pruebas, demostrando su alta eficiencia en la identificación automática de variedades. A diferencia de este estudio, que se centró en la clasificación por tipo de grano, la presente investigación busca automatizar la evaluación del factor de rendimiento, integrando visión artificial para optimizar la calidad y la valoración económica del café.

En Turquía, Korkmaz et al. [4] indicaron que métodos de clasificación tradicionales son lentos, ineficaces, costosos y propensos a errores humanos. Para resolver este desafío, utilizaron técnicas de procesamiento de imágenes basadas en el aprendizaje profundo para la clasificación de especies de granos de café, empleando un conjunto de datos de 1554 imágenes que abarcaba tres tipos comerciales (Starbucks Pike Place, Espresso y Kenia). Compararon el rendimiento de cinco modelos de Redes Neuronales Convolucionales (CNN): Xception, DenseNet201, InceptionV3, InceptionResNetV2 y DenseNet121, logrando que InceptionV3 fuera el modelo más eficaz, al conseguir la mayor precisión de clasificación (93 %) y exactitud (95 %), y demostrando ser el más eficiente computacionalmente con un tiempo de entrenamiento más corto (70,4 minutos). Si bien este estudio aporta una comparación relevante de arquitecturas CNN para la clasificación visual, su enfoque se limitó a la distinción de especies de café y no a la detección de defectos físicos del café verde.

En Tailandia, Arwatchananukul et al. [5] identificaron que la selección manual de granos de café verde arábica sigue siendo un reto para garantizar la calidad, debido a defectos como moho, fermentación o daños por insectos que reducen su valor comercial. Para abordar esta problemática, desarrollaron un modelo de aprendizaje profundo con redes neuronales convolucionales, entrenado con 6,853 imágenes tras aplicar aumento de datos. Entre las arquitecturas evaluadas, MobileNetV3 obtuvo el mejor rendimiento, alcanzando precisiones de hasta 99.84 % en validación cruzada y 88.63 % con datos no vistos. El modelo se implementó en una aplicación web probada por siete agricultores, de los cuales el 71.4 % mostró alta satisfacción. A diferencia de este estudio, el presente trabajo se enfoca en una cooperativa peruana, priorizando el uso de sistemas ligeros y accesibles para contextos rurales con infraestructura tecnológica limitada.

En Indonesia, Muchtar et al. [12] identificaron que la clasificación manual de granos de café genera problemas de calidad por la fatiga del agricultor, los errores humanos y la falta de consistencia en los resultados. Como alternativa, los autores desarrollaron un sistema de detección basado en Edge AI utilizando el dataset USK-Coffee (8,000 imágenes en cuatro clases) y evaluaron diversas arquitecturas, destacando FocalNet con una precisión del 92 % y una pérdida de validación de 0.22. El sistema fue implementado en un dispositivo Jetson Orin Nano con interfaz en Streamlit y mapas de calor Grad-CAM para visualizar defectos en tiempo real. Este estudio demuestra que la inteligencia artificial puede mejorar la eficiencia y reducir errores en la clasificación del café. A diferencia de este trabajo, la presente investigación busca automatizar la determinación del factor de rendimiento, priorizando la transparencia y la valoración justa del producto.

En Brasil, Zanella et al. [15] destacan la necesidad de reemplazar la inspección manual tradicional, que es lenta, subjetiva y propensa a errores, por sistemas automáticos de clasificación de la madurez del fruto de café. Para lograr la clasificación, la investigación empleó el algoritmo YOLOv9 (You Only Look Once), destacando su nueva arquitectura ligera GELAN (Generalized Efficient Layer Aggregation Network), que optimiza el flujo de gradientes para una detección más rápida y precisa, ideal para aplicaciones agrícolas en tiempo real. El modelo se entrenó para identificar y clasificar rápidamente el grado de madurez de los frutos cosechados en cuatro clases: no maduro, maduro-rojo, maduro-amarillo y sobremaduro. Utilizando imágenes capturadas por una cámara, el modelo YOLOv9 logró un nivel de precisión del 99 % y una puntuación F1 del 98,75 con imágenes de 640 px. Este avance apoya el uso de la visión artificial y modelos ligeros para el control de calidad en el café; sin embargo, este estudio se enfoca en el fruto (cerezo) para la cosecha, mientras que la presente investigación se centra en la clasificación de defectos físicos en el café verde y la determinación del factor de rendimiento.

En Perú, León et al. [1] señalaron que los defectos físicos en los granos de café verde afectan directamente su calidad y valor comercial en los mercados internacionales. Dado que la inspección manual es lenta, subjetiva y propensa a errores, desarrollaron un software de visión artificial basado en redes neuronales convolucionales (CNN) implementadas en TensorFlow y Keras para automatizar la detección de defectos. El sistema alcanzó una eficiencia del 92 % en pruebas experimentales, evidenciando su potencial para reducir la variabilidad humana y mejorar la consistencia en la clasificación. A diferencia de este estudio, la presente investigación busca automatizar la determinación del factor de rendimiento, integrando visión artificial no solo para el control de calidad, sino también para optimizar la valorización económica del café en cooperativas locales.

En Perú, León et al. [8] analizaron el impacto de la broca del café (CBB), una de las plagas más destructivas del sector, responsable de pérdidas anuales estimadas en 120 millones de soles y reducciones de hasta 16.3 % en el peso. Para enfrentar este problema, desarrollaron un algoritmo de visión artificial con redes neuronales convolucionales (YOLOv8m) capaz de detectar granos infestados mediante imágenes capturadas con iluminación LED controlada. El modelo, entrenado con técnicas de procesamiento de imágenes en OpenCV y Ultralytics, logró una eficiencia del 91.8 % y permitió la identificación visual de defectos en tiempo real gracias a Grad-CAM y segmentación. Este estudio demuestra que la visión artificial puede sustituir métodos tradicionales como el de flotación, reduciendo tiempo y recursos. A diferencia de este trabajo, la presente investigación busca automatizar la identificación integral de defectos y la determinación del factor de rendimiento, contribuyendo a la estandarización de la calidad y a una valoración más justa del café.

En Perú, Valles-Coral et al. [6] destacan la subjetividad en la selección manual del café cerezo en Latinoamérica, un problema que en la Asociación Valle Grande (San Martín) resultaba en bajos promedios de calidad de taza (≤83 puntos SCAA). Con el objetivo de automatizar el proceso, desarrollaron un prototipo seleccionador que utilizó el procesamiento de Redes Neuronales Convolucionales (CNN) y el algoritmo YOLOv3. Dicho modelo fue entrenado con 24,000 imágenes de granos Catimor clasificados en cinco estados (verde, maduro, pintón, sobre-maduro y seco). Los resultados demostraron la efectividad del prototipo al lograr una precisión del 94.00 % en la clasificación y reducir el tiempo de selección en aproximadamente tres horas por cada 100 kg procesados, permitiendo obtener una calidad de café superior a los 84 puntos SCAA. Este avance confirma el potencial de la visión artificial (CNN y YOLOv3) como una herramienta objetiva y rápida para el control de calidad en el sector. Sin embargo, mientras este estudio se enfocó en perfeccionar la selección del café cerezo por madurez, la presente investigación se centra en la clasificación de defectos físicos en el café verde (grano ya procesado) y la determinación del factor de rendimiento integrando la visión artificial.

En Lambayeque, Perú, Llauce y Vera [7] desarrollaron un sistema inteligente basado en redes neuronales convolucionales para clasificar granos de café normales y defectuosos, con el propósito de optimizar el control de calidad previo a la exportación. El modelo fue entrenado con 11,301 imágenes capturadas bajo condiciones controladas de iluminación y enfoque, alcanzando una exactitud del 95.86 %, una precisión del 97.91 % y una sensibilidad del 93.80 %, lo que evidencia un alto rendimiento en la detección de defectos físicos. El sistema, implementado con una interfaz gráfica, permite la carga, clasificación y almacenamiento de imágenes, además de generar reportes en formato PDF. Este trabajo demuestra que las CNN pueden aplicarse de forma efectiva en el sector cafetalero peruano para reducir errores humanos y agilizar la evaluación de calidad. A diferencia de esa propuesta, la presente investigación no solo busca clasificar los granos, sino también determinar el factor de rendimiento, aportando una herramienta integral para la valoración económica del café en cooperativas locales.

***Bases teóricas***

**Lenguajes de programación en Inteligencia Artificial**

Los lenguajes de programación en inteligencia artificial (IA) permiten construir algoritmos, modelos de aprendizaje automático y sistemas de visión computacional. Su elección influye directamente en la velocidad de desarrollo, el acceso a bibliotecas especializadas, el rendimiento del sistema y su capacidad de escalar [16].

|  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- |
| **comparación de lenguajes de programación** | | | | | |
| **Factores** | **Python** | **R** | **Java** | **C++** | **Julia** |
| **Curva de aprendizaje** | Baja: Sintaxis clara y concisa, la cual es fácil de aprender [16]. | Moderada: Se enfoca en el análisis estadístico, su sintaxis puede ser menos intuitiva para principiantes [16]. | Moderada: Su sintaxis es más verbosa y puede resultar menos legible para principiantes [17]. | Alta: Requiere un mayor conocimiento de conceptos avanzados como punteros y gestión manual de la memoria [18]. | Baja: Posee una sintaxis clara [16], comparable a Python. Fue diseñada para ser simple y amigable. |
| **Enfoque principal** | Es versátil y un referente en Visión Artificial, ML y robótica [16]. Se centra en la simplicidad y flexibilidad [18]. | Fuerte en cálculo estadístico y análisis de datos [16]. | Adecuado para aplicaciones empresariales [17]. | Ideal para sistemas embebidos y aplicaciones que requieren procesamiento en tiempo real o alto rendimiento [18]*.* | Diseñado para cálculos científicos y numéricos de alto rendimiento [16], buscando la velocidad de C con la facilidad de Python [19]. |
| **Librerías** | Extenso: TensorFlow, PyTorch, OpenCV, Scikit-learn, NumPy, Pandas | Enfocado en estadística: Caret, H2O, RandomFores, mlr | Moderado: DL4J, Weka, MOA | Limitado: Dlib, Shark, FANN | En crecimiento: Flux.jl, MLJ.jl, Knet.jl |
| **Aplicaciones destacadas** | Deep learning, visión por computadora, procesamiento de lenguaje natural | Bioestadística, econometría, minería de datos | Backend de IA, big data y analítica empresarial | Robótica, videojuegos, optimización de hardware | Simulación científica, modelado numérico y análisis de alto rendimiento |

**Visión computacional**

La visión computacional es una rama de la inteligencia artificial que permite a los sistemas analizar e interpretar información visual proveniente de imágenes o videos mediante algoritmos de *machine learning* y redes neuronales convolucionales (CNN) [20].A diferencia de la visión humana, estos sistemas aprenden a reconocer patrones, formas y texturas a partir de grandes volúmenes de datos, logrando automatizar tareas visuales con alta precisión y velocidad [21].

Según IBM [20], el mercado global de visión artificial alcanzará 386 mil millones de dólares en 2031, impulsado por la demanda de automatización en sectores industriales, de seguridad y agrícolas. En el ámbito agroindustrial, investigaciones como la de Ghazal et al. [22] demuestran que la visión artificial combinada con deep learning y Edge AI permite clasificar productos y detectar defectos con precisiones superiores al 95 %, incluso en dispositivos de bajo costo.

**El Barrenador del Café (CBB)**

El barrenador del café (Hypothenemus hampei) es considerado la plaga más dañina del cultivo a nivel mundial, afectando la calidad y el rendimiento del grano [23]. Este insecto perfora el fruto del café para alimentarse y depositar sus huevos, provocando pérdidas que pueden alcanzar hasta el 100 % de la producción en infestaciones severas [24]. Su ciclo biológico transcurre dentro del grano, lo que dificulta su control químico y favorece su rápida propagación [23].

En países productores como Colombia, las tasas de infestación varían entre 4.5 % y 14.6 %, afectando directamente el valor comercial del café [25]. Estudios recientes destacan la importancia del manejo integrado de plagas y el uso de herramientas tecnológicas que permitan la detección temprana del daño. En este contexto, la visión artificial se presenta como una alternativa eficaz para identificar defectos causados por la CBB, reduciendo la dependencia de la inspección manual y fortaleciendo el control de calidad en cooperativas cafetaleras.

**Calidad café verde**

La calidad del café verde se define por un conjunto de parámetros físicos, sensoriales y fitosanitarios que determinan su valor comercial y su aceptación en los mercados internacionales. La Norma Técnica Peruana NTP 209.027:2018 establece los requisitos para su clasificación, métodos de ensayo, muestreo, envasado y transporte, buscando uniformizar los criterios de evaluación del producto [26].

El café verde se clasifica en tres grados (1, 2 y 3) según el número de defectos permitidos, el color, la homogeneidad del grano, el aroma y la calidad de taza.

* Grado 1: Presenta la mejor calidad, admitiendo un máximo de 15 defectos
* Grado 2: Puede tener hasta 23 defectos.
* Grado 3: Puede tener hasta 30 defectos.

**Defectos del Café Verde**

La Norma Técnica Peruana NTP-ISO 10470:2014 establece una clasificación internacional de los defectos presentes en el café verde (Ver Anexo 4), aplicable a cualquier especie, variedad o tipo de procesamiento posterior a la cosecha. Esta norma agrupa los defectos en cinco categorías principales, considerando su impacto en la pérdida de masa y en la calidad sensorial del grano. Cada defecto recibe un coeficiente (0) sin impacto, (0,5) impacto moderado y (1) impacto severo.

Entre los defectos más comunes se encuentran los granos negros, vinagres, inmaduros, brocados, partidos, malformados y con restos de cáscara, los cuales influyen negativamente en la valoración comercial del lote. La norma permite cuantificar la incidencia de estos defectos y establecer criterios objetivos de aceptación o rechazo, convirtiéndose en una herramienta clave para el control de calidad y la negociación comercial.

**Rendimiento de café**

Según la Norma Técnica Peruana NTP-ISO 4072:2016, el rendimiento del café se determina mediante un muestreo representativo de los sacos entregados por el productor, utilizando una sonda o herramienta similar para extraer porciones homogéneas del lote. De la muestra obtenida se seleccionan 300 gramos de café verde para su evaluación. En este proceso se identifican y separan los granos defectuosos (dañados, brocados, negros, partidos, etc.), mientras que los granos conformes se pesan nuevamente para calcular el factor de rendimiento, que representa la proporción de café comercializable respecto al total analizado.

Este valor es fundamental, ya que determina el pago al productor y la calidad del lote [27]. Además, la norma establece que la humedad del café verde debe mantenerse entre 10 % y 12.5 % para garantizar estabilidad y evitar deterioro del producto [28].

**Redes Neuronales Convolucionales (CNN)**

Las redes neuronales convolucionales (CNN) son un tipo de red neuronal profunda especializada en el procesamiento y análisis de datos tridimensionales, como imágenes o videos, y constituyen una de las arquitecturas más utilizadas en visión computacional [29]. Estas redes están compuestas por capas interconectadas de nodos (entrada, ocultas y salida), donde cada conexión tiene un peso ajustado durante el entrenamiento. Cuando la salida de un nodo supera un umbral, este se activa y transmite la información a la siguiente capa, permitiendo que la red aprenda de manera jerárquica los patrones visuales [30].

**Arquitecturas ligeras de redes neuronales convolucionales (CNN)**

Las arquitecturas ligeras de redes neuronales convolucionales han sido desarrolladas para optimizar la velocidad de inferencia y reducir el consumo de recursos computacionales, sin sacrificar precisión. Estos modelos son especialmente útiles en dispositivos con capacidad limitada, como edge devices o sistemas embebidos. Entre las más representativas se encuentran MobileNet, ShuffleNet y EfficientNet, las cuales aplican estrategias de reducción de parámetros como convoluciones separables en profundidad, agrupamiento por canales y búsqueda de arquitectura neuronal (Neural Architecture Search).

MobileNet, introducida por Howard et al. [31], emplea convoluciones separables en profundidad para disminuir drásticamente el número de operaciones, manteniendo alta precisión con un tamaño de modelo reducido. ShuffleNet, por su parte, incorpora operaciones de barajado de canales (channel shuffle) que mejoran la eficiencia del flujo de información entre capas [32]. EfficientNet propone un escalado compuesto que balancea la profundidad, anchura y resolución del modelo, logrando una relación óptima entre rendimiento y costo computacional [33].

Estas arquitecturas son ampliamente utilizadas en aplicaciones de visión artificial que requieren procesamiento en tiempo real, como clasificación de imágenes agrícolas o detección de defectos industriales, permitiendo alcanzar precisiones superiores al 90% con tiempos de inferencia reducidos y modelos de pocos megabytes.

**SCRUM**

Scrum es un marco de trabajo liviano que se fundamenta en el empirismo y el pensamiento Lean para generar valor a través de soluciones adaptativas para problemas complejos [34].

I. Teoría y Pilares de Scrum

Scrum emplea un enfoque iterativo e incremental para optimizar la previsibilidad y controlar el riesgo. Se apoya en tres pilares empíricos:

1. Transparencia: El proceso y el trabajo deben ser visibles para todos.

2. Inspección: Los artefactos y el progreso hacia los objetivos deben inspeccionarse con frecuencia.

3. Adaptación: Si algo se desvía, el proceso debe ajustarse lo antes posible para minimizar la desviación.

II. El Scrum Team y su Adaptación al Proyecto

La unidad fundamental de Scrum es el Scrum Team, que es multifuncional (posee todas las habilidades necesarias) y autogestionado (decide internamente quién, cómo y cuándo trabajar). Está compuesto por tres responsabilidades específicas: el Product Owner, el Scrum Master y los Developers.

III. Eventos de Scrum (Sprints)

El Sprint es el corazón de Scrum, un evento de duración fija (un mes o menos) que actúa como el contenedor de todos los demás eventos formales de inspección y adaptación.

IV. Artefactos y Compromisos Clave

Los artefactos representan trabajo o valor y contienen compromisos que refuerzan el empirismo y los valores de Scrum

|  |  |  |
| --- | --- | --- |
| **Artefacto** | **Compromiso** | **Ejemplo** |
| Product Backlog | Objetivo del Producto | Lista priorizada de tareas elaborada en la fase de despliegue e implementación |
| Sprint Backlog | Objetivo del Sprint | El plan de acción para entregar el Incremento en cada ciclo. Los Developers (el autor) deciden cómo descomponer los elementos del Product Backlog en tareas de trabajo más pequeñas. |
| Incremento | Definición de Terminado | El paso preciso y verificable del sistema. Para que se considere "Terminado", debe cumplir las métricas de calidad, tales como Precisión ≥ 85 % y F1-score ≥ 0.85. |

**CRISP-ML(Q)**

La Metodología CRISP-ML(Q) se define como un modelo de proceso estándar para el desarrollo de aplicaciones de Machine Learning (ML) que incorpora una metodología de aseguramiento de calidad (Q). Este modelo se basa en el estándar CRISP-DM, pero expande su alcance para cubrir las especificidades de las aplicaciones de ML, buscando mejorar la eficiencia y la tasa de éxito de los proyectos [35].

La estructura de CRISP-ML(Q) se compone de seis fases a lo largo del ciclo de vida de una aplicación de ML:

1. Comprensión del Negocio y los Datos (Business and Data Understanding): Esta fase inicial combina la definición de objetivos de negocio y ML con la recopilación y verificación de la calidad de los datos para evaluar la viabilidad del proyecto.
2. Preparación de los Datos (Data Preparation): Su propósito es crear un conjunto de datos apto para el modelado, basándose en las experiencias de la fase anterior.
3. Modelado (Modeling): Se centra en crear uno o varios modelos que cumplan con las restricciones y requisitos definidos previamente, evaluando no solo el rendimiento, sino también la robustez, escalabilidad y la demanda de recursos.
4. Evaluación (Evaluation): Aquí se valida el rendimiento del modelo en datos no vistos (conjunto de prueba), se evalua la robustez del modelo con datos erróneos o con ruido y se desarrolla un modelo de aprendizaje automático para la confianza.
5. Despliegue (Deployment): Implica el uso práctico del modelo en el campo de aplicación designado, considerando el hardware de inferencia y asegurando la aceptación del usuario.
6. Monitoreo y Mantenimiento (Monitoring and Maintenance): Es la fase crucial que extiende el modelo respecto a CRISP-DM. Se encarga de gestionar el riesgo de degradación del rendimiento del modelo a lo largo del tiempo debido a cambios en la distribución de los datos (data drift) o el envejecimiento del hardware.

La característica distintiva del modelo es la integración de la metodología de Aseguramiento de Calidad (QA), que sigue un enfoque genérico basado en el "pensamiento basado en riesgos". Para cada tarea, se identifican y mitigan los riesgos técnicos para garantizar la trazabilidad y la calidad durante todo el proceso de desarrollo.

# **MATERIALES Y MÉTODOS**

## **Metodología**

1. **Tipo de investigación**

Esta investigación se enmarca en el enfoque aplicado y tecnológico, ya que busca ofrecer una solución práctica a una problemática real que enfrentan los productores y cooperativas cafetaleras de Amazonas: automatizar la clasificación y evaluación del factor de rendimiento del café verde. Para ello, se desarrollará un sistema inteligente basado en visión artificial y redes neuronales convolucionales (CNN), capaz de identificar y clasificar los granos según su calidad, reduciendo la subjetividad humana y mejorando la precisión del proceso.

De acuerdo con el Manual de Frascati [36], la investigación aplicada se orienta hacia la resolución de problemas prácticos específicos mediante el uso del conocimiento científico y tecnológico. A diferencia de la investigación básica, que busca ampliar el saber teórico, la aplicada tiene un propósito instrumental: generar soluciones utilizables y medibles en contextos reales.

En el marco metodológico, se adoptará una combinación entre SCRUM para la gestión ágil del desarrollo del sistema y CRISP-ML(Q) para la construcción, validación y aseguramiento de calidad del modelo de aprendizaje automático. SCRUM permitirá estructurar el trabajo en sprints iterativos con entregables funcionales al finalizar cada ciclo [34], mientras que CRISP-ML(Q) garantizará una ejecución sistemática y trazable del proceso de machine learning, abarcando desde la comprensión del problema y los datos hasta la monitorización del rendimiento y la mejora continua del modelo [35].

La elección de este tipo y enfoque metodológico responde a que la investigación no solo busca analizar un problema, sino desarrollar una solución tecnológica sostenible y adaptable, que mejore la eficiencia, la objetividad y la transparencia en el proceso de clasificación del café verde. El prototipo propuesto será validado en la Cooperativa Agraria Line Coffee Marañón, empleando métricas cuantitativas que evalúen su precisión, velocidad de clasificación y confiabilidad bajo condiciones reales de trabajo.

1. **Métodos de investigación**

Para el desarrollo de esta investigación se empleará diversos métodos seleccionados en función de la naturaleza del problema, los objetivos planteados y el enfoque tecnológico de la solución. Cada uno de ellos contribuirá a comprender, diseñar, implementar y validar el sistema inteligente de clasificación de granos de café mediante visión artificial.

**TABLA I**

métodos de investigación

|  |  |
| --- | --- |
| **Método** | **Sustento por el cual será empleado en la investigación** |
| **Analítico sintético** | Según Sampieri et al [37] ,Este enfoque permite descomponer un fenómeno complejo en sus elementos esenciales y posteriormente integrarlos en una totalidad coherente. |
| **Hipotético deductivo** | Según Bunge [38], este método consiste en formular hipótesis verificables y contrastarlas mediante la observación o la experimentación. |
| **Inductivo** | Según Bernal [39], el enfoque inductivo analiza los resultados obtenidos del sistema y detectar patrones de clasificación o errores recurrentes. |
| **Cuantitativo** | Según Sampieri et al. [37], el enfoque cuantitativo se basa en la medición numérica de variables y el análisis estadístico de los datos, con el propósito de establecer patrones de comportamiento y validar hipótesis de manera objetiva. |
| **Experimentación** | Según Piattini et al. [40], la experimentación permite validar hipótesis mediante la manipulación de variables y la observación de sus efectos. |

En conjunto, estos métodos se alinean plenamente con los objetivos de la investigación, ya que facilitan el desarrollo, validación y evaluación integral de un sistema inteligente funcional, técnica y económicamente viable. Así, se busca garantizar una solución que no solo optimice la calidad y la objetividad del proceso de clasificación, sino que también genere beneficios económicos sostenibles para los productores de café en Amazonas.

**TABLA II**

|  |  |  |  |
| --- | --- | --- | --- |
| técnicas de investigación | | | |
| **Técnicas** | **Instrumentos** | **Población** | **Propósito** |
| **Revisión documental** | Fichas de revisión bibliográfica (Ver Anexo 5) | Normas técnicas, guías de implementación y documentos especializados sobre café verde. | Analizar, registrar y sistematizar la información técnica para sustentar teóricamente el diseño del sistema |
| **Observación estructurada** | Guía de observación (Ver Anexo 4) | Muestras de granos de café | Registrar las características visuales de los granos |
| **Encuesta estructurada** | Cuestionario (Ver Anexo 6) | Productores de café asociados a la cooperativa y externos | Recoger la percepción sobre el proceso de clasificación manual y el cálculo del factor de rendimiento |
| **Entrevista** | Entrevistar (Ver Anexo 2) | Operarios y encargados de la clasificación del café en la cooperativa | Obtener información sobre el proceso actual de clasificación y cálculo del rendimiento del café |

En conjunto, estas técnicas garantizan una cobertura metodológica coherente con los objetivos de la investigación y con su carácter aplicado, asegurando que los resultados obtenidos sean tanto científicamente válidos como funcionales para la realidad operativa de las cooperativas cafetaleras.

1. **Metodología de desarrollo**

Para el desarrollo del sistema automático de clasificación de granos de café mediante visión artificial, se aplicará una metodología híbrida basada en SCRUM y CRISP-ML(Q), ya que ambas se complementan al integrar la gestión ágil de desarrollo de software con un proceso sistemático y controlado de modelado de aprendizaje automático con aseguramiento de calidad.

**Fases CRISP-ML(Q)**

**Fase 1. Comprensión del negocio y de los datos**

* Definir los objetivos del negocio: automatizar la clasificación del café verde y el cálculo del factor de rendimiento para reducir errores humanos y agilizar el proceso de evaluación en la Cooperativa Agraria Line Coffee Marañón.
* Definir los objetivos del modelo de Machine Learning: desarrollar una CNN ligera capaz de clasificar granos con una precisión ≥ 90 % y latencia ≤ 200 ms.
* Evaluar la situación actual: analizar el método manual de clasificación, las pérdidas promedio (≈ 15 %), recursos tecnológicos disponibles (cámara, sensores, laptop con GPU) y limitaciones del entorno rural.
* Elaborar el plan del proyecto: establecer cronograma, herramientas (Python, TensorFlow, OpenCV, Flask), métricas de desempeño y criterios de éxito técnico y operativo.

**Fase 2. Preparación de los datos**

* Recolectar datos iniciales: capturar imágenes de granos de café proporcionadas por la cooperativa y complementar con bases públicas.
* Describir los datos: definir variables visuales relevantes: color, textura, tamaño, contorno y defectos físicos.
* Explorar los datos: generar histogramas, análisis de correlaciones y distribución de clases (buenos / defectuosos).
* Verificar calidad: descartar imágenes borrosas o sobreexpuestas y comprobar balance entre clases.
* Seleccionar y preparar datos: recorte, redimensionamiento, normalización de píxeles, balanceo y aumento de datos (rotación, brillo).
* Asegurar calidad de datos: documentar trazabilidad, diversidad y consistencia del dataset.

**Fase 3. Modelado**

* Seleccionar técnica de modelado: evaluar arquitecturas CNN ligeras por precisión y eficiencia computacional.
* Definir métricas de calidad: accuracy, precision, recall, F1-score y matriz de confusión.
* Entrenar y optimizar el modelo: aplicar validación cruzada, ajuste de hiperparámetros y transfer learning para mejorar generalización.
* Aplicar conocimiento de dominio: integrar criterios de clasificación según NTP 209.027:2018 y NTP-ISO 10470:2014.
* Documentar experimentos: registrar resultados, parámetros, configuraciones y evolución del modelo en Notebooks.

**Fase 4. Evaluación**

* Validar desempeño: medir métricas con datos no vistos y comparar frente al proceso manual tradicional.
* Evaluar robustez: analizar estabilidad del modelo ante variaciones de luz, ángulo o movimiento del grano.
* Interpretar resultados: utilizar Grad-CAM para visualizar las regiones de atención del modelo.
* Decidir despliegue: si el modelo cumple los umbrales definidos, proceder a su integración; de lo contrario, reentrenar.
* Documentar evaluación: generar reporte técnico con resultados y observaciones.

**Fase 5. Despliegue**

* Integración del modelo entrenado: implementar en una aplicación desarrollada con Flask y OpenCV para clasificar granos en tiempo real.
* Vinculación hardware: conectar cámara global shutter, sensores de carga HX711, banda transportadora y actuadores controlados por Arduino.
* Evaluación en campo: probar el sistema bajo condiciones reales de producción.
* Gestión y gobernanza: mantener versión del modelo y registros de rendimiento.

**Fase 6. Monitoreo y mantenimiento**

* Monitorear desempeño: registrar métricas de precisión y eficiencia del modelo durante el uso continuo.
* Recolectar nuevos datos: incorporar imágenes reales de producción para reentrenar y actualizar el modelo.
* Asegurar calidad continua: aplicar reentrenamiento periódico ante degradación del rendimiento.
* Documentar mantenimiento: mantener registro histórico de mejoras y versiones del modelo.

**Fases SCRUM**

Aplicada durante las fases de despliegue y mantenimiento de CRISP-ML(Q).

**1. Planificación del sprint**

* Definir tareas y objetivos de cada iteración (captura, clasificación, visualización, reporte).
* Priorizar funcionalidades críticas: procesamiento de imágenes, interfaz de usuario y comunicación con hardware (Arduino + sensores).
* Establecer criterios de aceptación y entregables de cada sprint.

**2. Desarrollo iterativo**

* Construir de forma incremental el sistema:
* Módulo de captura: adquisición en tiempo real desde la cámara global shutter.
* Módulo de procesamiento: ejecución del modelo CNN y generación de resultados.
* Módulo de control: envío de señales a actuadores para separar granos buenos / defectuosos.
* Módulo de interfaz: visualización de resultados, peso total y cálculo del factor de rendimiento.
* Realizar pruebas unitarias y funcionales en cada iteración.

**3. Revisión del sprint**

* Evaluar los avances y demostrar funcionalidades implementadas.
* Recoger observaciones del asesor y del personal técnico de la cooperativa.
* Ajustar módulos según retroalimentación recibida.

## **Resultados esperados**

## **5.2.1. Mapeo de objetivos, resultados y verificación**

|  |  |  |
| --- | --- | --- |
| **Objetivo específico 01:**  Identificar las características físicas y los defectos más comunes de los granos de café, como base para definir criterios de clasificación automática. | | |
| Resultados | Medio de verificación | Indicador objetivamente verificable |
| Resultado 1: Catálogo técnico de defectos y características físicas del café verde (forma, tamaño, color, textura, humedad) conforme a la NTP 209.027:2018 y la NTP-ISO 10470:2014. | Documento técnico con la taxonomía visual y tabla de defectos basada en estándares nacionales e internacionales. | Catálogo validado con tipos de defectos clasificados y descritos visualmente. |
| Resultado 2: Base de datos estructurada de imágenes de granos de café etiquetadas según su tipo de defecto. | Dataset propio de la cooperativa Line Coffee Marañón con anotaciones de clase y dataset público de café verde | Dataset compuesto por al menos 5,000 imágenes etiquetadas y verificadas. |
| **Objetivo específico 02:** Aplicar un modelo de visión artificial apoyado en procesamiento de imágenes y redes neuronales convolucionales (CNN) que permita identificar y clasificar granos según estándares de calidad | | |
| Resultados | Medio de verificación | Indicador objetivamente verificable |
| Resultado 1: Modelo CNN entrenado y validado para la clasificación de granos normales y defectuosos. | Archivo del modelo entrenado y reporte de métricas de desempeño | Precisión ≥ 85 %, F1-score ≥ 0.85 y tiempo de inferencia ≤ 1 s por imagen |
| Resultado 2: Documentación del proceso de entrenamiento, ajuste de parámetros y evaluación del modelo. | Bitácora digital (Jupyter Notebook) con registros de experimentación y validación cruzada. | Documentación reproducible que cumpla criterios de calidad del proceso CRISP-ML(Q). |
| **Objetivo específico 3:** Desarrollar la arquitectura física del prototipo, incorporando los componentes de hardware necesarios para la clasificación automática de granos de café. | | |
| Resultados | Medio de verificación | Indicador objetivamente verificable |
| Resultado 01: Estructura física del prototipo ensamblada, incluyendo cámara, sistema de iluminación, faja transportadora y soporte mecánico. | Fotografías del ensamblaje, plano del prototipo, informe de armado. | 100% de los componentes físicos instalados según plano técnico. |
| Resultado 02: Sistema de captura de imágenes operando correctamente dentro del prototipo. | Registro de pruebas de captura, videos y reporte técnico de funcionamiento. | Tasa de captura exitosa ≥ 95% de las imágenes tomadas por la cámara. |
| Resultado 03: Sistema de iluminación calibrado para obtener imágenes con contraste adecuado y mínima interferencia de sombras. | Informe de calibración y reportes de pruebas con variación de luz. | Variación de iluminación controlada ±10% respecto al valor calibrado durante 5 pruebas consecutivas. |
| **Objetivo específico 4:** Integrar el hardware con el sistema de visión artificial, garantizando la comunicación y sincronización entre los componentes físicos y el modelo de clasificación. | | |
| Resultados | Medio de verificación | Indicador objetivamente verificable |
| Resultado 01: Comunicación estable entre la cámara, el sistema de iluminación, la faja transportadora y el módulo de procesamiento digital. | Registro de pruebas de conexión, bitácoras de funcionamiento, capturas de consola y reportes técnicos. | Latencia de comunicación ≤ 200 ms entre captura, procesamiento y registro en al menos 50 iteraciones consecutivas. |
| Resultado 02: Integración funcional del modelo de visión artificial con el flujo de captura, preprocesamiento y clasificación. | Informe técnico del pipeline integrado (captura, procesamiento, predicción). | Flujo de clasificación completo operando con una tasa de éxito ≥ 95 % en pruebas internas controladas. |
| Resultado 03: Sincronización entre el avance del transporte (faja) y el sistema de clasificación para evitar capturas fuera de tiempo. | Reportes de sincronización, tiempo, videos y evidencia de pruebas. | Desalineación ≤ 5 % entre el tiempo esperado y el tiempo real de captura por ciclo. |
| **Objetivo específico 5:** Validar la precisión y eficiencia del sistema mediante pruebas experimentales y comparaciones con el método manual. | | |
| Resultados | Medio de verificación | Indicador objetivamente verificable |
| Resultado 01: Informe comparativo que evalúe la precisión, rapidez y objetividad del sistema automático frente al método manual tradicional. | Documento técnico con análisis estadístico (t-test, ANOVA o equivalentes), tablas de resultados, gráficos comparativos. | F1-Score ≥ 0.85 para la clasificación de defectos.  Diferencia de error ≤ 10% entre sistema automático y método manual.  Reducción ≥ 30% en el tiempo de clasificación por grano. |
| Resultado 02: Prueba experimental del sistema bajo variaciones controladas de iluminación y condiciones ambientales. | Registro de pruebas, mediciones de lux, reporte fotográfico y videos de ejecución. | Variación de precisión ≤ 5% entre condiciones estándar y condiciones adversas.  Estabilidad operativa ≥ 90% durante pruebas ambientales. |
| Resultado 03: Evaluación del sistema por parte de personal técnico de la cooperativa. | Encuestas estructuradas, actas de validación, entrevistas y observaciones de campo. | Participación de al menos 3 evaluadores.  Nivel de satisfacción ≥ 80% respecto a uso, confiabilidad y precisión del sistema. |
| Resultado 04: Reporte final de validación experimental integrando todos los hallazgos y métricas de desempeño. | Documento final, anexos de pruebas y gráficos de rendimiento. | Informe validado y completo según protocolo experimental definido. |

## **5.2.2 Prototipo de la solución**

1. **Funcionalidad de la solución**

El prototipo busca automatizar el proceso de clasificación y evaluación del rendimiento del café verde mediante un sistema de visión artificial basado en redes neuronales convolucionales (CNN). El sistema permite identificar de manera automática los granos con defectos físicos y separarlos de los granos buenos. De este modo, se optimiza el control de calidad en las cooperativas, reduciendo la subjetividad del operario, los errores humanos y el tiempo requerido en la evaluación manual.

El sistema incluirá un módulo de visión, una faja transportadora con actuador de desvío, un sensor de carga para el cálculo del factor de rendimiento, y una interfaz digital que muestra los resultados en tiempo real y genera reportes automáticos.

* Requerimientos funcionales de la solución del proyecto de tesis.
  + Permitir el ingreso de datos de la muestra desde la interfaz del sistema, incluyendo:
    - Peso total de la muestra (por ejemplo, 250 g).
    - Peso del café trillado y tamizado antes de la clasificación (por ejemplo, 230 g).
  + Capturar imágenes en tiempo real mediante una cámara global shutter con iluminación controlada.
  + Detectar y clasificar automáticamente los granos según su estado: buenos o defectuosos (broca, partido, cascarilla, objeto extraño, etc.).
  + Activar un actuador electromecánico o servo para desviar los granos defectuosos hacia una bandeja lateral.
  + Medir el peso final de los granos buenos utilizando una celda de carga de 5 kg conectada al módulo HX711.
  + Calcular automáticamente el factor de rendimiento (FR) utilizando los datos iniciales ingresados por el usuario y el peso final medido por el sistema.
  + Mostrar en tiempo real el conteo de defectos detectados y el avance del proceso.
  + Generar un reporte final automatizado con: fecha, lote, pesos ingresados, peso de granos buenos, factor de rendimiento y desglose de defectos.
  + Guardar el historial de procesos en una base de datos local para trazabilidad y auditoría de calidad.
* Requerimientos no funcionales de la solución del proyecto de tesis.
  + Precisión mínima del modelo IA ≥ 90 % en la clasificación entre granos buenos y defectuosos.
  + Procesamiento en tiempo real con latencia de respuesta ≤ 200 ms entre detección y actuación.
  + Interfaz visual intuitiva, diseñada para operarios sin experiencia técnica.
  + La arquitectura del sistema debe ser modular y flexible, permitiendo incorporar nuevos tipos de defectos, métricas o sensores sin necesidad de rediseñar todo el sistema.
  + Compatibilidad con laptops o mini PC con GPU.
  + El acceso al sistema debe estar protegido mediante autenticación básica (usuario y contraseña).
  + Registro temporal y trazabilidad completa, manteniendo la información de cada lote procesado.

1. **Interfaces**

**Interfaz 1: Interfaz de inicio del sistema**

Esta interfaz permite al usuario acceder al sistema, validando su identidad antes de operar el prototipo. Incluye campos de autenticación básica (usuario y contraseña) y la posibilidad de registrar nuevos operadores autorizados de la cooperativa.

Objetivo: Garantizar el acceso seguro y controlado al sistema por parte de usuarios responsables del proceso de clasificación.



*Fig. 01: Pantalla de inicio de sesión del sistema*

**Interfaz 2: Interfaz de registro de muestra**

En esta ventana, el operario ingresa los datos iniciales del lote, como el código o nombre del productor, el número de tamiz utilizado, el peso total de la muestra y el peso de los granos trillados y tamizados.

Objetivo: Registrar los datos de entrada que servirán de base para el cálculo posterior del factor de rendimiento (FR).



*Fig. 02: Pantalla registro de muestra de granos de café*

**Interfaz 3: Interfaz de monitoreo en tiempo real**

Durante la ejecución, la cámara transmite en directo el flujo de café sobre la faja transportadora. En la pantalla se muestran los granos detectados y clasificados con rectángulos de color (verde = bueno, rojo = defectuoso), junto con indicadores numéricos de conteo y barras de progreso.

Objetivo: Permitir al usuario visualizar en tiempo real el proceso de clasificación y la respuesta del actuador que separa los granos defectuosos.



*Fig. 03: Interfaz de monitoreo en tiempo real*

**Interfaz 4: Interfaz de resultados y reporte**

Una vez finalizada la clasificación, el sistema genera un reporte automático con los siguientes datos:

* + Peso inicial y peso de granos buenos (medido por la celda de carga).
  + Factor de rendimiento (FR) calculado automáticamente.
  + Distribución de defectos detectados (broca, partido, cascarilla, objetos extraños, etc.).
  + Fecha, hora, tamiz utilizado y operador responsable.

Objetivo: Facilitar la evaluación final del lote y documentar los resultados de manera digital y exportable (PDF o CSV).



*Fig. 04: Interfaz de reporte y resultados*

1. **Arquitectura de la solución propuesta**

La arquitectura que se considerará en la solución propuesta es la siguiente:

**

*Fig. 05: Arquitectura de red propuesta*



*Fig. 06: Arquitectura del prototipo del sistema de clasificación automática de granos de café*

La infraestructura tecnología estará conformada por:

* **Cámara global shutter**

Dispositivo de captura óptica que adquiere imágenes en tiempo real del flujo de café sobre la faja transportadora. Evita distorsión por movimiento y proporciona una representación fiel del grano.

* **Sistema de iluminación LED**

Conjunto de luces LED blancas (6500 K) dispuestas en domo o anillo difusor que proporciona iluminación uniforme, minimizando sombras y reflejos en los granos.

* **Faja transportadora**

Estructura mecánica que permite el desplazamiento continuo de los granos bajo la cámara para su análisis visual.

* **Actuador de desvío**

Servo o solenoide de respuesta rápida sincronizado con el modelo de visión encargado de separar automáticamente los granos defectuosos detectados por el sistema.

* **Celda de carga + Módulo HX711**

Sensor de peso encargado de medir el peso final de los granos buenos para el cálculo del factor de rendimiento.

* **Microcontrolador Arduino**

Placa de control que coordina los dispositivos físicos (celda de carga, actuador y sensores). Envía los datos al sistema principal por comunicación serial.

* **Laptop de procesamiento**

Equipo central que ejecuta los módulos de visión artificial, clasificación y generación de reportes.

Características:

* + - Procesador: Intel 9 Ultra 275HX
    - GPU: NVIDIA RTX 50570ti (12 GB VRAM)
    - RAM: 32 GB
    - Sistema operativo: Windows 11
* **Módulo de visión artificial (IA)**

Modelo de redes neuronales convolucionales (CNN) entrenado para identificar y clasificar granos de café en tiempo real según su estado (buenos o defectuosos).

* **Bandejas de clasificación**

Contenedores que reciben los granos después del proceso de clasificación: una para granos defectuosos y otra para los granos buenos que serán pesados.

# **CRONOGRAMA**

El plan sugerido cubre el periodo de enero a diciembre de 2026 e incluye las etapas de preparación, realización, verificación y divulgación del proyecto. Se llevará a cabo utilizando un enfoque combinado de SCRUM y de CRISP-ML(Q), garantizando entregas periódicas y supervisión de la calidad en cada ciclo.

**TABLA III.**

Cronograma de actividades

|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Actividades** | **2026** | | | | | | | | | | | | | | | |
| **Mar.** | **Abr.** | | **May.** | | **Jun.** | | **Jul.** | **Ago.** | **Set.** | | **Oct.** | | **Nov.** | | **Dic.** |
| **2** | **1** | **2** | **1** | **2** | **1** | **2** | **1** | **2** | **1** | **2** | **1** | **2** | **1** | **2** | **1** |
| FASE DE EJECUCIÓN | | | | | | | | | | | | | | | | |
| Análisis de requerimientos funcionales y técnicos | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| Diseño del Product Backlog y planificación de sprints |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| Recolección de imágenes de café y etiquetado |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |
| Preprocesamiento y aumento de datos |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |
| Entrenamiento del modelo CNN |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |
| Evaluación de desempeño del modelo |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |
| Desarrollo de la interfaz gráfica |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |
| Integración del hardware (cámara, iluminación, sensor de carga) |  |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |
| Pruebas funcionales del prototipo |  |  |  |  |  | X | X |  |  |  |  |  |  |  |  |  |
| Comparación con el método manual |  |  |  |  |  |  | X | X |  |  |  |  |  |  |  |  |
| Análisis de resultados y retroalimentación |  |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  |
| FASE DE COMUNICACIÓN | | | | | | | | | | | | | | | | |
| Elaboración de documentación del articulo |  |  |  |  |  |  |  |  | X | X | X | X | X | X |  |  |
| Entrega y defensa del proyecto |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X | X |

La agenda contempla las actividades desde marzo hasta diciembre de 2026, organizadas en dos fases: ejecución y comunicación. Durante los primeros meses se abordará la definición de requerimientos, el diseño del sistema y el entrenamiento del modelo de visión artificial. Posteriormente, se desarrollará la integración del hardware, las pruebas del prototipo en la cooperativa y la evaluación experimental del rendimiento del sistema. Finalmente, se elaborará la documentación técnica y académica para la presentación y sustentación del proyecto.

Esta planificación garantiza un proceso estructurado y coherente con los objetivos de la investigación, asegurando la entrega del prototipo funcional y la obtención de resultados válidos dentro del plazo establecido.

# **PRESUPUESTO**

## **Presupuesto del producto acreditable**

TABLA IV

Presupuesto del producto acreditable

| PARTE PRESUP. | DESCRIPCIÓN | CANT. | UNIDAD DE MEDIDA | PRECIO UNITARIO  (S/.) | PRECIO TOTAL  (S/.) | SUBTOTAL (S/.) |
| --- | --- | --- | --- | --- | --- | --- |
| Código | Módulo de CNN | | | | | 400.00 |
| MCN01 | Módulo de CNN | 1 | UNIDAD | 400.00 | 300.00 |  |
| Código | Módulo de Captura | | | | | 100.00 |
| MC01 | Módulo de Captura | 1 | UNIDAD | 100.00 | 100.00 |  |
| Código | Módulo de Procesamiento y control | | | | | 200.00 |
| MPC01 | Módulo de procesamiento | 1 | UNIDAD | 100.00 | 100.00 |  |
| MPC02 | Módulo de control | 1 | UNIDAD | 100.00 | 100.00 |  |
| Código | Módulo de Usuario | | | | | 300.00 |
| MU01 | Login | 1 | UNIDAD | 50.00 | 50.00 |  |
| MU02 | Gestión de usuarios | 1 | UNIDAD | 50.00 | 50.00 |  |
| MU03 | Reportes | 1 | UNIDAD | 100.00 | 100.00 |  |
| MU04 | Registro de clasificación automática y cálculo del rendimiento | 1 | UNIDAD | 200.00 | 200.00 |  |
| Código | Material de soporte y documentación | | | | | 330.00 |
| MSD01 | Material impreso para manual técnico y guías del sistema | 1 | UNIDAD | 30.00 | 30.00 |  |
| MSD02 | Disco de almacenamiento digital de respaldo | 1 | UNIDAD | 300.00 | 300.00 |  |
| MSD03 | Documentación de tesis | 1 | UNIDAD | 0.00 | 0.00 |  |
| Código | Servicios | | | | | 750.00 |
| SRV01 | Internet | 4 | MES | 75.00 | 300.00 |  |
| SRV02 | Viajes a la Cooperativa Agraria Line Coffee Marañón (transporte y viáticos) | 3 | UNIDAD | 150.00 | 450.00 |  |
| TOTAL PRESUPUESTO DEL PROUCTO ACREDITABLE | | | | | | 2,080.00 |

## **Presupuesto tecnológico**

TABLA V

Presupuesto tecnológico

|  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- |
| PARTE PRESUP. | DESCRIPCIÓN | CANT. | UNIDAD DE MEDIDA | PRECIO UNITARIO  (S/.) | PRECIO TOTAL  (S/.) | SUBTOTAL (S/.) |
| Código | Componentes electrónicos | | | | | 678.00 |
| 2.6.3.2.9.5 | Sensor de carga HX711 + celda de 5 kg | 1 | GLOBAL | 35.00 | 35.00 |  |
| 2.6.3.2.9.4 | Arduboard Uno R3 | 1 | GLOBAL | 60.00 | 60.00 |  |
| 2.6.3.2.9.4 | Driver puente h mmx1508 (mini l298n) | 1 | GLOBAL | 10.00 | 10.00 |  |
| 2.6.3.2.9.4 | Micro servo SG90 1.5Kg | 1 | GLOBAL | 15.00 | 15.00 |  |
| 2.6.3.2.9.4 | Motor DC TT 6V/200RPM eje doble de metal | 1 | GLOBAL | 20.00 | 20.00 |  |
| 2.6.3.2.9.5 | Cámara global shutter | 1 | GLOBAL | 450.00 | 450.00 |  |
| 2.6.3.2.9.4 | PCB | 1 | GLOBAL | 20.00 | 20.00 |  |
| 2.6.3.2.9.4 | Fuente de Poder Switching 12V 5A | 1 | GLOBAL | 50.00 | 50.00 |  |
| 2.6.3.2.9.4 | Cable jumper | 2 | KIT | 10.00 | 20.00 |  |
| Código | Deprecision de equipos tecnologicos | | | | | 4,500.00 |
| 2.6.3.2.3.1 | Laptop | 1 | GLOBAL | 4500.00 | 4500.00 |  |
| Código | Software y herramientas | | | | | 0.00 |
| 2.6.6.1.3.2 | Licencias o entornos de desarrollo (Python, PyTorch, OpenCV, Streamlit, etc.) | 1 | GLOBAL | 0.00 | 0.00 |  |
| TOTAL PRESUPUESTO TECNOLÓGICO | | | | | | 5,178.00 |

## **Resumen presupuestal**

TABLA VI

Resumen presupuestal

|  |  |  |
| --- | --- | --- |
| ITEM | DESCRIPCIÓN PRESUPUESTO | SUBTOTAL (S/.) |
|
| 1 | TOTAL PRESUPUESTO DEL PRODUCTO ACREDITABLE | 2,080.00 |
| 2 | TOTAL PRESUPUESTO TECNOLÓGICO | 5,180.00 |
| TOTAL PRESUPUESTO | | S/. 7,260.00 |

# **COLABORADORES**

TABLA VII

Colaboradores

|  |  |  |  |
| --- | --- | --- | --- |
| N° | COLABORADOR | TIPO DE APOYO | ESPECIFICACIÓN DEL APOYO |
| 1 | Cooperativa Agraria Line Coffee Marañón | Logístico y técnico | Proporcionará muestras de café verde, espacio para la validación experimental y asesoría sobre el proceso de clasificación y cálculo del factor de rendimiento. |
| 2 | Gerente General | Administrativo y coordinación | Autorización del desarrollo del proyecto y coordinación para la ejecución de las pruebas y actividades de campo. |
| 3 | Caficultores | Participación práctica | Aplicación de encuestas para conocer su percepción de la clasificación manual y el uso del sistema automatizado. |
| 4 | Personal encargado de la evaluación del café | Técnico y operativo | Ejecución de pruebas experimentales, identificación de defectos y en la validación comparativa entre el método manual y el sistema automatizado. |

# **REFERENCIAS BIBLIOGRÁFICAS**

[1] R. A. León León, E. E. Atalaya Morales, y S. B. Narvaez Alvarado, «Development of a Software with Artificial Vision to Detect the Physical Defect of the Green Coffee Bean», en *CISCI - Conferencia Iberoam. Sistemas, Cibern. Inform.*, International Institute of Informatics and Cybernetics, 2024, pp. 468-474. doi: 10.54808/CISCI2024.01.468.

[2] A. Yonar y Ö. Özaltın, «Automatic recognition of coffee bean varieties based on pre-trained architectures», *Commun. Fac. Sci. Univ. Ank. Ser. A2-A3 Phys. Sci. Eng.*, vol. 66, n.o 2, pp. 162-175, dic. 2024, doi: 10.33769/aupse.1411294.

[3] R. Neto, P. Sousa, L. Rodrigues Moreira, P. God, y J. Mari, *Enhancing green coffee quality assessment through deep learning*. 2023, p. 89. doi: 10.5753/wvc.2023.27537.

[4] A. Korkmaz, T. Talan, S. Koşunalp, y T. Iliev, «Comparison of deep learning models in automatic classification of coffee bean species», *PeerJ Comput. Sci.*, vol. 11, abr. 2025, doi: 10.7717/peerj-cs.2759.

[5] S. Arwatchananukul, D. Xu, P. Charoenkwan, S. Aung Moon, y R. Saengrayap, «Implementing a deep learning model for defect classification in Thai Arabica green coffee beans», *Smart Agric. Technol.*, vol. 9, p. 15, dic. 2024, doi: 10.1016/j.atech.2024.100680.

[6] M. A. Valles-Coral, C. I. Bernales-Del-Aguila, E. Benavides-Cuvas, y L. Cabanillas-Pardo, «Effectiveness of a cherry coffee sorter prototype with image recognition using machine learning», *Rev. Bras. Cienc. Agrar.*, vol. 18, n.o 1, 2023, doi: 10.5039/AGRARIA.V18I1A2586.

[7] M. Llauce Chapoñan y C. P. Vera Molla, «Clasificación de granos de café, usando un modelo de red neuronal convolucional», Tesis de pregrado, Universidad Nacional Pedro Ruiz Gallo, Lambayeque, Peru, 2025. Accedido: 28 de agosto de 2025. [En línea]. Disponible en: https://repositorio.unprg.edu.pe/handle/20.500.12893/14644

[8] R. A. León León, M. A. R. Davila, B. A. Lara Guerra, A. Manosalva Ruiz, y C. A. Sotomayor Montenegro, «Development of an artificial vision algorithm with neural networks to detect coffee berry borer in coffee beans», *Acta Sci. - Technol.*, vol. 47, n.o 1, 2025, doi: 10.4025/actascitechnol.v47i1.71113.

[9] S. Datta y N. Gupta, «A Novel Approach For the Detection of Tea Leaf Disease Using Deep Neural Network», *Int. Conf. Mach. Learn. Data Eng.*, vol. 218, pp. 2273-2286, ene. 2023, doi: 10.1016/j.procs.2023.01.203.

[10] C. H. Hsia, Y. H. Lee, y C. F. Lai, «An Explainable and Lightweight Deep Convolutional Neural Network for Quality Detection of Green Coffee Beans», *Appl. Sci.*, vol. 12, n.o 21, p. 10966, ene. 2022, doi: 10.3390/app122110966.

[11] P.-H. Chen, S.-Y. Jhong, y C.-H. Hsia, *Semi-Supervised Learning with Attention-Based CNN for Classification of Coffee Beans Defect*. 2022, p. 412. doi: 10.1109/ICCE-Taiwan55306.2022.9869187.

[12] K. Muchtar *et al.*, «Edge AI-Based Detection for Defective Coffee Beans Using Deep Learning and Streamlit Framework», *IEEE Access*, vol. 13, pp. 67977-67992, 2025, doi: 10.1109/ACCESS.2025.3561189.

[13] MIDAGRI, «Café peruano conquista 52 mercados en el mundo y es el sustento de 223 mil familias». [En línea]. Disponible en: https://www.gob.pe/institucion/midagri/noticias/822680-cafe-peruano-conquista-52-mercados-en-el-mundo-y-es-el-sustento-de-223-mil-familias

[14] PRODUCE, «Estudio de investigación sectorial del café», Observatorio PRODUCEmpresarial. [En línea]. Disponible en: https://www.producempresarial.pe/estudio-de-investigacion-sectorial-del-cafe/

[15] M. A. Zanella, M. Barrio-Conde, J. Gomez-Gil, J. M. Aguiar-Perez, M. Á. Pérez-Juárez, y F. M. da Silva, «Deep learning to classify the ripeness of coffee fruit in the mechanized harvesting process», *Sci. Agric.*, vol. 82, 2025, doi: 10.1590/1678-992X-2024-0156.

[16] G. Türkmen, A. Sezen, y G. Şengül, «Comparative Analysis of Programming Languages Utilized in Artificial Intelligence Applications: Features, Performance, and Suitability», *Int. J. Comput. Exp. Sci. Eng.*, vol. 10, n.o 3, pp. 461-469, 2024, doi: 10.22399/ijcesen.342.

[17] AWS, «¿Qué es Java? - Explicación del lenguaje de programación Java», Amazon Web Services, Inc. Accedido: 7 de octubre de 2025. [En línea]. Disponible en: https://aws.amazon.com/es/what-is/java/

[18] A. Rebledano, «Qué es C++ y su importancia en la programación moderna | OpenWebinars», OpenWebinars.net. Accedido: 8 de octubre de 2025. [En línea]. Disponible en: https://openwebinars.net/blog/que-es-cpp/

[19] Julia, «Julia Documentation · The Julia Language», The Julia Project. Accedido: 11 de noviembre de 2025. [En línea]. Disponible en: https://docs.julialang.org/en/v1/

[20] IBM, «¿Qué es la visión artificial?» Accedido: 6 de octubre de 2025. [En línea]. Disponible en: https://www.ibm.com/es-es/think/topics/computer-vision

[21] CEPLAN, «Observatorio Nacional de Prospectiva». [En línea]. Disponible en: https://observatorio.ceplan.gob.pe

[22] S. Ghazal, A. Munir, y W. S. Qureshi, «Computer vision in smart agriculture and precision farming: Techniques and applications», *Artif. Intell. Agric.*, vol. 13, pp. 64-83, sep. 2024, doi: 10.1016/j.aiia.2024.06.004.

[23] N. Moreno-Ramírez, F. J. J. A. Bianchi, M. R. Manzano, F. Martinez-Hofmans, y M. Dicke, «Coffee berry borer infestations and natural enemy communities shaped by altitude, shade, and management practices», *Agric. Ecosyst. Environ.*, vol. 395, p. 109944, ene. 2026, doi: 10.1016/j.agee.2025.109944.

[24] NSW, «Coffee berry borer», DPI Website. Accedido: 7 de octubre de 2025. [En línea]. Disponible en: https://www.dpi.nsw.gov.au/dpi/biosecurity/plant-biosecurity/insect-pests-and-plant-diseases/coffee-berry-borer

[25] M. A. Johnson, C. P. Ruiz-Diaz, N. C. Manoukis, y J. C. Verle Rodrigues, «Coffee Berry Borer (Hypothenemus hampei), a Global Pest of Coffee: Perspectives from Historical and Recent Invasions, and Future Priorities», *Insects*, vol. 11, n.o 12, p. 882, dic. 2020, doi: 10.3390/insects11120882.

[26] INACAL, «GIP 101 - Guía de Implementación de la Norma Técnica Peruana NTP 209.027:2018 CAFÉ. Café verde. Requisitos». Accedido: 7 de octubre de 2025. [En línea]. Disponible en: https://www.gob.pe/institucion/inacal/informes-publicaciones/2187944-gip-101-guia-de-implementacion-de-la-norma-tecnica-peruana-ntp-209-027-2018-cafe-cafe-verde-requisitos

[27] Federación Nacional de Cafeteros de Colombia, «Aprenda a vender su café», Federación Nacional de Cafeteros. [En línea]. Disponible en: https://federaciondecafeteros.org/wp/servicios-al-caficultor/aprenda-a-vender-su-cafe/

[28] INACAL, «GIP 105 - Guía de Implementación de la Norma Técnica Peruana NTP-ISO 8455-2018 Café verde. Guía de almacenamiento y transporte». Accedido: 7 de octubre de 2025. [En línea]. Disponible en: https://www.gob.pe/institucion/inacal/informes-publicaciones/2205811-gip-105-guia-de-implementacion-de-la-norma-tecnica-peruana-ntp-iso-8455-2018-cafe-verde-guia-de-almacenamiento-y-transporte

[29] IBM, «¿Qué son las redes neuronales convolucionales?» Accedido: 7 de octubre de 2025. [En línea]. Disponible en: https://www.ibm.com/es-es/think/topics/convolutional-neural-networks

[30] Y. LeCun, Y. Bengio, y G. Hinton, «Deep learning», *Nature*, vol. 521, n.o 7553, pp. 436-444, may 2015, doi: 10.1038/nature14539.

[31] A. G. Howard *et al.*, «MobileNets: Efficient Convolutional Neural Networks for Mobile Vision Applications», *arXiv*, p. 9, abr. 2017, doi: 10.48550/arXiv.1704.04861.

[32] X. Zhang, X. Zhou, M. Lin, y J. Sun, «ShuffleNet: An Extremely Efficient Convolutional Neural Network for Mobile Devices», *arXiv*, p. 9, dic. 2017, doi: 10.48550/arXiv.1707.01083.

[33] M. Tan y Q. V. Le, «EfficientNet: Rethinking Model Scaling for Convolutional Neural Networks», *arXiv*, p. 11, sep. 2020, doi: 10.48550/arXiv.1905.11946.

[34] K. Schwaber y J. Sutherland, «Scrum Guide | Scrum Guides». [En línea]. Disponible en: https://scrumguides.org/scrum-guide.html

[35] S. Studer *et al.*, «Towards CRISP-ML(Q): A Machine Learning Process Model with Quality Assurance Methodology», *Mach. Learn. Knowl. Extr.*, vol. 3, n.o 2, pp. 392-413, jun. 2021, doi: 10.3390/make3020020.

[36] OECD, *Manual de Frascati 2015*. Fundación Española para la Ciencia y la Tecnología, 2018. Accedido: 7 de octubre de 2025. [En línea]. Disponible en: https://www.oecd.org/es/publications/manual-de-frascati-2015\_9789264310681-es.html

[37] R. Hernández Sampieri, C. Fernández Collado, y P. Baptista Lucio, *Metodología de la investigación*, 6.a ed. España: McGraw Hill España, 2014. Accedido: 26 de octubre de 2025. [En línea]. Disponible en: https://dialnet.unirioja.es/servlet/libro?codigo=775008

[38] M. Bunge, *La ciencia. Su método y su filosofía*. Argentina: Penguin Random House Grupo Editorial Argentina, 2014. [En línea]. Disponible en: https://www.google.com.pe/books/edition/La\_ciencia\_su\_m%C3%A9todo\_y\_su\_filosof%C3%ADa/ypthAgAAQBAJ?hl=es-419&gbpv=0

[39] C. A. Bernal, *Metodología de la investigación*, 3.a ed. Colombia: PEARSON EDUCACIÓN, 2010.

[40] M. Piatiini Velthuis, M. Genero Bocco, y J. Cruz Lemus, *Métodos de investigación en ingeniería del software*. Grupo Editorial RA-MA.

# **ANEXOS**

## **ANEXO N° 01. CARTA DE ACEPTACIÓN DE LA INSTITUCIÓN PARA LA EJECUCIÓN DEL PROYECTO**

****

## **ANEXO N° 02**

**Entrevista dirigida a los encargados de la evaluación y clasificación de granos de café verde**

1. ¿Qué métodos de clasificación de granos de café (manual, semiautomático, automático) se utilizan actualmente en su empresa/cooperativa?
2. ¿Qué porcentaje de la clasificación de granos de café se realiza manualmente?
3. ¿Con qué frecuencia se detectan errores en la clasificación de los granos de café (defectuosos/normales) realizados manualmente?
4. ¿Cómo se evalúa la eficiencia del proceso de clasificación actual?
5. ¿Se han observado efectos negativos en los trabajadores debido a las largas horas de clasificación manual?
6. ¿De qué manera la clasificación actual impacta la calidad del café y su aceptación en los mercados de exportación?
7. ¿Existen desafíos para cumplir con certificaciones de calidad o acceder a mercados especializados debido a la precisión de la clasificación actual?
8. ¿Cuáles son los costos asociados con los errores de clasificación (ej. pérdidas de producto, reprocesamiento)?
9. ¿Qué cambios cree que podrían optimizar la precisión y eficiencia en la clasificación de granos de café?
10. ¿Qué expectativas tiene respecto a la modernización del proceso de clasificación de café?
11. ¿Qué limitaciones del proceso actual cree que deberían resolverse para mejorar la calidad y confiabilidad de la clasificación?

## **ANEXO N° 03**

**Árbol de causas y efectos**



## **ANEXO N° 04**

**Clasificación de defectos café verde (INACAL - NTP-ISO 10470:2014)**



## **ANEXO N° 05**

**Ficha de revisión bibliográfica N°1**

|  |  |
| --- | --- |
| **Tema** | Café verde. Tabla de referencia de defectos. 3ª Edición |
| **Fuente** | Norma Técnica Peruana NTP-ISO 10470:2014 |
| **Acceso** | <https://salalecturavirtual.inacal.gob.pe:8098/datos.aspx?id=28742> |
| **Tipo de documento** | Norma técnica internacional adoptada por INACAL |
| **Entidad** | Instituto Nacional de Calidad (INACAL) – ISO |
| **Año** | Revisada 2019 |
| **Resumen:**  Proporciona una lista estandarizada de defectos presentes en el café verde y los clasifica en cinco categorías principales, asignando un coeficiente de impacto (0, 0.5 o 1) según su influencia en la pérdida de masa o la calidad sensorial. | |
| **Aporte a la investigación:**  Define los criterios objetivos que serán usados para entrenar el modelo de visión artificial y validar la precisión del sistema en la identificación de defectos. | |

**Ficha de revisión bibliográfica N°2**

|  |  |
| --- | --- |
| **Tema** | Implementación de la Norma Técnica Peruana para la calidad del café verde |
| **Fuente** | Instituto Nacional de Calidad (INACAL), GIP 101 – Guía de Implementación de la Norma Técnica Peruana NTP 209.027:2018 CAFÉ. Café verde. Requisitos |
| **Acceso** | <https://goo.su/FG6Gi> |
| **Tipo de documento** | Guía técnica |
| **Entidad** | Instituto Nacional de Calidad (INACAL) |
| **Año** | 2021 |
| **Resumen:**  La guía detalla los criterios de aplicación de la NTP 209.027:2018, orientados a estandarizar los procesos de clasificación y control de calidad del café. Incluye especificaciones sobre los métodos de muestreo y requisitos de humedad. | |
| **Aporte a la investigación:**  Proporciona un marco técnico esencial para definir los parámetros de evaluación y clasificación del café en el sistema automatizado propuesto, asegurando que el prototipo se alinee con los estándares nacionales de calidad establecidos por INACAL | |

## **ANEXO N° 06**

Encuesta dirigida a cafetaleros: Percepción sobre la clasificación y cálculo del rendimiento del café

**Datos generales**

1. **Edad:** \_\_\_\_\_\_ años
2. **Sexo:** ☐ Masculino ☐ Femenino
3. **Años de experiencia en el cultivo de café:** ☐ Menos de 5 ☐ 5–10 ☐ Más de 10
4. **Pertenece a la cooperativa:** ☐ Sí ☐ No

**Sección I: Clasificación del café**

1. ¿Qué aspectos se considera para clasificar su café?
   ☐ Tamaño del grano
   ☐ Color
   ☐ Presencia de defectos (broca, partidos, impurezas, etc.)
   ☐ Humedad
   ☐ Otro: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
2. ¿Qué tan satisfecho está con el método de clasificación actual?
   ☐ Muy satisfecho
   ☐ Satisfecho
   ☐ Poco satisfecho
   ☐ Insatisfecho
3. ¿Considera que la clasificación manual es objetiva y precisa?
   ☐ Sí
   ☐ Parcialmente
   ☐ No
4. En promedio, ¿cuánto tiempo tarda clasificar una muestra de café verde?
   ☐ Menos de 5 minutos
   ☐ Entre 5 y 10 minutos
   ☐ Más de 10 minutos

**Sección II: Cálculo del factor de rendimiento**

1. ¿Conoce cómo se calcula el factor de rendimiento de su café?
   ☐ Sí, completamente
   ☐ Algo, pero no con exactitud
   ☐ No lo conozco
2. ¿Quién realiza el cálculo del rendimiento del café que produce?
   ☐ Usted mismo
   ☐ Personal de la cooperativa
   ☐ Compradores o intermediarios
   ☐ Otro: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
3. ¿Cree que el resultado del rendimiento siempre refleja la calidad real de su café?
   ☐ Sí
   ☐ A veces
   ☐ No
4. ¿Ha tenido desacuerdos o reclamos respecto al pago por rendimiento?
   ☐ Sí
   ☐ No
   Si respondió “Sí”, indique la razón:

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

1. ¿Cuánto confía en el proceso actual de evaluación y pago por rendimiento?
   ☐ Confío plenamente
   ☐ Confío parcialmente
   ☐ No confío

**Sección III: Percepción sobre tecnologías automatizadas**

1. ¿Ha escuchado sobre sistemas automáticos o computarizados el cálculo del rendimiento del café?
   ☐ Sí
   ☐ No
2. ¿Estaría dispuesto a que una máquina clasifique automáticamente su café según su calidad y rendimiento?
   ☐ Sí
   ☐ No
   ☐ Tal vez
3. ¿Qué beneficio esperaría de un sistema automatizado? *(Puede marcar más de uno)*
   ☐ Mayor rapidez
   ☐ Menor error humano
   ☐ Transparencia en el cálculo
   ☐ Pago justo
   ☐ Otro: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
4. ¿Considera que la implementación de una tecnología de este tipo sería útil?
   ☐ Sí
   ☐ No
   ☐ No estoy seguro
5. ¿Estaría dispuesto a participar en pruebas o validaciones de un sistema automatizado de clasificación?
   ☐ Sí
   ☐ No