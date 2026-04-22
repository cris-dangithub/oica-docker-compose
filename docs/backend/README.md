# Análisis del Servicio Backend — OICA

Documento de referencia con el análisis exhaustivo del backend Flask + Celery + Algoritmo Genético.
Generado para reutilización futura en documentación académica, agentes de IA, o desarrollo.

---

## 1. Estructura de Directorios

```
services/backend/
├── server.py                       # Servidor Flask + Socket.IO (producción)
├── celery_worker.py                # Tarea Celery (procesamiento asíncrono)
├── main.py                         # Entry point legacy (sincrónico, sin Celery)
├── barras_estandar.json            # Configuración de barras comerciales
├── requirements.txt                # Dependencias Python (copia de config/backend/)
├── Pipfile / Pipfile.lock          # Pipenv (desincronizado con requirements.txt)
├── models/
│   ├── __init__.py                 # Inicializa SQLAlchemy (db = SQLAlchemy())
│   └── uploaded_file.py            # Modelos: UploadedFile (1:N) → ProcessingResult
├── genetic_algorithm/
│   ├── __init__.py                 # Constantes globales + configuración por defecto
│   ├── engine.py                   # Motor principal del AG
│   ├── chromosome.py               # Clases Patron y Cromosoma
│   ├── population.py               # Inicialización: FFD, BFD, óptimo, aleatorio
│   ├── fitness.py                  # Función fitness multi-componente ponderada
│   ├── selection.py                # Selección: torneo, ruleta, elitista
│   ├── crossover.py                # Cruce: 1 punto, 2 puntos, basado en piezas
│   ├── mutation.py                 # Mutación: 6 operadores
│   ├── metrics.py                  # RegistroEvolucion, diversidad, convergencia
│   ├── input_adapter.py            # Adaptadores de entrada (DataFrame → formato AG)
│   ├── output_formatter.py         # Formateadores de salida (Cromosoma → JSON/DataFrame)
│   ├── optimal_analyzer.py         # Análisis exhaustivo de casos homogéneos
│   └── chromosome_utils.py         # Utilidades de manipulación de cromosomas
├── utils/
│   └── artifact_generator.py       # Generación de Excel, PDF (WeasyPrint), PNG (matplotlib)
├── tests/                          # Tests unitarios (unittest)
├── data/filestore/                 # Almacenamiento de artefactos (runtime)
├── server_old.py                   # Versión anterior del servidor (legacy)
├── convertir_cartilla.py           # Script de conversión (utilidad)
├── demo_algoritmo_genetico.py      # Demo del AG
├── demo_integracion.py             # Demo de integración
├── test_optimal_analysis.py        # Test del analizador óptimo
├── *.md                            # Documentos de planificación (TAREAS_*, PLAN_*)
├── cartilla_acero.csv              # Datos de ejemplo
├── cortes_ejemplo.csv              # Datos de ejemplo
├── Planilla_Cartilla.xlsx          # Plantilla de ejemplo
└── ultimo_resultado.json           # Último resultado (debug)
```

---

## 2. Dependencias (requirements.txt)

**Python 3.12** (obligatorio — psycopg2-binary 2.9.9 incompatible con 3.13)

| Paquete | Versión | Propósito |
|---------|---------|-----------|
| `flask` | 3.1.0 | Framework web |
| `flask-cors` | 5.0.1 | CORS |
| `flask-sqlalchemy` | 3.1.1 | ORM |
| `flask-socketio` | 5.5.1 | WebSocket server |
| `python-socketio` | 5.12.1 | Motor Socket.IO |
| `celery` | 5.4.0 | Cola de tareas asíncronas |
| `redis` | 5.2.1 | Cliente Redis |
| `gevent` | 24.11.1 | Async mode para WebSocket (**solo backend**) |
| `gevent-websocket` | 0.10.1 | WebSocket con gevent |
| `psycopg2-binary` | 2.9.9 | Driver PostgreSQL |
| `sqlalchemy` | 2.0.36 | ORM |
| `pandas` | 2.2.3 | Manipulación de datos |
| `openpyxl` | 3.1.5 | Lectura/escritura Excel |
| `numpy` | 2.2.1 | Cálculos numéricos |
| `matplotlib` | 3.10.0 | Gráficas PNG |
| `weasyprint` | 63.1 | Generación PDF desde HTML |
| `werkzeug` | 3.1.3 | Utilidades HTTP |

