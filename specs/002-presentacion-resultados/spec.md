# Feature Specification: Presentación de resultados para el usuario

**Feature Branch**: `002-presentacion-resultados` (sin hook de ramas; rama de trabajo actual `production`)

**Created**: 2026-10-03

**Status**: Draft

**Input**: User description: "Mejorar la presentación de los resultados que la aplicación muestra al usuario (Excel, PDF, imagen de nesting y pantalla de detalle), sin alterar el plan de corte ni el formato del inventario final reimportable. Decisiones aprobadas por el usuario el 2026-10-03: (1) Excel: nueva hoja «Resumen» al inicio con indicadores legibles (indicador, valor, unidad) y una tabla «Totales de compra» por diámetro y total general (la hoja «Resumen de compra» queda sin filas de total para no romper el auditor); nueva hoja «Trazabilidad» con los datos técnicos (valido, escala, motor, huella, semilla, perfil, método, tiempos, versión del análisis, cota ajustada); se elimina «Metricas»; orden de hojas: Resumen, Resumen de compra, Patrones, Cortes, Barras, Descartados, Admisibilidad, Cota, Avisos, Inventario, Inventario excluido, Parámetros, Trazabilidad; se quita stock_id de Barras; parámetros en formato legible; barras_minimas renombrada a barras mínimas teóricas de la cota simple. (2) PDF: nuevo orden (encabezado con proyecto, versión, perfil y fecha; plan verificado; indicadores clave; resumen de compra con totales; patrones con la imagen de nesting incrustada y una línea de cobertura «se muestran N de M patrones que cubren B de T barras»; desperdicio y admisibilidad por diámetro; calidad con cota y brecha; avisos; datos técnicos legibles al final), coma decimal y menos decimales. El límite de 150 es de patrones, no de barras. (3) Imagen: longitud escrita sobre cada pieza cuando cabe, leyenda de etapas y de pérdida/descarte/reutilizable, 200 dpi, se mantiene el tope de 60 patrones y se informa la cobertura de barras. (4) Pantalla: nueva sección «Patrones de corte» con los 10 más repetidos (incluida su secuencia por etapa) y vista previa de la imagen; totales en el resumen de compra (compra separada del inventario adicional); se quita la tarjeta «cota simple» de la pantalla. El resumen persistido de patrones debe incluir la secuencia, con nueva versión del análisis (analisis-2); las versiones históricas muestran «no disponible» donde falte un dato y sus artefactos no se modifican. Los 136 ensayos y 12 controles deben seguir con 0 diferencias."

## Contexto

La spec 001 añadió a la aplicación el resumen de compra, los patrones de corte, la cota inferior,
la admisibilidad y los avisos de masa. La revisión con el autor (2026-10-03) mostró que esos
resultados existen, pero se presentan pensando en quien los programó y no en quien los usa:

- En el Excel, los indicadores útiles están mezclados con datos técnicos en una sola hoja, los
  parámetros aparecen en un formato de programación, hay un código interno del catálogo que no
  le dice nada al usuario, la compra no tiene totales y la primera hoja es el listado barra por
  barra.
- En el PDF, los datos técnicos aparecen al principio y la compra casi al final. No dice la fecha,
  el perfil ni la versión, no incluye la imagen del nesting y usa punto decimal con tres o cuatro
  decimales.
- En la imagen, no se leen las longitudes de las piezas, no hay leyenda de etapas y la resolución
  es baja para imprimir.
- En la pantalla, los patrones de corte (término del título de la tesis) solo están disponibles
  como descarga, la compra no tiene totales y la «cota simple» muestra un valor (0,0069 % en la
  cartilla 002) que desconcierta a quien no conoce el concepto.

Esta funcionalidad reorganiza y completa esa presentación. **No cambia el plan de corte**: el
algoritmo genético, sus métricas y los 136 ensayos y 12 controles de la línea base siguen igual.
El archivo de inventario final conserva su formato, porque es el que se vuelve a importar en el
siguiente proyecto (objetivo específico 3). Las versiones ya procesadas y sus archivos no se
modifican.

