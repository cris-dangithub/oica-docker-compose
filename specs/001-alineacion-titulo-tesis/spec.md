# Feature Specification: Alineación de OICA con el título fijo de la tesis

**Feature Branch**: `001-alineacion-titulo-tesis` (sin hook de ramas; rama de trabajo actual `production`)

**Created**: 2026-10-02

**Status**: Draft

**Input**: User description: "Alinear OICA con el título fijo de la tesis («Diseño y desarrollo de una aplicación web con Inteligencia Artificial para la distribución eficiente de barras de acero comercial de 6, 9 y 12 metros en Colombia, con desperdicios admisibles mediante el enfoque basado en patrones de corte y nesting»), según INF-014. Decisiones del usuario: (1) título fijo palabra por palabra; (2) desperdicios admisibles = umbral porcentual opcional ingresado por el usuario (no existe norma colombiana con máximo; en INVIAS art. 640/IDU el desperdicio va incluido en el precio unitario), la app reporta cumple/excede por proyecto y por diámetro, separa pérdida irrecuperable de saldo reutilizable, sin alterar el motor AG ni la huella del problema; (3) patrones de corte = agrupar barras con idéntico esquema de cortes en «patrón × repeticiones» en Excel/PDF/PNG, más una cota inferior Gilmore–Gomory (relajación lineal con generación de columnas) que mide la brecha del AG frente al mejor resultado posible, como métrica y no como optimizador; (4) nesting = nesting lineal (1D) definido con fuente, sin nesting 2D; (5) en Colombia = masas nominales NSR-10 con aviso de discrepancia y procedencia de cartillas 001/002 como obra colombiana confidencial anonimizada; (6) IA = AG encuadrado como computación evolutiva; distribución eficiente = métrica de aprovechamiento; aplicación web en lugar de «local» en el documento; (7) crear docs/tesis-doc/Referencias.md con fichas detalladas de cada referencia (normativa, obra pública, métodos, IA, nesting), indicando por qué se propuso, qué pregunta del usuario la originó, qué término del título respalda, dónde va en la tesis y su estado de verificación. Los 136 ensayos existentes deben seguir siendo válidos; no repetir la matriz."

## Contexto

El título de la tesis quedó fijado palabra por palabra (decisión del usuario, 2026-10-02). La
evaluación INF-014 mostró que varios términos no tienen respaldo en la aplicación ni en el
documento: «desperdicios admisibles», «enfoque basado en patrones de corte», «nesting»,
«Inteligencia Artificial», «distribución eficiente», «en Colombia» y «aplicación web» (el
documento aún dice «local»). Esta funcionalidad da a cada término un respaldo verificable, sin
cambiar el método de optimización validado ni invalidar la evidencia experimental ya obtenida
(136 ensayos y 12 controles de las cartillas 001 y 002).

Los objetivos vigentes de la tesis los aportó el autor (2026-10-02). Ya estaban alineados con
el título, y el autor aceptó ajustar su redacción para que sean verificables. La versión
aceptada, pendiente de revisión del director, es:

- **Objetivo general**: desarrollar una aplicación web que integre técnicas de inteligencia
  artificial, específicamente un algoritmo genético, para optimizar la distribución de barras de
  acero comercial de 6, 9 y 12 metros en Colombia, mediante patrones de corte unidimensional y
  enfoque de nesting lineal, con el fin de reducir el desperdicio a niveles admisibles y mejorar
  la eficiencia del uso del material.
- **OE1**: calcular la cantidad de barras por diámetro y longitud comercial (6, 9 y 12 m) y el
  aprovechamiento del material del plan de corte.
- **OE2**: medir el tiempo de procesamiento según el tamaño de la cartilla y el perfil de
  optimización (rápido, balanceado y profundo), y su relación con el desperdicio obtenido frente
  al nivel admisible definido por el usuario.
- **OE3**: registrar la reutilización de los sobrantes de barras de acero de proyectos anteriores
  como complemento para optimizar los recursos dispuestos para la ejecución de proyectos futuros.
- **OE4**: desarrollar un sistema de análisis de compra que genere planes de compra y corte
  verificados automáticamente (demanda, diámetro, capacidad y etapas), reduciendo las
  limitaciones del análisis manual.
- **OE5**: evaluar la eficiencia del algoritmo genético con la cartilla de un proyecto real de
  construcción en Colombia, comparando su desperdicio con heurísticas de referencia y con la cota
  inferior por patrones de corte. La comparación con el desperdicio registrado en obra se
  incorporará si se obtienen esos datos.

