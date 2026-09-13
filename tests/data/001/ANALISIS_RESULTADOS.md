> Actualización 2026-09-13: el análisis siguiente corresponde al motor histórico. La evaluación vigente usa `backend/cutting/`, etapas sucesivas e inventario trazable; ver `docs/CORTE_SECUENCIAL.md`, `docs/tesis-doc/04_Capitulo4.md` y `tests/benchmarks/2026-09-13-agrupado.jsonl`. Sus métricas no son directamente comparables con las anteriores. El motor y la aplicación local con imágenes nuevas ya pasaron validación; ver la sección 4.7 del capítulo 4 y `tests/benchmarks/2026-09-13-integracion-local.json`.

# Test 001 — Análisis de Resultados

> **Archivo de entrada:** `tests/data/001/001-pruebaInicial.xlsx`
> **Fecha de ejecución:** 2026-05-06
> **Estado:** Completado — BUG-001 corregido, coherencia verificada post-fix

---

## Descripción del dataset

Planilla de vigas con 16 piezas reales, 3 diámetros:

| N° Orden | Elemento | Diámetro | Longitud (m) | Cantidad |
|----------|----------|----------|--------------|----------|
| 1 | Vigas | #5 | 2.00 | 10 |
| 2 | Vigas | #5 | 6.13 | 10 |
| 3 | Vigas | #5 | 5.33 | 10 |
| 4 | Vigas | #5 | 2.38 | 10 |
| 5 | Vigas | #5 | 3.98 | 6 |
| 6 | Vigas | #5 | 5.20 | 6 |
| 7 | Vigas | #5 | 4.93 | 6 |
| 8 | Vigas | #5 | 5.93 | 6 |
| 9 | Vigas | #5 | 4.55 | 6 |
| 10 | Vigas | #5 | 4.70 | 6 |
| 11 | Vigas | #5 | 3.18 | 6 |
| 12 | Vigas | #5 | 4.25 | 6 |
| 13 | Vigas | #4 | 1.00 | 1 |
| 14 | Vigas | #4 | 1.20 | 1 |
| 15 | Vigas | #4 | 1.20 | 1 |
| 16 | Vigas | #3 | 1.08 | 1 |

Columna extra `Grupo de Ejecución` presente en el input — el backend la ignora correctamente.

---

## Resultados por perfil

| Perfil | Tiempo | Barras usadas | Desperdicio total | Artefactos |
|--------|--------|---------------|-------------------|-----------|
| `rapido` | 8.50s | 35 | 24.80m | ✅ Excel / PDF / PNG |
| `balanceado` | 14.89s | 35 | 24.80m | ✅ Excel / PDF / PNG |
| `profundo` | 27.23s | 35 | 24.80m | ✅ Excel / PDF / PNG |

**Los 3 perfiles convergen al mismo resultado.** Esperado: con 16 piezas y espacio de soluciones pequeño, cualquier configuración del AG encuentra el óptimo. La diferencia entre perfiles debería emerger en datasets más grandes (>50 piezas por diámetro).

---

## Resultados del AG por diámetro

| Diámetro | Barras usadas | Longitud por barra | Desperdicio | Eficiencia |
|----------|---------------|---------------------|-------------|------------|
| #5 | 33 | 12m | 17.28m | **95.64%** |
| #4 | 1 | 6m | 2.60m | **56.67%** |
| #3 | 1 | 6m | 4.92m | **18.00%** |
| **Total** | **35** | — | **24.80m** | **93.92%** |

El bajo aprovechamiento de #3 y #4 es consecuencia directa de la baja demanda (1-2 piezas cortas). Es el resultado matemáticamente correcto para ese caso — no es un bug.

---

## Coherencia entre los 3 artefactos

### Excel ↔ PDF
- ✅ Mismo número de barras (35)
- ✅ Mismos patrones de corte
- ✅ Mismo desperdicio fila a fila
- ✅ Misma masa total (623.78 kg)
- ✅ Eficiencia en PDF = **93.92%** coincide con cálculo real (BUG-001 corregido 2026-05-06)

### Excel ↔ PNG
- ✅ 35 barras representadas
- ✅ Barras 34-35 visualmente más cortas (6m) vs barras 1-33 (12m)
- ✅ El área sombreada (diagonal) representa desperdicio
- ⚠️ Los colores en la gráfica son por índice de pedido, no por diámetro — ningún indicador visual de agrupación por diámetro

### PDF ↔ PNG
- ✅ Mismos 35 barras, mismo orden
- ⚠️ Ninguno de los dos indica a qué diámetro pertenece cada barra

---

## Verificación matemática

```
Integridad cortes: 35/35 filas correctas — desperdicio = longitud_barra − Σcortes (0 errores)
Total material:    408.00m (33×12m + 1×6m + 1×6m)
Total desperdicio: 24.80m
Total útil:        383.20m
Eficiencia real:   93.92%
```

---

## Bugs identificados

