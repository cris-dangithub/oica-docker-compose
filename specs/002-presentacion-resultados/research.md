# Research — Presentación de resultados (spec 002)

No había marcadores [NEEDS CLARIFICATION] en el contexto técnico. Las decisiones siguientes
resuelven los puntos de diseño que la spec deja abiertos. La enmienda del 2026-10-04 (explorador
de patrones) retira R-10, reescribe R-11, ajusta R-14 y añade R-16 a R-19; el resto sigue vigente. Se basan en el código vigente
(`backend/cutting/report.py`, `analysis.py`, `patterns.py`, `celery_worker.py`,
`scripts/verify_sequential_result.py`, `frontend/src/components/file-detail/`).

## R-01 — Imagen de nesting dentro del PDF

- **Decision**:
  - Dibujar el nesting con una sola función, reutilizada para dos salidas:
    1. El PNG descargable (hasta 60 patrones).
    2. Las imágenes del PDF, **en bloques de 18 patrones por página** (hasta los mismos 60),
       incrustadas como `data:image/png;base64,...` al ancho útil de la página A4 horizontal.
  - Cada bloque mide unas 11 × 6,6 pulgadas, así que cabe en una página sin reducirse y las
    medidas se imprimen a escala casi real.
  - Si el dibujo falla, el PDF se genera igual, con la nota «imagen no disponible».
- **Rationale**:
  - El PDF queda autocontenido y no depende de rutas de archivo ni de `base_url`. WeasyPrint
    admite data URI de forma nativa.
  - Una sola imagen de 60 patrones (unas 19 pulgadas de alto) se reduciría a un tercio al
    encajarla en A4, y las medidas quedarían ilegibles.
- **Alternatives considered**:
  - Incrustar el PNG completo: ilegible al imprimir.
  - `<img src="file://...">` con `base_url`: depende del directorio de trabajo y es más frágil.
  - Anexar el PNG como página aparte: rompe el orden de lectura acordado.

## R-02 — Medidas escritas sobre las piezas

- **Decision**: escribir la longitud (coma decimal, sin ceros finales) centrada en cada pieza,
  solo si cabe, con letra de 5 puntos. Una pieza **cabe** si su ancho en pulgadas es al menos
  `0,55 × 5 pt / 72 × caracteres + 0,03`. Las pulgadas por metro se calculan a partir del ancho
  del eje en pulgadas y del rango del eje x (la barra más larga mostrada). El color del texto se
  elige por contraste con el color de la etapa (blanco o negro, según su luminancia).
- **Rationale**: evita textos superpuestos en piezas cortas (por ejemplo, 0,37 m en una barra de
  12 m), y la medida sigue en la tabla de patrones y en el Excel.
- **Alternatives considered**:
  - Rotular siempre: se superpone.
  - Rotular solo los cambios de longitud: confunde al taller.
  - Información emergente: no existe en un PNG.

## R-03 — Leyenda

- **Decision**: una leyenda bajo el gráfico, en varias columnas, con:
  - una entrada por etapa presente en la muestra (`E1`, `E2`…, con su color de `tab20`);
  - «Pérdida por corte» (negro), «Descarte» (rojo) y «Saldo reutilizable» (gris con trama).
  - Si una muestra tuviera más de 20 etapas, el color se repite (ciclo de `tab20`) y la leyenda lo
    indica.
  - *Ajuste en la implementación (2026-10-04)*: la revisión visual de la 002 (13 etapas) mostró
    dos problemas. `tab20` alterna oscuro y claro del mismo color, así que E3 y E4 salían en dos
    naranjas, y su par rojo se confundía con el «Descarte». Por eso las etapas usan primero los
    tonos oscuros y luego los claros, sin el par rojo: son 18 colores, que se repiten desde E19 (el
    pie lo indica). La leyenda va en filas de hasta 12 entradas, bajo el rótulo del eje, con
    1,0 pulgadas de margen inferior. La imagen de 60 patrones queda en 2.200 × 3.890 px (8,56 MP),
    dentro del límite de 9 MP (R-04).
- **Rationale**: hoy el eje x describe los colores en una sola línea de texto que no dice qué
  color es cada etapa.