| Objetivo | Respaldo en esta funcionalidad | Estado previo |
|----------|--------------------------------|---------------|
| General | Historias 1 a 6 en conjunto | Parcial: web, algoritmo genético y reducción de desperdicio ya existen |
| OE1 | Historia 2 (resumen de compra) y métrica de aprovechamiento | Solo existe la lista barra por barra |
| OE2 | Historia 1 (comparación de versiones por perfil, tiempo, desperdicio y admisibilidad) | Ya se miden los tiempos; no hay evaluación frente a un nivel admisible |
| OE3 | Inventario importable y exportable, saldos entre etapas | Ya existe (INF-008, INF-012) |
| OE4 | Historia 2 (verificación independiente visible) | El validador existe, pero no se muestra al usuario |
| OE5 | Historia 4 (cota por patrones) y heurísticas de referencia existentes | Solo heurísticas; sin cota |

Actores:

- **Planificador de obra**: ingeniero o residente que sube la cartilla, configura condiciones y
  decide si el plan es aceptable frente a lo presupuestado.
- **Taller de corte**: quien ejecuta el plan y necesita instrucciones repetibles.
- **Autor de la tesis**: presenta resultados y debe poder defender cada término del título.
- **Jurado y director**: verifican la coherencia entre título, documento, aplicación y fuentes.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Evaluar el plan frente a un desperdicio admisible (Priority: P1)

El planificador indica, de forma opcional, el porcentaje de desperdicio que considera admisible
para el proyecto (por ejemplo, el que asumió en su análisis de precios unitarios o el que exige
su contrato). Al terminar la optimización, la aplicación le dice si el plan queda dentro o fuera
de ese límite, para el proyecto completo y para cada diámetro. También separa el material
perdido de forma irrecuperable (pérdida por corte y descartes) del saldo que sigue siendo
reutilizable.

**Why this priority**: «desperdicios admisibles» es el término del título más alejado de la
aplicación actual, que minimiza el desperdicio pero nunca lo contrasta con un límite. Es también
lo que más le sirve al planificador para decidir.

**Independent Test**: subir la cartilla 001 con un umbral bajo y luego con uno alto, y comprobar
que el estado cambia de «excede» a «dentro de lo admisible» sin que el plan de corte ni su
porcentaje de desperdicio cambien.

**Acceptance Scenarios**:

1. **Given** una cartilla válida y un umbral de 10 %, **When** el plan resultante tiene 7,9 % de
   desperdicio, **Then** la aplicación muestra «dentro de lo admisible» para el proyecto e indica
   el estado de cada diámetro según su propio porcentaje.
2. **Given** una cartilla válida y un umbral de 5 %, **When** el plan tiene 7,9 % de desperdicio,
   **Then** la aplicación muestra «excede», la diferencia en puntos porcentuales y qué diámetros
   exceden.
3. **Given** una cartilla sin umbral, **When** termina la optimización, **Then** la aplicación
   muestra «sin evaluar» y presenta igualmente el desperdicio y la pérdida irrecuperable.
4. **Given** un archivo procesado con umbral, **When** el usuario lo reprocesa con otro perfil
   sin tocar el umbral, **Then** la nueva versión conserva el mismo umbral y lo vuelve a evaluar.
   Si al reprocesar el usuario cambia o quita el umbral, la nueva versión usa el valor nuevo y
   las versiones anteriores conservan el suyo.
5. **Given** cualquier umbral, **When** se compara con la ejecución equivalente sin umbral (misma
   cartilla, parámetros y semilla), **Then** el plan de corte y sus métricas de desperdicio son
   idénticos.
6. **Given** un archivo procesado con los perfiles rápido, balanceado y profundo, **When** el
   usuario consulta sus versiones, **Then** puede comparar en una sola vista el perfil, el tiempo
   de procesamiento, el desperdicio y el estado de admisibilidad de cada versión (OE2).

---

### User Story 2 - Obtener el resumen de compra verificado (Priority: P2)

El planificador obtiene, para el plan generado, cuántas barras debe comprar o tomar de cada
diámetro y longitud (6, 9 y 12 m u otras del catálogo), separando las barras comerciales de las
del inventario adicional, con su masa y el aprovechamiento del material. El resultado indica que
el plan pasó la verificación independiente de demanda, diámetro, capacidad y etapas, de modo que
puede usarse como base de compra sin rehacer el cálculo a mano.

