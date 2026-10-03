# Research — Presentación de resultados (spec 002)

No había marcadores [NEEDS CLARIFICATION] en el contexto técnico. Las decisiones siguientes
resuelven los puntos de diseño que la spec deja abiertos. Se basan en el código vigente
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

## R-10 — `analisis-2`

- **Decision**:
  - En `resumen_patrones`, añadir `secuencia: secuencia_legible(problem, p)` a cada patrón del
    `top`.
  - `VERSION_ANALISIS = 'analisis-2'`.
  - Ningún otro cálculo cambia.
  - Las pruebas que esperan `'analisis-1'` se actualizan.
  - La regresión no se ve afectada, porque `IGNORED` excluye `analisis`.
- **Rationale**: la pantalla necesita la secuencia, y no se puede derivar del resumen actual sin
  volver a leer las barras. Versionar el cambio lo hace trazable (Principio III).
- **Alternatives considered**: calcularla en el servidor al pedir el detalle. Obligaría a
  reconstruir los patrones desde `resultados` en cada consulta, y las versiones históricas no
  la tendrían de forma homogénea.

## R-11 — Sección «Patrones de corte» en pantalla

- **Decision**: crear `PatternsSection.tsx`, que lee `version.analisis.patrones`
  (`total`, `barras`, `top`).
  - Tabla en escritorio y tarjetas en móvil, siguiendo el patrón de `PurchaseSummary`.
  - Vista previa con `<img src={`${API_URL}/descargar-imagen/${storage_uuid}`} loading="lazy">`.
    Las etiquetas `img` ignoran `Content-Disposition: attachment`, así que no hace falta un
    endpoint nuevo.
  - Si la imagen falla (`onError`), se muestra un aviso.
  - Texto alternativo: «Nesting lineal de los N patrones más repetidos de M (B de T barras)».
  - Si `secuencia` falta (`analisis-1`), la columna muestra «no disponible».
  - Antes de implementar, leer `docs/oica-redesign/AI-DESIGN-RULES.md` y `STATE.md`.
- **Rationale**: no cambia la API y reutiliza la imagen ya generada.
- **Alternatives considered**: un endpoint de miniatura. Añade código de servidor y
  almacenamiento sin necesidad.

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
  - La pantalla trata como opcionales `analisis`, `patrones`, `top` y `secuencia`, y la imagen.
- **Rationale**: Principio III y FR-020.

## R-15 — Medición de SC-007

- **Decision**: repetir la comparación controlada de la spec 001 con
  `check_cutting_container.py --artifacts-smoke` sobre la 002, perfil balanceado, semilla 0 y
  condiciones físicas por defecto: 5 repeticiones antes y después, en la misma sesión. Se comparan
  las medianas del total. El resultado se guarda en un JSON nuevo en `tests/benchmarks/`
  (sin sobrescribir).
- **Rationale**: es el mismo arnés y la misma configuración que la línea base declarada en la spec.