- **Alternatives considered**: una paleta continua con barra de color. Se descarta porque las
  etapas son categorías, no una magnitud.

## R-04 — Resolución y tamaño acotado

- **Decision**:
  - Resolución de 200 dpi.
  - Ancho de 11 pulgadas, el ancho útil de A4 horizontal (unas 10,5 pulgadas) más un margen.
  - Alto: 0,3 pulgadas por patrón, más 1,2 de título, leyenda y cobertura.
  - Tope de 60 patrones en el PNG y de 18 por bloque en el PDF.
  - Peor caso del PNG: 11 × 19,2 pulgadas → 2.200 × 3.840 píxeles, unos 8,4 MP.
  - **Nuevo límite**: 9 MP, en lugar de 3 MP. Se actualiza la aserción de
    `test_artefactos_visuales_acotados`.
- **Rationale**:
  - El límite sigue siendo **fijo e independiente del número de barras**, que es lo que exigió
    BUG-005: 9 MP en RGBA son unos 36 MB en memoria, frente a los 26 GB del fallo original.
  - Las piezas son más altas y las medidas legibles.
  - La lectura impresa la garantiza el PDF (R-01), y el PNG se lee en pantalla al 100 %.
- **Alternatives considered**:
  - Mantener 3 MP: obliga a unos 110 dpi con 60 patrones, el mismo problema de hoy.
  - Reducir el PNG a 25 patrones: pierde cobertura.
  - 300 dpi: duplica el tamaño sin beneficio.
  - SVG: no se previsualiza igual en todos los visores.

## R-05 — Coma decimal

- **Decision**: crear el ayudante `numero(valor, decimales)` en `report.py`, con punto de miles y
  coma decimal (por ejemplo, `152.039,57`).
  - Se usa en textos del PDF y del PNG: dos decimales en general y tres en la cota y la brecha.
  - En el Excel, los valores siguen siendo **numéricos**: el usuario puede operar con ellos, y
    Excel los muestra según su configuración regional. Solo cambian los nombres y las unidades.
- **Rationale**: convertir los números del Excel en texto con coma impediría sumarlos o graficarlos.
- **Alternatives considered**: `locale.setlocale('es_CO')`. Se descarta porque depende de los
  *locales* instalados en la imagen Alpine, que no están garantizados.

## R-06 — Hoja «Resumen» y totales de compra

- **Decision**: una sola hoja con dos bloques.
  1. Desde la fila 1, la tabla `indicador | valor | unidad`, con nombres legibles (contrato §1.1).
  2. Una fila en blanco, el título «Totales de compra» y la tabla
     `diametro | origen | barras | masa_kg`, construida a partir de `analisis['resumen_compra']`:
     - una fila por diámetro y origen;
     - al final, «Total comprado» (solo origen comercial) y, si existe, «Total tomado del
       inventario».
  - La hoja «Resumen de compra» no cambia (sin filas de total).
- **Rationale**:
  - El auditor (`verify_sequential_result.py`, líneas 90–99) suma «Resumen de compra» fila por
    fila y la compara con las barras: no hay que tocarlo.
  - Al usuario le basta abrir la primera hoja (SC-001).
- **Alternatives considered**:
  - Filas «TOTAL» en «Resumen de compra»: rompen el auditor y cualquier suma del usuario.
  - Una hoja «Totales» aparte: el usuario aprobó ponerlos en «Resumen».
- **Consecuencia para las pruebas**: la hoja «Resumen» se lee con `header=0` y `nrows` igual al
  número de indicadores. Los totales se localizan por el título del bloque.

## R-07 — Hoja «Trazabilidad»

- **Decision**: tabla `dato | valor` con estos campos:
  - De la línea base: `valido`, `escala_longitudes`, `motor`, `input_hash`, `seed`, `perfil`,
    `metodo` y `duracion_segundos`.
  - Del análisis: `analisis_version`, `analisis_segundos` y `cota_ajustada`.
  - Además, `parametros_resueltos` con el JSON exacto de `problem['resolved_parameters']` (antes
    estaba en «Parametros»), para conservar la reproducibilidad exacta ahora que «Parámetros» es
    legible.
  - `artifacts_seconds` y `pipeline_seconds` no existen cuando se genera el Excel: siguen
    guardados en la base de datos y se informan en «Versiones».
  - Los escalares que no pasan a «Resumen» van aquí, para que ningún dato de «Metricas» se pierda.