**Why this priority**: respalda directamente OE1 (cantidad de barras por longitud de compra) y
OE4 (análisis de compra verificado). Es la salida que el planificador necesita para comprar, y
hoy solo existe la lista barra por barra.

**Independent Test**: procesar la cartilla 002 y comprobar que la suma de barras del resumen de
compra es igual al número de barras del plan para cada diámetro y longitud, y que el resultado
muestra la verificación superada.

**Acceptance Scenarios**:

1. **Given** un plan terminado, **When** el usuario consulta sus resultados o descarga el Excel o
   el PDF, **Then** ve una tabla por diámetro y longitud con el número de barras, su origen
   (comercial o adicional), la masa y el aprovechamiento.
2. **Given** un plan que usa inventario adicional, **When** se genera el resumen, **Then** las
   barras del inventario aparecen separadas de las comerciales y no se cuentan como compra.
3. **Given** un plan terminado, **When** se consulta, **Then** se indica que pasó la verificación
   independiente de demanda, diámetro, capacidad y etapas.
4. **Given** un plan que no pasa la verificación, **When** termina el procesamiento, **Then** no se
   presenta como válido y se muestra el motivo.

---

### User Story 3 - Leer el plan como patrones de corte repetidos (Priority: P3)

El taller recibe el plan agrupado en patrones: cada patrón dice de qué barra se parte, qué piezas
se obtienen y en qué etapas, qué sobra y cuántas veces se repite. La vista barra por barra sigue
disponible para la trazabilidad completa, y cada barra indica a qué patrón pertenece. La imagen
del plan muestra el acomodo de piezas por patrón (nesting lineal).

**Why this priority**: respalda «enfoque basado en patrones de corte» y «nesting» con un producto
visible y útil en obra. Además, en la cartilla 002 la salida barra por barra tiene miles de
filas, y hoy la imagen y el PDF solo muestran muestras.

**Independent Test**: procesar la cartilla 002 y comprobar en el Excel que la suma de
repeticiones de todos los patrones es igual al número de barras utilizadas, y que reconstruir las
barras a partir de los patrones reproduce exactamente la demanda de la cartilla.

**Acceptance Scenarios**:

1. **Given** un plan con varias barras cortadas de forma idéntica, **When** se descarga el Excel,
   **Then** existe una hoja de patrones donde esas barras aparecen como un solo patrón con su
   número de repeticiones.
2. **Given** dos barras con las mismas piezas cortadas en etapas distintas, **When** se agrupan los
   patrones, **Then** aparecen como patrones distintos, porque la secuencia de etapas forma parte
   de la instrucción de corte.
3. **Given** el plan de la cartilla 002, **When** se descargan el PDF y la imagen, **Then** ambos
   presentan patrones con sus repeticiones. Si no caben todos, muestran los más repetidos e
   indican cuántos se omitieron y que el Excel contiene el total.
4. **Given** cualquier plan, **When** se consulta la vista barra por barra, **Then** cada barra
   indica el identificador de su patrón.

---

### User Story 4 - Medir la calidad del plan frente al mejor resultado posible (Priority: P4)

Para cada plan, la aplicación calcula una cota inferior de desperdicio con el enfoque clásico
basado en patrones de corte (Gilmore–Gomory). Es el porcentaje por debajo del cual ningún plan
puede bajar. Luego muestra la brecha entre el resultado del algoritmo genético y esa cota. La
cota solo mide; el plan lo sigue produciendo el algoritmo genético.

**Why this priority**: da al Cap. 4 una medida objetiva de calidad (hoy reconoce que no hay
certificado de optimalidad) y convierte el «mediante el enfoque basado en patrones de corte» del
título en un método usado de verdad. Depende de que exista el plan, y su valor principal es
académico.

**Independent Test**: calcular la cota para 001 y 002 y comprobar que el desperdicio de cada
ejecución registrada en los ensayos existentes es mayor o igual que la cota del caso
correspondiente. En instancias pequeñas resueltas por fuerza bruta, la cota debe ser menor o
igual que el óptimo.

**Acceptance Scenarios**:

1. **Given** un plan terminado, **When** se consultan sus resultados, **Then** se muestran la cota
   de desperdicio por patrones, la cota simple (aprovechamiento perfecto del material de las
   piezas) y la brecha del plan en puntos porcentuales.
