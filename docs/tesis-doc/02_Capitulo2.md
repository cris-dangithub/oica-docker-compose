## Capítulo 2

### 2. Marco Teórico

En el marco de este proyecto de grado, es esencial profundizar en la comprensión del proceso de desarrollo de software, incluyendo el análisis de las tecnologías pertinentes y su implementación efectiva en entornos productivos.   

El desarrollo de software constituye un componente fundamental en la esfera tecnológica, abarcando elementos intangibles que contrastan con los aspectos físicos del hardware. Este comprende una diversidad de programas que gestionan sistemas y engloba dependencias como bases de datos, documentos y procesos. Estos programas se materializan a través de lenguajes de programación, que actúan como sistemas de comunicación, permitiendo a los desarrolladores emitir instrucciones precisas a las computadoras. Estos lenguajes se rigen por un conjunto de reglas gramaticales que deben seguirse rigurosamente para garantizar su comprensión por parte de las máquinas ​(Luara, n.d.)​. 

Además, en este proyecto se trabajarán varios lenguajes de programación, incluyendo los siguientes: 

- Python: Python es un lenguaje de programación de alto nivel, interpretado, multiparadigma y de tipado dinámico. Python es conocido por su sintaxis clara y legible; es un lenguaje de programación poderoso y fácil de aprender, utilizado en varios campos, incluida la programación web, la ciencia de datos, la inteligencia artificial, el desarrollo de juegos y más. 

- HTML: HTML (HyperText Markup Language) es el lenguaje estándar utilizado para crear y diseñar páginas web. Es un lenguaje de marcado que define la estructura y el contenido de una página web mediante una serie de elementos y etiquetas. Estas etiquetas se utilizan para definir diferentes tipos de contenido, como encabezados, párrafos, listas, enlaces, imágenes y muchos otros elementos que pueden encontrarse en una página web. HTML utiliza una sintaxis sencilla basada en etiquetas que envuelven el contenido y proporcionan información sobre cómo debería mostrarse dicho contenido en un navegador web. HTML es un componente fundamental en el desarrollo web y se combina con otros lenguajes como CSS (Cascading Style Sheets) para estilizar y dar formato a las páginas web, y JavaScript para agregar interactividad y funcionalidades dinámicas. En conjunto, estos lenguajes permiten crear experiencias web interactivas y atractivas para los usuarios. 

- CSS: CSS (Cascading Style Sheets) es un lenguaje de hojas de estilo utilizado para definir el aspecto y el formato de los documentos HTML (o XML). CSS describe cómo se deben mostrar los elementos HTML en la pantalla, en papel o en otros medios. CSS se usa para separar el contenido estructural de un documento HTML de su presentación visual. Permite controlar aspectos como el diseño, el espaciado, los colores, las fuentes y otros estilos de presentación de los elementos de una página web. Al aplicar reglas CSS a elementos HTML específicos, los desarrolladores pueden lograr una apariencia coherente y atractiva en toda la página o sitio web. 

- JavaScript: JavaScript es un lenguaje de programación de alto nivel, interpretado y multiplataforma. Es uno de los pilares fundamentales de la web junto con HTML y CSS. JavaScript se usa principalmente en el lado del cliente (navegador web), pero también puede usarse en el lado del servidor (por ejemplo, a través de Node.js). JavaScript permite agregar interactividad y dinamismo a las páginas web. Con JavaScript, los desarrolladores pueden manipular el contenido de una página web, responder a eventos del usuario (como clics de ratón o pulsaciones de teclas), realizar peticiones a servidores web para obtener o enviar datos (a través de AJAX), y muchas otras funciones que mejoran la experiencia del usuario. JavaScript es un lenguaje versátil y poderoso que ha experimentado un crecimiento significativo en popularidad y uso en los últimos años, convirtiéndose en una habilidad indispensable para muchos desarrolladores de software. 

> Nota: Colocar NextJS

Asimismo, es importante destacar que de los lenguajes de programación emergen los frameworks, herramientas cruciales definidas por ​(Spinelli, 2023)​ como facilitadores del desarrollo de aplicaciones de manera ágil y eficiente. Estos frameworks ofrecen un conjunto de recursos, bibliotecas y estándares de codificación que pueden ser reutilizados en la creación de diversos tipos de aplicaciones, optimizando así el proceso de desarrollo. 

> Nota: El despliegue es Dockerizado.

