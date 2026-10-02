# Capítulo 3. Metodología e implementación

## 3.1 Diseño del estudio

Se desarrolla y evalúa un artefacto de ingeniería para planificación de cortes de acero. La secuencia de trabajo es: formalización de reglas de dominio, pruebas independientes de factibilidad, implementación, comparación controlada de algoritmos e interpretación de resultados. No se presenta la elección de herramientas de programación como método de investigación por sí misma.

Se emplean dos cartillas facilitadas por el autor, provenientes de una obra de construcción en Colombia cuyos datos son confidenciales y se presentan anonimizados: 001 como caso pequeño de regresión y 002 como caso principal de rendimiento. La procedencia documental detallada y las condiciones de uso de los datos deben integrarse en los anexos antes de la entrega académica. Los archivos originales se conservan sin modificaciones.

## 3.2 Arquitectura

La interfaz Next.js envía la cartilla, catálogo e inventario al backend Flask. El backend valida y guarda la configuración antes de encolar una tarea Celery. PostgreSQL conserva cargas y versiones; Redis transporta tareas y progreso; Nginx publica la aplicación. Docker Compose es el mecanismo de operación local; el despliegue VPS es una capacidad secundaria.

No intervienen AWS Lambda, S3 ni URLs prefirmadas en este flujo. El módulo `backend/cutting/` contiene el mismo núcleo usado por el worker y los comandos de experimentación. No hay entrenamiento de modelos: el algoritmo genético realiza búsqueda para cada problema recibido.

## 3.3 Preparación de datos

La cartilla contiene pedido, diámetro, longitud, cantidad, masa y, opcionalmente, grupo de ejecución. Cada fila tiene identidad interna independiente del nombre del pedido. Se rechazan cantidades fraccionarias, valores no finitos, longitudes no positivas, diámetros ausentes y grupos inválidos. Solo se omiten filas sin datos de demanda.

La masa lineal por diámetro se verifica entre filas. Solo se tolera una diferencia relativa de una millonésima para absorber representación numérica de fórmulas XLSX; una diferencia mayor exige corregir la cartilla. Las longitudes se convierten a una escala entera obtenida de la precisión de entrada y no se redondean durante la asignación.

La ausencia de columna de grupos equivale a una sola etapa. Si existe, cada pedido debe tener un entero positivo. Las etapas se recorren en orden numérico y los diámetros se mantienen separados.

## 3.4 Inventario y planificación secuencial

El catálogo comercial permite longitudes y cantidades por diámetro; una cantidad nula significa disponibilidad ilimitada. El inventario adicional es finito y se carga con columnas `diametro`, `longitud_m`, `cantidad`. Las existencias pueden usarse desde la primera etapa.

Una barra utilizada conserva identidad de origen. Su saldo puede abastecer etapas posteriores hasta agotarse o descartarse por mínimo. Los inventarios de candidatos genéticos no comparten estado mutable. El inventario final combina existencias finitas elegibles no utilizadas con saldos reutilizables y se exporta en el mismo esquema de entrada. El inventario inicial bajo el mínimo se registra aparte, sin cargarlo como desperdicio generado.

Las condiciones se guardan al cargar la cartilla: activación de pérdida, proceso, pérdida uniforme en milímetros, activación de mínimo, modo automático/manual y momento del descarte. La UI inicia ambos checks activos, disco 1 mm, mínimo automático e inmediato. Clientes API que omiten el objeto conservan el escenario ideal. La escala entera incluye la precisión de la pérdida y del mínimo. El umbral automático se calcula por diámetro sobre toda la demanda y no cambia entre etapas.

Cada reprocesamiento conserva la configuración original. El inventario final es proyectado; importar sus valores en otro proyecto requiere verificar disponibilidad física. La aplicación no registra automáticamente cortes realmente ejecutados en obra.

## 3.5 Búsqueda y verificación independiente

Se utiliza selección por torneo, cruce uniforme, mutación de genes y elitismo, con candidatos de prioridades y reglas de apertura. Cada candidato evalúa todas las etapas del diámetro; el indicador no suma repetidamente los sobrantes intermedios.

La evaluación agrupa saldos idénticos. Solo el candidato ganador se materializa como barras individuales con cortes agrupados por pedido y etapa. Se exige coincidencia exacta entre la puntuación agrupada y la reconstruida. Un validador independiente comprueba demanda, capacidad, origen, saldos e inventario final antes de guardar un resultado como válido.

Perfiles `(población, generaciones máximas, generaciones sin mejora)`:

