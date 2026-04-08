# Capítulo: Metodología de Desarrollo del Sistema OICA

## Introducción Metodológica

El presente capítulo describe la metodología empleada en el diseño y desarrollo del **Optimizador Inteligente de Cortes de Acero (OICA)**, una aplicación web de código abierto que aplica técnicas de Inteligencia Artificial —específicamente un Algoritmo Genético— para resolver el problema de corte unidimensional (*1D Cutting Stock Problem*) en barras de acero comercial de 6, 9 y 12 metros, según las longitudes disponibles en el mercado colombiano.

El proceso de desarrollo siguió un enfoque de **ingeniería de software basada en componentes y orientada a servicios**, donde cada módulo funcional del sistema fue analizado, diseñado e implementado de manera independiente pero interconectada. La metodología se fundamenta en cuatro principios rectores:

1. **Descomposición funcional**: Cada servicio del sistema fue descompuesto en *features* atómicos con disparadores (*triggers*) identificados, flujos de datos trazables y contratos de integración definidos.
2. **Separación de responsabilidades**: El sistema se divide en servicios independientes —servidor HTTP, procesador asíncrono, interfaz de usuario, base de datos y broker de mensajes— cada uno con un ciclo de vida, despliegue y escalamiento propios.
3. **Reproducibilidad del entorno**: La contenerización mediante Docker garantiza que el sistema sea replicable en cualquier máquina con condiciones idénticas de ejecución, eliminando la variabilidad del entorno de desarrollo.
4. **Trazabilidad del proceso**: Cada decisión técnica responde a un requerimiento funcional específico y se justifica desde la perspectiva de la optimización de recursos y la eficiencia estructural.

---

## 1. Definición de Parámetros Técnicos

### 1.1. Selección Tecnológica y Justificación

La selección de tecnologías para el sistema OICA se realizó evaluando criterios de compatibilidad, rendimiento computacional, madurez del ecosistema y pertinencia para el dominio del problema. Cada tecnología seleccionada cumple un rol análogo al de un material de construcción en una obra civil: debe cumplir especificaciones técnicas, ser compatible con los demás componentes y garantizar la integridad estructural del sistema.

#### 1.1.1. Backend: Python 3.12 con Flask

**Justificación**: Python fue seleccionado como lenguaje del backend por tres razones fundamentales:

- **Ecosistema científico-computacional**: Las bibliotecas `NumPy` y `pandas` proporcionan las estructuras de datos y operaciones vectorizadas necesarias para la manipulación eficiente de las matrices de piezas requeridas, longitudes de barras y patrones de corte. Esta capacidad es indispensable para un algoritmo genético que evalúa miles de soluciones candidatas.
- **Procesamiento de archivos de ingeniería**: La biblioteca `openpyxl` permite la lectura y escritura de archivos Excel (`.xlsx`), que constituyen el formato estándar de las planillas de despiece (*cartillas de fierro*) utilizadas en la industria de la construcción colombiana.
- **Generación de artefactos técnicos**: `WeasyPrint` (renderizado HTML→PDF) y `matplotlib` (generación de gráficas) permiten producir los entregables visuales —planes de corte en PDF e imágenes de distribución de barras— directamente desde el backend sin dependencias externas de terceros.

**Restricción crítica**: Se fijó la versión **Python 3.12** como requisito inmutable. La dependencia `psycopg2-binary 2.9.9` (driver PostgreSQL) es incompatible con Python 3.13, lo cual impide actualizar la versión base sin riesgo de ruptura en la capa de persistencia.

**Flask** fue seleccionado como framework HTTP por su naturaleza minimalista y su compatibilidad con `Flask-SocketIO`, que habilita la comunicación bidireccional en tiempo real (WebSocket) necesaria para reportar el progreso del algoritmo genético al usuario durante la ejecución.

#### 1.1.2. Procesamiento Asíncrono: Celery con Redis

**Justificación**: El algoritmo genético es una operación computacionalmente intensiva cuyo tiempo de ejecución oscila entre 30 segundos (perfil rápido) y 5 minutos (perfil profundo). Ejecutar este cálculo de manera síncrona dentro del ciclo de petición HTTP (*request-response*) bloquearía el servidor, impidiendo atender nuevas solicitudes y provocando *timeouts* en el navegador.

**Celery** resuelve este problema mediante un modelo de *task queue*: el servidor HTTP encola la tarea de procesamiento y retorna inmediatamente un identificador de tarea (`task_id`). Un proceso separado —el *worker*— consume la tarea de la cola, ejecuta el algoritmo y publica actualizaciones de progreso a través de **Redis Pub/Sub**.

**Redis** cumple un doble propósito:
- **Broker de mensajes**: Gestiona la cola de tareas entre el servidor Flask y los workers de Celery.
- **Canal de comunicación en tiempo real**: Mediante el patrón *Publish/Subscribe*, el worker publica el progreso de cada generación del algoritmo genético, y el servidor Flask retransmite estas actualizaciones al navegador del usuario vía WebSocket.

#### 1.1.3. Persistencia: PostgreSQL 15

**Justificación**: Se seleccionó PostgreSQL por su soporte nativo de columnas `JSONB`, que permite almacenar los resultados del algoritmo genético (patrones de corte, métricas de evolución y datos originales de la cartilla) en formato estructurado pero flexible, sin necesidad de normalizar cada campo individual en tablas relacionales. Esta decisión responde al hecho de que la estructura de los resultados varía según la complejidad de la cartilla de entrada.

El esquema relacional se define en `config/backend/init.sql` y consta de dos tablas principales con relación 1:N:

- **`uploaded_files`**: Registro del archivo Excel subido, con estado de procesamiento rastreable a través de 8 estados discretos (`uploaded` → `validating` → `validated` → `processing` → `generating_artifacts` → `completed`, con ramificaciones a `error_validation`, `error_processing`, `error_generation`).
- **`processing_results`**: Resultados versionados de la optimización. Cada archivo puede tener múltiples versiones de resultados (reprocesamiento con diferentes perfiles), cada una identificada por un `storage_uuid` único que aísla los artefactos generados en el sistema de archivos.

#### 1.1.4. Frontend: Next.js 15 con React 19

**Justificación**: Next.js fue seleccionado por su arquitectura *App Router*, que permite renderizado híbrido (servidor y cliente) dentro del mismo framework. React 19 proporciona el modelo de componentes declarativo necesario para construir interfaces reactivas que reflejen en tiempo real el estado del procesamiento.

Las bibliotecas complementarias fueron seleccionadas por su función específica:
- **`socket.io-client`**: Cliente WebSocket para la comunicación bidireccional con el servidor Flask, habilitando la actualización en tiempo real de las barras de progreso.
- **`react-dropzone`**: Interfaz de arrastrar-y-soltar para la carga de archivos Excel, simplificando la interacción del usuario en entornos de campo.
- **`Tailwind CSS`**: Framework de utilidades CSS que permite construir interfaces responsivas sin archivos de estilos externos, reduciendo la complejidad de mantenimiento.

#### 1.1.5. Contenerización: Docker con Docker Compose

**Justificación**: El sistema debe ser desplegable en cualquier entorno —desde la computadora de un ingeniero civil hasta un servidor de producción— sin configuración manual de dependencias. Docker resuelve este problema encapsulando cada servicio con todas sus dependencias en imágenes inmutables. Docker Compose orquesta los 5 servicios con su cadena de dependencias y verificaciones de salud (*health checks*).

### 1.2. Definición de Contratos de Integración (APIs)

Los contratos de integración entre servicios se definieron como especificaciones técnicas de diseño, análogos a los planos de detalle en una obra civil. Cada contrato establece el formato exacto de entrada, salida y los códigos de estado esperados.

#### 1.2.1. API REST (Backend → Frontend)

| Endpoint | Método | Disparador | Entrada | Salida |
|----------|--------|-----------|---------|--------|
| `POST /upload` | HTTP | Usuario sube archivo | `FormData {file, perfil}` | `{file_id, task_id, status}` |
| `GET /files` | HTTP | Usuario abre tabla de archivos | Query params: `page, per_page, search, status, perfil, date_from, date_to` | `{files[], total, pages}` |
| `DELETE /file/{id}` | HTTP | Usuario elimina archivo | — | `{message, file_id}` |
| `POST /reprocess/{id}` | HTTP | Usuario reprocesa archivo | `{perfil}` | `{task_id, file_id}` |
| `GET /descargar-excel/{uuid}` | HTTP | Usuario descarga resultado | — | Archivo `.xlsx` |
| `GET /descargar-pdf/{uuid}` | HTTP | Usuario descarga resultado | — | Archivo `.pdf` |
| `GET /descargar-imagen/{uuid}` | HTTP | Usuario descarga resultado | — | Archivo `.png` |
| `GET /status/{task_id}` | HTTP | Polling de respaldo | — | `{state, progress, message}` |

#### 1.2.2. API WebSocket (Servidor ↔ Cliente)

| Evento | Dirección | Disparador | Payload |
|--------|-----------|-----------|---------|
| `subscribe_task` | Cliente → Servidor | Archivo encolado | `{task_id}` |
| `task_update` | Servidor → Cliente | Worker publica progreso | `{task_id, state, progress, message, result?}` |
| `connected` | Servidor → Cliente | Conexión establecida | `{message}` |

#### 1.2.3. Canal Redis Pub/Sub (Worker → Servidor)

| Canal | Publicador | Suscriptor | Payload |
|-------|-----------|-----------|---------|
| `task_progress:{task_id}` | Celery Worker | Servidor Flask (thread daemon) | `{task_id, progress, state, message, timestamp}` |

### 1.3. Captura de Parámetros del Dominio de Ingeniería Civil

El sistema captura los datos críticos del dominio de la ingeniería estructural colombiana:

#### 1.3.1. Longitudes Comerciales de Barras de Acero

Las barras de acero corrugado en Colombia se comercializan en tres longitudes estándar: **6.0 m, 9.0 m y 12.0 m**. Esta restricción se codifica en el archivo `barras_estandar.json`, que define las longitudes disponibles para cada diámetro de barra:

```json
{
    "#3": [6.0, 9.0, 12.0],
    "#4": [6.0, 9.0, 12.0],
    ...
    "#18": [6.0, 9.0, 12.0]
}
```

Se cubren 11 diámetros nominales: #3, #4, #5, #6, #7, #8, #9, #10, #11, #14 y #18, que corresponden a la nomenclatura ASTM A615/A615M empleada en la normativa colombiana (NSR-10).

#### 1.3.2. Desperdicios Admisibles

El sistema define un umbral mínimo de desperdicio utilizable de **0.5 metros** (constante `LONGITUD_MINIMA_DESPERDICIO_UTILIZABLE`). Los retazos inferiores a esta longitud se consideran pérdida irrecuperable, mientras que los retazos superiores se clasifican como **desperdicios reutilizables** que pueden alimentar ejecuciones futuras del optimizador. Este umbral responde a la práctica constructiva donde retazos menores a 50 centímetros no tienen aplicación estructural factible.

#### 1.3.3. Formato de Entrada: Cartilla de Despiece

