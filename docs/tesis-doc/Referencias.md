# Referencias de la tesis — fichas de trazabilidad

> Archivo de control de la spec 001 (FR-021, FR-022). Cada ficha dice por qué se propuso la
> fuente, qué término del título respalda, dónde va en la tesis y si ya se verificó.
> Una fuente que no esté «verificada» MUST NOT citarse en la tesis como si lo estuviera
> (constitución, Principio V).

**Estados de verificación**:
- **verificada**: se consultó el documento y se comprobaron cita, tabla o página.
- **verificar cita literal**: falta comprobar las palabras exactas en el documento oficial.
- **verificar edición y páginas**: la fuente existe, pero falta fijar edición y páginas.
- **pendiente de localizar**: aún no se obtuvo el documento.

Estado del archivo (2026-10-02): fichas de las tareas T003 (normativa citada por la aplicación) y
T045 (resto de FR-022 y fuentes ya citadas en los capítulos). La «pregunta textual del usuario»
no quedó registrada en las sesiones: figura como «pendiente: pedir al autor» y no se inventa.

| Ficha | Término del título | Estado |
|---|---|---|
| REF-NSR10-TABLA | en Colombia | verificada |
| REF-DECRETO926 | en Colombia | verificada (consulta del 2026-09-13 registrada en el Cap. 2) |
| REF-INVIAS-640 | desperdicios admisibles | verificada |
| REF-IDU-ACERO | desperdicios admisibles | pendiente de localizar |
| REF-RES472 | desperdicios admisibles | verificada (textos compilados) |
| REF-RECIAMUC-2022 | desperdicios admisibles | verificada |
| REF-APU | desperdicios admisibles | pendiente de localizar (fuente débil) |
| REF-GG-1961 / REF-GG-1963 | patrones de corte | verificar cita literal (datos bibliográficos confirmados) |
| REF-WASCHER-2007 | patrones de corte, nesting | verificar cita literal (datos bibliográficos confirmados) |
| REF-BENJAORAN-2013 | distribución eficiente | verificada |
| REF-RUSSELL-NORVIG | Inteligencia Artificial | verificar cita literal (edición, sección y página verificadas) |
| REF-HOLLAND-1975 | Inteligencia Artificial | verificar edición y páginas (datos bibliográficos confirmados) |
| REF-GOLDBERG-1989 | Inteligencia Artificial | verificar edición y páginas (datos bibliográficos confirmados) |
| REF-NESTING-LINEAL | nesting | pendiente de localizar |
| REF-HILTI-ACD | (hipótesis física) | verificar cita literal |
| REF-NSR10-GANCHOS-RECUBRIMIENTOS | (cartillas sintéticas) | verificada |
| REF-NSR10-EMPALMES | (cartillas sintéticas) | verificada |
| REF-NSR10-DMO | (cartillas sintéticas) | verificada |
| REF-CARTILLA-001 | (procedencia de datos) | pendiente de localizar (periodo y nombre completo del docente) |

Actualización 2026-10-04 (Bloque N): las tres fichas de la NSR-10 respaldan los supuestos de las
cartillas sintéticas 003 y 004 (INF-018), y REF-CARTILLA-001 documenta la procedencia de 001
(INF-017). Las cifras nuevas usan punto decimal.

---

## REF-NSR10-TABLA — Masas nominales de las barras de refuerzo

- **Cita completa**: Asociación Colombiana de Ingeniería Sísmica (AIS) y Comisión Asesora
  Permanente para el Régimen de Construcciones Sismo Resistentes. *Reglamento Colombiano de
  Construcción Sismo Resistente NSR-10, Título C — Concreto estructural*. Adoptado por el Decreto
  926 de 2010. Tabla C.3.5.3-2, «Dimensiones nominales de las barras de refuerzo (diámetros
  basados en octavos de pulgada)», p. C-47; repetida en el Apéndice C-E, p. C-515.
- **Enlace**: copia publicada por CAMACOL,
  <https://camacol.co/sites/default/files/descargables/T%C3%ADtulo%20C%20NSR-10%20del%20Decreto%20926%20del%2019032010_0.pdf>.
  Decreto en SUIN-Juriscol: <https://suin-juriscol.gov.co/viewDocument.asp?id=1918254>.