- **Rationale**: Principio III; nada de «Metricas» desaparece, solo se reubica.
- **Alternatives considered**: ocultar las columnas técnicas en «Resumen». Es peor para un usuario
  no técnico.

## R-08 — Hoja «Parámetros» legible

- **Decision**: tabla `condicion | valor | referencia`, a partir de `resolved_parameters` y
  `parameters.REFERENCES`:

  | condicion | valor (ejemplos) | referencia |
  |---|---|---|
  | Pérdida por corte | «Disco, 1 mm» / «Cizalla, 0 mm» / «Desactivada» | URL o nota de `REFERENCES[proceso]` |
  | Mínimo reutilizable | «Automático: menor longitud demandada por diámetro» / «Manual común: 0,5 m» / «Desactivado» | DOI de `REFERENCES['automatico']` si es automático |
  | Mínimo por diámetro | una fila por diámetro: «#3: 0,37 m» | — |
  | Momento del descarte | «Inmediato, tras cada corte» / «Al cerrar cada etapa» | — |
  | Pérdida efectiva aplicada | «1 mm» | — |

- **Rationale**: el JSON crudo era ilegible y mezclaba enlaces.
- **Alternatives considered**: conservar el JSON aquí. Pasa a «Trazabilidad» (R-07).

## R-09 — Versión, perfil y fecha en el encabezado del PDF

- **Decision**:
  - En `celery_worker.py`, calcular `version` (la misma consulta de `latest`) **antes** de llamar
    a `generate()` y pasarla como argumento opcional `version`.
  - El perfil sale de `metrics['perfil']`.
  - La fecha es la de generación, en hora de Colombia (UTC−5 fijo, sin horario de verano), con
    `datetime.now(timezone(timedelta(hours=-5)))`, rotulada «hora de Colombia».
  - `generate()` acepta `version=None`: el arnés `--artifacts-smoke` y las pruebas siguen
    funcionando y muestran «versión no asignada».
- **Rationale**:
  - El worker corre con concurrencia 1, así que mover la consulta no crea condiciones de carrera
    nuevas.
  - UTC−5 fijo evita depender de `tzdata` en Alpine.
- **Alternatives considered**:
  - `ZoneInfo('America/Bogota')`: requiere `tzdata`, que podría faltar en la imagen.
  - Omitir la versión: el usuario pidió verla.

## R-10 — `analisis-2` *(retirada en la enmienda 2026-10-04)*

- **Estado**: **retirada**. La sustituye R-16.
- **Decisión original (2026-10-03)**: añadir `secuencia` al `top` de `resumen_patrones` y pasar a
  `VERSION_ANALISIS = 'analisis-2'`. Se descartó la alternativa de «calcularla en el servidor al
  pedir el detalle» porque obligaba a reconstruir los patrones en cada consulta y las versiones
  históricas no la tendrían de forma homogénea.
- **Por qué se retira**: el explorador (US2) necesita **todos** los patrones, con sus pedidos y
  sus barras, no solo la secuencia de los 10 primeros. La reconstrucción desde `resultados`
  cuesta unos 0,5 s con la cartilla 002 (R-18). Además, funciona igual con las versiones
  `secuencial-2` ya procesadas, que es más homogéneo que `analisis-2`, el cual solo cubriría las
  versiones nuevas. Con eso desaparecen las dos razones del descarte original.
- **Consecuencia**: `analysis.py` no cambia, `VERSION_ANALISIS` sigue en `analisis-1` y las
  pruebas que esperan `'analisis-1'` siguen igual.

## R-11 — Sección «Patrones de corte» en pantalla *(reescrita en la enmienda 2026-10-04)*

