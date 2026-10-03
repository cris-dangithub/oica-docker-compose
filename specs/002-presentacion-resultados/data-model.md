# Data Model — Presentación de resultados (spec 002)

Esta funcionalidad **no añade tablas ni migraciones**. Las estructuras siguientes se **derivan**
del plan ya validado y de `metricas.analisis`. La única que se guarda es el campo `secuencia` del
resumen de patrones (`analisis-2`).

## 1. Cambio persistido: `metricas.analisis` (`analisis-2`)

```text
analisis.version              "analisis-2"   (antes "analisis-1")
analisis.patrones.top[]       + secuencia: str   (formato de patterns.secuencia_legible)
                                 p. ej. «E1: 2×4,2 m + 1×3,5 m | E3: 1×1,1 m»
```

- El resto de `analisis` es idéntico a `analisis-1`.
- **Compatibilidad**: en las versiones con `analisis-1`, `secuencia` no existe y la pantalla
  muestra «no disponible». En las versiones sin `analisis`, la sección completa queda «no
  disponible».

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