- **Estado**: **verificada** (2026-10-02). La tabla se leyó del PDF. Sus masas en kg/m coinciden
  valor por valor con la hoja `TablaBarras` de `backend/Planilla_Cartilla.xlsx`:

  | Barra | #2 | #3 | #4 | #5 | #6 | #7 | #8 | #9 | #10 | #11 | #14 | #18 |
  |---|---|---|---|---|---|---|---|---|---|---|---|---|
  | kg/m | 0,250 | 0,560 | 0,994 | 1,552 | 2,235 | 3,042 | 3,973 | 5,060 | 6,404 | 7,907 | 11,380 | 20,240 |

- **Motivo de la propuesta**: dar una referencia normativa colombiana para contrastar la masa
  por metro de cada cartilla (aviso no bloqueante, FR-018).
- **Evidencia adicional**: el texto completo del Título C en la copia consultada (35.395 líneas
  extraídas con `pdftotext`) no contiene el término «desperdicio» (2026-10-02). Solo se revisó
  el Título C, no los demás títulos de la NSR-10.
- **Concordancia**: INVIAS 2022, Tabla 640-1 (p. 640-2), repite los mismos valores (REF-INVIAS-640).
- **Pregunta textual del usuario que la originó**: pendiente: pedir al autor. La decisión se
  registró en INF-014 («en Colombia = masas nominales NSR-10 con aviso de discrepancia»), pero
  no la pregunta literal.
- **Término del título que respalda**: «en Colombia».
- **Ubicación prevista en la tesis**: Cap. 2 (marco normativo), Cap. 3 (aviso de masa nominal).
- **Advertencias**:
  - La copia consultada es la publicada por CAMACOL, no el *Diario Oficial*. Antes de la
    entrega, comprobar en SUIN-Juriscol que las modificaciones posteriores al Decreto 926 no
    cambiaron esta tabla.
  - La tabla fija masas nominales, no tolerancias de fabricación. Si la tesis cita tolerancias,
    hay que localizarlas en la norma de producto que remite C.3.5.3.1 (por verificar; no se
    consultó). La tolerancia del aviso (1 %) es una decisión de diseño de OICA, no un requisito
    normativo.

---

## REF-INVIAS-640 — Especificaciones generales de INVIAS, artículo 640 (acero de refuerzo)

- **Cita completa**: Instituto Nacional de Vías (INVIAS). (2022). *Especificaciones Generales de
  Construcción de Carreteras*. Capítulo 6, «Estructuras y drenajes», Artículo 640-22 «Acero de
  refuerzo»:
  - 640.6 «Medida» y 640.7 «Forma de pago», pp. 640-8 a 640-10;
  - Tabla 640-1, p. 640-2.
- **Enlace**: portal oficial, <https://www.invias.gov.co/publicaciones/4154/documentos-tecnicos/>
  (sección «Especificaciones generales de construcción de carreteras (2022)»; la descarga
  requiere navegador). Copia local fuera del repositorio: `docs/tesis-doc/fuentes/`.
- **Estado**: **verificada** (2026-10-03) con el PDF oficial descargado por el autor, de 1.344
  páginas. La fe de erratas de 2022 no menciona el artículo 640.
- **Contenido verificado**:
  - **640.6 Medida**: «La unidad de medida debe ser el kilogramo (kg), aproximado al entero, de
    acero de refuerzo para estructuras de concreto realmente suministrado y colocado en obra y
    debidamente aceptado por el interventor». La medida de barras se basa en la masa calculada con
    las Tablas 640-1 y 640-2.
  - **640.6 Medida**: «No se deben medir cantidades en exceso de las indicadas en los documentos
    del proyecto o las ordenadas por el interventor».
  - **640.7 Forma de pago**: «El precio unitario debe cubrir todos los costos por concepto de
    suministro, ensayos, transportes, almacenamiento, corte, desperdicios, doblamiento, limpieza,
    colocación y fijación del refuerzo […]».
  - El artículo **no fija un porcentaje máximo de desperdicio**: la palabra aparece una sola vez,
    dentro de los costos que cubre el precio unitario.
  - **Tabla 640-1** (masas por metro, barras en octavos de pulgada): valores idénticos a la
    NSR-10, Tabla C.3.5.3-2, de n.º 2 (0,250 kg/m) a n.º 18 (20,240 kg/m).
- **Motivo de la propuesta**: sustentar que en la obra pública colombiana el desperdicio de acero
  no tiene un máximo normativo general y se presupuesta dentro del precio unitario. Por eso OICA no
  propone un umbral por defecto (FR-002).
