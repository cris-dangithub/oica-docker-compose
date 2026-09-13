# Capítulo 4. Resultados del modelo secuencial

Las secciones 4.1–4.7 conservan la evidencia del piloto `secuencial-1` y su E2E.
La ampliación con pérdida y mínimo reutilizable se evalúa por separado en 4.8.

## 4.1 Casos, protocolo y evidencia

Se evaluaron exclusivamente 001 (92 piezas, 16 órdenes, tres diámetros) y 002
(67.443 piezas, 137 órdenes, cinco diámetros y 13 etapas). El ensayo utilizó catálogo
comercial ilimitado de 6, 9 y 12 m, sin inventario adicional inicial, pérdida por
corte cero y transferencia de cualquier sobrante positivo entre etapas.

Se ejecutaron FFD y BFD adaptados y cinco semillas (0–4) por perfil genético.
Los datos completos se conservan en
[`tests/benchmarks/2026-09-13-agrupado.jsonl`](../../tests/benchmarks/2026-09-13-agrupado.jsonl).
Cada registro contiene huellas de código y archivo, Python, plataforma, semilla,
perfil, métricas y resultado del validador. El entorno fue Python 3.12 dentro del
worker Docker existente en WSL2. Los tiempos corresponden al motor, incluyendo
referencias heurísticas, inicialización, búsqueda, materialización y validación;
excluyen lectura del XLSX, cola, HTTP y generación de artefactos.

Los resultados del caso histórico de 683 piezas se retiraron de este capítulo por
decisión de alcance del autor. Tampoco se comparan directamente los porcentajes
anteriores calculados en metros con el indicador nuevo ponderado por masa.

## 4.2 Desperdicio y tiempo

Las heurísticas se ejecutaron una vez por caso, pues son deterministas. Las filas
AG resumen cinco semillas: mediana y rango observado. No son intervalos de confianza.

### Caso 001

| Método/perfil | n | Tiempo mediano (s) | Rango de tiempo (s) | Desperdicio mediano (%) | Rango de desperdicio (%) |
|---|---:|---:|---:|---:|---:|
| FFD | 1 | 0.002 | 0.002–0.002 | 5.1542 | 5.1542–5.1542 |
| BFD | 1 | 0.003 | 0.003–0.003 | 5.1542 | 5.1542–5.1542 |
| AG rapido | 5 | 0.020 | 0.017–0.024 | 5.1542 | 5.1542–5.1542 |
| AG balanceado | 5 | 0.085 | 0.083–0.148 | 5.1542 | 4.4411–5.1542 |
| AG profundo | 5 | 0.406 | 0.271–0.457 | 4.4411 | 4.4411–5.1542 |

### Caso 002

| Método/perfil | n | Tiempo mediano (s) | Rango de tiempo (s) | Desperdicio mediano (%) | Rango de desperdicio (%) |
|---|---:|---:|---:|---:|---:|
| FFD | 1 | 1.145 | 1.145–1.145 | 9.4898 | 9.4898–9.4898 |
| BFD | 1 | 1.036 | 1.036–1.036 | 9.4898 | 9.4898–9.4898 |
| AG rapido | 5 | 1.435 | 1.379–1.510 | 8.0616 | 7.9716–8.1675 |
| AG balanceado | 5 | 3.337 | 3.129–3.793 | 7.9467 | 7.9337–7.9951 |
| AG profundo | 5 | 7.245 | 5.648–9.150 | 7.9404 | 7.9344–7.9483 |

## 4.3 Interpretación

En 002, los tres perfiles genéticos mejoraron el desperdicio respecto de las
referencias bajo el mismo modelo secuencial. El balanceado y el profundo presentan
resultados próximos; el profundo requiere más tiempo y no domina todas las semillas.
El tamaño de la población no garantiza por sí solo una solución mejor.

En 001, varias ejecuciones igualaron la heurística y otras mejoraron el resultado.
Por tanto, se retira la afirmación anterior de que los tres perfiles siempre
convergen al mismo óptimo. No se dispone de un certificado de optimalidad para
ninguna de las dos cartillas completas.