- **Decision**: la sección se convierte en el **explorador de patrones**, en
  `frontend/src/components/file-detail/patterns/` y montado en `FileDetail.tsx` entre
  `PurchaseSummary` y `QualitySection`.
  - Pide los datos al endpoint de R-16 (`contracts/api-patrones.md`) **solo cuando la sección
    entra en pantalla o el usuario la abre**, no al cargar el detalle, para no penalizar a quien
    no la usa.
  - Filtros, orden y cobertura se calculan **en el navegador** sobre la respuesta, que es pequeña
    (R-18). No hay más peticiones al filtrar.
  - El dibujo sigue R-17; el detalle del patrón y los rangos de barras siguen R-18 y R-19.
  - La imagen PNG **ya no** se muestra como vista previa. Su descarga sigue en los enlaces de
    `VersionsTable.tsx` (`/descargar-imagen/<uuid>`).
  - Antes de implementar, leer `docs/oica-redesign/AI-DESIGN-RULES.md` y `STATE.md`.
- **Rationale**: una sola fuente para la tabla, el dibujo y el detalle evita incoherencias entre
  ellos. El PNG es una selección fija de 60 patrones y no sirve para explorar.
- **Alternatives considered**:
  - Mantener la tabla de los 10 más repetidos y la vista previa del PNG junto al explorador:
    repite información (decisión del usuario, enmienda).
  - Filtrar en el servidor: añade peticiones y latencia sin necesidad, con unos 136 patrones.

## R-12 — Totales de compra en pantalla

- **Decision**: calcularlos en `PurchaseSummary.tsx` a partir de `lineas`: total por diámetro y
  total general de compra (origen comercial), y un total aparte del inventario adicional.
- **Rationale**: es la misma regla que en el Excel, sin cambiar la API.
- **Alternatives considered**: enviarlos desde el backend. Duplica datos en el JSON guardado.

## R-13 — Cobertura

- **Decision**: definir `cobertura(patrones_mostrados, patrones_totales, total_barras)`, que
  devuelve `(n, m, b, t, pct)` con `b = Σ repeticiones mostradas` y `t = len(result['bars'])`.
  - Se usa en el PDF (límite de 150) y en el PNG (límite de 60).
  - Texto: «Se muestran N de M patrones, que cubren B de T barras (x %)».
- **Rationale**: SC-003. Al venir de los mismos patrones que se dibujan, la cobertura no puede
  desalinearse de lo que se muestra.

## R-14 — Versiones históricas

- **Decision**:
  - Los artefactos solo se generan para versiones nuevas; los ya guardados no se regeneran.
  - La pantalla trata como opcionales `analisis` y sus partes.
  - *(Enmienda)* El explorador no depende de `analisis`: reconstruye los patrones de cualquier
    versión con `resultados` reconstruibles (R-16), y para las demás responde «no disponible».
- **Rationale**: Principio III y FR-020.

## R-15 — Medición de SC-007

- **Decision**: repetir la comparación controlada de la spec 001 con
  `check_cutting_container.py --artifacts-smoke` sobre la 002, perfil balanceado, semilla 0 y
  condiciones físicas por defecto: 5 repeticiones antes y después, en la misma sesión. Se comparan
  las medianas del total. El resultado se guarda en un JSON nuevo en `tests/benchmarks/`
  (sin sobrescribir).
- **Rationale**: es el mismo arnés y la misma configuración que la línea base declarada en la spec.

## R-16 — Fuente de datos del explorador: reconstrucción desde `resultados` *(enmienda)*

