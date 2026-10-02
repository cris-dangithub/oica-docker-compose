# Data Model: Alineación de OICA con el título fijo de la tesis

**Feature**: `001-alineacion-titulo-tesis` | **Plan**: [plan.md](plan.md) |
**Research**: [research.md](research.md)

No hay migración nueva. Todo se guarda en las columnas JSONB existentes:
`uploaded_files.execution_config`, `processing_results.execution_config` y
`processing_results.metricas` (migraciones 001 y 003). Las longitudes internas son enteros
escalados por `problem['scale']`. En los contratos y artefactos se expresan en metros.

## 1. Umbral de desperdicio admisible

| Campo | Ubicación | Tipo | Regla |
|---|---|---|---|
| `umbral_desperdicio_pct` | `uploaded_files.execution_config` (vigente) y `processing_results.execution_config` (snapshot de la versión) | número o `null` | Opcional. Si existe, `0 < v < 100` y finito. Sin valor por defecto (FR-002). |

- **Huella**: nunca entra en `problem` ni en `parametros_corte`, así que no altera
  `input_hash`, la estimación ni el plan (FR-005).
- **Ciclo de vida**:
  - Al subir el archivo, se fija o queda `null`.
  - Al reprocesar, la clave ausente lo conserva, `null` lo quita y un valor lo reemplaza.
  - La versión nueva copia el valor vigente en su snapshot. Las versiones anteriores no
    cambian.

## 2. Análisis de la versión — `metricas.analisis`

Raíz añadida por `cutting.analysis.analizar`. Las versiones históricas no la tienen y se leen
como «no disponible».

```text
analisis
├── version: "analisis-1"
├── umbral_desperdicio_pct: number | null
├── verificacion: {valido: bool, comprobaciones: ["demanda","diametro","capacidad","etapas","inventario"]}
├── aprovechamiento_pct: number                  # 100 − desperdicio_porcentaje
├── perdidas
│   ├── irrecuperable: {kg, pct}                 # perdida_corte + descartado
│   ├── reutilizable: {kg, pct}                  # sobrante_final
│   └── por_diametro: {"#n": {irrecuperable:{kg,pct}, reutilizable:{kg,pct}}}
├── admisibilidad
│   ├── proyecto: EvaluacionAdmisibilidad
│   └── por_diametro: [EvaluacionAdmisibilidad & {diametro}]
├── resumen_compra: [LineaCompra]
├── patrones: {total, barras, max_repeticiones, top: [PatronResumen ≤ 10]}
├── cota: CotaInferior
└── avisos_masa: [AvisoMasa]
```

### 2.1 Evaluación de admisibilidad

| Campo | Tipo | Regla |
|---|---|---|
| `estado` | `dentro` \| `excede` \| `sin_evaluar` | `sin_evaluar` si el umbral es `null`. Si no, `dentro` cuando `desperdicio_pct ≤ umbral`. |
| `desperdicio_pct` | número | Definición de INF-012, por masa. El valor del proyecto es igual a `metricas.desperdicio_porcentaje`. |
| `diferencia_pp` | número o `null` | `desperdicio_pct − umbral`; `null` si `sin_evaluar`. |

Transiciones: no hay estados intermedios. El estado se calcula una vez por versión y es
inmutable; si cambia el umbral, se reprocesa y nace una versión nueva.

### 2.2 Línea de compra (FR-027)

| Campo | Tipo | Regla |
|---|---|---|
| `diametro` | `#n` | |
| `longitud_m` | número | Longitudes realmente usadas, no se fuerzan 6, 9 y 12. |
| `origen` | `comercial` \| `adicional` | Las barras `adicional` no se cuentan como compra. |
| `barras` | entero > 0 | Por (diámetro, longitud), la suma de los dos orígenes es igual a las barras del plan (SC-010). |
| `masa_kg` | número | `barras·longitud·densidad`. |
| `aprovechamiento_pct` | número | Masa de las piezas cortadas de esas barras sobre `masa_kg`. |