- **Pregunta textual del usuario que la originó**: pendiente: pedir al autor.
- **Término del título que respalda**: «desperdicios admisibles», «en Colombia».
- **Ubicación prevista en la tesis**: Cap. 2 §2.8.
- **Advertencias**:
  - Las especificaciones INVIAS rigen la obra vial nacional; no se extienden automáticamente a la
    edificación.
  - Unos resúmenes secundarios mencionan especificaciones particulares de contratos con un
    «desperdicio máximo» del 2 % o 3 %. **No están verificados** y no se citan en la tesis.

---

## REF-IDU-ACERO — Especificación técnica de acero de refuerzo del IDU

- **Cita completa**: Instituto de Desarrollo Urbano (IDU), Bogotá. Especificación técnica de
  acero de refuerzo para concreto. Número de sección y edición por localizar.
- **Enlace**: no localizado.
- **Estado**: **pendiente de localizar**.
- **Motivo de la propuesta**: contrastar con una entidad territorial si el desperdicio se paga
  aparte o va en el precio unitario.
- **Pregunta textual del usuario que la originó**: pendiente: pedir al autor.
- **Término del título que respalda**: «desperdicios admisibles», «en Colombia».
- **Ubicación prevista en la tesis**: Cap. 2 (desperdicio admisible).
- **Advertencias**: sin documento no se puede afirmar nada sobre su contenido. La app no lo
  nombra y la tesis no debe citarlo hasta localizarlo.

---

## REF-DECRETO926 — Decreto 926 de 2010 (adopta la NSR-10)

- **Cita completa**: Presidencia de la República de Colombia. Decreto 926 de 2010, por el cual se
  establecen los requisitos de carácter técnico y científico para construcciones sismo
  resistentes NSR-10.
- **Enlace**: <https://suin-juriscol.gov.co/viewDocument.asp?id=1918254>.
- **Estado**: **verificada** según el Cap. 2 §2.5 (vigencia consultada en SUIN-Juriscol el
  2026-09-13). No se volvió a consultar en esta sesión.
- **Motivo de la propuesta**: delimitar el marco normativo colombiano de la construcción en
  concreto reforzado.
- **Pregunta textual del usuario que la originó**: pendiente: pedir al autor.
- **Término del título que respalda**: «en Colombia».
- **Ubicación prevista en la tesis**: Cap. 2 §2.5 (ya citada).
- **Advertencias**: la NSR-10 no fija un porcentaje de desperdicio de acero ni un mínimo
  reutilizable; el Cap. 2 ya lo declara.

---

## REF-RES472 — Resolución 472 de 2017 del Ministerio de Ambiente (RCD) y su modificación

- **Cita completa**:
  - Ministerio de Ambiente y Desarrollo Sostenible. Resolución 0472 de 2017, sobre la gestión
    integral de residuos de construcción y demolición (RCD).
  - Modificada por la Resolución 1257 del 23 de noviembre de 2021 (*Diario Oficial* n.º 51.867),
    «por la cual se modifica la Resolución 0472 de 2017 sobre la gestión integral de Residuos de
    Construcción y Demolición (RCD)».
- **Enlace**:
  - Texto compilado de la 472, con sus modificaciones:
    <https://normograma.mintic.gov.co/mintic/compilacion/docs/resolucion_minambienteds_0472_2017.htm>.
  - Resolución 1257: <https://normas.cra.gov.co/gestor/docs/resolucion_minambienteds_1257_2021.htm>
    y <https://www.minambiente.gov.co/documento-normativa/resolucion-1257-de-2021/>.
- **Estado**: **verificada** (2026-10-02), sobre los textos compilados del normograma de MinTIC y
  del gestor normativo de la CRA, que no son el *Diario Oficial*. En ambos textos:
  - el término «desperdicio» no aparece;
  - el acero solo figura como un tipo de RCD no pétreo («metales como acero, hierro, cobre…»);
  - el único porcentaje es una **meta mínima de aprovechamiento de RCD** para grandes generadores,
    en peso sobre el total de materiales usados en la obra.
- **Motivo de la propuesta**: mostrar que la regulación ambiental colombiana trata los RCD sin
  fijar un porcentaje admisible de desperdicio de acero en el corte.
- **Pregunta textual del usuario que la originó**: pendiente: pedir al autor.
- **Término del título que respalda**: «desperdicios admisibles», «en Colombia».
- **Ubicación prevista en la tesis**: Cap. 2 §2.8.
- **Advertencias**: la meta de aprovechamiento de RCD es un mínimo de reciclaje de residuos, no un
  máximo de desperdicio. El «desperdicio» de OICA incluye el saldo reutilizable (INF-012) y no
  equivale a un RCD. Antes de citar porcentajes o plazos de la meta, consultar el texto vigente.

