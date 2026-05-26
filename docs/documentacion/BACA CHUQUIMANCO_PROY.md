**UNIVERSIDAD CAT�LICA SANTO TORIBIO DE MOGROVEJO**

**FACULTAD DE INGENIER�A**

**ESCUELA DE INGENIER�A DE SISTEMAS Y COMPUTACI�N**

![http://www.usat.edu.pe/images/usat/acerca_usat/escudo.jpg](data:image/jpeg;base64...)

**Sistema autom�tico de clasificaci�n de granos de caf� verde mediante visi�n artificial en una cooperativa de Amazonas**

**AUTOR**

**Anderson Jhomar Baca Chuquimanco**

**Chiclayo, 2025**

**![](data:image/png;base64...)**

# **INTRODUCCI�N**

En el Per� la evaluaci�n del rendimiento y la calidad del caf� es clave para su valor en el mercado y para el ingreso de los productores [1]. Tradicionalmente, este proceso se realiza mediante inspecci�n visual, lo que genera una dependencia del criterio subjetivo del evaluador [2]. Esta situaci�n genera variabilidad, dificulta la estandarizaci�n y afecta la confianza en la comercializaci�n [3], adem�s requiere tiempo y experiencia que aumentan el riesgo de errores en la detecci�n de granos defectuosos [4].

En Tailandia, la selecci�n manual de granos de caf� verde sigue siendo un reto, pues la fatal de detecci�n de los defectos afectan directamente su presencia en el mercado [5]. En el Per�, la clasificaci�n del caf� presenta limitaciones, como la variabilidad entre operarios, la fatiga, la inconsistencia en la detecci�n de defectos y la baja velocidad de procesamiento, lo que afecta la calidad final del producto [6]. En Amazonas, especialmente en cooperativas de Lonya Grande, la clasificaci�n se realiza manualmente, un proceso lento y subjetivo que genera errores frecuentes, comprometiendo la calidad del producto y debilitando la confianza de los productores en la comercializaci�n [7].

La precisi�n en la clasificaci�n de los granos de caf� depende de varios factores, tanto de las caracter�sticas f�sicas del grano como de las condiciones del proceso de evaluaci�n. Aspectos como el color, el tama�o o la morfolog�a, junto con defectos generados por plagas, humedad o fallas en el secado, afectan directamente la calidad [1], [4], [8]. A ello se suman factores humanos como la experiencia del evaluador, el cansancio visual y la ausencia de protocolos estandarizados, que incrementan la subjetividad y elevan la probabilidad de error en la selecci�n [9].

La dependencia de la inspecci�n visual y manual hace que el proceso sea subjetivo, lento y propenso a errores [3]. Esta situaci�n empeora con la variabilidad en el criterio de los evaluadores, la fatiga y el cansancio derivados de tareas repetitivas [10]. Adem�s, las condiciones laborales exigentes y la deficiente iluminaci�n limitan la detecci�n de defectos [1], [7].

Si la clasificaci�n manual se mantiene como pr�ctica predominante, se seguir� enfrentando baja eficiencia y errores constantes debido a la subjetividad humana, la fatiga laboral y las condiciones deficientes de trabajo [11]. La dificultad para identificar defectos sutiles, como el caracolillo, o da�os causados por la broca del caf� generar� p�rdidas econ�micas significativas [9], [5]. Adem�s, la falta de precisi�n, junto con la limitada adopci�n de tecnolog�as y el no cumplimiento de normas estandarizadas, restringir� el acceso a certificaciones y a mercados especializados que demandan est�ndares internacionales m�s rigurosos [7].

Diversos estudios han demostrado la eficacia de la visi�n artificial en la clasificaci�n de caf�. Yonar y �zalt?n [2] alcanzaron un 99.75 % de precisi�n en el reconocimiento de variedades con arquitecturas como ShuffleNet y MobileNet. Arwatchananukul et al. [5]. lograron un 98.38 % de exactitud y un F1 de 98.24 % en la detecci�n de defectos en caf� ar�bica tailand�s. Muchtar et al. [12] desarrollaron el dataset USK-Coffee (8,000 im�genes en 4 clases), destacando FocalNet con un 92 % de precisi�n en la identificaci�n de granos defectuosos. En el contexto peruano, Le�n et al. [8] reportaron un 91.8 % de eficiencia en la detecci�n de la broca del caf� con YOLOv8m y en otro trabajo Leon et al. [1], lograron una efiencia de 92 % en la identificaci�n de defectos f�sicos en granos verdes. A nivel local, Llauce y Vera [7] propusieron un clasificador de granos basado en CNN, que obtuvo una exactitud del 95.86%.

Ante esta situaci�n, la investigaci�n se centrar� en la Cooperativa Agraria Line Coffee Mara��n, ubicada en Lonya Grande (Amazonas), dedicada a la compra, venta y tostado de caf�. Aunque m�s del 90 % de sus ingresos depende de la adquisici�n de grano a productores y socios, el rendimiento y la calidad a�n se miden manualmente, un proceso lento, subjetivo y propenso a errores frecuentes. La cooperativa es consciente de que esta dependencia del criterio del evaluador y factores humanos como la fatiga aumentan la probabilidad de error, lo cual es cr�tico dado que la clasificaci�n manual conlleva un alto riesgo en la detecci�n de defectos sutiles, especialmente los causados por la broca del caf�, una plaga que puede reducir la producci�n hasta en un 16 % y causar p�rdidas econ�micas significativas (Ver Anexo N�2).

Por ello, surge la pregunta de investigaci�n: �En qu� medida un prototipo de clasificaci�n autom�tica basado en visi�n artificial mejora la precisi�n, rapidez y objetividad del proceso de clasificaci�n de granos de caf� verde en una cooperativa de Amazonas?

# **JUSTIFICACI�N DE LA INVESTIGACI�N**

Desde el enfoque tecnol�gico, la visi�n artificial y el aprendizaje autom�tico han demostrado gran efectividad en la automatizaci�n agr�cola, alcanzando precisiones superiores al 95% en la detecci�n de defectos en granos [10]. El uso de modelos ligeros como MobileNetV2, ResNet-50 o DenseNet [4], permite obtener alta exactitud con bajo costo computacional, haciendo posible su implementaci�n en cooperativas con recursos limitados. Esta investigaci�n resulta importante porque promueve la aplicaci�n de estas tecnolog�as para mejorar la evaluaci�n de la calidad y el rendimiento del caf�, contribuyendo al fortalecimiento tecnol�gico y productivo del sector cafetalero.

Desde el enfoque social, esta investigaci�n busca mejorar las condiciones de los productores de caf�, quienes a�n dependen de procesos manuales de clasificaci�n lentos, subjetivos y con alto margen de error. En el Per�, m�s de 223,000 familias viven directamente de este cultivo, y cerca del 85% se encuentran en zonas rurales con acceso limitado a tecnolog�a [13]. En Cajamarca, que representa el 16.5% de la producci�n nacional [14], la falta de estandarizaci�n en la evaluaci�n del grano genera desconfianza y desigualdad en los pagos. La automatizaci�n del proceso no pretende reemplazar al trabajador, sino brindar una herramienta de apoyo que reduzca el esfuerzo f�sico, garantice una valoraci�n m�s justa y fortalezca la confianza entre productores y cooperativas.

Desde el aspecto econ�mico, esta investigaci�n es relevante porque plantea un sistema de visi�n artificial de bajo costo, utilizando c�maras accesibles, iluminaci�n LED y microprocesadores eficientes. Esta alternativa busca reducir las p�rdidas de hasta un 15% en el rendimiento del caf� ocasionadas por errores humanos en la clasificaci�n manual [8]. Al reducir el tiempo de evaluaci�n, minimizar el procesamiento y garantizar pagos m�s justos, la cooperativa incrementar� su eficiencia operativa y los productores ver�n fortalecidos sus ingresos, generando as� un impacto positivo en la competitividad del caf� cajamarquino en mercados nacionales e internacionales.

# **OBJETIVOS DE LA INVESTIGACI�N**

## **Objetivo general**

* Crear un prototipo de clasificaci�n autom�tica de granos de caf� verde mediante visi�n artificial y redes neuronales convolucionales, integrando hardware especializado y procesamiento digital para mejorar la precisi�n, objetividad y eficiencia del proceso en una cooperativa de Amazonas.

## **Objetivos espec�ficos**

* Identificar las caracter�sticas f�sicas y los defectos m�s comunes de los granos de caf�, como base para definir criterios de clasificaci�n autom�tica.
* Aplicar un modelo de visi�n artificial apoyado en procesamiento de im�genes y redes neuronales convolucionales que permita identificar y clasificar granos seg�n est�ndares de calidad.
* Desarrollar la arquitectura f�sica del prototipo, incorporando los componentes de hardware necesarios para la clasificaci�n autom�tica de granos de caf�.
* Integrar el hardware con el sistema de visi�n artificial, garantizando la comunicaci�n y sincronizaci�n entre los componentes f�sicos y el modelo de clasificaci�n.
* Validar el rendimiento del sistema mediante la medici�n de precisi�n, velocidad de clasificaci�n por grano y robustez ante variaciones de iluminaci�n y condiciones ambientales.

# **REVISI�N DE LITERATURA**

***Antecedentes***

En Turqu�a, A. Yonar y �. �zalt?n [2] se�alaron que la clasificaci�n manual de granos de caf� es lenta, subjetiva y propensa a errores, afectando la consistencia de la calidad y el valor del producto. Para abordar este problema, emplearon cinco arquitecturas de redes neuronales convolucionales preentrenadas (AlexNet, Inception\_v1, MobileNetV2, ShuffleNet y SqueezeNet) sobre un conjunto de 1,600 im�genes de cuatro variedades de caf�. El modelo ShuffleNet alcanz� una precisi�n del 99.75 % en pruebas, demostrando su alta eficiencia en la identificaci�n autom�tica de variedades. A diferencia de este estudio, que se centr� en la clasificaci�n por tipo de grano, la presente investigaci�n busca automatizar la evaluaci�n del factor de rendimiento, integrando visi�n artificial para optimizar la calidad y la valoraci�n econ�mica del caf�.

En Turqu�a, Korkmaz et al. [4] indicaron que m�todos de clasificaci�n tradicionales son lentos, ineficaces, costosos y propensos a errores humanos. Para resolver este desaf�o, utilizaron t�cnicas de procesamiento de im�genes basadas en el aprendizaje profundo para la clasificaci�n de especies de granos de caf�, empleando un conjunto de datos de 1554 im�genes que abarcaba tres tipos comerciales (Starbucks Pike Place, Espresso y Kenia). Compararon el rendimiento de cinco modelos de Redes Neuronales Convolucionales (CNN): Xception, DenseNet201, InceptionV3, InceptionResNetV2 y DenseNet121, logrando que InceptionV3 fuera el modelo m�s eficaz, al conseguir la mayor precisi�n de clasificaci�n (93 %) y exactitud (95 %), y demostrando ser el m�s eficiente computacionalmente con un tiempo de entrenamiento m�s corto (70,4 minutos). Si bien este estudio aporta una comparaci�n relevante de arquitecturas CNN para la clasificaci�n visual, su enfoque se limit� a la distinci�n de especies de caf� y no a la detecci�n de defectos f�sicos del caf� verde.

En Tailandia, Arwatchananukul et al. [5] identificaron que la selecci�n manual de granos de caf� verde ar�bica sigue siendo un reto para garantizar la calidad, debido a defectos como moho, fermentaci�n o da�os por insectos que reducen su valor comercial. Para abordar esta problem�tica, desarrollaron un modelo de aprendizaje profundo con redes neuronales convolucionales, entrenado con 6,853 im�genes tras aplicar aumento de datos. Entre las arquitecturas evaluadas, MobileNetV3 obtuvo el mejor rendimiento, alcanzando precisiones de hasta 99.84 % en validaci�n cruzada y 88.63 % con datos no vistos. El modelo se implement� en una aplicaci�n web probada por siete agricultores, de los cuales el 71.4 % mostr� alta satisfacci�n. A diferencia de este estudio, el presente trabajo se enfoca en una cooperativa peruana, priorizando el uso de sistemas ligeros y accesibles para contextos rurales con infraestructura tecnol�gica limitada.

En Indonesia, Muchtar et al. [12] identificaron que la clasificaci�n manual de granos de caf� genera problemas de calidad por la fatiga del agricultor, los errores humanos y la falta de consistencia en los resultados. Como alternativa, los autores desarrollaron un sistema de detecci�n basado en Edge AI utilizando el dataset USK-Coffee (8,000 im�genes en cuatro clases) y evaluaron diversas arquitecturas, destacando FocalNet con una precisi�n del 92 % y una p�rdida de validaci�n de 0.22. El sistema fue implementado en un dispositivo Jetson Orin Nano con interfaz en Streamlit y mapas de calor Grad-CAM para visualizar defectos en tiempo real. Este estudio demuestra que la inteligencia artificial puede mejorar la eficiencia y reducir errores en la clasificaci�n del caf�. A diferencia de este trabajo, la presente investigaci�n busca automatizar la determinaci�n del factor de rendimiento, priorizando la transparencia y la valoraci�n justa del producto.

En Brasil, Zanella et al. [15] destacan la necesidad de reemplazar la inspecci�n manual tradicional, que es lenta, subjetiva y propensa a errores, por sistemas autom�ticos de clasificaci�n de la madurez del fruto de caf�. Para lograr la clasificaci�n, la investigaci�n emple� el algoritmo YOLOv9 (You Only Look Once), destacando su nueva arquitectura ligera GELAN (Generalized Efficient Layer Aggregation Network), que optimiza el flujo de gradientes para una detecci�n m�s r�pida y precisa, ideal para aplicaciones agr�colas en tiempo real. El modelo se entren� para identificar y clasificar r�pidamente el grado de madurez de los frutos cosechados en cuatro clases: no maduro, maduro-rojo, maduro-amarillo y sobremaduro. Utilizando im�genes capturadas por una c�mara, el modelo YOLOv9 logr� un nivel de precisi�n del 99 % y una puntuaci�n F1 del 98,75 con im�genes de 640 px. Este avance apoya el uso de la visi�n artificial y modelos ligeros para el control de calidad en el caf�; sin embargo, este estudio se enfoca en el fruto (cerezo) para la cosecha, mientras que la presente investigaci�n se centra en la clasificaci�n de defectos f�sicos en el caf� verde y la determinaci�n del factor de rendimiento.

En Per�, Le�n et al. [1] se�alaron que los defectos f�sicos en los granos de caf� verde afectan directamente su calidad y valor comercial en los mercados internacionales. Dado que la inspecci�n manual es lenta, subjetiva y propensa a errores, desarrollaron un software de visi�n artificial basado en redes neuronales convolucionales (CNN) implementadas en TensorFlow y Keras para automatizar la detecci�n de defectos. El sistema alcanz� una eficiencia del 92 % en pruebas experimentales, evidenciando su potencial para reducir la variabilidad humana y mejorar la consistencia en la clasificaci�n. A diferencia de este estudio, la presente investigaci�n busca automatizar la determinaci�n del factor de rendimiento, integrando visi�n artificial no solo para el control de calidad, sino tambi�n para optimizar la valorizaci�n econ�mica del caf� en cooperativas locales.

En Per�, Le�n et al. [8] analizaron el impacto de la broca del caf� (CBB), una de las plagas m�s destructivas del sector, responsable de p�rdidas anuales estimadas en 120 millones de soles y reducciones de hasta 16.3 % en el peso. Para enfrentar este problema, desarrollaron un algoritmo de visi�n artificial con redes neuronales convolucionales (YOLOv8m) capaz de detectar granos infestados mediante im�genes capturadas con iluminaci�n LED controlada. El modelo, entrenado con t�cnicas de procesamiento de im�genes en OpenCV y Ultralytics, logr� una eficiencia del 91.8 % y permiti� la identificaci�n visual de defectos en tiempo real gracias a Grad-CAM y segmentaci�n. Este estudio demuestra que la visi�n artificial puede sustituir m�todos tradicionales como el de flotaci�n, reduciendo tiempo y recursos. A diferencia de este trabajo, la presente investigaci�n busca automatizar la identificaci�n integral de defectos y la determinaci�n del factor de rendimiento, contribuyendo a la estandarizaci�n de la calidad y a una valoraci�n m�s justa del caf�.

En Per�, Valles-Coral et al. [6] destacan la subjetividad en la selecci�n manual del caf� cerezo en Latinoam�rica, un problema que en la Asociaci�n Valle Grande (San Mart�n) resultaba en bajos promedios de calidad de taza (?83 puntos SCAA). Con el objetivo de automatizar el proceso, desarrollaron un prototipo seleccionador que utiliz� el procesamiento de Redes Neuronales Convolucionales (CNN) y el algoritmo YOLOv3. Dicho modelo fue entrenado con 24,000 im�genes de granos Catimor clasificados en cinco estados (verde, maduro, pint�n, sobre-maduro y seco). Los resultados demostraron la efectividad del prototipo al lograr una precisi�n del 94.00 % en la clasificaci�n y reducir el tiempo de selecci�n en aproximadamente tres horas por cada 100 kg procesados, permitiendo obtener una calidad de caf� superior a los 84 puntos SCAA. Este avance confirma el potencial de la visi�n artificial (CNN y YOLOv3) como una herramienta objetiva y r�pida para el control de calidad en el sector. Sin embargo, mientras este estudio se enfoc� en perfeccionar la selecci�n del caf� cerezo por madurez, la presente investigaci�n se centra en la clasificaci�n de defectos f�sicos en el caf� verde (grano ya procesado) y la determinaci�n del factor de rendimiento integrando la visi�n artificial.

En Lambayeque, Per�, Llauce y Vera [7] desarrollaron un sistema inteligente basado en redes neuronales convolucionales para clasificar granos de caf� normales y defectuosos, con el prop�sito de optimizar el control de calidad previo a la exportaci�n. El modelo fue entrenado con 11,301 im�genes capturadas bajo condiciones controladas de iluminaci�n y enfoque, alcanzando una exactitud del 95.86 %, una precisi�n del 97.91 % y una sensibilidad del 93.80 %, lo que evidencia un alto rendimiento en la detecci�n de defectos f�sicos. El sistema, implementado con una interfaz gr�fica, permite la carga, clasificaci�n y almacenamiento de im�genes, adem�s de generar reportes en formato PDF. Este trabajo demuestra que las CNN pueden aplicarse de forma efectiva en el sector cafetalero peruano para reducir errores humanos y agilizar la evaluaci�n de calidad. A diferencia de esa propuesta, la presente investigaci�n no solo busca clasificar los granos, sino tambi�n determinar el factor de rendimiento, aportando una herramienta integral para la valoraci�n econ�mica del caf� en cooperativas locales.

***Bases te�ricas***

**Lenguajes de programaci�n en Inteligencia Artificial**

Los lenguajes de programaci�n en inteligencia artificial (IA) permiten construir algoritmos, modelos de aprendizaje autom�tico y sistemas de visi�n computacional. Su elecci�n influye directamente en la velocidad de desarrollo, el acceso a bibliotecas especializadas, el rendimiento del sistema y su capacidad de escalar [16].

|  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- |
| **comparaci�n de lenguajes de programaci�n** | | | | | |
| **Factores** | **Python** | **R** | **Java** | **C++** | **Julia** |
| **Curva de aprendizaje** | Baja: Sintaxis clara y concisa, la cual es f�cil de aprender [16]. | Moderada: Se enfoca en el an�lisis estad�stico, su sintaxis puede ser menos intuitiva para principiantes [16]. | Moderada: Su sintaxis es m�s verbosa y puede resultar menos legible para principiantes [17]. | Alta: Requiere un mayor conocimiento de conceptos avanzados como punteros y gesti�n manual de la memoria [18]. | Baja: Posee una sintaxis clara [16], comparable a Python. Fue dise�ada para ser simple y amigable. |
| **Enfoque principal** | Es vers�til y un referente en Visi�n Artificial, ML y rob�tica [16]. Se centra en la simplicidad y flexibilidad [18]. | Fuerte en c�lculo estad�stico y an�lisis de datos [16]. | Adecuado para aplicaciones empresariales [17]. | Ideal para sistemas embebidos y aplicaciones que requieren procesamiento en tiempo real o alto rendimiento [18]*.* | Dise�ado para c�lculos cient�ficos y num�ricos de alto rendimiento [16], buscando la velocidad de C con la facilidad de Python [19]. |
| **Librer�as** | Extenso: TensorFlow, PyTorch, OpenCV, Scikit-learn, NumPy, Pandas | Enfocado en estad�stica: Caret, H2O, RandomFores, mlr | Moderado: DL4J, Weka, MOA | Limitado: Dlib, Shark, FANN | En crecimiento: Flux.jl, MLJ.jl, Knet.jl |
| **Aplicaciones destacadas** | Deep learning, visi�n por computadora, procesamiento de lenguaje natural | Bioestad�stica, econometr�a, miner�a de datos | Backend de IA, big data y anal�tica empresarial | Rob�tica, videojuegos, optimizaci�n de hardware | Simulaci�n cient�fica, modelado num�rico y an�lisis de alto rendimiento |

**Visi�n computacional**

La visi�n computacional es una rama de la inteligencia artificial que permite a los sistemas analizar e interpretar informaci�n visual proveniente de im�genes o videos mediante algoritmos de *machine learning* y redes neuronales convolucionales (CNN) [20].A diferencia de la visi�n humana, estos sistemas aprenden a reconocer patrones, formas y texturas a partir de grandes vol�menes de datos, logrando automatizar tareas visuales con alta precisi�n y velocidad [21].

Seg�n IBM [20], el mercado global de visi�n artificial alcanzar� 386 mil millones de d�lares en 2031, impulsado por la demanda de automatizaci�n en sectores industriales, de seguridad y agr�colas. En el �mbito agroindustrial, investigaciones como la de Ghazal et al. [22] demuestran que la visi�n artificial combinada con deep learning y Edge AI permite clasificar productos y detectar defectos con precisiones superiores al 95 %, incluso en dispositivos de bajo costo.

**El Barrenador del Caf� (CBB)**

El barrenador del caf� (Hypothenemus hampei) es considerado la plaga m�s da�ina del cultivo a nivel mundial, afectando la calidad y el rendimiento del grano [23]. Este insecto perfora el fruto del caf� para alimentarse y depositar sus huevos, provocando p�rdidas que pueden alcanzar hasta el 100 % de la producci�n en infestaciones severas [24]. Su ciclo biol�gico transcurre dentro del grano, lo que dificulta su control qu�mico y favorece su r�pida propagaci�n [23].

En pa�ses productores como Colombia, las tasas de infestaci�n var�an entre 4.5 % y 14.6 %, afectando directamente el valor comercial del caf� [25]. Estudios recientes destacan la importancia del manejo integrado de plagas y el uso de herramientas tecnol�gicas que permitan la detecci�n temprana del da�o. En este contexto, la visi�n artificial se presenta como una alternativa eficaz para identificar defectos causados por la CBB, reduciendo la dependencia de la inspecci�n manual y fortaleciendo el control de calidad en cooperativas cafetaleras.

**Calidad caf� verde**

La calidad del caf� verde se define por un conjunto de par�metros f�sicos, sensoriales y fitosanitarios que determinan su valor comercial y su aceptaci�n en los mercados internacionales. La Norma T�cnica Peruana NTP 209.027:2018 establece los requisitos para su clasificaci�n, m�todos de ensayo, muestreo, envasado y transporte, buscando uniformizar los criterios de evaluaci�n del producto [26].

El caf� verde se clasifica en tres grados (1, 2 y 3) seg�n el n�mero de defectos permitidos, el color, la homogeneidad del grano, el aroma y la calidad de taza.

* Grado 1: Presenta la mejor calidad, admitiendo un m�ximo de 15 defectos
* Grado 2: Puede tener hasta 23 defectos.
* Grado 3: Puede tener hasta 30 defectos.

**Defectos del Caf� Verde**

La Norma T�cnica Peruana NTP-ISO 10470:2014 establece una clasificaci�n internacional de los defectos presentes en el caf� verde (Ver Anexo 4), aplicable a cualquier especie, variedad o tipo de procesamiento posterior a la cosecha. Esta norma agrupa los defectos en cinco categor�as principales, considerando su impacto en la p�rdida de masa y en la calidad sensorial del grano. Cada defecto recibe un coeficiente (0) sin impacto, (0,5) impacto moderado y (1) impacto severo.

Entre los defectos m�s comunes se encuentran los granos negros, vinagres, inmaduros, brocados, partidos, malformados y con restos de c�scara, los cuales influyen negativamente en la valoraci�n comercial del lote. La norma permite cuantificar la incidencia de estos defectos y establecer criterios objetivos de aceptaci�n o rechazo, convirti�ndose en una herramienta clave para el control de calidad y la negociaci�n comercial.

**Rendimiento de caf�**

Seg�n la Norma T�cnica Peruana NTP-ISO 4072:2016, el rendimiento del caf� se determina mediante un muestreo representativo de los sacos entregados por el productor, utilizando una sonda o herramienta similar para extraer porciones homog�neas del lote. De la muestra obtenida se seleccionan 300 gramos de caf� verde para su evaluaci�n. En este proceso se identifican y separan los granos defectuosos (da�ados, brocados, negros, partidos, etc.), mientras que los granos conformes se pesan nuevamente para calcular el factor de rendimiento, que representa la proporci�n de caf� comercializable respecto al total analizado.

Este valor es fundamental, ya que determina el pago al productor y la calidad del lote [27]. Adem�s, la norma establece que la humedad del caf� verde debe mantenerse entre 10 % y 12.5 % para garantizar estabilidad y evitar deterioro del producto [28].

**Redes Neuronales Convolucionales (CNN)**

Las redes neuronales convolucionales (CNN) son un tipo de red neuronal profunda especializada en el procesamiento y an�lisis de datos tridimensionales, como im�genes o videos, y constituyen una de las arquitecturas m�s utilizadas en visi�n computacional [29]. Estas redes est�n compuestas por capas interconectadas de nodos (entrada, ocultas y salida), donde cada conexi�n tiene un peso ajustado durante el entrenamiento. Cuando la salida de un nodo supera un umbral, este se activa y transmite la informaci�n a la siguiente capa, permitiendo que la red aprenda de manera jer�rquica los patrones visuales [30].

**Arquitecturas ligeras de redes neuronales convolucionales (CNN)**

Las arquitecturas ligeras de redes neuronales convolucionales han sido desarrolladas para optimizar la velocidad de inferencia y reducir el consumo de recursos computacionales, sin sacrificar precisi�n. Estos modelos son especialmente �tiles en dispositivos con capacidad limitada, como edge devices o sistemas embebidos. Entre las m�s representativas se encuentran MobileNet, ShuffleNet y EfficientNet, las cuales aplican estrategias de reducci�n de par�metros como convoluciones separables en profundidad, agrupamiento por canales y b�squeda de arquitectura neuronal (Neural Architecture Search).

MobileNet, introducida por Howard et al. [31], emplea convoluciones separables en profundidad para disminuir dr�sticamente el n�mero de operaciones, manteniendo alta precisi�n con un tama�o de modelo reducido. ShuffleNet, por su parte, incorpora operaciones de barajado de canales (channel shuffle) que mejoran la eficiencia del flujo de informaci�n entre capas [32]. EfficientNet propone un escalado compuesto que balancea la profundidad, anchura y resoluci�n del modelo, logrando una relaci�n �ptima entre rendimiento y costo computacional [33].

Estas arquitecturas son ampliamente utilizadas en aplicaciones de visi�n artificial que requieren procesamiento en tiempo real, como clasificaci�n de im�genes agr�colas o detecci�n de defectos industriales, permitiendo alcanzar precisiones superiores al 90% con tiempos de inferencia reducidos y modelos de pocos megabytes.

**SCRUM**

Scrum es un marco de trabajo liviano que se fundamenta en el empirismo y el pensamiento Lean para generar valor a trav�s de soluciones adaptativas para problemas complejos [34].

I. Teor�a y Pilares de Scrum

Scrum emplea un enfoque iterativo e incremental para optimizar la previsibilidad y controlar el riesgo. Se apoya en tres pilares emp�ricos:

1. Transparencia: El proceso y el trabajo deben ser visibles para todos.

2. Inspecci�n: Los artefactos y el progreso hacia los objetivos deben inspeccionarse con frecuencia.

3. Adaptaci�n: Si algo se desv�a, el proceso debe ajustarse lo antes posible para minimizar la desviaci�n.

II. El Scrum Team y su Adaptaci�n al Proyecto

La unidad fundamental de Scrum es el Scrum Team, que es multifuncional (posee todas las habilidades necesarias) y autogestionado (decide internamente qui�n, c�mo y cu�ndo trabajar). Est� compuesto por tres responsabilidades espec�ficas: el Product Owner, el Scrum Master y los Developers.

III. Eventos de Scrum (Sprints)

El Sprint es el coraz�n de Scrum, un evento de duraci�n fija (un mes o menos) que act�a como el contenedor de todos los dem�s eventos formales de inspecci�n y adaptaci�n.

IV. Artefactos y Compromisos Clave

Los artefactos representan trabajo o valor y contienen compromisos que refuerzan el empirismo y los valores de Scrum

|  |  |  |
| --- | --- | --- |
| **Artefacto** | **Compromiso** | **Ejemplo** |
| Product Backlog | Objetivo del Producto | Lista priorizada de tareas elaborada en la fase de despliegue e implementaci�n |
| Sprint Backlog | Objetivo del Sprint | El plan de acci�n para entregar el Incremento en cada ciclo. Los Developers (el autor) deciden c�mo descomponer los elementos del Product Backlog en tareas de trabajo m�s peque�as. |
| Incremento | Definici�n de Terminado | El paso preciso y verificable del sistema. Para que se considere "Terminado", debe cumplir las m�tricas de calidad, tales como Precisi�n ? 85 % y F1-score ? 0.85. |

**CRISP-ML(Q)**

La Metodolog�a CRISP-ML(Q) se define como un modelo de proceso est�ndar para el desarrollo de aplicaciones de Machine Learning (ML) que incorpora una metodolog�a de aseguramiento de calidad (Q). Este modelo se basa en el est�ndar CRISP-DM, pero expande su alcance para cubrir las especificidades de las aplicaciones de ML, buscando mejorar la eficiencia y la tasa de �xito de los proyectos [35].

La estructura de CRISP-ML(Q) se compone de seis fases a lo largo del ciclo de vida de una aplicaci�n de ML:

1. Comprensi�n del Negocio y los Datos (Business and Data Understanding): Esta fase inicial combina la definici�n de objetivos de negocio y ML con la recopilaci�n y verificaci�n de la calidad de los datos para evaluar la viabilidad del proyecto.
2. Preparaci�n de los Datos (Data Preparation): Su prop�sito es crear un conjunto de datos apto para el modelado, bas�ndose en las experiencias de la fase anterior.
3. Modelado (Modeling): Se centra en crear uno o varios modelos que cumplan con las restricciones y requisitos definidos previamente, evaluando no solo el rendimiento, sino tambi�n la robustez, escalabilidad y la demanda de recursos.
4. Evaluaci�n (Evaluation): Aqu� se valida el rendimiento del modelo en datos no vistos (conjunto de prueba), se evalua la robustez del modelo con datos err�neos o con ruido y se desarrolla un modelo de aprendizaje autom�tico para la confianza.
5. Despliegue (Deployment): Implica el uso pr�ctico del modelo en el campo de aplicaci�n designado, considerando el hardware de inferencia y asegurando la aceptaci�n del usuario.
6. Monitoreo y Mantenimiento (Monitoring and Maintenance): Es la fase crucial que extiende el modelo respecto a CRISP-DM. Se encarga de gestionar el riesgo de degradaci�n del rendimiento del modelo a lo largo del tiempo debido a cambios en la distribuci�n de los datos (data drift) o el envejecimiento del hardware.

La caracter�stica distintiva del modelo es la integraci�n de la metodolog�a de Aseguramiento de Calidad (QA), que sigue un enfoque gen�rico basado en el "pensamiento basado en riesgos". Para cada tarea, se identifican y mitigan los riesgos t�cnicos para garantizar la trazabilidad y la calidad durante todo el proceso de desarrollo.

# **MATERIALES Y M�TODOS**

## **Metodolog�a**

1. **Tipo de investigaci�n**

Esta investigaci�n se enmarca en el enfoque aplicado y tecnol�gico, ya que busca ofrecer una soluci�n pr�ctica a una problem�tica real que enfrentan los productores y cooperativas cafetaleras de Amazonas: automatizar la clasificaci�n y evaluaci�n del factor de rendimiento del caf� verde. Para ello, se desarrollar� un sistema inteligente basado en visi�n artificial y redes neuronales convolucionales (CNN), capaz de identificar y clasificar los granos seg�n su calidad, reduciendo la subjetividad humana y mejorando la precisi�n del proceso.

De acuerdo con el Manual de Frascati [36], la investigaci�n aplicada se orienta hacia la resoluci�n de problemas pr�cticos espec�ficos mediante el uso del conocimiento cient�fico y tecnol�gico. A diferencia de la investigaci�n b�sica, que busca ampliar el saber te�rico, la aplicada tiene un prop�sito instrumental: generar soluciones utilizables y medibles en contextos reales.

En el marco metodol�gico, se adoptar� una combinaci�n entre SCRUM para la gesti�n �gil del desarrollo del sistema y CRISP-ML(Q) para la construcci�n, validaci�n y aseguramiento de calidad del modelo de aprendizaje autom�tico. SCRUM permitir� estructurar el trabajo en sprints iterativos con entregables funcionales al finalizar cada ciclo [34], mientras que CRISP-ML(Q) garantizar� una ejecuci�n sistem�tica y trazable del proceso de machine learning, abarcando desde la comprensi�n del problema y los datos hasta la monitorizaci�n del rendimiento y la mejora continua del modelo [35].

La elecci�n de este tipo y enfoque metodol�gico responde a que la investigaci�n no solo busca analizar un problema, sino desarrollar una soluci�n tecnol�gica sostenible y adaptable, que mejore la eficiencia, la objetividad y la transparencia en el proceso de clasificaci�n del caf� verde. El prototipo propuesto ser� validado en la Cooperativa Agraria Line Coffee Mara��n, empleando m�tricas cuantitativas que eval�en su precisi�n, velocidad de clasificaci�n y confiabilidad bajo condiciones reales de trabajo.

1. **M�todos de investigaci�n**

Para el desarrollo de esta investigaci�n se emplear� diversos m�todos seleccionados en funci�n de la naturaleza del problema, los objetivos planteados y el enfoque tecnol�gico de la soluci�n. Cada uno de ellos contribuir� a comprender, dise�ar, implementar y validar el sistema inteligente de clasificaci�n de granos de caf� mediante visi�n artificial.

**TABLA I**

m�todos de investigaci�n

|  |  |
| --- | --- |
| **M�todo** | **Sustento por el cual ser� empleado en la investigaci�n** |
| **Anal�tico sint�tico** | Seg�n Sampieri et al [37] ,Este enfoque permite descomponer un fen�meno complejo en sus elementos esenciales y posteriormente integrarlos en una totalidad coherente. |
| **Hipot�tico deductivo** | Seg�n Bunge [38], este m�todo consiste en formular hip�tesis verificables y contrastarlas mediante la observaci�n o la experimentaci�n. |
| **Inductivo** | Seg�n Bernal [39], el enfoque inductivo analiza los resultados obtenidos del sistema y detectar patrones de clasificaci�n o errores recurrentes. |
| **Cuantitativo** | Seg�n Sampieri et al. [37], el enfoque cuantitativo se basa en la medici�n num�rica de variables y el an�lisis estad�stico de los datos, con el prop�sito de establecer patrones de comportamiento y validar hip�tesis de manera objetiva. |
| **Experimentaci�n** | Seg�n Piattini et al. [40], la experimentaci�n permite validar hip�tesis mediante la manipulaci�n de variables y la observaci�n de sus efectos. |

En conjunto, estos m�todos se alinean plenamente con los objetivos de la investigaci�n, ya que facilitan el desarrollo, validaci�n y evaluaci�n integral de un sistema inteligente funcional, t�cnica y econ�micamente viable. As�, se busca garantizar una soluci�n que no solo optimice la calidad y la objetividad del proceso de clasificaci�n, sino que tambi�n genere beneficios econ�micos sostenibles para los productores de caf� en Amazonas.

**TABLA II**

|  |  |  |  |
| --- | --- | --- | --- |
| t�cnicas de investigaci�n | | | |
| **T�cnicas** | **Instrumentos** | **Poblaci�n** | **Prop�sito** |
| **Revisi�n documental** | Fichas de revisi�n bibliogr�fica (Ver Anexo 5) | Normas t�cnicas, gu�as de implementaci�n y documentos especializados sobre caf� verde. | Analizar, registrar y sistematizar la informaci�n t�cnica para sustentar te�ricamente el dise�o del sistema |
| **Observaci�n estructurada** | Gu�a de observaci�n (Ver Anexo 4) | Muestras de granos de caf� | Registrar las caracter�sticas visuales de los granos |
| **Encuesta estructurada** | Cuestionario (Ver Anexo 6) | Productores de caf� asociados a la cooperativa y externos | Recoger la percepci�n sobre el proceso de clasificaci�n manual y el c�lculo del factor de rendimiento |
| **Entrevista** | Entrevistar (Ver Anexo 2) | Operarios y encargados de la clasificaci�n del caf� en la cooperativa | Obtener informaci�n sobre el proceso actual de clasificaci�n y c�lculo del rendimiento del caf� |

En conjunto, estas t�cnicas garantizan una cobertura metodol�gica coherente con los objetivos de la investigaci�n y con su car�cter aplicado, asegurando que los resultados obtenidos sean tanto cient�ficamente v�lidos como funcionales para la realidad operativa de las cooperativas cafetaleras.

1. **Metodolog�a de desarrollo**

Para el desarrollo del sistema autom�tico de clasificaci�n de granos de caf� mediante visi�n artificial, se aplicar� una metodolog�a h�brida basada en SCRUM y CRISP-ML(Q), ya que ambas se complementan al integrar la gesti�n �gil de desarrollo de software con un proceso sistem�tico y controlado de modelado de aprendizaje autom�tico con aseguramiento de calidad.

**Fases CRISP-ML(Q)**

**Fase 1. Comprensi�n del negocio y de los datos**

* Definir los objetivos del negocio: automatizar la clasificaci�n del caf� verde y el c�lculo del factor de rendimiento para reducir errores humanos y agilizar el proceso de evaluaci�n en la Cooperativa Agraria Line Coffee Mara��n.
* Definir los objetivos del modelo de Machine Learning: desarrollar una CNN ligera capaz de clasificar granos con una precisi�n ? 90 % y latencia ? 200 ms.
* Evaluar la situaci�n actual: analizar el m�todo manual de clasificaci�n, las p�rdidas promedio (? 15 %), recursos tecnol�gicos disponibles (c�mara, sensores, laptop con GPU) y limitaciones del entorno rural.
* Elaborar el plan del proyecto: establecer cronograma, herramientas (Python, TensorFlow, OpenCV, Flask), m�tricas de desempe�o y criterios de �xito t�cnico y operativo.

**Fase 2. Preparaci�n de los datos**

* Recolectar datos iniciales: capturar im�genes de granos de caf� proporcionadas por la cooperativa y complementar con bases p�blicas.
* Describir los datos: definir variables visuales relevantes: color, textura, tama�o, contorno y defectos f�sicos.
* Explorar los datos: generar histogramas, an�lisis de correlaciones y distribuci�n de clases (buenos / defectuosos).
* Verificar calidad: descartar im�genes borrosas o sobreexpuestas y comprobar balance entre clases.
* Seleccionar y preparar datos: recorte, redimensionamiento, normalizaci�n de p�xeles, balanceo y aumento de datos (rotaci�n, brillo).
* Asegurar calidad de datos: documentar trazabilidad, diversidad y consistencia del dataset.

**Fase 3. Modelado**

* Seleccionar t�cnica de modelado: evaluar arquitecturas CNN ligeras por precisi�n y eficiencia computacional.
* Definir m�tricas de calidad: accuracy, precision, recall, F1-score y matriz de confusi�n.
* Entrenar y optimizar el modelo: aplicar validaci�n cruzada, ajuste de hiperpar�metros y transfer learning para mejorar generalizaci�n.
* Aplicar conocimiento de dominio: integrar criterios de clasificaci�n seg�n NTP 209.027:2018 y NTP-ISO 10470:2014.
* Documentar experimentos: registrar resultados, par�metros, configuraciones y evoluci�n del modelo en Notebooks.

**Fase 4. Evaluaci�n**

* Validar desempe�o: medir m�tricas con datos no vistos y comparar frente al proceso manual tradicional.
* Evaluar robustez: analizar estabilidad del modelo ante variaciones de luz, �ngulo o movimiento del grano.
* Interpretar resultados: utilizar Grad-CAM para visualizar las regiones de atenci�n del modelo.
* Decidir despliegue: si el modelo cumple los umbrales definidos, proceder a su integraci�n; de lo contrario, reentrenar.
* Documentar evaluaci�n: generar reporte t�cnico con resultados y observaciones.

**Fase 5. Despliegue**

* Integraci�n del modelo entrenado: implementar en una aplicaci�n desarrollada con Flask y OpenCV para clasificar granos en tiempo real.
* Vinculaci�n hardware: conectar c�mara global shutter, sensores de carga HX711, banda transportadora y actuadores controlados por Arduino.
* Evaluaci�n en campo: probar el sistema bajo condiciones reales de producci�n.
* Gesti�n y gobernanza: mantener versi�n del modelo y registros de rendimiento.

**Fase 6. Monitoreo y mantenimiento**

* Monitorear desempe�o: registrar m�tricas de precisi�n y eficiencia del modelo durante el uso continuo.
* Recolectar nuevos datos: incorporar im�genes reales de producci�n para reentrenar y actualizar el modelo.
* Asegurar calidad continua: aplicar reentrenamiento peri�dico ante degradaci�n del rendimiento.
* Documentar mantenimiento: mantener registro hist�rico de mejoras y versiones del modelo.

**Fases SCRUM**

Aplicada durante las fases de despliegue y mantenimiento de CRISP-ML(Q).

**1. Planificaci�n del sprint**

* Definir tareas y objetivos de cada iteraci�n (captura, clasificaci�n, visualizaci�n, reporte).
* Priorizar funcionalidades cr�ticas: procesamiento de im�genes, interfaz de usuario y comunicaci�n con hardware (Arduino + sensores).
* Establecer criterios de aceptaci�n y entregables de cada sprint.

**2. Desarrollo iterativo**

* Construir de forma incremental el sistema:
* M�dulo de captura: adquisici�n en tiempo real desde la c�mara global shutter.
* M�dulo de procesamiento: ejecuci�n del modelo CNN y generaci�n de resultados.
* M�dulo de control: env�o de se�ales a actuadores para separar granos buenos / defectuosos.
* M�dulo de interfaz: visualizaci�n de resultados, peso total y c�lculo del factor de rendimiento.
* Realizar pruebas unitarias y funcionales en cada iteraci�n.

**3. Revisi�n del sprint**

* Evaluar los avances y demostrar funcionalidades implementadas.
* Recoger observaciones del asesor y del personal t�cnico de la cooperativa.
* Ajustar m�dulos seg�n retroalimentaci�n recibida.

## **Resultados esperados**

## **5.2.1. Mapeo de objetivos, resultados y verificaci�n**

|  |  |  |
| --- | --- | --- |
| **Objetivo espec�fico 01:**  Identificar las caracter�sticas f�sicas y los defectos m�s comunes de los granos de caf�, como base para definir criterios de clasificaci�n autom�tica. | | |
| Resultados | Medio de verificaci�n | Indicador objetivamente verificable |
| Resultado 1: Cat�logo t�cnico de defectos y caracter�sticas f�sicas del caf� verde (forma, tama�o, color, textura, humedad) conforme a la NTP 209.027:2018 y la NTP-ISO 10470:2014. | Documento t�cnico con la taxonom�a visual y tabla de defectos basada en est�ndares nacionales e internacionales. | Cat�logo validado con tipos de defectos clasificados y descritos visualmente. |
| Resultado 2: Base de datos estructurada de im�genes de granos de caf� etiquetadas seg�n su tipo de defecto. | Dataset propio de la cooperativa Line Coffee Mara��n con anotaciones de clase y dataset p�blico de caf� verde | Dataset compuesto por al menos 5,000 im�genes etiquetadas y verificadas. |
| **Objetivo espec�fico 02:** Aplicar un modelo de visi�n artificial apoyado en procesamiento de im�genes y redes neuronales convolucionales (CNN) que permita identificar y clasificar granos seg�n est�ndares de calidad | | |
| Resultados | Medio de verificaci�n | Indicador objetivamente verificable |
| Resultado 1: Modelo CNN entrenado y validado para la clasificaci�n de granos normales y defectuosos. | Archivo del modelo entrenado y reporte de m�tricas de desempe�o | Precisi�n ? 85 %, F1-score ? 0.85 y tiempo de inferencia ? 1 s por imagen |
| Resultado 2: Documentaci�n del proceso de entrenamiento, ajuste de par�metros y evaluaci�n del modelo. | Bit�cora digital (Jupyter Notebook) con registros de experimentaci�n y validaci�n cruzada. | Documentaci�n reproducible que cumpla criterios de calidad del proceso CRISP-ML(Q). |
| **Objetivo espec�fico 3:** Desarrollar la arquitectura f�sica del prototipo, incorporando los componentes de hardware necesarios para la clasificaci�n autom�tica de granos de caf�. | | |
| Resultados | Medio de verificaci�n | Indicador objetivamente verificable |
| Resultado 01: Estructura f�sica del prototipo ensamblada, incluyendo c�mara, sistema de iluminaci�n, faja transportadora y soporte mec�nico. | Fotograf�as del ensamblaje, plano del prototipo, informe de armado. | 100% de los componentes f�sicos instalados seg�n plano t�cnico. |
| Resultado 02: Sistema de captura de im�genes operando correctamente dentro del prototipo. | Registro de pruebas de captura, videos y reporte t�cnico de funcionamiento. | Tasa de captura exitosa ? 95% de las im�genes tomadas por la c�mara. |
| Resultado 03: Sistema de iluminaci�n calibrado para obtener im�genes con contraste adecuado y m�nima interferencia de sombras. | Informe de calibraci�n y reportes de pruebas con variaci�n de luz. | Variaci�n de iluminaci�n controlada �10% respecto al valor calibrado durante 5 pruebas consecutivas. |
| **Objetivo espec�fico 4:** Integrar el hardware con el sistema de visi�n artificial, garantizando la comunicaci�n y sincronizaci�n entre los componentes f�sicos y el modelo de clasificaci�n. | | |
| Resultados | Medio de verificaci�n | Indicador objetivamente verificable |
| Resultado 01: Comunicaci�n estable entre la c�mara, el sistema de iluminaci�n, la faja transportadora y el m�dulo de procesamiento digital. | Registro de pruebas de conexi�n, bit�coras de funcionamiento, capturas de consola y reportes t�cnicos. | Latencia de comunicaci�n ? 200 ms entre captura, procesamiento y registro en al menos 50 iteraciones consecutivas. |
| Resultado 02: Integraci�n funcional del modelo de visi�n artificial con el flujo de captura, preprocesamiento y clasificaci�n. | Informe t�cnico del pipeline integrado (captura, procesamiento, predicci�n). | Flujo de clasificaci�n completo operando con una tasa de �xito ? 95 % en pruebas internas controladas. |
| Resultado 03: Sincronizaci�n entre el avance del transporte (faja) y el sistema de clasificaci�n para evitar capturas fuera de tiempo. | Reportes de sincronizaci�n, tiempo, videos y evidencia de pruebas. | Desalineaci�n ? 5 % entre el tiempo esperado y el tiempo real de captura por ciclo. |
| **Objetivo espec�fico 5:** Validar la precisi�n y eficiencia del sistema mediante pruebas experimentales y comparaciones con el m�todo manual. | | |
| Resultados | Medio de verificaci�n | Indicador objetivamente verificable |
| Resultado 01: Informe comparativo que eval�e la precisi�n, rapidez y objetividad del sistema autom�tico frente al m�todo manual tradicional. | Documento t�cnico con an�lisis estad�stico (t-test, ANOVA o equivalentes), tablas de resultados, gr�ficos comparativos. | F1-Score ? 0.85 para la clasificaci�n de defectos.  Diferencia de error ? 10% entre sistema autom�tico y m�todo manual.  Reducci�n ? 30% en el tiempo de clasificaci�n por grano. |
| Resultado 02: Prueba experimental del sistema bajo variaciones controladas de iluminaci�n y condiciones ambientales. | Registro de pruebas, mediciones de lux, reporte fotogr�fico y videos de ejecuci�n. | Variaci�n de precisi�n ? 5% entre condiciones est�ndar y condiciones adversas.  Estabilidad operativa ? 90% durante pruebas ambientales. |
| Resultado 03: Evaluaci�n del sistema por parte de personal t�cnico de la cooperativa. | Encuestas estructuradas, actas de validaci�n, entrevistas y observaciones de campo. | Participaci�n de al menos 3 evaluadores.  Nivel de satisfacci�n ? 80% respecto a uso, confiabilidad y precisi�n del sistema. |
| Resultado 04: Reporte final de validaci�n experimental integrando todos los hallazgos y m�tricas de desempe�o. | Documento final, anexos de pruebas y gr�ficos de rendimiento. | Informe validado y completo seg�n protocolo experimental definido. |

## **5.2.2 Prototipo de la soluci�n**

1. **Funcionalidad de la soluci�n**

El prototipo busca automatizar el proceso de clasificaci�n y evaluaci�n del rendimiento del caf� verde mediante un sistema de visi�n artificial basado en redes neuronales convolucionales (CNN). El sistema permite identificar de manera autom�tica los granos con defectos f�sicos y separarlos de los granos buenos. De este modo, se optimiza el control de calidad en las cooperativas, reduciendo la subjetividad del operario, los errores humanos y el tiempo requerido en la evaluaci�n manual.

El sistema incluir� un m�dulo de visi�n, una faja transportadora con actuador de desv�o, un sensor de carga para el c�lculo del factor de rendimiento, y una interfaz digital que muestra los resultados en tiempo real y genera reportes autom�ticos.

* Requerimientos funcionales de la soluci�n del proyecto de tesis.
  + Permitir el ingreso de datos de la muestra desde la interfaz del sistema, incluyendo:
    - Peso total de la muestra (por ejemplo, 250 g).
    - Peso del caf� trillado y tamizado antes de la clasificaci�n (por ejemplo, 230 g).
  + Capturar im�genes en tiempo real mediante una c�mara global shutter con iluminaci�n controlada.
  + Detectar y clasificar autom�ticamente los granos seg�n su estado: buenos o defectuosos (broca, partido, cascarilla, objeto extra�o, etc.).
  + Activar un actuador electromec�nico o servo para desviar los granos defectuosos hacia una bandeja lateral.
  + Medir el peso final de los granos buenos utilizando una celda de carga de 5 kg conectada al m�dulo HX711.
  + Calcular autom�ticamente el factor de rendimiento (FR) utilizando los datos iniciales ingresados por el usuario y el peso final medido por el sistema.
  + Mostrar en tiempo real el conteo de defectos detectados y el avance del proceso.
  + Generar un reporte final automatizado con: fecha, lote, pesos ingresados, peso de granos buenos, factor de rendimiento y desglose de defectos.
  + Guardar el historial de procesos en una base de datos local para trazabilidad y auditor�a de calidad.
* Requerimientos no funcionales de la soluci�n del proyecto de tesis.
  + Precisi�n m�nima del modelo IA ? 90 % en la clasificaci�n entre granos buenos y defectuosos.
  + Procesamiento en tiempo real con latencia de respuesta ? 200 ms entre detecci�n y actuaci�n.
  + Interfaz visual intuitiva, dise�ada para operarios sin experiencia t�cnica.
  + La arquitectura del sistema debe ser modular y flexible, permitiendo incorporar nuevos tipos de defectos, m�tricas o sensores sin necesidad de redise�ar todo el sistema.
  + Compatibilidad con laptops o mini PC con GPU.
  + El acceso al sistema debe estar protegido mediante autenticaci�n b�sica (usuario y contrase�a).
  + Registro temporal y trazabilidad completa, manteniendo la informaci�n de cada lote procesado.

1. **Interfaces**

**Interfaz 1: Interfaz de inicio del sistema**

Esta interfaz permite al usuario acceder al sistema, validando su identidad antes de operar el prototipo. Incluye campos de autenticaci�n b�sica (usuario y contrase�a) y la posibilidad de registrar nuevos operadores autorizados de la cooperativa.

Objetivo: Garantizar el acceso seguro y controlado al sistema por parte de usuarios responsables del proceso de clasificaci�n.

![](data:image/png;base64...)

*Fig. 01: Pantalla de inicio de sesi�n del sistema*

**Interfaz 2: Interfaz de registro de muestra**

En esta ventana, el operario ingresa los datos iniciales del lote, como el c�digo o nombre del productor, el n�mero de tamiz utilizado, el peso total de la muestra y el peso de los granos trillados y tamizados.

Objetivo: Registrar los datos de entrada que servir�n de base para el c�lculo posterior del factor de rendimiento (FR).

![](data:image/png;base64...)

*Fig. 02: Pantalla registro de muestra de granos de caf�*

**Interfaz 3: Interfaz de monitoreo en tiempo real**

Durante la ejecuci�n, la c�mara transmite en directo el flujo de caf� sobre la faja transportadora. En la pantalla se muestran los granos detectados y clasificados con rect�ngulos de color (verde = bueno, rojo = defectuoso), junto con indicadores num�ricos de conteo y barras de progreso.

Objetivo: Permitir al usuario visualizar en tiempo real el proceso de clasificaci�n y la respuesta del actuador que separa los granos defectuosos.

![](data:image/png;base64...)

*Fig. 03: Interfaz de monitoreo en tiempo real*

**Interfaz 4: Interfaz de resultados y reporte**

Una vez finalizada la clasificaci�n, el sistema genera un reporte autom�tico con los siguientes datos:

* + Peso inicial y peso de granos buenos (medido por la celda de carga).
  + Factor de rendimiento (FR) calculado autom�ticamente.
  + Distribuci�n de defectos detectados (broca, partido, cascarilla, objetos extra�os, etc.).
  + Fecha, hora, tamiz utilizado y operador responsable.

Objetivo: Facilitar la evaluaci�n final del lote y documentar los resultados de manera digital y exportable (PDF o CSV).

![](data:image/png;base64...)

*Fig. 04: Interfaz de reporte y resultados*

1. **Arquitectura de la soluci�n propuesta**

La arquitectura que se considerar� en la soluci�n propuesta es la siguiente:

*![](data:image/png;base64...)*

*Fig. 05: Arquitectura de red propuesta*

![](data:image/png;base64...)

*Fig. 06: Arquitectura del prototipo del sistema de clasificaci�n autom�tica de granos de caf�*

La infraestructura tecnolog�a estar� conformada por:

* **C�mara global shutter**

Dispositivo de captura �ptica que adquiere im�genes en tiempo real del flujo de caf� sobre la faja transportadora. Evita distorsi�n por movimiento y proporciona una representaci�n fiel del grano.

* **Sistema de iluminaci�n LED**

Conjunto de luces LED blancas (6500 K) dispuestas en domo o anillo difusor que proporciona iluminaci�n uniforme, minimizando sombras y reflejos en los granos.

* **Faja transportadora**

Estructura mec�nica que permite el desplazamiento continuo de los granos bajo la c�mara para su an�lisis visual.

* **Actuador de desv�o**

Servo o solenoide de respuesta r�pida sincronizado con el modelo de visi�n encargado de separar autom�ticamente los granos defectuosos detectados por el sistema.

* **Celda de carga + M�dulo HX711**

Sensor de peso encargado de medir el peso final de los granos buenos para el c�lculo del factor de rendimiento.

* **Microcontrolador Arduino**

Placa de control que coordina los dispositivos f�sicos (celda de carga, actuador y sensores). Env�a los datos al sistema principal por comunicaci�n serial.

* **Laptop de procesamiento**

Equipo central que ejecuta los m�dulos de visi�n artificial, clasificaci�n y generaci�n de reportes.

Caracter�sticas:

* + - Procesador: Intel 9 Ultra 275HX
    - GPU: NVIDIA RTX 50570ti (12 GB VRAM)
    - RAM: 32 GB
    - Sistema operativo: Windows 11
* **M�dulo de visi�n artificial (IA)**

Modelo de redes neuronales convolucionales (CNN) entrenado para identificar y clasificar granos de caf� en tiempo real seg�n su estado (buenos o defectuosos).

* **Bandejas de clasificaci�n**

Contenedores que reciben los granos despu�s del proceso de clasificaci�n: una para granos defectuosos y otra para los granos buenos que ser�n pesados.

# **CRONOGRAMA**

El plan sugerido cubre el periodo de enero a diciembre de 2026 e incluye las etapas de preparaci�n, realizaci�n, verificaci�n y divulgaci�n del proyecto. Se llevar� a cabo utilizando un enfoque combinado de SCRUM y de CRISP-ML(Q), garantizando entregas peri�dicas y supervisi�n de la calidad�en�cada�ciclo.

**TABLA III.**

Cronograma de actividades

|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Actividades** | **2026** | | | | | | | | | | | | | | | |
| **Mar.** | **Abr.** | | **May.** | | **Jun.** | | **Jul.** | **Ago.** | **Set.** | | **Oct.** | | **Nov.** | | **Dic.** |
| **2** | **1** | **2** | **1** | **2** | **1** | **2** | **1** | **2** | **1** | **2** | **1** | **2** | **1** | **2** | **1** |
| FASE DE EJECUCI�N | | | | | | | | | | | | | | | | |
| An�lisis de requerimientos funcionales y t�cnicos | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| Dise�o del Product Backlog y planificaci�n de sprints |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| Recolecci�n de im�genes de caf� y etiquetado |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |
| Preprocesamiento y aumento de datos |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |
| Entrenamiento del modelo CNN |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |
| Evaluaci�n de desempe�o del modelo |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |
| Desarrollo de la interfaz gr�fica |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |
| Integraci�n del hardware (c�mara, iluminaci�n, sensor de carga) |  |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |
| Pruebas funcionales del prototipo |  |  |  |  |  | X | X |  |  |  |  |  |  |  |  |  |
| Comparaci�n con el m�todo manual |  |  |  |  |  |  | X | X |  |  |  |  |  |  |  |  |
| An�lisis de resultados y retroalimentaci�n |  |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  |
| FASE DE COMUNICACI�N | | | | | | | | | | | | | | | | |
| Elaboraci�n de documentaci�n del articulo |  |  |  |  |  |  |  |  | X | X | X | X | X | X |  |  |
| Entrega y defensa del proyecto |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X | X |

La agenda contempla las actividades desde marzo hasta diciembre de 2026, organizadas en dos fases: ejecuci�n y comunicaci�n. Durante los primeros meses se abordar� la definici�n de requerimientos, el dise�o del sistema y el entrenamiento del modelo de visi�n artificial. Posteriormente, se desarrollar� la integraci�n del hardware, las pruebas del prototipo en la cooperativa y la evaluaci�n experimental del rendimiento del sistema. Finalmente, se elaborar� la documentaci�n t�cnica y acad�mica para la presentaci�n y sustentaci�n del proyecto.

Esta planificaci�n garantiza un proceso estructurado y coherente con los objetivos de la investigaci�n, asegurando la entrega del prototipo funcional y la obtenci�n de resultados v�lidos dentro del plazo establecido.

# **PRESUPUESTO**

## **Presupuesto del producto acreditable**

TABLA IV

Presupuesto del producto acreditable

| PARTE PRESUP. | DESCRIPCI�N | CANT. | UNIDAD DE MEDIDA | PRECIO UNITARIO  (S/.) | PRECIO TOTAL  (S/.) | SUBTOTAL (S/.) |
| --- | --- | --- | --- | --- | --- | --- |
| C�digo | M�dulo de CNN | | | | | 400.00 |
| MCN01 | M�dulo de CNN | 1 | UNIDAD | 400.00 | 300.00 |  |
| C�digo | M�dulo de Captura | | | | | 100.00 |
| MC01 | M�dulo de Captura | 1 | UNIDAD | 100.00 | 100.00 |  |
| C�digo | M�dulo de Procesamiento y control | | | | | 200.00 |
| MPC01 | M�dulo de procesamiento | 1 | UNIDAD | 100.00 | 100.00 |  |
| MPC02 | M�dulo de control | 1 | UNIDAD | 100.00 | 100.00 |  |
| C�digo | M�dulo de Usuario | | | | | 300.00 |
| MU01 | Login | 1 | UNIDAD | 50.00 | 50.00 |  |
| MU02 | Gesti�n de usuarios | 1 | UNIDAD | 50.00 | 50.00 |  |
| MU03 | Reportes | 1 | UNIDAD | 100.00 | 100.00 |  |
| MU04 | Registro de clasificaci�n autom�tica y c�lculo del rendimiento | 1 | UNIDAD | 200.00 | 200.00 |  |
| C�digo | Material de soporte y documentaci�n | | | | | 330.00 |
| MSD01 | Material impreso para manual t�cnico y gu�as del sistema | 1 | UNIDAD | 30.00 | 30.00 |  |
| MSD02 | Disco de almacenamiento digital de respaldo | 1 | UNIDAD | 300.00 | 300.00 |  |
| MSD03 | Documentaci�n de tesis | 1 | UNIDAD | 0.00 | 0.00 |  |
| C�digo | Servicios | | | | | 750.00 |
| SRV01 | Internet | 4 | MES | 75.00 | 300.00 |  |
| SRV02 | Viajes a la Cooperativa Agraria Line Coffee Mara��n (transporte y vi�ticos) | 3 | UNIDAD | 150.00 | 450.00 |  |
| TOTAL PRESUPUESTO DEL PROUCTO ACREDITABLE | | | | | | 2,080.00 |

## **Presupuesto tecnol�gico**

TABLA V

Presupuesto tecnol�gico

|  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- |
| PARTE PRESUP. | DESCRIPCI�N | CANT. | UNIDAD DE MEDIDA | PRECIO UNITARIO  (S/.) | PRECIO TOTAL  (S/.) | SUBTOTAL (S/.) |
| C�digo | Componentes electr�nicos | | | | | 678.00 |
| 2.6.3.2.9.5 | Sensor de carga HX711 + celda de 5 kg | 1 | GLOBAL | 35.00 | 35.00 |  |
| 2.6.3.2.9.4 | Arduboard Uno R3 | 1 | GLOBAL | 60.00 | 60.00 |  |
| 2.6.3.2.9.4 | Driver puente h mmx1508 (mini l298n) | 1 | GLOBAL | 10.00 | 10.00 |  |
| 2.6.3.2.9.4 | Micro servo SG90 1.5Kg | 1 | GLOBAL | 15.00 | 15.00 |  |
| 2.6.3.2.9.4 | Motor DC TT 6V/200RPM eje doble de metal | 1 | GLOBAL | 20.00 | 20.00 |  |
| 2.6.3.2.9.5 | C�mara global shutter | 1 | GLOBAL | 450.00 | 450.00 |  |
| 2.6.3.2.9.4 | PCB | 1 | GLOBAL | 20.00 | 20.00 |  |
| 2.6.3.2.9.4 | Fuente de Poder Switching 12V 5A | 1 | GLOBAL | 50.00 | 50.00 |  |
| 2.6.3.2.9.4 | Cable jumper | 2 | KIT | 10.00 | 20.00 |  |
| C�digo | Deprecision de equipos tecnologicos | | | | | 4,500.00 |
| 2.6.3.2.3.1 | Laptop | 1 | GLOBAL | 4500.00 | 4500.00 |  |
| C�digo | Software y herramientas | | | | | 0.00 |
| 2.6.6.1.3.2 | Licencias o entornos de desarrollo (Python, PyTorch, OpenCV, Streamlit, etc.) | 1 | GLOBAL | 0.00 | 0.00 |  |
| TOTAL PRESUPUESTO TECNOL�GICO | | | | | | 5,178.00 |

## **Resumen presupuestal**

TABLA VI

Resumen presupuestal

|  |  |  |
| --- | --- | --- |
| ITEM | DESCRIPCI�N PRESUPUESTO | SUBTOTAL (S/.) |
|
| 1 | TOTAL PRESUPUESTO DEL PRODUCTO ACREDITABLE | 2,080.00 |
| 2 | TOTAL PRESUPUESTO TECNOL�GICO | 5,180.00 |
| TOTAL PRESUPUESTO | | S/. 7,260.00 |

# **COLABORADORES**

TABLA VII

Colaboradores

|  |  |  |  |
| --- | --- | --- | --- |
| N� | COLABORADOR | TIPO DE APOYO | ESPECIFICACI�N DEL APOYO |
| 1 | Cooperativa Agraria Line Coffee Mara��n | Log�stico y t�cnico | Proporcionar� muestras de caf� verde, espacio para la validaci�n experimental y asesor�a sobre el proceso de clasificaci�n y c�lculo del factor de rendimiento. |
| 2 | Gerente General | Administrativo y coordinaci�n | Autorizaci�n del desarrollo del proyecto y coordinaci�n para la ejecuci�n de las pruebas y actividades de campo. |
| 3 | Caficultores | Participaci�n pr�ctica | Aplicaci�n de encuestas para conocer su percepci�n de la clasificaci�n manual y el uso del sistema automatizado. |
| 4 | Personal encargado de la evaluaci�n del caf� | T�cnico y operativo | Ejecuci�n de pruebas experimentales, identificaci�n de defectos y en la validaci�n comparativa entre el m�todo manual y el sistema automatizado. |

# **REFERENCIAS BIBLIOGR�FICAS**

[1] R. A. Le�n Le�n, E. E. Atalaya Morales, y S. B. Narvaez Alvarado, �Development of a Software with Artificial Vision to Detect the Physical Defect of the Green Coffee Bean�, en *CISCI - Conferencia Iberoam. Sistemas, Cibern. Inform.*, International Institute of Informatics and Cybernetics, 2024, pp. 468-474. doi: 10.54808/CISCI2024.01.468.

[2] A. Yonar y �. �zalt?n, �Automatic recognition of coffee bean varieties based on pre-trained architectures�, *Commun. Fac. Sci. Univ. Ank. Ser. A2-A3 Phys. Sci. Eng.*, vol. 66, n.o 2, pp. 162-175, dic. 2024, doi: 10.33769/aupse.1411294.

[3] R. Neto, P. Sousa, L. Rodrigues Moreira, P. God, y J. Mari, *Enhancing green coffee quality assessment through deep learning*. 2023, p. 89. doi: 10.5753/wvc.2023.27537.

[4] A. Korkmaz, T. Talan, S. Ko?unalp, y T. Iliev, �Comparison of deep learning models in automatic classification of coffee bean species�, *PeerJ Comput. Sci.*, vol. 11, abr. 2025, doi: 10.7717/peerj-cs.2759.

[5] S. Arwatchananukul, D. Xu, P. Charoenkwan, S. Aung Moon, y R. Saengrayap, �Implementing a deep learning model for defect classification in Thai Arabica green coffee beans�, *Smart Agric. Technol.*, vol. 9, p. 15, dic. 2024, doi: 10.1016/j.atech.2024.100680.

[6] M. A. Valles-Coral, C. I. Bernales-Del-Aguila, E. Benavides-Cuvas, y L. Cabanillas-Pardo, �Effectiveness of a cherry coffee sorter prototype with image recognition using machine learning�, *Rev. Bras. Cienc. Agrar.*, vol. 18, n.o 1, 2023, doi: 10.5039/AGRARIA.V18I1A2586.

[7] M. Llauce Chapo�an y C. P. Vera Molla, �Clasificaci�n de granos de caf�, usando un modelo de red neuronal convolucional�, Tesis de pregrado, Universidad Nacional Pedro Ruiz Gallo, Lambayeque, Peru, 2025. Accedido: 28 de agosto de 2025. [En l�nea]. Disponible en: https://repositorio.unprg.edu.pe/handle/20.500.12893/14644

[8] R. A. Le�n Le�n, M. A. R. Davila, B. A. Lara Guerra, A. Manosalva Ruiz, y C. A. Sotomayor Montenegro, �Development of an artificial vision algorithm with neural networks to detect coffee berry borer in coffee beans�, *Acta Sci. - Technol.*, vol. 47, n.o 1, 2025, doi: 10.4025/actascitechnol.v47i1.71113.

[9] S. Datta y N. Gupta, �A Novel Approach For the Detection of Tea Leaf Disease Using Deep Neural Network�, *Int. Conf. Mach. Learn. Data Eng.*, vol. 218, pp. 2273-2286, ene. 2023, doi: 10.1016/j.procs.2023.01.203.

[10] C. H. Hsia, Y. H. Lee, y C. F. Lai, �An Explainable and Lightweight Deep Convolutional Neural Network for Quality Detection of Green Coffee Beans�, *Appl. Sci.*, vol. 12, n.o 21, p. 10966, ene. 2022, doi: 10.3390/app122110966.

[11] P.-H. Chen, S.-Y. Jhong, y C.-H. Hsia, *Semi-Supervised Learning with Attention-Based CNN for Classification of Coffee Beans Defect*. 2022, p. 412. doi: 10.1109/ICCE-Taiwan55306.2022.9869187.

[12] K. Muchtar *et�al.*, �Edge AI-Based Detection for Defective Coffee Beans Using Deep Learning and Streamlit Framework�, *IEEE Access*, vol. 13, pp. 67977-67992, 2025, doi: 10.1109/ACCESS.2025.3561189.

[13] MIDAGRI, �Caf� peruano conquista 52 mercados en el mundo y es el sustento de 223 mil familias�. [En l�nea]. Disponible en: https://www.gob.pe/institucion/midagri/noticias/822680-cafe-peruano-conquista-52-mercados-en-el-mundo-y-es-el-sustento-de-223-mil-familias

[14] PRODUCE, �Estudio de investigaci�n sectorial del caf�, Observatorio PRODUCEmpresarial. [En l�nea]. Disponible en: https://www.producempresarial.pe/estudio-de-investigacion-sectorial-del-cafe/

[15] M. A. Zanella, M. Barrio-Conde, J. Gomez-Gil, J. M. Aguiar-Perez, M. �. P�rez-Ju�rez, y F. M. da Silva, �Deep learning to classify the ripeness of coffee fruit in the mechanized harvesting process�, *Sci. Agric.*, vol. 82, 2025, doi: 10.1590/1678-992X-2024-0156.

[16] G. T�rkmen, A. Sezen, y G. ?eng�l, �Comparative Analysis of Programming Languages Utilized in Artificial Intelligence Applications: Features, Performance, and Suitability�, *Int. J. Comput. Exp. Sci. Eng.*, vol. 10, n.o 3, pp. 461-469, 2024, doi: 10.22399/ijcesen.342.

[17] AWS, ��Qu� es Java? - Explicaci�n del lenguaje de programaci�n Java�, Amazon Web Services, Inc. Accedido: 7 de octubre de 2025. [En l�nea]. Disponible en: https://aws.amazon.com/es/what-is/java/

[18] A. Rebledano, �Qu� es C++ y su importancia en la programaci�n moderna | OpenWebinars�, OpenWebinars.net. Accedido: 8 de octubre de 2025. [En l�nea]. Disponible en: https://openwebinars.net/blog/que-es-cpp/

[19] Julia, �Julia Documentation � The Julia Language�, The Julia Project. Accedido: 11 de noviembre de 2025. [En l�nea]. Disponible en: https://docs.julialang.org/en/v1/

[20] IBM, ��Qu� es la visi�n artificial?� Accedido: 6 de octubre de 2025. [En l�nea]. Disponible en: https://www.ibm.com/es-es/think/topics/computer-vision

[21] CEPLAN, �Observatorio Nacional de Prospectiva�. [En l�nea]. Disponible en: https://observatorio.ceplan.gob.pe

[22] S. Ghazal, A. Munir, y W. S. Qureshi, �Computer vision in smart agriculture and precision farming: Techniques and applications�, *Artif. Intell. Agric.*, vol. 13, pp. 64-83, sep. 2024, doi: 10.1016/j.aiia.2024.06.004.

[23] N. Moreno-Ram�rez, F. J. J. A. Bianchi, M. R. Manzano, F. Martinez-Hofmans, y M. Dicke, �Coffee berry borer infestations and natural enemy communities shaped by altitude, shade, and management practices�, *Agric. Ecosyst. Environ.*, vol. 395, p. 109944, ene. 2026, doi: 10.1016/j.agee.2025.109944.

[24] NSW, �Coffee berry borer�, DPI Website. Accedido: 7 de octubre de 2025. [En l�nea]. Disponible en: https://www.dpi.nsw.gov.au/dpi/biosecurity/plant-biosecurity/insect-pests-and-plant-diseases/coffee-berry-borer

[25] M. A. Johnson, C. P. Ruiz-Diaz, N. C. Manoukis, y J. C. Verle Rodrigues, �Coffee Berry Borer (Hypothenemus hampei), a Global Pest of Coffee: Perspectives from Historical and Recent Invasions, and Future Priorities�, *Insects*, vol. 11, n.o 12, p. 882, dic. 2020, doi: 10.3390/insects11120882.

[26] INACAL, �GIP 101 - Gu�a de Implementaci�n de la Norma T�cnica Peruana NTP 209.027:2018 CAF�. Caf� verde. Requisitos�. Accedido: 7 de octubre de 2025. [En l�nea]. Disponible en: https://www.gob.pe/institucion/inacal/informes-publicaciones/2187944-gip-101-guia-de-implementacion-de-la-norma-tecnica-peruana-ntp-209-027-2018-cafe-cafe-verde-requisitos

[27] Federaci�n Nacional de Cafeteros de Colombia, �Aprenda a vender su caf�, Federaci�n Nacional de Cafeteros. [En l�nea]. Disponible en: https://federaciondecafeteros.org/wp/servicios-al-caficultor/aprenda-a-vender-su-cafe/

[28] INACAL, �GIP 105 - Gu�a de Implementaci�n de la Norma T�cnica Peruana NTP-ISO 8455-2018 Caf� verde. Gu�a de almacenamiento y transporte�. Accedido: 7 de octubre de 2025. [En l�nea]. Disponible en: https://www.gob.pe/institucion/inacal/informes-publicaciones/2205811-gip-105-guia-de-implementacion-de-la-norma-tecnica-peruana-ntp-iso-8455-2018-cafe-verde-guia-de-almacenamiento-y-transporte

[29] IBM, ��Qu� son las redes neuronales convolucionales?� Accedido: 7 de octubre de 2025. [En l�nea]. Disponible en: https://www.ibm.com/es-es/think/topics/convolutional-neural-networks

[30] Y. LeCun, Y. Bengio, y G. Hinton, �Deep learning�, *Nature*, vol. 521, n.o 7553, pp. 436-444, may 2015, doi: 10.1038/nature14539.

[31] A. G. Howard *et�al.*, �MobileNets: Efficient Convolutional Neural Networks for Mobile Vision Applications�, *arXiv*, p. 9, abr. 2017, doi: 10.48550/arXiv.1704.04861.

[32] X. Zhang, X. Zhou, M. Lin, y J. Sun, �ShuffleNet: An Extremely Efficient Convolutional Neural Network for Mobile Devices�, *arXiv*, p. 9, dic. 2017, doi: 10.48550/arXiv.1707.01083.

[33] M. Tan y Q. V. Le, �EfficientNet: Rethinking Model Scaling for Convolutional Neural Networks�, *arXiv*, p. 11, sep. 2020, doi: 10.48550/arXiv.1905.11946.

[34] K. Schwaber y J. Sutherland, �Scrum Guide | Scrum Guides�. [En l�nea]. Disponible en: https://scrumguides.org/scrum-guide.html

[35] S. Studer *et�al.*, �Towards CRISP-ML(Q): A Machine Learning Process Model with Quality Assurance Methodology�, *Mach. Learn. Knowl. Extr.*, vol. 3, n.o 2, pp. 392-413, jun. 2021, doi: 10.3390/make3020020.

[36] OECD, *Manual de Frascati 2015*. Fundaci�n Espa�ola para la Ciencia y la Tecnolog�a, 2018. Accedido: 7 de octubre de 2025. [En l�nea]. Disponible en: https://www.oecd.org/es/publications/manual-de-frascati-2015\_9789264310681-es.html

[37] R. Hern�ndez Sampieri, C. Fern�ndez Collado, y P. Baptista Lucio, *Metodolog�a de la investigaci�n*, 6.a ed. Espa�a: McGraw Hill Espa�a, 2014. Accedido: 26 de octubre de 2025. [En l�nea]. Disponible en: https://dialnet.unirioja.es/servlet/libro?codigo=775008

[38] M. Bunge, *La ciencia. Su m�todo y su filosof�a*. Argentina: Penguin Random House Grupo Editorial Argentina, 2014. [En l�nea]. Disponible en: https://www.google.com.pe/books/edition/La\_ciencia\_su\_m%C3%A9todo\_y\_su\_filosof%C3%ADa/ypthAgAAQBAJ?hl=es-419&gbpv=0

[39] C. A. Bernal, *Metodolog�a de la investigaci�n*, 3.a ed. Colombia: PEARSON EDUCACI�N, 2010.

[40] M. Piatiini Velthuis, M. Genero Bocco, y J. Cruz Lemus, *M�todos de investigaci�n en ingenier�a del software*. Grupo Editorial RA-MA.

# **ANEXOS**

## **ANEXO N� 01. CARTA DE ACEPTACI�N DE LA INSTITUCI�N PARA LA EJECUCI�N DEL PROYECTO**

**![](data:image/png;base64...)**

## **ANEXO N� 02**

**Entrevista dirigida a los encargados de la evaluaci�n y clasificaci�n de granos de caf� verde**

1. �Qu� m�todos de clasificaci�n de granos de caf� (manual, semiautom�tico, autom�tico) se utilizan actualmente en su empresa/cooperativa?
2. �Qu� porcentaje de la clasificaci�n de granos de caf� se realiza manualmente?
3. �Con qu� frecuencia se detectan errores en la clasificaci�n de los granos de caf� (defectuosos/normales) realizados manualmente?
4. �C�mo se eval�a la eficiencia del proceso de clasificaci�n actual?
5. �Se han observado efectos negativos en los trabajadores debido a las largas horas de clasificaci�n manual?
6. �De qu� manera la clasificaci�n actual impacta la calidad del caf� y su aceptaci�n en los mercados de exportaci�n?
7. �Existen desaf�os para cumplir con certificaciones de calidad o acceder a mercados especializados debido a la precisi�n de la clasificaci�n actual?
8. �Cu�les son los costos asociados con los errores de clasificaci�n (ej. p�rdidas de producto, reprocesamiento)?
9. �Qu� cambios cree que podr�an optimizar la precisi�n y eficiencia en la clasificaci�n de granos de caf�?
10. �Qu� expectativas tiene respecto a la modernizaci�n del proceso de clasificaci�n de caf�?
11. �Qu� limitaciones del proceso actual cree que deber�an resolverse para mejorar la calidad y confiabilidad de la clasificaci�n?

## **ANEXO N� 03**

**�rbol de causas y efectos**

![](data:image/png;base64...)

## **ANEXO N� 04**

**Clasificaci�n de defectos caf� verde (INACAL - NTP-ISO 10470:2014)**

![](data:image/png;base64...)

## **ANEXO N� 05**

**Ficha de revisi�n bibliogr�fica N�1**

|  |  |
| --- | --- |
| **Tema** | Caf� verde. Tabla de referencia de defectos. 3� Edici�n |
| **Fuente** | Norma T�cnica Peruana NTP-ISO 10470:2014 |
| **Acceso** | <https://salalecturavirtual.inacal.gob.pe:8098/datos.aspx?id=28742> |
| **Tipo de documento** | Norma t�cnica internacional adoptada por INACAL |
| **Entidad** | Instituto Nacional de Calidad (INACAL) � ISO |
| **A�o** | Revisada 2019 |
| **Resumen:**  Proporciona una lista estandarizada de defectos presentes en el caf� verde y los clasifica en cinco categor�as principales, asignando un coeficiente de impacto (0, 0.5 o 1) seg�n su influencia en la p�rdida de masa o la calidad sensorial. | |
| **Aporte a la investigaci�n:**  Define los criterios objetivos que ser�n usados para entrenar el modelo de visi�n artificial y validar la precisi�n del sistema en la identificaci�n de defectos. | |

**Ficha de revisi�n bibliogr�fica N�2**

|  |  |
| --- | --- |
| **Tema** | Implementaci�n de la Norma T�cnica Peruana para la calidad del caf� verde |
| **Fuente** | Instituto Nacional de Calidad (INACAL), GIP 101 � Gu�a de Implementaci�n de la Norma T�cnica Peruana NTP 209.027:2018 CAF�. Caf� verde. Requisitos |
| **Acceso** | <https://goo.su/FG6Gi> |
| **Tipo de documento** | Gu�a t�cnica |
| **Entidad** | Instituto Nacional de Calidad (INACAL) |
| **A�o** | 2021 |
| **Resumen:**  La gu�a detalla los criterios de aplicaci�n de la NTP 209.027:2018, orientados a estandarizar los procesos de clasificaci�n y control de calidad del caf�. Incluye especificaciones sobre los m�todos de muestreo y requisitos de humedad. | |
| **Aporte a la investigaci�n:**  Proporciona un marco t�cnico esencial para definir los par�metros de evaluaci�n y clasificaci�n del caf� en el sistema automatizado propuesto, asegurando que el prototipo se alinee con los est�ndares nacionales de calidad establecidos por INACAL | |

## **ANEXO N� 06**

Encuesta dirigida a cafetaleros: Percepci�n sobre la clasificaci�n y c�lculo del rendimiento del caf�

**Datos generales**

1. **Edad:** \_\_\_\_\_\_ a�os
2. **Sexo:** ? Masculino ? Femenino
3. **A�os de experiencia en el cultivo de caf�:** ? Menos de 5 ? 5�10 ? M�s de 10
4. **Pertenece a la cooperativa:** ? S� ? No

**Secci�n I: Clasificaci�n del caf�**

1. �Qu� aspectos se considera para clasificar su caf�?
   ? Tama�o del grano
   ? Color
   ? Presencia de defectos (broca, partidos, impurezas, etc.)
   ? Humedad
   ? Otro: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
2. �Qu� tan satisfecho est� con el m�todo de clasificaci�n actual?
   ? Muy satisfecho
   ? Satisfecho
   ? Poco satisfecho
   ? Insatisfecho
3. �Considera que la clasificaci�n manual es objetiva y precisa?
   ? S�
   ? Parcialmente
   ? No
4. En promedio, �cu�nto tiempo tarda clasificar una muestra de caf� verde?
   ? Menos de 5 minutos
   ? Entre 5 y 10 minutos
   ? M�s de 10 minutos

**Secci�n II: C�lculo del factor de rendimiento**

1. �Conoce c�mo se calcula el factor de rendimiento de su caf�?
   ? S�, completamente
   ? Algo, pero no con exactitud
   ? No lo conozco
2. �Qui�n realiza el c�lculo del rendimiento del caf� que produce?
   ? Usted mismo
   ? Personal de la cooperativa
   ? Compradores o intermediarios
   ? Otro: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
3. �Cree que el resultado del rendimiento siempre refleja la calidad real de su caf�?
   ? S�
   ? A veces
   ? No
4. �Ha tenido desacuerdos o reclamos respecto al pago por rendimiento?
   ? S�
   ? No
   Si respondi� �S�, indique la raz�n:

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

1. �Cu�nto conf�a en el proceso actual de evaluaci�n y pago por rendimiento?
   ? Conf�o plenamente
   ? Conf�o parcialmente
   ? No conf�o

**Secci�n III: Percepci�n sobre tecnolog�as automatizadas**

1. �Ha escuchado sobre sistemas autom�ticos o computarizados el c�lculo del rendimiento del caf�?
   ? S�
   ? No
2. �Estar�a dispuesto a que una m�quina clasifique autom�ticamente su caf� seg�n su calidad y rendimiento?
   ? S�
   ? No
   ? Tal vez
3. �Qu� beneficio esperar�a de un sistema automatizado? *(Puede marcar m�s de uno)*
   ? Mayor rapidez
   ? Menor error humano
   ? Transparencia en el c�lculo
   ? Pago justo
   ? Otro: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
4. �Considera que la implementaci�n de una tecnolog�a de este tipo ser�a �til?
   ? S�
   ? No
   ? No estoy seguro
5. �Estar�a dispuesto a participar en pruebas o validaciones de un sistema automatizado de clasificaci�n?
   ? S�
   ? No