- **Decision**: crear un módulo puro `backend/cutting/vista_patrones.py`, que no toca la base ni
  los archivos.
  - `barras_desde_resultados(resultados, escala)` rehace las barras del motor a partir de
    `ProcessingResult.resultados`, que escribe `legacy_patterns` (`report.py:14`). Usa estos
    campos:
    - `bar_id`, `diametro` y `origen`.
    - `cuts` = `trazabilidad_cortes`: enteros escalados con `row_id`, `pedido`, `grupo`,
      `longitud` y `cantidad`.
    - `discard_events` = `descartes_fin_etapa`.
    - `longitud`, `kerf`, `discarded` y `remaining` = `round(valor_m × escala)` de
      `barra_origen_longitud`, `perdida_corte_m`, `descartado_m` y `desperdicio_resultante`.
    - La escala es `metricas.escala_longitudes` (1000 en las versiones actuales).
  - Si falta la escala o algún registro no trae `trazabilidad_cortes` (motor histórico o
    `secuencial-1`), devuelve `None` y la vista responde `disponible: false`.
  - `vista(resultados, metricas)` llama a `patterns.agrupar` y a `report.patrones_rows`, el mismo
    código que genera la hoja «Patrones». Así, los identificadores, las repeticiones, la
    secuencia, el aprovechamiento, la pérdida, el descarte y el saldo coinciden por construcción
    (FR-025, SC-010). Luego añade las piezas con sus pedidos (R-19) y los rangos de barras (R-18).
  - **Comprobaciones** antes de responder. Si alguna falla, se lanza un error de dominio y la
    ruta responde 500 con «Patrones inconsistentes».
    - `Σ repeticiones = número de registros de resultados`.
    - Si la versión tiene `analisis.patrones`, coinciden `total`, `barras` y los `patron_id` con
      las repeticiones del `top`.
- **Evidencia** (medición exploratoria de solo lectura en el stack local, 2026-10-04, sin escribir
  nada):
  - Versión `secuencial-2` de la cartilla 002: 13.955 barras → **136 patrones**, como en la
    línea base.
  - Su segunda versión: 13.511 barras y 133 patrones.
  - Cartilla pequeña: 35 barras y 13 patrones.
  - Las versiones `secuencial-1` y las del motor histórico no traen `trazabilidad_cortes`:
    quedan como «no disponible».
  - Las versiones locales son anteriores a la spec 001 (sin `analisis`), así que la comprobación
    contra el `top` se valida en las pruebas, no en esta medición.
- **Rationale**:
  - Sin migraciones, sin volver a ejecutar el AG (Principio III) y sin regenerar artefactos.
  - Cubre también las versiones `secuencial-2` ya procesadas.
  - El redondeo `round(x × escala)` recupera los enteros exactos, porque los valores se
    guardaron como `entero / escala`.
- **Alternatives considered**:
  - Guardar un `patrones.json` por versión al generar los artefactos: solo cubre las versiones
    nuevas y añade un archivo más.
  - Guardar todos los patrones en `metricas.analisis`: hace crecer el JSONB, y
    `analysis.patrones_de` documenta que la lista completa no se guarda.
  - Volver a ejecutar `normalize` con `cartilla`: es innecesario, porque las barras ya traen la
    demanda atendida.

## R-17 — Dibujo y accesibilidad del explorador *(enmienda)*

- **Decision**:
  - **Sin librerías.** Cada patrón se dibuja como una fila con tramos HTML (`div` en flex con
    ancho en %), el mismo recurso del diagrama de `frontend/src/app/page.tsx`. Para unos 136
    patrones con unos 10 tramos cada uno son unos 1.500 nodos.
  - **Escala común** (aclaración): `ancho = longitud / escala_m`, donde `escala_m` es la barra
    más larga del plan, enviada por el endpoint. La escala no cambia al filtrar.
  - **Contenido de cada fila**: las piezas en orden de corte, con una separación de 1 px que
    representa la pérdida por corte (1 mm en 12 m no se vería a escala). Después, un tramo de
    descarte y otro de saldo.
  - **Rótulos**: la medida va dentro de la pieza solo si su ancho calculado en px supera el del
    texto; un `ResizeObserver` sobre el contenedor da el ancho.
  - **Colores**: no hay una paleta categórica de etapas en el sistema visual (los tokens `data/*`
    son `primary`, `efficient`, `warning`, `grid` y `remaining-material`).
    - Se añaden los tokens semánticos `color/data/stage-1` … `stage-6`, alias de primitivos
      existentes (cobalto, teal, ámbar y neutral), que se repiten en ciclo a partir de la
      etapa 7.
    - Se registran en `docs/oica-redesign/DESIGN-SYSTEM.md` (reglas 1, 5 y 13).
    - El descarte usa `status/error` y el saldo, `data/remaining-material`.
    - El color nunca es el único canal: la leyenda, el `aria-label` de la fila y el detalle
      nombran la etapa como «E1», «E2»….
  - **Interacción** (reglas 6 a 8): cada fila es un `<button aria-expanded aria-controls>` con
    `aria-label`, por ejemplo «P-#4-001, barra de 12 m, 230 repeticiones, aprovechamiento
    97,5 %». Al activarlo con Enter o Espacio, el detalle se despliega debajo, en el mismo lugar
    en escritorio y en móvil. Hay **una parada de tabulación por patrón**, no una por pieza.
  - El dibujo lleva `aria-hidden`: su información está en el `aria-label` y en el detalle. Un
    tooltip al pasar el ratón sobre una pieza es solo una mejora, nunca la única vía.
  - **Móvil** (reglas 9 y 10): la fila se recompone. El identificador y las repeticiones van
    arriba y la barra ocupa todo el ancho debajo, sin tablas ni desplazamiento horizontal.
  - **Filtros**: los controles de `components/ui/form-controls.tsx`. Diámetro, etapa y origen
    son `select`. El pedido es un `input` con `<datalist>` que sugiere los pedidos de la versión
    (aclaración).
  - El orden se elige con un `select` (aclaración): «Como el Excel», «Repeticiones»,
    «Aprovechamiento» o «Saldo».