### ~~BUG-001~~ — Eficiencia incorrecta en PDF (mezcla de unidades) `✅ CORREGIDO 2026-05-06`

**Archivo:** `services/backend/utils/artifact_generator.py` línea 100

**Código actual:**
```python
total_masa = resultados_df['masa_unitaria_kg'].sum()       # kg  → 623.78
total_desperdicio = resultados_df['desperdicio_m'].sum()   # metros → 24.80
eficiencia = ((total_masa - total_desperdicio) / total_masa * 100)
# = (623.78 - 24.80) / 623.78 × 100 = 96.02%  ← INCORRECTO (mezcla kg y m)
```

**Resultado incorrecto:** 96.02%
**Resultado correcto:** 93.92%

**Corrección:**
```python
total_barra_m = resultados_df['barra_origen_longitud'].sum()    # metros
total_desperdicio_m = resultados_df['desperdicio_m'].sum()      # metros
eficiencia = ((total_barra_m - total_desperdicio_m) / total_barra_m * 100) if total_barra_m > 0 else 0
```

**Impacto académico:** El Capítulo 4 no puede citar la eficiencia del sistema si el cálculo está mal. Debe corregirse antes de generar resultados para la tesis.

---

### BUG-002 — Columna `cantidad_requerida` en Excel tiene semántica incorrecta `MEDIA`

**Archivo:** `services/backend/celery_worker.py` línea 492

**Problema:** En el input, `Cantidad` = cuántas piezas de ese largo necesita el proyecto. En el output Excel, `cantidad_requerida` = `len(cortes)` = cuántos cortes se hacen de una sola barra física.

**Ejemplo:** La barra 31 tiene `cortes_realizados = [3.18, 3.18, 3.18, 2.38]` y `cantidad_requerida = 4`. Esto no es la cantidad demandada del pedido — son los cortes de esa barra específica.

**Impacto:** Un ingeniero que lea el Excel esperaría ver la demanda original en esa columna, no el número de cortes por barra. La columna debería llamarse `piezas_por_barra` o similar.

---

## Hallazgos de usabilidad (no bugs, mejoras deseables)

### MEJORA-001 — PDF y PNG no muestran agrupación por diámetro

El Excel tiene columna `diametro` (#5, #4, #3), pero el PDF lista 35 barras secuencialmente y la imagen no tiene indicadores por diámetro. Un ingeniero de obra no puede saber qué barras son de qué diámetro leyendo el PDF o mirando el gráfico.

**Sugerido:** Sección separada por diámetro en el PDF, y colores o subgráficas por grupo en el PNG.

---

## Preguntas pendientes respondidas

### INF-002 — Nombres de perfiles

El frontend usa `rapido`, `balanceado`, `profundo` y los muestra correctamente en la UI:
- "Rápido (procesamiento rápido)"
- "Balanceado (recomendado)"
- "Profundo (más ahorro de material)"

El código, la BD y la API son consistentes con estos nombres. **Los nombres canónicos son `rapido/balanceado/profundo`.**
La documentación del Cap. 3 que usa otros nombres debe actualizarse (Bloque E).

### INF-005 — Resultados para Cap. 4

Este test provee los primeros datos reales. Sin embargo, **no deben usarse directamente para Cap. 4** porque:
1. ~~BUG-001 (eficiencia incorrecta)~~ — **corregido 2026-05-06** ✅
2. El dataset es pequeño (16 piezas) — no demuestra la diferenciación entre perfiles
3. Falta un dataset más representativo de un proyecto real de construcción

Recomendación: crear un dataset más grande (>50 piezas, >3 diámetros) donde los perfiles sí difieran, y usar esos resultados para Cap. 4. → **Ver test 002.**

### INF-008 — Reutilización de desperdicios

No explorado en este test (siempre `desperdicios_previos = []`). El análisis queda pendiente de la decisión del usuario sobre el alcance.

---

## Estado del sistema tras este test

| Componente | Estado |
|------------|--------|
| Upload → procesamiento → artefactos | ✅ Funcional |
| Agrupación por diámetro en AG | ✅ Correcto |
| Integridad matemática de cortes | ✅ Sin errores |
| Eficiencia en PDF | ✅ Corregida (BUG-001 resuelto — ahora muestra 93.92%) |
| Semántica de columnas en Excel | ⚠️ Confusa (BUG-002) |
| Visibilidad de diámetros en PDF/PNG | ⚠️ Ausente (MEJORA-001) |
| Diferenciación entre perfiles | ⚠️ Solo visible en datasets grandes |

---

## Próximos pasos de testing

1. ~~Corregir BUG-001~~ — **✅ Corregido 2026-05-06**
2. Crear dataset más grande (test 002) con >3 diámetros y suficientes piezas para diferenciar perfiles — **✅ Ver test 002**
3. Verificar que `rapido` vs `profundo` sí divergen en un dataset complejo
4. Evaluar si MEJORA-001 (diámetros en PDF/PNG) es prioritaria o se documenta como limitación
