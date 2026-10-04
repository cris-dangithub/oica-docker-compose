# Data Model — Presentación de resultados (spec 002)

Esta funcionalidad **no añade tablas ni migraciones** y, tras la enmienda del 2026-10-04,
**no guarda nada nuevo**. Las estructuras siguientes se **derivan** del plan ya validado, de
`metricas.analisis` o de `ProcessingResult.resultados`.

## 1. `metricas.analisis` sin cambios *(enmienda 2026-10-04)*

- Se retira el cambio a `analisis-2` (research R-10). `analisis.version` sigue en `analisis-1` y
  `analisis.patrones.top[]` conserva sus campos, sin `secuencia`.
- La secuencia y el resto de los datos de cada patrón se obtienen bajo demanda con la vista de
  patrones (§8), a partir de `resultados`.
- **Compatibilidad**: las versiones sin `analisis` siguen mostrando «no disponible» en las
  secciones que dependen de él. El explorador depende de `resultados`, no de `analisis`.

## 2. Indicador del resumen (hoja «Resumen» y PDF)

| Campo | Tipo | Origen |
|---|---|---|
| `indicador` | texto legible | Contrato artefactos §1.1 |
| `valor` | número, texto o «no disponible» | `metrics` y `analisis` |
| `unidad` | `piezas`, `barras`, `kg`, `%`, `pp` o vacío | Contrato artefactos §1.1 |

Regla: un indicador sin dato (versión sin umbral, cota no calculada) muestra «no disponible» o
«sin evaluar», nunca una celda vacía ambigua.

## 3. Totales de compra

Derivados de `analisis.resumen_compra` (líneas `diametro, longitud_m, origen, barras, masa_kg`).

| Campo | Regla |
|---|---|
| `diametro` | Agrupa por diámetro; filas finales «Total comprado» y «Total tomado del inventario» |
| `origen` | `Compra` (comercial) o `Inventario adicional` |
| `barras` | Σ `barras` del grupo |
| `masa_kg` | Σ `masa_kg` del grupo |

**Invariantes**:
- `Total comprado.barras` = Σ barras de las líneas comerciales.
- `Total comprado.barras + Total inventario.barras` = número de barras del plan.
- Lo mismo para la masa.

## 4. Dato de trazabilidad (hoja «Trazabilidad»)

| `dato` | Origen |
|---|---|
| `valido`, `escala_longitudes` | `metrics` (validador) |
| `motor`, `input_hash`, `seed`, `perfil`, `metodo`, `duracion_segundos` | `metrics` (optimizador) |
| `analisis_version`, `analisis_segundos`, `cota_ajustada` | `metrics.analisis` y el worker |
| `parametros_resueltos` | JSON exacto de `problem['resolved_parameters']` |
| Cualquier otro escalar de `metrics` que no esté en «Resumen» | `metrics` |

**Invariante**: todo escalar que hoy se escribe en «Metricas» aparece en «Resumen» o en
«Trazabilidad».

## 5. Condición de corte legible (hoja «Parámetros» y sección técnica del PDF)

| Campo | Regla |
|---|---|
| `condicion` | «Pérdida por corte», «Mínimo reutilizable», «Mínimo por diámetro (#n)», «Momento del descarte», «Pérdida efectiva aplicada» |
| `valor` | Texto legible con coma decimal (research R-08) |
| `referencia` | URL, DOI o nota de `parameters.REFERENCES`, o vacío |

## 6. Cobertura (PDF y PNG)

| Campo | Regla |
|---|---|
| `n` | Patrones mostrados (≤ 150 en el PDF, ≤ 60 en el PNG) |
| `m` | Patrones totales del plan |
| `b` | Σ repeticiones de los patrones mostrados |
| `t` | Barras del plan (`len(result['bars'])`) |
| `pct` | `100 × b / t` |

**Invariante**: `b ≤ t`; si `n = m`, entonces `b = t`.

## 7. Encabezado del PDF

| Campo | Origen |
|---|---|
| Proyecto | `title` (nombre del archivo cargado), escapado para HTML |
| Versión | argumento `version` de `generate()`; «no asignada» si falta |
| Perfil | `metrics['perfil']`, con etiqueta legible (Rápido, Balanceado, Profundo) |
| Fecha | Momento de generación, hora de Colombia (UTC−5) |

## 8. Vista de patrones (explorador; enmienda 2026-10-04)

Se deriva bajo demanda de `ProcessingResult.resultados` y `metricas` (research R-16). No se
guarda. Su formato JSON está en [contracts/api-patrones.md](contracts/api-patrones.md).

### 8.1 Barra reconstruida (interna, `cutting.vista_patrones`)

| Campo del motor | Origen en `resultados[i]` |
|---|---|
| `bar_id`, `diametro`, `origen` | iguales |
| `longitud` | `round(barra_origen_longitud × escala)` |
| `cuts` | `trazabilidad_cortes` (enteros escalados; `row_id`, `pedido`, `grupo`, `longitud`, `cantidad`) |
| `kerf` | `round(perdida_corte_m × escala)` |
| `discarded` | `round(descartado_m × escala)` |
| `remaining` | `round(desperdicio_resultante × escala)` |
| `discard_events` | `descartes_fin_etapa` |

`escala` = `metricas.escala_longitudes`. Si falta la escala, o si algún registro no trae
`trazabilidad_cortes`, la vista no está disponible.

### 8.2 Entidades de la vista

| Entidad | Campos | Regla |
|---|---|---|
| Patrón explorable | los de `report.patrones_rows`, más `etapas`, `piezas` y `barras` | Coincide campo a campo con la hoja «Patrones» |
| Pieza del patrón | `etapa`, `longitud_m`, `cantidad` y `pedidos[]` | Una por elemento de la secuencia, en orden de corte |
| Pedido-piezas | `pedido`, `piezas` | Agregado sobre las barras del patrón (R-19) |
| Rango de barras | `desde`, `hasta`, `n` | Números consecutivos de `#d:n` del mismo diámetro |
| Índice de pedidos | `pedido`, `piezas` | Agregado sobre todas las barras |
| Filtro | `diametro?`, `etapa?`, `origen?`, `pedido?`, más el orden | Se aplica en el navegador; combina con Y |
| Cobertura del filtro | `n`, `m`, `b`, `t`, `pct` | `b = Σ repeticiones` de los patrones filtrados; `t = totales.barras` |

### 8.3 Invariantes (se prueban en el backend)

- `Σ patrones.repeticiones = totales.barras = len(resultados)`.
- Para cada patrón: `barras.total = repeticiones = Σ rangos.n`.
- Para cada pieza: `Σ pedidos.piezas = cantidad × repeticiones`.
- Para cada pedido del índice: `piezas = Σ` de sus aportes en todos los patrones `= Σ Cantidad` de
  las filas de la cartilla con ese «N° Orden».
- Los identificadores, las repeticiones, la secuencia y las métricas de la vista coinciden con la
  hoja «Patrones» del Excel de la misma versión. Además, la reconstrucción desde `resultados`
  coincide con `patterns.agrupar` sobre el resultado original del optimizador.
- Si la versión tiene `analisis.patrones`, coinciden `total`, `barras` y las repeticiones de cada
  `patron_id` del `top`.
- `escala_m = max(longitud_m)` de todos los patrones; no depende de los filtros.
- Cobertura: `b ≤ t`; sin filtros, `n = m` y `b = t`.

### 8.4 Estados de la sección en pantalla

`inactiva` (aún no visible) → `cargando` → `lista` | `no_disponible` (respuesta con
`disponible: false`) | `error` (red o 500, con «Reintentar» → `cargando`).
