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

