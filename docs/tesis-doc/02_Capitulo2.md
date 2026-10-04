# Capítulo 2. Fundamentos del modelo de corte

## 2.1 Problema de corte unidimensional

OICA recibe longitudes de piezas ya definidas en una cartilla y las asigna a barras de longitud conocida. Una pieza no puede dividirse entre dos barras ni obtenerse de un diámetro diferente. La aplicación no determina dimensiones estructurales del elemento construido.

Se estudia stock con varias longitudes comerciales y disponibilidad configurable, complementado por un inventario finito. Las demandas están divididas en etapas ordenadas. Un sobrante puede permanecer disponible durante varias etapas, pero solo puede consumirse una vez en cada estado de su saldo.

En el título, «nesting» se entiende como **nesting lineal**: el acomodo unidimensional de piezas a lo largo de barras, en el sentido con que se usa en la fabricación con barras y perfiles. OICA lo presenta como patrones de corte con sus repeticiones (sección 2.7). En la tipología académica de corte y empaque el término suele reservarse para piezas irregulares en dos dimensiones (Wäscher, Haußner y Schumann, 2007; *cita literal por verificar*, ficha REF-WASCHER-2007). Por eso se declara el sentido usado y se mantiene la exclusión: no se modelan áreas, rotaciones de figuras ni láminas. La fuente del uso industrial de «nesting lineal» está **pendiente de localizar** (ficha REF-NESTING-LINEAL). Tampoco se emplean modelos generativos, entrenamiento supervisado ni redes neuronales.

## 2.2 Factibilidad y objetivo

Una solución factible cumple todas las cantidades por fila de origen, longitudes, diámetros, precedencias de etapa y cantidades de inventario. La longitud de una barra original equivale a piezas más pérdida de corte, descartes y saldo reutilizable final. El cumplimiento se comprueba independientemente del algoritmo que propone el plan.

Sea B el conjunto de barras originales efectivamente utilizadas; L_b su longitud inicial; r_b su saldo reutilizable final; k_b la pérdida acumulada por corte; d_b la longitud descartada y rho_b su masa por metro. El objetivo es minimizar:

`D = 100 × sum(rho_b × (r_b + k_b + d_b)) / sum(rho_b × L_b), para b en B`.

Una barra adicional entra al denominador cuando se utiliza, con su longitud completa disponible al inicio. Los saldos que pasan entre etapas no se incorporan nuevamente al denominador. El inventario intacto queda fuera del indicador, aunque permanezca en el inventario final exportado.

Con demanda fija por diámetro, la longitud útil es constante: minimizar la longitud original utilizada minimiza el total no incorporado a piezas. Como los diámetros no comparten material, minimizar ese valor en cada diámetro minimiza la masa incorporada total y el porcentaje global. No se promedian porcentajes de diámetros con distinta masa. En empate se prefiere menor pérdida irrecuperable (corte más descarte), luego menor uso comercial y menor número de barras. La búsqueda heurística no certifica el mínimo global.

El sobrante final se denomina desperdicio respecto de este proyecto, aunque pueda reutilizarse después. No equivale automáticamente a residuo desechado ni a una pérdida económica definitiva.

## 2.3 Heurísticas de referencia

First Fit Decreasing (FFD) ordena pedidos por longitud decreciente dentro de la etapa y coloca piezas en la primera barra abierta con capacidad. Best Fit Decreasing (BFD) elige el saldo disponible más ajustado. Para stock de longitudes distintas es necesaria una regla adicional de apertura: esta implementación compara mayor longitud, menor longitud y menor residuo relativo para la pieza actual.

Cada referencia devuelve su mejor plan factible entre esas tres reglas. Esta adaptación se declara porque comparar el genético únicamente contra una heurística que siempre abre barras de 12 m confundiría la selección del catálogo con el aporte de la evolución. Ninguna referencia recibe piezas de etapas futuras por adelantado.

## 2.4 Algoritmo genético y representación

El algoritmo genético es la técnica de Inteligencia Artificial de la aplicación. Pertenece a la computación evolutiva: busca soluciones evolucionando una población de candidatos mediante selección, cruce y mutación (Holland, 1975; Goldberg, 1989; Russell y Norvig, 2021, cap. 4, §4.1.4; *páginas de Holland y Goldberg y cita literal por verificar*, fichas REF-HOLLAND-1975, REF-GOLDBERG-1989 y REF-RUSSELL-NORVIG). La selección por torneo y el elitismo que se describen a continuación son decisiones de diseño del motor de OICA. Es el único optimizador que produce el plan. Las heurísticas de la sección 2.3 y la cota de la sección 2.7 sirven de referencia o de medida.