2. **Given** un problema con inventario adicional limitado y pérdida por corte activa, **When** se
   calcula la cota, **Then** la cota respeta las cantidades disponibles y la pérdida por corte, y
   sigue siendo menor o igual que cualquier plan factible.
3. **Given** que la cota no termina de ajustarse dentro del tiempo asignado, **When** se presenta,
   **Then** se muestra una cota válida aunque más holgada, marcada como «no ajustada».
4. **Given** que el desperdicio del plan resulta inferior a la cota, **When** se detecta, **Then**
   se registra como error de dominio visible y el resultado no se presenta como válido.
5. **Given** los resultados existentes de los 136 ensayos, **When** se calcula la brecha para 001 y
   002, **Then** se obtiene sin volver a ejecutar el algoritmo genético.

---

### User Story 5 - Contexto colombiano, eficiencia e Inteligencia Artificial visibles (Priority: P5)

El planificador ve el aprovechamiento del material (100 % menos el desperdicio) como medida de
«distribución eficiente». Recibe un aviso si la masa por metro de su cartilla no coincide con la
masa nominal de las barras según la NSR-10. El tutorial define con precisión «algoritmo genético
(técnica de Inteligencia Artificial, computación evolutiva)», «nesting lineal», «patrón de
corte», «cota inferior» y «desperdicio admisible», sin prometer optimalidad.

**Why this priority**: respalda «en Colombia», «distribución eficiente», «Inteligencia
Artificial» y «nesting» con cambios pequeños, que no afectan resultados.

**Independent Test**: subir una cartilla cuya masa por metro de un diámetro difiera de la nominal
y comprobar que aparece el aviso sin bloquear el procesamiento. Revisar que el tutorial contiene
las cinco definiciones.

**Acceptance Scenarios**:

1. **Given** una cartilla con la masa nominal correcta, **When** se procesa, **Then** no aparece
   ningún aviso de masa.
2. **Given** una cartilla cuya masa por metro de #4 difiere más de 1 % de la nominal, **When** se
   procesa, **Then** se muestra un aviso con el diámetro, el valor de la cartilla y el nominal, y
   el plan se genera igualmente.
3. **Given** cualquier resultado nuevo, **When** se consulta, **Then** muestra el aprovechamiento
   y el desperdicio, que suman 100 %.

---

### User Story 6 - Documento de tesis y referencias coherentes con el título (Priority: P6)

El autor dispone de un documento de tesis donde cada término del título está definido y
respaldado por la aplicación y por fuentes. Tiene además un archivo de referencias con fichas
detalladas: por qué se propuso cada fuente, qué pregunta suya la originó, qué término respalda,
dónde va en la tesis y si ya está verificada.

**Why this priority**: el documento solo puede describir lo que la aplicación ya hace (prioridad
del proyecto: app correcta → coherencia → documento). Por eso va al final, aunque el archivo de
referencias puede empezarse de inmediato.

**Independent Test**: un revisor toma cada término del título y encuentra, en el documento, su
definición, la funcionalidad que lo respalda y al menos una fuente con estado de verificación.

**Acceptance Scenarios**:

1. **Given** el archivo de referencias, **When** se revisa cualquier ficha, **Then** contiene cita
   completa, enlace si existe, estado de verificación, motivo de la propuesta, pregunta de origen
   del usuario (textual), término del título que respalda, ubicación prevista en la tesis y
   advertencias.
2. **Given** las fuentes normativas (NSR-10, especificaciones de acero de refuerzo de INVIAS e
   IDU, resolución de residuos de construcción y demolición), **When** se citan, **Then** el
   documento dice explícitamente que ninguna fija un porcentaje máximo de desperdicio de acero, y
   que el desperdicio va dentro del precio unitario en la obra pública.
3. **Given** el Cap. 1, **When** se lee, **Then** el título es el fijo y la aplicación se describe
   como web. Los objetivos son los aportados por el autor, con la redacción aceptada el
   2026-10-02 y la nota «pendiente de revisión del director».
4. **Given** el Cap. 2, **When** se lee la sección de alcance, **Then** «nesting» se define como
   nesting lineal (1D) con fuente. Se reconoce que en la tipología académica el término suele
   reservarse para piezas irregulares, y se mantiene la exclusión de modelos generativos, redes
   neuronales y nesting bidimensional.