---

## REF-RECIAMUC-2022 — Desperdicio de acero de refuerzo en una vivienda

- **Cita completa**: Almendariz Rodríguez, C. E. y Ortiz Aguirre, I. J. (2022). Determinación de
  porcentaje de desperdicios del acero estructural de refuerzo en diversos elementos de hormigón
  armado perteneciente a la estructura de una vivienda de 2 plantas. *RECIAMUC*, 6(1), 25–39.
  <https://doi.org/10.26820/reciamuc/6.(1).enero.2022.25-39>
- **Enlace**: <https://reciamuc.com/index.php/RECIAMUC/article/view/769>. Copia local en
  `docs/tesis-doc/fuentes/`.
- **Estado**: **verificada** (2026-10-03) con el PDF del artículo.
- **Contenido verificado**: para una vivienda de 2 plantas, el peso de acero a pagar en planilla
  es de 4.552,288 kg y la compra se determinó en 4.860,412 kg, con un desperdicio total del 6,77 %
  (conclusiones, p. 38). Los desperdicios considerados son los sobrantes del material empleado.
- **Motivo de la propuesta**: dar un orden de magnitud empírico del desperdicio de acero en obra.
- **Pregunta textual del usuario que la originó**: pendiente: pedir al autor.
- **Término del título que respalda**: «desperdicios admisibles».
- **Ubicación prevista en la tesis**: Cap. 2 §2.8, como referencia empírica.
- **Advertencias**:
  - Es una fuente **débil**: un solo caso de vivienda.
  - Los autores son de la Universidad de Guayaquil (Ecuador); no es un caso colombiano.
  - Su «desperdicio» (sobrantes sobre lo comprado) se parece al de OICA (sobrante + pérdida +
    descarte), pero no es idéntico.
  - El 7,7 % que aparece en el texto es el crecimiento del sector de la construcción en Perú, no
    un desperdicio.
  - No usar el 6,77 % como umbral normativo ni como valor por defecto de OICA (FR-002).

---

## REF-APU — Guías de análisis de precios unitarios con porcentaje de desperdicio de acero

- **Cita completa**: por localizar (guías o bases de precios de entidades colombianas).
- **Enlace**: no localizado.
- **Estado**: **pendiente de localizar** (fuente débil).
- **Motivo de la propuesta**: documentar de dónde suele salir el porcentaje que el usuario ingresa
  como umbral.
- **Pregunta textual del usuario que la originó**: pendiente: pedir al autor.
- **Término del título que respalda**: «desperdicios admisibles».
- **Ubicación prevista en la tesis**: Cap. 2 y Cap. 3 (umbral del usuario).
- **Advertencias**: un porcentaje de un APU es un supuesto de presupuesto, no una norma. Según INF-015
  (validada), OICA compara el umbral con el desperdicio total: todo lo comprado que no queda en
  piezas. Si un APU usa otra definición, el usuario debe convertir su porcentaje antes de ingresarlo.

---

## REF-GG-1961 y REF-GG-1963 — Gilmore y Gomory, enfoque de programación lineal por patrones

- **Cita completa**:
  - Gilmore, P. C. y Gomory, R. E. (1961). A Linear Programming Approach to the Cutting-Stock
    Problem. *Operations Research*, 9(6), 849–859. <https://doi.org/10.1287/opre.9.6.849>
  - Gilmore, P. C. y Gomory, R. E. (1963). A Linear Programming Approach to the Cutting Stock
    Problem—Part II. *Operations Research*, 11(6), 863–888. <https://doi.org/10.1287/opre.11.6.863>
- **Enlace**: los DOI anteriores.
- **Estado**: **verificar cita literal**. Los datos bibliográficos se confirmaron en Crossref el
  2026-10-02; falta leer los artículos para citar su contenido con página.
- **Motivo de la propuesta**: es el origen del «enfoque basado en patrones de corte»: relajación
  lineal con generación de columnas, que OICA usa para la cota inferior (research R-02).
- **Pregunta textual del usuario que la originó**: pendiente: pedir al autor.
- **Término del título que respalda**: «mediante el enfoque basado en patrones de corte».
- **Ubicación prevista en la tesis**: Cap. 2 (patrones de corte) y Cap. 3 (cálculo de la cota).
- **Advertencias**: OICA usa el enfoque para **medir** (cota), no para construir el plan. Las
  extensiones propias (inventario limitado, pérdida por corte como l+e, certificado lagrangiano,
  etapas relajadas) son del diseño de OICA y no deben atribuirse a los autores.