La población contiene candidatos con genes por orden, no por pieza individual. Cada orden tiene una prioridad de colocación y una regla de elección de longitud. El decodificador respeta primero la etapa; la prioridad genética solo decide dentro de esa restricción.

La selección por torneo favorece candidatos con menor material incorporado. El cruce uniforme combina genes de ambos padres; la mutación altera prioridades o reglas de apertura; el elitismo conserva candidatos mejores. No se considera evolución válida reconstruir todos los hijos como la misma solución BFD ignorando lo heredado.

La evaluación usa lotes de barras con saldos idénticos para no materializar miles de objetos en cada candidato. El ganador se reconstruye barra por barra, se contrasta su puntuación con la evaluación agrupada y se valida su demanda e inventario. Las pruebas diferenciales comprueban que ambas representaciones produzcan la misma puntuación.

El criterio de parada depende del máximo de generaciones o del estancamiento observado. No demuestra optimalidad matemática. Un resultado mejor en una semilla no garantiza que un perfil sea superior en todas las ejecuciones.

## 2.5 Hipótesis físicas y marco normativo

Se conserva un escenario ideal con pérdida cero y cualquier sobrante positivo, y se añaden condiciones editables de pérdida y mínimo reutilizable. Las longitudes comerciales de 6, 9 y 12 m son valores iniciales de la aplicación; no se presentan como una obligación normativa exclusiva.

