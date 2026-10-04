# Contrato de artefactos — Excel, PDF, PNG e inventario (spec 002)

Sustituye a `specs/001-alineacion-titulo-tesis/contracts/artefactos.md` en lo que aquí se
indica; lo no mencionado sigue igual. Los genera `backend/cutting/report.py`. Antes de tocarlo
hay que leer el último `tests/data/<NNN>/ANALISIS_RESULTADOS.md`. Los artefactos de versiones
históricas no se regeneran.

## 1. Excel `resultados_optimizacion.xlsx`

**Orden de hojas (FR-001)**:

1. Resumen
2. Resumen de compra
3. Patrones
4. Cortes
5. Barras
6. Descartados
7. Admisibilidad
8. Cota
9. Avisos
10. Inventario
11. Inventario excluido
12. Parámetros
13. Trazabilidad

La hoja «Metricas» deja de generarse.

### 1.1 «Resumen» (FR-002, FR-003)

**Bloque 1**: columnas `indicador | valor | unidad`, en este orden.

| indicador | unidad | origen del valor |
|---|---|---|
| Estado de verificación | | «Plan verificado: demanda, diámetro, capacidad, etapas e inventario» o el motivo |
| Piezas producidas | piezas | `metrics.piezas` |
| Barras utilizadas | barras | `metrics.barras` |
| Barras compradas | barras | Σ líneas comerciales de `resumen_compra` |
| Barras tomadas del inventario | barras | Σ líneas adicionales de `resumen_compra` |
| Patrones de corte distintos | patrones | `analisis.patrones.total` |
| Masa de barras utilizadas | kg | `metrics.masa_inicial_kg` |
| Masa incorporada en piezas | kg | `metrics.piezas_kg` |
| Pérdida por corte | kg | `metrics.perdida_corte_kg` |
| Descartado (retazos bajo el mínimo) | kg | `metrics.descartado_kg` |
| Pérdida irrecuperable | kg | `analisis.perdidas.irrecuperable.kg` |
| Pérdida irrecuperable | % | `analisis.perdidas.irrecuperable.pct` |
| Saldo reutilizable final | kg | `analisis.perdidas.reutilizable.kg` |
| Saldo reutilizable final | % | `analisis.perdidas.reutilizable.pct` |
| Desperdicio en masa | % | `metrics.desperdicio_porcentaje` |
| Aprovechamiento | % | `analisis.aprovechamiento_pct` |
| Desperdicio admisible definido por el usuario | % | `analisis.umbral_desperdicio_pct` o «sin umbral» |
| Estado de admisibilidad | | Dentro de lo admisible, Excede o Sin evaluar |
| Diferencia frente al umbral | pp | `admisibilidad.proyecto.diferencia_pp` o «no disponible» |
| Cota inferior por patrones | % | `cota.proyecto.desperdicio_pct` o «no disponible: motivo» |
| Brecha del plan frente a la cota | pp | `cota.proyecto.brecha_pp` o «no disponible» |

**Bloque 2**: una fila en blanco, la celda de título «Totales de compra» y luego las columnas
`diametro | origen | barras | masa_kg`:
- Una fila por diámetro y origen (`Compra` / `Inventario adicional`).
- Una fila «Total comprado» (origen `Compra`).
- Una fila «Total tomado del inventario», solo si hay barras de inventario.

Los valores son numéricos. Los nombres y unidades van en español legible.

### 1.2 Cambios en hojas existentes

| Hoja | Cambio |
|---|---|
| Resumen de compra | Sin cambios de columnas ni filas de total (el auditor la suma fila por fila) |
| Barras | **Se elimina `stock_id`**. Columnas: `barra_id, patron_id, diametro, origen, longitud_m, piezas_por_barra, perdida_corte_m, descartado_m, sobrante_final_m` |
| Cota | `barras_minimas` → `barras_minimas_teoricas_cota_simple` |
| Parámetros | Columnas `condicion, valor, referencia`, con filas legibles (research R-08). El nombre de la hoja pasa a «Parámetros», con tilde |
| Patrones, Cortes, Descartados, Admisibilidad, Avisos, Inventario, Inventario excluido | Sin cambios de columnas |

### 1.3 «Trazabilidad» (FR-005)

Columnas `dato | valor`. Contenido según data-model §4, incluido `parametros_resueltos` (JSON
exacto). Ningún escalar que antes estaba en «Metricas» se pierde.

### 1.4 Invariantes verificables desde el Excel

