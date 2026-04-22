# Diseño y desarrollo de una aplicación web con Inteligencia Artificial para la distribución eficiente de barras de acero comercial de 6, 9 y 12 metros en Colombia, con desperdicios admisibles mediante el enfoque basado en patrones de corte y nesting.

## Abstract

Es el mismo resumen, pero traducido al inglés. Es posible incluir el resumen en otro idioma diferente al español o al inglés, si se considera como importante dentro del tema tratado en la investigación, por ejemplo: un trabajo dedicado a problemas lingüísticos del mandarín seguramente estaría mejor con un resumen en mandarín.

### Keywords:

## Lista de figuras

> Nota: Si es requerido, se pueden incluir lista de ilustraciones, graficas, diagramas, dibujos o fotografías. Tenga presente que estas lista deben ser generadas de forma automatizada utilizando las opciones que proporciona el software de procesamiento de texto.

## Lista de tablas

> Nota: Si es requerido, se puede incluir la lista de cuadros, en caso de que se utilicen en el desarrollo del proyecto de grado o trabajo de investigación. Tenga presente que estas lista deben ser generadas de forma automatizada utilizando las opciones que proporciona el software de procesamiento de texto.

## Capítulo 1

### 1. Introducción

Actualmente, los ingenieros civiles dedican mucho tiempo al análisis y planificación de proyectos, incluyendo la evaluación de opciones para actividades específicas, como la compra de acero tras un análisis geométrico. Esta tarea puede ser engorrosa y llevar a una pérdida de tiempo valioso que podría dedicarse a otras áreas del proyecto. Sin embargo, esta actividad es importante porque influye directamente en los costos de una obra. Realizando una comparativa estimada, se tiene que el costo de 1 kg de acero para el presente año (2025) oscila entre los $3.500 y $4.500 COP; por ende, a mayores desperdicios generados de acero, se generan más costos y horas trabajadas. Por esta razón, muchos ingenieros buscan optimizar su tiempo mediante herramientas eficientes, lo que ha llevado a la creación de este aplicativo.

La idea de desarrollar esta herramienta surge de la necesidad de contar con soluciones más precisas y confiables, debido a la posibilidad de errores humanos en el proceso de selección de opciones. Este aplicativo ayudará a los ingenieros civiles y campos relacionados a seleccionar las opciones más favorables para la adquisición de barras de refuerzo de 6, 9 y 12 metros con desperdicios mínimos, al funcionar de manera automática y ahorrar tiempo valioso

El desarrollo de este software representa una innovación en el campo de la ingeniería de software y la construcción. Introducir una herramienta especializada que optimice el proceso de diseño y reduzca el desperdicio de material es un avance tecnológico importante. Esto fomentaría la búsqueda de soluciones tecnológicas más eficientes en otros campos de la ingeniería y la construcción, impulsando así la innovación en el desarrollo de software en general. Esto promovería la colaboración entre desarrolladores de software y expertos en otros campos, como ingenieros estructurales y profesionales de la construcción. La experiencia adquirida en este proyecto de integración de tecnologías se podría aplicar a otros proyectos de software que requieran la interacción de sistemas diversos. Además, este aplicativo también tiene un impacto positivo en la educación, ya que los estudiantes de asignaturas relacionadas con construcción de edificaciones, presupuestos y programación, podrán tener una experiencia mejorada y adquirir conocimientos necesarios para la planificación y desarrollo de proyectos de manera eficiente y con buenas prácticas ingenieriles en mente.

### 1.1 Antecedentes

La industria de la construcción comenzó a enfrentar desafíos de eficiencia y manejo de recursos, décadas atrás. El desperdicio de barras de acero se manifiesta en diversas formas, desde la sobrecompra de material debido a estimaciones inexactas hasta la generación de residuos debido a cortes ineficientes durante la fase de construcción. Esto ha resultado en costos económicos significativos, así como en un impacto ambiental negativo debido a la extracción y producción adicional de acero.

El problema también se relaciona con el crecimiento constante de la industria de la construcción a nivel mundial, lo que ha intensificado la demanda de barras de acero y la necesidad de abordar eficazmente su manejo. A medida que las preocupaciones ambientales y la búsqueda de prácticas más sostenibles en la construcción ganan relevancia, la reducción del desperdicio de barras de acero se ha convertido en un objetivo clave para promover una industria más eficiente y responsable.

#### 1.1.1 Antecedentes internacionales

En el contexto de la problemática del desperdicio de barras de acero en la industria de la construcción, es fundamental comprender que este desafío no se limita a las fronteras nacionales, sino que es un fenómeno de alcance internacional. A medida que la construcción se ha convertido en una empresa globalizada, los antecedentes internacionales en relación con el desperdicio de barras de acero han adquirido una importancia creciente en la búsqueda de soluciones efectivas y sostenibles.

