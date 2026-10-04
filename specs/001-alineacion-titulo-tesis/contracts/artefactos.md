# Contrato de artefactos — Excel, PDF y PNG

> **Sustituido en parte por `specs/002-presentacion-resultados/contracts/` (2026-10-04).** Lo que la spec 002 cambia rige desde allí; el resto de este contrato sigue vigente.

Los genera `backend/cutting/report.py`. Antes de tocar este archivo hay que leer el último
`tests/data/<NNN>/ANALISIS_RESULTADOS.md`. Los artefactos de versiones históricas no se
regeneran.

## Excel `resultados_optimizacion.xlsx`

Las hojas existentes se conservan, con dos cambios: `Barras` gana la columna `patron_id`, y
`Metricas` gana `aprovechamiento_pct`, `umbral_desperdicio_pct`, `admisibilidad_estado`,
`perdida_irrecuperable_pct`, `reutilizable_pct`, `cota_desperdicio_pct`, `cota_ajustada`,
`brecha_pp` y `analisis_version`.

Hojas nuevas:

| Hoja | Columnas | Orden |
|---|---|---|
| `Patrones` | `patron_id, diametro, origen, longitud_m, secuencia, repeticiones, aprovechamiento_pct, perdida_corte_m, descartado_m, saldo_m` | Por diámetro y repeticiones descendentes |
| `Resumen de compra` | `diametro, longitud_m, origen, barras, masa_kg, aprovechamiento_pct` | Por diámetro, longitud y origen |
| `Admisibilidad` | `ambito, diametro, desperdicio_pct, umbral_desperdicio_pct, estado, diferencia_pp, irrecuperable_kg, irrecuperable_pct, reutilizable_kg, reutilizable_pct` | El proyecto primero |
| `Cota` | `ambito, diametro, material_m, material_kg, desperdicio_cota_pct, simple_desperdicio_pct, barras_minimas, desperdicio_plan_pct, brecha_pp, ajustada, estado` | El proyecto primero |
| `Avisos` | `diametro, masa_cartilla_kg_m, masa_nominal_kg_m, diferencia_relativa_pct, estado` | Si no hay avisos, una fila «Sin avisos» |

- **Formato de `secuencia`**: legible, por ejemplo `E1: 2×2,35 m + 1×1,10 m | E2: 3×0,80 m`.
- **Invariantes verificables desde el Excel**:
  - `Σ Patrones.repeticiones = filas de Barras`.
  - Cada `Barras.patron_id` existe en `Patrones`.
  - Por (diámetro, longitud), `Σ Resumen de compra.barras` es igual al número de barras.

## PDF `plan_corte.pdf` (WeasyPrint, A4 horizontal)

Contenido, en este orden:

1. **Verificación**: «Plan verificado: demanda, diámetro, capacidad, etapas e inventario».
2. **Desperdicio y aprovechamiento**: incluye la pérdida irrecuperable y el saldo reutilizable.
3. **Admisibilidad**: estado del proyecto, tabla por diámetro y la nota «el umbral lo define el
   usuario; no se identificó un máximo normativo».
4. **Cota inferior por patrones y brecha**: incluye la marca «no ajustada» si aplica.
5. **Avisos de masa nominal NSR-10**, con el rótulo de `nominal.ROTULO`
   («masa nominal NSR-10 (Título C, Tabla C.3.5.3-2)»).
6. **Resumen de compra.**
7. **Patrones de corte**: hasta **150** filas, los más repetidos. Si hay más, el texto «Se
   omitieron N patrones; el Excel contiene el total». Esta tabla sustituye la muestra actual
   de 150 cortes.

## PNG `grafica_cortes.png`

- **Título**: «Nesting lineal por patrones de corte» (FR-010).
- **Contenido**: hasta **60** patrones, los más repetidos. Cada uno se dibuja como una barra
  con sus piezas, la pérdida, el descarte y el saldo, y lleva la etiqueta `P-#n-nnn ×rep`.
- **Pie**: «N patrones omitidos; ver Excel» si hay más de 60.
- Se mantienen dpi 100 y el alto máximo actual.

## Inventario `inventario_final.xlsx`

Sin cambios.