El archivo Excel de entrada debe contener las siguientes columnas obligatorias, que corresponden a los campos estándar de una cartilla de despiece de fierro:

| Columna | Tipo | Descripción | Validación |
|---------|------|-------------|-----------|
| `N° Orden` | Texto | Identificador del pedido o elemento estructural | Obligatorio |
| `Elemento` | Texto | Nombre del elemento (viga, columna, zapata) | Obligatorio |
| `N° de Barra` | Texto | Identificador del tipo de barra | Obligatorio |
| `Longitud total (m)` | Numérico | Longitud requerida de la pieza en metros | 0.1 – 100 m |
| `Cantidad` | Entero | Número de piezas requeridas | > 0 |
| `Masa total (kg)` | Numérico | Masa total de las piezas | 0.01 – 50,000 kg |

---

## 2. Arquitectura del Sistema

### 2.1. Infraestructura Lógica: Monolito Modular Distribuido

La arquitectura del sistema OICA se clasifica como un **monolito modular distribuido en contenedores**. A diferencia de una arquitectura de microservicios pura —donde cada servicio posee su propia base de código, base de datos y protocolo de comunicación— el sistema OICA comparte una base de código única entre el servidor HTTP y el procesador asíncrono, pero los ejecuta como procesos independientes y aislados dentro de contenedores Docker separados.

Esta decisión responde a un balance pragmático entre complejidad operativa y beneficios de escalamiento:

- **Backend y Celery Worker** comparten el mismo código fuente (montado como volumen en ambos contenedores), pero ejecutan entrypoints diferentes: `python server.py` (servidor HTTP con `gevent` para WebSocket) versus `celery -A celery_worker worker` (procesador de tareas con `eventlet`).
- **Frontend** es una aplicación independiente con su propio repositorio, framework y ciclo de despliegue.
- Los servicios de infraestructura (**PostgreSQL** y **Redis**) se despliegan como contenedores con volúmenes persistentes.

### 2.2. Topología de Servicios

El sistema se compone de **5 servicios** orquestados por Docker Compose, con la siguiente cadena de dependencias y verificaciones de salud:

```
┌─────────────────────────────────────────────────────────────────┐
│                    docker-compose.yaml                          │
│                    Proyecto: oica-app                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐         ┌──────────────────┐              │
│  │  db               │         │  redis             │            │
│  │  PostgreSQL 15    │         │  Redis 7           │            │
│  │  Puerto: 5432     │         │  Puerto: 6379      │            │
│  │  Healthcheck:     │         │  Healthcheck:      │            │
│  │  pg_isready       │         │  redis-cli ping    │            │
│  └───────┬──────────┘         └───────┬──────────┘              │
│          │ depends_on: healthy         │ depends_on: healthy     │
│   ┌──────┴─────────────────────────────┴──────┐                 │
│   │              backend                       │                │
│   │  Flask + Socket.IO (gevent)                │                │
│   │  Puerto: 5000                              │                │
│   │  Entrypoint: python server.py              │                │
│   │  - API REST + WebSocket                    │                │
│   │  - Encola tareas en Celery                 │                │
│   │  - Thread daemon: Redis Pub/Sub listener   │                │
│   └──────┬─────────────────────────────────────┘                │
│          │ depends_on: backend                                  │
│   ┌──────┴─────────────────────────────────────┐                │
│   │              frontend                       │                │
│   │  Next.js 15 + React 19                     │                │
│   │  Puerto: 80 → 3000                         │                │
│   │  Comando: npm install && npm run build     │                │
│   │           && npm start                     │                │
│   └────────────────────────────────────────────┘                │
│                                                                 │
│   ┌────────────────────────────────────────────┐                │
│   │           celery_worker                     │                │
│   │  Python 3.12 (eventlet)                    │                │
│   │  Sin puerto expuesto                       │                │
│   │  Entrypoint: celery -A celery_worker       │                │
│   │              worker --loglevel=info         │                │
│   │  - Ejecuta algoritmo genético              │                │
│   │  - Genera artefactos (PDF, Excel, PNG)     │                │
│   │  - Publica progreso vía Redis Pub/Sub      │                │
│   └────────────────────────────────────────────┘                │
└─────────────────────────────────────────────────────────────────┘
```

### 2.3. Flujo de Datos (*Data Pipeline*)

El flujo de datos del sistema sigue un pipeline secuencial con comunicación asíncrona:

```
[1] CARGA                [2] ENCOLAMIENTO         [3] PROCESAMIENTO
Usuario sube .xlsx  ──►  Flask guarda en BD   ──►  Celery Worker:
via POST /upload         y filestore temporal      - Lee Excel
                         Encola tarea Celery       - Valida estructura
                         Retorna task_id           - Ejecuta AG
                                                   - Genera artefactos

[4] PROGRESO TIEMPO REAL                    [5] ENTREGA
Worker publica a Redis Pub/Sub  ──►         Artefactos guardados en
Flask listener retransmite      ──►         filestore/{uuid}/
via WebSocket al navegador                  Resultado en BD (JSONB)
                                            Usuario descarga via GET
```

Cada paso del pipeline tiene un estado correspondiente en la base de datos (`uploaded` → `validating` → `validated` → `processing` → `generating_artifacts` → `completed`), lo que permite rastrear la posición exacta de cada archivo en el pipeline en cualquier momento.

### 2.4. Contenerización como Entorno de Ejecución Controlado

La contenerización con Docker cumple un rol análogo al de un **campamento de obra prefabricado**: un entorno estandarizado, portátil y listo para operar, independiente de las condiciones del terreno (sistema operativo anfitrión).