Actores:

- **Planificador de obra**: necesita saber primero qué comprar, cuánto desperdicio queda y si es
  admisible.
- **Taller de corte**: necesita leer los patrones y las medidas de cada pieza.
- **Autor de la tesis y jurado**: necesitan trazabilidad (versión, semilla, huella, parámetros) y
  ver en la aplicación web los términos del título.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ver primero lo que hay que comprar y los indicadores clave (Priority: P1)

El planificador abre el Excel o el PDF de una versión y encuentra al principio un resumen legible:
barras y kilogramos a comprar (por diámetro y en total), desperdicio, aprovechamiento,
admisibilidad, pérdida irrecuperable, saldo reutilizable, cota y brecha, y si el plan está
verificado. Los datos técnicos siguen disponibles, pero al final.

**Why this priority**: es lo que decide la compra (objetivo específico 1) y lo primero que lee
cualquier usuario. Hoy ese dato está repartido entre varias hojas o al final del PDF.

**Independent Test**: procesar la cartilla 001, abrir el Excel y comprobar que la primera hoja es
«Resumen» con los totales de compra; abrir el PDF y comprobar que la primera página contiene los
indicadores clave y el resumen de compra con totales.

**Acceptance Scenarios**:

1. **Given** una versión nueva, **When** se abre el Excel, **Then** las hojas aparecen en el orden
   Resumen, Resumen de compra, Patrones, Cortes, Barras, Descartados, Admisibilidad, Cota, Avisos,
   Inventario, Inventario excluido, Parámetros y Trazabilidad.
2. **Given** la hoja «Resumen», **When** se lee, **Then** cada indicador tiene un nombre legible,
   un valor y una unidad. Debajo aparece la tabla «Totales de compra» con barras y kilogramos por
   diámetro (solo compra), barras tomadas del inventario adicional y total general.
3. **Given** cualquier plan, **When** se suman las filas de la hoja «Resumen de compra», **Then**
   coinciden con los totales de la hoja «Resumen», y la hoja de detalle no contiene filas de total.
4. **Given** una versión nueva, **When** se abre el PDF, **Then** empieza con proyecto, versión,
   perfil y fecha de generación, el estado de verificación, los indicadores clave y el resumen de
   compra con totales, en ese orden.
5. **Given** el PDF, **When** se leen sus cifras, **Then** usan coma decimal y dos decimales, salvo
   la cota y la brecha, que usan tres.

---

### User Story 2 - Leer los patrones de corte y sus medidas para el taller (Priority: P2)

El taller abre el PDF o la imagen y ve los patrones más repetidos dibujados pieza por pieza, con
la longitud escrita sobre cada pieza cuando cabe, una leyenda de qué color corresponde a cada
etapa y qué representan la pérdida por corte, el descarte y el saldo reutilizable. Cada vista
indica cuántos patrones y cuántas barras representa del total.

**Why this priority**: respalda «patrones de corte» y «nesting» del título y es la instrucción que
el taller ejecuta. Hoy las piezas no tienen medida legible y la imagen no está en el PDF.

**Independent Test**: procesar la cartilla 002, abrir el PDF y comprobar que incluye la imagen y
la tabla de los 136 patrones con la línea de cobertura «136 de 136 patrones, 13.955 de 13.955
barras (100 %)». En la imagen, comprobar la leyenda, las longitudes legibles y una línea de
cobertura con menos del 100 % de los patrones (60 de 136).

**Acceptance Scenarios**:

1. **Given** un plan con hasta 150 patrones distintos, **When** se abre el PDF, **Then** la tabla
   muestra todos los patrones, y la línea de cobertura indica el 100 % de patrones y de barras.
2. **Given** un plan con más de 150 patrones distintos, **When** se abre el PDF, **Then** muestra
   los 150 más repetidos, cuántos se omitieron y qué proporción de barras cubren los mostrados.