En cuanto a las bases de datos, se optará por PostgreSQL para el almacenamiento de información. Según AWS (2023), una base de datos se utiliza para almacenar, recuperar y editar datos de manera eficiente, siendo PostgreSQL un sistema de gestión de bases de datos relacional de código abierto y libre. Se le reconoce como uno de los más avanzados y populares del mundo, utilizado en aplicaciones ​(Dorantes, 2025).​ 

> Nota: Hablar de Docker como open source

> Nota: Hablar sobre qué subrama de IA estamos usando – algoritmo genético; IA generativa VS IA predictiva (algoritmos genéticos con redes neuronales evolutivas)

### 2.1 Características de las Barras de Acero Comercial
> Nota: Hablar sobre el marco teórico de las barras de acero en Colombia.

| Características                                        | Detalle                                                                                                                         |
|--------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------|
| Longitudes Estándar                                    | 6 metros, 9 metros, 12 metros                                                                                                   |
| Diámetros Comunes                                      | 6mm, ¼", 8mm, 9mm, 3/8", 11mm, 12mm, ½", 15mm, 5/8", ¾", 7/8", 1", 1 ¼", 1 3/8"                                                 |
| Tipo de Material                                       | Barras microaleadas de alta ductilidad, sección recta y redonda, proyecciones Hi-bond                                           |
| Norma Técnica Colombiana (NTC)                         | NTC 2289 (Décima actualización): Barras corrugadas y lisas de acero de baja aleación para refuerzo de concreto.                 |
| Reglamento Colombiano de Construcción Sismo Resistente | NSR-10: Requisitos generales para amarres, pruebas, corte, doblado, traslapes y uniones de barras de acero.                     |
| Norma Internacional Aplicable                          | ASTM A706/A706M-16: Especificación estándar para barras de acero de baja aleación deformadas y lisas para refuerzo de concreto. |
| Presentación Comercial                                 | Suministradas en paquetes de 1 o 2 toneladas, en varillas                                                                       |
| Personalización                                        | Otros diámetros y longitudes pueden producirse por acuerdo con el cliente.                                                      |

- Tabla ##: Longitudes estándar y normativas aplicables a las barras de acero comercial en Colombia

La inclusión de esta tabla es siginificativa porque no solo precisa el alcance del problema del proyecto al proporcionar los parámetros específicos de las barras de acero en Colombia, sino que también establece las restricciones fundamentales para cualquier modelo de optimización. El problema de corte depende de cuánto material se tenga disponible. Además, al detallar las normativas nacionales e internacionales, se garantiza que la solución propuesta en el documento sea viable tanto legal como industrialmente. Finalmente, la tabla sirve como una referencia concisa y autorizada para el desarrollo de la aplicación, influyendo directamente en los modelos de datos, las reglas de validación y los formatos de salida. 

### 2.2 Definición y Clasificación de los Problemas de Corte (1D, 2D, Nesting)

> Nota: Buscar y hablar sobre este literal (con su respectiva bibliografía)

### 2.3  Algoritmos Clásicos para la Solución de Problemas de Corte

> Nota: Hacerlo sonar menos IA y verificar bibliografía; hablar también del método Búfalo que no es mencionado.

Para abordar la complejidad inherente de los problemas de corte, se han desarrollado diversas metodologías algorítmicas. La elección de un algoritmo depende a menudo del equilibrio entre la búsqueda de una solución óptima y la necesidad de un tiempo de cómputo razonable, especialmente en contextos industriales donde las decisiones deben tomarse rápidamente. 

- Generación de Columnas (Gilmore-Gomory): Este método, ampliamente reconocido y desarrollado por Gilmore y Gomory en la década de 1960, aborda el gran número de patrones de corte potenciales al comenzar con un conjunto limitado y generar nuevos patrones de forma dinámica. Implica la resolución iterativa de un programa lineal maestro y un problema auxiliar de la mochila para identificar patrones nuevos que mejoren el costo. Este método está teóricamente garantizado para converger a la solución óptima fraccional.    

- Programación Dinámica: Esta técnica algorítmica puede utilizarse eficazmente para resolver el subproblema de la mochila dentro del marco de la generación de columnas, o para ciertas variantes específicas del CSP 1D, descomponiendo el problema en subproblemas superpuestos más simples.    

