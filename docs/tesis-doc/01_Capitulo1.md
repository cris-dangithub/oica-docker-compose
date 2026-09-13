# Desarrollo y evaluación de una aplicación local para la planificación secuencial de cortes de acero mediante algoritmos genéticos e inventario reutilizable

## Resumen

Se desarrolla una aplicación local para planificar cortes unidimensionales de acero por etapas, con inventario comercial y adicional y transferencia de sobrantes entre etapas. El algoritmo genético utiliza una representación por órdenes y evalúa saldos agrupados, mientras un validador independiente comprueba demanda, capacidad e inventario. El modelo permite configurar pérdida por corte y longitud mínima reutilizable, conservando el escenario ideal anterior como control. Se evalúan dos cartillas de 92 y 67.443 piezas mediante heurísticas de referencia y cinco semillas por perfil genético. La comparación distingue material incorporado a piezas, pérdida por corte, descarte y sobrante reutilizable final. El piloto ideal inicial produjo planes válidos en menos de diez segundos de motor en el caso principal; los escenarios ampliados se presentan por separado en el capítulo 4. Los tiempos del motor excluyen artefactos y no constituyen garantía de optimalidad, validación física o generalización a otras obras.

## Abstract

This work develops a local application for sequential one-dimensional steel cutting with commercial and additional stock and reuse of remaining material across execution stages. A genetic algorithm represents orders rather than individual pieces and evaluates grouped stock balances. An independent validator checks demand, capacity and inventory conservation. Cutting loss and minimum reusable length are configurable, while the previous ideal model remains a control scenario. Two schedules containing 92 and 67,443 pieces are evaluated against adapted heuristics using five seeds per genetic profile. The comparison distinguishes finished pieces, cutting loss, discarded material and final reusable remnants. The initial ideal-model pilot produced feasible plans in less than ten seconds of engine time on the larger case; the extended scenarios are reported separately in Chapter 4. Engine timings exclude artifact generation and do not establish optimality, physical validation or generalization to other construction projects.

Palabras clave: corte unidimensional; acero; algoritmo genético; inventario; planificación por etapas.

## Capítulo 1

### 1. Introducción

La planificación de cortes transforma una cartilla de despiece en una asignación de piezas a barras disponibles. Para que el plan sea utilizable debe conservar cantidades, longitudes y diámetros, y respetar la disponibilidad temporal del material. La sola reducción de cantidad de barras no mide adecuadamente el aprovechamiento cuando las longitudes y diámetros son diferentes.

Este proyecto aborda esa planificación mediante una aplicación local que permite configurar el catálogo comercial, incorporar inventario adicional y trasladar sobrantes entre etapas del mismo proyecto. Su evaluación distingue la corrección de los planes, el porcentaje de desperdicio final por masa y el tiempo de cálculo. No se atribuyen ahorros económicos, mejoras de productividad de operarios o beneficios ambientales sin mediciones específicas.

### 1.1 Antecedentes

> Material heredado pendiente de revisión bibliográfica: deben verificarse autores, fuentes originales y alcance de las comparaciones de las tablas. Estas reseñas no sustentan por sí solas la elección del algoritmo ni demuestran resultados de OICA.

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

Una cartilla de despiece indica qué piezas requiere la obra, pero no determina por sí sola su asignación a barras comerciales y existencias disponibles. Cuando la ejecución se divide en etapas, esa asignación también debe conservar los sobrantes que podrán utilizarse más adelante y evitar contabilizar una misma barra como material nuevo en cada etapa.

La contribución propuesta consiste en una herramienta local cuyo plan de corte sea verificable por pedido, diámetro, etapa y barra de origen. El algoritmo genético busca mejorar el aprovechamiento del material; su uso se justifica mediante comparación experimental con heurísticas sometidas a las mismas restricciones, sin presumir optimalidad ni superioridad universal.

El valor para ingeniería civil se evaluará por la satisfacción de la cartilla, la conservación del inventario, el desperdicio final por masa y el tiempo requerido para producir un plan. La reducción potencial de compras, costos o impacto ambiental requiere información adicional de precios, operación y ejecución real; no se presenta como resultado demostrado por esta investigación.

### 1.3 Objetivos

#### 1.3.1 Objetivo general

Desarrollar y evaluar una aplicación local para planificar cortes unidimensionales de acero por etapas, utilizando algoritmos genéticos e inventario reutilizable, con el propósito de reducir el porcentaje de material no aprovechado al finalizar el proyecto.

> Reformulación autorizada por el autor el 13 de septiembre de 2026, pendiente de revisión formal con el director. No se afirma aprobación institucional del nuevo título.

#### 1.3.2 Objetivos específicos

1. Formalizar la demanda por pedido, diámetro y etapa, la disponibilidad de barras comerciales y adicionales, y la transferencia de sobrantes entre etapas.
2. Implementar un algoritmo genético con evaluación del desperdicio final por masa y un validador independiente de demanda, capacidad y disponibilidad.
3. Incorporar importación y exportación compatibles de inventario, planes de corte trazables y seguimiento del tiempo de procesamiento.
4. Evaluar corrección, desperdicio, tiempo y variabilidad del algoritmo usando las cartillas 001 y 002, comparándolo con heurísticas sometidas a las mismas restricciones.
5. Documentar los resultados reproducibles y los límites del modelo, distinguiendo planificación ideal de ejecución física en obra.

#### 1.3.3 Alcance y pregunta evaluable

¿En qué medida el algoritmo genético mejora el porcentaje final de material no aprovechado respecto de heurísticas de referencia, y qué costo temporal añade, para las cartillas 001 y 002 bajo un mismo modelo secuencial?

El caso principal es 002: 67.443 piezas, 137 órdenes, cinco diámetros y 13 etapas. El caso 001 contiene 92 piezas y 16 órdenes. Los ejemplos históricos de 683 piezas no forman parte de esta evaluación. No se infieren resultados generales para toda obra a partir de dos cartillas.

Los grupos se ejecutan en orden numérico; los sobrantes disponibles de grupos anteriores pueden abastecer grupos posteriores del mismo diámetro. El catálogo predeterminado de 6, 9 y 12 m es configurable, y puede complementarse con existencias finitas importadas. El inventario de salida es una proyección del plan: su disponibilidad física debe comprobarse antes de emplearlo en otro proyecto.

El modelo permite configurar pérdida uniforme por corte y mínimo reutilizable, además de conservar el escenario ideal con ambos desactivados. Supone material compatible dentro de cada diámetro y longitudes de despiece suministradas como dato de entrada. No calcula diseño estructural, ganchos, anclajes, traslapos, degradación, manejo o transporte. No certifica cumplimiento normativo ni cuantifica ahorros monetarios o ambientales sin datos específicos. Las referencias iniciales son editables y requieren calibración física.

El indicador principal es el porcentaje de masa sobrante al finalizar el proyecto sobre la masa de las barras efectivamente utilizadas, contando cada barra original una sola vez. La rapidez deseada es aproximadamente un minuto y, preferiblemente, no más de cinco minutos de optimización; estos valores son objetivos de evaluación, no abortos temporales ni garantías universales.

### 1.4 Estructura del documento

El capítulo 1 delimita el problema, los objetivos y el alcance. El capítulo 2 presenta el modelo de corte, los conceptos utilizados y sus límites. El capítulo 3 describe la implementación y el protocolo de evaluación. El capítulo 4 presenta los resultados reproducibles de las cartillas 001 y 002 y las limitaciones del piloto. La revisión bibliográfica, la validación con el director y el cierre formal del documento siguen pendientes.
