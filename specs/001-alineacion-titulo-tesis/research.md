# Research: Alineación de OICA con el título fijo de la tesis

**Feature**: `001-alineacion-titulo-tesis` | **Fecha**: 2026-10-02 | **Plan**: [plan.md](plan.md)

Cada decisión sigue el formato Decisión / Razón / Alternativas. Las decisiones R-01 a R-04
las cerró el usuario el 2026-10-02. Las demás se derivan de la spec, de la constitución v1.0.0
y de la lectura del código.

---

## R-01 — Solver de programación lineal para la cota Gilmore–Gomory

- **Decisión**: `scipy.optimize.linprog(method='highs')`, con scipy **1.18.1** fijado en
  `config/backend/constraints.txt` y declarado en `config/backend/requirements-common.txt`. Así
  queda disponible en el backend y en el worker.
- **Verificación hecha (PyPI, 2026-10-02)**:
  - Existe la rueda `scipy-1.18.1-cp312-cp312-musllinux_1_2_x86_64.whl` (37,5 MB), compatible
    con la imagen `python:3.12-alpine`.
  - Requiere `numpy>=2.0.0,<2.8`, compatible con el `numpy==2.4.4` fijado.
  - No hay que compilar, así que el `gcc` temporal de los Dockerfiles no interviene.
- **Razón**: HiGHS es un solver LP robusto y mantenido, que devuelve las variables duales
  (`res.ineqlin.marginals`) necesarias para el pricing. El usuario lo eligió por robustez frente
  a un simplex propio.
- **Coste y condiciones**:
  - Instalado ocupa del orden de 100 MB por imagen; la medición exacta queda como tarea de
    implementación.
  - Cambiar los requisitos invalida la capa de pip de backend y worker. Reconstruir **requiere
    aprobación previa del usuario** con una estimación de espacio (constitución, Restricciones;
    C: tenía 9,3 GB libres el 2026-10-02).
- **Mitigación**: `cutting/bound.py` importa scipy de forma diferida. Si no está instalado, la
  cota se reporta con estado `no_disponible` y el resto del análisis funciona. Así, las pruebas
  de patrones, admisibilidad y compra, y la regresión de los 136, pueden correr en el contenedor
  actual antes de reconstruir.
- **Alternativas consideradas**:
  - Simplex propio sobre numpy: sin dependencia, pero el usuario lo descartó por más código que
    validar.
  - `highspy` 1.15.1 (solo los bindings de HiGHS, rueda musllinux de 6,6 MB): mismo solver con
    menos peso. Queda registrado como alternativa si el espacio en disco impide instalar scipy;
    cambiarlo requiere nueva decisión del usuario.
  - PuLP/CBC u OR-Tools: más pesadas y con binarios externos; sin ventaja para un LP continuo.

## R-02 — Formulación y certificación de la cota (FR-012 a FR-016)

