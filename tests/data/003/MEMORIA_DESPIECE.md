# Memoria de despiece: cartilla 003, vivienda de dos pisos (sintética)

> Archivo generado por `scripts/generar_cartillas_sinteticas.py`; no se edita a mano.
> **Cartilla sintética.** La elaboró el autor para evaluar el motor de corte con un tamaño y
> una mezcla de diámetros que 001 y 002 no cubren. No proviene de una obra, no es un diseño
> estructural y no certifica cumplimiento de la NSR-10: las longitudes resultan de una
> geometría ficticia y de los supuestos de la sección 4. Sus resultados no son evidencia de
> desperdicio en obra (INF-017, INF-018, RIESGO-AC-011).

## 1. Descripción

| Atributo | Valor |
|---|---|
| Archivo | `tests/data/003/003-sinteticaVivienda.xlsx` |
| Sistema | pórticos de concreto reforzado con losa aligerada en una dirección |
| Pisos | 2; entrepiso de 2.70 m |
| Ejes en x | 4, luces 3.50 / 4.00 / 3.50 m (total 11.00 m) |
| Ejes en y | 3, luces 4.50 / 4.50 m (total 9.00 m) |
| Columnas | 12 por piso |
| Área construida | 198.00 m² (2 × 99.00 m²) |
| Desplante | 1.20 m del fondo de la zapata al nivel 0 |

## 2. Secciones y refuerzo

| Elemento | Sección (m) | Refuerzo longitudinal | Refuerzo transversal |
|---|---|---|---|
| Zapatas aisladas | esquina 1.00 × 1.00, borde 1.20 × 1.20, interior 1.40 × 1.40; h = 0.30 | parrilla #4 @ 0.15 en dos direcciones | — |
| Vigas de cimentación | 0.25 × 0.30 | 2 + 2 #4 continuas | estribos #3 @ 0.15 |
| Columnas piso 1 | 0.30 × 0.30 | 4 #5 | estribos #3: 0.10 en lo, 0.20 al centro y 0.10 en el nudo |
| Columnas piso 2 | 0.30 × 0.30 | 4 #5 | estribos #3: 0.10 en lo, 0.20 al centro y 0.10 en el nudo |
| Vigas losa nivel 2 | 0.25 × 0.35 | 2 + 2 #5 continuas, 1 bastón superior por apoyo | estribos #3: 0.075 en 2h, 0.15 al centro |
| Vigas cubierta | 0.25 × 0.35 | 2 + 2 #5 continuas, 1 bastón superior por apoyo | estribos #3: 0.075 en 2h, 0.15 al centro |
| Viguetas | @ 0.75, paralelas al eje y | 2 #4 inferiores continuas, 1 bastón #4 por apoyo | sin flejes (S-10) |
| Loseta | — | #3 @ 0.25 en dos direcciones | — |
| Escalera | 1 tramo por piso, ancho 1.00, huella total 3.92 por tramo | #4 @ 0.15 inferior y negativos en los apoyos | #3 @ 0.20 |

## 3. Etapas (Grupo de Ejecución)

| Grupo | Contenido | Diámetros | Piezas | Masa (kg) |
|---|---|---|---|---|
| 1 | Vigas de cimentación; Zapatas; Arranques de columnas | #3, #4, #5 | 707 | 1057.758 |
| 2 | Columnas piso 1 | #3, #5 | 312 | 434.534 |
| 3 | Loseta losa nivel 2; Escalera piso 1; Vigas losa nivel 2; Viguetas losa nivel 2 | #3, #4, #5 | 838 | 1769.989 |
| 4 | Columnas piso 2 | #3, #5 | 312 | 278.093 |
| 5 | Loseta cubierta; Vigas cubierta; Viguetas cubierta | #3, #4, #5 | 789 | 1678.630 |

## 4. Supuestos de despiece (S-01 a S-14)

Las páginas son las del PDF del Título C publicado por CAMACOL (Decreto 926 de 2010).
Fichas en `docs/tesis-doc/Referencias.md`.