| Perfil | Población | Generaciones máximas | Estancamiento |
|---|---:|---:|---:|
| Rápido | 20 | 30 | 8 |
| Balanceado | 50 | 100 | 15 |
| Profundo | 100 | 200 | 25 |

El presupuesto de cinco minutos es un objetivo de desempeño. No se usa como aborto automático ni se afirma que una mayor población siempre mejore la solución. Las soluciones imposibles no se aceptan a cambio de una penalización finita de fitness.

## 3.6 Protocolo experimental

1. Identificar cartilla y configuración mediante SHA-256; registrar semilla y versión del motor.
2. Ejecutar FFD y BFD adaptados a las mismas etapas, inventario y catálogo.
3. Ejecutar el genético con semillas 0, 1, 2, 3 y 4 en cada perfil.
4. Comprobar automáticamente todos los pedidos y saldos en cada ejecución.
5. Registrar duración de optimización, fases internas, porcentaje de desperdicio por masa, barras utilizadas y máximo de memoria observado.
6. Presentar mediana y rango por perfil. No seleccionar únicamente la mejor semilla.
7. Comprobar integración y reportes de forma separada, sin incluir su tiempo en la comparación del motor.

Para `secuencial-2` se repite la comparación en cuatro escenarios: ambos checks
desactivados, solo pérdida, solo mínimo y ambos activos. Se usa disco 1 mm y
mínimo automático inmediato cuando corresponda. Las referencias y el AG reciben
exactamente las mismas condiciones. Cizalla y descarte al fin de etapa se revisan
como controles adicionales. Se informa por separado masa en piezas, corte,
descarte y reutilizable final, sin presentar el material excluido como desperdicio.

Los comandos y contratos de API se documentan en `docs/CORTE_SECUENCIAL.md`. Los resúmenes de mediciones viven en `tests/benchmarks/`; cada línea identifica código y entrada. El ensayo previo por barras individuales es un diagnóstico de rendimiento y no se mezcla con el ensayo final de evaluación agrupada.

## 3.7 Seguimiento y estimación temporal

El progreso informa operación, diámetro y tiempo transcurrido. Para estimar duración se requieren cinco ejecuciones anteriores del mismo problema, perfil, código/entorno y selección de artefactos. Antes se muestra «calibrando». El rango observado se amplía un 20 %; es una estimación empírica, no un intervalo estadístico de confianza.

Si una ejecución excede ese rango, la aplicación lo comunica y evita mostrar un tiempo restante ficticio. El tiempo de cola se excluye. Las publicaciones de progreso se limitan a una por segundo salvo transiciones de diámetro/fase; la base recibe actualizaciones cada cinco segundos o cambios explícitos de estado.

## 3.8 Artefactos y límites de validación

Excel contiene barras raíz (con su patrón), cortes por etapa/pedido, inventario, métricas, descartes, inventario inicial excluido y parámetros con referencias, además de las hojas del análisis de la sección 3.9. PDF y PNG presentan el plan por patrones de corte, acotados a los más repetidos, y remiten al Excel para el plan completo. El error de generación de archivos se distingue del error del algoritmo: un plan válido no se anuncia como una entrega íntegra si falló un artefacto.

Las pruebas HTTP/worker aisladas emplean SQLite en memoria y un broker simulado, con generación real de archivos pequeños. No sustituyen la verificación final de migraciones PostgreSQL, Celery, Redis, WebSocket y frontend con las imágenes de la entrega. La reproducibilidad en una segunda máquina y la revisión con el director deben documentarse antes de presentar la tesis.

## 3.9 Análisis posterior a la optimización

Desde la versión `analisis-1`, después de que el algoritmo genético entrega un plan y el validador independiente lo acepta, el worker ejecuta un análisis único. Ese análisis no construye ni modifica el plan: el motor sigue siendo `secuencial-2`. Calcula seis grupos de indicadores, que se guardan con cada versión.

1. **Admisibilidad.** El usuario puede ingresar un umbral opcional de desperdicio admisible, entre 0 y 100 %, sin valor por defecto.
   - El umbral se guarda junto a la configuración del archivo, fuera de los parámetros de corte. Así no cambia la huella del problema ni la estimación de tiempo.
   - Al reprocesar puede conservarse, cambiarse o quitarse; cada versión guarda el umbral con el que se evaluó.
   - El estado es «dentro de lo admisible», «excede» o «sin evaluar», para el proyecto y para cada diámetro. Un empate cuenta como «dentro».
   - El umbral se compara con el desperdicio por masa de la sección 2.2. Esa comparación está pendiente de confirmación por el director (INF-015).
