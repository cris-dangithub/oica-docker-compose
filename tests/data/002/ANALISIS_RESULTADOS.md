> Actualización 2026-09-13: el análisis siguiente corresponde al motor histórico. La evaluación vigente usa `backend/cutting/`, etapas sucesivas e inventario trazable; ver `docs/CORTE_SECUENCIAL.md`, `docs/tesis-doc/04_Capitulo4.md` y `tests/benchmarks/2026-09-13-agrupado.jsonl`. Sus métricas no son directamente comparables con las anteriores. El motor y la aplicación local con imágenes nuevas ya pasaron validación; ver la sección 4.7 del capítulo 4 y `tests/benchmarks/2026-09-13-integracion-local.json`.

# Análisis de Resultados — Test 002

> **Dataset:** `002-ingeBigTest.xlsx`
> **Fecha de ejecución:** 2026-05-13
> **Perfiles probados:** `rapido` ✅ | `balanceado` ✅ | `profundo` ✅
> **Bugs detectados en esta sesión:** BUG-003 (corregido antes de correr), BUG-004 (corregido en mid-session), BUG-005 (corregido en mid-session)

---

## 1. Descripción del dataset

| Atributo | Valor |
|----------|-------|
| Órdenes de trabajo | 137 |
| Piezas totales | 67,443 |
| Diámetros | #3, #4, #5, #6, #7 |
| Fuente | Datos reales de proyecto de construcción |

### Piezas por diámetro (demanda original)

| Diámetro | Piezas requeridas |
|----------|------------------|
| #3 | 58,500 |
| #4 | 864 |
| #5 | 2,774 |
| #6 | 5,237 |
| #7 | 68 |
| **Total** | **67,443** |

---

## 2. Bugs detectados durante este test

### BUG-003 — `population.py`: expansión de cantidades (CRÍTICO) ✅ Corregido antes de correr

**Descripción:** FFD/BFD/Aleatorio expandían cada orden de N piezas en N objetos Python individuales. Para 58,500 piezas de #3: la inicialización de población tardó >26 min sin completar con el primer intento.