---

## REF-WASCHER-2007 — Tipología de problemas de corte y empaque

- **Cita completa**: Wäscher, G., Haußner, H. y Schumann, H. (2007). An improved typology of
  cutting and packing problems. *European Journal of Operational Research*, 183(3), 1109–1130.
  <https://doi.org/10.1016/j.ejor.2005.12.047>
- **Enlace**: el DOI anterior.
- **Estado**: **verificar cita literal**. Los datos bibliográficos se confirmaron en Crossref el
  2026-10-02.
- **Motivo de la propuesta**: clasificar el problema de OICA (corte unidimensional con varias
  longitudes de stock) y precisar el uso del término «nesting».
- **Pregunta textual del usuario que la originó**: pendiente: pedir al autor.
- **Término del título que respalda**: «patrones de corte», «nesting».
- **Ubicación prevista en la tesis**: Cap. 2 §2.1.
- **Advertencias**: en esa tipología, «nesting» suele asociarse a piezas irregulares
  (bidimensionales); la tesis debe decir que OICA usa «nesting lineal» en el sentido industrial
  1D. Confirmar la clasificación exacta en el texto antes de citarla.

---

## REF-BENJAORAN-2013 — Minimización de pérdida en acero de refuerzo

- **Cita completa**: Benjaoran, V. y Bhokha, S. (2013). Trim Loss Minimization for Construction
  Reinforcement Steel with Oversupply Constraints. *Journal of Advanced Management Science*, 1(3),
  313–316. <https://doi.org/10.12720/joams.1.3.313-316>
- **Enlace**: <https://www.joams.com/uploadfile/2013/1024/20131024100240137.pdf>.
- **Estado**: **verificada**. El Cap. 2 §2.5 la cita desde el PDF (criterio de *retails*) y los
  datos bibliográficos se confirmaron en Crossref el 2026-10-02.
- **Motivo de la propuesta**: sustenta el mínimo reutilizable automático y el contexto de obra del
  corte de acero.
- **Pregunta textual del usuario que la originó**: pendiente: pedir al autor.
- **Término del título que respalda**: «distribución eficiente», «barras de acero comercial».
- **Ubicación prevista en la tesis**: Cap. 2 §2.5 (ya citada).
- **Advertencias**: su parámetro Tw no es un mínimo universal ni un umbral de desperdicio
  admisible (el Cap. 2 ya lo aclara). Crossref no registra volumen ni número; se toman del PDF.

---

## REF-RUSSELL-NORVIG — Inteligencia Artificial como disciplina

- **Cita completa**: Russell, S. y Norvig, P. (2021). *Artificial Intelligence: A Modern Approach*
  (4.ª ed.). Pearson. Capítulo 4, «Search in Complex Environments», sección 4.1.4,
  «Evolutionary algorithms», p. 115.
- **Enlace**: índice oficial del libro, <https://aima.cs.berkeley.edu/contents.html>.
- **Estado**: **verificar cita literal**.
  - Verificado el 2026-10-02 en el índice oficial: edición, capítulo, sección y página inicial.
  - Los algoritmos evolutivos aparecen como una técnica de búsqueda dentro de un texto de
    referencia de Inteligencia Artificial.
  - Falta leer la sección para citar su contenido textual.
- **Motivo de la propuesta**: respaldar que los algoritmos genéticos son una técnica de IA
  (búsqueda local y computación evolutiva).
- **Pregunta textual del usuario que la originó**: pendiente: pedir al autor.
- **Término del título que respalda**: «con Inteligencia Artificial».
- **Ubicación prevista en la tesis**: Cap. 2 §2.4.
- **Advertencias**:
  - El índice oficial corresponde a la 4.ª edición de EE. UU.; la edición global puede tener otra
    paginación.
  - El año figura como 2020 o 2021 según la impresión; usar el de la página de créditos del
    ejemplar consultado.

---

## REF-HOLLAND-1975 — Origen de los algoritmos genéticos

- **Cita completa**: Holland, J. H. (1975). *Adaptation in Natural and Artificial Systems: An
  Introductory Analysis with Applications to Biology, Control, and Artificial Intelligence*.
  University of Michigan Press. Reimpresión: MIT Press, 1992.
- **Enlace**: registros en Internet Archive (préstamo digital con cuenta gratuita):
  <https://archive.org/details/adaptationinnatu0000holl> (1975) y
  <https://archive.org/details/adaptationinnatu00holl> (MIT Press, 1992).