Cada servicio se construye sobre una imagen base Alpine Linux, seleccionada por su tamaño reducido (~5 MB). Los Dockerfiles del backend y del worker instalan 25 paquetes del sistema operativo necesarios para las dependencias nativas de Python (compiladores C, bibliotecas gráficas para WeasyPrint y matplotlib, driver PostgreSQL).

**Volúmenes compartidos**: El código fuente del backend se monta como volumen en ambos contenedores (`backend` y `celery_worker`), y el directorio de almacenamiento de artefactos (`app/data/filestore/`) se comparte entre ambos para que los archivos generados por el worker sean accesibles al servidor HTTP para su descarga.

**Persistencia de datos**: PostgreSQL y Redis utilizan volúmenes nombrados (`postgres_data`, `redis_data`) que sobreviven a la destrucción y recreación de contenedores, garantizando la persistencia de los datos entre reinicios.

---

## 3. Metodología del Backend

### 3.1. Análisis Funcional del Servidor HTTP

El servidor HTTP (`server.py`) fue diseñado siguiendo un análisis de **disparadores funcionales**, donde cada endpoint responde a una acción específica del usuario con un flujo de procesamiento definido.

#### 3.1.1. Feature: Carga de Archivo y Encolamiento

**Disparador**: El usuario envía un archivo Excel vía `POST /upload` con un perfil de optimización seleccionado.

**Flujo de ejecución**:
1. Validación de la extensión del archivo (solo `.xlsx` y `.csv` permitidos).
2. Validación del perfil de optimización (`rapido`, `balanceado` o `profundo`).
3. Almacenamiento temporal del archivo en `filestore/temp/` con nombre prefijado por *timestamp* para evitar colisiones.
4. Creación del registro `UploadedFile` en PostgreSQL con estado `uploaded`.
5. Encolamiento de la tarea `process_file_task` en Celery con `task_id = "process_{file_id}"`.
6. Respuesta inmediata con código HTTP 202 (*Accepted*), devolviendo `file_id` y `task_id`.

**Justificación del diseño asíncrono**: El patrón *fire-and-forget* desacopla el tiempo de respuesta HTTP del tiempo de procesamiento del algoritmo genético, que puede oscilar entre 30 segundos y 5 minutos según el perfil y la complejidad de la cartilla.

#### 3.1.2. Feature: Comunicación en Tiempo Real

**Disparador**: El cliente emite un evento WebSocket `subscribe_task` con el `task_id` recibido del endpoint de carga.

**Mecanismo de retransmisión**: El servidor Flask ejecuta un thread daemon que se suscribe al patrón Redis Pub/Sub `task_progress:*`. Cuando el Celery Worker publica una actualización de progreso en el canal `task_progress:{task_id}`, el thread la captura, la deserializa y la emite como evento WebSocket `task_update` al *room* correspondiente.

Este mecanismo de puente Redis→WebSocket fue necesario porque Celery y Flask ejecutan en procesos separados sin memoria compartida. Redis actúa como bus de mensajes interprocess.

**Fallback de resiliencia**: Si la conexión WebSocket se interrumpe, el cliente activa un mecanismo de *polling* HTTP que consulta `GET /status/{task_id}` cada 2 segundos. Este endpoint lee el estado directamente del backend de Celery (también almacenado en Redis), garantizando que el usuario nunca pierda visibilidad del progreso.

#### 3.1.3. Feature: Listado con Filtros y Paginación

**Disparador**: El usuario accede a la página de archivos o modifica un filtro.

**Capacidades**: Búsqueda por nombre de archivo, filtrado por estado de procesamiento, filtrado por perfil de optimización, filtrado por rango de fechas, y paginación con 20 resultados por página. Los archivos en procesamiento se enriquecen con datos de progreso en tiempo real obtenidos de Redis.

#### 3.1.4. Feature: Descarga de Artefactos

**Disparador**: El usuario hace clic en uno de los tres botones de descarga (Excel, PDF o Imagen).

**Flujo**: El servidor consulta el `ProcessingResult` por su `storage_uuid`, verifica la existencia física del archivo en el sistema de archivos, y lo sirve con los encabezados MIME apropiados mediante `send_file()`.

### 3.2. Modelado de la Lógica de Negocio: Algoritmo Genético

El núcleo computacional del sistema es un **Algoritmo Genético (AG)** diseñado para resolver el **Problema de Corte Unidimensional** (*1D Cutting Stock Problem*), un problema de optimización combinatoria clasificado como NP-difícil. A continuación se describe la metodología de modelado de cada componente del AG.

#### 3.2.1. Representación Cromosómica (Codificación de la Solución)

La codificación de las soluciones constituye la decisión de diseño más crítica del algoritmo genético, ya que determina la expresividad del espacio de búsqueda.

**Estructura de dos niveles**:

- **Cromosoma** (`Cromosoma`): Representa una solución completa al problema de corte. Contiene una lista ordenada de *patrones de corte*.
- **Patrón** (`Patron`): Representa una barra individual siendo cortada. Almacena:
  - `origen_barra_longitud`: Longitud de la barra madre (6.0, 9.0 o 12.0 m).
  - `origen_barra_tipo`: Clasificación de la barra (`'estandar'` para barras nuevas, `'desperdicio'` para retazos reutilizados).
  - `piezas_cortadas`: Lista de piezas que se obtienen de esta barra, cada una con `id_pedido`, `longitud_pieza` y `cantidad_pieza_en_patron`.
  - `desperdicio_patron_longitud`: Calculado automáticamente como la diferencia entre la longitud de la barra origen y la suma de las piezas cortadas.

