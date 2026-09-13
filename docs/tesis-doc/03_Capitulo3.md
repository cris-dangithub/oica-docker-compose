# Capítulo 3. Metodología e implementación

## 3.1 Diseño del estudio

Se desarrolla y evalúa un artefacto de ingeniería para planificación de cortes de acero. La secuencia de trabajo es: formalización de reglas de dominio, pruebas independientes de factibilidad, implementación, comparación controlada de algoritmos e interpretación de resultados. No se presenta la elección de herramientas de programación como método de investigación por sí misma.

Se emplean dos cartillas facilitadas por el autor: 001 como caso pequeño de regresión y 002 como caso principal de rendimiento. La procedencia documental detallada y las condiciones de uso de los datos deben integrarse en los anexos antes de la entrega académica. Los archivos originales se conservan sin modificaciones.

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

Excel contiene barras raíz, cortes por etapa/pedido, inventario, métricas, descartes, inventario inicial excluido y parámetros con referencias. PDF y PNG muestran muestras acotadas y remiten al Excel para el plan completo. El error de generación de archivos se distingue del error del algoritmo: un plan válido no se anuncia como una entrega íntegra si falló un artefacto.

Las pruebas HTTP/worker aisladas emplean SQLite en memoria y un broker simulado, con generación real de archivos pequeños. No sustituyen la verificación final de migraciones PostgreSQL, Celery, Redis, WebSocket y frontend con las imágenes de la entrega. La reproducibilidad en una segunda máquina y la revisión con el director deben documentarse antes de presentar la tesis.