| Título                                                                                                           | Autor(es) / Año                  | Descripción                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| ---------------------------------------------------------------------------------------------------------------- | -------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Particle swarm optimization approach for resolving the cutting stock problem                                     | (Ben Lagha Ghassen et al., 2014) | Este artículo propone un problema de stock de corte unidimensional en un gran fabricante de cables multiusos. El desafío radica en el proceso de postproducción, donde se deben satisfacer pedidos variados de conjuntos de cables de diferentes tamaños. Se desarrolló un método de solución basado en la optimización por enjambre de partículas, considerando las características específicas del problema. Se asume que el fabricante produce conjuntos de cables de la misma longitud y se aborda la reducción del desperdicio. Se presenta un modelo matemático del problema y se muestran resultados y comparaciones con otros trabajos para ilustrar la efectividad del algoritmo propuesto. |
| An efficient genetic algorithm with a corner space algorithm for a cutting stock problem in the TFT-LCD industry | (Lu & Huang, 2015)               | Este estudio aborda un problema de stock de corte bidimensional en la industria de los displays de cristal líquido con transistores de película delgada. El método de producción por lotes, que se ha utilizado hasta ahora, no es eficiente ya que aumenta los costos de producción y genera desperdicios. Se han propuesto varios enfoques de producción mixta, pero no pueden resolver eficientemente el problema debido a su complejidad computacional.                                                                                                                                                                                                                                          |

> Tabla 1: Antecedentes internacionales.

#### 1.1.2 Antecedentes nacionales

A nivel nacional, la gestión ineficiente de las barras de acero ha sido un problema recurrente en la industria de la construcción, con una serie de factores que contribuyen a este fenómeno. Estos factores pueden incluir desde prácticas de estimación poco precisas hasta la falta de regulaciones adecuadas para el manejo de los residuos de acero en proyectos de construcción. El resultado es un aumento de los costos en la ejecución de proyectos, la generación de residuos innecesarios y un impacto ambiental negativo.

| Título                                                                              | Autor(es) / Año                                                                | Descripción                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| ----------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| El Problema de patrones de corte, clasificación y enfoques.                         | Gil Gonzalez et al., 2017                                                      | La investigación aborda el problema de patrones de corte en empresas manufactureras, que implica cortar grandes rollos de material en rollos más pequeños de diferentes anchos. Este problema tiene un impacto significativo en los inventarios de productos en proceso y materias primas. Una gestión adecuada de este problema puede generar beneficios económicos y sostenibles, ya que busca equilibrar el costo del inventario y los residuos del proceso. |
| Programación lineal y algoritmos genéticos para la solución de un problema de corte | David Jaramillo Jaramillo & Jaramillo Mejía Francisco José Correa Zabala, 2008 | El proyecto propone una solución utilizando un algoritmo genético que considera los factores mencionados anteriormente. Se demuestra que el rendimiento de esta solución es superior al obtenido mediante el enfoque de programación lineal.                                                                                                                                                                                                                    |

> Tabla 2: Antecedentes nacionales.

### 1.2 Justificación

La adopción de herramientas tecnológicas en el desarrollo de las labores de planeación de proyectos puede contribuir enormemente en una mejor gestión del capital y de los recursos empleados en su construcción.

Este proyecto busca optimizar la planeación de compra del acero de refuerzo longitudinal mediante un aplicativo web que calcule la cantidad de barras de acero demandada teniendo en cuenta las longitudes comerciales de las mismas en Colombia haciendo uso de algoritmos que estimen una combinación óptima.

La propuesta se centra en la optimización de barras de acero mediante la planificación de los desperdicios generados en obra, abordando tanto beneficios económicos como ambientales derivados de la reducción de material desechado. Con un enfoque en la planeación, se busca desarrollar una herramienta que agilice el análisis de compra del acero, lo que contribuirá a mejorar la productividad y el aprovechamiento de recursos, promoviendo así una gestión más eficiente y sostenible en proyectos civiles.

### 1.3 Objetivos

#### 1.3.1 Objetivo general

- Desarrollar una solución tecnológica accesible vía web que, mediante la aplicación de algoritmos inteligentes de optimización de cortes (nesting), permita al sector de la construcción en Colombia lograr una distribución más eficiente de barras de acero de diferentes longitudes, reduciendo significativamente los costos asociados a los desperdicios de material.

- Implementar una aplicación web que integre técnicas de Inteligencia Artificial para optimizar la distribución de barras de acero comercial de 6, 9 y 12 metros en Colombia, a través de un enfoque basado en patrones de corte y algoritmos de nesting, con el fin de minimizar desperdicios dentro de márgenes admisibles y mejorar la eficiencia en los procesos de corte y utilización del material.

#### 1.3.2 Objetivos específicos

- Calcular la eficiencia en el análisis de la cantidad de barras de acero necesarias para cada longitud de compra.

- Estimar el tiempo de duración de la actividad de análisis de compra de acero mientras se aumenta la cantidad de opciones viables al considerar niveles aceptables de desperdicios generados.

- Registrar la reutilización de los desperdicios de barras de acero de proyectos anteriores como complemento a optimizar los recursos dispuestos para la ejecución de proyectos futuros.

- Desarrollar un sistema de análisis de compra que minimice los errores y limitaciones del análisis manual en la optimización de barras de acero para proyectos civiles, mediante la implementación de herramientas automatizadas y metodologías eficientes.

- Evaluar la eficiencia de los algoritmos empleados en la aplicación haciendo comparativas con proyectos reales de la construcción.

### 1.4 Estructura del documento

En el presente documento, se enlista los capítulos correspondientes del 1 al 5, de los cuales, como ya se evidenció anteriormente, el capítulo 1 abordó todo lo relacionado a introducción, justificación y objetivos del proyecto; en el capitulo 2 se verá lo correspondiente al marco teórico, se enunciará una investigación