5. **Given** el documento, **When** se describe el origen de los datos, **Then** las cartillas 001
   y 002 figuran como provenientes de una obra colombiana, con datos confidenciales y
   anonimizados.

---

### Edge Cases

- Umbral ausente: el estado es «sin evaluar» y no se muestra ningún juicio de cumplimiento.
- Umbral fuera de rango (≤ 0, ≥ 100 o no numérico): se rechaza antes de encolar el trabajo, con
  un mensaje claro.
- Un diámetro con desperdicio exactamente igual al umbral se considera «dentro de lo admisible».
- Resultados históricos sin los campos nuevos (umbral, patrones, cota, aviso de masa): se
  muestran sin error, con «no disponible», y no se modifican.
- Un umbral distinto con la misma cartilla, catálogo, inventario, parámetros y semilla no cambia
  la identidad del problema ni la estimación de tiempo basada en ejecuciones anteriores.
- Un plan cuyas barras son todas distintas tiene tantos patrones como barras, y la agrupación no
  falla.
- Un número de patrones distintos superior al límite visual del PDF o de la imagen activa la
  regla de «más repetidos + aviso» sin superar los límites de tamaño vigentes.
- Las barras de inventario adicional y las comerciales de igual longitud forman patrones
  distintos, porque su origen difiere.
- Cota con pérdida por corte activa: la capacidad de cada patrón descuenta la pérdida de cada
  separación, salvo cuando una pieza consume exactamente el saldo.
- Un diámetro con una sola longitud de pieza y una sola longitud de barra: la cota debe coincidir
  con el óptimo analítico (⌈n/q⌉ barras, con q piezas por barra). Con varias longitudes de barra
  solo se exige que la cota no supere el óptimo.
- Un diámetro de la cartilla sin masa nominal conocida: no se emite aviso de masa y se informa que
  no se pudo contrastar.
- Una cartilla con pedidos #2: el comportamiento actual (catálogo por defecto sin #2) se documenta;
  el usuario puede añadir #2 editando el catálogo.
- Resumen de compra con inventario adicional: las barras tomadas del inventario se listan aparte
  y no suman a la compra. Las barras de inventario no usadas no aparecen en el resumen; quedan en
  el inventario final.
- Resumen de compra con longitudes distintas de 6, 9 y 12 m (catálogo editado): se listan las
  longitudes realmente usadas, sin forzar las tres de referencia.
- Comparación de versiones con perfiles distintos y umbrales distintos: cada versión muestra su
  propio umbral; la comparación no mezcla estados evaluados con umbrales diferentes sin indicarlo.
- Versiones históricas sin tiempo registrado o sin estado de verificación: se muestran como «no
  disponible».

## Requirements *(mandatory)*

### Functional Requirements

**Desperdicio admisible**

- **FR-001**: El sistema MUST permitir que el usuario ingrese, de forma opcional, un umbral de
  desperdicio admisible en porcentaje (0 < valor < 100) al subir una cartilla.
- **FR-002**: El sistema MUST NOT proponer un valor por defecto del umbral, y MUST indicar junto
  al campo que el valor proviene del presupuesto o contrato del usuario y que no se identificó
  una norma colombiana que fije un máximo. Mientras las fichas de INVIAS e IDU no estén
  «verificadas» en `Referencias.md`, el texto MUST NOT nombrar normas concretas como respaldo.
- **FR-003**: El sistema MUST comparar el umbral con el porcentaje de desperdicio por masa ya
  definido en INF-012 (todo lo que sobra al final del proyecto sobre la masa de barras usadas), a
  nivel de proyecto y de cada diámetro, y reportar «dentro de lo admisible», «excede» o «sin
  evaluar», junto con la diferencia en puntos porcentuales.
- **FR-004**: El sistema MUST reportar por separado la pérdida irrecuperable (pérdida por corte +
  descartes) y el saldo reutilizable final, en masa y en porcentaje.
- **FR-005**: El umbral MUST NOT alterar el plan de corte, la búsqueda del algoritmo genético, la
  identidad del problema que se usa para comparar ejecuciones, ni la estimación de tiempo basada
  en ejecuciones anteriores. MUST conservarse con el archivo y reutilizarse al reprocesar. Al
  reprocesar, el usuario MAY cambiarlo o quitarlo; cada versión guarda el umbral con el que se
  evaluó (decisión del usuario, 2026-10-02).
- **FR-006**: El estado de admisibilidad MUST aparecer en la lista de archivos, en el Excel (con
  detalle por diámetro) y en el PDF.

