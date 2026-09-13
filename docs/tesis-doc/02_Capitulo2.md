# Capítulo 2. Fundamentos del modelo de corte

## 2.1 Problema de corte unidimensional

OICA recibe longitudes de piezas ya definidas en una cartilla y las asigna a barras de longitud conocida. Una pieza no puede dividirse entre dos barras ni obtenerse de un diámetro diferente. La aplicación no determina dimensiones estructurales del elemento construido.

Se estudia stock con varias longitudes comerciales y disponibilidad configurable, complementado por un inventario finito. Las demandas están divididas en etapas ordenadas. Un sobrante puede permanecer disponible durante varias etapas, pero solo puede consumirse una vez en cada estado de su saldo.

El término «nesting» no se usa aquí para sugerir una implementación de distribución bidimensional: no se modelan áreas, rotaciones de figuras o láminas. Tampoco se emplean modelos generativos, entrenamiento supervisado ni redes neuronales.

## 2.2 Factibilidad y objetivo

Una solución factible cumple todas las cantidades por fila de origen, longitudes, diámetros, precedencias de etapa y cantidades de inventario. La longitud de una barra original equivale a la suma de piezas obtenidas durante todo el proyecto y su saldo final. El cumplimiento se comprueba independientemente del algoritmo que propone el plan.

Sea B el conjunto de barras originales efectivamente utilizadas; L_b su longitud inicial; r_b su saldo final y rho_b su masa por metro. El objetivo es minimizar:

`D = 100 × sum(rho_b × r_b) / sum(rho_b × L_b), para b en B`.

Una barra adicional entra al denominador cuando se utiliza, con su longitud completa disponible al inicio. Los saldos que pasan entre etapas no se incorporan nuevamente al denominador. El inventario intacto queda fuera del indicador, aunque permanezca en el inventario final exportado.

Con demanda fija por diámetro, la longitud útil es constante: minimizar la longitud original utilizada minimiza su saldo final. Como los diámetros no comparten material, minimizar ese valor en cada diámetro minimiza la masa incorporada total y el porcentaje global. No se promedian porcentajes de diámetros con distinta masa.

El sobrante final se denomina desperdicio respecto de este proyecto, aunque pueda reutilizarse después. No equivale automáticamente a residuo desechado ni a una pérdida económica definitiva.

## 2.3 Heurísticas de referencia

First Fit Decreasing (FFD) ordena pedidos por longitud decreciente dentro de la etapa y coloca piezas en la primera barra abierta con capacidad. Best Fit Decreasing (BFD) elige el saldo disponible más ajustado. Para stock de longitudes distintas es necesaria una regla adicional de apertura: esta implementación compara mayor longitud, menor longitud y menor residuo relativo para la pieza actual.

Cada referencia devuelve su mejor plan factible entre esas tres reglas. Esta adaptación se declara porque comparar el genético únicamente contra una heurística que siempre abre barras de 12 m confundiría la selección del catálogo con el aporte de la evolución. Ninguna referencia recibe piezas de etapas futuras por adelantado.

## 2.4 Algoritmo genético y representación

La población contiene candidatos con genes por orden, no por pieza individual. Cada orden tiene una prioridad de colocación y una regla de elección de longitud. El decodificador respeta primero la etapa; la prioridad genética solo decide dentro de esa restricción.

La selección por torneo favorece candidatos con menor material incorporado. El cruce uniforme combina genes de ambos padres; la mutación altera prioridades o reglas de apertura; el elitismo conserva candidatos mejores. No se considera evolución válida reconstruir todos los hijos como la misma solución BFD ignorando lo heredado.

La evaluación usa lotes de barras con saldos idénticos para no materializar miles de objetos en cada candidato. El ganador se reconstruye barra por barra, se contrasta su puntuación con la evaluación agrupada y se valida su demanda e inventario. Las pruebas diferenciales comprueban que ambas representaciones produzcan la misma puntuación.

El criterio de parada depende del máximo de generaciones o del estancamiento observado. No demuestra optimalidad matemática. Un resultado mejor en una semilla no garantiza que un perfil sea superior en todas las ejecuciones.

## 2.5 Hipótesis físicas y marco normativo

Se adoptan explícitamente pérdida por corte cero y reutilización de cualquier sobrante positivo. Las longitudes comerciales de 6, 9 y 12 m son valores iniciales de la aplicación; no se presentan como una obligación normativa exclusiva.

El Decreto 926 de 2010, que adopta el marco NSR-10, figura como vigente en la consulta de SUIN-Juriscol realizada el 13 de septiembre de 2026. Su consulta debe considerar las modificaciones incorporadas, no una copia inicial aislada. Fuente oficial: [Decreto 926 de 2010, SUIN-Juriscol](https://suin-juriscol.gov.co/viewDocument.asp?id=1918254).

Esta referencia delimita el contexto de construcción; no valida por sí sola los patrones producidos por OICA. No se ha verificado una disposición vigente que permita deducir de ella pérdida por corte cero o ausencia de mínimo reutilizable. Por tanto, esas decisiones se presentan exclusivamente como hipótesis ideales del estudio. No se incorporan valores de NTC, resoluciones o tolerancias cuya edición, vigencia y aplicación no hayan sido comprobadas.

## 2.6 Evaluación y reproducibilidad

Corrección, calidad y tiempo son dimensiones distintas. Un programa puede terminar rápidamente y producir piezas incorrectas; también puede producir un plan válido con desperdicio alto. La evaluación exige primero factibilidad, luego comparación de desperdicio y duración bajo las mismas entradas y restricciones.

Se conservan huellas de entradas y código, semilla, perfil, versión de Python, plataforma, tiempos y consumo máximo observado de memoria. Los ensayos del motor excluyen PDF y PNG para separar optimización de presentación. Cinco semillas por perfil constituyen un piloto descriptivo; no bastan para afirmar significación estadística, optimalidad o generalización a todas las cartillas.