| ID | Supuesto | Valor | Fuente |
|---|---|---|---|
| S-01 | Materiales y factores de ld | f'c = 21 MPa, fy = 420 MPa, ψt = ψe = λ = 1.0 (sin efecto de barra superior) | Supuesto; factores de C.12.2.4, p. C-220 (REF-NSR10-EMPALMES) |
| S-02 | Diámetros y masas nominales | NSR-10, Tabla C.3.5.3-2 | p. C-47 (REF-NSR10-TABLA) |
| S-03 | Recubrimiento libre | zapatas 75 mm; vigas de cimentación 50 mm; vigas y columnas 40 mm; losas, viguetas y escaleras 20 mm | C.7.7.1, pp. C-96 y C-97 (REF-NSR10-GANCHOS-RECUBRIMIENTOS) |
| S-04 | Gancho estándar de 90°: extensión de 12 db; el doblez no se suma | #3 0.15, #4 0.20, #5 0.20 m | C.7.1.2, p. C-91 (REF-NSR10-GANCHOS-RECUBRIMIENTOS) |
| S-05 | Estribos cerrados y grapas con ganchos sísmicos de 135° (extensión 6 db, no menor de 75 mm) | se suman 0.10 m por gancho (75 mm más el doblez); estribo = 2(b − 2r) + 2(h − 2r) + 0.20; grapa = (b − 2r) + 0.20 | C.7.1.4, p. C-91, y C.2.2, p. C-33; los 25 mm del doblez son supuesto |
| S-06 | Traslapo clase B = 1.3 ld, no menor de 300 mm; ld del caso favorable: 43.64 db hasta #6 y 53.91 db desde #7 | #3 0.55, #4 0.75, #5 0.95 m | C.12.2.2, p. C-218, y C.12.15.1-2, pp. C-240 y C-241 (REF-NSR10-EMPALMES) |
| S-07 | Barras continuas de más de 12 m: tramos de 12.00 m más el resto; si el resto es menor que max(2 traslapos, 2 m) se igualan los dos últimos. No se modela la posición del empalme | — | Supuesto. C.21.3.4.5 (p. C-366) prohíbe traslapos dentro de los nudos: un despiece real los desplaza |
| S-08 | Longitudes redondeadas hacia arriba a 0.05 m | — | Supuesto; 123 de las 137 longitudes de 002 son múltiplos de 0.05 m |
| S-09 | Separaciones | vigas: 0.075 en 2h y 0.15 al centro; columnas: 0.10 en lo = max(ln/6, b, 0.50 m) y 0.20 al centro; nudos 0.10; vigas de cimentación 0.15; parrillas 0.15; viguetas 0.75; loseta 0.25; escalera 0.15 y 0.20, anclaje 0.30 m más gancho | Vigas y columnas dentro de los límites de DMO: C.21.3.4.6 y C.21.3.4.8 (pp. C-366 y C-367), C.21.3.5.6 a C.21.3.5.11 (pp. C-367 a C-369) (REF-NSR10-DMO). El resto es supuesto |
| S-10 | Estribos y grapas #3; sin barras #2; viguetas sin flejes | — | C.7.10.5.1, p. C-103, y C.21.3.5.8; #2 no está en el catálogo de OICA |
| S-11 | Filas agregadas por elemento, diámetro, longitud y etapa | — | Supuesto |
| S-12 | Etapas: 1 cimentación; columnas del piso k en el grupo 2k; losa sobre el piso k en el grupo 2k + 1 | — | Supuesto de secuencia constructiva |
| S-13 | Fuera del modelo: mampostería, cimentación profunda, aberturas de losa, descansos de escalera, acceso a la cubierta, cambios de sección (dobleces) y alambre de amarre | — | Supuesto |
| S-14 | Empalmes de columnas a media altura del piso; arranques desde el fondo de la zapata con gancho; la última barra termina con gancho en la cubierta | — | C.21.3.5.3, p. C-367 (REF-NSR10-DMO): traslapos solo en la mitad central |

## 5. Reglas por elemento

- **Zapatas:** barras por dirección = ⌈(lado − 2r) / s⌉ + 1; longitud = lado − 2r + 2 ganchos.
- **Arranques:** desplante − r + gancho + altura / 2 + traslapo.
- **Columnas:** piso 1: altura + traslapo; piso 2: altura / 2 − r + gancho.
- **Vigas y vigas de cimentación:** longitud desarrollada = suma de luces + ancho de columna − 2r + 2 ganchos, dividida según S-07; bastones = un tercio de la luz libre a cada lado del apoyo más el ancho del apoyo (en los extremos, más gancho − r).
- **Viguetas:** por cada luz en x, ⌈(luz − b viga) / s⌉ − 1; barra inferior continua en y y bastones como en vigas.
- **Loseta:** barras rectas de borde a borde en cada dirección, ⌈ancho / s⌉ + 1.
- **Escalera:** longitud inclinada √(huella² + subida²); inferiores con anclaje y gancho en cada extremo; negativos de un cuarto de la inclinada más anclaje y gancho; repartición transversal.

**Ejemplo (estribo de columna del piso 1):** sección 0.30 × 0.30, r = 0.04:
2(0.22) + 2(0.22) + 2(0.10) = 1.08 → 1.10 m.
Altura libre 2.35 m, lo = max(0.392, 0.30, 0.50) = 0.500 m:
22 juegos por columna y piso, incluidos 4 en el nudo.

## 6. Estadísticas

- Filas: **38**. Piezas: **2958**. Masa: **5219.005 kg**.
- Diámetros: #3, #4, #5. Etapas: 5. Longitudes distintas: 20.
- Masa por m² construido: 26.4 kg/m² (dato descriptivo, sin rango de referencia).
- Masa en piezas de longitud comercial (6, 9 o 12 m): 0.000 kg, 0.0 % (en 002: 26.2 %).

| Diámetro | Filas | Piezas | Masa (kg) | % masa | Longitudes distintas | Mínima (m) | Máxima (m) |
|---|---|---|---|---|---|---|---|
| #3 | 10 | 2346 | 2225.552 | 42.6 | 5 | 0.90 | 11.20 |
| #4 | 13 | 364 | 1258.006 | 24.1 | 9 | 1.25 | 11.60 |
| #5 | 15 | 248 | 1735.446 | 33.3 | 7 | 1.55 | 11.65 |

La mínima por diámetro es el mínimo reutilizable automático que aplica OICA (menor longitud demandada).

| Longitud (m) | Piezas |
|---|---|
| [0, 1) | 439 |
| [1, 2) | 2075 |
| [2, 3) | 12 |
| [3, 4) | 128 |
| [4, 5) | 0 |
| [5, 6) | 8 |
| [6, 7) | 0 |
| [7, 8) | 0 |
| [8, 9) | 0 |
| [9, 10) | 186 |
| [10, 11) | 0 |
| [11, 12] | 110 |

## 7. Trazabilidad

- SHA-256 del XLSX: `bd16d9d2140a5c25f3f088bc498bd30776e97ca00cf39c9f7357ce95ee710921`
- SHA-256 del contenido (filas canónicas): `4f0fcac76b0809b7b215480992e119ecb107c781d643ac098d756a8ca67de815`
- Regenerar en memoria y comparar: `PYTHONUTF8=1 python scripts/generar_cartillas_sinteticas.py --verificar`
- Las entradas quedan congeladas tras la revisión del usuario; cualquier cambio posterior lleva un nombre de archivo nuevo.
