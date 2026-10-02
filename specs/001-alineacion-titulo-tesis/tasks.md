---

description: "Lista de tareas de la feature 001 — alineación de OICA con el título fijo"
---

# Tasks: Alineación de OICA con el título fijo de la tesis

**Input**: documentos de diseño en `/specs/001-alineacion-titulo-tesis/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md)

**Tests**: se incluyen porque son obligatorios. La constitución v1.0.0 (Flujo de trabajo) exige
pruebas automatizadas en todo cambio de dominio, métricas o artefactos, y una puerta de
regresión. La UI se verifica con typecheck, lint, build y axe.

**Organization**: tareas agrupadas por historia de usuario (US1–US6 de la spec).

## Reglas que aplican a todas las tareas

- **Archivos intocables** (Principio III): `backend/cutting/optimizer.py`,
  `backend/cutting/physical.py`, `backend/cutting/parameters.py`, y `normalize()` y `validate()`
  en `backend/cutting/domain.py`. Tampoco se toca `services/`.
- **Idioma**: código, comentarios, interfaz y textos en español. El frontend usa tres espacios
  de indentación, y las directivas `'use client'` van antes de los imports.
- **Antes de tocar `report.py` o `celery_worker.py`**: leer
  `tests/data/002/ANALISIS_RESULTADOS.md`.
- **Antes de tocar UI**: leer `docs/oica-redesign/AI-DESIGN-RULES.md`.
- **Pruebas backend**: `python3 scripts/check_cutting_container.py --all-tests --container
  oica-validation-backend-1`, con el código en memoria. Usar el contenedor del **backend**: el del
  worker no tiene `gevent` y la importación de `server` falla allí (verificado 2026-10-02). O
  `cd backend && python -m unittest discover -s tests -p 'test_*.py'` en la imagen.
- **Prohibido**: commits, push y despliegues. Tampoco se reconstruyen imágenes sin aprobación
  del usuario.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: se puede hacer en paralelo (otro archivo y sin dependencias pendientes).
- **[Story]**: US1–US6.

---

## Phase 1: Setup (infraestructura compartida)

**Purpose**: preparar los módulos y los datos de prueba. Sin scipy todavía.

- [X] T001 Crear `backend/tests/test_analisis.py` con `unittest`. Incluir un helper
  `row(order, length, quantity=1, group=1, diam='#3', mass_per_m=None)` (copiar el patrón de
  `backend/tests/test_sequential.py:9`, de modo que `Masa total (kg)` sea
  `length·quantity·(mass_per_m or 1)`) y un helper `plan(rows, catalog=None, options=None,
  seed=0)` que llame a `normalize` y `optimize` y devuelva `(problem, result)`.
- [X] T002 [P] Ejecutar la regresión de referencia **antes** de cualquier cambio: correr
  `python3 scripts/check_cutting_container.py --all-tests` y anotar en
  `.claude/context/CURRENT_STATE.md` que la línea base de pruebas pasa (número de pruebas y
  fecha).
  Medir también la línea base de SC-007 con el código actual:
  `python3 scripts/check_cutting_container.py --artifacts-smoke --dataset
  tests/data/002/002-ingeBigTest.xlsx --profiles balanceado --seeds 1 --output
  tests/benchmarks/<fecha>-base-sc007.jsonl`. Guardar
  `duracion_segundos + artefactos_y_verificacion_segundos` en `CURRENT_STATE.md`. Los
  artefactos son temporales (≈1,6 MB); comprobar antes el espacio libre.
- [X] T003 [P] Verificar las fuentes que la app cita (Principio V). No bloquea a las demás
  tareas: mientras no termine, la app usa los rótulos «por verificar» de
  [contracts/ui.md](contracts/ui.md).
  1. Tabla de masas de barras corrugadas de la NSR-10 (Decreto 926 de 2010, Título C):
     número de tabla, página y valores, comparados con `MASA_NOMINAL_KG_M` (research R-08).
  2. INVIAS, Especificaciones Generales, art. 640, y la especificación de acero de refuerzo del
     IDU: confirmar si fijan o no un porcentaje de desperdicio y cómo se paga el acero.

  Registrar el resultado en fichas de `docs/tesis-doc/Referencias.md`, con los ocho campos de
  FR-021. Si no hay acceso a la fuente, dejar el estado «verificar…» o «pendiente de localizar»
  y pedir el documento al usuario; no marcarla verificada por inferencia. Si la tabla queda
  verificada, cambiar el rótulo «masa de referencia (NSR-10, por verificar)» por «masa nominal
  NSR-10 (Título C, tabla X)» en `backend/cutting/nominal.py`, `backend/cutting/report.py`,
  `frontend/src/components/file-detail/MassWarnings.tsx` y los contracts. Si quedan verificadas
  INVIAS e IDU, la ayuda del umbral puede nombrarlas como normas consultadas.
  **Resultado (2026-10-02)**: la NSR-10 quedó verificada (Tabla C.3.5.3-2, p. C-47) y los
  rótulos se actualizaron en contracts, tareas, quickstart, plan y research. No se obtuvo copia
  oficial de INVIAS 640 («verificar cita literal») ni del IDU («pendiente de localizar»), así
  que la ayuda del umbral no las nombra; hay que pedir los documentos al autor.

---

## Phase 2: Foundational (prerrequisitos bloqueantes)

**Purpose**: punto de entrada único del análisis, su persistencia, su exposición en la API, la
herramienta de regresión y el esqueleto de la página de detalle.

**⚠️ CRITICAL**: ninguna historia empieza antes de cerrar esta fase.

- [X] T004 Crear `backend/cutting/analysis.py` con:
  - `VERSION_ANALISIS = 'analisis-1'`;
  - `masa(problem, diametro, longitud_escalada)`, que devuelve
    `longitud/problem['scale']·float(problem['densities'][diametro])`;
  - `analizar(problem, result, umbral=None)`, que devuelve
    `{'version': 'analisis-1', 'umbral_desperdicio_pct': umbral, 'verificacion': {'valido':
    result['metrics']['valido'], 'comprobaciones': ['demanda','diametro','capacidad','etapas',
    'inventario']}}`.

  `analizar` MUST NOT modificar `result['bars']` ni `result['inventory']`. Debe hacer una copia
  defensiva y verificar en una prueba que las barras quedan iguales.
- [X] T005 Integrar `analizar` en `backend/celery_worker.py`:
  - **Dónde**: justo después de `result = optimize(...)` (≈ línea 244) y antes de
    `generate(...)`.
  - **Qué**: asignar `result['metrics']['analisis'] = analizar(problem, result,
    config.get('umbral_desperdicio_pct'))`.
  - **Errores**: si `analizar` lanza una excepción cuyo mensaje empieza por
    «Error de dominio:», debe propagarse al `except` existente, que marca `error_processing`
    con `status_details`. No capturarla.
- [X] T006 Exponer los campos en `ProcessingResult.to_dict` de
  `backend/models/uploaded_file.py` (líneas ≈116-150), según
  [data-model.md §3](data-model.md):
  - siempre: `valido`, `umbral_desperdicio_pct` (de `execution_config`) y
    `admisibilidad_estado` (de `metricas.analisis.admisibilidad.proyecto.estado`);
  - con un parámetro nuevo `include_analysis=False`: `analisis` completo;
  - si faltan datos, `null`.

  Hacer que `GET /file/<id>` en `backend/server.py` (≈ líneas 357-369) use
  `include_analysis=True` y exponga el umbral vigente del archivo.
- [X] T007 [P] Añadir a `scripts/check_cutting_container.py` el modo `--comparar RUTA.jsonl`
  (repetible). Debe:
  - por cada registro de la línea base, reconstruir la ejecución desde `dataset`,
    `parametros_corte` (con las claves de `parameters.defaults()` únicamente; `None` en el
    escenario `ideal`), `metodo`, `perfil` y `seed`;
  - ejecutar `optimize` con el código en memoria;
  - comparar todas las claves salvo `duracion_segundos`, `timings`, `memoria_maxima_kib`,
    `codigo_sha256`, `python`, `plataforma`, `artefactos_generados`, `analisis`,
    `artifacts_seconds` y `pipeline_seconds`;
  - escribir cada diferencia en un JSONL nuevo, `--output`, que nunca sobrescribe (`open(...,
    'x')`), y terminar con código distinto de 0 si hay diferencias.

  Mapear el nombre de dataset a `tests/data/001/001-pruebaInicial.xlsx` y
  `tests/data/002/002-ingeBigTest.xlsx`. El mapeo se hace por el campo `dataset` del registro
  (`'001-pruebaInicial.xlsx'` y `'002-ingeBigTest.xlsx'`); un nombre desconocido es un error
  explícito.

  Compatibilidad, porque la CI usa este script (`.github/workflows/ci.yml:59`):
  - `--tests`, `--api-tests`, `--all-tests`, `--matrix` y `--artifacts-smoke` conservan sus
    argumentos y su salida;
  - la aserción de hojas de `--artifacts-smoke` (línea ≈61, hoy igualdad exacta con las siete
    hojas) pasa a «contiene las siete hojas originales». Cada tarea que añada una hoja en
    `report.py` la añade también a esa lista;
  - si existe `cutting/analysis.py`, `--artifacts-smoke` llama a `analizar` antes de
    `generate` y mide `analisis_segundos` (lo usa SC-007).

  Verificación: ejecutar la línea exacta de la CI (`--dataset
  tests/data/002/002-ingeBigTest.xlsx --seeds 1 --profiles rapido --matrix`) y
  `python3 -m unittest discover -s tests/deployment -v`.
- [X] T008 [P] Crear `frontend/src/app/archivos/[id]/page.tsx` como página cliente:
  - lee `id` con `useParams` y llama a `` `${API_URL}/file/${id}` `` (`frontend/src/lib/api.ts`);
  - maneja los estados de carga, error y no encontrado;
  - muestra el encabezado (nombre, selector de versión, por defecto la última, y umbral
    vigente);
  - tiene contenedores vacíos para las secciones de [contracts/ui.md](contracts/ui.md);
  - define los tipos TypeScript de `analisis` en `frontend/src/components/file-detail/types.ts`,
    según [data-model.md §2](data-model.md).
- [X] T009 Añadir en `frontend/src/components/FilesTable.tsx` el enlace «Ver detalle» a
  `/archivos/<id>`, en la tabla de escritorio (≈ líneas 611-650) y en las tarjetas móviles
  (≈ 651+).
- [X] T010 Prueba de huella e invariancia en `backend/tests/test_analisis.py`, que comprueba:
  - `analizar` no altera `result['bars']`;
  - `problem['hash']` es idéntico cuando `execution_config` lleva `umbral_desperdicio_pct`,
    porque el umbral nunca llega a `normalize`;
  - `optimize` con la misma semilla devuelve las mismas barras.

**Checkpoint**: el worker guarda `metricas.analisis.version = 'analisis-1'`, `/file/<id>` lo
expone y `/archivos/<id>` carga.

---

## Phase 3: User Story 1 — Evaluar el plan frente a un desperdicio admisible (P1) 🎯 MVP

**Goal**: umbral opcional; estado dentro, excede o sin evaluar por proyecto y por diámetro;
pérdida irrecuperable frente a saldo reutilizable; comparación de versiones (FR-001 a FR-006 y
FR-028).

**Independent Test**: subir 001 con umbral 5 % y reprocesar con 10 %. El estado pasa de
`excede` a `dentro`, y el desperdicio y las barras son idénticos (quickstart 6–9).

### Tests for User Story 1

- [X] T011 [P] [US1] Pruebas de admisibilidad en `backend/tests/test_analisis.py`:
  - estados `dentro` si «`desperdicio_pct ≤ umbral`», `excede` si es mayor y `sin_evaluar`
    si el umbral es `null`;
  - un empate exacto cuenta como `dentro`;
  - `diferencia_pp = desperdicio_pct − umbral` y `null` cuando el estado es `sin_evaluar`;
  - el `desperdicio_pct` del proyecto es igual a `metrics['desperdicio_porcentaje']`
    (tolerancia 1e-9);
  - el % por diámetro usa `(sobrante + perdida + descartado)/longitud_inicial` de
    `por_diametro`, ponderado por masa;
  - irrecuperable = `perdida_irrecuperable_kg` y reutilizable = `sobrante_final_kg`, con su %
    sobre `masa_inicial_kg`. Usar un caso con dos diámetros y pérdida por corte activa.
- [X] T012 [P] [US1] Pruebas de API en `backend/tests/test_cutting_api.py`, con el patrón de
  `upload()` y `patch.object(... 'apply_async')`:
  - `POST /upload` con `umbral_desperdicio_pct` igual a `0`, `100`, `-1` o `abc` devuelve 400 y
    no encola;
  - `"7,5"` y `"7.5"` se aceptan y se guardan como `7.5` en `execution_config`;
  - campo vacío o ausente se guarda como `null`;
  - `POST /estimate` con umbral responde igual que sin él;
  - `POST /reprocess/<id>`: clave ausente conserva el umbral, `null` lo quita, un valor lo
    reemplaza y uno inválido da 400 sin cambios;
  - el worker síncrono (`process_file_task.run`) guarda `metricas.analisis.admisibilidad` y
    copia el umbral en el snapshot de la versión.

### Implementation for User Story 1

- [X] T013 [US1] Implementar en `backend/cutting/analysis.py`:
  - `evaluar_admisibilidad(problem, metrics, umbral)`, que devuelve
    `{'proyecto': {...}, 'por_diametro': [{diametro, ...}]}` con `estado`, `desperdicio_pct` y
    `diferencia_pp`;
  - `perdidas(problem, metrics)`, que devuelve `irrecuperable` y `reutilizable` (`{kg, pct}`) y
    `por_diametro`.

  Conectarlas en `analizar` (data-model §2.1 y `perdidas`). Las masas por diámetro se convierten
  con `masa()` desde `por_diametro`.
- [X] T014 [US1] Añadir en `backend/server.py` el helper `parse_umbral(value)`:
  - acepta `str`, número o `None`; reemplaza `,` por `.`;
  - vacío o `None` devuelve `None`;
  - exige un número finito con «`0 < v < 100`»; si no, `ValueError('Umbral de desperdicio
    admisible inválido: debe ser un porcentaje mayor que 0 y menor que 100')`.

  Usarlo en `uploaded_configuration()` (≈ líneas 90-112) para añadir
  `umbral_desperdicio_pct` a la configuración devuelta **sin pasarlo a `normalize`** ni a
  `parametros_corte`.
- [X] T015 [US1] En `POST /reprocess/<id>` de `backend/server.py` (≈ líneas 412-488):
  - si el JSON trae la clave `umbral_desperdicio_pct`, validarla con `parse_umbral` antes de
    encolar;
  - si es válida, reasignar `uploaded_files.execution_config` (con un dict nuevo, para que
    SQLAlchemy detecte el cambio en JSONB) con el valor o con `None`;
  - si la clave falta, no tocar nada;
  - un error devuelve 400 sin encolar.
- [X] T016 [US1] En `backend/cutting/report.py` (`generate`, bloque `ExcelWriter`, ≈ líneas
  75-103):
  - hoja nueva `Admisibilidad`, con las columnas exactas de
    [contracts/artefactos.md](contracts/artefactos.md) y el proyecto primero;
  - `Metricas` añade `umbral_desperdicio_pct`, `admisibilidad_estado`,
    `perdida_irrecuperable_pct`, `reutilizable_pct` y `analisis_version`;
  - en el PDF (≈ líneas 116-137), las secciones «Desperdicio» (con irrecuperable y
    reutilizable) y «Admisibilidad», con la nota «el umbral lo define el usuario; no se
    identificó un máximo normativo». La sección de verificación es de T024 (US2, FR-029).

  Los datos se leen de `result['metrics'].get('analisis')`; si falta, la hoja indica «no
  disponible».
- [X] T017 [P] [US1] Añadir en `frontend/src/components/file-upload.tsx` un campo numérico
  opcional «Desperdicio admisible (%)», sin valor por defecto, con el texto de ayuda exacto de
  [contracts/ui.md](contracts/ui.md) («No identificamos una norma colombiana que fije un
  porcentaje máximo…»; MUST NOT nombrar normas concretas hasta que T003 las verifique) y
  validación local «`0 < v < 100`». En `makeForm()`
  (≈ líneas 205-215), enviar `umbral_desperdicio_pct` solo si tiene valor.
- [X] T018 [US1] Añadir en `frontend/src/components/FilesTable.tsx`:
  - la insignia de la última versión («Dentro de lo admisible», «Excede» o «Sin evaluar»;
    nada si `admisibilidad_estado` es `null`), en la tabla y en las tarjetas;
  - en el diálogo de reproceso (≈ líneas 737-758), el campo de umbral precargado con el
    vigente.

  `handleReprocess` (≈ 277-307) envía `umbral_desperdicio_pct`: el número, `null` si se vació
  o la clave ausente si no se tocó.
- [X] T019 [P] [US1] Crear `frontend/src/components/file-detail/AdmissibilitySection.tsx`:
  - estado del proyecto y diferencia en pp;
  - tabla por diámetro;
  - irrecuperable frente a reutilizable en kg y %;
  - «no disponible» si `analisis` es `null`.

  Montarla en `frontend/src/app/archivos/[id]/page.tsx`.
- [X] T020 [P] [US1] Crear `frontend/src/components/file-detail/VersionsTable.tsx` (FR-028):
  - columnas: versión, perfil, tiempo (`processing_time_seconds`), desperdicio, umbral,
    estado de admisibilidad, verificación y descargas (`/descargar-{excel,pdf,imagen,
    inventario}/<storage_uuid>`);
  - aviso «umbrales distintos» si los umbrales difieren entre versiones;
  - «no disponible» en cualquier celda cuyo dato falte (versiones históricas sin tiempo,
    sin verificación o sin `analisis`);
  - tarjetas en móvil.

  Montarla en `frontend/src/app/archivos/[id]/page.tsx`.
- [X] T021 [US1] **Detenerse y pedir aprobación** para el E2E del MVP. Las imágenes llevan el
  código dentro, sin montajes (AGENTS.md), así que validar US1 en el navegador requiere
  reconstruir backend, worker y frontend.
  - Medir `df -h /mnt/c` y `docker system df` (solo lectura).
  - Estimar el espacio: sin cambios de requisitos, backend y worker solo rehacen la capa
    `COPY backend/`; el frontend rehace `npm run build`.
  - Preguntar al usuario. Solo con aprobación, ejecutar
    `docker compose build backend celery_worker frontend` y `docker compose up -d --wait`.
  - Registrar el espacio antes y después en `.claude/context/CURRENT_STATE.md`.
  - Si T038 (scipy en requisitos) ya se aplicó, avisar de que esta reconstrucción incluye scipy.
  **Decisión del usuario (2026-10-02)**: con 7,3 GB libres en C: y la caché de build vacía, no se
  reconstruye ahora. Se hará **una sola reconstrucción al final**, de las tres imágenes y ya con
  scipy (T037/T038), seguida del E2E completo (T054). Tras verificar que las nuevas imágenes
  arrancan sanas, se retiran solo las imágenes huérfanas de oica-backend, oica-worker y
  oica-frontend (nunca `docker system prune` ni volúmenes). El MVP quedó validado sin navegador:
  97 pruebas y 0 diferencias en 148 registros.

**Checkpoint**: US1 funciona sola. Prueba independiente: quickstart 6, 7, 8 y 9.

---

## Phase 4: User Story 2 — Resumen de compra verificado (P2)

**Goal**: barras por diámetro, longitud y origen, con masa y aprovechamiento; verificación
visible (FR-027, FR-029).

**Independent Test**: en 002, la suma del resumen por (diámetro, longitud) es igual a las
barras del plan, y se muestra «Plan verificado» (quickstart 10).

### Tests for User Story 2

- [X] T022 [P] [US2] Pruebas en `backend/tests/test_analisis.py`:
  - `resumen_compra` agrupa por `(diametro, longitud, origen)`;
  - por (diámetro, longitud), la suma de `barras` es igual a las barras del plan;
  - en un caso con inventario adicional, las líneas `adicional` salen aparte;
  - `masa_kg = barras·longitud·densidad`;
  - `aprovechamiento_pct` es la masa de piezas sobre `masa_kg`;
  - las longitudes no estándar aparecen tal cual;
  - `verificacion.valido` es `True`.

### Implementation for User Story 2

- [X] T023 [US2] Implementar `resumen_compra(problem, result)` en `backend/cutting/analysis.py`:
  - campos según data-model §2.2: «Las barras `adicional` no se cuentan como compra»;
  - longitudes en metros con `longitud/scale`;
  - masa de las piezas por barra: `Σ cut.longitud·cut.cantidad`.

  Conectarla en `analizar`.
- [X] T024 [US2] En `backend/cutting/report.py`:
  - hoja `Resumen de compra` con las columnas de contracts/artefactos.md;
  - sección «Resumen de compra» en el PDF;
  - encabezado del PDF: «Plan verificado: demanda, diámetro, capacidad, etapas e inventario».
    Es la única tarea que escribe la verificación en el PDF.
- [X] T025 [P] [US2] Crear `frontend/src/components/file-detail/PurchaseSummary.tsx` (tabla por
  diámetro, longitud y origen, con el inventario separado) y `VerificationBanner.tsx` («Plan
  verificado», o el `status_details` del archivo si la versión falló). Montarlos en
  `frontend/src/app/archivos/[id]/page.tsx`.

**Checkpoint**: US1 y US2 funcionan de forma independiente.

---

## Phase 5: User Story 3 — Plan como patrones de corte repetidos (P3)

**Goal**: agrupación en patrones, `patron_id` por barra, y PDF y PNG por patrones con «nesting
lineal» (FR-007 a FR-011).

**Independent Test**: en 002, `Σ repeticiones = filas de Barras` y la reconstrucción da la
demanda exacta (quickstart 11 y 12).

### Tests for User Story 3

- [X] T026 [P] [US3] Pruebas en `backend/tests/test_analisis.py`:
  - barras idénticas forman un solo patrón;
  - las mismas piezas en otro `grupo` forman otro patrón;
  - otro origen o el mismo largo con otra pérdida forman otro patrón;
  - un plan con todas las barras distintas da tantos patrones como barras;
  - `Σ repeticiones = len(bars)`;
  - expandir los patrones reproduce la demanda por (diámetro, grupo, longitud);
  - los IDs `P-<diámetro>-<nnn>` son deterministas (mismo resultado en dos llamadas).
- [X] T027 [P] [US3] Prueba de artefactos en `backend/tests/test_cutting_api.py`, extendiendo
  `test_artefactos_visuales_acotados`:
  - el Excel tiene la hoja `Patrones` y la columna `Barras.patron_id`;
  - cada `patron_id` existe en `Patrones`;
  - el PDF y el PNG siguen dentro de los límites actuales.

### Implementation for User Story 3

- [X] T028 [US3] Crear `backend/cutting/patterns.py`:
  - `clave(bar)`: `(diametro, origen, longitud, tuple((grupo, longitud, cantidad) por corte),
    kerf, discarded, remaining, tuple((e['grupo'], e['longitud']) for e in discard_events))`,
    con 0 o vacío si faltan campos (ruta sin pérdida física);
  - `agrupar(problem, bars)`: devuelve `(patrones, patron_por_barra)`, ordenados por diámetro,
    repeticiones descendentes y clave, con IDs `P-<diámetro>-<nnn>`;
  - `verificar(problem, patrones, bars)`: lanza `ValueError` si no se cumple FR-011.
- [X] T029 [US3] En `backend/cutting/analysis.py`, llamar a `patterns.agrupar` y
  `patterns.verificar`, y guardar solo el resumen (`total`, `barras`, `max_repeticiones`, `top`
  de hasta 10). Exponer una función `patrones_de(problem, result)` para que `report.py` obtenga
  la lista completa sin persistirla en JSONB.
- [X] T030 [US3] En `backend/cutting/report.py`:
  - `Barras` añade la columna `patron_id`;
  - hoja `Patrones` con las columnas de contracts/artefactos.md y la `secuencia` en formato
    «`E1: 2×2,35 m + 1×1,10 m | E2: 3×0,80 m`»;
  - el PDF reemplaza la muestra `cuts[:150]` (≈ línea 112) por la tabla de patrones (hasta 150,
    los más repetidos), con «Se omitieron N patrones; el Excel contiene el total»;
  - el PNG (≈ líneas 132-152) dibuja hasta 60 patrones con la etiqueta `P-… ×rep`, lleva el
    título «Nesting lineal por patrones de corte» y el pie de omitidos, con dpi 100 y el alto
    máximo actual.

**Checkpoint**: US1–US3 funcionan de forma independiente.

---

## Phase 6: User Story 4 — Calidad frente al mejor resultado posible (P4)

**Goal**: cota Gilmore–Gomory certificada, cota simple y brecha; error de dominio; cota de los
ensayos registrados (FR-012 a FR-017).

**Independent Test**: `cota_ensayos.py` muestra desperdicio ≥ cota en el 100 % de los registros,
y las instancias pequeñas dan cota ≤ óptimo (quickstart 4 y 5).

### Tests for User Story 4

- [X] T031 [P] [US4] Pruebas en `backend/tests/test_analisis.py`; las que necesitan scipy usan
  `@unittest.skipUnless(scipy disponible, 'scipy no instalado: cota no disponible')`:
  1. **Caso analítico**: una longitud de pieza y una de barra, sin pérdida, da
     `cota = ⌈n/q⌉·L`, con `q = ⌊(L+e)/(l+e)⌋`.
  2. **Fuerza bruta**: en 20 instancias aleatorias pequeñas (≤ 3 longitudes de pieza, ≤ 8
     piezas, barras de 6, 9 y 12), la cota es ≤ el óptimo enumerado.
  3. **Inventario limitado y pérdida activa**: la cota es ≤ el material del plan de `optimize`.
  4. **Sin converger**: con `max_iter=1`, `ajustada` es `False` y la cota sigue siendo válida.
  5. **Cota simple**: es ≤ la cota por patrones.
  6. **Sin scipy** (con `import` simulado): `estado = 'no_disponible'`.
  7. **Error de dominio**: si se inyecta una cota mayor que el desperdicio, `analizar` lanza
     `ValueError` que empieza por «Error de dominio:».
  8. **Fallo del solver**: con `linprog` simulado para lanzar una excepción, `estado` es
     `'no_disponible'`, hay un `motivo` y `analizar` no lanza excepción.

### Implementation for User Story 4

- [X] T032 [US4] Crear `backend/cutting/bound.py` según research R-02:
  - `mochila(capacidad, pesos, valores, cotas)`: mochila acotada exacta, con división binaria
    vectorizada en numpy y reconstrucción del patrón;
  - `cota_diametro(problem, d, max_iter=200, limite_s=2.0)`: maestro con
    `scipy.optimize.linprog(method='highs')` importado dentro de la función; patrones
    homogéneos iniciales; pricing con capacidad `L+e` y pesos `l+e`; certificado
    `LB = θ·Σn·y + Σ_inv u·min(0, L−θz)` con `z·(1+1e-9)`; redondeo al múltiplo de
    `mcd(L_k)`; `ajustada`;
  - `cota_simple(problem, d)`: devuelve `material_m`, `desperdicio_pct` y `barras_minimas`;
  - `cota_plan(problem, metrics, limite_total_s=4.0)` (implementado con 4 s, en lugar de 6 s, por el margen de SC-007).

  Los resultados siguen data-model §2.4. Si falla el import de scipy, o si el solver o el
  pricing lanzan cualquier excepción, `cota_plan` devuelve `estado='no_disponible'` con un
  `motivo` y la registra en el log. Nunca propaga la excepción, porque una métrica no puede
  impedir entregar un plan válido (Principio IV). Agotar el tiempo o las iteraciones no es un
  error: da una cota válida con `ajustada=False`.
- [X] T033 [US4] En `backend/cutting/analysis.py`, conectar `bound.cota_plan`:
  - calcular `brecha_pp` por diámetro y para el proyecto;
  - lanzar `ValueError('Error de dominio: ...')` (con el diámetro, el desperdicio y la cota) si
    `desperdicio_plan < desperdicio_cota − 1e-9` en el proyecto o en algún diámetro (FR-015).
  - solo el `ValueError` cuyo mensaje empieza por «Error de dominio:» sale de `analizar`.
- [X] T034 [US4] En `backend/cutting/report.py`:
  - hoja `Cota` con las columnas de contracts/artefactos.md;
  - `Metricas` añade `cota_desperdicio_pct`, `cota_ajustada` y `brecha_pp`;
  - sección «Cota inferior por patrones y brecha» en el PDF, con «no ajustada» o «no
    disponible» si aplica.
- [X] T035 [P] [US4] Crear `frontend/src/components/file-detail/QualitySection.tsx`, con la cota
  por patrones, la cota simple, la brecha en pp y las marcas «no ajustada» o «no disponible».
  Montarla en `frontend/src/app/archivos/[id]/page.tsx`.
- [X] T036 [P] [US4] Crear `scripts/cota_ensayos.py` (research R-12):
  - lee `tests/benchmarks/2026-09-13-fisico-matriz-final.jsonl` y los dos
    `2026-09-13-fisico-control-*.jsonl`;
  - normaliza cada cartilla con el `parametros_corte` del registro (solo las claves de
    `parameters.defaults()`; `None` en el escenario `ideal`);
  - calcula la cota una vez por (dataset, escenario o parámetros) sin ejecutar el AG;
  - compara con `desperdicio_porcentaje` y `por_diametro`;
  - escribe `tests/benchmarks/<fecha>-cota-ensayos.jsonl` (`open('x')`) y sale con código 1 si
    algún registro queda por debajo de la cota.
- [X] T037 [US4] **Detenerse y pedir aprobación** para añadir scipy y reconstruir. El usuario
  aprobó por adelantado una única reconstrucción final de las tres imágenes con scipy (decisión de
  T021). Antes de construir hay que volver a medir: si el pico estimado supera el espacio libre,
  detenerse y consultar:
  - medir `df -h /mnt/c` y `docker system df` (solo lectura);
  - estimar el espacio: rueda de 37,5 MB más la reinstalación de la capa pip de backend y
    worker, porque cambian los requisitos;
  - preguntar al usuario.

  Sin aprobación, US4 queda con la cota «no disponible» y se sigue con US5. Si el espacio no
  alcanza, ofrecer la alternativa registrada en research R-01 (`highspy`), que requiere una
  nueva decisión del usuario.
  **Resultado (2026-10-02)**: aprobación anticipada (T021) confirmada con una nueva medición:
  C: 9,4 GB libres, pico estimado de 3–4 GB, caché de build vacía. Se procede con T038.
- [X] T038 [US4] Solo con la aprobación de T037:
  1. añadir `scipy==1.18.1` a `config/backend/constraints.txt` y `scipy` a
     `config/backend/requirements-common.txt` (research R-01; rueda `musllinux_1_2_x86_64`,
     `numpy>=2.0,<2.8`). Los requisitos no se tocan antes de la aprobación, para que ninguna
     reconstrucción incidental ni la CI descarguen scipy antes de tiempo;
  2. ejecutar `docker compose build backend celery_worker frontend` y `docker compose up -d --wait`
     (reconstrucción única, decisión de T021). Con las nuevas imágenes sanas, retirar solo las
     imágenes huérfanas de OICA;
  3. correr las pruebas de T031 sin `skip`;
  4. ejecutar `scripts/cota_ensayos.py` (FR-017, SC-006).

  Registrar el tamaño de las imágenes antes y después en `.claude/context/CURRENT_STATE.md`.

**Checkpoint**: US4 funciona con scipy; sin scipy, la app sigue operando con la cota «no
disponible».

---

## Phase 7: User Story 5 — Contexto colombiano, eficiencia e IA visibles (P5)

**Goal**: aviso de masa nominal NSR-10 (Tabla C.3.5.3-2, verificada en T003), aprovechamiento y
cinco definiciones en el tutorial (FR-018 a FR-020).

**Independent Test**: una cartilla temporal con #4 alterado en más de 1 % muestra el aviso sin
bloquear el proceso; el tutorial contiene las cinco definiciones (quickstart 13).

### Tests for User Story 5

- [X] T039 [P] [US5] Pruebas en `backend/tests/test_analisis.py`:
  - con masas nominales (`mass_per_m=0.994` para #4), no hay avisos;
  - con #4 a `1.01` (más de 1 %), aparece un aviso con `masa_cartilla_kg_m`,
    `masa_nominal_kg_m` y `diferencia_relativa_pct`, y el plan se genera;
  - una diferencia de exactamente 1 % no avisa;
  - un diámetro fuera de la tabla da `estado='no_contrastado'`;
  - `aprovechamiento_pct + desperdicio_porcentaje = 100`.

### Implementation for User Story 5

- [X] T040 [P] [US5] Crear `backend/cutting/nominal.py` con:
  - `MASA_NOMINAL_KG_M`: `{'#2': 0.25, '#3': 0.560, '#4': 0.994, '#5': 1.552, '#6': 2.235,
    '#7': 3.042, '#8': 3.973, '#9': 5.060, '#10': 6.404, '#11': 7.907, '#14': 11.380,
    '#18': 20.240}`, y el comentario «NSR-10, Título C, Tabla C.3.5.3-2, p. C-47 (verificada
    2026-10-02, ficha REF-NSR10-TABLA de Referencias.md); coincide con TablaBarras de
    Planilla_Cartilla.xlsx», y la constante `ROTULO = 'masa nominal NSR-10 (Título C, Tabla C.3.5.3-2)'`, que usan los artefactos;
  - `TOLERANCIA = 0.01`;
  - `avisos(problem)`, que devuelve solo los diámetros con aviso (diferencia > 1 %) o
    `no_contrastado`.
- [X] T041 [US5] Conectar `nominal.avisos` y `aprovechamiento_pct = 100 −
  desperdicio_porcentaje` en `analizar` (`backend/cutting/analysis.py`).
- [X] T042 [US5] En `backend/cutting/report.py`:
  - hoja `Avisos` (con la fila «Sin avisos» si no hay ninguno);
  - `Metricas` añade `aprovechamiento_pct`;
  - secciones «Aprovechamiento» y «Avisos de masa nominal NSR-10» en el PDF, con el rótulo
    tomado de `nominal.ROTULO`.
- [X] T043 [P] [US5] Crear `frontend/src/components/file-detail/MassWarnings.tsx`, titulado
  «Avisos de masa nominal NSR-10» y con la fuente «masa nominal NSR-10 (Título C, Tabla C.3.5.3-2)» (verificada en T003),
  que solo aparece si hay avisos, y mostrar el aprovechamiento junto al desperdicio en
  `AdmissibilitySection.tsx`.
- [X] T044 [P] [US5] En el arreglo `glosario` de
  `frontend/src/components/tutorial/TutorialGuide.tsx` (≈ línea 51):
  - reencuadrar «Algoritmo genético» como técnica de Inteligencia Artificial de la computación
    evolutiva;
  - ampliar «Patrón de corte» con las repeticiones;
  - añadir «Nesting lineal», «Cota inferior» y «Desperdicio admisible», con los textos de
    contracts/ui.md;
  - en el arreglo `faqs`, añadir una entrada sobre las barras #2: el catálogo por defecto no
    incluye #2 (va de #3 a #18); una cartilla con pedidos #2 necesita que el usuario agregue
    esa longitud al catálogo antes de procesar (caso límite de la spec).

  Ningún texto debe afirmar optimalidad.

**Checkpoint**: US1–US5 funcionan.

---

## Phase 8: User Story 6 — Documento de tesis y referencias coherentes (P6)

**Goal**: `Referencias.md` con fichas completas, y los capítulos 1–4 coherentes con el título y
con lo que la app ya hace (FR-021 a FR-026).

**Independent Test**: un revisor toma cada término del título y encuentra su definición, su
respaldo y una fuente con estado (SC-001, SC-008).

- [X] T045 [US6] Escribir `docs/tesis-doc/Referencias.md`: una ficha por fuente de la tabla
  R-13 de [research.md](research.md), más las ya citadas en `docs/tesis-doc/0*_Capitulo*.md`.
  - **Campos** (FR-021): cita completa, enlace, estado («verificada», «verificar cita literal»,
    «verificar edición y páginas» o «pendiente de localizar»), motivo, **pregunta textual del
    usuario que la originó**, término del título, ubicación en la tesis y advertencias.
  - **Pregunta textual**: tomarla de INF-014 en `INFERENCIAS_TESIS.md` y de
    `specs/001-alineacion-titulo-tesis/spec.md`. Si no está registrada, escribir «pendiente:
    pedir al autor» y no inventarla.
  - **Verificación**: ninguna ficha se marca «verificada» sin haber consultado la fuente.
  - **Fichas de T003**: completar las que T003 no haya creado; conservar su estado.
- [X] T046 [US6] Actualizar `docs/tesis-doc/01_Capitulo1.md`:
  - título fijo exacto y «aplicación web» en lugar de «local» en todo el capítulo: título,
    Resumen, Abstract en inglés y cuerpo (hoy en las líneas 1, 5, 9, 19 y 55; confirmar con
    `grep -n local`);
  - objetivo general y OE1–OE5 con la redacción de la sección Contexto de la spec, marcados
    «redacción ajustada, pendiente de revisión del director»;
  - procedencia de 001/002 como obra colombiana confidencial y anonimizada, sin identificarla.
- [X] T047 [US6] Actualizar `docs/tesis-doc/02_Capitulo2.md`:
  - el AG como técnica de IA (computación evolutiva);
  - «nesting» definido como nesting lineal 1D con fuente, reconociendo que en la tipología de
    Wäscher et al. el término suele reservarse para piezas irregulares; se mantiene la
    exclusión de modelos generativos, redes neuronales y nesting 2D;
  - patrones de corte y Gilmore–Gomory;
  - desperdicio admisible, con la frase explícita de que ninguna norma (NSR-10, INVIAS 640,
    IDU, Res. 472) fija un máximo y que el desperdicio va en el precio unitario. Cada cita
    lleva el estado de su ficha.
- [X] T048 [US6] Actualizar `docs/tesis-doc/03_Capitulo3.md` con la capa de análisis
  posterior: admisibilidad (INF-015), patrones, cota con certificado lagrangiano y etapas
  relajadas (INF-016), aviso NSR-10 y resumen de compra. Declarar que la cota puede ser holgada
  y que no construye el plan.
- [X] T049 [US6] Actualizar `docs/tesis-doc/04_Capitulo4.md` **solo con salidas reales**: la
  matriz original (`2026-09-13-fisico-matriz-final.jsonl` y controles) y la cota de T036/T038
  (`tests/benchmarks/<fecha>-cota-ensayos.jsonl`). La regresión de T052 se cita únicamente
  como confirmación de que la línea base sigue siendo válida con `analisis-1`; no aporta
  resultados nuevos (research R-03, Principio III):
  - evaluar OE5 comparando el desperdicio del AG en 001/002 con las heurísticas FFD/BFD de la
    matriz y con la cota (brecha);
  - no mostrar admisibilidad salvo que el autor aporte un porcentaje con fuente (FR-025);
  - la comparación con datos de obra se marca pendiente (RIESGO-AC-009).
- [X] T050 [US6] Archivos de control (FR-026):
  - en `INFERENCIAS_TESIS.md`, actualizar el estado de INF-015 si el director respondió, y el
    de INF-016;
  - pasar RIESGO-AC-008 de `.claude/diagnostics/ACADEMIC_RISKS.md` a «mitigado» solo si
    T045–T049 están completas, o dejarlo en mitigación con lo pendiente.

**Checkpoint**: todas las historias completas.

---

## Phase 9: Polish & Cross-Cutting Concerns

- [X] T051 Ejecutar todas las pruebas backend (`python3 scripts/check_cutting_container.py
  --all-tests`, y en la imagen nueva si se completó T038). Deben dar 0 fallos.
- [X] T052 **Puerta de regresión SC-002**: ejecutar `python3 scripts/check_cutting_container.py`
  con
  `--comparar tests/benchmarks/2026-09-13-fisico-matriz-final.jsonl`,
  `--comparar tests/benchmarks/2026-09-13-fisico-control-cizalla.jsonl`,
  `--comparar tests/benchmarks/2026-09-13-fisico-control-fin-etapa.jsonl` y
  `--output tests/benchmarks/<fecha>-regresion-analisis-1.jsonl`.

  Resultado exigido: 0 diferencias en los 148 registros. Si hay diferencias, detenerse y
  reportar (Principio III). Estas ejecuciones no llevan umbral; la parte «con o sin umbral» de
  SC-002 la cubre T010, porque el umbral nunca llega a `optimize`.
- [X] T053 [P] Ejecutar `cd frontend && npm run typecheck && npm run lint && npm run build`, y
  axe en `/subir-cartilla`, `/archivos` y `/archivos/<id>` a 1440, 820 y 390 px. Sin errores y
  sin violaciones nuevas.
- [X] T054 E2E local según [quickstart.md](quickstart.md), escenarios 6–13 y 15:
  - usar cartillas de QA con prefijo `qa-001-*`;
  - para el escenario 13, crear la cartilla con la masa alterada en el directorio temporal,
    nunca en `tests/data/`;
  - verificar que las versiones históricas (ids 36, 38 y 39) muestran «no disponible» sin
    error y no se modifican;
  - al terminar, eliminar los proyectos de QA.

  Requiere las imágenes reconstruidas con el código final de backend, worker y frontend. Si no
  están al día, repetir el procedimiento de aprobación de T021 antes de reconstruir.
- [X] T055 Medir SC-005 (filas de `Barras` / filas de `Patrones` en 002) y SC-007. Para
  SC-007, repetir el comando de T002 con `--output tests/benchmarks/<fecha>-despues-sc007.jsonl`
  y comparar `duracion_segundos + analisis_segundos + artefactos_y_verificacion_segundos` con
  la línea base de T002. Criterio: «≤ 1,25 × base»; si no se cumple, detenerse y reportar.
  Registrar ambos resultados en `tests/data/002/ANALISIS_RESULTADOS.md` y, si SC-005 no llega
  a 5×, actualizar la meta de la spec con el valor medido.
  Ampliar `scripts/verify_sequential_result.py` para auditar las versiones con `analisis-1`:
  `Σ Patrones.repeticiones = filas de Barras`, cada `Barras.patron_id` existe en `Patrones`, y
  por (diámetro, longitud) la suma de `Resumen de compra.barras` es igual a las barras (SC-004,
  SC-010). Las versiones sin esas hojas se omiten sin error. Ejecutarlo sobre las versiones E2E
  de T054.
- [X] T056 Cierre de sesión: actualizar `.claude/context/CURRENT_STATE.md`, `PLAN_TRABAJO.md`
  (Bloque K) e `INFERENCIAS_TESIS.md`, con las rutas de los JSONL nuevos y los ids de prueba.
  Sin commits salvo orden explícita.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (T001–T003)**: sin dependencias. T003 (verificación de fuentes) no bloquea: solo
  decide los rótulos finales de C1.
- **Foundational (T004–T010)**: depende de Setup y bloquea todas las historias.
- **US1 (T011–T021)**: depende de Foundational. Es el MVP. T021 requiere aprobación del
  usuario para reconstruir imágenes.
- **US2 (T022–T025)**: depende de Foundational; es independiente de US1 en lógica, pero
  comparte `analysis.py`, `report.py` y la página de detalle (editar en serie).
- **US3 (T026–T030)**: depende de Foundational; independiente de US1 y US2.
- **US4 (T031–T038)**: depende de Foundational. T037 pide la aprobación del usuario y T038 solo
  se ejecuta con ella. La brecha y el error de dominio usan el `desperdicio_pct` por diámetro
  de US1 (T013), así que conviene hacerla después de US1.
- **US5 (T039–T044)**: depende de Foundational. T043 usa `AdmissibilitySection` de US1.
- **US6 (T045–T050)**: T045–T048 pueden empezar en cualquier momento después de este plan.
  T049 depende de T036, T038 y T052.
- **Polish (T051–T056)**: después de las historias elegidas. T052 debe ejecutarse siempre
  antes de declarar terminada cualquier entrega.

### Archivos compartidos (no paralelizar entre historias)

`backend/cutting/analysis.py`, `backend/cutting/report.py`,
`backend/tests/test_analisis.py` (cada historia añade su propia clase de pruebas),
`frontend/src/app/archivos/[id]/page.tsx` y `frontend/src/components/FilesTable.tsx`.

### Within Each User Story

Pruebas primero (deben fallar), luego módulos de dominio, `analysis.py`, `report.py`, API y
por último UI. Cerrar cada historia con `--all-tests`.

## Parallel Opportunities

- **Setup**: T003 (verificación de fuentes) en paralelo con todo el trabajo de código.
- **Foundational**: T007 (script) y T008 (página) en paralelo con T004–T006.
- **US1**: T011 y T012 en paralelo; T017, T019 y T020 (frontend) en paralelo con T013–T016
  (backend).
- **US3**: T026 y T027 en paralelo; T028 es independiente del frontend.
- **US4**: T035 y T036 en paralelo con T032.
- **US5**: T040, T043 y T044 en paralelo.
- **US6**: T045–T048 en paralelo con todo el trabajo de código (solo documentos).

## Parallel Example: User Story 1

```bash
# Pruebas en paralelo:
Task: "T011 [US1] Pruebas de admisibilidad en backend/tests/test_analisis.py"
Task: "T012 [US1] Pruebas de API del umbral en backend/tests/test_cutting_api.py"

# Frontend en paralelo con el backend:
Task: "T017 [US1] Campo de umbral en frontend/src/components/file-upload.tsx"
Task: "T019 [US1] AdmissibilitySection.tsx"
Task: "T020 [US1] VersionsTable.tsx"
```

## Implementation Strategy

### MVP (solo US1)

1. Phase 1 y Phase 2.
2. Phase 3 (US1).
3. **Validar**: T051, T052 (regresión, 0 diferencias) y quickstart 6–9.
4. Reconstruir backend, worker y frontend solo tras la aprobación de T021 (sin scipy: solo
   capas de código) y ejecutar quickstart 6–9. Detenerse y mostrar al usuario.

### Entrega incremental

1. MVP (US1).
2. US2 y US3: ninguna requiere scipy.
3. US5: cambios pequeños.
4. US4: pedir aprobación de espacio (T037) y, con ella, añadir scipy y reconstruir (T038).
5. US6: documento, cuando la app esté validada (prioridades de la constitución).
6. Polish completo.

### Notas

- Cada «≈ línea» es orientativa: confirmar con `grep` antes de editar.
- Si una tarea revela que hay que tocar un archivo intocable, detenerse y consultar
  (Principio III).