- **Decisión**: generación de columnas de Gilmore–Gomory **por diámetro**, sobre la relajación
  lineal y en enteros escalados (`problem['scale']`).
  - **Datos por diámetro**:
    - Longitudes de pieza distintas `l_i`, con demanda total `n_i`, que es la suma de las
      etapas (el orden de etapas se relaja).
    - Tipos de barra `k`, tomados de `problem['stock']`: longitud `L_k`, origen y cantidad
      `u_k`. `u_k = ∞` si `cantidad` es `None` (comercial ilimitado).
    - Pérdida por corte `e = problem['rules']['kerf']`.
  - **Patrón factible (relajado)**: `Σ_i (l_i + e)·a_i ≤ L_k + e`, con `0 ≤ a_i ≤ n_i` enteros.
    Es necesario para cualquier barra real. Con `m` piezas hay al menos `m − 1` separaciones,
    porque `physical.capacity()` no cobra la pérdida cuando la última pieza agota la barra.
    Por eso es una relajación válida. Descartes por mínimo reutilizable, saldos entre etapas y
    orden de etapas se relajan.
  - **Maestro**: `min Σ_k L_k·Σ_{p∈P_k} x_p`, sujeto a `Σ_p a_ip·x_p ≥ n_i`,
    `Σ_{p∈P_k} x_p ≤ u_k` (si `u_k` es finito) y `x ≥ 0`. Se arranca con patrones homogéneos
    (una sola longitud de pieza), que siempre son factibles si alguna barra admite la pieza.
  - **Pricing**: para cada tipo `k`, una mochila acotada **exacta en pesos enteros**, con
    capacidad `L_k + e`, pesos `l_i + e`, valores `y_i` (duales) y división binaria de
    cantidades. Se vectoriza con numpy (`dp = maximum(dp, shift(dp) + v)`) y conserva las
    elecciones para reconstruir el patrón. Entra la columna si `L_k − (z_k − w_k) < −tol`.
  - **Certificado de validez** (independiente de la precisión del solver), en cualquier
    iteración y con duales `y ≥ 0`:
    1. `z_k = valor máximo de la mochila de k`, inflado por `(1 + 1e-9)` como margen de coma
       flotante.
    2. `θ = min(1, min_{k: u_k=∞} L_k / z_k)`, de modo que todos los costes reducidos de las
       barras ilimitadas sean ≥ 0.
    3. `LB_d = θ·Σ_i n_i·y_i + Σ_{k: u_k<∞} u_k·min(0, L_k − θ·z_k)`.

    Es la cota lagrangiana de la relajación lineal, válida para todo plan entero factible.
  - **Redondeo**: el material de un plan es una combinación entera de las `L_k`. Por eso
    `LB_d` se redondea hacia arriba al múltiplo de `g = mcd(L_k)` del diámetro.
  - **Estado de ajuste**: `ajustada = True` si la generación de columnas terminó sin columnas
    de coste reducido negativo y el certificado coincide con el valor del maestro (con
    tolerancia relativa de 1e-6). En otro caso, `ajustada = False` y se presenta como «no
    ajustada» (FR-014).
  - **Presupuesto de tiempo**: 2 s por diámetro y 4 s por plan (implementado; se bajó de 6 s para dejar margen a SC-007, cuya base medida es 19,14 s con límite 23,93 s), más un máximo de 200
    iteraciones por diámetro. Ambos son constantes del módulo y se miden contra SC-007.
  - **Conversión**: material en metros = `LB_d / scale` y masa = metros·densidad del diámetro.
    El % de desperdicio límite es `1 − masa_piezas / masa_LB`, por diámetro y para el proyecto
    (sumando masas).
  - **Cota simple** (FR-013): material ≥ `Σ_i l_i·n_i`, redondeado a `g`; equivale a un
    aprovechamiento perfecto. Se informa además el número mínimo de barras,
    `⌈Σ l_i·n_i / L_max⌉`, que corresponde a la redacción «sobre la barra más larga».
  - **Brecha**: `desperdicio_plan − desperdicio_cota`, en puntos porcentuales.
  - **Error de dominio (FR-015)**: si `desperdicio_plan < desperdicio_cota − 1e-9` en el
    proyecto o en algún diámetro, el worker lanza un error de dominio. La versión queda en
    `error_processing` con el motivo y no se presenta como válida.
- **Razón**: la cota es una métrica, no un optimizador (Principio IV). Con el certificado
  lagrangiano, su validez no depende de que el LP converja (Principio I), y el redondeo por
  `g` la acerca al óptimo entero sin perder validez.
- **Precisión del caso límite de la spec** («una sola longitud de pieza: la cota coincide con
  el óptimo analítico»): se garantiza cuando además hay **una sola longitud de barra**. La cota
  vale `⌈n/q⌉·L`, con `q = ⌊(L + e)/(l + e)⌋`. Con varias longitudes de barra se exige solo
  `cota ≤ óptimo`, comprobado por fuerza bruta.
- **Alternativas**:
  - Cota de Martello–Toth L2: no maneja varias longitudes ni inventario limitado.
  - Modelo de arcos (Valério de Carvalho): más ajustado, pero con muchas variables con
    escala 1000.
  - Resolver el entero con branch-and-price: convertiría la cota en un optimizador, lo que
    viola el Principio IV.

## R-03 — Puerta de regresión de SC-002

- **Decisión**: volver a ejecutar las **136 combinaciones** de
  `tests/benchmarks/2026-09-13-fisico-matriz-final.jsonl` y los **12 controles** (dos archivos
  `fisico-control-*`). Se usa un nuevo modo de comparación de
  `scripts/check_cutting_container.py` en el contenedor actual, con el código cargado en
  memoria y sin reconstruir imágenes.
  - Para cada registro, `(dataset, escenario, metodo, perfil, seed, parametros_corte)`
    reproduce la ejecución.
  - Se comparan exactamente todas las claves salvo las temporales o de entorno: `duracion_segundos`,
    `timings`, `memoria_maxima_kib`, `codigo_sha256`, `python`, `plataforma`,
    `artefactos_generados` y las claves nuevas de `analisis`.
  - Salida: `tests/benchmarks/<fecha>-regresion-analisis-1.jsonl`, un archivo nuevo que nunca
    sobrescribe la línea base.
