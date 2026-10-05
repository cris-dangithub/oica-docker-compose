# Feature Specification: Presentación de resultados para el usuario

**Feature Branch**: `feat/spec-002-presentacion-resultados` (sin hook de ramas)

**Created**: 2026-10-03 · **Amended**: 2026-10-04

**Status**: Implementada y cerrada (2026-10-04). En producción con el PR #7 (`5b1e2d5`); enmiendas 1 (explorador de patrones), 2 (estándar numérico) y 3 (punto decimal, sin separador de miles). Enmienda 4 (nombres de descarga, FR-036) implementada en la rama `fix/nombres-descarga`, pendiente de PR.

**Input**: User description: "Mejorar la presentación de los resultados que la aplicación muestra al usuario (Excel, PDF, imagen de nesting y pantalla de detalle), sin alterar el plan de corte ni el formato del inventario final reimportable. Decisiones aprobadas por el usuario el 2026-10-03: (1) Excel: nueva hoja «Resumen» al inicio con indicadores legibles (indicador, valor, unidad) y una tabla «Totales de compra» por diámetro y total general (la hoja «Resumen de compra» queda sin filas de total para no romper el auditor); nueva hoja «Trazabilidad» con los datos técnicos (valido, escala, motor, huella, semilla, perfil, método, tiempos, versión del análisis, cota ajustada); se elimina «Metricas»; orden de hojas: Resumen, Resumen de compra, Patrones, Cortes, Barras, Descartados, Admisibilidad, Cota, Avisos, Inventario, Inventario excluido, Parámetros, Trazabilidad; se quita stock_id de Barras; parámetros en formato legible; barras_minimas renombrada a barras mínimas teóricas de la cota simple. (2) PDF: nuevo orden (encabezado con proyecto, versión, perfil y fecha; plan verificado; indicadores clave; resumen de compra con totales; patrones con la imagen de nesting incrustada y una línea de cobertura «se muestran N de M patrones que cubren B de T barras»; desperdicio y admisibilidad por diámetro; calidad con cota y brecha; avisos; datos técnicos legibles al final), coma decimal y menos decimales. El límite de 150 es de patrones, no de barras. (3) Imagen: longitud escrita sobre cada pieza cuando cabe, leyenda de etapas y de pérdida/descarte/reutilizable, 200 dpi, se mantiene el tope de 60 patrones y se informa la cobertura de barras. (4) Pantalla: nueva sección «Patrones de corte» con los 10 más repetidos (incluida su secuencia por etapa) y vista previa de la imagen; totales en el resumen de compra (compra separada del inventario adicional); se quita la tarjeta «cota simple» de la pantalla. El resumen persistido de patrones debe incluir la secuencia, con nueva versión del análisis (analisis-2); las versiones históricas muestran «no disponible» donde falte un dato y sus artefactos no se modifican. Los 136 ensayos y 12 controles deben seguir con 0 diferencias."

**Enmienda 2026-10-04** (decisiones aprobadas por el usuario el 2026-10-04): "Incluir en la
pantalla de detalle un explorador interactivo con **todos** los patrones de corte de la versión
(por ejemplo, los 136 de la cartilla 002), dibujados pieza por pieza, con filtros (diámetro,
etapa, origen y pedido) y un detalle por patrón: secuencia, longitud de cada pieza, pedidos que
atiende, repeticiones y barras que lo usan. (1) Se enmienda esta spec; no se crea otra. La
sección estática de los diez más repetidos con la vista previa de la imagen se **sustituye** por
el explorador. (2) Alcance: solo visualización, sin guardar estado; el chequeo de taller (marcar
patrones cortados) queda fuera. (3) Prioridad P2: después de la compra e indicadores (P1) y antes
del nesting de los archivos, de la compra en pantalla y de la trazabilidad." Consecuencia,
confirmada en las aclaraciones: la versión `analisis-2` se retira, porque el explorador obtiene
la secuencia de los datos ya guardados de cada versión (FR-019 queda retirado).