3. **Given** cualquier plan, **When** se abre la imagen, **Then** muestra como máximo los 60
   patrones más repetidos, con la longitud escrita sobre cada pieza cuyo ancho lo permite, una
   leyenda de etapas y de pérdida por corte, descarte y saldo reutilizable, y la cobertura de
   patrones y barras.
4. **Given** el PDF, **When** se imprimen sus páginas de nesting en A4, **Then** cada página
   muestra como máximo 18 patrones y las medidas son legibles. La imagen suelta se lee en
   pantalla al 100 %.
5. **Given** la cobertura informada en el PDF o en la imagen, **When** se suman las repeticiones
   de los patrones mostrados, **Then** coinciden con el número de barras declarado.

---

### User Story 3 - Ver patrones y totales de compra en la aplicación web (Priority: P3)

El usuario abre el detalle de una versión en la aplicación web y encuentra una sección «Patrones
de corte» con el total de patrones y barras, los diez patrones más repetidos con su secuencia por
etapa, y una vista previa de la imagen. El resumen de compra muestra totales por diámetro y total
general, separando lo que se compra de lo que se toma del inventario. La sección de calidad
presenta la cota por patrones y la brecha, sin la tarjeta de «cota simple».

**Why this priority**: hace visibles en la web los términos «patrones de corte» y «nesting» del
título, y completa la compra en pantalla. Depende de que el resumen guardado incluya la secuencia
de cada patrón.

**Independent Test**: procesar la cartilla 001 y abrir su detalle: comprobar la sección de
patrones con su tabla y su imagen, los totales de compra y la ausencia de la tarjeta de cota
simple. Abrir una versión procesada antes de esta funcionalidad y comprobar que todo se muestra
sin errores, con «no disponible» donde falte un dato.

**Acceptance Scenarios**:

1. **Given** una versión nueva, **When** se abre su detalle, **Then** aparece la sección «Patrones
   de corte» entre el resumen de compra y la calidad del plan, con el total de patrones y barras,
   la tabla de los diez más repetidos (patrón, diámetro, barra, secuencia por etapa, repeticiones,
   aprovechamiento) y la vista previa de la imagen con un texto alternativo descriptivo.
2. **Given** el resumen de compra en pantalla, **When** se lee, **Then** incluye el total por
   diámetro y el total general de lo comprado, y las barras del inventario adicional aparecen
   aparte.
3. **Given** la sección de calidad, **When** se lee, **Then** muestra la cota por patrones y la
   brecha. La cota simple solo aparece como una frase explicativa, no como una cifra destacada.
4. **Given** una versión procesada con la versión anterior del análisis, **When** se abre su
   detalle, **Then** la secuencia de los patrones aparece como «no disponible» y el resto de la
   página funciona.
5. **Given** una versión sin imagen, **When** se abre su detalle, **Then** la vista previa se
   sustituye por un aviso y la tabla de patrones sigue visible.
6. **Given** la pantalla en un teléfono, **When** se abre el detalle, **Then** la tabla de
   patrones se presenta como tarjetas legibles, sin desplazamiento horizontal de la página.

---

### User Story 4 - Conservar la trazabilidad técnica y la compatibilidad (Priority: P4)

El autor y el jurado encuentran en una hoja «Trazabilidad» y en la sección final del PDF los datos
técnicos que permiten reproducir el resultado (versión del motor y del análisis, huella de la
entrada, semilla, perfil, método, tiempos, validez, escala y si la cota quedó ajustada), y en la
hoja «Parámetros» las condiciones de corte escritas en lenguaje normal. Las herramientas de
auditoría y la reimportación del inventario siguen funcionando, y los resultados de la línea base
no cambian.

**Why this priority**: es la condición de validez académica (constitución, Principio III). No
aporta funciones nuevas al usuario final, pero ninguna de las otras historias puede romperla.

**Independent Test**: comparar la línea base de 148 registros con 0 diferencias; auditar una
versión nueva y una histórica; reimportar el inventario final de una versión nueva.