**Ejemplo de un cromosoma con 3 patrones**:
```
Cromosoma = [
    Patrón 1: Barra 12m → [pieza 3.5m ×2, pieza 2.0m ×1] → desperdicio 3.0m (reutilizable)
    Patrón 2: Barra 9m  → [pieza 4.2m ×1, pieza 4.2m ×1] → desperdicio 0.6m (reutilizable)
    Patrón 3: Barra 6m  → [pieza 2.8m ×2]                 → desperdicio 0.4m (pérdida)
]
```

#### 3.2.2. Función de Fitness (Evaluación de Soluciones)

La función de fitness cuantifica la calidad de cada solución candidata. Se diseñó como una **función de minimización multiobjetivo ponderada** con la siguiente formulación:

```
F(cromosoma) = W_d · D_total
             + W_f · P_faltantes
             + W_s · P_sobrantes
             + W_b · N_barras_estandar
             − W_r · L_desperdicios_reutilizados
```

Donde:

| Componente | Símbolo | Peso por defecto | Descripción |
|-----------|---------|-----------------|-------------|
| Desperdicio total | D_total | 10.0 | Suma de longitudes de desperdicio en todos los patrones |
| Penalización por faltantes | P_faltantes | 10,000.0 | Penaliza fuertemente las piezas que no se produjeron respecto a la demanda. Proporcional a `cantidad_faltante × longitud_pieza` |
| Penalización por sobrantes | P_sobrantes | 5,000.0 | Penaliza la sobreproducción de piezas |
| Penalización por barras usadas | N_barras_estandar | 50.0 | Penaliza cada barra estándar consumida, incentivando la consolidación |
| Bonificación por reutilización | L_desperdicios_reutilizados | 30.0 | Bonifica el uso de retazos previos en lugar de barras nuevas |

**Justificación de los pesos**: La penalización por piezas faltantes (10,000) es dos órdenes de magnitud superior a la penalización por desperdicio (10), garantizando que el algoritmo priorice absolutamente el cumplimiento de la demanda sobre la minimización de desperdicios. Esto refleja la realidad operativa: un faltante en obra detiene la construcción, mientras que el desperdicio es un costo de eficiencia.

#### 3.2.3. Inicialización de la Población

La calidad de la población inicial tiene un impacto directo en la convergencia del algoritmo. El sistema implementa una **estrategia de inicialización híbrida** que combina tres métodos:

| Método | Proporción | Descripción |
|--------|-----------|-------------|
| **Análisis Óptimo** | ~6% (máx. 3 individuos) | Utiliza `optimal_analyzer` para identificar casos homogéneos (piezas de longitud idéntica) y generar soluciones óptimas deterministas. |
| **Heurísticas (FFD/BFD)** | ~60% | Alternancia entre *First Fit Decreasing* y *Best Fit Decreasing*: ordena las piezas por longitud descendente y las asigna a la primera barra donde quepan (FFD) o a la barra con menos espacio residual (BFD). |
| **Aleatorio con Reparación** | ~34% | Genera asignaciones aleatorias de piezas a barras, y luego repara las soluciones inválidas mediante BFD para garantizar factibilidad. |

Esta estrategia garantiza que la población inicial tenga tanto soluciones de alta calidad (heurísticas) como diversidad genética (aleatorias), evitando la convergencia prematura a óptimos locales.

#### 3.2.4. Operadores Genéticos

**Selección de padres**: Se implementan tres métodos de selección:
- **Torneo** (por defecto, tamaño 3): Selecciona aleatoriamente `k` individuos y el de mejor fitness pasa a la siguiente fase. Proporciona presión selectiva moderada.
- **Ruleta**: Probabilidad de selección inversamente proporcional al fitness. Mantiene mayor diversidad.
- **Elitista**: Selecciona directamente los mejores individuos. Máxima presión selectiva.

**Cruce** (tasa por defecto: 0.80): Se implementan tres estrategias:
- **Un punto**: Se selecciona un punto de corte aleatorio en cada padre y se intercambian los segmentos de patrones. Es el operador por defecto.
- **Dos puntos**: Similar, pero con dos puntos de corte, intercambiando el segmento central.
- **Basado en piezas**: Operador de cruce más sofisticado que analiza la eficiencia de cada patrón (ratio de material utilizado vs. desperdicio) y selecciona preferentemente los patrones más eficientes de ambos padres para construir los hijos.

Los hijos resultantes del cruce son **reparados automáticamente** mediante el algoritmo BFD para garantizar que cumplan con la demanda completa.

**Mutación** (tasa por individuo: 0.20, tasa por gen: 0.10): Se implementan cinco operaciones de mutación, cada una con probabilidad independiente:
- **Cambiar origen**: Modifica la barra madre de un patrón (ej. cambiar de 12m a 9m si las piezas caben).
- **Reoptimizar patrón**: Extrae las piezas de un patrón y las redistribuye mediante BFD.
- **Mover pieza**: Transfiere una pieza de un patrón con exceso de capacidad a otro con espacio disponible.
- **Dividir patrón** (5% de probabilidad): Divide un patrón complejo en dos patrones más simples.
- **Combinar patrones** (5% de probabilidad): Fusiona dos patrones pequeños en uno, reduciendo el número de barras consumidas.

#### 3.2.5. Elitismo y Reemplazo Generacional

El sistema emplea **elitismo** (activo por defecto con tamaño de élite = 2): los mejores individuos de la generación actual se preservan intactos en la siguiente generación, garantizando que la mejor solución encontrada nunca se pierda.

El reemplazo generacional combina la élite con los mejores hijos producidos, ordenados por fitness, hasta completar el tamaño de población configurado.

#### 3.2.6. Criterios de Parada