**Enmienda 2 (2026-10-04, formato numérico)** (decisión del usuario): "No hay una definición de
cómo usamos comas o puntos. Dices que el formato es coma decimal y punto de miles, pero en algunas
tablas se ve, por ejemplo, «5.154% en masa». No hay un estándar en la app, y hay que aplicarlo en
toda la app." La spec define un estándar numérico único (FR-032 a FR-035) para todo lo que lee el
usuario: pantalla, PDF, imagen, textos legibles del Excel y mensajes. Los datos para máquinas
(API, JSON, celdas numéricas del Excel, inventario reimportable) siguen con números nativos.

**Enmienda 3 (2026-10-04, separadores)** (decisión del usuario): "Entonces deberíamos de usar sin
separador de miles y punto decimal para toda la app". El motivo es la coherencia con el documento
de tesis, cuya plantilla USCO usa punto decimal y miles sin separador. FR-032 cambia de coma decimal
y punto de miles a **punto decimal y sin separador de miles**. Los decimales por tipo de cifra
(FR-033), el espacio antes de la unidad, las entradas que aceptan coma o punto (FR-034) y los datos
nativos (FR-035) no cambian.

**Enmienda 4 (2026-10-04, nombres de descarga)** (decisión del usuario): "Al descargar cualquiera
de estos archivos, se descargan con un nombre larguísimo que no tiene sentido". Los archivos se
llamaban con el identificador interno de la versión (`plan_corte_<uuid de 36 caracteres>.pdf`), y el
inventario siempre como `inventario_final.xlsx`. El usuario eligió el formato
`OICA_<proyecto>_v<versión>_<perfil>_<tipo>.<ext>` (FR-036). Solo cambia el nombre que recibe el
navegador: el contenido de los archivos, sus nombres en disco y las rutas de descarga no cambian.

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
- Ninguna salida permite **explorar** los patrones: el Excel los lista, el PDF y la imagen
  muestran una selección fija, y no hay forma de preguntar qué patrones atienden un pedido, qué
  barras usan un patrón o cómo se reparten por diámetro y etapa (enmienda 2026-10-04).

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
  ver en la aplicación web los términos del título. En la sustentación, el autor recorre en vivo
  los patrones del proyecto real.

## Clarifications

### Session 2026-10-04

- Q: ¿Se retira `analisis-2`, de modo que el análisis guardado no cambie y el explorador obtenga
  la secuencia de los datos ya guardados? → A: Sí. Se retira `analisis-2` y el análisis
  conserva su versión vigente (FR-019 retirado; FR-025).
- Q: ¿Con qué escala se dibujan los patrones en el explorador? → A: Escala común para todos: la
  barra más larga del plan ocupa el 100 % del ancho, y la escala no cambia al filtrar (FR-026).
- Q: ¿Cómo se muestran las barras de un patrón que se repite cientos o miles de veces? → A: Total
  siempre visible, identificadores agrupados en rangos consecutivos y presentados por tramos de
  100 con «Ver más». La pantalla nunca dibuja ni carga de una vez todos los identificadores de un
  patrón grande, para no afectar el rendimiento del navegador (FR-028, SC-012).
- Q: ¿En qué orden aparecen los patrones al abrir el explorador? → A: Por defecto, el orden del
  Excel (diámetro y, dentro de cada uno, repeticiones de mayor a menor). Un selector permite
  ordenar por repeticiones, aprovechamiento o saldo (FR-031).
- Q: ¿Cómo funciona el filtro por pedido? → A: Es un campo de búsqueda con sugerencias de los
  pedidos que existen en la versión. Se elige un pedido a la vez, y cada patrón mostrado indica
  cuántas piezas de ese pedido aporta (FR-027).
