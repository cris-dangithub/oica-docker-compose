# Memoria de despiece: cartilla 004, edificio de cinco pisos (sintético)

> Archivo generado por `scripts/generar_cartillas_sinteticas.py`; no se edita a mano.
> **Cartilla sintética.** La elaboró el autor para evaluar el motor de corte con un tamaño y
> una mezcla de diámetros que 001 y 002 no cubren. No proviene de una obra, no es un diseño
> estructural y no certifica cumplimiento de la NSR-10: las longitudes resultan de una
> geometría ficticia y de los supuestos de la sección 4. Sus resultados no son evidencia de
> desperdicio en obra (INF-017, INF-018, RIESGO-AC-011).

## 1. Descripción

| Atributo | Valor |
|---|---|
| Archivo | `tests/data/004/004-sinteticaEdificio.xlsx` |
| Sistema | pórticos de concreto reforzado con losa aligerada en una dirección |
| Pisos | 5; entrepiso de 3.00 m |
| Ejes en x | 5, luces 5.00 / 5.50 / 5.50 / 5.00 m (total 21.00 m) |
| Ejes en y | 4, luces 5.00 / 6.00 / 5.00 m (total 16.00 m) |
| Columnas | 20 por piso |
| Área construida | 1680.00 m² (5 × 336.00 m²) |
| Desplante | 1.80 m del fondo de la zapata al nivel 0 |

## 2. Secciones y refuerzo

| Elemento | Sección (m) | Refuerzo longitudinal | Refuerzo transversal |
|---|---|---|---|
| Zapatas aisladas | esquina 1.60 × 1.60, borde 2.00 × 2.00, interior 2.40 × 2.40; h = 0.45 | parrilla #5 @ 0.15 en dos direcciones | — |
| Vigas de cimentación | 0.35 × 0.45 | 3 + 3 #6 continuas | estribos #3 @ 0.15 |
| Columnas piso 1 | 0.45 × 0.45 | 8 #7 | estribos + 2 grapas #3: 0.10 en lo, 0.20 al centro y 0.10 en el nudo |
| Columnas piso 2 | 0.45 × 0.45 | 8 #7 | estribos + 2 grapas #3: 0.10 en lo, 0.20 al centro y 0.10 en el nudo |
| Columnas piso 3 | 0.40 × 0.40 | 8 #6 | estribos + 2 grapas #3: 0.10 en lo, 0.20 al centro y 0.10 en el nudo |
| Columnas piso 4 | 0.40 × 0.40 | 8 #6 | estribos + 2 grapas #3: 0.10 en lo, 0.20 al centro y 0.10 en el nudo |
| Columnas piso 5 | 0.40 × 0.40 | 8 #6 | estribos + 2 grapas #3: 0.10 en lo, 0.20 al centro y 0.10 en el nudo |
| Vigas losa nivel 2 | 0.30 × 0.45 | 2 + 3 #6 continuas, 2 bastones superiores por apoyo | estribos #3: 0.10 en 2h, 0.20 al centro |
| Vigas losa nivel 3 | 0.30 × 0.45 | 2 + 3 #6 continuas, 2 bastones superiores por apoyo | estribos #3: 0.10 en 2h, 0.20 al centro |
| Vigas losa nivel 4 | 0.30 × 0.45 | 2 + 3 #5 continuas, 2 bastones superiores por apoyo | estribos #3: 0.10 en 2h, 0.20 al centro |
| Vigas losa nivel 5 | 0.30 × 0.45 | 2 + 3 #5 continuas, 2 bastones superiores por apoyo | estribos #3: 0.10 en 2h, 0.20 al centro |
| Vigas cubierta | 0.30 × 0.45 | 2 + 3 #5 continuas, 2 bastones superiores por apoyo | estribos #3: 0.10 en 2h, 0.20 al centro |
| Viguetas | @ 0.80, paralelas al eje y | 2 #4 inferiores continuas, 1 bastón #4 por apoyo | sin flejes (S-10) |
| Loseta | — | #3 @ 0.25 en dos direcciones | — |
| Escalera | 2 tramos por piso, ancho 1.20, huella total 2.52 por tramo | #4 @ 0.15 inferior y negativos en los apoyos | #3 @ 0.20 |

## 3. Etapas (Grupo de Ejecución)

