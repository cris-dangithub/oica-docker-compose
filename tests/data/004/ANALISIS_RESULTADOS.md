# Test 004 — Análisis de resultados (cartilla sintética: edificio de cinco pisos)

> **Cartilla sintética** (INF-017, INF-018, RIESGO-AC-011). Sus resultados describen el
> comportamiento del motor con una demanda verosímil, no el desperdicio de una obra.
> Geometría, supuestos y estadísticas: `MEMORIA_DESPIECE.md`.

| Atributo | Valor |
|---|---|
| Archivo | `tests/data/004/004-sinteticaEdificio.xlsx` (SHA-256 `8bdc27ac…99c9e8de6`) |
| Tamaño | 105 filas, 18782 piezas, 30 longitudes distintas, 47732.309 kg |
| Diámetros | #3 (15208 piezas, 35.1 % de la masa), #4 (1096; 11.6 %), #5 (1070; 15.3 %), #6 (928; 23.4 %), #7 (480; 14.6 %) |
| Etapas | 11, con dos a cuatro diámetros por etapa |
| Piezas de longitud comercial exacta | 30.8 % de la masa en piezas de 6.00 o 12.00 m (en 002: 26.2 %) |
| Motor y entorno | Los mismos de 003: `secuencial-2` sin cambios; Docker Desktop, Python 3.12.15 |

## 1. Protocolo y evidencia

Mismo protocolo y mismos archivos de evidencia que 003 (ver `tests/data/003/ANALISIS_RESULTADOS.md`,
sección 1): 68 registros en la matriz, 3 en cada control, 0 diferencias al repetir los controles y
cota calculada y «ajustada» en todos los registros. La prueba de artefactos generó y verificó
Excel, PDF y PNG con 134 patrones y sin avisos de masa.

## 2. Desperdicio por escenario

Desperdicio final por masa (%). Para el AG: mediana [mínimo–máximo] de 5 semillas.

| Escenario | Cota | FFD = BFD | AG rápido | AG balanceado | AG profundo |
|---|---|---|---|---|---|
| ideal | 4.6629 | 6.2658 | 5.7279 [5.7148–5.7772] | 5.6957 [5.6870–5.7154] | 5.6814 [5.6814–5.6901] |
| solo pérdida | 4.8398 | 6.4719 | 5.9350 [5.9132–5.9623] | 5.8763 [5.8707–5.8818] | 5.8707 [5.8676–5.8707] |
| solo mínimo | 4.6629 | 6.2658 | 5.7043 [5.6901–5.7384] | 5.6957 [5.6814–5.7068] | 5.6870 [5.6814–5.6870] |
| ambos | 4.8398 | 6.4719 | 5.9209 [5.9184–5.9347] | 5.8787 [5.8707–5.8818] | 5.8676 [5.8676–5.8818] |

- Todas las semillas de todos los perfiles mejoran a FFD/BFD. Con ambas condiciones la mejora es
  de 0.54 a 0.60 pp.
- La dispersión entre semillas es pequeña: menos de 0.06 pp en el balanceado y el profundo.
- FFD/BFD usan 4322 barras (ideal) y 4315 (con pérdida). El AG usa a menudo más barras (mediana
  de 4314 a 4588) y aun así desperdicia menos masa: combina más barras de 6 y 9 m. El objetivo es
  la masa, no el número de barras, como ya se vio en 001.

## 3. Brecha frente a la cota

| Escenario | Brecha FFD (pp) | Brecha AG balanceado, mediana (pp) | Mejor AG (pp) |
|---|---|---|---|
| ideal | 1.6029 | 1.0327 | 1.0185 |
| ambos | 1.6321 | 1.0388 | 1.0278 |

El AG reduce en un 36 % la brecha de las heurísticas (de 1.63 a 1.04 pp con ambas condiciones).

Por diámetro (escenario ambos, FFD → AG balanceado de semilla mediana, frente a la cota):

| Diámetro | FFD (%) | AG (%) | Cota (%) |
|---|---|---|---|
| #3 | 1.98 | 1.53 | 0.36 |
| #4 | 3.94 | 3.14 | 2.32 |
| #5 | 5.66 | 4.97 | 2.19 |
| #6 | 4.48 | 3.31 | 2.57 |
| #7 | 20.28 | 20.28 | 20.28 |

- **#7: el plan alcanza la cota, así que es óptimo para esa demanda, aunque desperdicie el
  20.28 %.** Solo hay piezas de 4.60 y 5.15 m, y ninguna combinación con barras de 6, 9 o 12 m las
  aprovecha mejor. Es un ejemplo de desperdicio inevitable que solo la cota permite demostrar.
- **#3: la cota es 0.00 % en el escenario ideal**, porque sin etapas las piezas se podrían combinar
  sin sobrante, pero el plan queda en 1.35 %. Las piezas #3 están repartidas en las 11 etapas y la
  cota relaja ese orden (INF-016). Al menos parte de la brecha se debe a esa relajación y no al AG.
- **#5 conserva la mayor brecha** (2.8 pp con el AG).

## 4. Controles

| Control | FFD = BFD | AG rápido (semilla 0) | Observación |
|---|---|---|---|
| Cizalla (0 mm, mínimo automático) | 6.2658 % | 5.7043 % (4705 barras) | Igual al ideal en FFD |
| Descarte al fin de etapa (disco 1 mm) | 6.4719 % | 5.9347 % | Igual al descarte inmediato |

## 5. Tiempo

Con ambas condiciones, la mediana es de 1.05 s (rápido), 3.50 s (balanceado) y 9.22 s (profundo),
y FFD/BFD tardan 0.32 s. El máximo de todas las medianas es 10.32 s (profundo, solo mínimo).

Tiempo del AG balanceado por diámetro, escenario ambos (mediana de 5 semillas):

| Diámetro | Filas | Piezas | Segundos | Evaluaciones | ms por evaluación |
|---|---|---|---|---|---|
| #3 | 35 | 15208 | 1.733 | 2588 | 0.671 |
| #4 | 28 | 1096 | 0.912 | 2353 | 0.377 |
| #5 | 21 | 1070 | 0.589 | 1807 | 0.287 |
| #6 | 18 | 928 | 0.347 | 1374 | 0.246 |
| #7 | 3 | 480 | 0.041 | 699 | 0.059 |

El costo de cada evaluación crece con las piezas y con las filas del diámetro. El número de
evaluaciones depende del estancamiento, que llega más tarde cuantas más filas hay.

## 6. Observaciones

- Es el caso intermedio que faltaba: unas 3.6 veces menos piezas que 002 y unas 200 veces más que
  001. Su comportamiento se parece al de 002: el AG mejora a FFD/BFD con todas las semillas y
  recorta más de un tercio de la brecha.
- El 30.8 % de la masa está en piezas de 6.00 o 12.00 m exactos, que no dejan sobrante con ningún
  método. Esto baja el porcentaje total y diluye las diferencias entre métodos. Viene de partir en
  tramos de 12 m las barras de vigas, viguetas y loseta (supuesto S-07).
- Todos los tiempos quedan muy por debajo del rango de 1 a 5 minutos que se consideró deseable
  (INF-012).