La mejora de rendimiento más importante fue agrupar saldos equivalentes durante
la evaluación y materializar solo el ganador. Las regresiones incluyen 60 casos
pequeños generados con semilla fija en los que se compara puntuación agrupada con
puntuación de barras individuales. El motor también exige esa coincidencia al
reconstruir cada solución ganadora.

La serie diagnóstica `2026-09-13-secuencial.jsonl` corresponde a la versión anterior
que evaluaba barras individualmente. Fue detenida deliberadamente antes de completar
el perfil profundo al introducir la agrupación; no es una ejecución fallida del
modelo final ni una muestra completa. Se conserva como evidencia del cambio.

## 4.4 Factibilidad y conservación

Los 34 resultados finales pasaron el validador independiente. En cada uno se comprobaron cantidades por fila, longitudes, diámetro, orden de etapas, capacidad de barras, consumo finito de inventario y saldo final. El número de piezas fue exactamente 92 o 67.443 según la cartilla.

El balance cuenta una barra raíz una sola vez, aunque produzca cortes en varias
etapas. El inventario intacto queda fuera del indicador de desperdicio. Los casos
pequeños adicionales comprueban stock finito, importación/exportación, sobrantes
menores de 0,50 m, pedidos repetidos y discrepancias de masa.

## 4.5 Alcance de las verificaciones de software

Las pruebas aisladas HTTP/worker usan SQLite en memoria y broker simulado; ejecutan
el cálculo y generan Excel e inventario reales. También se comprobaron PDF y PNG
pequeños. En una comprobación adicional de 002 (rápido, semilla 0), el motor tardó
1,64 s y la generación más relectura/verificación de artefactos tardó 13,11 s.
Excel, inventario XLSX, PDF y PNG ocuparon juntos 969.077 bytes. Se comprobó que la
hoja Cortes conserva las 67.443 piezas por fila de origen y que el inventario
reimportado satisface el validador. Los archivos temporales se retiraron al terminar;
se conserva el resumen en
[`2026-09-13-artefactos-002.jsonl`](../../tests/benchmarks/2026-09-13-artefactos-002.jsonl).

Las 74 pruebas de backend y las comprobaciones de tipos y lint del frontend pasaron.
La migración 003 se ensayó con PostgreSQL en tablas temporales y rollback. Estas
verificaciones aisladas se complementaron después con el ensayo local de la sección 4.7. Los 13,11 s incluyen comprobaciones
adicionales del ensayo y no equivalen al tiempo de generación del worker en producción.

La estimación temporal es una funcionalidad distinta de estas mediciones. Hasta
contar con cinco muestras comparables de procesamiento completo, la interfaz
muestra calibración pendiente. Los segundos de esta tabla no se cargan como si
fueran tiempos end-to-end medidos en producción.

## 4.6 Limitaciones y conclusiones del piloto

El objetivo de menos de un minuto se alcanzó en los ensayos del motor de 002 bajo
el entorno descrito. No constituye una garantía para otra máquina, otros inventarios
o el flujo completo con artefactos. La memoria registrada es el máximo acumulado
del proceso de ensayo, incluyendo librerías; no una medición aislada por generación.

Cinco semillas y dos cartillas permiten una comparación descriptiva de estos casos,
no una generalización estadística a todos los proyectos. No se midieron ejecución
física, tiempos de operario, costos de compra ni impacto ambiental. Tampoco se
valida la procedencia de los datos únicamente mediante una huella digital.

El resultado demuestra factibilidad del modelo ideal y evidencia una contribución
medible del genético en 002 respecto de las referencias implementadas. La revisión
con el director, la documentación de procedencia y la reproducción de la aplicación
completa en otra máquina siguen siendo condiciones de cierre académico.


## 4.7 Validación de la aplicación local completa

El 13 de septiembre de 2026 se construyeron las tres imágenes, se aplicó la
migración 003 y se activó la entrega en `http://localhost`. Las 74 pruebas pasaron
dentro de la imagen nueva; el frontend pasó compilación, tipos y lint. El ensayo
utilizó PostgreSQL, Redis, Celery, Nginx y Chrome de Windows reales.