**Resumen de compra, tiempos y verificación (OE1, OE2, OE4)**

- **FR-027**: El sistema MUST generar un resumen de compra por diámetro, longitud de barra y origen
  (comercial o inventario adicional), con número de barras, masa y aprovechamiento. MUST estar
  visible en los resultados, el Excel (hoja propia) y el PDF. La suma de barras del resumen MUST
  ser igual al número de barras del plan para cada diámetro y longitud.
- **FR-028**: La vista de versiones de un archivo MUST permitir comparar perfil de optimización,
  tiempo de procesamiento, desperdicio y estado de admisibilidad de cada versión.
- **FR-029**: Cada resultado MUST indicar que pasó la verificación independiente de demanda,
  diámetro, capacidad y etapas. Un plan que no la pase MUST NOT presentarse como válido, y MUST
  mostrar el motivo.

**Patrones de corte y nesting lineal**

- **FR-007**: El sistema MUST agrupar las barras del plan en patrones de corte. Dos barras
  pertenecen al mismo patrón solo si coinciden en diámetro, origen, longitud de barra, secuencia
  de cortes (etapa, longitud y cantidad), pérdida por corte, descarte y saldo final.
- **FR-008**: El Excel MUST incluir una hoja de patrones con: identificador, diámetro, longitud y
  origen de la barra, secuencia legible de cortes por etapa, repeticiones, aprovechamiento del
  patrón, pérdida por corte, descarte y saldo. Cada barra de la vista barra por barra MUST indicar
  su patrón.
- **FR-009**: El PDF y la imagen MUST presentar el plan por patrones con sus repeticiones,
  respetando los límites de tamaño vigentes. Cuando no quepan todos, MUST mostrar los más
  repetidos e indicar cuántos se omitieron.
- **FR-010**: La imagen MUST identificarse como «nesting lineal por patrones de corte».
- **FR-011**: La suma de repeticiones de todos los patrones MUST ser igual al número de barras
  utilizadas, y reconstruir las barras desde los patrones MUST satisfacer exactamente la demanda.

**Cota inferior por patrones**

- **FR-012**: El sistema MUST calcular para cada plan una cota inferior de material, y por tanto de
  porcentaje de desperdicio, con el enfoque de patrones de corte de Gilmore–Gomory (relajación
  lineal), por diámetro. MUST considerar las longitudes comerciales, el inventario adicional
  limitado y la pérdida por corte, y relajar el orden de etapas.
- **FR-013**: El sistema MUST reportar también la cota simple y la brecha del plan frente a la
  cota por patrones, en puntos porcentuales. La cota simple supone aprovechamiento perfecto:
  material mínimo igual a la longitud total de las piezas, redondeada al múltiplo común de las
  longitudes de barra disponibles. Se acompaña del número mínimo de barras, que es la longitud
  total de las piezas dividida por la barra disponible más larga, redondeada hacia arriba.
- **FR-014**: Si la cota no se ajusta por completo dentro del tiempo asignado, el sistema MUST
  presentar una cota todavía válida y marcarla como «no ajustada».
- **FR-015**: Si el desperdicio del plan es menor que la cota, el sistema MUST registrar un error de
  dominio visible y MUST NOT presentar el resultado como válido.
- **FR-016**: La cota MUST NOT usarse para construir ni modificar el plan de corte: es solo una
  métrica.
- **FR-017**: El autor MUST poder obtener la cota y la brecha de las cartillas 001 y 002 frente a
  los ensayos ya registrados, sin volver a ejecutar el algoritmo genético.

**Colombia, eficiencia, IA**

- **FR-018**: El sistema MUST contrastar la masa por metro de cada diámetro de la cartilla con la
  masa nominal de referencia (tabla de barras de la plantilla de cartilla, cuya correspondencia
  con la NSR-10 debe verificarse) y emitir un aviso no bloqueante cuando la diferencia supere
  1 %. El aviso MUST verse en los resultados, el Excel y el PDF. Mientras la correspondencia no
  esté verificada, el rótulo MUST ser «masa de referencia (NSR-10, por verificar)».
- **FR-019**: El sistema MUST mostrar el aprovechamiento (100 % − desperdicio) en los resultados
  nuevos.
- **FR-020**: El tutorial MUST definir «algoritmo genético (técnica de IA, computación
  evolutiva)», «nesting lineal», «patrón de corte», «cota inferior» y «desperdicio admisible», sin
  afirmar optimalidad.