**Acceptance Scenarios**:

1. **Given** una versión nueva, **When** se abre la hoja «Trazabilidad», **Then** contiene todos
   los datos técnicos que antes estaban en «Metricas» y que no pasaron a «Resumen».
2. **Given** la hoja «Parámetros», **When** se lee, **Then** cada condición aparece en una fila con
   su descripción legible (por ejemplo, «Pérdida por corte: disco, 1 mm» o «Mínimo reutilizable:
   automático, #3 0,37 m…») y la referencia correspondiente en una columna aparte.
3. **Given** la hoja «Barras», **When** se lee, **Then** no incluye el código interno del catálogo,
   y conserva barra, patrón, diámetro, origen, longitud, piezas, pérdida, descarte y saldo.
4. **Given** la hoja «Cota», **When** se lee, **Then** la columna de barras mínimas se identifica
   como barras mínimas teóricas de la cota simple.
5. **Given** la línea base de 136 ensayos y 12 controles, **When** se reproduce con el código
   nuevo, **Then** se obtienen 0 diferencias en el plan y en sus métricas.
6. **Given** una versión nueva y una histórica, **When** se auditan, **Then** ambas pasan la
   auditoría independiente.
7. **Given** el inventario final de una versión nueva, **When** se importa en otro proyecto,
   **Then** se acepta sin cambios, con las mismas columnas que antes.

---

### Edge Cases

- Plan sin inventario adicional: la tabla «Totales de compra» no muestra una fila de inventario, o
  la muestra en cero, sin errores.
- Plan con más de 150 patrones distintos: el PDF muestra los 150 más repetidos con su cobertura y
  el número de omitidos; el Excel conserva todos.
- Plan con más de 60 patrones distintos: la imagen muestra los 60 más repetidos y su cobertura,
  con un tamaño acotado.
- Pieza demasiado corta para rotular su longitud: se dibuja sin texto; la medida sigue en la tabla
  de patrones y en el Excel.
- Plan sin umbral de desperdicio admisible: los indicadores muestran «sin evaluar», sin errores.
- Cota no disponible o no ajustada: el resumen y el PDF lo indican con su motivo.
- Versión procesada antes de la spec 001 (sin análisis): el detalle y las descargas existentes
  funcionan; las secciones nuevas muestran «no disponible».
- Versión procesada con la versión anterior del análisis: sin secuencia en los patrones de la
  pantalla; se muestra «no disponible» en esa columna.
- Procesamiento sin artefactos visuales (sin PDF ni imagen): el Excel y el inventario se generan
  igual; la pantalla indica que no hay imagen.
- Nombre del proyecto con caracteres especiales: el encabezado del PDF los muestra de forma
  segura, sin romper el documento.
- Inventario adicional consumido en parte: los totales de compra no cuentan las barras del
  inventario como compra.

## Requirements *(mandatory)*

### Functional Requirements

**Excel**

- **FR-001**: El Excel de una versión nueva MUST presentar sus hojas en este orden: Resumen,
  Resumen de compra, Patrones, Cortes, Barras, Descartados, Admisibilidad, Cota, Avisos,
  Inventario, Inventario excluido, Parámetros y Trazabilidad.
- **FR-002**: La hoja «Resumen» MUST contener indicadores con nombre legible, valor y unidad, al
  menos: piezas, barras, masa de barras usadas, masa en piezas, pérdida por corte, descartado,
  pérdida irrecuperable (kg y %), saldo reutilizable (kg y %), desperdicio en masa, aprovechamiento,
  umbral y estado de admisibilidad, cota por patrones, brecha y estado de verificación.
- **FR-003**: La hoja «Resumen» MUST incluir la tabla «Totales de compra»: barras y kilogramos
  comprados por diámetro, barras y kilogramos tomados del inventario adicional, y total general
  comprado. Los totales MUST coincidir con la suma de la hoja «Resumen de compra».
- **FR-004**: La hoja «Resumen de compra» MUST conservar una fila por diámetro, longitud y origen,
  sin filas de total.
- **FR-005**: La hoja «Trazabilidad» MUST contener: validez, escala de longitudes, versión del
  motor, huella de la entrada, semilla, perfil, método, duración del motor, duración del análisis,
  versión del análisis y si la cota quedó ajustada. La hoja «Metricas» MUST dejar de generarse en
  las versiones nuevas.
- **FR-006**: La hoja «Barras» MUST NOT incluir el código interno del catálogo, y MUST conservar el
  resto de sus columnas.
- **FR-007**: La hoja «Parámetros» MUST presentar una fila por condición de corte con su
  descripción legible y, en una columna aparte, su referencia cuando exista.
- **FR-008**: En la hoja «Cota», la columna de barras mínimas MUST identificarse como barras
  mínimas teóricas de la cota simple.

**PDF**

- **FR-009**: El PDF MUST presentar, en este orden: encabezado (proyecto, versión, perfil y fecha
  de generación); estado de verificación; indicadores clave (barras y kilogramos a comprar,
  desperdicio, aprovechamiento, admisibilidad); resumen de compra con totales; patrones de corte
  con la imagen de nesting incluida; desperdicio y admisibilidad por diámetro; calidad (cota y
  brecha); avisos de masa; y datos técnicos legibles (parámetros, motor, método, semilla, huella).
- **FR-010**: El PDF MUST mostrar todos los patrones cuando no superan 150; si los superan, MUST
  mostrar los 150 más repetidos y el número de omitidos. En ambos casos MUST incluir la línea de
  cobertura: patrones mostrados frente al total, y barras representadas frente al total, con su
  porcentaje.
- **FR-011**: Las cifras del PDF dirigidas al usuario MUST usar coma decimal, con dos decimales
  en general y tres en la cota y la brecha.

**Imagen**

- **FR-012**: La imagen MUST mostrar como máximo los 60 patrones más repetidos, con la longitud
  escrita sobre cada pieza cuyo ancho lo permita (con coma decimal) y una leyenda de las etapas
  presentes, la pérdida por corte, el descarte y el saldo reutilizable.
- **FR-013**: La imagen MUST incluir la línea de cobertura de patrones y barras, y tener una
  resolución de 200 puntos por pulgada, con medidas legibles al verla al 100 %. Para imprimir en
  A4, el PDF MUST presentar el mismo nesting por páginas de como máximo 18 patrones, con las
  medidas legibles a escala casi real.
- **FR-014**: El tamaño de la imagen MUST permanecer acotado por un máximo fijo (9 megapíxeles),
  sin importar el número de barras del plan.

**Pantalla**

- **FR-015**: El detalle de una versión MUST incluir una sección «Patrones de corte», entre el
  resumen de compra y la calidad del plan, con el total de patrones y barras, los diez patrones
  más repetidos (patrón, diámetro, barra, secuencia por etapa, repeticiones, aprovechamiento) y
  una vista previa de la imagen con texto alternativo.
- **FR-016**: El resumen de compra en pantalla MUST mostrar el total por diámetro y el total
  general de lo comprado, separando las barras del inventario adicional.
- **FR-017**: La sección de calidad MUST mostrar la cota por patrones y la brecha. La cota simple
  MUST NOT aparecer como cifra destacada; MAY mencionarse en una frase explicativa.
- **FR-018**: En un teléfono, la tabla de patrones MUST presentarse como tarjetas, sin
  desplazamiento horizontal de la página, y la sección MUST cumplir las reglas de accesibilidad del
  sistema visual del proyecto.

**Datos del análisis y compatibilidad**

- **FR-019**: El resumen guardado de cada versión nueva MUST incluir la secuencia legible por
  etapa de cada uno de los patrones más repetidos, y la versión del análisis MUST identificarse
  como `analisis-2`.
- **FR-020**: Las versiones procesadas antes de esta funcionalidad MUST mostrarse sin error. Los
  datos que les falten MUST aparecer como «no disponible», y sus archivos ya generados MUST NOT
  modificarse.
- **FR-021**: El plan de corte y sus métricas MUST NOT cambiar: la línea base de 136 ensayos y
  12 controles MUST reproducirse con 0 diferencias.
- **FR-022**: El archivo de inventario final MUST conservar exactamente su formato actual.
- **FR-023**: La auditoría independiente de versiones guardadas MUST seguir funcionando para
  versiones nuevas e históricas.

### Key Entities

- **Indicador del resumen**: nombre legible, valor y unidad de una métrica del plan, dirigida al
  usuario final.
- **Totales de compra**: barras y masa por diámetro y en total, separando compra comercial e
  inventario adicional; se deriva del resumen de compra y coincide con él.
- **Dato de trazabilidad**: valor técnico necesario para reproducir una versión (versiones,
  huella, semilla, perfil, método, tiempos, validez, escala, ajuste de la cota).
- **Condición de corte legible**: descripción en lenguaje normal de un parámetro resuelto (pérdida
  por corte, mínimo reutilizable, momento del descarte) con su referencia.
- **Cobertura**: patrones mostrados frente al total, y barras representadas por ellos frente al
  total de barras del plan.
- **Patrón resumido**: patrón de los más repetidos, con su secuencia legible por etapa, guardado
  con la versión.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El planificador encuentra el total de barras y kilogramos a comprar en la primera
  hoja del Excel y en la primera página del PDF, sin consultar otra hoja ni otra página.
- **SC-002**: En el 100 % de las versiones nuevas, los totales de compra coinciden con la suma del
  detalle de compra y con el número de barras del plan.
- **SC-003**: En el 100 % de las vistas acotadas (PDF e imagen), la cobertura informada coincide
  con la suma de repeticiones de los patrones mostrados. En la cartilla 002, el PDF cubre el 100 %
  de las barras.
- **SC-004**: La reproducción de la línea base (136 ensayos y 12 controles) da 0 diferencias.
- **SC-005**: El 100 % de las versiones históricas consultadas se abre sin errores en pantalla y
  pasa la auditoría independiente.
- **SC-006**: La sección de patrones en pantalla no introduce nuevas barreras de accesibilidad en
  escritorio, tableta y teléfono, según la verificación automática del proyecto.
- **SC-007**: El tiempo total de procesamiento de la cartilla 002 no aumenta más de 10 % respecto
  de la medición vigente con la misma configuración.
- **SC-008**: Las medidas escritas sobre las piezas son legibles en las páginas de nesting del PDF
  impreso en A4 y en la imagen vista al 100 %.

## Assumptions

- Son cambios de presentación: el algoritmo genético, la normalización, la validación y los
  parámetros del modelo no se tocan, así que no hace falta una nueva versión del motor.
- La nueva versión del análisis (`analisis-2`) solo añade la secuencia de los patrones más
  repetidos; no cambia ningún otro cálculo del análisis.
- La fecha del encabezado del PDF es la de generación del documento; no forma parte de la
  identidad del problema ni afecta la reproducibilidad del plan.
- La vista previa de la pantalla usa la misma imagen que se descarga.
- Los contratos de artefactos y de pantalla de la spec 001 quedan sustituidos por los de esta
  funcionalidad en lo que cambie. La spec 001 llevará una nota que lo indique.
- La prueba de extremo a extremo en la aplicación local requiere reconstruir las imágenes de los
  contenedores. Por la restricción de espacio en disco, se pedirá aprobación con una estimación
  antes de hacerlo.
- La línea base de tiempo para SC-007 es la medición controlada vigente
  (`tests/benchmarks/2026-10-02-sc007-comparacion.json`, mediana total de 26,75 s para la 002 con
  el perfil balanceado y la semilla 0).
- Rigen la constitución v1.0.0 y `CLAUDE.md`: sin commits sin instrucción explícita,
  documentación en español, cartillas anonimizadas.