| Grupo | Contenido | Diámetros | Piezas | Masa (kg) |
|---|---|---|---|---|
| 1 | Vigas de cimentación; Zapatas; Arranques de columnas | #3, #5, #6, #7 | 1848 | 7760.957 |
| 2 | Columnas piso 1 | #3, #7 | 1600 | 3018.432 |
| 3 | Loseta losa nivel 2; Escalera piso 1; Vigas losa nivel 2; Viguetas losa nivel 2 | #3, #4, #6 | 1804 | 6175.112 |
| 4 | Columnas piso 2 | #3, #7 | 1600 | 3018.432 |
| 5 | Loseta losa nivel 3; Escalera piso 2; Vigas losa nivel 3; Viguetas losa nivel 3 | #3, #4, #6 | 1804 | 6175.112 |
| 6 | Columnas piso 3 | #3, #6 | 1600 | 2165.040 |
| 7 | Loseta losa nivel 4; Escalera piso 3; Vigas losa nivel 4; Viguetas losa nivel 4 | #3, #4, #5 | 1804 | 5357.262 |
| 8 | Columnas piso 4 | #3, #6 | 1600 | 2165.040 |
| 9 | Loseta losa nivel 5; Escalera piso 4; Vigas losa nivel 5; Viguetas losa nivel 5 | #3, #4, #5 | 1804 | 5357.262 |
| 10 | Columnas piso 5 | #3, #6 | 1600 | 1324.680 |
| 11 | Loseta cubierta; Vigas cubierta; Viguetas cubierta | #3, #4, #5 | 1718 | 5214.979 |

## 4. Supuestos de despiece (S-01 a S-14)

Las páginas son las del PDF del Título C publicado por CAMACOL (Decreto 926 de 2010).
Fichas en `docs/tesis-doc/Referencias.md`.

| ID | Supuesto | Valor | Fuente |
|---|---|---|---|
| S-01 | Materiales y factores de ld | f'c = 21 MPa, fy = 420 MPa, ψt = ψe = λ = 1.0 (sin efecto de barra superior) | Supuesto; factores de C.12.2.4, p. C-220 (REF-NSR10-EMPALMES) |
| S-02 | Diámetros y masas nominales | NSR-10, Tabla C.3.5.3-2 | p. C-47 (REF-NSR10-TABLA) |
| S-03 | Recubrimiento libre | zapatas 75 mm; vigas de cimentación 50 mm; vigas y columnas 40 mm; losas, viguetas y escaleras 20 mm | C.7.7.1, pp. C-96 y C-97 (REF-NSR10-GANCHOS-RECUBRIMIENTOS) |
| S-04 | Gancho estándar de 90°: extensión de 12 db; el doblez no se suma | #3 0.15, #4 0.20, #5 0.20, #6 0.25, #7 0.30 m | C.7.1.2, p. C-91 (REF-NSR10-GANCHOS-RECUBRIMIENTOS) |
| S-05 | Estribos cerrados y grapas con ganchos sísmicos de 135° (extensión 6 db, no menor de 75 mm) | se suman 0.10 m por gancho (75 mm más el doblez); estribo = 2(b − 2r) + 2(h − 2r) + 0.20; grapa = (b − 2r) + 0.20 | C.7.1.4, p. C-91, y C.2.2, p. C-33; los 25 mm del doblez son supuesto |
| S-06 | Traslapo clase B = 1.3 ld, no menor de 300 mm; ld del caso favorable: 43.64 db hasta #6 y 53.91 db desde #7 | #3 0.55, #4 0.75, #5 0.95, #6 1.10, #7 1.60 m | C.12.2.2, p. C-218, y C.12.15.1-2, pp. C-240 y C-241 (REF-NSR10-EMPALMES) |
| S-07 | Barras continuas de más de 12 m: tramos de 12.00 m más el resto; si el resto es menor que max(2 traslapos, 2 m) se igualan los dos últimos. No se modela la posición del empalme | — | Supuesto. C.21.3.4.5 (p. C-366) prohíbe traslapos dentro de los nudos: un despiece real los desplaza |
| S-08 | Longitudes redondeadas hacia arriba a 0.05 m | — | Supuesto; 123 de las 137 longitudes de 002 son múltiplos de 0.05 m |
| S-09 | Separaciones | vigas: 0.10 en 2h y 0.20 al centro; columnas: 0.10 en lo = max(ln/6, b, 0.50 m) y 0.20 al centro; nudos 0.10; vigas de cimentación 0.15; parrillas 0.15; viguetas 0.80; loseta 0.25; escalera 0.15 y 0.20, anclaje 0.30 m más gancho | Vigas y columnas dentro de los límites de DMO: C.21.3.4.6 y C.21.3.4.8 (pp. C-366 y C-367), C.21.3.5.6 a C.21.3.5.11 (pp. C-367 a C-369) (REF-NSR10-DMO). El resto es supuesto |
| S-10 | Estribos y grapas #3; sin barras #2; viguetas sin flejes | — | C.7.10.5.1, p. C-103, y C.21.3.5.8; #2 no está en el catálogo de OICA |
| S-11 | Filas agregadas por elemento, diámetro, longitud y etapa | — | Supuesto |
| S-12 | Etapas: 1 cimentación; columnas del piso k en el grupo 2k; losa sobre el piso k en el grupo 2k + 1 | — | Supuesto de secuencia constructiva |
| S-13 | Fuera del modelo: mampostería, cimentación profunda, aberturas de losa, descansos de escalera, acceso a la cubierta, cambios de sección (dobleces) y alambre de amarre | — | Supuesto |
| S-14 | Empalmes de columnas a media altura del piso; arranques desde el fondo de la zapata con gancho; la última barra termina con gancho en la cubierta | — | C.21.3.5.3, p. C-367 (REF-NSR10-DMO): traslapos solo en la mitad central |