- **Rationale**: el patrón ya existe en el proyecto, sin dependencias nuevas que obliguen a
  reconstruir la imagen del frontend con más paquetes, y con un modelo de teclado simple y
  verificable con axe.
- **Alternatives considered**:
  - SVG por fila: obliga a medir el texto a mano y no aporta nada para rectángulos alineados.
  - Recharts o d3: dependencias nuevas sin necesidad (constitución, Principio VI).
  - Un panel lateral fijo para el detalle: no se recompone bien en móvil.

## R-18 — Rendimiento, tamaño de la respuesta y caché *(enmienda)*

- **Decision**:
  - **Servidor**:
    - La ruta carga solo `resultados` y `metricas` de la versión (`load_only`), sin `cartilla`.
    - Responde un JSON compacto: sin listas por pieza ni por barra; las barras van agrupadas en
      **rangos** de identificadores consecutivos.
    - Caché en memoria de proceso, `functools.lru_cache(maxsize=8)`, con clave `storage_uuid`:
      una versión guardada no cambia, así que la caché no puede quedar obsoleta.
  - **Navegador**:
    - Una sola petición por versión, diferida (R-11).
    - Filtros y orden en memoria.
    - La lista de patrones se pinta por tramos de 50 con «Mostrar más patrones».
    - Los rangos de barras del detalle se pintan por tramos de 100 con «Ver más» (aclaración,
      FR-028).
- **Evidencia** (misma medición de R-16, versión de la 002, en el contenedor del backend):
  - Lectura de `resultados` (12,5 MB de JSON) desde PostgreSQL: **0,33 s** (3 repeticiones).
  - `agrupar`: 0,05–0,13 s.
  - Pedidos por pieza: 0,01–0,02 s.
  - Total: unos 0,5 s, por debajo de los 2 s de SC-009.
  - Las 13.955 barras se agrupan en **145 rangos**; hay 275 pares pieza-pedido y 137 pedidos.
    La respuesta estimada es de decenas de KB.
- **Riesgo declarado**: el backend corre con gevent y el `json.loads` de 12,5 MB ocupa la CPU
  unos 0,3 s, tiempo en el que no atiende otras peticiones. Para una app de un solo usuario
  activo es aceptable, y la caché lo evita en las consultas repetidas. Si la VPS mostrara
  bloqueos, la alternativa es precalcular la vista en el worker (fuera de alcance).
- **Alternatives considered**:
  - Redis como caché: más piezas para unos 0,5 s.
  - Virtualizar la lista: innecesario con tramos de 50 y unos 10 nodos por fila.
  - Paginar en el servidor: complica los filtros combinados sin ganar nada con unos 136
    patrones.

## R-19 — Pedidos por pieza del patrón *(enmienda)*