- Q: ¿Qué formato numérico usa la aplicación? → A: Uno solo en toda la app, para todo lo que lee el
  usuario: **punto decimal y sin separador de miles** (enmienda 3, por coherencia con la plantilla
  USCO de la tesis; reemplaza la coma decimal y el punto de miles de la enmienda 2). Además,
  espacio antes de la unidad y una cantidad fija de decimales por tipo de cifra. Las entradas
  aceptan coma o punto, y los datos para máquinas siguen con números nativos (FR-032 a FR-035).

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

### User Story 2 - Explorar todos los patrones de corte en la aplicación web (Priority: P2)

<!-- Nueva en la enmienda 2026-10-04. Sustituye la sección estática de patrones de la antigua US3. -->

El usuario abre el detalle de una versión y, en la sección «Patrones de corte», ve **todos** los
patrones del plan dibujados como barras: cada pieza con el color de su etapa, y la pérdida por
corte, el descarte y el saldo reutilizable al final. Puede filtrar por diámetro, etapa, origen
(compra o inventario adicional) y pedido. Al seleccionar un patrón, con el ratón o con el
teclado, ve su detalle: la secuencia por etapa, la longitud de cada pieza y los pedidos que
atiende (con cuántas piezas de cada uno), las repeticiones, el aprovechamiento, las barras que lo
usan y el desglose de pérdida, descarte y saldo.

**Why this priority**: es la forma más directa de mostrar «nesting» y «patrones de corte» (dos
términos del título) sobre el proyecto real, tanto al taller como al jurado en la sustentación.
Responde preguntas que ninguna salida fija responde, como qué patrones atienden un pedido. Solo
necesita los datos que cada versión ya guarda, sin volver a ejecutar el algoritmo.

**Independent Test**: abrir el detalle de una versión de la cartilla 002 y comprobar que el
explorador muestra 136 patrones y 13.955 barras. Filtrar por un diámetro y por un pedido, y
comprobar la línea «N de M patrones, B de T barras». Seleccionar un patrón con el teclado y
contrastar su identificador, sus repeticiones y su secuencia con la hoja «Patrones» del Excel de
esa misma versión.

**Acceptance Scenarios**:

1. **Given** una versión con plan guardado, **When** se abre su detalle, **Then** la sección
   «Patrones de corte», entre el resumen de compra y la calidad del plan, muestra el total de
   patrones y de barras. Todos los patrones están disponibles en la lista, dibujados a escala con
   su identificador (`P-<diámetro>-<nnn>`) y sus repeticiones, y se pintan por tramos con
   «Mostrar más patrones» para no cargar la pantalla.
2. **Given** el explorador, **When** se aplica un filtro por diámetro, etapa, origen o pedido,
   **Then** solo quedan los patrones que cumplen todos los filtros activos, y la línea de
   cobertura indica cuántos patrones y barras se muestran frente al total. Un filtro sin
   resultados muestra un mensaje claro, no una lista vacía.
3. **Given** un patrón, **When** se selecciona con el ratón o con el teclado, **Then** el detalle
   muestra su secuencia por etapa, la longitud de cada pieza, los pedidos que atiende con su
   cantidad de piezas, las repeticiones, el aprovechamiento, la pérdida por corte, el descarte, el
   saldo y los identificadores de las barras que lo usan.
4. **Given** cualquier versión, **When** se comparan el explorador y la hoja «Patrones» del Excel
   de esa versión, **Then** coinciden los identificadores, las repeticiones y las secuencias, y la
   suma de repeticiones es igual al número de barras del plan.
5. **Given** un teléfono, **When** se abre el explorador, **Then** los patrones se presentan como
   una lista legible, sin desplazamiento horizontal de la página, y el detalle se puede abrir y
   cerrar con el teclado y con un lector de pantalla.
6. **Given** una versión sin plan guardado que se pueda reconstruir (por ejemplo, del motor
   histórico), **When** se abre su detalle, **Then** la sección indica «Patrones: no disponible
   para esta versión» y el resto de la página funciona.
7. **Given** el explorador, **When** se busca la imagen de nesting, **Then** sigue disponible su
   descarga, aunque la pantalla ya no la muestre como vista previa.