**Nota:** El worker usa `eventlet` en vez de `gevent` (ver `config/celery_worker/requirements.txt`).

---

## 3. Puntos de Entrada

### server.py — Servidor Flask + Socket.IO (583 líneas)

**Configuración:**
- `SQLALCHEMY_DATABASE_URI` desde env `DATABASE_URL` o default
- `MAX_CONTENT_LENGTH`: 16 MB
- CORS: `origins="*"` (todas las rutas)
- Socket.IO: `async_mode='gevent'`, `cors_allowed_origins="*"`
- Redis Pub/Sub para bridge Worker → WebSocket
- Filestore: `data/filestore/`
- Extensiones permitidas: `.xlsx`, `.csv`

**9 endpoints HTTP:**

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/health` | Health check con verificación de BD (`SELECT 1`) |
| POST | `/upload` | Carga archivo + encola tarea Celery. Form data: `file`, `perfil`. Retorna `task_id` (202) |
| GET | `/files` | Lista archivos con filtros (`search`, `status`, `perfil`, `date_from`, `date_to`) + paginación. Enriquece con progreso de Redis |
| GET | `/file/<id>` | Detalle de archivo con todas sus versiones |
| DELETE | `/file/<id>` | Elimina archivo + versiones + directorios UUID del filestore |
| POST | `/reprocess/<id>` | Reprocesa con nuevo perfil. Body JSON: `{perfil}`. Crea nueva versión |
| GET | `/descargar-excel/<uuid>` | Descarga Excel de resultados |
| GET | `/descargar-pdf/<uuid>` | Descarga PDF con plan de corte |
| GET | `/descargar-imagen/<uuid>` | Descarga PNG con gráfica |
| GET | `/status/<task_id>` | Fallback: consulta estado de tarea desde Celery backend |

**3 eventos WebSocket:**

| Evento | Dirección | Descripción |
|--------|-----------|-------------|
| `connect` | Client → Server | Log + emit `connected` |
| `disconnect` | Client → Server | Log |
| `subscribe_task` | Client → Server | `join_room(task_id)` + emit `subscribed` |
| `task_update` | Server → Client | Progreso en tiempo real (emitido por Redis listener) |

**Thread daemon Redis Pub/Sub:**
- `redis_pubsub_listener()` — thread background que escucha `task_progress:*`
- Parsea JSON y emite `task_update` al room WebSocket correspondiente

### celery_worker.py — Tarea Celery (619 líneas)

**Configuración Celery:**
```python
celery = Celery('oica_tasks', broker=REDIS_URL, backend=REDIS_URL)
celery.conf: task_serializer='json', timezone='America/Bogota',
             task_track_started=True, task_send_sent_event=True