- **Complemento**: una prueba unitaria comprueba que `optimize()` devuelve las mismas barras con
  y sin umbral. Otra comprueba que `problem['hash']` no cambia al añadir el umbral a la
  configuración.
- **Razón**: la línea base guarda métricas, no planes; con la semilla, el AG es determinista
  (`optimizer.py:149`) y las métricas incluyen `por_diametro`. Repetir todo da evidencia literal
  de «0 diferencias». No es evidencia nueva para el Cap. 4 (Principio III).
- **Alternativa**: un subconjunto más una garantía estática; el usuario la descartó.
- **Efecto sobre la spec**: el supuesto «no se ejecutará de nuevo la matriz» se precisa como
  «se repite solo como verificación de regresión».

## R-04 — Umbral de desperdicio admisible (FR-001 a FR-006)

- **Decisión**:
  - **Campo**: se envía en el formulario como `umbral_desperdicio_pct`.
  - **Validación**: en `uploaded_configuration()` (`server.py:90-112`): opcional, decimal
    finito, `0 < v < 100`. Si no cumple, se devuelve 400 antes de guardar o encolar.
  - **Almacenamiento**: como clave hermana en `execution_config`, **fuera de
    `parametros_corte`**. `parameters.parse` rechaza claves desconocidas, y `parameters` forma
    parte de `problem['hash']` (`domain.py:103`).
  - **Normalización y estimación**: el umbral nunca llega a `normalize()`. `/estimate` lo acepta
    y lo ignora.
  - **Reproceso**: `POST /reprocess/<id>` acepta `umbral_desperdicio_pct`. Si la clave falta,
    se conserva el umbral vigente; si es `null`, se quita; si trae valor, se valida y se
    actualiza `uploaded_files.execution_config` antes de encolar. El snapshot del worker copia
    `**config` (`celery_worker.py:231-234`), así que cada versión guarda el umbral con el que se
    evaluó.
  - **Interfaz**: el diálogo de reproceso lo muestra precargado y editable (decisión del
    usuario).
- **Razón**: cumple FR-005: no cambia el plan, la huella ni las muestras de estimación, y no
  necesita migración.
- **Alternativa**: guardar el umbral dentro de `parametros_corte`; se descartó porque cambia la
  huella y lo rechaza el parser.

## R-05 — Cálculo de la admisibilidad y de las pérdidas

- **Decisión**:
  - **Masa por diámetro**: `masa = longitud/scale·densidad`, aplicada a `por_diametro[d]`
    (`longitud_inicial`, `sobrante_final`, `perdida_corte`, `descartado`).
  - **Desperdicio por diámetro**: `(sobrante + perdida + descartado)/longitud_inicial`, la
    misma definición de INF-012 que usa `domain.validate`. Se comprueba que la agregación por
    masa reproduce `desperdicio_porcentaje` con tolerancia de 1e-9.
  - **Estados**: `dentro` si `% ≤ umbral` (el empate cuenta como dentro), `excede` si es mayor,
    y `sin_evaluar` si no hay umbral. La diferencia se da en puntos porcentuales
    (`% − umbral`).
  - **Pérdidas**: la pérdida irrecuperable usa `perdida_irrecuperable_kg`, y el saldo
    reutilizable usa `sobrante_final_kg`, ambos ya calculados. Se añaden sus porcentajes sobre
    `masa_inicial_kg` y lo mismo por diámetro.
  - **Aprovechamiento**: `100 − desperdicio_porcentaje` (FR-019).
- **Razón**: reutiliza métricas ya validadas y no introduce una definición nueva de
  desperdicio.

## R-06 — Patrones de corte (FR-007 a FR-011)

- **Decisión**:
  - **Clave del patrón**: `(diametro, origen, longitud, tuple((grupo, longitud, cantidad) por
    corte, en orden), kerf, discarded, remaining, tuple(discard_events))`. Coincide con FR-007:
    el origen y las etapas distinguen patrones.
  - **Barras sin pérdida física**: la ruta sin campos de pérdida usa 0.
  - **Identificador**: `P-<diámetro>-<nnn>`, numerado dentro de cada diámetro por repeticiones
    descendentes y, a igual número, por la clave. Es determinista y se escribe en cada barra
    como `patron_id`.
  - **Invariantes** (comprobados en código y en pruebas): `Σ repeticiones = número de barras`;
    reconstruir piezas desde los patrones da la demanda exacta por (diámetro, grupo, longitud).
  - **Persistencia**: en `metricas.analisis.patrones` solo el resumen (total, barras, top
    corto). La lista completa va en la hoja `Patrones` del Excel, para no inflar JSONB ni la
    respuesta de `/files`.
