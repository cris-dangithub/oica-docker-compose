# Test 003 — Análisis de resultados (cartilla sintética: vivienda de dos pisos)

> **Cartilla sintética** (INF-017, INF-018, RIESGO-AC-011). Sus resultados describen el
> comportamiento del motor con una demanda verosímil, no el desperdicio de una obra.
> Geometría, supuestos y estadísticas: `MEMORIA_DESPIECE.md`.

| Atributo | Valor |
|---|---|
| Archivo | `tests/data/003/003-sinteticaVivienda.xlsx` (SHA-256 `bd16d9d2…e710921`) |
| Tamaño | 38 filas, 2958 piezas, 20 longitudes distintas, 5219.005 kg |
| Diámetros | #3 (2346 piezas, 42.6 % de la masa), #4 (364; 24.1 %), #5 (248; 33.3 %) |
| Etapas | 5, con dos o tres diámetros por etapa (en 002 cada etapa tiene un solo diámetro) |
| Motor | `secuencial-2`, sin cambios (`git diff origin/production -- backend/cutting` vacío) |
| Entorno | Docker Desktop (WSL2 6.6.87), Python 3.12.15, imagen del worker construida el 2026-10-04 |

## 1. Protocolo y evidencia

Mismo protocolo que 001 y 002 (Cap. 3 §3.6):
- 4 escenarios: ideal, solo pérdida, solo mínimo y ambos.
- FFD, BFD y AG con 3 perfiles × semillas 0–4: 17 ensayos por escenario.
- Controles de cizalla y de descarte al fin de etapa.
- Cota Gilmore–Gomory para cada registro.

| Archivo | Contenido |
|---|---|
| `tests/benchmarks/2026-10-04-tamano-matriz.jsonl` | Matriz de las 4 cartillas en una sola sesión (272 registros; 68 de 003) |
| `tests/benchmarks/2026-10-04-sinteticas-control-cizalla.jsonl` y `-fin-etapa.jsonl` | Controles (3 registros de 003 en cada uno) |
| `tests/benchmarks/2026-10-04-reproduccion-sinteticas.jsonl` | Repetición de los controles: 0 diferencias |
| `tests/benchmarks/2026-10-04-cota-tamano.jsonl` | Cota de los 284 registros: ninguno por debajo, todas «ajustadas» |
| `tests/benchmarks/2026-10-04-sinteticas-artefactos.jsonl` | Excel, PDF y PNG verificados; 46 patrones; sin avisos de masa |
| `tests/benchmarks/2026-10-04-tamano-tiempo.json` | Resumen de tiempo según tamaño (OE2) |

Todos los registros son válidos: el validador independiente reconstruye demanda, capacidad y
etapas.

## 2. Desperdicio por escenario

Desperdicio final por masa (%). Para el AG: mediana [mínimo–máximo] de 5 semillas.

| Escenario | Cota | FFD = BFD | AG rápido | AG balanceado | AG profundo |
|---|---|---|---|---|---|
| ideal | 2.7889 | 5.0182 | 5.0182 [4.9150–5.0182] | 4.9150 [4.9150–5.0182] | 4.9150 [4.9150–4.9150] |
| solo pérdida | 2.8733 | 5.1342 | 5.1052 [5.1052–5.1342] | 5.1052 [5.0022–5.1052] | 5.0022 [5.0022–5.1052] |
| solo mínimo | 2.7889 | 5.0182 | 5.0182 [4.9150–5.0182] | 4.9150 [4.9150–5.0182] | 4.9150 [4.9150–5.0182] |
| ambos | 2.8733 | 5.1342 | 5.1052 [5.1052–5.1342] | 5.1052 [5.0022–5.1052] | 5.1052 [5.0022–5.1052] |

- FFD y BFD dan el mismo plan en los cuatro escenarios: 634 barras (ideal) y 624 (con pérdida).
- La mejora del AG es pequeña: 0.10 pp en el escenario ideal y entre 0.03 y 0.13 pp con ambas
  condiciones. El AG usa menos barras: mediana de 606 a 621, frente a 624 o 634 de FFD/BFD.
- El mínimo automático no cambia el desperdicio de FFD/BFD (ideal = solo mínimo; solo pérdida =
  ambos). En el AG tampoco cambian las medianas.

## 3. Brecha frente a la cota

| Escenario | Brecha FFD (pp) | Brecha AG balanceado, mediana (pp) | Mejor AG (pp) |
|---|---|---|---|
| ideal | 2.2293 | 2.1261 | 2.1261 |
| ambos | 2.2609 | 2.2320 | 2.1289 |

Por diámetro (escenario ambos, FFD → AG balanceado de semilla mediana, frente a la cota):

| Diámetro | FFD (%) | AG (%) | Cota (%) |
|---|---|---|---|
| #3 | 4.00 | 3.94 | 2.16 |
| #4 | 5.41 | 5.41 | 3.68 |
| #5 | 6.35 | 6.35 | 3.19 |

La brecha de unos 2.1 pp no se cierra con ningún perfil ni semilla. Con la evidencia disponible no
se puede separar cuánto se debe a la cota y cuánto al AG:
- **La cota puede ser holgada.** Relaja el orden de etapas (INF-016), y esta cartilla reparte cada
  diámetro entre varias etapas: #5 aparece en las cinco.
- **El AG puede quedarse corto** en algún diámetro.

No se afirma que el plan sea óptimo ni que el AG falle.

## 4. Controles

| Control | FFD = BFD | AG rápido (semilla 0) | Observación |
|---|---|---|---|
| Cizalla (0 mm, mínimo automático) | 5.0182 % | 5.0182 % (629 barras) | Igual al escenario ideal en desperdicio |
| Descarte al fin de etapa (disco 1 mm) | 5.1342 % | 5.1052 % | Igual al descarte inmediato |

## 5. Tiempo

Con ambas condiciones, la mediana es de 0.18 s (rápido), 0.61 s (balanceado) y 1.73 s (profundo).
FFD y BFD tardan 0.03 s. El máximo de todas las medianas es 1.75 s. El análisis de tiempo según el
tamaño de la cartilla está en `tests/benchmarks/2026-10-04-tamano-tiempo.json` y en el Cap. 4.

## 6. Observaciones

- Es el caso en que el AG aporta menos. FFD ya queda a unos 2.2 pp de la cota y el AG gana como
  máximo 0.13 pp. Con 001 pasa algo parecido: el AG mejora solo con algunas semillas.
- El perfil profundo no garantiza el mejor resultado en el escenario ambos: su mediana es igual a la
  del rápido. Con 5 semillas la comparación entre perfiles es descriptiva.
- No hay piezas de longitud comercial exacta (0 % de la masa), así que ninguna pieza se corta sin
  sobrante de forma trivial.