```

**Función `publish_progress(task_id, progress, state, message)`:**
1. Publica a canal Redis Pub/Sub `task_progress:{task_id}`
2. Almacena en clave Redis con TTL de 5 minutos (para consultas HTTP)

**Función `validate_content(df)`:**
- Valida columnas numéricas: `Longitud total (m)` (0.1-100), `Masa total (kg)` (0.01-50000), `Cantidad` (>0)
- Retorna lista de errores

**Tarea principal `process_file_task(self, uploaded_file_id, perfil)`:**

Pipeline completo con 9 fases:

| Fase | Progreso | Descripción |
|------|----------|-------------|
| 1. VALIDATING | 10% | Lee Excel, valida estructura |
| 2. Validar columnas | 10-15% | 6 columnas obligatorias |
| 3. Validar contenido | 15-20% | Tipos, rangos, positivos |
| 4. VALIDATED | 20% | Validación exitosa |
| 5. PROCESSING | 20-70% | Algoritmo genético con callbacks granulares |
| 6. GENERATING | 70-90% | Generar Excel + PDF + PNG |
| 7. Guardar BD | 90% | Crear ProcessingResult |
| 8. SUCCESS | 100% | Completado |
| Error | 0% | FAILURE con detalle |

**Columnas obligatorias del Excel:**
```
N° Orden, Elemento, N° de Barra, Longitud total (m), Cantidad, Masa total (kg)
```

**Perfiles de optimización:**

| Perfil | Población | Generaciones |
|--------|-----------|--------------|
| `rapido` | 20 | 30 |
| `balanceado` | 50 | 100 |
| `profundo` | 100 | 200 |

**Callback de progreso granular — rangos:**
- 20-25%: Inicialización de población
- 25-30%: Evaluación inicial
- 30-70%: Bucle evolutivo (con sub-operaciones: selección, cruce, mutación, evaluación)
- 70-100%: Generación de artefactos y guardado

### main.py — Entry point legacy (~1163 líneas)

Servidor Flask sincrónico con el AG ejecutándose inline (sin Celery). Tiene su propia copia del algoritmo, configuraciones, y generación de PDF. **Ya no se usa en producción** pero sigue funcional.

**Inconsistencia:** Llama al perfil más pesado `intensivo` en vez de `profundo`.

---

## 4. Modelos de Datos (SQLAlchemy)

### UploadedFile (`uploaded_files`)

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id` | Integer PK | |
| `file_path` | String(500) | Ruta al archivo temporal |
| `file_name` | String(255) | Nombre del archivo |
| `file_extension` | String(10) | Extensión sin punto |
| `document_number` | String(50) | [DEPRECATED] Auto-rellenado desde filename |
| `processing_status` | String(20) | Default `'processing'`. Estados: uploaded, validating, processing, generating_artifacts, completed, error_validation, error_processing, error_generation |
| `status_details` | String(255) | Mensaje descriptivo del estado |
| `created_at` | DateTime | |
| `updated_at` | DateTime | Con `onupdate` |

**Relación:** `results` → `ProcessingResult` (1:N, CASCADE, ordenado por `version_number` desc)

**Método `to_dict(include_results=False)`:** Serialización con campos de compatibilidad (`filename`, `status`, `perfil` del último resultado).

### ProcessingResult (`processing_results`)

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id` | Integer PK | |
| `uploaded_file_id` | Integer FK | Referencia a `uploaded_files.id` |
| `version_number` | Integer | Versionamiento (1, 2, 3...) |
| `storage_uuid` | String(36) UNIQUE | UUID v4 para directorio de artefactos |
| `resultados` | JSON | Patrones de corte como JSONB |
| `metricas` | JSON | Métricas del AG como JSONB |
| `cartilla` | JSON | Excel original como JSONB |
| `graph_image_path` | String(500) | Path a PNG |
| `pdf_path` | String(500) | Path a PDF |
| `excel_path` | String(500) | Path a Excel |
| `result_status` | String(20) | `completed`, `error_generation`, `processing` |
| `error_message` | Text | Detalle del error |
| `perfil_usado` | String(20) | rapido, balanceado, profundo |
| `processing_time_seconds` | Numeric(10,2) | Tiempo de procesamiento |
| `pdf_template_version` | String(20) | Versión de la plantilla PDF |
| `created_at` / `updated_at` | DateTime | |

---

## 5. Algoritmo Genético — Paquete `genetic_algorithm/`

### 5.1. Constantes y Configuración (`__init__.py`, 59 líneas)

```python
LONGITUD_MINIMA_DESPERDICIO_UTILIZABLE = 0.5  # metros

CONFIG_OPERADORES_DEFAULT = {
    'tamaño_poblacion': 50,
    'estrategia_inicializacion': 'hibrida',
    'proporcion_heuristicos': 0.6,
    'metodo_seleccion': 'torneo',
    'tamaño_torneo': 3,
    'tasa_cruce': 0.8,
    'estrategia_cruce': 'un_punto',
    'tasa_mutacion_individuo': 0.2,
    'tasa_mutacion_gen': 0.1,
    'operaciones_mutacion': ['cambiar_origen', 'reoptimizar', 'mover_pieza'],
    'reparar_hijos_cruce': True
}