- **Estado**: **verificar edición y páginas**. Los datos bibliográficos de ambas ediciones están
  confirmados en el catálogo de Internet Archive (2026-10-02). Si se cita solo como origen de los
  algoritmos genéticos, sin parafrasear un pasaje concreto, basta con la edición; para atribuirle
  una idea puntual, hace falta la página.
- **Motivo de la propuesta**: fuente original de los algoritmos genéticos.
- **Pregunta textual del usuario que la originó**: pendiente: pedir al autor.
- **Término del título que respalda**: «con Inteligencia Artificial».
- **Ubicación prevista en la tesis**: Cap. 2 §2.4.
- **Advertencias**: citar la edición que se consulte (1975 o la reimpresión de 1992).

---

## REF-GOLDBERG-1989 — Algoritmos genéticos en búsqueda y optimización

- **Cita completa**: Goldberg, D. E. (1989). *Genetic Algorithms in Search, Optimization, and
  Machine Learning*. Addison-Wesley.
- **Enlace**: registro en Internet Archive (préstamo digital con cuenta gratuita):
  <https://archive.org/details/geneticalgorithm0000gold>.
- **Estado**: **verificar edición y páginas**. Los datos bibliográficos están confirmados en el
  catálogo de Internet Archive (2026-10-02). Faltan las páginas del capítulo 1, donde se presenta
  el algoritmo genético simple y sus operadores.
- **Motivo de la propuesta**: referencia clásica de los operadores del algoritmo genético
  (selección o reproducción, cruce y mutación) que usa el motor de OICA.
- **Pregunta textual del usuario que la originó**: pendiente: pedir al autor.
- **Término del título que respalda**: «con Inteligencia Artificial».
- **Ubicación prevista en la tesis**: Cap. 2 §2.4.
- **Advertencias**: la selección por torneo y el elitismo del motor no deben atribuirse a este
  libro sin comprobar en qué páginas los trata; el capítulo 1 se centra en reproducción, cruce y
  mutación.

---

## REF-NESTING-LINEAL — Uso industrial de «nesting» unidimensional

- **Cita completa**: por localizar (literatura técnica o documentación de software de corte de
  barras y perfiles que use «nesting lineal» o *1D nesting*).
- **Enlace**: no localizado.
- **Estado**: **pendiente de localizar**.
- **Motivo de la propuesta**: dar respaldo al término «nesting» del título en su sentido 1D.
- **Pregunta textual del usuario que la originó**: pendiente: pedir al autor.
- **Término del título que respalda**: «nesting».
- **Ubicación prevista en la tesis**: Cap. 2 §2.1.
- **Advertencias**: mientras no se localice, la tesis debe presentar «nesting lineal» como uso
  industrial **sin** citar una fuente inexistente, y reconocer que académicamente el término
  suele reservarse para piezas irregulares (REF-WASCHER-2007, por verificar).

---

## REF-HILTI-ACD — Espesor nominal de disco abrasivo

- **Cita completa**: Hilti. Ficha del disco de corte AC-D (abrasivos para acero).
- **Enlace**: <https://www.hilti.com.ph/c/CLS_POWER_TOOL_INSERT_7126/CLS_ABRASIVES_7126/r6473822>.
- **Estado**: **verificar cita literal** (citada en el Cap. 2 §2.5; no se volvió a consultar).
- **Motivo de la propuesta**: referencia del espesor nominal de 1 mm del disco que propone la
  interfaz como pérdida por corte.
- **Pregunta textual del usuario que la originó**: pendiente: pedir al autor.
- **Término del título que respalda**: ninguno directamente (hipótesis física del modelo).
- **Ubicación prevista en la tesis**: Cap. 2 §2.5 (ya citada).
- **Advertencias**: es una ficha comercial, no una norma; el valor debe calibrarse con el equipo
  real (el Cap. 2 ya lo dice).


---

## REF-NSR10-GANCHOS-RECUBRIMIENTOS — Ganchos, doblado, recubrimiento y estribos mínimos

- **Cita completa**: AIS y Comisión Asesora Permanente para el Régimen de Construcciones Sismo
  Resistentes. *Reglamento Colombiano de Construcción Sismo Resistente NSR-10, Título C — Concreto
  estructural*. Decreto 926 de 2010. Secciones:
  - C.2.2, definición de gancho sísmico, p. C-33;
  - C.7.1, ganchos estándar, y C.7.2 con la tabla C.7.2, diámetros mínimos de doblado, pp. C-91 y C-92;
  - C.7.7.1, recubrimiento mínimo del concreto construido en sitio, pp. C-96 y C-97;
  - C.7.10.5.1, diámetro mínimo de estribos en elementos a compresión, p. C-103.