**Documento y referencias**

- **FR-021**: Se MUST crear `docs/tesis-doc/Referencias.md` con una ficha por referencia que
  incluya: cita completa, enlace si existe, estado de verificación («verificada», «verificar cita
  literal», «verificar edición y páginas», «pendiente de localizar»), motivo de la propuesta,
  pregunta textual del usuario que la originó, término del título que respalda, ubicación prevista
  en la tesis y advertencias.
- **FR-022**: Las fichas MUST cubrir al menos: NSR-10 (Decreto 926 de 2010); especificación de
  acero de refuerzo de INVIAS (art. 640) y del IDU; Resolución 472 de 2017 del Ministerio de
  Ambiente y su modificación vigente; el estudio de porcentaje de desperdicio de acero en vivienda
  (RECIAMUC, 2022) y las guías de APU (marcadas como débiles); Gilmore y Gomory; la tipología de
  corte y empaque de Wäscher, Haußner y Schumann (2007); Benjaoran y Bhokha (2013); fuentes de IA
  y algoritmos genéticos (Russell y Norvig; Holland; Goldberg); una fuente de «nesting lineal»; y
  las fuentes ya citadas en la tesis.
- **FR-023**: El documento de tesis MUST usar el título fijo, describir la aplicación como web,
  definir cada término del título con su respaldo y presentar la procedencia de 001/002 como obra
  colombiana confidencial y anonimizada.
- **FR-024**: El Cap. 1 MUST contener el objetivo general y los cinco objetivos específicos
  aportados por el autor, con la redacción aceptada el 2026-10-02 (sección Contexto), marcados
  como «redacción ajustada, pendiente de revisión del director». No se añaden objetivos nuevos.
- **FR-025**: El Cap. 4 MUST evaluar OE5 comparando el desperdicio del algoritmo genético en
  001/002 con las heurísticas de referencia y con la cota por patrones (brecha). Solo MUST mostrar
  una evaluación de admisibilidad si el autor aporta un porcentaje con fuente. La comparación con
  el desperdicio registrado en obra queda fuera de esta funcionalidad hasta que existan datos.
- **FR-026**: Se MUST registrar en los archivos de control del proyecto la resolución de INF-014,
  las nuevas inferencias (desperdicio admisible; patrones y cota) y la actualización del riesgo
  académico correspondiente.

### Key Entities

- **Umbral de desperdicio admisible**: porcentaje opcional definido por el usuario para un
  archivo; se conserva en sus versiones y no forma parte de la identidad del problema.
- **Evaluación de admisibilidad**: estado (dentro, excede, sin evaluar) y diferencia, para el
  proyecto y para cada diámetro; incluye la pérdida irrecuperable y el saldo reutilizable.
- **Patrón de corte**: esquema repetible de corte de una barra (diámetro, origen, longitud,
  secuencia de cortes por etapa, pérdida, descarte, saldo) con su número de repeticiones; agrupa
  barras del plan.
- **Cota inferior**: material mínimo teórico por diámetro y su porcentaje de desperdicio
  equivalente (cota simple y cota por patrones), con indicador de ajuste y brecha del plan.
- **Aviso de masa nominal**: diámetro, masa por metro de la cartilla, masa nominal NSR-10
  (Título C, Tabla C.3.5.3-2; verificada el 2026-10-02) y diferencia relativa.
- **Resumen de compra**: por diámetro, longitud de barra y origen, número de barras, masa y
  aprovechamiento; se deriva de las barras del plan y su total coincide con ellas.
- **Estado de verificación**: resultado de la comprobación independiente de demanda, diámetro,
  capacidad y etapas de cada versión, con el motivo cuando falla.
- **Ficha de referencia**: fuente bibliográfica o normativa con su trazabilidad hacia las
  preguntas del usuario, los términos del título y las secciones de la tesis.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Cada uno de los nueve componentes del título (aplicación web, Inteligencia
  Artificial, distribución eficiente, 6/9/12 m, Colombia, desperdicios admisibles, patrones de
  corte, nesting, diseño y desarrollo) tiene al menos una funcionalidad o sección del documento que
  lo respalda y al menos una fuente con estado de verificación declarado.
- **SC-002**: Con la misma cartilla, parámetros y semilla, el plan y el porcentaje de desperdicio
  de 001 y 002 son idénticos a los registrados en los ensayos existentes: 0 diferencias en los 136
  ensayos de referencia, con o sin umbral.