## 5. Reglas por elemento

- **Zapatas:** barras por dirección = ⌈(lado − 2r) / s⌉ + 1; longitud = lado − 2r + 2 ganchos.
- **Arranques:** desplante − r + gancho + altura / 2 + traslapo.
- **Columnas:** pisos 1 a 4: altura + traslapo; piso 5: altura / 2 − r + gancho.
- **Vigas y vigas de cimentación:** longitud desarrollada = suma de luces + ancho de columna − 2r + 2 ganchos, dividida según S-07; bastones = un tercio de la luz libre a cada lado del apoyo más el ancho del apoyo (en los extremos, más gancho − r).
- **Viguetas:** por cada luz en x, ⌈(luz − b viga) / s⌉ − 1; barra inferior continua en y y bastones como en vigas.
- **Loseta:** barras rectas de borde a borde en cada dirección, ⌈ancho / s⌉ + 1.
- **Escalera:** longitud inclinada √(huella² + subida²); inferiores con anclaje y gancho en cada extremo; negativos de un cuarto de la inclinada más anclaje y gancho; repartición transversal.

**Ejemplo (estribo de columna del piso 1):** sección 0.45 × 0.45, r = 0.04:
2(0.37) + 2(0.37) + 2(0.10) = 1.68 → 1.70 m.
Altura libre 2.55 m, lo = max(0.425, 0.45, 0.50) = 0.500 m:
24 juegos por columna y piso, incluidos 5 en el nudo.

## 6. Estadísticas

- Filas: **105**. Piezas: **18782**. Masa: **47732.309 kg**.
- Diámetros: #3, #4, #5, #6, #7. Etapas: 11. Longitudes distintas: 30.
- Masa por m² construido: 28.4 kg/m² (dato descriptivo, sin rango de referencia).
- Masa en piezas de longitud comercial (6, 9 o 12 m): 14710.980 kg, 30.8 % (en 002: 26.2 %).

| Diámetro | Filas | Piezas | Masa (kg) | % masa | Longitudes distintas | Mínima (m) | Máxima (m) |
|---|---|---|---|---|---|---|---|
| #3 | 35 | 15208 | 16731.120 | 35.1 | 8 | 0.55 | 12.00 |
| #4 | 28 | 1096 | 5545.924 | 11.6 | 6 | 1.25 | 12.00 |
| #5 | 21 | 1070 | 7313.490 | 15.3 | 9 | 1.85 | 12.00 |
| #6 | 18 | 928 | 11157.344 | 23.4 | 10 | 1.75 | 12.00 |
| #7 | 3 | 480 | 6984.432 | 14.6 | 2 | 4.60 | 5.15 |

La mínima por diámetro es el mínimo reutilizable automático que aplica OICA (menor longitud demandada).

| Longitud (m) | Piezas |
|---|---|
| [0, 1) | 4800 |
| [1, 2) | 9300 |
| [2, 3) | 872 |
| [3, 4) | 512 |
| [4, 5) | 1065 |
| [5, 6) | 485 |
| [6, 7) | 50 |
| [7, 8) | 0 |
| [8, 9) | 0 |
| [9, 10) | 325 |
| [10, 11) | 84 |
| [11, 12] | 1289 |

## 7. Trazabilidad

- SHA-256 del XLSX: `8bdc27acb43def3539e95578878f3ff4d6e0756cf1055b204f35d0799c9e8de6`
- SHA-256 del contenido (filas canónicas): `b8cd43a302121899c1424ccf0f5c757cfbc1b114252499398a0a8bdb328b0bc6`
- Regenerar en memoria y comparar: `PYTHONUTF8=1 python scripts/generar_cartillas_sinteticas.py --verificar`
- Las entradas quedan congeladas tras la revisión del usuario; cualquier cambio posterior lleva un nombre de archivo nuevo.