- Heurísticas y Metaheurísticas: Dada la naturaleza NP-hard del CSP, los algoritmos heurísticos y metaheurísticos se emplean ampliamente en la práctica industrial para encontrar soluciones buenas o aceptables en un tiempo de cómputo razonable, incluso si no garantizan la optimización absoluta. Las heurísticas suelen realizar mejoras locales y "codiciosas". Las metaheurísticas, por otro lado, son métodos de exploración más generales que se aplican para optimizar una heurística subyacente. A diferencia de las heurísticas, que son específicas de un problema, las metaheurísticas son más generalizadas y pueden aplicarse de manera similar a muchos problemas diferentes. Se clasifican en metaheurísticas basadas en población (como los algoritmos inspirados en el comportamiento de enjambres o la evolución natural) y metaheurísticas basadas en iteración (inspiradas en leyes físicas, matemáticas o el comportamiento humano).    

La elección entre algoritmos exactos, como la Programación Lineal Entera con generación de columnas, y las metaheurísticas para el problema de corte de stock dependerá del equilibrio aceptable entre la optimización de la solución y el tiempo de cómputo. Esta es una consideración crítica para una aplicación web que requiere respuestas en tiempo real. Los métodos exactos, aunque garantizan la solución óptima, pueden ser prohibitivamente lentos para grandes instancias de problemas NP-hard. Las metaheurísticas, si bien no garantizan la optimización global, pueden proporcionar soluciones de muy alta calidad en un tiempo mucho más corto, lo que las hace adecuadas para entornos operativos dinámicos. Por lo tanto, la implementación de la aplicación web necesitará evaluar cuidadosamente este compromiso, posiblemente utilizando una combinación de enfoques o un enfoque híbrido, donde las metaheurísticas generen soluciones rápidas que luego puedan ser refinadas por métodos exactos para instancias más pequeñas o críticas. 

### 2.4 Desperdicios Admisibles y Optimización de Rendimiento en el Corte 

> Nota: Misma situación que en el literal anterior, hacerlo sonar menos IA y verificar bibliografía.

El concepto de "desperdicios admisibles" se enmarca en la filosofía de la manufactura esbelta (Lean Manufacturing), donde el desperdicio se define como cualquier actividad que no añade valor para el cliente. Esto va más allá de los residuos físicos e incluye cualquier cosa que consuma tiempo o reduzca la eficiencia operativa de una empresa. En este contexto, la "merma" (shrinkage) es la diferencia entre el inventario registrado y el real, y puede deberse a factores como el daño durante la fabricación, el deterioro o los errores de registro. El objetivo es minimizar estos desperdicios para reducir los tiempos de ciclo y de entrega, y aumentar la eficacia de los procesos.    

La optimización del rendimiento del material es un pilar fundamental en la industria siderúrgica. El rendimiento del material se refiere a la proporción de producto terminado utilizable en relación con el total de materia prima de entrada. Las pérdidas de rendimiento en una planta de acero pueden ocurrir debido a la formación de escoria, recortes y retales, defectos superficiales, retrabajo, oxidación, errores de fundición o laminación, y daños durante la manipulación y el transporte. Incluso una pequeña mejora porcentual en el rendimiento (por ejemplo, del 92% al 94%) puede generar ahorros masivos en operaciones de alto volumen al reducir directamente el desperdicio, minimizar el retrabajo, mejorar la eficiencia energética y asegurar una mejor utilización de materias primas costosas.    

La definición de "desperdicio admisible" requiere un marco cuantitativo que considere no solo la pérdida física del material, sino también el impacto económico y las implicaciones ambientales. Esto va más allá de un simple porcentaje de desperdicio para llegar a un análisis holístico de costo-beneficio. La justificación de esta aproximación radica en que el desperdicio no es solo una cuestión de material perdido, sino que tiene ramificaciones significativas en toda la cadena de valor. Por ejemplo, el desperdicio de material implica costos de adquisición no recuperados, costos de energía utilizados en su procesamiento inicial, y costos de disposición o reciclaje. Además, los restos de corte, si no son reutilizables, pueden generar costos de almacenamiento o la necesidad de retrabajo, lo que aumenta los gastos operativos. Desde una perspectiva ambiental, la reducción del desperdicio contribuye a la sostenibilidad al disminuir la huella de carbono y el consumo de recursos, un factor cada vez más relevante en la industria del acero. Por lo tanto, un marco cuantitativo para el "desperdicio admisible" consideraría el valor del material perdido, los costos de procesamiento asociados, los costos de manejo de residuos y el impacto ambiental, permitiendo una evaluación integral que va más allá de la simple métrica de "porcentaje de desperdicio" para determinar el nivel óptimo de desperdicio que minimiza el costo total y maximiza el valor.    