- **SC-003**: En el 100 % de los resultados nuevos con umbral se muestra un estado de
  admisibilidad del proyecto y de cada diámetro. El usuario puede saber si su plan cumple sin
  abrir ningún archivo descargado.
- **SC-004**: En el 100 % de los planes, la suma de repeticiones de patrones es igual al número de
  barras, y la reconstrucción desde patrones satisface exactamente la demanda.
- **SC-005**: Para la cartilla 002, la hoja de patrones tiene al menos 5 veces menos filas que la
  vista barra por barra (supuesto a confirmar al medir), lo que facilita la lectura en taller.
- **SC-006**: En el 100 % de los ensayos existentes de 001 y 002, el desperdicio obtenido es mayor
  o igual que la cota por patrones del caso. En instancias pequeñas resueltas por fuerza bruta, la
  cota nunca supera el óptimo.
- **SC-007**: Para la cartilla 002 (perfil balanceado, semilla 0, condiciones físicas por
  defecto), el tiempo de motor + análisis + artefactos medido con el mismo arnés no aumenta más
  de 25 % respecto a la medición previa a la feature.
- **SC-008**: El 100 % de las fichas de `Referencias.md` contiene los ocho campos exigidos. Ninguna
  fuente no verificada aparece en el documento de tesis como si estuviera verificada.
- **SC-009**: El objetivo general y cada uno de los cinco objetivos específicos tienen al menos una
  funcionalidad o evidencia verificable descrita en esta especificación y presentada en la tesis.
- **SC-010**: En el 100 % de los planes, el total de barras del resumen de compra coincide con el
  número de barras del plan para cada diámetro y longitud. El planificador obtiene su lista de
  compra sin hacer cálculos adicionales.

## Assumptions

- El título es fijo. Los objetivos vigentes los aportó el autor y su redacción ajustada se aceptó
  el 2026-10-02. El director revisará esa redacción, pero no el título.
- No hay resumen de compra real de la obra de la cartilla 002, solo su demanda. Por eso OE5 se
  evalúa con heurísticas y con la cota por patrones. Si el autor consigue facturas o remisiones de
  esa u otra obra colombiana (al menos kg comprados por diámetro), se añadirán como comparación
  adicional anonimizada en una funcionalidad posterior.
- El umbral se compara con el desperdicio definido en INF-012 (incluye el saldo reutilizable final).
  La pérdida irrecuperable se informa aparte como referencia.
- No existe una norma colombiana que fije un porcentaje máximo de desperdicio de acero de refuerzo.
  En la obra pública (INVIAS art. 640, IDU) el acero se paga por kilogramo colocado según planos y
  el desperdicio va incluido en el precio unitario. La cita literal debe verificarse en los
  documentos oficiales antes de incluirla en la tesis.
- La masa nominal de referencia es la tabla de barras corrugadas de la NSR-10, que coincide con la
  hoja de masas de la plantilla de cartilla. La tolerancia del aviso es 1 %.
- El catálogo por defecto mantiene los diámetros actuales (#3–#18) y las longitudes 6, 9 y 12 m.
  Añadir #2 queda fuera de alcance porque cambiaría la identidad de los problemas nuevos y su
  estimación de tiempo.
- «Nesting» se entiende como nesting lineal (1D), según el uso industrial en la fabricación con
  barras y perfiles. El nesting bidimensional queda fuera de alcance.
- La relajación de etapas en la cota la vuelve válida pero posiblemente holgada. Esto se declara en
  la tesis.
- El cálculo de la cota puede requerir ampliar el entorno de ejecución de la aplicación. Por la
  restricción de espacio en disco, cualquier reconstrucción de ese entorno requiere aprobación
  previa del usuario.
- Las cartillas 001 y 002 provienen de una obra colombiana cuyos datos son confidenciales; se
  presentan anonimizadas.
- La matriz de 136 ensayos (y los 12 controles) se vuelve a ejecutar solo como verificación de
  regresión (decisión del usuario, 2026-10-02): no produce evidencia nueva para el Cap. 4. La
  brecha se calcula sobre los resultados registrados, sin ejecutar el algoritmo genético.
- Rige la constitución del proyecto (`.specify/memory/constitution.md`, v1.0.0, 2026-10-02), que
  prevalece sobre `AGENTS.md` y `CLAUDE.md`.