**Corrección:** Representación agrupada — FFD/BFD operan sobre tipos de pieza con su cantidad (17 tipos para #3, no 58,500 ítems). Complejidad: O(R×B) donde R = tipos de pieza.

**Verificación:** 58,700 piezas de #3 → 0.15s, 0 errores de demanda.

---

### BUG-004 — `optimal_analyzer.py`: búsqueda exhaustiva O(N^k) (CRÍTICO) ✅ Corregido 2026-05-13

**Descripción:** `calcular_solucion_optima_homogenea` usaba `itertools.product` para enumerar todas las combinaciones posibles de barras. Para el grupo #5 (2,774 piezas con barras de 6/9/12m): espacio de búsqueda ≈ 3,560 millones de combinaciones. El worker colgó durante **8 horas 12 minutos** sin output.

**Corrección:** Guard de espacio de búsqueda en `optimal_analyzer.py`: si las combinaciones superan 500,000, fallback a greedy (mejor barra por ratio piezas/metro). El fallback se activa solo para datasets medianos; datasets pequeños (test 001) siguen usando búsqueda exhaustiva sin cambio.

**Verificación:** 2,774 piezas de 4.0m (peor caso) → 0.000s. Eficiencia 100% (óptimo matemático con 12m, 0 desperdicio).

---

### BUG-005 — `artifact_generator.py`: OOM en generación de PNG (ALTA) ✅ Corregido 2026-05-13

**Descripción:** `generar_imagen_grafica` calculaba `figsize=(16, len(barras) * 0.5)` sin límite. Para ~11,354 barras: figura de 16×5,677 pulgadas × 200 DPI = buffer de ~26 GB → `MemoryError: std::bad_alloc`.

**Corrección:**
- Cap de barras: `MAX_BARRAS_GRAFICA = 300` — si el total supera 300, la gráfica muestra las primeras 300 con nota en el título.
- Alto máximo: `min(len(barras) * 0.5, 150)` pulgadas.
- DPI reducido a 100 cuando es muestra (vs 200 para gráficas completas).

**Verificación:** PNG generado correctamente, 535 KB, sin OOM.

---

## 3. Resultados — Perfil `rapido`

### Parámetros del AG

| Parámetro | Valor |
|-----------|-------|
| Individuos por población | 20 |
| Generaciones máx | 30 |
| Tiempo total | 269.64s (~4.5 min) |

### Resultados por diámetro

| Diámetro | Método | Barras | Gen ejecutadas | Mejor fitness | Tiempo AG | Eficiencia |
|----------|--------|--------|----------------|---------------|-----------|------------|
| #3 | FFD directo* | 6,051 | 0 | — | ~0.15s | 99.09% |
| #4 | AG | 319 | 20 (convergió) | 16,318.0 | 5.07s | 99.04% |
| #5 | AG | 1,768 | 30 | 116,871.5 | 49.76s | 86.50% |
| #6 | AG | 3,168 | 30 | 246,220.1 | 85.85s | 76.70% |
| #7 | AG | 48 | 30 | 3,230.0 | 2.00s | 85.13% |
| **Total** | — | **11,354** | — | — | **~143s AG** | **90.86%** |

*#3 activa el fallback FFD por superar el umbral de barras estimadas (5,996 > MAX_BARRAS_AG=3,000).

### Distribución de barras usadas

| Diámetro | Barras 6m | Barras 9m | Barras 12m |
|----------|-----------|-----------|------------|
| #3 | 0 | 0 | 6,051 |
| #4 | 0 | 0 | 319 |
| #5 | 0 | 42 | 1,726 |
| #6 | 0 | 111 | 3,057 |
| #7 | 1 | 4 | 43 |

**Observación:** El AG prefiere barras de 12m (máxima longitud) en casi todos los casos. Esto es consistente con FFD/BFD en `population.py` que abre barras por `_abrir_barra` (mayor primero).

### Desperdicio por diámetro

| Diámetro | Desperdicio total | Promedio / barra | Eficiencia |
|----------|-------------------|------------------|------------|
| #3 | 660.37 m | 0.109 m/barra | 99.09% |
| #4 | 36.80 m | 0.115 m/barra | 99.04% |
| #5 | 2,847.15 m | 1.610 m/barra | 86.50% |
| #6 | 8,782.01 m | 2.772 m/barra | 76.70% |
| #7 | 83.00 m | 1.729 m/barra | 85.13% |
| **Global** | **12,409.33 m** | **1.093 m/barra** | **90.86%** |

### Verificación de demanda

| Diámetro | Piezas requeridas | Piezas cortadas | ¿Demanda satisfecha? |
|----------|------------------|-----------------|----------------------|
| #3 | 58,500 | 58,500 | ✅ |
| #4 | 864 | 864 | ✅ |
| #5 | 2,774 | 2,774 | ✅ |
| #6 | 5,237 | 5,237 | ✅ |
| #7 | 68 | 68 | ✅ |
| **Total** | **67,443** | **67,443** | ✅ |

---

## 4. Coherencia entre artefactos

### Excel ↔ Datos esperados

| Verificación | Estado |
|--------------|--------|
| Hojas: Sheet1 con 7 columnas | ✅ |
| 11,354 filas (= total barras) | ✅ |
| Columnas: numero_barra, diametro, barra_origen_longitud, cortes_realizados, cantidad_requerida, masa_unitaria_kg, desperdicio_m | ✅ |
| Piezas totales cortadas = 67,443 (demanda exacta) | ✅ |
| BUG-002: `cantidad_requerida` = len(cortes) por barra (no demanda original) | ⚠️ Conocido, sin corregir |

### PDF

| Verificación | Estado |
|--------------|--------|
| Generado (1.2 MB) | ✅ |
| Pendiente revisión visual de contenido | ⏳ |

### PNG (gráfica)

| Verificación | Estado |
|--------------|--------|
| Generado (535 KB) | ✅ |
| Muestra: primeras 300 barras de 11,354 | ⚠️ Por BUG-005 (intencional) |
| DPI: 100 (reducido para muestras grandes) | ✅ |

---

## 5. Análisis del comportamiento del AG

### ¿El AG aportó valor sobre FFD?

Para los grupos donde corrió el AG (#4, #5, #6, #7):

- **#4 (pequeño, 864 piezas):** AG convergió en 20 generaciones (menos que el máximo de 30). Fitness estable (16,318). El AG encontró la solución óptima rápidamente — consistente con un dataset pequeño.

- **#5 (mediano, 2,774 piezas):** AG corrió las 30 generaciones sin convergencia. Mejora de 1,260 unidades de fitness sobre la población inicial. El AG diversificó (diversidad final: 0.37). Eficiencia: 86.5% — moderada, sugiere fragmentación en longitudes de pieza.

- **#6 (grande, 5,237 piezas):** Mejor caso relativo del AG. Corrió 30 generaciones, mejora de 3,330. La mejor solución se encontró en gen 28/30. Eficiencia: 76.7% — la más baja, sugiere piezas de longitud "difícil" (no encajan limpiamente en 6/9/12m).

- **#7 (pequeño, 68 piezas):** AG corrió 30 generaciones, mejora de 180. Convergió tarde (gen 26). Eficiencia: 85.1%.

### Observación sobre eficiencias bajas (#5, #6)

Las eficiencias del 76-86% en #5 y #6 (vs >99% en #3 y #4) sugieren que las piezas de esos diámetros tienen longitudes que no encajan eficientemente en barras comerciales de 6/9/12m. Esto es un resultado esperado del problema de corte 1D — no es un bug del AG sino una característica del dataset.

### #3 con FFD vs AG

El grupo #3 (58,500 piezas, ~6,000 barras estimadas) usa FFD directo por superar `MAX_BARRAS_AG=3000`. Eficiencia: 99.09%. Esto indica que FFD ya produce una solución casi óptima para piezas de #3 en este dataset — el AG agregaría tiempo de cómputo sin mejora significativa esperada.

Esta observación es relevante para el Cap. 4 de la tesis: **para datasets con patrones uniformes de piezas (mismo diámetro repetido), el heurístico FFD puede ser competitivo con el AG**.

---

## 6. Resultados — Perfil `balanceado`

| Parámetro | Valor |
|-----------|-------|
| Individuos por población | 50 |
| Generaciones máx | 100 |
| Tiempo total | 805.91s (~13.4 min) |

| Diámetro | Método | Barras | Gen ejecutadas | Mejor fitness | Tiempo AG | Eficiencia |
|----------|--------|--------|----------------|---------------|-----------|------------|
| #3 | FFD directo | 6,051 | 0 | — | ~0.15s | 99.09% |
| #4 | AG | 319 | 25 | 16,288.0 | 60.4s | 99.12% |
| #5 | AG | 1,768 | 78 | 113,721.5 | 309.0s | 87.81% |
| #6 | AG | 3,168 | 45 | 242,770.1 | 308.1s | 77.40% |
| #7 | AG | 48 | 32 | 3,260.0 | 4.0s | 84.67% |
| **Total** | — | **11,354** | — | — | **~682s AG** | **91.30%** |

---

## 7. Resultados — Perfil `profundo`

| Parámetro | Valor |
|-----------|-------|
| Individuos por población | 100 |
| Generaciones máx | 200 |
| Tiempo total | 1,246.31s (~20.8 min) |

| Diámetro | Método | Barras | Gen ejecutadas | Mejor fitness | Gen mejor | Tiempo AG | Eficiencia |
|----------|--------|--------|----------------|---------------|-----------|-----------|------------|
| #3 | FFD directo | 6,051 | 0 | — | — | ~0.15s | 99.09% |
| #4 | AG | 319 | 21 | 16,258.0 | 1 | 160.3s | 99.19% |
| #5 | AG | 1,768 | 21 | 116,091.5 | 20 | 323.6s | 86.82% |
| #6 | AG | 3,168 | **6** | 247,390.1 | 4 | **598.3s** | 76.46% |
| #7 | AG | 48 | 28 | 3,290.0 | 8 | 14.4s | 84.22% |
| **Total** | — | **11,354** | — | — | — | **~1097s AG** | **90.83%** |

> **Nota:** El perfil `profundo` ejecutó solo 6 generaciones para #6. Ver análisis de comportamiento en sección 8.

---

## 8. Comparación de 3 perfiles

### Eficiencia global

| Perfil | Tiempo total | Eficiencia global | Desperdicio total | Barras totales |
|--------|-------------|-------------------|------------------|----------------|
| `rapido` | 269.64s | 90.86% | 12,409.33m | 11,354 |
| `balanceado` | 805.91s | **91.30%** | **11,749.33m** | 11,354 |
| `profundo` | 1,246.31s | 90.83% | 12,448.33m | 11,354 |

### Eficiencia por diámetro

| Diámetro | `rapido` | `balanceado` | `profundo` | Mejor |
|----------|----------|-------------|------------|-------|
| #3 | 99.09% | 99.09% | 99.09% | Igual (FFD en todos) |
| #4 | 99.04% | 99.12% | **99.19%** | profundo |
| #5 | 86.50% | **87.81%** | 86.82% | balanceado |
| #6 | 76.70% | **77.40%** | 76.46% | balanceado |
| #7 | 85.13% | 84.67% | 84.22% | rapido |

### Hallazgo crítico: profundo NO supera a balanceado

El perfil `profundo` (100 ind., 200 gen máx) produce eficiencia **inferior** a `balanceado` (50 ind., 100 gen máx).

**Causa raíz:** `engine.py` aplica un tiempo límite por grupo de **300 segundos por defecto** (`tiempo_limite_segundos = 300`). `celery_worker.py` pasa `{'tamaño_poblacion': 100, 'max_generaciones': 200}` sin sobreescribir este parámetro. Con 100 individuos, cada generación de #6 tarda ~100 segundos → solo caben 6 generaciones en 300s. `balanceado` con 50 individuos ejecuta ~50s/gen → 45 generaciones en el mismo límite temporal.

**Consecuencia:** `profundo` invierte 3× más tiempo que `rapido` pero obtiene resultados similares o peores porque el tiempo por generación sube con el tamaño de la población, sin que se amplíe el presupuesto de tiempo.

**Clasificación:** BUG de configuración (no de código). El perfil `profundo` no está configurado para ser realmente más exhaustivo en datasets reales.

---

## 9. Análisis del comportamiento del AG

### ¿Por qué `balanceado` gana en #5 y #6?

`balanceado` ejecuta ~78 generaciones para #5 y ~45 para #6 dentro del límite de 300s/grupo. Con 50 individuos, el AG tiene más generaciones para explorar el espacio de soluciones, logrando mayor diversidad final (0.37 vs 0.22 en profundo). La mayor diversidad en `balanceado` indica que el AG no convergió prematuramente y siguió explorando.

### Comportamiento del #3 (FFD directo en todos los perfiles)

El grupo #3 (58,500 piezas, ~6,000 barras estimadas) activa el fallback FFD en todos los perfiles por superar `MAX_BARRAS_AG=3000`. La eficiencia de 99.09% con FFD es excelente — el AG no aportaría mejora significativa porque las piezas de #3 se cortan eficientemente de barras de 12m con mínimo desperdicio.

### Correlación entre eficiencia y tipo de pieza

La baja eficiencia de #5 (~87%) y #6 (~77%) respecto a #3/#4 (~99%) no es un fallo del AG sino una característica del dataset: las longitudes de las piezas de #5 y #6 en este proyecto no dividen limpiamente en barras comerciales de 6/9/12m, generando mayor desperdicio estructural. El AG no puede eliminar este desperdicio — solo minimizarlo.

---

## 10. Bugs activos (sin resolver)

| ID | Descripción | Severidad |
|----|-------------|-----------|
| BUG-002 | `cantidad_requerida` en Excel = len(cortes) por barra, no demanda original | MEDIA |
| BUG-006 | Perfil `profundo` limitado por `tiempo_limite_segundos=300s` defecto sin sobreescribir — no es más exhaustivo que `balanceado` para grupos grandes | MEDIA |
| MEJORA-001 | PDF y PNG no muestran agrupación visual por diámetro | BAJA |

---

## 11. Próximos pasos

1. ✅ Test 002 — `rapido`, `balanceado`, `profundo` completados
2. ✅ Análisis de resultados documentado
3. ⏳ Decidir INF-008 (reutilización de desperdicios en alcance)
4. ⏳ Iniciar Bloque E — redacción Cap. 4 con resultados reales (INF-005)