2. **Pérdidas.** Se separan la pérdida irrecuperable (corte y descartes) y el saldo reutilizable final, en masa y en porcentaje. También se informa el aprovechamiento, igual a 100 % menos el desperdicio.
3. **Resumen de compra.** Barras por diámetro, longitud y origen, con masa y aprovechamiento. Las barras de inventario adicional se listan aparte y no cuentan como compra. Por construcción, el total coincide con las barras del plan.
4. **Patrones de corte.** Se agrupan las barras idénticas, según la definición de la sección 2.7.
   - Cada patrón recibe un identificador determinista, `P-<diámetro>-<nnn>`.
   - Se comprueba que la suma de repeticiones sea igual al número de barras y que expandir los patrones reproduzca exactamente la demanda.
   - En la cartilla 002, perfil balanceado, 13.955 barras se agrupan en 136 patrones.
5. **Cota inferior.** Se calcula por diámetro con generación de columnas (sección 2.7).
   - El maestro lineal se resuelve con HiGHS (`scipy.optimize.linprog`, scipy 1.18.1) y el subproblema con una mochila exacta en enteros escalados.
   - La validez se certifica con una cota lagrangiana. Se informa también la cota simple, y se toma la mayor de las dos.
   - El cálculo tiene un presupuesto de 2 s por diámetro y 4 s por plan. Si se agota, la cota sigue siendo válida y se marca «no ajustada».
   - Si scipy falta o el solver falla, la cota se informa como «no disponible», con su motivo, y el plan se entrega igualmente.
   - Si el desperdicio de un plan quedara por debajo de una cota válida, la versión se registra como error de dominio y no se presenta como válida.
6. **Avisos de masa nominal.** La masa por metro de cada diámetro de la cartilla se contrasta con la NSR-10, Título C, Tabla C.3.5.3-2 (verificada). Una diferencia mayor a 1 % produce un aviso que no bloquea el plan. Ese 1 % es una decisión de diseño, no un requisito normativo.

**Dónde se presentan.** Los resultados aparecen en cinco hojas nuevas del Excel (Admisibilidad, Resumen de compra, Patrones, Cota y Avisos), en el PDF y en una página de detalle por proyecto. Esa página compara las versiones por perfil, tiempo, desperdicio, umbral, admisibilidad y verificación. El PNG se titula «Nesting lineal por patrones de corte» y dibuja las piezas de los patrones más repetidos.

**Efecto en la estimación de tiempo.** Un cambio de código reinicia la calibración de tiempos de la sección 3.7, porque la clave de entorno firma el módulo de corte. El umbral no la afecta.

**Validación.** Se verificaron cuatro puntos:

- **Pruebas automatizadas.** 124 pruebas automatizadas pasan dentro de la imagen reconstruida. Para la cota, las pruebas comparan:
  - un caso analítico;
  - instancias pequeñas resueltas por fuerza bruta, donde la cota nunca supera el óptimo;
  - certificados con duales aleatorios, que también deben ser válidos;
  - el fallo simulado del solver.
- **Regresión.** Se repitieron los 136 ensayos y los 12 controles de `secuencial-2` con el código nuevo. El resultado fue 0 diferencias en todas las métricas no temporales ([regresión](../../tests/benchmarks/2026-10-02-regresion-analisis-1.jsonl)). Su único fin es comprobar que el plan no cambió: no constituye evidencia nueva.
- **Cota sobre los ensayos registrados.** Se calculó sin volver a ejecutar el algoritmo genético (sus resultados se presentan en el capítulo 4).
- **Tiempo (SC-007).** Se compararon el código previo y el nuevo, intercalados en el mismo contenedor, con la cartilla 002 en perfil balanceado. El tiempo de motor, análisis y artefactos crece un 8,8 % en mediana (24,58 s frente a 26,75 s), por debajo del límite de 25 % ([comparación](../../tests/benchmarks/2026-10-02-sc007-comparacion.json)).
- **Prueba de punta a punta** con la aplicación y el navegador:
  - umbral inválido rechazado antes de encolar;
  - paso de «excede» a «dentro» con el plan idéntico;
  - comparación de cuatro versiones;
  - aviso de masa y versiones históricas sin el análisis, mostradas como «no disponible»;
  - sin violaciones de accesibilidad axe a 1440, 820 y 390 px.