El Decreto 926 de 2010, que adopta el marco NSR-10, figura como vigente en la consulta de SUIN-Juriscol realizada el 13 de septiembre de 2026. Su consulta debe considerar las modificaciones incorporadas, no una copia inicial aislada. Fuente oficial: [Decreto 926 de 2010, SUIN-Juriscol](https://suin-juriscol.gov.co/viewDocument.asp?id=1918254).

Esta referencia delimita el contexto de construcción; no valida por sí sola los patrones producidos por OICA. No se ha verificado una disposición vigente que imponga un kerf o mínimo reutilizable universal. Los requisitos de longitud de desarrollo, anclaje o traslapo no equivalen a mínimos de inventario y no se trasladan a este parámetro.

La interfaz propone disco de 1 mm como espesor nominal de una herramienta para acero, según la [ficha Hilti AC-D](https://www.hilti.com.ph/c/CLS_POWER_TOOL_INSERT_7126/CLS_ABRASIVES_7126/r6473822). No equivale a una medición de pérdida real: debe calibrarse con el equipo. Para cizalla, 0 mm es una idealización explícita y editable. Una pieza igual al saldo se obtiene sin nueva separación; las demás requieren espacio para pieza y pérdida completa. No se modela refrentado ni pérdida parcial de borde.

El criterio automático conserva sobrantes cuya longitud es al menos la menor longitud demandada por diámetro, siguiendo la definición de retails de [Benjaoran y Bhokha (2013), Trim Loss Minimization for Construction Reinforcement Steel with Oversupply Constraints](https://www.joams.com/uploadfile/2013/1024/20131024100240137.pdf), DOI 10.12720/joams.1.3.313-316. Se adapta ese criterio a toda la cartilla conocida y se fija entre etapas; no se reproduce el algoritmo completo del artículo. Su parámetro Tw de pérdida admisible no es un mínimo universal de reutilización.

El usuario puede sustituir el mínimo automático por un valor común positivo en metros y aplicar descarte inmediato o al cierre de etapa. Estos escenarios formalizan decisiones de manejo de material; no demuestran viabilidad estructural de cada sobrante. El material inicial excluido se informa aparte y no se atribuye como desperdicio del proyecto.

## 2.6 Evaluación y reproducibilidad

Corrección, calidad y tiempo son dimensiones distintas. Un programa puede terminar rápidamente y producir piezas incorrectas; también puede producir un plan válido con desperdicio alto. La evaluación exige primero factibilidad, luego comparación de desperdicio y duración bajo las mismas entradas y restricciones.

Se conservan huellas de entradas y código, semilla, perfil, versión de Python, plataforma, tiempos y consumo máximo observado de memoria. Los ensayos del motor excluyen PDF y PNG para separar optimización de presentación. Cinco semillas por perfil constituyen un piloto descriptivo; no bastan para afirmar significación estadística, optimalidad o generalización a todas las cartillas.

## 2.7 Patrones de corte y cota inferior

Un **patrón de corte** es el esquema repetible de corte de una barra: de qué barra se parte, qué piezas se obtienen en cada etapa, qué pérdida y descarte se producen y qué saldo queda. Dos barras del plan comparten patrón solo si coinciden en diámetro, origen, longitud, secuencia de cortes por etapa, pérdida, descarte y saldo. El plan se presenta como «patrón × repeticiones». La vista barra por barra se conserva para la trazabilidad.

El **enfoque basado en patrones de corte** de Gilmore y Gomory formula el problema de corte como un programa lineal sobre patrones y genera patrones útiles mediante un subproblema de mochila (Gilmore y Gomory, 1961, 1963; *cita literal por verificar*, ficha REF-GG; datos bibliográficos confirmados). OICA usa este enfoque para **medir**, no para construir el plan. Con él calcula una **cota inferior**: el desperdicio por debajo del cual ningún plan puede bajar.

La cota resuelve la relajación lineal por diámetro, con estas adaptaciones del diseño de OICA, que no se atribuyen a los autores:

- considera las longitudes comerciales, el inventario adicional limitado y la pérdida por corte;
- la pérdida por corte se modela como Σ(l + e)·a ≤ L + e, porque m piezas exigen al menos m − 1 separaciones;
- relaja el orden de etapas, los saldos entre etapas y los descartes por mínimo reutilizable.

Esas relajaciones la vuelven válida pero posiblemente holgada.

La validez no depende de que el programa lineal converja. Con cualquier vector dual no negativo se obtiene una cota lagrangiana, certificada con una mochila exacta en enteros. Si el cálculo no termina de ajustarse, la cota se informa como «no ajustada», sigue siendo válida y solo es más holgada. También se informa una **cota simple**, que supone aprovechamiento perfecto: material igual a la longitud de las piezas.

La **brecha** es la diferencia, en puntos porcentuales, entre el desperdicio del plan y la cota. No es una prueba de optimalidad. Si un plan quedara por debajo de una cota válida, se trataría como error de dominio y el plan no se presentaría como válido.

## 2.8 Desperdicio admisible

El **desperdicio admisible** es el porcentaje que el usuario considera aceptable para su proyecto: por ejemplo, el que asumió en su análisis de precios unitarios o el que exige su contrato. OICA no propone un valor por defecto. Con el umbral que el usuario ingresa, informa si el plan queda dentro o lo excede, para el proyecto y para cada diámetro.

El umbral se compara con el desperdicio por masa de la sección 2.2, que incluye el saldo reutilizable final. Por eso se informan aparte la pérdida irrecuperable (corte y descartes) y el saldo reutilizable. Esta es la definición adoptada: el desperdicio es todo el material comprado que no termina convertido en piezas (INF-015). La pérdida irrecuperable se informa solo como referencia, sin juicio de cumplimiento.

No se identificó una norma colombiana que fije un porcentaje máximo de desperdicio de acero de refuerzo. El estado de cada fuente es:

- **NSR-10, Título C** (*verificada*, fichas REF-NSR10-TABLA y REF-DECRETO926): su texto completo no contiene el término «desperdicio» (búsqueda del 2 de octubre de 2026 en la copia consultada). Solo se revisó el Título C.
- **INVIAS, artículo 640** (2022; *verificada*, ficha REF-INVIAS-640): mide el acero en «kilogramo (kg) […] realmente suministrado y colocado en obra y debidamente aceptado por el interventor» (640.6), y dispone que «el precio unitario debe cubrir todos los costos por concepto de suministro, […] corte, desperdicios, doblamiento […]» (640.7). No fija un porcentaje máximo de desperdicio. Su Tabla 640-1 repite las masas por metro de la NSR-10.
- **IDU** (*pendiente de localizar*, ficha REF-IDU-ACERO).
- **Resolución 472 de 2017** de MinAmbiente, modificada por la Resolución 1257 de 2021 (*verificada* en textos compilados, ficha REF-RES472): trata los residuos de construcción y demolición. No usa el término «desperdicio»; su único porcentaje es una meta mínima de aprovechamiento de RCD para grandes generadores, no un máximo de desperdicio.

Un contrato sí puede fijar un máximo en sus especificaciones particulares. Por eso el umbral se deja al usuario.

Como referencia empírica débil, un estudio de una vivienda de dos plantas en Ecuador reporta un desperdicio total de acero de refuerzo del 6,77 %: compra de 4.860,412 kg frente a 4.552,288 kg pagados (Almendariz Rodríguez y Ortiz Aguirre, 2022, p. 38; *verificada*, ficha REF-RECIAMUC-2022). Es un solo caso, no colombiano, con una definición de desperdicio parecida pero no idéntica a la de OICA; no se usa como umbral.