---

### User Story 3 - Leer los patrones de corte y sus medidas para el taller (Priority: P3)

<!-- Antes US2 (P2); renumerada en la enmienda 2026-10-04 sin cambios de fondo. -->


El taller abre el PDF o la imagen y ve los patrones más repetidos dibujados pieza por pieza, con
la longitud escrita sobre cada pieza cuando cabe, una leyenda de qué color corresponde a cada
etapa y qué representan la pérdida por corte, el descarte y el saldo reutilizable. Cada vista
indica cuántos patrones y cuántas barras representa del total.

**Why this priority**: respalda «patrones de corte» y «nesting» del título y es la instrucción que
el taller ejecuta. Hoy las piezas no tienen medida legible y la imagen no está en el PDF.

**Independent Test**: procesar la cartilla 002, abrir el PDF y comprobar que incluye la imagen y
la tabla de los 136 patrones con la línea de cobertura «136 de 136 patrones, 13955 de 13955
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

### User Story 4 - Ver los totales de compra y la calidad del plan en la aplicación web (Priority: P4)

<!-- Antes US3 (P3). En la enmienda 2026-10-04, la sección de patrones pasó a la US2 (explorador). -->

El usuario abre el detalle de una versión y el resumen de compra muestra totales por diámetro y
total general, separando lo que se compra de lo que se toma del inventario. La sección de calidad
presenta la cota por patrones y la brecha, sin la tarjeta de «cota simple».

**Why this priority**: completa en pantalla la compra (objetivo específico 1) y evita una cifra
que confunde. Es un cambio pequeño e independiente del explorador.

**Independent Test**: procesar la cartilla 001 y abrir su detalle: comprobar los totales de
compra y la ausencia de la tarjeta de cota simple. Abrir una versión procesada antes de esta
funcionalidad y comprobar que todo se muestra sin errores, con «no disponible» donde falte un
dato.

**Acceptance Scenarios**:

1. **Given** el resumen de compra en pantalla, **When** se lee, **Then** incluye el total por
   diámetro y el total general de lo comprado, y las barras del inventario adicional aparecen
   aparte.
2. **Given** la sección de calidad, **When** se lee, **Then** muestra la cota por patrones y la
   brecha. La cota simple solo aparece como una frase explicativa, no como una cifra destacada.
3. **Given** la pantalla en un teléfono, **When** se abre el detalle, **Then** los totales de
   compra se leen sin desplazamiento horizontal de la página.

---

### User Story 5 - Conservar la trazabilidad técnica y la compatibilidad (Priority: P5)

<!-- Antes US4 (P4); renumerada en la enmienda 2026-10-04 sin cambios de fondo. -->

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
- Procesamiento sin artefactos visuales (sin PDF ni imagen): el Excel y el inventario se generan
  igual; el explorador funciona, porque no depende de la imagen, y la descarga de la imagen
  indica que no está disponible.
- Versión del motor histórico, o sin plan guardado que se pueda reconstruir: el explorador
  muestra «Patrones: no disponible para esta versión», sin errores.
- Plan con cientos de patrones distintos (por ejemplo, el caso de prueba de 340): el explorador
  sigue respondiendo y se puede usar con el teclado; la carga se reparte por páginas o por tramos
  visibles, sin bloquear la pantalla.
- Patrón con cientos o miles de repeticiones: el detalle muestra el total, agrupa los
  identificadores en rangos y los presenta por tramos de 100 con «Ver más» (FR-028).
- Pieza demasiado corta para rotular en el dibujo: se dibuja sin texto, y su medida aparece en el
  detalle del patrón.
- Pedido presente en muchos patrones: el filtro por pedido los muestra todos, con la cobertura de
  barras correspondiente.