- **Decision**:
  - Dentro de un patrón, todas sus barras comparten la misma secuencia de cortes, porque
    `clave()` incluye `(grupo, longitud, cantidad)` en orden. Así, el corte *i* de cada barra
    corresponde a la pieza *i* del patrón.
  - Por cada pieza *i* se suman, en todas las barras del patrón,
    `cuts[i].cantidad` por `cuts[i].pedido`. El resultado es una lista `pedidos` de la forma
    `[{pedido, piezas}]`, ordenada por pedido.
  - El índice global de pedidos de la versión, `[{pedido, piezas}]`, se obtiene igual sobre
    todas las barras.
  - Con un pedido filtrado, el aporte de un patrón es la suma de `piezas` de ese pedido en sus
    piezas (FR-027).
- **Invariantes** (se prueban):
  - Para cada pieza *i*, `Σ pedidos.piezas = cantidad × repeticiones`.
  - Para cada pedido, `Σ aportes de los patrones = piezas del índice = Σ Cantidad` de las filas
    de la cartilla con ese «N° Orden».
- **Rationale**: los pedidos ya viajan en cada corte (`optimizer.py:131`, `physical.py:117`). La
  agrupación los pierde (`patterns.py:13`) y aquí solo se recuperan, sin cambiar la identidad
  del patrón.
- **Alternatives considered**: incluir el pedido en la clave del patrón. Cambiaría los
  identificadores y la hoja «Patrones», y rompería la coherencia con la línea base de la spec 001.

## R-20 — Estándar numérico único *(enmienda 2, 2026-10-04)*

- **Contexto**: la revisión del usuario encontró formatos mezclados en la misma app:
  - «5.154% en masa» en la lista de proyectos, con punto decimal y sin espacio;
  - la pantalla con 3 decimales en los porcentajes y el PDF con 2;
  - kg con 3 decimales en pantalla y con 2 en el PDF;
  - mínimos por diámetro mostrados tal como llegan de la API («0.37 m»);
  - repeticiones sin punto de miles en el PNG («×2199»);
  - campos `type="number"` cuyo separador depende del idioma del navegador.
- **Decision**: una sola regla, implementada una vez por lado y reutilizada en todas partes.
  - **Frontend**: `decimal(valor, d)` (decimales fijos), `entero(valor)`, `pct`, `pp` y `kg` en
    `components/file-detail/types.ts`, y `numero`/`metros` (sin ceros finales) en
    `file-detail/patterns/filtros.ts`. Todo componente que muestre cifras los usa; se prohíben
    `toFixed`/`toLocaleString` sueltos para texto visible. Los decimales siguen FR-033 (los
    mismos del PDF).
  - **Entradas decimales**: `type="text"` con `inputMode="decimal"` (teclado numérico en el
    móvil). El texto se conserva tal cual mientras se edita y se interpreta con
    `leerDecimal(texto)`, que acepta coma o punto y rechaza lo demás. Al enviar a la API se manda
    con punto. El backend ya acepta ambos (`domain.decimal` y `server.parse_umbral`), así que la
    API no cambia.
  - **Backend**: `cutting/formato.py` concentra `numero`, `con_signo` y `metros`. Lo usan
    `report.py` (PDF, PNG y textos del Excel) y los mensajes de error de dominio de
    `analysis.py`, sin importaciones circulares.
  - **Excel**: las celdas numéricas siguen siendo números (FR-035). Solo los textos legibles
    («Parámetros», «secuencia», estados) usan el formato.
  - **Excepción declarada**: los mensajes de validación de `domain.normalize` repiten el valor tal
    como lo escribió el usuario («Número inválido: 0,5,1»). `normalize` está protegido por la
    constitución (Principio III), y repetir la entrada literal es lo correcto para que el usuario
    la encuentre.
- **Rationale**: el usuario es colombiano y las normas de presentación de cifras en español usan
  coma decimal. Un solo juego de ayudantes por lado evita que reaparezcan formatos sueltos, y
  fijar los decimales por tipo hace que la pantalla y el PDF digan lo mismo.
- **Alternatives considered**:
  - `Intl.NumberFormat('es-CO')`: no agrupa los números de 4 cifras («3974») y su salida depende
    de los datos ICU del entorno (riesgo de discrepancia entre servidor y navegador).
  - `locale` de Python: depende de los *locales* instalados en la imagen Alpine (R-05).
  - Mantener `type="number"`: el separador aceptado depende del navegador y del idioma del
    sistema (FR-034).