La carga de 002 desde la interfaz mostró calibración inicial, progreso y eventos
WebSocket, redirigió a la tabla y permitió descargar los cuatro artefactos. El
reprocesamiento desde esa tabla creó otra versión. No se detectaron excepciones
JavaScript durante ambas operaciones.

| Versión 002 | Perfil | Procesamiento registrado (s) | Desperdicio final por masa (%) |
|---|---|---:|---:|
| 1 | Balanceado | 9,76 | 7,9951 |
| 2 | Profundo | 19,97 | 7,9344 |

Estos tiempos incluyen cálculo y generación de artefactos según el registro de la
aplicación; no son las mediciones del motor de la sección 4.2 ni incluyen toda la
latencia de red, cola y confirmación SQL. La espera medida desde Enviar hasta la
tabla en la primera carga fue 20,15 s. No se comparan directamente los tiempos de
este ensayo integrado con los de la serie aislada como si las condiciones fueran idénticas.

Una auditoría por lectura reconstruyó las barras a partir del JSON persistido y
contrastó la hoja Cortes y el inventario exportado. Ambas versiones conservaron
las 67.443 piezas, sus diámetros y etapas, la capacidad disponible y la métrica de
masa. Una carga de control reutilizó una pieza #3 de 0,01 m del inventario exportado
sin catálogo comercial, obteniendo el saldo esperado. Esta comprobación técnica
no prueba que un sobrante de esa longitud pueda aprovecharse físicamente en obra.

001 pasó carga HTTP, polling, WebSocket, descargas y reprocesamiento. Con cinco
muestras comparables, el endpoint de estimación pasó de calibración pendiente a
un rango empírico de 1,04–2,94 s. Ese rango no es una garantía de duración.

Evidencia: [integración local](../../tests/benchmarks/2026-09-13-integracion-local.json),
[ensayo de navegador](../../tests/benchmarks/2026-09-13-navegador-002.json) y
[captura de la aplicación](../../tests/benchmarks/2026-09-13-app-local.png).
También se conservaron identificadores de imágenes y dependencias instaladas.
La reproducción en otra máquina y la revisión académica continúan pendientes.

## 4.8 Ampliación: pérdida y mínimo reutilizable (`secuencial-2`)

La [matriz final](../../tests/benchmarks/2026-09-13-fisico-matriz-final.jsonl)
contiene **136 ensayos completos y válidos**, ejecutados en serie: cuatro escenarios,
dos cartillas, dos referencias deterministas y cinco semillas por cada uno de tres
perfiles genéticos. Se comprobó la unicidad de las 136 combinaciones, la cantidad
exacta de piezas y el balance de las cuatro categorías de material.
La huella común del código del runner es
`70e4beafe72950336f36f158ac3e52fd8a1ea1578a9551b9f34f15c95346e5e0`.

Escenarios: ideal (ambos desactivados), solo pérdida (disco 1 mm), solo mínimo
(automático inmediato) y ambos activos. Catálogo y demanda coinciden con el piloto
anterior. Los tiempos incluyen motor y validación; no lectura, cola ni artefactos.
No se ejecutaron simultáneamente otras pruebas intensivas de esta sesión durante
la matriz final. Los archivos `fisico-ideal`, `fisico-solo-perdida`,
`fisico-solo-minimo` y `fisico-ambos` son ensayos de desarrollo y no se mezclan con
esta serie temporal final. La memoria máxima acumulada del proceso fue 115,55 MiB,
incluidas librerías y ejecuciones previas; no representa consumo aislado por semilla.

### Caso crítico 002

Se muestra mediana (mínimo–máximo). AG: cinco semillas por fila; FFD/BFD: una
ejecución por referencia. Los rangos son descriptivos, no intervalos de confianza.