- Filtros sin resultados: el explorador lo dice explícitamente y ofrece quitar los filtros.
- *(Enmienda 2)* Entrada «0,5» o «0.5» en un campo decimal: ambas se aceptan y producen el mismo
  valor. Una entrada que no es un número (por ejemplo «0,5,1») se rechaza con un mensaje claro.
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
  en general y tres en la cota y la brecha. *(Enmienda 2: se generaliza a toda la aplicación en
  FR-032 y FR-033. Enmienda 3: el separador pasa a punto decimal, sin separador de miles.)*

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

- **FR-015** *(reescrito en la enmienda 2026-10-04)*: El detalle de una versión MUST incluir una
  sección «Patrones de corte», entre el resumen de compra y la calidad del plan, con el total de
  patrones y barras y el explorador de **todos** los patrones del plan (FR-024 a FR-031). La
  sección MUST NOT depender de la imagen de nesting; la descarga de la imagen se conserva.
- **FR-016**: El resumen de compra en pantalla MUST mostrar el total por diámetro y el total
  general de lo comprado, separando las barras del inventario adicional.
- **FR-017**: La sección de calidad MUST mostrar la cota por patrones y la brecha. La cota simple
  MUST NOT aparecer como cifra destacada; MAY mencionarse en una frase explicativa.
- **FR-018** *(ampliado en la enmienda 2026-10-04)*: En un teléfono, el explorador y los totales
  de compra MUST presentarse sin desplazamiento horizontal de la página, y las secciones MUST
  cumplir las reglas de accesibilidad del sistema visual del proyecto.

**Explorador de patrones** *(enmienda 2026-10-04)*

- **FR-024**: El sistema MUST ofrecer, para cada versión, una consulta de solo lectura que
  devuelva todos sus patrones de corte con la información necesaria para dibujarlos y detallarlos.
  La consulta MUST NOT modificar la versión, sus datos guardados ni sus archivos.
- **FR-025**: Los patrones MUST obtenerse de los datos que la versión ya tiene guardados, sin
  volver a ejecutar el algoritmo genético, y MUST ser idénticos a los de la hoja «Patrones» del
  Excel de esa versión: mismos identificadores, repeticiones y secuencias. La suma de las
  repeticiones MUST ser igual al número de barras del plan; si no lo es, la consulta MUST
  informar un error en lugar de mostrar datos incoherentes.
- **FR-026**: Cada patrón MUST dibujarse a escala, con sus piezas en orden de corte coloreadas por
  etapa, y con la pérdida por corte, el descarte y el saldo diferenciados y explicados en una
  leyenda. La escala MUST ser la misma para todos los patrones: la barra más larga del plan
  ocupa el ancho completo, y la escala MUST NOT cambiar al aplicar filtros, para que las
  longitudes y los saldos se puedan comparar.
- **FR-027**: El explorador MUST permitir filtrar por diámetro, etapa, origen y pedido, combinando
  los filtros, y MUST mostrar siempre la cobertura: patrones y barras mostrados frente al total.
  El filtro por pedido MUST ser un campo de búsqueda que sugiere los pedidos («N° Orden») que
  existen en la versión. Se elige un pedido a la vez y, con él activo, cada patrón mostrado MUST
  indicar cuántas piezas de ese pedido aporta en total (repeticiones incluidas). Cuando el pedido
  es el único filtro activo, la suma de esas piezas MUST ser igual a la cantidad demandada del
  pedido. Con otros filtros activos, la suma es la parte del pedido que cubren los patrones
  mostrados.
