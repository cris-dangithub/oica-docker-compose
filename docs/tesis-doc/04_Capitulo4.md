# Capítulo 4. Resultados del modelo secuencial

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