- `Σ Patrones.repeticiones` = filas de Barras.
- Cada `Barras.patron_id` existe en Patrones.
- Por (diámetro, longitud), `Σ Resumen de compra.barras` = número de barras.
- «Totales de compra»: `Total comprado` + `Total tomado del inventario` = filas de Barras, y la
  masa coincide con la suma del detalle.

## 2. PDF `plan_corte.pdf` (WeasyPrint, A4 horizontal)

Secciones, en este orden (FR-009):

1. **Encabezado**: «Plan de corte — proyecto», versión (o «no asignada»), perfil legible y fecha
   de generación (hora de Colombia).
2. **Verificación**: «Plan verificado: demanda, diámetro, capacidad, etapas e inventario».
3. **Indicadores clave**: barras compradas y kg comprados, barras tomadas del inventario,
   desperdicio en masa, aprovechamiento y estado de admisibilidad (con umbral y diferencia si
   existen).
4. **Resumen de compra**: tabla por diámetro, longitud y origen, más las filas de total por
   diámetro y total general (compra separada del inventario).
5. **Patrones de corte**:
   - Dos líneas de cobertura (research R-13): una para la **tabla** (por ejemplo, «136 de 136
     patrones, 13955 de 13955 barras (100 %)») y otra para las **imágenes** (por ejemplo,
     «60 de 136 patrones, B de 13955 barras (x %)»).
   - Las imágenes de nesting incrustadas en **bloques de 18 patrones por página** (hasta 60
     patrones, los mismos del PNG), a escala casi real para imprimir en A4, o «imagen no
     disponible» (research R-01).
   - La tabla de patrones: todos si son 150 o menos; si no, los 150 más repetidos y el número de
     omitidos (FR-010). Columnas: patrón, diámetro, origen, barra, secuencia por etapa,
     repeticiones, aprovechamiento, saldo.
6. **Desperdicio y admisibilidad por diámetro**: pérdida irrecuperable, saldo reutilizable y
   tabla por diámetro. Nota: «el umbral lo define el usuario; no se identificó un máximo
   normativo».
7. **Calidad del plan**: cota por patrones y brecha, con la marca «no ajustada» si aplica, y una
   frase con la cota simple («con aprovechamiento perfecto, x %»). La cota mide; no prueba
   optimalidad.
8. **Avisos de masa nominal NSR-10** (rótulo `nominal.ROTULO`), o «Sin avisos».
9. **Datos técnicos**: condiciones de corte legibles (las mismas filas de «Parámetros»), motor,
   versión del análisis, método, semilla, huella de la entrada, piezas, masa de barras usadas y
   nota «Inventario final proyectado; verificar físicamente antes de usar».

**Formato (FR-011)**: coma decimal y punto de miles; dos decimales en general y tres en la cota
y la brecha.

## 3. PNG `grafica_cortes.png`

- **Título**: «Nesting lineal por patrones de corte».
- **Contenido**: hasta **60** patrones, los más repetidos, con etiqueta `P-#n-nnn ×rep`, piezas,
  pérdida, descarte y saldo.
- **Medidas**: longitud escrita sobre cada pieza que la admita (research R-02).
- **Leyenda**: etapas presentes, «Pérdida por corte», «Descarte» y «Saldo reutilizable»
  (research R-03).
- **Cobertura**: pie con «Se muestran N de M patrones, que cubren B de T barras (x %)».
- **Resolución y tamaño** (FR-013, FR-014; research R-04):
  - 200 dpi y 11 pulgadas de ancho.
  - 0,3 pulgadas por patrón.
  - **Máximo 9 megapíxeles**, sin importar el número de barras.
- **Uso**: el PNG está pensado para verse en pantalla al 100 %; la versión imprimible está en el
  PDF, por páginas.

## Formato numérico de los artefactos (enmienda 2; FR-032 a FR-035; research R-20)

- **PDF y PNG** (enmienda 3): punto decimal, sin separador de miles y con un espacio antes de la
  unidad. Los decimales siguen FR-033. Las repeticiones del PNG van sin separador
  («P-#3-001 ×2199»), y la secuencia queda como «E1: 2×4.2 m».
- **Excel**: las celdas numéricas siguen siendo números (FR-035). Los textos legibles
  («Parámetros», «secuencia» y los estados de «Resumen») usan el formato del usuario.
- **Backend**: un solo módulo de formato, `cutting/formato.py`, para `report.py` y los mensajes de
  dominio de `analysis.py`.

## 4. Inventario `inventario_final.xlsx`

**Sin cambios** (FR-022): hoja `Inventario` con columnas `diametro, longitud_m, cantidad`.