- **FR-028**: El detalle de un patrón MUST mostrar su secuencia por etapa, la longitud de cada
  pieza, los pedidos que atiende con su número de piezas, las repeticiones, el aprovechamiento, la
  pérdida por corte, el descarte, el saldo y los identificadores de las barras que lo usan (los
  mismos de la hoja «Barras»). El total de barras MUST verse siempre. Los identificadores MUST
  agruparse en rangos consecutivos (por ejemplo, «#4:12 a #4:450») y presentarse por tramos de
  como máximo 100 elementos, con una acción «Ver más». La pantalla MUST NOT dibujar de una vez
  todos los identificadores de un patrón grande.
- **FR-029**: Todo lo que el explorador muestra al pasar el ratón MUST estar disponible también con
  el teclado y para un lector de pantalla: selección de patrón, detalle y filtros con nombres
  accesibles y foco visible.
- **FR-030**: Si una versión no tiene un plan guardado que se pueda reconstruir, o si su plan no
  consta como verificado (no pasó, o no registró, la verificación independiente), el explorador
  MUST mostrar «no disponible para esta versión» con el motivo, sin afectar al resto del
  detalle. Un plan no verificado MUST NOT presentarse como patrones válidos (constitución,
  Principio I).
- **FR-031**: Por defecto, los patrones MUST aparecer en el orden de la hoja «Patrones» del Excel
  (diámetro y, dentro de cada uno, repeticiones de mayor a menor). Un selector MUST permitir
  ordenarlos por repeticiones, aprovechamiento o saldo, de mayor a menor; los empates conservan
  el orden del Excel. Cambiar el orden MUST NOT alterar los filtros ni la cobertura.

**Formato numérico en toda la aplicación** *(enmienda 2, 2026-10-04)*

- **FR-032** *(reescrito en la enmienda 3)*: Toda cifra que lee el usuario (pantallas, PDF, imagen
  de nesting, textos legibles del Excel y mensajes de estado o error que genere la aplicación) MUST
  usar **punto decimal y ningún separador de miles** (por ejemplo, «152039.57 kg» o
  «13955 barras»). La unidad MUST ir separada de la cifra por un espacio, incluido el porcentaje
  («8.86 %»). Las diferencias en puntos porcentuales MUST llevar signo explícito («+1.26 pp» o
  «-1.14 pp»).
- **FR-033**: La cantidad de decimales MUST depender del tipo de cifra, igual en todas las
  salidas:
  - porcentajes de desperdicio, aprovechamiento, pérdidas y umbral: 2;
  - cota inferior y brecha: 3;
  - diferencias frente al umbral (pp): 2;
  - masas (kg): 2;
  - masa por metro (kg/m): 3;
  - longitudes (m) y pérdida por corte (mm): hasta 3, sin ceros finales («4.2 m», «0.37 m»);
  - tiempos: 1 decimal en segundos medidos y enteros en rangos estimados;
  - conteos (barras, piezas, patrones, repeticiones): enteros sin separador de miles.
- **FR-034**: Los campos de entrada decimales (umbral, pérdida por corte, mínimo reutilizable y
  longitudes del catálogo) MUST aceptar coma o punto como separador decimal, con el mismo
  comportamiento en cualquier navegador o idioma del sistema. Los valores escritos por el usuario
  MUST conservarse tal como los escribió mientras edita.
- **FR-035**: Los datos para máquinas MUST conservar números nativos: respuestas de la API, JSON
  guardado, celdas numéricas del Excel e inventario final reimportable. Las celdas numéricas del
  Excel MUST seguir siendo números, y su separador lo decide la configuración regional de quien
  abre el archivo.

**Nombres de descarga** *(enmienda 4)*

- **FR-036**: Cada descarga (Excel, PDF, imagen e inventario) MUST llegar al navegador con el nombre
  `OICA_<proyecto>_v<versión>_<perfil>_<tipo>.<ext>`, sin el identificador interno de la versión.
  `<proyecto>` es el nombre del archivo subido, sin extensión, en ASCII seguro y recortado a 40
  caracteres (`proyecto` si no queda nada); `<tipo>` es `resultados`, `plan_corte`, `nesting` o
  `inventario`. Las versiones sin perfil registrado lo omiten. Aplica también a las versiones
  históricas, porque solo cambia el nombre de la descarga y no el archivo (FR-020).

**Datos del análisis y compatibilidad**

- **FR-019** *(retirado en la enmienda 2026-10-04)*: ~~El resumen guardado de cada versión nueva
  MUST incluir la secuencia legible por etapa de cada uno de los patrones más repetidos, y la
  versión del análisis MUST identificarse como `analisis-2`.~~ El explorador obtiene la secuencia
  de los datos guardados (FR-025), así que el resumen del análisis no cambia y conserva su versión
  vigente.
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
- **Patrón explorable** *(enmienda 2026-10-04; sustituye a «Patrón resumido»)*: patrón de la
  versión con su identificador, diámetro, origen, longitud de barra, secuencia por etapa,
  repeticiones, aprovechamiento, pérdida por corte, descarte, saldo y barras que lo usan. Se
  obtiene de los datos guardados; no se guarda aparte.
- **Pieza del patrón**: posición de corte dentro del patrón (etapa, longitud y cantidad), con los
  pedidos que atiende a lo largo de todas las barras del patrón.
- **Filtro del explorador**: combinación de diámetro, etapa, origen y pedido, con su cobertura.

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
- **SC-009** *(enmienda)*: Con la cartilla 002 (136 patrones, 13.955 barras), el explorador
  muestra sus patrones en 2 segundos o menos desde que se abre la sección, en el entorno local de
  validación.
- **SC-010** *(enmienda)*: En el 100 % de las versiones comprobadas (001, 002 y el caso de 340
  patrones), los identificadores, las repeticiones y las secuencias del explorador coinciden con
  la hoja «Patrones» del Excel, y la suma de repeticiones es igual al número de barras.
- **SC-011** *(enmienda)*: Un usuario puede llegar al detalle de cualquier patrón y leerlo usando
  solo el teclado, y la verificación automática de accesibilidad no encuentra barreras nuevas en
  escritorio, tableta y teléfono.
- **SC-012** *(enmienda)*: Con la cartilla 002, abrir el detalle del patrón con más repeticiones,
  filtrar o pedir «Ver más» no bloquea la pantalla de forma perceptible: la respuesta es
  inmediata para el usuario (menos de 200 ms en el entorno local de validación). Al abrir el
  detalle se muestran como máximo 100 identificadores, y cada «Ver más» añade como máximo otros
  100.
- **SC-013** *(enmienda 2)*: En el 100 % de las pantallas de la aplicación (inicio, carga, lista,
  detalle, tutorial y contacto), en los tres anchos de verificación, ninguna cifra con unidad
  aparece con coma decimal, con separador de miles ni pegada a su unidad (enmienda 3). Con la cartilla 002, las mismas magnitudes
  (desperdicio, masa comprada, cota y brecha) se leen igual en la pantalla, el PDF y la hoja
  «Resumen».

## Assumptions

- Son cambios de presentación: el algoritmo genético, la normalización, la validación y los
  parámetros del modelo no se tocan, así que no hace falta una nueva versión del motor.
- *(Enmienda 2026-10-04)* El análisis guardado no cambia: no hay `analisis-2`. El explorador
  necesita una única consulta nueva de solo lectura; no hay migraciones, ni tablas nuevas, ni
  librerías nuevas.
- *(Enmienda 2026-10-04)* Cada versión del motor vigente ya guarda, barra por barra, los cortes con
  su pedido, su etapa y su longitud. Eso basta para reconstruir los patrones sin el algoritmo.
  Las versiones del motor histórico no tienen esos datos y quedan como «no disponible».
- *(Enmienda 2026-10-04)* El chequeo de taller (marcar patrones ya cortados y guardar el avance)
  queda fuera de alcance; podría ser una funcionalidad futura.
- *(Enmienda 2026-10-04, confidencialidad)* El explorador muestra los números de pedido
  («N° Orden») tal como vienen en la cartilla cargada. Las cartillas 001 y 002 son de una obra
  confidencial (constitución, Principio V). Toda demostración, captura o sustentación MUST usar
  versiones cuyos pedidos y nombre de archivo no identifiquen la obra. Si los originales la
  identifican, se usa una copia anonimizada de la cartilla.
- La fecha del encabezado del PDF es la de generación del documento; no forma parte de la
  identidad del problema ni afecta la reproducibilidad del plan.
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