- **Enlace**: la misma copia de CAMACOL de REF-NSR10-TABLA.
- **Estado**: **verificada** (2026-10-04). Texto extraído con `pdftotext`; en ese PDF, la página
  del archivo es la etiqueta C-xx más 12.
- **Lo verificado**:
  - C.7.1.2: «Doblez de 90º más una extensión de 12db en el extremo libre de la barra».
  - C.7.1.3: estribos No. 5 y menores, 90° con 6 db; No. 6 a No. 8, 90° con 12 db; No. 8 y
    menores, 135° con 6 db.
  - C.7.1.4: ganchos sísmicos «con un doblez de 135º o más, con una extensión de 6db pero no menor
    de 75 mm».
  - Tabla C.7.2: diámetro de doblado 6 db de No. 3 a No. 8; C.7.2.2: 4 db para estribos No. 5 y menores.
  - C.7.7.1: 75 mm contra el suelo; 50 mm (No. 6 y mayores) y 40 mm (No. 5 y menores) expuesto al
    suelo o a la intemperie; 20 mm en losas, muros y viguetas (No. 11 y menores) y 40 mm en vigas y
    columnas, no expuestos.
  - C.7.10.5.1: estribos de por lo menos No. 3 para barras longitudinales No. 10 o menores.
- **Motivo de la propuesta**: respaldar los supuestos S-03, S-04, S-05 y S-10 de las cartillas
  sintéticas (INF-018).
- **Pregunta textual del usuario que la originó**: «Verificarlos en la NSR-10» (respuesta del
  2026-10-04 sobre cómo tratar ganchos, traslapos y recubrimientos).
- **Término del título que respalda**: ninguno directamente; da verosimilitud a las cartillas
  sintéticas.
- **Ubicación prevista en la tesis**: Cap. 3, generación de cartillas sintéticas.
- **Advertencias**:
  - Copia de CAMACOL, no el *Diario Oficial* (ver REF-NSR10-TABLA).
  - C.2.2 dice «más de 135 grados» y C.7.1.4 «135º o más»: citar C.7.1.4.
  - La extensión de 12 db es el tramo recto después del doblez; no es la longitud de desarrollo
    con gancho (C.12.5, no consultada).
  - Las cartillas usan 50 mm en vigas de cimentación (valor de No. 6 y mayores) también para No. 4:
    es mayor que el mínimo.

---

## REF-NSR10-EMPALMES — Longitud de desarrollo y empalmes por traslapo en tracción

- **Cita completa**: NSR-10, Título C (como en REF-NSR10-GANCHOS-RECUBRIMIENTOS). Secciones:
  - C.12.2.1 y C.12.2.2, longitud de desarrollo en tracción, p. C-218;
  - CR12.2, comentario con ejemplo numérico, p. C-219;
  - C.12.2.4, factores ψt, ψe y λ, p. C-220;
  - C.12.14, empalmes, p. C-239;
  - C.12.15.1 y C.12.15.2, empalmes por traslapo en tracción, pp. C-240 y C-241.
- **Enlace**: la misma copia de CAMACOL.
- **Estado**: **verificada** (2026-10-04).
- **Lo verificado**:
  - C.12.2.2, caso con espaciamiento y recubrimiento libres no menores que db y estribos mínimos:
    ld = (fy ψt ψe / 2.1 λ √f'c) db para No. 6 y menores, y (fy ψt ψe / 1.7 λ √f'c) db para No. 7
    y mayores. C.12.2.1: ld no menor de 300 mm.
  - C.12.2.4: ψt = 1.3 con más de 300 mm de concreto fresco debajo del refuerzo horizontal; 1.0 en
    otros casos. ψe = 1.0 sin recubrimiento epóxico. λ = 1.0 en concreto de peso normal.
  - C.12.15.1: clase A = 1.0 ld, clase B = 1.3 ld, no menor de 300 mm; ld sin el mínimo de 300 mm.
    C.12.15.2: clase B salvo dos condiciones simultáneas para clase A.
  - Con f'c = 21 MPa y fy = 420 MPa: 43.64 db hasta No. 6 y 53.91 db para No. 7; traslapos clase B
    redondeados hacia arriba a 0.05 m: No. 3 0.55, No. 4 0.75, No. 5 0.95, No. 6 1.10 y No. 7 1.60 m.