El algoritmo se detiene cuando se cumple cualquiera de las siguientes condiciones:
- **Generaciones máximas alcanzadas** (configurado por perfil).
- **Tiempo límite excedido** (30s–300s según perfil).
- **Convergencia detectada**: 20 generaciones consecutivas sin mejora significativa del fitness (umbral de 0.001).
- **Fitness objetivo alcanzado** (opcional, no configurado por defecto).

#### 3.2.7. Perfiles de Optimización

El sistema ofrece tres perfiles que parametrizan el algoritmo genético para diferentes relaciones costo-beneficio entre tiempo de cómputo y calidad de la solución:

| Parámetro | Rápido | Balanceado | Profundo |
|-----------|--------|-----------|----------|
| Tamaño de población | 20 | 50 | 100 |
| Generaciones máximas | 30 | 100 | 200 |
| Tiempo límite | — | — | 300s |
| Uso recomendado | Estimaciones preliminares | Planificación estándar | Optimización máxima de recursos |

### 3.3. Procesamiento Asíncrono: Tarea Celery

La tarea `process_file_task` en el Celery Worker orquesta el pipeline completo de procesamiento con reporte de progreso granular:

**Fases del pipeline y distribución de progreso**:

| Fase | Rango de progreso | Operaciones |
|------|-------------------|-------------|
| Validación | 0% – 20% | Lectura del Excel, validación de columnas obligatorias, validación de tipos y rangos de valores |
| Preparación | 20% – 30% | Carga de barras estándar desde JSON, transformación del DataFrame al formato del AG, configuración del perfil |
| Inicialización del AG | 20% – 25% | Generación de la población inicial (óptima + heurística + aleatoria) |
| Evaluación inicial | 25% – 30% | Cálculo de fitness para toda la población inicial |
| Bucle evolutivo | 30% – 70% | Ciclo de selección → cruce → mutación → evaluación → elitismo. Progreso proporcional a `generación_actual / generaciones_máximas` |
| Generación de artefactos | 70% – 90% | Generación de Excel (75%), gráfica PNG y PDF (80%) |
| Persistencia | 90% – 100% | Guardado del resultado en PostgreSQL, actualización del estado |

Cada sub-operación dentro de una generación (selección, cruce, mutación, evaluación) genera un callback de progreso con granularidad de 25% de la generación, lo que produce actualizaciones fluidas en la interfaz del usuario.

### 3.4. Generación de Artefactos

El módulo `utils/artifact_generator.py` genera tres tipos de artefactos a partir del mejor cromosoma encontrado:

1. **Excel** (`.xlsx`): Plan de corte tabular con columnas de número de barra, longitud de origen, lista de cortes realizados, cantidad, masa estimada y desperdicio resultante. Incluye un resumen ejecutivo en las filas finales.

2. **PDF** (`.pdf`): Documento formal generado mediante renderizado HTML→PDF con WeasyPrint. Contiene una tabla estilizada con los mismos datos del Excel, un resumen ejecutivo con métricas de eficiencia (número total de barras, metros totales de desperdicio, porcentaje de aprovechamiento) y metadatos de la ejecución (número de documento, fecha de generación).

3. **Imagen PNG** (`.png`): Gráfica de barras horizontales generada con matplotlib que visualiza cada patrón de corte. Cada barra se representa con segmentos coloreados (piezas cortadas) y un segmento rayado gris (desperdicio). Esta visualización permite al ingeniero civil verificar visualmente la distribución de cortes antes de ejecutarla en campo.

Todos los artefactos se almacenan en `filestore/{storage_uuid}/`, donde cada UUID identifica unívocamente una versión de procesamiento.

### 3.5. Validaciones y Manejo de Errores

El sistema implementa una estrategia de validación en capas:

1. **Capa HTTP**: Validación de extensión del archivo, tamaño máximo (16 MB) y perfil de optimización.
2. **Capa de contenido**: Verificación de columnas obligatorias del Excel, validación de tipos de datos (numérico), verificación de valores positivos y rangos admisibles (longitud: 0.1–100 m, masa: 0.01–50,000 kg).
3. **Capa de dominio**: Validación interna del AG (verificación de configuración, validación de formato de salida con consistencia aritmética: suma de cortes + desperdicio = longitud de barra).

Los errores se propagan mediante estados explícitos en la base de datos (`error_validation`, `error_processing`, `error_generation`), cada uno con un campo `status_details` que contiene el mensaje descriptivo del error para presentación al usuario.

---

## 4. Metodología del Frontend

### 4.1. Principios de Diseño de la Interfaz

La interfaz fue diseñada siguiendo el principio de **funcionalidad en entorno de campo**: la aplicación debe ser operable por un ingeniero civil o residente de obra desde cualquier dispositivo con navegador, sin requerir conocimientos técnicos especializados en software. Este principio guió las siguientes decisiones de diseño:

- **Flujo lineal**: El usuario sigue un camino claro: subir archivo → esperar procesamiento → descargar resultados.
- **Retroalimentación continua**: El progreso del procesamiento se muestra en tiempo real mediante una barra de progreso animada con estados descriptivos en español.
- **Acceso directo a artefactos**: Los botones de descarga (Excel, PDF, Imagen) son visibles y accesibles directamente desde la tabla de archivos, sin navegación adicional.

### 4.2. Estructura de Rutas y Componentes

La aplicación utiliza el **App Router** de Next.js 15, donde cada ruta corresponde a una funcionalidad discreta:

| Ruta | Componente principal | Tipo de renderizado | Función |
|------|---------------------|---------------------|---------|
| `/` | `Inicio` | Cliente | Página de bienvenida con acceso rápido al optimizador |
| `/subir-cartilla` | `FileUpload` | Cliente | Carga de archivos Excel con selección de perfil y seguimiento en tiempo real |
| `/archivos` | `FilesTable` | Cliente | Tabla paginada con filtros, progreso en vivo y descarga de artefactos |
| `/tutorial` | `TutorialGuide` | Cliente | Guía paso a paso, glosario de términos de ingeniería y preguntas frecuentes |
| `/contact-us` | `ContactUs` | Cliente | Información de contacto y formulario vía Formspree |
| `/resultados` | `ResultadosContent` | Cliente | (Legado) Descarga de PDF desde datos en `localStorage` |

### 4.3. Feature: Carga de Archivo (`FileUpload`)

**Disparador**: El usuario arrastra o selecciona un archivo Excel en la zona de *dropzone*.

**Descomposición del flujo**:

1. **Selección de archivo**: El componente `react-dropzone` restringe la aceptación a archivos `.xlsx` y `.csv` con un límite de un archivo simultáneo. Al seleccionar, el nombre del archivo se muestra en una caja informativa azul.

2. **Selección de perfil**: Un control `<select>` ofrece tres opciones de optimización con descripciones contextuales:
   - *Rápido (procesamiento rápido)*
   - *Balanceado (recomendado)* — seleccionado por defecto
   - *Profundo (más ahorro de material)*

3. **Envío**: Al presionar "Enviar", se construye un objeto `FormData` con el archivo y el perfil, se envía vía `POST /upload`, y se obtiene el `task_id`.

4. **Suscripción a progreso**: El componente invoca `subscribeToTask(taskId, handleTaskUpdate)` del módulo `socket.ts`, que registra un callback para recibir actualizaciones WebSocket.

5. **Visualización de progreso**: Una barra de progreso con porcentaje numérico y etiqueta de estado descriptiva (ej. "Procesando con algoritmo genético", "Generando archivos de resultados"). Cada actualización produce un pulso visual (cambio de opacidad de 300ms) para confirmar al usuario que el sistema está activo.

6. **Indicador de conectividad**: Si la conexión WebSocket se interrumpe, se muestra un ícono de desconexión (`WifiOff`) con el mensaje "WebSocket desconectado - usando polling de respaldo".

7. **Redirección**: Al completar (progreso 100%), se muestra un ícono de verificación verde durante 2 segundos y se redirige automáticamente a `/archivos`.

**Resiliencia del flujo**: El componente implementa un mecanismo de *fallback* dual. Si no se recibe ninguna actualización WebSocket en 30 segundos, se activa automáticamente un intervalo de *polling* HTTP (`GET /status/{taskId}`) cada 2 segundos. Si el WebSocket se restablece, el polling se detiene automáticamente.

### 4.4. Feature: Tabla de Archivos (`FilesTable`)

**Disparador**: El usuario navega a `/archivos` o modifica cualquier filtro.

**Capacidades implementadas**:

- **4 tipos de filtros**: Búsqueda por texto libre (nombre de archivo), estado de procesamiento (6 opciones), perfil de optimización (3 opciones), y rango de fechas. Todos los filtros reinician la paginación a la página 1 al modificarse.
- **Paginación**: 20 registros por página con navegación "Anterior/Siguiente" y contador de resultados.
- **Progreso en tiempo real**: Los archivos en estado de procesamiento (`processing`, `validating`, `generating_artifacts`) muestran una barra de progreso animada que se actualiza vía WebSocket. El componente se suscribe automáticamente a las tareas activas y se des-suscribe al desmontarse.
- **3 botones de descarga**: Excel, PDF e Imagen, disponibles únicamente cuando el resultado tiene estado `completed`. Cada descarga abre una nueva pestaña del navegador apuntando a `GET /descargar-{tipo}/{uuid}`.
- **Reprocesamiento**: Permite re-ejecutar el algoritmo con un perfil diferente, creando una nueva versión de resultados sin eliminar las anteriores.
- **Eliminación**: Elimina el archivo, todas sus versiones de resultados y los artefactos asociados del sistema de archivos. Requiere confirmación del usuario.

### 4.5. Integración WebSocket: Módulo `socket.ts`

El módulo `socket.ts` implementa un **singleton de Socket.IO** con las siguientes características:

- **Inicialización diferida (*lazy initialization*)**: La conexión WebSocket solo se establece cuando el primer componente la necesita (al invocar `subscribeToTask`), evitando conexiones innecesarias en páginas que no requieren tiempo real.
- **Registro de callbacks por tarea**: Un `Map<string, Function>` almacena el callback de progreso para cada `task_id`, permitiendo que múltiples componentes consuman actualizaciones simultáneas de diferentes tareas.
- **Re-suscripción automática**: Al reconectarse tras una desconexión, el módulo re-emite `subscribe_task` para todas las tareas activas en el registro, garantizando continuidad del progreso.
- **Configuración de transporte**: Se prioriza WebSocket puro con fallback a *long-polling*, con un máximo de 5 intentos de reconexión con intervalo de 1 segundo.

### 4.6. Gestión de Estado

El frontend **no utiliza una biblioteca de gestión de estado global** (no Redux, no Zustand, no Context API). Todo el estado se gestiona localmente mediante hooks de React (`useState`, `useEffect`, `useRef`).

La comunicación entre componentes se resuelve mediante:
- **Módulo singleton** (`socket.ts`): Compartido a nivel de proceso entre `FileUpload` y `FilesTable`.
- **Navegación con Router**: `FileUpload` redirige a `/archivos` al completar, donde `FilesTable` carga los datos frescos desde la API.
- **Variable de entorno**: `NEXT_PUBLIC_API_URL` (con fallback a `http://localhost:5000`) inyectada en tiempo de compilación por Next.js.

### 4.7. Convenciones de Código y Estilo