- **Razón**: «enfoque basado en patrones de corte» y la lectura en taller (US3). Agrupar es
  determinista y no altera el plan.

## R-07 — Resumen de compra (FR-027) y verificación visible (FR-029)

- **Decisión**:
  - **Resumen de compra**: agrupa las barras raíz por `(diametro, longitud, origen)`. Cada
    grupo trae número de barras, masa (`barras·L·densidad`) y aprovechamiento (masa de piezas
    sobre masa del grupo). El origen `adicional` se lista aparte y no suma como compra.
  - **Invariante**: el total de barras por (diámetro, longitud) coincide con el plan.
  - **Verificación**: `metricas.valido`, que ya devuelve `domain.validate`, se expone en
    `to_dict` como `analisis.verificacion = {valido, comprobaciones: [demanda, diametro,
    capacidad, etapas, inventario]}`.
  - **Fallo**: si la validación falla, el worker ya marca `error_processing` con
    `status_details`; la interfaz muestra ese motivo.

## R-08 — Aviso de masa nominal NSR-10 (FR-018)

- **Decisión**: tabla constante en `backend/cutting/nominal.py`, en kg/m:

  | Barra | #3 | #4 | #5 | #6 | #7 | #8 | #9 | #10 | #11 | #14 | #18 |
  |---|---|---|---|---|---|---|---|---|---|---|---|
  | kg/m | 0,560 | 0,994 | 1,552 | 2,235 | 3,042 | 3,973 | 5,060 | 6,404 | 7,907 | 11,380 | 20,240 |

  - **Origen de los valores**: la hoja `TablaBarras` de `backend/Planilla_Cartilla.xlsx`.
    **Verificado el 2026-10-02 (T003)**: coinciden valor por valor con la NSR-10, Título C,
    Tabla C.3.5.3-2, p. C-47 (repetida en el Apéndice C-E, p. C-515). Ver la ficha
    REF-NSR10-TABLA de `docs/tesis-doc/Referencias.md`.
  - **#2 (0,25 kg/m)**: se incluye solo como referencia, porque el catálogo por defecto no
    tiene #2.
  - **Regla**: aviso si `|ρ_cartilla − ρ_nominal| / ρ_nominal > 1 %`. Un diámetro sin valor
    nominal recibe el estado `no_contrastado`.
  - **Comportamiento**: no bloquea. La densidad de la cartilla ya se deriva y valida por
    consistencia en `normalize` (`domain.py:54-66`).
- **Alternativa**: leer `TablaBarras` en tiempo de ejecución; se descartó porque acopla el
  servidor a la plantilla.

## R-09 — Ubicación del cálculo y versión del análisis

- **Decisión**:
  - **Ubicación**: una función única `cutting.analysis.analizar(problem, result, umbral)`.
    Compone `patterns`, `bound`, `nominal` y las evaluaciones, y devuelve
    `metricas['analisis']`. El worker la llama después de `optimize()` y antes de
    `report.generate()`.
  - **Versiones**: `cutting.VERSION` sigue en `secuencial-2`, porque el plan no cambia. Se añade
    `analisis.version = 'analisis-1'`.
  - **Calibración**: cambiar cualquier `cutting/*.py` cambia `environment_key()`, así que la
    calibración de tiempos se reinicia. Esto es correcto, porque `pipeline_seconds` incluye
    ahora la cota, y se documenta.
- **Archivos intocables**: `optimizer.py`, `physical.py`, `parameters.py`, `domain.normalize` y
  `domain.validate`.
- **Razón**: Principios III, IV y VI: un solo punto de entrada, sin servicios nuevos y con el
  plan aislado de las métricas.

## R-10 — Artefactos y límites (FR-006, FR-008, FR-009, FR-010)

- **Decisión**:
  - **Excel**: hojas nuevas `Patrones`, `Resumen de compra`, `Admisibilidad`, `Cota` y
    `Avisos`. `Barras` gana la columna `patron_id`, y `Metricas` gana los escalares nuevos.
  - **PDF**: secciones de resumen (desperdicio, aprovechamiento, admisibilidad, verificación,
    cota y avisos), resumen de compra y tabla de patrones. Muestra hasta 150 filas, los más
    repetidos, con el texto «se omitieron N patrones; el Excel contiene el total». La tabla de
    patrones **sustituye** la muestra actual de 150 cortes; los cortes siguen completos en el
    Excel.
  - **PNG**: titulado «Nesting lineal por patrones de corte». Dibuja hasta 60 patrones, los más
    repetidos, con la etiqueta `P-… ×n` y el pie «N patrones omitidos», con dpi 100 (los
    límites actuales).