- **Motivo de la propuesta**: respaldar los supuestos S-01 y S-06 (INF-018).
- **Pregunta textual del usuario que la originó**: la misma de REF-NSR10-GANCHOS-RECUBRIMIENTOS.
- **Término del título que respalda**: ninguno directamente.
- **Ubicación prevista en la tesis**: Cap. 3, generación de cartillas sintéticas.
- **Advertencias**:
  - El signo de raíz no está en la capa de texto del PDF. Se confirmó con el ejemplo de CR12.2
    (f'c = 28 MPa da 47 db).
  - En la celda de «otros casos» para No. 7 y mayores aparece una λ de más en el numerador,
    posiblemente una errata de la copia. No afecta las cartillas, que usan el caso favorable.
  - Las cartillas suponen ψt = 1.0 también en barras superiores: sus traslapos son menores que los
    que exigiría un diseño con ψt = 1.3.

---

## REF-NSR10-DMO — Refuerzo transversal y empalmes en pórticos con capacidad moderada (DMO)

- **Cita completa**: NSR-10, Título C (como en REF-NSR10-GANCHOS-RECUBRIMIENTOS). Secciones:
  - C.21.3.4.5, C.21.3.4.6 y C.21.3.4.8, vigas, pp. C-366 y C-367;
  - C.21.3.5.3 y C.21.3.5.6 a C.21.3.5.11, columnas, pp. C-367 a C-369.
- **Enlace**: la misma copia de CAMACOL.
- **Estado**: **verificada** (2026-10-04).
- **Lo verificado**:
  - Vigas: estribos cerrados de confinamiento de al menos No. 3 en longitudes de 2h desde la cara
    del apoyo; el primero a no más de 50 mm; separación no mayor que el menor de d/4, 8 db de la
    barra longitudinal más pequeña, 24 db del estribo y 300 mm. Fuera de esa zona, no más de d/2.
    No se permiten traslapos dentro de los nudos (C.21.3.4.5).
  - Columnas: so no mayor que el menor de 8 db de la barra longitudinal menor, 16 db del estribo, un
    tercio de la menor dimensión y 150 mm; lo no menor que el mayor de ln/6, la mayor dimensión de la
    sección y 500 mm; fuera de lo, no más de 2 so; estribos mínimo No. 3. Los traslapos solo se
    permiten en la mitad central de la longitud del elemento (C.21.3.5.3).
- **Motivo de la propuesta**: respaldar los supuestos S-09 y S-14 (INF-018).
- **Pregunta textual del usuario que la originó**: la misma de REF-NSR10-GANCHOS-RECUBRIMIENTOS.
- **Término del título que respalda**: ninguno directamente.
- **Ubicación prevista en la tesis**: Cap. 3, generación de cartillas sintéticas.
- **Advertencias**:
  - Las cartillas adoptan separaciones dentro de estos límites, pero no hay análisis sísmico ni
    diseño: no se afirma que cumplan la NSR-10.
  - El despiece de vigas no modela la posición de los empalmes (S-07), así que no comprueba
    C.21.3.4.5.

---

## REF-CARTILLA-001 — Procedencia de la cartilla 001

- **Cita completa**: «Cartilla N°1», ejercicio de despiece del curso Construcción de
  edificaciones, programa de Ingeniería Civil, Universidad Surcolombiana. Docente: Carlos Uriel
  (nombre como lo dio el autor). Periodo académico: no lo recuerda el autor.
- **Enlace**: no aplica (material de curso no publicado). El archivo es
  `tests/data/001/001-pruebaInicial.xlsx`.
- **Estado**: **pendiente de localizar** (periodo académico y nombre completo del docente). El
  autor aportó docente, programa y universidad el 2026-10-04.
- **Descripción**: según el autor (2026-10-04), el profesor pidió a cada grupo elaborar una
  cartilla a partir de un proyecto real, distinto para cada grupo. El autor no recuerda los datos
  del proyecto y no conserva la cartilla original. Las vigas de 001 coinciden en longitudes con la
  «Cartilla N°1» del borrador «Tesis final 1» (RIESGO-AC-010).
- **Motivo de la propuesta**: documentar la procedencia de 001 (INF-017).
- **Pregunta textual del usuario que la originó**: «¿De dónde proviene realmente la cartilla 001?»;
  respuesta: «Ejercicio académico».
- **Término del título que respalda**: ninguno.
- **Ubicación prevista en la tesis**: Cap. 1 §1.3.3, Cap. 3 §3.1 y Anexo A.
- **Advertencias**:
  - No presentar 001 como cartilla de obra.
  - No identificar el proyecto del que se sacó (Principio V).