- **Indentación de 3 espacios**: Configurada en `.prettierrc` y `.vscode/settings.json`. Esta convención no estándar se mantiene por consistencia con el código existente.
- **Alias de importación**: `@/*` mapea a `src/*` mediante la configuración de `tsconfig.json` con `baseUrl: "src"`.
- **Componentes UI**: Patrón *shadcn/ui* con variantes definidas por `class-variance-authority` (CVA). El componente `Button` soporta 6 variantes visuales y 4 tamaños.
- **Interfaz en español**: Todo el texto visible al usuario está en español. Los nombres de variables y comentarios alternan entre español e inglés.

---

## 5. Despliegue y Workflow

### 5.1. Estructura de Repositorios

El sistema se distribuye en **tres repositorios Git** independientes, cada uno con su propia historia de versiones, aislamiento de responsabilidades y ciclo de vida:

| Repositorio | Contenido | Rol |
|------------|-----------|-----|
| `oica-docker-compose` | Docker Compose, esquema SQL, Dockerfiles, script de setup | **Orquestador**: define cómo se ensamblan y ejecutan los servicios |
| `oica-steel-cutting-optimizer` | Servidor Flask, Celery Worker, Algoritmo Genético, modelos, utilidades | **Backend**: lógica de negocio y procesamiento |
| `tesis-frontend` | Aplicación Next.js, componentes React, integración WebSocket | **Frontend**: interfaz de usuario |

Esta separación permite que cada servicio evolucione independientemente. El repositorio orquestador clona los repositorios de servicio en el directorio `services/` (que está en `.gitignore`) mediante el script `init.sh`.

### 5.2. Script de Inicialización (`init.sh`)

El script `init.sh` funciona como un **proceso de entrega de obra automatizado**: desde una máquina virgen con sistema operativo Ubuntu, ejecuta todas las instalaciones necesarias y deja el sistema operativo.

**Secuencia de ejecución**:
1. Limpieza de instalaciones previas (`sudo rm -rf services`).
2. Verificación e instalación de Docker (si no está presente).
3. Verificación e instalación de Node.js 22 vía NVM (si no está presente).
4. Clonación de los repositorios de backend y frontend en `services/`.
5. Instalación de dependencias del frontend (`npm install`) y compilación (`npm run build`).
6. Detención de servicios previos y levantamiento de todos los contenedores (`docker compose up -d --build`).

**Advertencia**: El script ejecuta `sudo rm -rf services` al inicio, destruyendo cualquier cambio local no guardado en los repositorios clonados.

### 5.3. Control de Versiones como Bitácora de Obra

Git se emplea como **bitácora de obra digital**, donde cada *commit* representa un registro verificable de cambios con autor, fecha y descripción. La separación en tres repositorios permite:

- **Trazabilidad por servicio**: Los cambios en el algoritmo genético se rastrean independientemente de los cambios en la interfaz de usuario.
- **Responsabilidad aislada**: Cada repositorio puede asignarse a un equipo o responsable diferente sin riesgo de conflictos.
- **Versionamiento independiente**: El backend puede evolucionar a una versión 2.0 sin afectar la versión estable del frontend.

### 5.4. Comandos de Operación

| Operación | Comando | Contexto |
|-----------|---------|----------|
| Setup completo desde cero | `sudo chmod +x ./init.sh && ./init.sh` | Primera instalación |
| Reconstruir todos los servicios | `docker compose up -d --build` | Después de cambios en config |
| Reconstruir servicio específico | `docker compose build backend celery_worker` | Después de cambios en requirements.txt |
| Ver logs del backend | `docker compose logs -f backend` | Diagnóstico en tiempo real |
| Ver logs del worker | `docker compose logs -f celery_worker` | Seguimiento del AG |
| Resetear base de datos | `docker volume rm oica-app_postgres_data` + restart | Re-ejecución de init.sql |
| Sincronizar dependencias Python | `cp config/backend/requirements.txt services/backend/requirements.txt` | Después de editar requirements.txt en config/ |

### 5.5. Gestión de Dependencias Python

El proyecto mantiene **archivos de dependencias duplicados intencionalmente** debido a una restricción de Docker:

- **Fuente de verdad**: `config/backend/requirements.txt` y `config/celery_worker/requirements.txt`.
- **Copia de compilación**: `services/backend/requirements.txt` (dentro del build context de Docker).

Docker `COPY` solo puede acceder a archivos dentro del *build context* (`services/backend/`), pero los Dockerfiles residen en `config/`. Por lo tanto, después de editar las dependencias en `config/`, es necesario copiarlas manualmente al directorio de servicios antes de reconstruir las imágenes.

**Diferencia crítica entre backend y worker**: El backend utiliza `gevent` (para WebSocket con Socket.IO), mientras que el worker utiliza `eventlet` (requerido por Celery para concurrencia asíncrona). Sus archivos `requirements.txt` difieren exclusivamente en esta dependencia.

### 5.6. Esquema de Base de Datos: Inicialización sin Migraciones

El archivo `config/backend/init.sql` define el esquema de base de datos y se ejecuta **únicamente en la primera creación del volumen de PostgreSQL**. Este diseño implica que:

- Los cambios en el esquema no se aplican automáticamente a bases de datos existentes.
- Para aplicar cambios, se debe eliminar el volumen (`docker volume rm oica-app_postgres_data`) y reiniciar, o ejecutar scripts de migración SQL manualmente (ej. `config/backend/migration_remove_unique_document_number.sql`).

No se utiliza un sistema de migraciones formal (como Alembic o Flyway) dado que el proyecto se encuentra en fase de desarrollo activo con un único entorno de ejecución.
