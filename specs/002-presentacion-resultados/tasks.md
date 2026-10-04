---

description: "Tareas de la spec 002: presentación de resultados para el usuario (enmendada el 2026-10-04: explorador de patrones)"
---

# Tasks: Presentación de resultados para el usuario

**Input**: Documentos de diseño en `specs/002-presentacion-resultados/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md)

**Regenerado el 2026-10-04** tras la enmienda «explorador de patrones», sin ninguna tarea hecha
previamente.

- Las historias se renumeraron por prioridad: US1 compra, US2 explorador, US3 nesting de
  archivos, US4 totales y calidad en la web, US5 trazabilidad.
- **No hay tareas de `analisis-2`**: `backend/cutting/analysis.py` y
  `backend/tests/test_analisis.py` no se tocan (research R-10).

**Tests**: SÍ. La constitución exige pruebas automatizadas de las invariantes de los artefactos.

- Las pruebas de cada historia se escriben antes de su implementación y deben fallar primero.
- El frontend no tiene runner de pruebas y no se añade uno (plan, Technical Context). Sus puertas
  son `typecheck`, `lint`, `build` y axe.

**Organization**: tareas agrupadas por historia de usuario. Muchas tocan
`backend/cutting/report.py` y `backend/tests/test_report_presentacion.py`, así que solo se marcan
[P] las que van en archivos distintos sin dependencias pendientes.

**Ejecución de pruebas** (en todo el documento): `python3 scripts/check_cutting_container.py
--all-tests --container oica-validation-backend-1`. El arnés carga el código del árbol de trabajo
en memoria, sin reconstruir imágenes.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: se puede ejecutar en paralelo (archivos distintos, sin dependencias pendientes).
- **[Story]**: historia a la que pertenece (US1–US5).

---

## Phase 1: Setup (preparación y línea base)

**Purpose**: leer las reglas obligatorias y medir la línea base de tiempo **antes** de cambiar
código.

- [ ] T001 Leer las reglas obligatorias y anotar en las notas de la tarea las que apliquen:
  - `tests/data/002/ANALISIS_RESULTADOS.md` §12, obligatorio antes de tocar
    `backend/cutting/report.py` y `backend/celery_worker.py`.
  - `docs/oica-redesign/AI-DESIGN-RULES.md`, `docs/oica-redesign/STATE.md` y
    `docs/oica-redesign/DESIGN-SYSTEM.md`, obligatorios antes de tocar la UI.
  - Las reglas de UI que apliquen a tablas, tarjetas, avisos, filas-botón desplegables,
    diagramas a escala, tokens `data/*` y controles de `frontend/src/components/ui/form-controls.tsx`.
- [ ] T002 Medir la línea base de SC-007 con el código actual:
  - 5 ejecuciones de `python3 scripts/check_cutting_container.py --artifacts-smoke --dataset
    tests/data/002/002-ingeBigTest.xlsx --profiles balanceado --seeds 1 --container
    oica-validation-backend-1`, con las condiciones físicas por defecto (como en
    `tests/benchmarks/2026-10-02-sc007-comparacion.json`).
  - Guardar los totales, el motor, el análisis y los artefactos en
    `tests/benchmarks/2026-10-04-sc007-presentacion-antes.jsonl`, sin sobrescribir.
  - Si el arnés no admite repeticiones, ejecutarlo 5 veces con salidas numeradas.

---

## Phase 2: Foundational (bloquea todas las historias)

**Purpose**: ayudantes de formato y cobertura, y número de versión disponible para el PDF.

- [ ] T003 En `backend/cutting/report.py`, añadir los ayudantes:
  - `numero(valor, decimales=2)`: punto de miles y coma decimal (por ejemplo `152.039,57`);
    `None` → «no disponible»; sin `locale` (research R-05).
  - `PERFILES = {'rapido': 'Rápido', 'balanceado': 'Balanceado', 'profundo': 'Profundo'}`.
  - `cobertura(mostrados, total_patrones, total_barras)`: devuelve `(n, m, b, t, pct)`, con
    `b = Σ repeticiones de los mostrados`, y el texto «Se muestran N de M patrones, que cubren B
    de T barras (x %)» (data-model §6; invariante «`b ≤ t`; si `n = m`, entonces `b = t`»).
- [ ] T004 Crear `backend/tests/test_report_presentacion.py`:
  - Un plan pequeño de prueba (dos diámetros, dos etapas, inventario adicional opcional), con el
    estilo de `backend/tests/test_cutting_api.py` (`normalize` → `optimize` → `analizar` →
    `generate` en un `TemporaryDirectory`).
  - Pruebas iniciales de `numero()` y `cobertura()`, incluidos `n = m ⇒ b = t` y `b ≤ t`.
- [ ] T005 Pasar el número de versión a `generate()`:
  - En `backend/cutting/report.py`, ampliar la firma a `generate(problem, result, directory,
    title='', visuals=True, version=None)`, compatible con el arnés `--artifacts-smoke` y las
    pruebas existentes.
  - En `backend/celery_worker.py`, mover el cálculo de `version` (consulta `latest`, líneas
    ~271-273) **antes** de la llamada a `generate(...)` (línea ~260), pasar `version=version` y
    reutilizar el mismo valor al crear `ProcessingResult` (research R-09).
  - No cambiar ninguna otra lógica del worker.

**Checkpoint**: ayudantes probados y la versión llega a `generate()`.

---

## Phase 3: User Story 1 - Ver primero lo que hay que comprar y los indicadores clave (Priority: P1) 🎯 MVP

**Goal**: el Excel empieza con «Resumen» (indicadores legibles y totales de compra) y el PDF
empieza con encabezado, verificación, indicadores clave y compra con totales.

**Independent Test**: procesar la 001. La primera hoja del Excel es «Resumen», con sus totales;
la primera página del PDF tiene los indicadores clave y la compra con totales (quickstart §3).

### Tests for User Story 1

- [ ] T006 [US1] En `backend/tests/test_report_presentacion.py`, pruebas que deben fallar antes de T008–T011:
  - El orden exacto de las 13 hojas (contracts/artefactos.md §1).
  - La ausencia de «Metricas».
  - «Resumen» con los 21 indicadores de contracts/artefactos.md §1.1, en orden y con su `unidad`.
  - El bloque «Totales de compra», localizado por su título: «Total comprado» + «Total tomado
    del inventario» = filas de Barras, y la masa = Σ `Resumen de compra.masa_kg` (data-model §3).
  - «Resumen de compra» sin filas de total.
- [ ] T007 [US1] En `backend/tests/test_report_presentacion.py`, pruebas del PDF. Se extrae el
  texto con `pypdf` si está en la imagen; si no, se comprueba el HTML generado mediante una
  función pura `pdf_html(...)` expuesta por `report.py`:
  - El encabezado contiene el proyecto, la versión, el perfil legible y «hora de Colombia».
  - El orden: verificación → indicadores clave → resumen de compra con totales.
  - Las cifras del usuario usan coma decimal (por ejemplo, el desperdicio con dos decimales).

### Implementation for User Story 1

- [ ] T008 [US1] En `backend/cutting/report.py`, implementar `resumen_rows(problem, result, analisis)`:
  - 21 filas `{indicador, valor, unidad}`, en el orden y con los orígenes de
    contracts/artefactos.md §1.1.
  - Un dato faltante se muestra como «no disponible» o «sin evaluar» (data-model §2: «nunca una
    celda vacía ambigua»).
  - Los valores numéricos siguen siendo números.
- [ ] T009 [US1] En `backend/cutting/report.py`, implementar `totales_compra_rows(analisis)` a
  partir de `analisis['resumen_compra']`:
  - Una fila por diámetro y origen (`Compra` o `Inventario adicional`).
  - «Total comprado» y, si hay inventario, «Total tomado del inventario» (data-model §3).
  - Si falta `resumen_compra`, una fila «no disponible».
- [ ] T010 [US1] En `generate()` de `backend/cutting/report.py`:
  - Escribir la hoja «Resumen» con dos bloques: los indicadores desde la fila 1, una fila en
    blanco, la celda de título «Totales de compra» y la tabla de totales (`startrow` de pandas
    más una celda de título con openpyxl).
  - Reordenar todas las hojas según contracts/artefactos.md §1 y dejar de escribir «Metricas».
  - Escribir provisionalmente los escalares técnicos en una hoja «Trazabilidad» mínima; su
    contenido final se completa en T037.
- [ ] T011 [US1] En `backend/cutting/report.py`, reestructurar el HTML del PDF en una función pura
  `pdf_html(problem, result, analisis, patrones, title, version, imagenes)`, con las secciones de
  contracts/artefactos.md §2 en orden:
  1. Encabezado: proyecto escapado, versión o «no asignada», perfil con `PERFILES` y fecha con
     `datetime.now(timezone(timedelta(hours=-5)))`, rotulada «hora de Colombia».
  2. Verificación.
  3. Indicadores clave.
  4. Resumen de compra, con filas de total por diámetro y total general (reutilizar
     `totales_compra_rows`).

  Las secciones 5–9 reutilizan por ahora `patrones_html`, `admisibilidad_html`, `cota_html` y
  `avisos_html`; se completan en US3 y US5. Aplicar `numero()` a todas las cifras visibles, con 3
  decimales en la cota y la brecha (FR-011).
- [ ] T012 [US1] Ejecutar las pruebas:
  - Las de T006–T007 deben pasar.
  - También todas las existentes, salvo las que dependan de «Metricas» o de `stock_id`, que se
    actualizan en US5 (anotarlas).
  - Corregir lo necesario.

**Checkpoint**: la US1 se puede demostrar con el Excel y el PDF de la 001 (MVP).

---

## Phase 4: User Story 2 - Explorar todos los patrones de corte en la aplicación web (Priority: P2)

**Goal**: la sección «Patrones de corte» del detalle muestra **todos** los patrones de la versión,
dibujados a escala común, con filtros (diámetro, etapa, origen y pedido), un selector de orden,
la cobertura y un detalle por patrón (piezas, pedidos y rangos de barras). Los datos vienen de
`GET /patrones/<storage_uuid>`, que los reconstruye desde `resultados` sin ejecutar el AG.

**Independent Test**: con la versión de la 002, el explorador muestra 136 patrones y 13.955
barras. Filtrar por diámetro y pedido cambia la cobertura. El detalle del patrón más repetido se
abre con el teclado, y sus identificadores, repeticiones y secuencia coinciden con la hoja
«Patrones» del Excel (quickstart §7).

### Tests for User Story 2

- [ ] T013 [P] [US2] Crear `backend/tests/test_vista_patrones.py` con pruebas que deben fallar
  antes de T015:
  - **Planes de prueba**: el plan pequeño de T004 (con y sin reglas físicas, incluidos descartes
    de fin de etapa) y el caso de 340 patrones de `test_artefactos_por_patrones_acotados` en
    `backend/tests/test_cutting_api.py`. Para cada uno: `optimize` → `report.legacy_patterns` →
    `json.loads(json.dumps(...))`, para simular el JSONB → `vista_patrones.vista(resultados,
    metricas)`.
  - **Coherencia con el Excel** (FR-025, SC-010): los campos `patron_id` a `saldo_m` de cada
    patrón son iguales a `report.patrones_rows(problem, patterns.agrupar(problem,
    result['bars'])[0])`, en el mismo orden, y el `patron_por_barra` reconstruido es igual al
    original.
  - **Invariantes de data-model §8.3**:
    - `Σ repeticiones = totales.barras = len(resultados)`.
    - `barras.total = repeticiones = Σ rangos.n`.
    - Para cada pieza, `Σ pedidos.piezas = cantidad × repeticiones`.
    - Para cada pedido, `piezas = Σ Cantidad` de sus filas en `problem['orders']`.
    - `escala_m = max(longitud_m)`.
  - **Rangos** (R-18): `['#4:1', '#4:2', '#4:3', '#4:7']` → `[{desde:'#4:1', hasta:'#4:3', n:3},
    {desde:'#4:7', hasta:'#4:7', n:1}]`.
  - **Orden de `pedidos`**: numérico si todos son números (`'2' < '10'`) y textual si no.
  - **No disponible** (FR-030): `vista` devuelve `{'disponible': False, 'motivo': …}` sin escala,
    con `resultados` vacío y con registros sin `trazabilidad_cortes`.
  - **Inconsistencia** (FR-025): alterar una repetición del `top` de `metricas.analisis.patrones`
    o quitar un registro de `resultados` lanza un error de dominio con «Patrones inconsistentes».
- [ ] T014 [US2] En `backend/tests/test_cutting_api.py`, pruebas de la ruta `GET
  /patrones/<storage_uuid>` (contracts/api-patrones.md) que deben fallar antes de T016. Se usa la
  base SQLite en memoria de la clase, creando un `ProcessingResult` con `resultados` de
  `legacy_patterns` y `metricas` con `escala_longitudes`. Casos:
  - 200 con `disponible: true` y los campos del contrato.
  - 200 con `disponible: false` en cada caso de contracts/api-patrones.md:
    - `result_status = 'processing'` o un estado de error que no sea `error_generation`;
    - `metricas.valido` en `false` o ausente, con el motivo de verificación (FR-030;
      constitución, Principio I);
    - una versión sin `trazabilidad_cortes`.
  - 200 con `disponible: true` para `result_status = 'error_generation'` con un plan válido.
  - 404 para un uuid inexistente.
  - 500 con «Patrones inconsistentes» para datos alterados, sin cuerpo parcial.
  - La ruta no modifica la fila: `updated_at` y `resultados` iguales antes y después (FR-024).

### Implementation for User Story 2

- [ ] T015 [US2] Crear `backend/cutting/vista_patrones.py`, un módulo puro (research R-16, R-18 y
  R-19; data-model §8):
  - **`barras_desde_resultados(resultados, escala)`**: devuelve las barras con `longitud`,
    `kerf`, `discarded` y `remaining` = `round(valor_m × escala)`, `cuts` = `trazabilidad_cortes`
    y `discard_events` = `descartes_fin_etapa`. Devuelve `None` si falta la escala o algún
    registro no tiene `trazabilidad_cortes`.
  - **`rangos(bar_ids)`**: agrupa en rangos consecutivos por diámetro.
  - **`vista(resultados, metricas)`**: llama a `patterns.agrupar({'scale': escala}, barras)` y a
    `report.patrones_rows`, y añade `etapas`, `piezas` (pedidos por posición *i* de los cortes) y
    `barras`. También calcula los índices `diametros`, `etapas`, `origenes` y `pedidos`, `escala_m`
    y `totales`.
  - **Comprobaciones antes de devolver**: Σ repeticiones, coherencia con
    `metricas['analisis']['patrones']` si existe e invariantes de pedidos. Si alguna falla,
    `raise ValueError('Patrones inconsistentes: …')`.
  - No importa nada de la base ni de Flask.
- [ ] T016 [US2] En `backend/server.py`, añadir `@app.route('/patrones/<uuid>', methods=['GET'])`
  (contracts/api-patrones.md):
  - Busca `ProcessingResult` por `storage_uuid` (404 `{"error": "Versión no encontrada"}`) y
    carga solo `resultados` y `metricas` (`load_only`).
  - Antes de reconstruir, aplica en orden las comprobaciones de «200 — patrones no disponibles»
    del contrato. Responde `disponible: false` con su motivo si `result_status` no es
    `completed` ni `error_generation`, o si `metricas.get('valido') is not True` (FR-030; un
    plan no verificado nunca se presenta como válido).
  - Delega en `vista_patrones.vista`. Arma la respuesta como un diccionario **nuevo** en cada
    llamada (`{**vista, 'storage_uuid': …, 'version_number': …, 'motor': …}`), sin modificar el
    objeto cacheado.
  - Si hay `ValueError` de inconsistencia, lo registra en el log y responde 500 sin datos
    parciales.
  - Caché `functools.lru_cache(maxsize=8)` sobre una función interna con clave `storage_uuid`;
    solo cachea vistas disponibles.
  - Sin escrituras en la base.
- [ ] T017 [P] [US2] Añadir los tokens de etapa (research R-17; contracts/ui.md «Tokens de color
  nuevos»):
  - En `frontend/src/app/globals.css`, `--color-data-stage-1` … `--color-data-stage-6`, como alias
    de primitivos existentes (`--primitive-cobalt-*`, `--primitive-teal-*`,
    `--primitive-amber-*` y `--primitive-neutral-*`), elegidos para que el texto blanco o
    `content` cumpla AA sobre cada uno. Exponerlos a Tailwind igual que `data-primary`.
  - Registrarlos en `docs/oica-redesign/DESIGN-SYSTEM.md` (tabla «Semantic colors», grupo Data),
    con el par de contraste validado y la regla de ciclo desde la etapa 7.
- [ ] T018 [P] [US2] En `frontend/src/components/file-detail/types.ts`, añadir `PedidoPiezas`,
  `PiezaPatron`, `RangoBarras`, `PatronExplorable` y la unión `VistaPatrones`, exactamente como
  en contracts/ui.md «Tipos». `PatronResumen` no cambia.
- [ ] T019 [US2] Crear `frontend/src/components/file-detail/patterns/filtros.ts` con funciones
  puras, sin React:
  - `filtrar(patrones, filtro)`: combina con Y diámetro, etapa (`etapas.includes`), origen y
    pedido.
  - `aportePedido(patron, pedido)`: suma de `piezas` de ese pedido en `patron.piezas[].pedidos`.
  - `ordenar(patrones, criterio)`: «excel», «repeticiones», «aprovechamiento» o «saldo»; los tres
    últimos de mayor a menor, con un desempate estable por el índice original (FR-031).
  - `cobertura(filtrados, totales)` → `{n, m, b, t, pct}`, con `b = Σ repeticiones`.
  - `metros(valor)`: coma decimal, sin ceros finales.
- [ ] T020 [US2] Crear `frontend/src/components/file-detail/patterns/PatternRow.tsx` (research
  R-17; contracts/ui.md §5, «Lista de patrones»):
  - `<button aria-expanded aria-controls aria-label>` con el `aria-label` del contrato (más el
    aporte del pedido si hay uno filtrado).
  - Identificador en mono, diámetro y longitud, `×repeticiones` y aprovechamiento.
  - La barra a escala `longitud_m / escala_m`, con `aria-hidden="true"`: piezas por etapa con
    `bg-data-stage-n` (ciclo de 6), una separación de 1 px por corte y tramos de descarte
    (`status/error`) y saldo (`data/remaining-material`).
  - La medida dentro de la pieza solo si su ancho en px (`ResizeObserver` sobre el contenedor)
    supera el del texto.
  - Recomposición en móvil (< 640 px), sin desplazamiento horizontal.
  - Estados hover, active y focus-visible con tokens.
- [ ] T021 [US2] Crear `frontend/src/components/file-detail/patterns/PatternDetail.tsx`
  (contracts/ui.md §5, «Detalle del patrón»; FR-028):
  - La secuencia legible y la lista de piezas: etapa, longitud, cantidad por barra y pedidos con
    sus piezas.
  - Repeticiones, aprovechamiento, pérdida, descarte y saldo.
  - **Barras que lo usan**:
    - el total, siempre visible;
    - `rangos.slice(0, 100 × k)`;
    - un botón «Ver más (quedan K)» que suma 100;
    - nunca se pintan más rangos que los pedidos (SC-012).
  - La nota que remite a las hojas «Patrones» y «Barras».
- [ ] T022 [US2] Crear `frontend/src/components/file-detail/patterns/PatternExplorer.tsx`
  (contracts/ui.md §5; data-model §8.4):
  - Recibe `storageUuid`.
  - Carga diferida con `IntersectionObserver` sobre la sección y `fetch(`${API_URL}/patrones/${storageUuid}`)`
    una vez por versión. Se reinicia al cambiar `storageUuid`.
  - Estados: `inactiva`, `cargando` (esqueleto con `aria-busy`), `lista`, `no_disponible` (con
    `motivo`) y `error` (`Alert` con «Reintentar»).
  - Encabezado y frase del total.
  - Cobertura con `aria-live="polite"`.
  - Filtros con `form-controls`: diámetro, etapa y origen como `select` con «Todos»; pedido como
    `input` + `<datalist>` de `pedidos`, que solo se aplica si el valor existe; «Quitar filtros».
  - Selector de orden.
  - La leyenda (etapas presentes, pérdida, descarte y saldo).
  - La lista por tramos de 50 con «Mostrar más patrones (quedan K)».
  - Un único patrón desplegado a la vez. Al cerrarlo, el foco vuelve a su fila.
  - El mensaje «Ningún patrón cumple los filtros» con «Quitar filtros».
  - Usar `useMemo` para filtrar y ordenar.
- [ ] T023 [US2] En `frontend/src/components/file-detail/FileDetail.tsx`, insertar
  `<PatternExplorer storageUuid={version.storage_uuid} />` entre `PurchaseSummary` y
  `QualitySection` (FR-015). No añadir una vista previa del PNG; la descarga sigue en
  `VersionsTable.tsx`.
- [ ] T024 [US2] Ejecutar las puertas:
  - Las pruebas del backend: T013–T014 deben pasar, junto con todas las existentes salvo las ya
    anotadas en T012.
  - `cd frontend && npm run typecheck && npm run lint && npm run build`.
  - Corregir lo necesario.
- [ ] T025 [US2] Medir SC-009 sin reconstruir imágenes:
  - Crear `scripts/medir_vista_patrones.py` siguiendo el patrón de `scripts/cota_ensayos.py`:
    reutiliza el cargador en memoria `FINDER` de `scripts/check_cutting_container.py`, para
    ejecutar `backend/cutting/vista_patrones.py` del árbol de trabajo dentro del contenedor del
    backend.
  - Para la versión `secuencial-2` real de la 002 en la base local (solo lectura, sin escrituras
    ni `prune`), mide 3 veces:
    - la lectura de `resultados` y `metricas`;
    - `vista(...)`;
    - el total;
    - el tamaño del JSON de la respuesta;
    - el número de patrones, de barras, de rangos y de pedidos.
  - Guardar el resultado en `tests/benchmarks/2026-10-04-sc009-vista-patrones.json`, sin
    sobrescribir.
  - Aceptación: mediana total ≤ 2 s (SC-009) y `totales` = 136 patrones y 13.955 barras. Si no
    se cumple, informarlo al usuario con el desglose antes de seguir.
  - Las versiones `secuencial-2` locales (ids 44–47) tienen `metricas.valido = true`
    (comprobado el 2026-10-04).

**Checkpoint**: el explorador está completo con datos reales del backend, y SC-009 queda medido
(T025). La validación visual, axe, SC-011 y SC-012 en el navegador se hacen en el E2E aprobado
(T047).

---

## Phase 5: User Story 3 - Leer los patrones de corte y sus medidas para el taller (Priority: P3)

**Goal**: el nesting de los archivos muestra las medidas, la leyenda, 200 dpi y la cobertura. El
PDF incluye el nesting por páginas de 18 patrones y dos líneas de cobertura (tabla e imágenes).

**Independent Test**: procesar la 002. La tabla del PDF cubre «136 de 136 patrones, 13.955 de
13.955 barras (100 %)», las imágenes cubren «60 de 136…» y el PNG tiene leyenda y medidas
legibles al 100 % (quickstart §3).

### Tests for User Story 3

- [ ] T026 [US3] En `backend/tests/test_report_presentacion.py`, pruebas del dibujo de nesting:
  - El PNG generado tiene unos 200 dpi (`PIL.Image.info['dpi']`) y ≤ 9 MP (FR-014).
  - El número de bloques del PDF = ⌈min(60, M) / 18⌉.
  - La función de dibujo devuelve las etiquetas de leyenda esperadas: una por etapa presente, más
    «Pérdida por corte», «Descarte» y «Saldo reutilizable».
  - Las piezas rotuladas cumplen la regla de ancho de research R-02 (exponer una función pura
    `cabe_rotulo(ancho_m, texto, pulgadas_por_metro)`).
- [ ] T027 [US3] En `backend/tests/test_report_presentacion.py`:
  - La cobertura de la tabla y de las imágenes coincide con Σ repeticiones de los patrones
    mostrados (SC-003).
  - Con ≤ 150 patrones, la tabla del PDF muestra todos y su cobertura es 100 %.
  - Con > 150, reutilizando el caso de 340 patrones de `test_artefactos_por_patrones_acotados` en
    `backend/tests/test_cutting_api.py`, muestra 150 y el número de omitidos.

### Implementation for User Story 3

- [ ] T028 [US3] En `backend/cutting/report.py`, extraer `dibujar_nesting(problem, patrones_muestra,
  total_patrones, total_barras, titulo)` desde el bloque actual del PNG (líneas ~357-387):
  - Figura de 11 pulgadas de ancho y alto `0,3 × n + 1,2` (research R-04).
  - Piezas con borde fino y medida centrada si `cabe_rotulo(...)`: letra de 5 pt y color por
    contraste de luminancia (research R-02).
  - Leyenda bajo el gráfico, con las etapas presentes y el ciclo de `tab20` indicado si hay más de
    20 (research R-03).
  - Pie con `cobertura(...)`.
  - Título «Nesting lineal por patrones de corte».
  - Devuelve la figura y las etiquetas de la leyenda.
- [ ] T029 [US3] En `generate()` de `backend/cutting/report.py`:
  - Generar el PNG **antes** del PDF con `dibujar_nesting(mas_repetidos(patrones, 60), …)`, a
    200 dpi.
  - Generar en memoria los bloques del PDF (18 patrones cada uno, sobre los mismos 60) como PNG
    base64 (`io.BytesIO`) y pasarlos a `pdf_html(..., imagenes=[...])`.
  - Si el dibujo falla, generar el PDF con «imagen no disponible» (research R-01).
- [ ] T030 [US3] En `pdf_html` de `backend/cutting/report.py`, completar la sección 5 «Patrones de
  corte»:
  - Las dos líneas de cobertura (tabla e imágenes).
  - Las imágenes incrustadas con `<img src="data:image/png;base64,...">`, una por página
    (`page-break-before` o `break-inside: avoid`), al 100 % del ancho útil.
  - La tabla de patrones (≤ 150, los más repetidos), con coma decimal.
  - La nota de omitidos cuando corresponda.
- [ ] T031 [US3] En `backend/tests/test_cutting_api.py`, cambiar la aserción
  `image.width * image.height <= 3_000_000` por `<= 9_000_000` en
  `test_artefactos_visuales_acotados` (línea ~325) y en `test_artefactos_por_patrones_acotados`
  (línea ~355), con un comentario que cite research R-04. El límite sigue siendo fijo e
  independiente del número de barras (BUG-005).
- [ ] T032 [US3] Ejecutar las pruebas. Deben pasar las de T026–T027 y las existentes de patrones.

**Checkpoint**: la US3 se puede verificar con los artefactos de la 002, de forma independiente
del explorador.

---

## Phase 6: User Story 4 - Ver los totales de compra y la calidad del plan en la aplicación web (Priority: P4)

**Goal**: el resumen de compra en pantalla muestra los totales (compra separada del inventario) y
la calidad no tiene la tarjeta de cota simple.

**Independent Test**: en el detalle de una versión de la 001 se ven los totales de compra y la
calidad sin la tarjeta de cota simple. Una versión histórica se abre sin errores (quickstart §6).

### Implementation for User Story 4

- [ ] T033 [P] [US4] En `frontend/src/components/file-detail/PurchaseSummary.tsx`, calcular a
  partir de `lineas` (FR-016; research R-12):
  - una fila de total por diámetro, solo con origen `comercial`;
  - «Total comprado», en barras y kg;
  - «Total tomado del inventario» aparte, si hay líneas `adicional`;
  - en móvil, una tarjeta resumen al final de la lista, sin desplazamiento horizontal.
- [ ] T034 [P] [US4] En `frontend/src/components/file-detail/QualitySection.tsx`, quitar la
  tarjeta «Cota simple» y añadir al texto explicativo «Con aprovechamiento perfecto, el
  desperdicio sería x %» si existe `cota.proyecto.simple_desperdicio_pct` (FR-017).
- [ ] T035 [US4] Ejecutar `cd frontend && npm run typecheck && npm run lint && npm run build`.
  Corregir lo necesario.

**Checkpoint**: la US4 funciona con versiones nuevas e históricas (validación visual en el E2E
aprobado, T047).

---

## Phase 7: User Story 5 - Conservar la trazabilidad técnica y la compatibilidad (Priority: P5)

**Goal**: «Trazabilidad» completa, «Parámetros» legible, Barras sin `stock_id`, `barras_minimas`
renombrada y datos técnicos al final del PDF. El auditor y la reimportación siguen funcionando.

**Independent Test**: regresión de 148 registros con 0 diferencias, auditoría de una versión
nueva y una histórica, y reimportación del inventario (quickstart §2, §5 y §6).

### Tests for User Story 5

- [ ] T036 [US5] En `backend/tests/test_report_presentacion.py`, pruebas:
  - «Trazabilidad» contiene `valido`, `escala_longitudes`, `motor`, `input_hash`, `seed`,
    `perfil`, `metodo`, `duracion_segundos`, `analisis_version` (igual a `analisis-1`),
    `analisis_segundos` (si existe), `cota_ajustada` y `parametros_resueltos`. Este último es un
    JSON que, al volver a leerse, es igual a `problem['resolved_parameters']`.
  - Todo escalar que antes iba a «Metricas» está en «Resumen» o en «Trazabilidad» (data-model §4).
  - «Parámetros» tiene las columnas `condicion, valor, referencia` y las filas de research R-08.
  - «Barras» no tiene `stock_id` y conserva `barra_id, patron_id, diametro, origen, longitud_m,
    piezas_por_barra, perdida_corte_m, descartado_m, sobrante_final_m`.
  - «Cota» tiene `barras_minimas_teoricas_cota_simple` y no `barras_minimas`.
  - La sección 9 del PDF contiene las condiciones legibles, el motor, el método, la semilla y la
    huella.
  - El inventario final conserva exactamente las columnas `diametro, longitud_m, cantidad`
    (FR-022).

### Implementation for User Story 5

- [ ] T037 [US5] En `backend/cutting/report.py`, implementar `trazabilidad_rows(problem, result,
  analisis)` según data-model §4:
  - Incluye `parametros_resueltos` (`json.dumps(..., ensure_ascii=False, sort_keys=True)`).
  - Incluye todo escalar de `result['metrics']` que no aparezca en `resumen_rows`.
  - Escribir la hoja «Trazabilidad» definitiva (`dato | valor`).
- [ ] T038 [US5] En `backend/cutting/report.py`, implementar `parametros_rows(problem)` a partir
  de `problem['resolved_parameters']` y `cutting.parameters.REFERENCES` (research R-08):
  - Escribir la hoja «Parámetros» (con tilde), con las columnas `condicion | valor | referencia`.
  - En la sección 9 de `pdf_html`, usar las mismas filas, más el motor, la versión del análisis,
    el método, la semilla, la huella, las piezas, la masa de barras usadas y la nota «Inventario
    final proyectado; verificar físicamente antes de usar».
- [ ] T039 [US5] En `backend/cutting/report.py`:
  - Quitar `stock_id` de las filas de «Barras» en `generate()`.
  - Renombrar `barras_minimas` a `barras_minimas_teoricas_cota_simple` en `COLUMNAS_COTA` y en
    `cota_rows`.
  - No tocar `legacy_patterns`: sigue escribiendo `stock_id` en `resultados` y R-16 no lo usa.
- [ ] T040 [US5] En `backend/tests/test_cutting_api.py`:
  - Sustituir la lectura de `sheets['Metricas']` (líneas ~291-293) por la de «Resumen» (estado de
    admisibilidad «Dentro de lo admisible») y «Trazabilidad» (`analisis_version ==
    'analisis-1'`).
  - Revisar las demás pruebas que lean hojas o columnas renombradas.
  - La aserción `'analisis-1'` de la línea ~268 no cambia.
- [ ] T041 [US5] Ejecutar las pruebas completas y luego la regresión:
  `python3 scripts/check_cutting_container.py --comparar
  tests/benchmarks/2026-09-13-fisico-matriz-final.jsonl --comparar
  tests/benchmarks/2026-09-13-fisico-control-cizalla.jsonl --comparar
  tests/benchmarks/2026-09-13-fisico-control-fin-etapa.jsonl --output
  tests/benchmarks/2026-10-04-regresion-presentacion.jsonl`. Esperado: 148 registros y
  0 diferencias (FR-021, SC-004).

**Checkpoint**: todas las historias funcionan; la trazabilidad y la compatibilidad están
comprobadas.

---

## Phase 8: Polish & cross-cutting

- [ ] T042 Medir SC-007 después de los cambios, con el mismo procedimiento de T002:
  - Guardar `tests/benchmarks/2026-10-04-sc007-presentacion-despues.jsonl` y un resumen
    comparativo `tests/benchmarks/2026-10-04-sc007-presentacion-comparacion.json` (medianas y
    ratio).
  - Aceptación: ratio de medianas ≤ 1,10. Si se supera, informarlo al usuario con el desglose
    (motor, análisis y artefactos) antes de seguir.
  - La ruta de patrones no corre durante el procesamiento, así que no afecta a SC-007.
- [ ] T043 Revisar a mano los artefactos de la 001 y la 002:
  - Ejecutar `--artifacts-smoke`, copiar los artefactos a una carpeta temporal fuera del
    repositorio y revisarlos según quickstart §3 (hojas, totales, cobertura, páginas de nesting,
    medidas legibles y coma decimal).
  - Anotar el resultado en una sección nueva de `tests/data/002/ANALISIS_RESULTADOS.md`,
    «§13 Presentación (spec 002)».
  - No versionar los artefactos.
- [ ] T044 [P] En `specs/001-alineacion-titulo-tesis/contracts/artefactos.md` y
  `specs/001-alineacion-titulo-tesis/contracts/ui.md`, añadir al inicio la nota «Sustituido en
  parte por `specs/002-presentacion-resultados/contracts/` (2026-10-04)».
- [ ] T045 [P] Actualizar `CLAUDE.md`:
  - La tabla «Cobertura de evidencia vigente» suma las evidencias nuevas de T025, T041 y T042.
  - Mencionar en «Qué es este proyecto» la ruta de solo lectura `GET /patrones/<uuid>` del
    explorador.
  - El análisis sigue en `analisis-1`: no cambiar esas menciones.
  - Revisar si `AGENTS.md` y `backend/AGENTS.md` necesitan el mismo ajuste (contrato de la API).
- [ ] T046 [P] Actualizar `docs/oica-redesign/STATE.md` y `docs/oica-redesign/COMPONENT-MAP.md`:
  - el explorador de patrones como componente nuevo;
  - los tokens `data/stage-*`;
  - la regla de diseño 13. Figma queda pendiente si la cuota del MCP sigue bloqueada; declararlo.
- [ ] T047 Pedir aprobación al usuario para reconstruir las imágenes: estimar el espacio con
  `docker system df` y el libre en C:, y nunca usar `prune`. Con la aprobación, ejecutar el E2E de
  quickstart §6 y §7:
  - Subir la 001 con y sin umbral.
  - Revisar en el detalle el explorador, los totales y la calidad.
  - Medir con `curl` el tiempo de `GET /api/patrones/<uuid>` de la versión de la 002 (SC-009) y
    comparar con su Excel (SC-010).
  - Teclado y lector de pantalla en el explorador (SC-011), con la respuesta inmediata de filtros
    y «Ver más» (SC-012).
  - Descargar los cuatro artefactos y reimportar el inventario.
  - Abrir versiones históricas: una `secuencial-2` previa (por ejemplo, la versión local de la
    002) muestra sus patrones; una `secuencial-1` o del motor histórico muestra «no disponible»
    con su motivo.
  - Auditar una versión nueva y una histórica con `scripts/verify_sequential_result.py`
    (SC-005).
  - Pasar axe en 1440, 820 y 390 px, con la sección abierta y un detalle desplegado (SC-006,
    SC-011).
  - **Confidencialidad** (supuesto de la spec; constitución, Principio V): antes de capturas,
    QA visual o demostraciones, comprobar que los pedidos («N° Orden») y el nombre de archivo de
    las versiones mostradas no identifican la obra de las cartillas 001 y 002. Si la identifican,
    usar una copia anonimizada y no versionar capturas con datos identificables (quickstart §7,
    punto 7).

  Sin aprobación, dejar la tarea pendiente y declararlo.
- [ ] T048 Actualizar `.claude/context/CURRENT_STATE.md` y `PLAN_TRABAJO.md` (nuevo Bloque L,
  spec 002 enmendada, con el estado real de cada puerta):
  - Si alguna decisión lo amerita, registrarla en `INFERENCIAS_TESIS.md`, tras comprobar que no
    haya duplicados.
  - Sin commits ni push sin una instrucción explícita para esa ocasión.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (fase 1)**: sin dependencias. T002 **debe** ejecutarse antes de cualquier cambio de
  código.
- **Foundational (fase 2)**: depende de la fase 1 y bloquea todas las historias.
- **US1 (fase 3)**: depende de la fase 2. Es el MVP.
- **US2 (fase 4)**:
  - Backend (T013–T016): solo depende de la fase 2 (T004 da el plan pequeño). **No** depende de
    US1: `vista_patrones` reutiliza `patrones_rows`, que no cambia.
  - Frontend (T017–T023): solo depende de los contratos.
  - T024 y T025 cierran la historia (T025 necesita T015 y la base local en marcha).
- **US3 (fase 5)**: depende de la fase 2 y de T011 (estructura de `pdf_html`), porque comparte
  `report.py`.
- **US4 (fase 6)**: independiente del backend. Comparte `FileDetail.tsx` con la US2 solo en
  lectura: T033 y T034 tocan archivos distintos.
- **US5 (fase 7)**: depende de T010 y T011 (hojas y PDF reestructurados).
- **Polish (fase 8)**: depende de todas las historias.

### Within Each User Story

- Las pruebas se escriben primero y deben fallar; luego se implementa.
- En `report.py`: primero los ayudantes y las filas (`*_rows`), luego la escritura en
  `generate()` y luego el PDF.
- En el explorador: primero el módulo puro y la ruta, luego los tipos y `filtros.ts`, luego las
  filas y el detalle, y al final el contenedor y su montaje.

### Parallel Opportunities

- T013 (pruebas de `vista_patrones`, archivo nuevo) en paralelo con T006–T011 de la US1.
- T017 (tokens) y T018 (tipos) en paralelo con cualquier tarea del backend.
- Todo el frontend de la US2 (T017–T023) en paralelo con las fases 5 y 7, que son del backend.
- T033 y T034 de la US4 en paralelo entre sí y con la US2.
- T044, T045 y T046 (documentación) en paralelo entre sí.
- Casi todas las tareas de `report.py` van en serie, porque comparten archivo.

## Parallel Example: User Story 2

```text
# Mientras otra persona trabaja la US1/US3 en backend/cutting/report.py:
Task: "T013 [P] [US2] Pruebas de vista_patrones en backend/tests/test_vista_patrones.py"
Task: "T017 [P] [US2] Tokens data-stage en frontend/src/app/globals.css y DESIGN-SYSTEM.md"
Task: "T018 [P] [US2] Tipos del explorador en frontend/src/components/file-detail/types.ts"
# Luego, en serie: T015 → T016 → T025 (backend) y T019 → T020 → T021 → T022 → T023 (frontend)
```

## Implementation Strategy

### MVP first (solo US1)

1. Fases 1 y 2 (incluida la línea base de tiempo T002).
2. Fase 3 (US1): el Excel con «Resumen» y totales, y el PDF con la compra al inicio.
3. **Parar y validar** con los artefactos de la 001.

### Incremental delivery

1. US1: compra e indicadores primero (Excel y PDF).
2. US2: explorador de patrones en la web, con datos reales de las versiones ya procesadas.
3. US3: nesting legible y cobertura (PNG y PDF).
4. US4: totales y calidad en la web.
5. US5: trazabilidad, parámetros legibles y regresión.
6. Polish: SC-007, revisión manual, documentación y E2E con aprobación.

## Notes

- No se tocan `optimizer.py`, `physical.py`, `parameters.py`, ni `normalize` y `validate` de
  `domain.py` (constitución, Principio III).
- Tampoco `analysis.py` ni `test_analisis.py`: se retira `analisis-2` (research R-10).
- No se regeneran artefactos de versiones históricas. La ruta de patrones es de solo lectura.
- La evidencia nueva se guarda con fecha en `tests/benchmarks/` y nunca sobrescribe.
- Sin commits, push ni despliegues sin una instrucción explícita del usuario para esa ocasión.