- **Razón**: FR-009 exige que el PDF y la imagen se presenten por patrones, sin superar los
  límites vigentes (Principio VI).

## R-11 — Interfaz (FR-006, FR-020, FR-028)

- **Decisión** (vista elegida por el usuario):
  - **Nueva ruta `/archivos/[id]`**:
    - Componente cliente que llama a `GET /api/file/<id>`.
    - Secciones: verificación; admisibilidad por proyecto y por diámetro; pérdidas;
      aprovechamiento; resumen de compra; cota y brecha; avisos de masa.
    - Tabla comparativa de versiones, con perfil, tiempo, desperdicio, umbral, estado y
      verificación, más sus descargas.
  - **`/archivos`**: insignia de admisibilidad de la última versión y enlace «Ver detalle».
  - **`/subir-cartilla`**: campo opcional de umbral con el texto de FR-002, sin valor por
    defecto.
  - **Diálogo de reproceso**: el umbral precargado.
  - **Glosario del tutorial**: se añaden «cota inferior», «desperdicio admisible» y «nesting
    lineal», y se reencuadra «algoritmo genético» como técnica de IA (computación evolutiva),
    sin prometer optimalidad.
  - **Reglas visuales**: se siguen `docs/oica-redesign/AI-DESIGN-RULES.md`.

## R-12 — Cota sobre los ensayos existentes (FR-017, SC-006)

- **Decisión**: un script nuevo, `scripts/cota_ensayos.py`.
  - Por cada registro de la matriz y de los controles: lee la cartilla de `tests/data/`,
    normaliza con su `parametros_corte` (o `None` en el escenario ideal) y calcula la cota con
    `cutting.bound`.
  - Compara la cota con el `desperdicio_porcentaje` y el `por_diametro` registrados, **sin
    ejecutar el AG**.
  - La cota se calcula una vez por (dataset, escenario), porque no depende de la semilla ni
    del perfil.
  - Salida: `tests/benchmarks/<fecha>-cota-ensayos.jsonl`, un archivo nuevo.
  - Requiere scipy, así que corre en la imagen reconstruida o en un entorno temporal aprobado.

## R-13 — Fuentes para `docs/tesis-doc/Referencias.md` (FR-021, FR-022)

- **Decisión**: cada ficha tiene los ocho campos de FR-021. Estado inicial de cada fuente:

| Fuente | Término del título | Estado inicial |
|---|---|---|
| NSR-10 (Decreto 926 de 2010), Título C, tabla de barras corrugadas | en Colombia | verificar edición y páginas |
| INVIAS, Especificaciones generales, art. 640 (acero de refuerzo) | desperdicios admisibles | verificar cita literal |
| IDU, especificación de acero de refuerzo | desperdicios admisibles | pendiente de localizar |
| Res. 472 de 2017 (MinAmbiente, RCD) y su modificación vigente | desperdicios admisibles | verificar edición y páginas |
| RECIAMUC (2022), porcentaje de desperdicio de acero en vivienda | desperdicios admisibles | verificar cita literal (fuente débil) |
| Guías de APU | desperdicios admisibles | verificar (fuente débil) |
| Gilmore y Gomory (1961, 1963) | patrones de corte | verificar edición y páginas |
| Wäscher, Haußner y Schumann (2007) | patrones de corte, nesting | verificar edición y páginas |
| Benjaoran y Bhokha (2013), DOI 10.12720/joams.1.3.313-316 | distribución eficiente | verificada (ya citada en el Cap. 2) |
| Russell y Norvig, *Artificial Intelligence: A Modern Approach* | Inteligencia Artificial | verificar edición y páginas |
| Holland (1975); Goldberg (1989) | Inteligencia Artificial | verificar edición y páginas |
| Fuente de «nesting lineal» (uso industrial 1D) | nesting | pendiente de localizar |

- **Fuentes ya citadas**: las del documento (`02_Capitulo2.md:45`, `:51` y otras) se incorporan
  con su estado actual.
- **Regla**: ninguna fuente aparece en la tesis como verificada si su ficha no lo dice
  (Principio V, SC-008).