CONFIG_CICLO_EVOLUTIVO_DEFAULT = {
    'max_generaciones': 100,
    'criterio_convergencia': 'generaciones_sin_mejora',
    'generaciones_sin_mejora_max': 20,
    'fitness_objetivo': None,
    'tiempo_limite_segundos': 300,
    'diversidad_minima': 0.01,
    'elitismo': True,
    'tamaño_elite': 2,
    'estrategia_reemplazo': 'elitismo',
    'logging_habilitado': True,
    'logging_frecuencia': 10,
    'guardar_mejor_por_generacion': True,
    'paralelizar_evaluacion': False,
    'cache_fitness': False
}
```

### 5.2. Representación del Cromosoma (`chromosome.py`, 219 líneas)

**Clase `Patron`** — Un patrón de corte para una barra específica:

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| `origen_barra_longitud` | float | Longitud de la barra origen (metros) |
| `origen_barra_tipo` | str | `'estandar'` o `'desperdicio'` |
| `piezas_cortadas` | List[Dict] | Lista de `{id_pedido, longitud_pieza, cantidad_pieza_en_patron}` |
| `desperdicio_patron_longitud` | float | Calculado automáticamente |
| `es_desperdicio_utilizable` | bool | `True` si desperdicio >= 0.5m |

Métodos: `agregar_pieza()`, `obtener_longitud_utilizada()`, `es_valido()`, `_calcular_desperdicio()`

**Clase `Cromosoma`** — Una solución completa (lista de patrones):

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| `patrones` | List[Patron] | Lista de patrones de corte |

Métodos: `agregar_patron()`, `calcular_desperdicio_total()`, `obtener_desperdicios_utilizables()`, `contar_barras_estandar()`, `contar_desperdicios_usados()`, `longitud_total_desperdicios_usados()`, `clonar()` (deepcopy)

### 5.3. Inicialización de Población (`population.py`, 604 líneas)

**4 estrategias de generación de individuos:**

| Estrategia | Función | Descripción |
|------------|---------|-------------|
| FFD | `generar_individuo_heuristico_ffd()` | First Fit Decreasing: ordena piezas por longitud desc, coloca en primera barra que quepa |
| BFD | `generar_individuo_heuristico_bfd()` | Best Fit Decreasing: como FFD pero busca el mejor ajuste (menor desperdicio) |
| Óptimo | `generar_individuo_con_analisis_optimo()` | Analiza casos homogéneos con solución exhaustiva, FFD para el resto |
| Aleatorio | `generar_individuo_aleatorio_con_reparacion()` | Asignación aleatoria + reparación vía BFD |

**Estrategia híbrida (default):**
- `num_optimos = min(tamaño_poblacion // 4, 3)` — Máximo 3 individuos óptimos
- `num_heuristicos = (población - óptimos) * 0.6` — 60% heurísticos (FFD/BFD alternados)
- `num_aleatorios` — El resto, aleatorios con reparación
- Se mezcla aleatoriamente al final

**Función `reparar_cromosoma()`:** Extrae todas las piezas, agrupa idénticas, reconstruye con BFD.

### 5.4. Función Fitness (`fitness.py`, 295 líneas)

**Fitness multi-componente ponderado (minimización — menor es mejor):**

```
fitness = desperdicio * 10.0
        + faltantes * 10000.0
        + sobrantes * 5000.0
        + num_barras * 50.0
        - desperdicios_usados * 30.0
```

| Componente | Peso | Descripción |
|------------|------|-------------|
| `peso_desperdicio` | 10.0 | Penalización por metro de desperdicio |
| `penalizacion_faltantes` | 10000.0 | Por metro de longitud faltante (no cumplir demanda) |
| `penalizacion_sobrantes` | 5000.0 | Por metro de longitud en exceso |
| `penalizacion_num_barras_estandar` | 50.0 | Por cada barra estándar utilizada |
| `bonificacion_uso_desperdicios` | 30.0 | Bonificación por metro de desperdicio reutilizado |

**Funciones auxiliares:**
- `calcular_penalizacion_faltantes()` — Compara sumario del cromosoma vs demanda
- `calcular_penalizacion_sobrantes()` — Detecta piezas producidas en exceso
- `calcular_penalizacion_barras_usadas()` — Cuenta barras estándar
- `calcular_bonificacion_uso_desperdicios()` — Longitud total de desperdicios usados como origen
- `analizar_componentes_fitness()` — Desglose para debugging

### 5.5. Selección (`selection.py`, 296 líneas)

**3 métodos de selección:**

| Método | Función | Descripción |
|--------|---------|-------------|
| Torneo | `seleccion_torneo()` | Selecciona `tamaño_torneo` individuos aleatorios, elige el mejor fitness (default: 3) |
| Ruleta | `seleccion_ruleta()` | Probabilidad inversamente proporcional al fitness. Transformación: `aptitud = max_fitness - fitness + ε` |
| Elitista | `seleccion_elitista()` | Selecciona los N mejores directamente |

**Funciones adicionales:**
- `seleccionar_padres()` — Dispatcher que elige el método según configuración
- `seleccionar_parejas_para_cruce()` — Emparejamiento aleatorio o secuencial
- `calcular_presion_selectiva()` — Métrica de presión selectiva

### 5.6. Cruce (`crossover.py`, 412 líneas)

**3 operadores de cruce:**

| Operador | Función | Descripción |
|----------|---------|-------------|
| Un punto | `cruce_un_punto()` | Punto de corte aleatorio en cada padre, intercambia segmentos |
| Dos puntos | `cruce_dos_puntos()` | Dos puntos de corte, intercambia segmento central |
| Basado en piezas | `cruce_basado_en_piezas()` | Selecciona patrones de ambos padres por eficiencia, evita redundancia |

**Función principal `cruzar()`:**
- Aplica cruce con probabilidad `tasa_cruce` (default 0.8)
- Si no cruza, retorna copias de los padres
- Si `reparar_hijos_cruce=True` (default), repara descendencia vía BFD

**Funciones auxiliares:**
- `reparar_descendencia()` — Delega a `reparar_cromosoma()` de population
- `validar_descendencia()` — Verifica cobertura de demanda
- `cruce_poblacion()` — Aplica cruce a lista de parejas
- `analizar_diversidad_cruce()` — Métricas de diversidad introducida

### 5.7. Mutación (`mutation.py`, 552 líneas)

**6 operadores de mutación:**

| Operador | Función | Probabilidad | Descripción |
|----------|---------|-------------|-------------|
| Cambiar origen | `mutacion_cambiar_origen_patron()` | Por gen (10%) | Cambia barra origen por otra compatible |
| Reoptimizar | `mutacion_reoptimizar_patron()` | Por gen (10%) | Re-genera el patrón con BFD |
| Mover pieza | `mutacion_mover_pieza()` | Por gen (10%) | Mueve una pieza entre patrones si cabe |
| Ajustar cantidad | `mutacion_ajustar_cantidad_piezas()` | 10% cromosoma | Corrige faltantes/sobrantes (prioriza faltantes 70%) |
| Dividir patrón | `mutacion_dividir_patron()` | 5% cromosoma | Divide un patrón en dos |
| Combinar patrones | `mutacion_combinar_patrones()` | 5% cromosoma | Fusiona dos patrones en uno |

**Función principal `mutar()`:**
1. Decide si mutar el individuo (prob. `tasa_mutacion_individuo`, default 0.2)
2. Para cada patrón: decide si mutar el gen (prob. `tasa_mutacion_gen`, default 0.1)
3. Selecciona operador aleatorio de la lista habilitada
4. Aplica mutaciones a nivel de cromosoma (ajustar, dividir, combinar)

**Operaciones habilitadas por defecto:** `['cambiar_origen', 'reoptimizar', 'mover_pieza']`

### 5.8. Motor del AG (`engine.py`, 586 líneas)

**Función principal `ejecutar_algoritmo_genetico()`:**

```
Entrada: piezas_requeridas_df, barras_disponibles, desperdicios, config_ga, progress_callback
Salida:  (mejor_cromosoma, resumen_estadísticas)
```

**Pipeline:**
1. Merge config proporcionada con defaults
2. Inicializar `RegistroEvolucion`
3. **Inicialización de población** (con callbacks cada 20%):
   - Generar óptimos + FFD/BFD + aleatorios según estrategia
   - Shuffle final
4. **Evaluación inicial** (con callbacks cada 20%):
   - `calcular_fitness()` para cada individuo
5. **Bucle evolutivo principal** (`while generacion <= max_generaciones`):
   - Verificar criterios de parada
   - Selección de padres (reserva espacio para élite)
   - Formar parejas y cruzar
   - Mutar hijos
   - Evaluar nueva generación
   - Aplicar elitismo y reemplazo
   - Registrar estadísticas
   - Callback de progreso
6. Finalizar registro, retornar mejor cromosoma + resumen

**4 criterios de parada (`verificar_criterios_parada()`):**
1. Máximo de generaciones alcanzado
2. Tiempo límite excedido (default 300s)
3. Fitness objetivo alcanzado (si configurado)
4. Convergencia: N generaciones sin mejora significativa (default 20, umbral 0.001)

**Elitismo (`aplicar_elitismo_y_reemplazo()`):**
- Selecciona los `tamaño_elite` mejores de la población actual
- Completa con los mejores hijos hasta `tamaño_poblacion`
- Si no hay elitismo: reemplazo generacional completo

**Versión simplificada:** `ejecutar_algoritmo_genetico_simple()` con parámetros básicos.

**Validación:** `validar_configuracion_ga()` verifica rangos y consistencia.

### 5.9. Métricas (`metrics.py`, 373 líneas)

**Clase `RegistroEvolucion`:**

Registra por generación: mejor/promedio/peor fitness, diversidad, tiempo.
Mantiene mejor cromosoma global y generación en que se encontró.

**Métodos:**
- `iniciar_registro()`, `registrar_generacion()`, `finalizar_registro()`
- `obtener_resumen()` → Dict con todas las métricas finales
- `_detectar_convergencia_final()` — diversidad < 0.01 en últimas 10 generaciones

**Funciones de diversidad:**
- `calcular_diversidad_poblacion()` — Desviación estándar normalizada del fitness
- `calcular_diversidad_estructural()` — Diferencias entre cromosomas (patrones, desperdicio, barras)
- `detectar_convergencia()` — Mejora < umbral en ventana de generaciones

**Funciones de reporte:**
- `generar_reporte_evolucion()` — Reporte textual formateado
- `exportar_metricas_csv()` — Exportación a CSV

### 5.10. Adaptador de Entrada (`input_adapter.py`, 364 líneas)

**Conversiones:**
- `longitudes_a_barras_dict(longitudes)` → `[{'longitud': float, 'tipo': 'estandar'}]`
- `longitudes_a_desperdicios_dict(longitudes)` → `[{'longitud': float, 'tipo': 'desperdicio'}]`
- `adaptar_entrada_para_ag(piezas_df, barras, desperdicios)` — Adaptación completa

**Validación:** `validar_entrada_ag()` — Verifica DataFrame, columnas, tipos, valores positivos

**Limpieza:** `limpiar_datos_entrada()` — Redondea, elimina inválidos, deduplica, ordena

**Utilidades:**
- `consolidar_piezas_identicas()` — Agrupa por id_pedido + longitud
- `expandir_piezas_multiples()` — Expande cantidad > 1 en filas individuales
- `generar_resumen_entrada()` — Estadísticas de piezas, barras, desperdicios

### 5.11. Formateador de Salida (`output_formatter.py`, 301 líneas)

**Función principal `formatear_salida_desde_cromosoma()`:**

```python
# Entrada: Cromosoma
# Salida: (patrones_de_corte, desperdicios_utilizables)
# Formato de patrón:
{
    'barra_origen_longitud': float,
    'cortes_realizados': [float, ...],
    'piezas_obtenidas': [{'id_pedido': str, 'longitud': float}, ...],
    'desperdicio_resultante': float
}
```

**Validación:** `validar_formato_salida()` — Verifica estructura, tipos, consistencia (cortes + desperdicio = barra)

**Funciones adicionales:**
- `generar_resumen_patrones()` — Estadísticas: total barras, piezas, desperdicio, eficiencia
- `formatear_salida_con_metadatos()` — Incluye metadatos de optimización
- `convertir_cromosoma_a_formato_legacy()` — Compatibilidad con versiones anteriores

### 5.12. Analizador Óptimo (`optimal_analyzer.py`, 265 líneas)

**Análisis exhaustivo para casos homogéneos** (una sola longitud de pieza):

`calcular_solucion_optima_homogenea(longitud_pieza, cantidad, longitudes_barras)`:
- Calcula cuántas piezas caben en cada tipo de barra
- Genera todas las combinaciones posibles (product)
- Evalúa desperdicio total (incluyendo exceso de piezas)
- Retorna combinación con menor desperdicio (y menor barras en empate)

`analizar_casos_homogeneos(piezas_df, longitudes_barras, tolerancia=0.01)`:
- Agrupa piezas por longitud (con tolerancia)
- Solo analiza grupos con >= 10 piezas
- Retorna solución óptima por grupo

**Funciones adicionales:**
- `comparar_con_solucion_genetica()` — Comparación AG vs óptimo
- `generar_reporte_optimizacion()` — Reporte markdown

### 5.13. Utilidades de Cromosoma (`chromosome_utils.py`, 284 líneas)

| Función | Descripción |
|---------|-------------|
| `crear_patron_corte()` | Crea patrón validando que piezas quepan |
| `validar_patron()` | Verifica desperdicio y clasificación |
| `calcular_sumario_piezas_en_cromosoma()` | Dict `{(id_pedido, longitud): cantidad}` |
| `validar_cromosoma_completitud()` | Faltantes y sobrantes vs demanda |
| `calcular_desperdicio_total_cromosoma()` | Wrapper de `cromosoma.calcular_desperdicio_total()` |
| `obtener_nuevos_desperdicios_utilizables_de_cromosoma()` | Lista de desperdicios >= 0.5m |
| `fusionar_cromosomas()` | Combina patrones de 2 cromosomas |
| `crear_cromosoma_desde_dict()` | Deserialización desde JSON/dict |
| `convertir_cromosoma_a_dict()` | Serialización a JSON/dict |

---

## 6. Generación de Artefactos (`utils/artifact_generator.py`, 321 líneas)

**Función principal `generar_artefactos_completos()`:**

```python
# Entrada: resultados_df, storage_uuid, filestore_base, document_number
# Salida: (excel_path, pdf_path, image_path)
```

**Columnas requeridas del DataFrame:**
```
numero_barra, barra_origen_longitud, cortes_realizados,
cantidad_requerida, masa_unitaria_kg, desperdicio_m
```

**3 artefactos generados:**

| Artefacto | Función | Tecnología | Archivo |
|-----------|---------|------------|---------|
| Excel | `resultados_df.to_excel()` | openpyxl | `resultados_optimizacion.xlsx` |
| PDF | `generar_pdf_con_link_correcto()` | WeasyPrint (HTML→PDF) | `plan_de_corte.pdf` |
| PNG | `generar_imagen_grafica()` | matplotlib | `grafica_cortes.png` |

**PDF:** Plantilla HTML inline con estilos CSS. Contiene:
- Título "Plan de Corte Optimizado" + documento
- Resumen ejecutivo: total barras, masa, desperdicio, eficiencia
- Tabla de cortes: barra, longitud, cortes, cantidad, desperdicio
- Footer con descripción del algoritmo

**PNG:** Gráfica horizontal de barras con:
- Cada barra como fila con segmentos de color (cortes) + gris (desperdicio)
- Paleta de 8 colores cíclica
- Límite: no genera si alguna orden supera 100 piezas
- 200 DPI, figsize adaptativo

**Nota:** `matplotlib.use('Agg')` está configurado correctamente aquí.

---

## 7. Datos del Dominio

### barras_estandar.json

11 diámetros (nomenclatura colombiana ASTM A615) × 3 longitudes comerciales:

| Diámetro | Longitudes (m) |
|----------|-----------------|
| #3 a #11, #14, #18 | 6.0, 9.0, 12.0 |

**Nota:** Solo se usan las longitudes (6, 9, 12) en el AG actual. El diámetro se ignora en el procesamiento.

### Formato de entrada Excel

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `N° Orden` | str | Identificador del pedido |
| `Elemento` | str | Descripción del elemento estructural |
| `N° de Barra` | str | Número de barra |
| `Longitud total (m)` | float | Longitud de la pieza (0.1-100m) |
| `Cantidad` | int | Cantidad requerida (>0) |
| `Masa total (kg)` | float | Masa total (0.01-50000kg) |

---

## 8. API REST Completa

### Endpoints

| Método | Ruta | Request | Response | Status |
|--------|------|---------|----------|--------|
| GET | `/health` | — | `{status, database}` | 200/500 |
| POST | `/upload` | Form: file, perfil | `{file_id, task_id, status, message}` | 202/400/500 |
| GET | `/files` | Query: search, status, perfil, date_from, date_to, page, per_page | `{files[], total, page, per_page, pages}` | 200 |
| GET | `/file/<id>` | — | `{id, filename, status, ..., processing_results[]}` | 200/404 |
| DELETE | `/file/<id>` | — | `{message, file_id}` | 200/404/500 |
| POST | `/reprocess/<id>` | JSON: `{perfil}` | `{task_id, file_id, perfil, message}` | 202/400/404/500 |
| GET | `/descargar-excel/<uuid>` | — | Binary (xlsx) | 200/404 |
| GET | `/descargar-pdf/<uuid>` | — | Binary (pdf) | 200/404 |
| GET | `/descargar-imagen/<uuid>` | — | Binary (png) | 200/404 |
| GET | `/status/<task_id>` | — | `{task_id, state, progress, message}` | 200/500 |

### Perfiles válidos

`rapido`, `balanceado`, `profundo`

### Estados del procesamiento

`uploaded` → `validating` → `processing` → `generating_artifacts` → `completed`

Errores: `error_validation`, `error_processing`, `error_generation`

---

## 9. Comunicación en Tiempo Real

### Flujo de progreso

```
Celery Worker
  ↓ publish_progress()
Redis Pub/Sub (canal: task_progress:{task_id})
  ↓ redis_pubsub_listener() [thread daemon en Flask]
WebSocket (room: task_id, evento: task_update)
  ↓
Browser (Socket.IO client)
  ↓ fallback si WS falla 30s
HTTP Polling (GET /status/{task_id}, cada 2s)
```

### Formato del mensaje de progreso

```json
{
    "task_id": "process_123",
    "progress": 45,
    "state": "PROCESSING",
    "message": "Gen 15/100: Cruce (fitness: 125.3400)",
    "timestamp": "2026-04-08T10:30:00",
    "phase": "processing",
    "generation": 15,
    "total_generations": 100
}
```

---

## 10. Tests

Tests con `unittest` (no pytest). Solo cubren `genetic_algorithm/`:

```bash
python -m unittest discover tests/
python -m unittest tests.test_engine
python -m unittest tests.test_fitness
python -m unittest tests.test_operators
python -m unittest tests.test_integration
python -m unittest test_optimal_analysis  # raíz
```

**No hay tests para:** endpoints Flask, tareas Celery, artifact_generator, modelos SQLAlchemy.

---

## 11. Inconsistencias Conocidas

1. **Nombre del perfil:** `main.py` usa `intensivo`, `celery_worker.py` usa `profundo`
2. **`LONGITUD_MINIMA_DESPERDICIO_UTILIZABLE`:** `0.0` en `main.py` vs `0.5` en `genetic_algorithm/__init__.py`
3. **`Pipfile`** desincronizado con `requirements.txt` (falta psycopg2, SQLAlchemy, Celery, Redis, etc.)
4. **`matplotlib.use('Agg')`:** presente en `main.py` y `artifact_generator.py`, ausente en `celery_worker.py`
5. **`init.sql` ON CONFLICT:** usa `document_number` UNIQUE que ya no existe tras migración
6. **Sin CI, sin linting, sin type checking** configurado