| Escenario | Método | Tiempo (s) | Desperdicio (%) |
|---|---|---:|---:|
| Ideal | FFD | 1,30 | 9,4898 |
| Ideal | BFD | 1,35 | 9,4898 |
| Ideal | AG rápido | 1,74 (1,67–1,98) | 8,0616 (7,9716–8,1675) |
| Ideal | AG balanceado | 3,71 (3,51–4,13) | 7,9467 (7,9337–7,9951) |
| Ideal | AG profundo | 8,63 (6,67–10,24) | 7,9404 (7,9344–7,9483) |
| Solo pérdida | FFD | 1,57 | 10,1300 |
| Solo pérdida | BFD | 1,52 | 10,1300 |
| Solo pérdida | AG rápido | 2,04 (1,94–2,14) | 8,9632 (8,9282–9,1259) |
| Solo pérdida | AG balanceado | 5,34 (4,38–5,68) | 8,8952 (8,8384–8,9236) |
| Solo pérdida | AG profundo | 9,92 (9,57–11,49) | 8,8851 (8,8795–8,9095) |
| Solo mínimo | FFD | 1,72 | 9,4898 |
| Solo mínimo | BFD | 1,59 | 9,4898 |
| Solo mínimo | AG rápido | 2,16 (2,15–2,37) | 8,0846 (7,9818–8,3152) |
| Solo mínimo | AG balanceado | 6,59 (6,12–6,90) | 7,9527 (7,9319–7,9894) |
| Solo mínimo | AG profundo | 19,77 (14,04–21,16) | 7,9332 (7,9262–7,9373) |
| Ambos | FFD | 1,62 | 10,1300 |
| Ambos | BFD | 1,51 | 10,1300 |
| Ambos | AG rápido | 2,27 (2,09–2,53) | 8,9656 (8,9626–9,0028) |
| Ambos | AG balanceado | 5,68 (5,31–6,20) | 8,8935 (8,8602–8,9058) |
| Ambos | AG profundo | 14,34 (10,85–15,50) | 8,8811 (8,8288–8,8907) |

Los mínimos automáticos de 002 son #3: 0,37 m; #4: 1,05 m; #5: 1,35 m;
#6: 1,65 m; #7: 3,50 m. Proceden de las longitudes de demanda, no de una ley.
Con ambos checks, rápido/semilla 0 utiliza 152.039,571 kg de barras raíz y produce
138.412,93033 kg en piezas, 45,488045 kg de pérdida, 2.822,999238 kg descartados
y 10.758,153387 kg reutilizables al final. Su suma conserva la masa original.

### Regresión 001

FFD y BFD obtienen 5,1542 % en los cuatro escenarios, en menos de 0,01 s cada uno.
Para AG se conservan todas las semillas, también cuando igualan las referencias:

| Escenario | Perfil | Tiempo mediano (s) | Rango (s) | Desperdicio mediano (%) | Rango (%) |
|---|---|---:|---:|---:|---:|
| Ideal | Rápido | 0,03 | 0,03–0,03 | 5,1542 | 5,1542–5,1542 |
| Ideal | Balanceado | 0,11 | 0,10–0,19 | 5,1542 | 4,4411–5,1542 |
| Ideal | Profundo | 0,44 | 0,30–0,46 | 4,4411 | 4,4411–5,1542 |
| Solo pérdida | Rápido | 0,03 | 0,02–0,04 | 5,1542 | 5,1542–5,1542 |
| Solo pérdida | Balanceado | 0,12 | 0,12–0,15 | 5,1542 | 4,4411–5,1542 |
| Solo pérdida | Profundo | 0,39 | 0,38–0,46 | 5,1542 | 4,4411–5,1542 |
| Solo mínimo | Rápido | 0,04 | 0,03–0,05 | 5,1542 | 5,1542–5,1542 |
| Solo mínimo | Balanceado | 0,27 | 0,17–0,35 | 4,4411 | 4,4411–5,1542 |
| Solo mínimo | Profundo | 0,60 | 0,57–0,90 | 4,4411 | 4,4411–4,4411 |
| Ambos | Rápido | 0,03 | 0,02–0,04 | 5,1542 | 5,1542–5,1542 |
| Ambos | Balanceado | 0,24 | 0,15–0,32 | 5,1542 | 4,4411–5,1542 |
| Ambos | Profundo | 0,64 | 0,59–0,97 | 4,4411 | 4,4411–5,1542 |

