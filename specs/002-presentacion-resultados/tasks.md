---

description: "Tareas de la spec 002: presentación de resultados para el usuario"
---

# Tasks: Presentación de resultados para el usuario

**Input**: Documentos de diseño en `specs/002-presentacion-resultados/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md)

**Tests**: SÍ. La constitución exige pruebas automatizadas de las invariantes de los artefactos.
Las pruebas de cada historia se escriben antes de su implementación y deben fallar primero.

**Organization**: tareas agrupadas por historia de usuario. Muchas tocan
`backend/cutting/report.py` y `backend/tests/test_report_presentacion.py`, así que solo se marcan
[P] las que van en archivos distintos sin dependencias pendientes.

**Ejecución de pruebas** (en todo el documento): `python3 scripts/check_cutting_container.py
--all-tests --container oica-validation-backend-1`. El arnés carga el código del árbol de trabajo
en memoria, sin reconstruir imágenes.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: se puede ejecutar en paralelo (archivos distintos, sin dependencias pendientes).
- **[Story]**: historia a la que pertenece (US1–US4).

---

## Phase 1: Setup (preparación y línea base)

**Purpose**: leer las reglas obligatorias y medir la línea base de tiempo **antes** de cambiar
código.

- [ ] T001 Leer `tests/data/002/ANALISIS_RESULTADOS.md` §12 (obligatorio antes de tocar `backend/cutting/report.py` y `backend/celery_worker.py`), y `docs/oica-redesign/AI-DESIGN-RULES.md` y `docs/oica-redesign/STATE.md` (obligatorio antes de tocar la UI). Anotar en las notas de la tarea las reglas de UI que apliquen a tablas, tarjetas, imágenes y avisos.
- [ ] T002 Medir la línea base de SC-007 con el código actual: 5 ejecuciones de `python3 scripts/check_cutting_container.py --artifacts-smoke --dataset tests/data/002/002-ingeBigTest.xlsx --profiles balanceado --seeds 1 --container oica-validation-backend-1` con las condiciones físicas por defecto (como en `tests/benchmarks/2026-10-02-sc007-comparacion.json`). Guardar los totales, el motor, el análisis y los artefactos en `tests/benchmarks/2026-10-03-sc007-presentacion-antes.jsonl`, sin sobrescribir. Si el arnés no admite repeticiones, ejecutarlo 5 veces con salidas numeradas.

---

## Phase 2: Foundational (bloquea todas las historias)

**Purpose**: ayudantes de formato y cobertura, y número de versión disponible para el PDF.

- [ ] T003 En `backend/cutting/report.py`, añadir los ayudantes:
  - `numero(valor, decimales=2)`: punto de miles y coma decimal (por ejemplo `152.039,57`); `None` → «no disponible»; sin `locale` (research R-05).
  - `PERFILES = {'rapido': 'Rápido', 'balanceado': 'Balanceado', 'profundo': 'Profundo'}`.
  - `cobertura(mostrados, total_patrones, total_barras)`: devuelve `(n, m, b, t, pct)`, con `b = Σ repeticiones de los mostrados`, y el texto «Se muestran N de M patrones, que cubren B de T barras (x %)» (data-model §6; invariante «`b ≤ t`; si `n = m`, entonces `b = t`»).
- [ ] T004 Crear `backend/tests/test_report_presentacion.py` con un plan pequeño de prueba (dos diámetros, dos etapas, inventario adicional opcional), siguiendo el estilo de `backend/tests/test_cutting_api.py` (`normalize` → `optimize` → `analizar` → `generate` en un `TemporaryDirectory`). Pruebas iniciales de `numero()` y `cobertura()`, incluidos `n = m ⇒ b = t` y `b ≤ t`.
- [ ] T005 En `backend/cutting/report.py`, ampliar la firma a `generate(problem, result, directory, title='', visuals=True, version=None)`, compatible con el arnés `--artifacts-smoke` y las pruebas existentes. En `backend/celery_worker.py`, mover el cálculo de `version` (consulta `latest`, líneas ~271-273) **antes** de la llamada a `generate(...)` (línea ~260), pasar `version=version` y reutilizar el mismo valor al crear `ProcessingResult` (research R-09). No cambiar ninguna otra lógica del worker.

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
  - «Resumen» con los 21 indicadores de contracts/artefactos.md §1.1, en orden, con su `unidad`.
  - El bloque «Totales de compra», localizado por su título: «Total comprado» + «Total tomado del inventario» = filas de Barras, y la masa = Σ `Resumen de compra.masa_kg` (data-model §3).
  - «Resumen de compra» sin filas de total.
- [ ] T007 [US1] En `backend/tests/test_report_presentacion.py`, pruebas del PDF (extraer el texto con `pypdf` si está en la imagen; si no, comprobar el HTML generado mediante una función pura `pdf_html(...)` expuesta por `report.py`):
  - El encabezado contiene el proyecto, la versión, el perfil legible y «hora de Colombia».
  - El orden: verificación → indicadores clave → resumen de compra con totales.
  - Las cifras del usuario usan coma decimal (por ejemplo, el desperdicio con dos decimales).

### Implementation for User Story 1

- [ ] T008 [US1] En `backend/cutting/report.py`, implementar `resumen_rows(problem, result, analisis)`: 21 filas `{indicador, valor, unidad}` en el orden y con los orígenes de contracts/artefactos.md §1.1. Un dato faltante se muestra como «no disponible» o «sin evaluar» (data-model §2: «nunca una celda vacía ambigua»). Los valores numéricos siguen siendo números.
- [ ] T009 [US1] En `backend/cutting/report.py`, implementar `totales_compra_rows(analisis)` a partir de `analisis['resumen_compra']`: una fila por diámetro y origen (`Compra` o `Inventario adicional`), «Total comprado» y, si hay inventario, «Total tomado del inventario» (data-model §3). Si falta `resumen_compra`, una fila «no disponible».
- [ ] T010 [US1] En `generate()` de `backend/cutting/report.py`, escribir la hoja «Resumen» con dos bloques: indicadores desde la fila 1; una fila en blanco; la celda de título «Totales de compra»; y la tabla de totales (`startrow` de pandas más una celda de título con openpyxl). Reordenar todas las hojas según contracts/artefactos.md §1 y dejar de escribir «Metricas». Los escalares técnicos se escriben provisionalmente en una hoja «Trazabilidad» mínima; su contenido final se completa en T026.
- [ ] T011 [US1] En `backend/cutting/report.py`, reestructurar el HTML del PDF en una función pura `pdf_html(problem, result, analisis, patrones, title, version, imagenes)`, con las secciones de contracts/artefactos.md §2 en orden:
  1. Encabezado (proyecto escapado, versión o «no asignada», perfil con `PERFILES` y fecha con `datetime.now(timezone(timedelta(hours=-5)))` rotulada «hora de Colombia»).
  2. Verificación.
  3. Indicadores clave.
  4. Resumen de compra con filas de total por diámetro y total general (reutilizar `totales_compra_rows`).

  Las secciones 5–9 reutilizan por ahora `patrones_html`, `admisibilidad_html`, `cota_html` y `avisos_html` (se completan en US2 y US4). Aplicar `numero()` a todas las cifras visibles, con 3 decimales en la cota y la brecha (FR-011).
- [ ] T012 [US1] Ejecutar las pruebas. Las de T006–T007 deben pasar, y también todas las existentes salvo las que dependan de «Metricas» o de `stock_id`, que se actualizan en US4 (anotarlas). Corregir lo necesario.

**Checkpoint**: la US1 se puede demostrar con el Excel y el PDF de la 001 (MVP).

---

## Phase 4: User Story 2 - Leer los patrones de corte y sus medidas para el taller (Priority: P2)

**Goal**: el nesting muestra las medidas, la leyenda, 200 dpi y la cobertura. El PDF incluye el
nesting por páginas de 18 patrones y dos líneas de cobertura (tabla e imágenes).

**Independent Test**: procesar la 002. La tabla del PDF cubre «136 de 136 patrones, 13.955 de
13.955 barras (100 %)», las imágenes cubren «60 de 136…» y el PNG tiene leyenda y medidas
legibles al 100 % (quickstart §3).

### Tests for User Story 2

- [ ] T013 [US2] En `backend/tests/test_report_presentacion.py`, pruebas del dibujo de nesting:
  - El PNG generado tiene unos 200 dpi (`PIL.Image.info['dpi']`) y ≤ 9 MP (FR-014).
  - El número de bloques del PDF = ⌈min(60, M) / 18⌉.
  - La función de dibujo devuelve las etiquetas de leyenda esperadas (una por etapa presente, más «Pérdida por corte», «Descarte» y «Saldo reutilizable»).
  - Las piezas rotuladas cumplen la regla de ancho de research R-02 (exponer una función pura `cabe_rotulo(ancho_m, texto, pulgadas_por_metro)`).
- [ ] T014 [US2] En `backend/tests/test_report_presentacion.py`:
  - La cobertura de la tabla y de las imágenes coincide con Σ repeticiones de los patrones mostrados (SC-003).
  - Con ≤ 150 patrones, la tabla del PDF muestra todos y su cobertura es 100 %.
  - Con > 150 (reutilizar el caso de 340 patrones de `test_artefactos_por_patrones_acotados` en `backend/tests/test_cutting_api.py`), muestra 150 y el número de omitidos.

### Implementation for User Story 2

- [ ] T015 [US2] En `backend/cutting/report.py`, extraer `dibujar_nesting(problem, patrones_muestra, total_patrones, total_barras, titulo)` desde el bloque actual del PNG (líneas ~357-387):
  - Figura de 11 pulgadas de ancho y alto `0,3 × n + 1,2` (research R-04).
  - Piezas con borde fino y medida centrada si `cabe_rotulo(...)` (letra de 5 pt, color por contraste de luminancia; research R-02).
  - Leyenda bajo el gráfico, con etapas presentes y ciclo de `tab20` indicado si hay más de 20 (research R-03).
  - Pie con `cobertura(...)`.
  - Título «Nesting lineal por patrones de corte».
  - Devuelve la figura y las etiquetas de la leyenda.
- [ ] T016 [US2] En `generate()` de `backend/cutting/report.py`:
  - Generar el PNG **antes** del PDF con `dibujar_nesting(mas_repetidos(patrones, 60), …)`, a 200 dpi.
  - Generar en memoria los bloques del PDF (18 patrones cada uno, sobre los mismos 60) como PNG base64 (`io.BytesIO`), y pasarlos a `pdf_html(..., imagenes=[...])`.
  - Si el dibujo falla, el PDF se genera con «imagen no disponible» (research R-01).
- [ ] T017 [US2] En `pdf_html` de `backend/cutting/report.py`, completar la sección 5 «Patrones de corte»:
  - Las dos líneas de cobertura (tabla e imágenes).
  - Las imágenes incrustadas con `<img src="data:image/png;base64,...">`, una por página (`page-break-before` o `break-inside: avoid`, ancho 100 % del área útil).
  - La tabla de patrones (≤ 150, los más repetidos) con coma decimal.
  - La nota de omitidos cuando corresponda.
- [ ] T018 [US2] En `backend/tests/test_cutting_api.py`, cambiar en `test_artefactos_visuales_acotados` la aserción `image.width * image.height <= 3_000_000` por `<= 9_000_000`, con un comentario que cite research R-04 (el límite sigue siendo fijo e independiente del número de barras, BUG-005).
- [ ] T019 [US2] Ejecutar las pruebas. Las de T013–T014 y las existentes de patrones deben pasar.

**Checkpoint**: la US2 se puede verificar con los artefactos de la 002, de forma independiente de la US3.

---

## Phase 5: User Story 3 - Ver patrones y totales de compra en la aplicación web (Priority: P3)

**Goal**: sección «Patrones de corte» con secuencia y vista previa, totales de compra en
pantalla y sin la tarjeta de cota simple. El análisis pasa a `analisis-2`.

**Independent Test**: en el detalle de una versión nueva de la 001 se ven la sección de patrones
(tabla y vista previa), los totales de compra y la calidad sin cota simple. Una versión histórica
se abre sin errores (quickstart §6).

### Tests for User Story 3

- [ ] T020 [US3] En `backend/tests/test_analisis.py`, cambiar la aserción `analisis['version'] == 'analisis-1'` (línea ~32) por `'analisis-2'` y añadir una prueba: cada elemento de `analisis['patrones']['top']` tiene `secuencia` igual a `patterns.secuencia_legible(problem, patron)` del patrón correspondiente. En `backend/tests/test_cutting_api.py`, cambiar `'analisis-1'` por `'analisis-2'` en la línea ~268.

### Implementation for User Story 3

- [ ] T021 [US3] En `backend/cutting/analysis.py`, poner `VERSION_ANALISIS = 'analisis-2'` y, en `resumen_patrones`, añadir `'secuencia': secuencia_legible(problem, p)` (importado de `.patterns`) a cada patrón del `top`. Ningún otro cálculo cambia (research R-10; data-model §1).
- [ ] T022 [P] [US3] En `frontend/src/components/file-detail/types.ts`:
  - Añadir `secuencia?: string` a `PatronResumen`.
  - Definir `ResumenPatrones { total: number; barras: number; max_repeticiones: number; top: PatronResumen[] }`.
  - Asegurar `patrones?: ResumenPatrones` en el tipo del análisis.

  Todo opcional (contracts/ui.md, sección Tipos).
- [ ] T023 [US3] Crear `frontend/src/components/file-detail/PatternsSection.tsx` según contracts/ui.md §5:
  - Título, frase de total, tabla de los 10 más repetidos y tarjetas en móvil, siguiendo el patrón de `PurchaseSummary.tsx` y las reglas anotadas en T001.
  - `secuencia` ausente → «no disponible».
  - Vista previa `<img src={`${API_URL}/descargar-imagen/${storage_uuid}`} loading="lazy">`, con texto alternativo y `onError` → aviso «Imagen no disponible para esta versión».
  - Nota que remite a la hoja «Patrones» del Excel.
  - Sin `analisis.patrones` → «Patrones: no disponible (versión procesada antes de este análisis)».
- [ ] T024 [US3] Actualizar las secciones del detalle:
  - `frontend/src/components/file-detail/FileDetail.tsx`: insertar `<PatternsSection …/>` entre `PurchaseSummary` y `QualitySection`, pasando `version.analisis?.patrones`, `version.storage_uuid` y la disponibilidad de la imagen (`graph_image_path || image_path`).
  - `frontend/src/components/file-detail/PurchaseSummary.tsx`: totales por diámetro y «Total comprado» (solo comercial), y «Total tomado del inventario» aparte, también en la vista móvil (FR-016; research R-12).
  - `frontend/src/components/file-detail/QualitySection.tsx`: quitar la tarjeta «Cota simple» y añadir al texto explicativo «Con aprovechamiento perfecto, el desperdicio sería x %» si existe el dato (FR-017).
- [ ] T025 [US3] Ejecutar `cd frontend && npm run typecheck && npm run lint && npm run build`, y las pruebas del backend. Corregir lo necesario.

**Checkpoint**: la US3 funciona con las versiones nuevas e históricas (validación visual en la fase final, tras el E2E aprobado).

---

## Phase 6: User Story 4 - Conservar la trazabilidad técnica y la compatibilidad (Priority: P4)

**Goal**: «Trazabilidad» completa, «Parámetros» legible, Barras sin `stock_id`, `barras_minimas`
renombrada, datos técnicos al final del PDF; el auditor y la reimportación siguen funcionando.

**Independent Test**: regresión de 148 registros con 0 diferencias, auditoría de una versión
nueva y una histórica, y reimportación del inventario (quickstart §2, §5 y §6).

### Tests for User Story 4

- [ ] T026 [US4] En `backend/tests/test_report_presentacion.py`, pruebas:
  - «Trazabilidad» contiene `valido`, `escala_longitudes`, `motor`, `input_hash`, `seed`, `perfil`, `metodo`, `duracion_segundos`, `analisis_version`, `analisis_segundos` (si existe), `cota_ajustada` y `parametros_resueltos` (JSON que se vuelve a leer igual a `problem['resolved_parameters']`).
  - Todo escalar que antes iba a «Metricas» está en «Resumen» o en «Trazabilidad» (data-model §4).
  - «Parámetros» tiene las columnas `condicion, valor, referencia` y las filas de research R-08.
  - «Barras» no tiene `stock_id` y conserva `barra_id, patron_id, diametro, origen, longitud_m, piezas_por_barra, perdida_corte_m, descartado_m, sobrante_final_m`.
  - «Cota» tiene `barras_minimas_teoricas_cota_simple` y no `barras_minimas`.
  - La sección 9 del PDF contiene las condiciones legibles, el motor, el método, la semilla y la huella.
  - El inventario final conserva exactamente las columnas `diametro, longitud_m, cantidad` (FR-022).

### Implementation for User Story 4

- [ ] T027 [US4] En `backend/cutting/report.py`, implementar `trazabilidad_rows(problem, result, analisis)` según data-model §4, incluidos `parametros_resueltos` (`json.dumps(..., ensure_ascii=False, sort_keys=True)`) y todo escalar de `result['metrics']` que no aparezca en `resumen_rows`. Escribir la hoja «Trazabilidad» definitiva (`dato | valor`).
- [ ] T028 [US4] En `backend/cutting/report.py`, implementar `parametros_rows(problem)`, a partir de `problem['resolved_parameters']` y `cutting.parameters.REFERENCES` (research R-08), y escribir la hoja «Parámetros» (con tilde) con `condicion | valor | referencia`. En la sección 9 de `pdf_html`, usar las mismas filas, más el motor, la versión del análisis, el método, la semilla, la huella, las piezas, la masa de barras usadas y la nota «Inventario final proyectado; verificar físicamente antes de usar».
- [ ] T029 [US4] En `backend/cutting/report.py`, quitar `stock_id` de las filas de «Barras» en `generate()`. Renombrar `barras_minimas` a `barras_minimas_teoricas_cota_simple` en `COLUMNAS_COTA` y en `cota_rows`.
- [ ] T030 [US4] En `backend/tests/test_cutting_api.py`, sustituir la lectura de `sheets['Metricas']` (líneas ~291-293) por la de «Resumen» (estado de admisibilidad «Dentro de lo admisible») y «Trazabilidad» (`analisis_version == 'analisis-2'`). Revisar las demás pruebas que lean hojas o columnas renombradas.
- [ ] T031 [US4] Ejecutar las pruebas completas y luego la regresión: `python3 scripts/check_cutting_container.py --comparar tests/benchmarks/2026-09-13-fisico-matriz-final.jsonl --comparar tests/benchmarks/2026-09-13-fisico-control-cizalla.jsonl --comparar tests/benchmarks/2026-09-13-fisico-control-fin-etapa.jsonl --output tests/benchmarks/2026-10-03-regresion-presentacion.jsonl`. Esperado: 148 registros y 0 diferencias (FR-021, SC-004).

**Checkpoint**: todas las historias funcionan; la trazabilidad y la compatibilidad están comprobadas.

---

## Phase 7: Polish & cross-cutting

- [ ] T032 Medir SC-007 después de los cambios con el mismo procedimiento de T002 y guardar `tests/benchmarks/2026-10-03-sc007-presentacion-despues.jsonl` y un resumen comparativo `tests/benchmarks/2026-10-03-sc007-presentacion-comparacion.json` (medianas y ratio). Aceptación: ratio de medianas ≤ 1,10. Si se supera, informarlo al usuario con el desglose (motor, análisis, artefactos) antes de seguir.
- [ ] T033 Ejecutar `--artifacts-smoke` sobre la 001 y la 002, copiar los artefactos a una carpeta temporal fuera del repositorio y revisarlos a mano según quickstart §3 (hojas, totales, cobertura, páginas de nesting, medidas legibles, coma decimal). Anotar el resultado en `tests/data/002/ANALISIS_RESULTADOS.md` en una sección nueva «§13 Presentación (spec 002)». No versionar artefactos.
- [ ] T034 [P] En `specs/001-alineacion-titulo-tesis/contracts/artefactos.md` y `specs/001-alineacion-titulo-tesis/contracts/ui.md`, añadir al inicio una nota: «Sustituido en parte por `specs/002-presentacion-resultados/contracts/` (2026-10-03)».
- [ ] T035 [P] Actualizar `CLAUDE.md`: las menciones a `analisis-1` pasan a `analisis-2` donde describan el estado vigente, y la tabla «Cobertura de evidencia vigente» suma las evidencias nuevas de T031–T032. Revisar si `AGENTS.md` necesita el mismo ajuste.
- [ ] T036 Pedir aprobación al usuario para reconstruir las imágenes (estimar el espacio con `docker system df` y el libre en C:; nunca `prune`). Con aprobación, ejecutar el E2E de quickstart §6:
  - Subir la 001 con y sin umbral.
  - Revisar el detalle: patrones, totales y calidad.
  - Descargar los cuatro artefactos y reimportar el inventario.
  - Abrir una versión histórica.
  - Auditar una versión nueva y una histórica con `scripts/verify_sequential_result.py` (SC-005).
  - Pasar axe en 1440, 820 y 390 px (SC-006).

  Sin aprobación, dejar la tarea pendiente y declararlo.
- [ ] T037 Actualizar `.claude/context/CURRENT_STATE.md` y `PLAN_TRABAJO.md` (nuevo Bloque L, spec 002, con el estado real de cada puerta). Si alguna decisión lo amerita, registrarla en `INFERENCIAS_TESIS.md` tras comprobar que no haya duplicados. Sin commits ni push sin una instrucción explícita para esa ocasión.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (fase 1)**: sin dependencias. T002 **debe** ejecutarse antes de cualquier cambio de código.
- **Foundational (fase 2)**: depende de la fase 1 y bloquea todas las historias.
- **US1 (fase 3)**: depende de la fase 2. Es el MVP.
- **US2 (fase 4)**: depende de la fase 2 y de T011 (estructura `pdf_html`), porque comparte `report.py`.
- **US3 (fase 5)**: el backend (T020–T021) solo depende de la fase 2. El frontend (T022–T025) es independiente del backend de US1, US2 y US4.
- **US4 (fase 6)**: depende de T010 y T011 (hojas y PDF reestructurados).
- **Polish (fase 7)**: depende de todas las historias.

### Within Each User Story

- Las pruebas se escriben primero y deben fallar; luego se implementa.
- En `report.py`: primero los ayudantes y las filas (`*_rows`), luego la escritura en `generate()` y luego el PDF.

### Parallel Opportunities

- T022 (tipos del frontend) se puede hacer en paralelo con cualquier tarea del backend.
- La fase 5 completa del frontend (T022–T024) puede avanzar en paralelo con las fases 4 y 6, que son del backend.
- T034 y T035 (documentación) se pueden hacer en paralelo entre sí.
- Casi todas las tareas del backend comparten `report.py` o `test_report_presentacion.py` y van en serie.

## Parallel Example: User Story 3

```text
# Mientras otra persona trabaja US2/US4 en backend/cutting/report.py:
Task: "T022 [P] [US3] Tipos opcionales en frontend/src/components/file-detail/types.ts"
Task: "T023 [US3] PatternsSection.tsx" (tras T022)
Task: "T024 [US3] FileDetail/PurchaseSummary/QualitySection" (tras T023)
```

## Implementation Strategy

### MVP first (solo US1)

1. Fases 1 y 2 (incluida la línea base de tiempo T002).
2. Fase 3 (US1): el Excel con «Resumen» y totales, y el PDF con la compra al inicio.
3. **Parar y validar** con los artefactos de la 001.

### Incremental delivery

1. US1: compra e indicadores primero (Excel y PDF).
2. US2: nesting legible y cobertura (PNG y PDF).
3. US3: patrones y totales en la web (`analisis-2`).
4. US4: trazabilidad, parámetros legibles y regresión.
5. Polish: SC-007, revisión manual, documentación y E2E con aprobación.

## Notes

- No se tocan `optimizer.py`, `physical.py`, `parameters.py`, ni `normalize` y `validate` de `domain.py` (constitución, Principio III).
- No se regeneran artefactos de versiones históricas.
- La evidencia nueva se guarda con fecha en `tests/benchmarks/` y nunca sobrescribe.
- Sin commits, push ni despliegues sin una instrucción explícita del usuario para esa ocasión.