### 2.3 Patrón de corte (FR-007, FR-008)

| Campo | Tipo | Regla |
|---|---|---|
| `patron_id` | `P-<diámetro>-<nnn>` | Determinista: repeticiones descendentes y, a igual número, por la clave. |
| `diametro`, `origen`, `longitud_m` | | Forman parte de la clave. |
| `secuencia` | lista de `{grupo, longitud_m, cantidad}` en orden de corte | Es parte de la clave: las mismas piezas en otras etapas dan otro patrón. |
| `perdida_corte_m`, `descartado_m`, `saldo_m` | número | Parte de la clave; incluye los eventos de descarte. |
| `repeticiones` | entero ≥ 1 | `Σ repeticiones = barras del plan` (FR-011). |
| `aprovechamiento_pct` | número | Piezas sobre longitud de la barra. |

- **Relación**: cada barra del plan en la hoja `Barras` tiene exactamente un `patron_id`. El
  JSON de compatibilidad `resultados` (`legacy_patterns`) no cambia, para no inflar el JSONB.
- **Invariante**: expandir los patrones por sus repeticiones reproduce la demanda exacta por
  (diámetro, grupo, longitud).

### 2.4 Cota inferior (FR-012 a FR-016)

```text
cota
├── estado: "calculada" | "no_disponible"      # no_disponible: scipy ausente o error de cálculo
├── motivo: string | null                       # causa de no_disponible; null si calculada
├── ajustada: bool                              # false → «no ajustada» (FR-014)
├── proyecto: {material_kg, desperdicio_pct, simple_desperdicio_pct, brecha_pp}
└── por_diametro: [{diametro, material_m, material_kg, desperdicio_pct, ajustada,
                    simple: {material_m, desperdicio_pct, barras_minimas},
                    brecha_pp, iteraciones, columnas, segundos}]
```

Reglas:

- `desperdicio_pct(cota) ≤ desperdicio_pct(plan)` en el proyecto y en cada diámetro. Si no se
  cumple, es un **error de dominio**: la versión no se guarda como `completed` (FR-015).
- `cota simple ≤ cota por patrones`, porque ambas son válidas y la de patrones domina.
- `brecha_pp = desperdicio_plan − desperdicio_cota ≥ 0`.
- La cota nunca se usa para construir el plan (FR-016).

### 2.5 Aviso de masa nominal (FR-018)

| Campo | Tipo | Regla |
|---|---|---|
| `diametro` | `#n` | |
| `masa_cartilla_kg_m` | número | `problem['densities'][d]` |
| `masa_nominal_kg_m` | número o `null` | Tabla NSR-10 de `cutting/nominal.py`. |
| `diferencia_relativa_pct` | número o `null` | |
| `estado` | `aviso` \| `no_contrastado` | Solo se listan los diámetros con aviso (diferencia > 1 %) o sin valor nominal. |

## 3. Exposición en la API (`ProcessingResult.to_dict`)

- **`GET /files`** (lista): cada versión añade `valido`, `umbral_desperdicio_pct` y
  `admisibilidad_estado` (la del proyecto). Así la respuesta sigue siendo ligera.
- **`GET /file/<id>`** (detalle): cada versión añade `analisis` completo,
  `processing_time_seconds`, `perfil_usado` y `umbral_desperdicio_pct`. El archivo añade
  `umbral_desperdicio_pct` vigente.
- **Versión sin `analisis`**: campos `null`; la interfaz muestra «no disponible».

## 4. Entidades sin persistencia en la base de datos

- **Ficha de referencia**: vive en `docs/tesis-doc/Referencias.md`. Campos de FR-021: cita
  completa, enlace, estado de verificación, motivo, pregunta textual de origen, término del
  título, ubicación en la tesis y advertencias.
- **Registro de regresión y de cota**: JSONL nuevos en `tests/benchmarks/`. Contienen la clave
  del ensayo (`dataset`, `escenario`, `metodo`, `perfil`, `seed`), las diferencias encontradas,
  y la cota con su comparación.