El aumento de desperdicio al reservar kerf en 002 no indica por sí solo un defecto:
el problema factible cambia. La comparación del aporte genético debe hacerse
dentro del mismo escenario. El mínimo automático no promete reducir el material
total: clasifica saldos que no satisfacen ninguna pieza conocida. El desempate por
pérdida irrecuperable también modifica la trayectoria estocástica de la búsqueda.

Los controles de [cizalla](../../tests/benchmarks/2026-09-13-fisico-control-cizalla.jsonl)
y [fin de etapa](../../tests/benchmarks/2026-09-13-fisico-control-fin-etapa.jsonl)
añaden 12 ensayos válidos (FFD, BFD y AG rápido/semilla 0 en cada cartilla y control).
No se presentan como una comparación de cinco semillas. Las pruebas pequeñas
comprueban el caso manual donde descarte inmediato y al fin de etapa sí requieren
distinta cantidad de barras; la igualdad de resultados en estos controles automáticos
no demuestra equivalencia general de ambas políticas.

La matriz valida el modelo implementado, no cortes ejecutados en taller. La
calibración de la herramienta, revisión del director y reproducción externa siguen
pendientes. El E2E de 4.7 pertenece a la versión anterior; la integración nueva
se verificó posteriormente y se describe en 4.9.

La [verificación final de artefactos](../../tests/benchmarks/2026-09-13-fisico-artefactos-final.jsonl)
generó y releyó los cuatro archivos por cartilla: 95.090 bytes para 001 y 1.619.999
para 002. En este último, generación y comprobaciones adicionales tomaron 16,35 s;
no equivalen al tiempo exclusivo de generación del worker. Se verificaron las siete
hojas del Excel, demanda exacta, inventario reimportado, firma PDF y límite de la
imagen. Las 83 pruebas backend pasan; las siete de integración API se repitieron
tras reforzar la auditoría del JSON persistido. Tipos y lint frontend pasan.
Las dos versiones anteriores de 002 también pasaron la auditoría del validador
nuevo mediante lectura de PostgreSQL y Excel, conservando sus métricas originales.

## 4.9 Integración local de las condiciones configurables

Tras recuperar margen de disco se construyeron y activaron las tres imágenes
nuevas, con seis servicios saludables. Se reutilizaron dependencias; el espacio
libre en C: se mantuvo cerca de 8,3 GB. Los 83 tests pasaron dentro de la imagen
nueva y frontend completó compilación, tipos y lint.

Chrome de Windows, operado mediante CDP, verificó los checks predeterminados,
los mínimos calculados de 002, carga balanceada y reprocesamiento profundo desde
los controles de la interfaz. Se recibieron 33 frames WebSocket sin excepciones
JavaScript y se descargaron Excel, PDF, PNG e inventario de ambas versiones.

| Caso/versión | Perfil | Tiempo registrado (s) | Desperdicio (%) |
|---|---|---:|---:|
| 002 / 1 | Balanceado | 18,01 | 8,8602 |
| 002 / 2 | Profundo | 24,77 | 8,8811 |

Ambas versiones del archivo local id 38 pasan auditoría independiente de JSON,
Excel e inventario: 67.443 piezas, pérdida y descartes correctos, masa conservada.
El profundo no mejora la semilla balanceada en este ejemplo; tampoco se prometía
esa dominancia. Los tiempos son los registrados por la aplicación, no latencia
completa del navegador ni tiempos exclusivos del motor.

001, id 39 y nombre técnico smoke.xlsx, completó HTTP, polling, WebSocket, filtros,
descargas y reproceso; sus dos versiones auditadas conservan 92 piezas y 5,1542 %.
Las instantáneas son idénticas entre versiones en ambos casos. También se auditaron
las dos versiones históricas de 002, id 36, sin modificarlas.

Evidencia: [integración de condiciones físicas](../../tests/benchmarks/2026-09-13-fisico-integracion-local.json),
[navegador 002](../../tests/benchmarks/2026-09-13-fisico-navegador-002.json) y
[HTTP/WS 001](../../tests/benchmarks/2026-09-13-fisico-http-001.json).
Estos resultados cierran la validación local de software; mantienen los límites
de calibración física, revisión académica y reproducibilidad externa ya declarados.
