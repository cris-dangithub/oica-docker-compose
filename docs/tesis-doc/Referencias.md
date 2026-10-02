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
| REF-INVIAS-640 | desperdicios admisibles | verificar cita literal |
| REF-IDU-ACERO | desperdicios admisibles | pendiente de localizar |
| REF-RES472 | desperdicios admisibles | verificada (textos compilados) |
| REF-RECIAMUC-2022 | desperdicios admisibles | verificar cita literal (datos bibliográficos confirmados) |
| REF-APU | desperdicios admisibles | pendiente de localizar (fuente débil) |
| REF-GG-1961 / REF-GG-1963 | patrones de corte | verificar cita literal (datos bibliográficos confirmados) |
| REF-WASCHER-2007 | patrones de corte, nesting | verificar cita literal (datos bibliográficos confirmados) |
| REF-BENJAORAN-2013 | distribución eficiente | verificada |
| REF-RUSSELL-NORVIG | Inteligencia Artificial | verificar edición y páginas |
| REF-HOLLAND-1975 | Inteligencia Artificial | verificar edición y páginas |
| REF-GOLDBERG-1989 | Inteligencia Artificial | verificar edición y páginas |
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

- **Cita completa**: Instituto Nacional de Vías (INVIAS). *Especificaciones Generales de
  Construcción de Carreteras*, Capítulo 6, Artículo 640 «Acero de refuerzo». Edición por fijar
  (2013 o 2022).
- **Enlace**: no se obtuvo una copia oficial el 2026-10-02. Los espejos conocidos no
  respondieron: `gerconcesion.co` agotó el tiempo de conexión y un pliego de Findeter devolvió
  HTTP 403.
- **Estado**: **verificar cita literal**.
- **Contenido por confirmar**: según resúmenes secundarios (no verificados):
  - la medida se hace en kilogramos de acero realmente suministrado y colocado, con las masas
    unitarias del propio artículo;
  - el precio unitario debe cubrir, entre otros, corte, desperdicios y doblamiento.

  Si se confirma, el desperdicio va dentro del precio unitario y el artículo no fija un
  porcentaje máximo.
- **Motivo de la propuesta**: sustentar que en la obra pública colombiana el desperdicio de
  acero no tiene un máximo normativo general y se presupuesta dentro del precio unitario. Por eso
  OICA no propone un umbral por defecto (FR-002).
- **Pregunta textual del usuario que la originó**: pendiente: pedir al autor.
- **Término del título que respalda**: «desperdicios admisibles».
- **Ubicación prevista en la tesis**: Cap. 2 (desperdicio admisible), Cap. 3 (umbral del usuario).
- **Advertencias**:
  - Los resúmenes encontrados mencionan **especificaciones técnicas particulares** de algunos
    contratos que fijan un «desperdicio máximo» del 2 % o del 3 %. Si se confirma, no son normas
    generales sino condiciones de un contrato. Eso respalda el texto de la app («usa el que
    exige tu contrato»), pero la tesis no debe afirmar que «nadie» fija un máximo: debe decir que
    la norma general no lo fija y que un contrato sí puede hacerlo.
  - Mientras siga sin verificar, la app no nombra a INVIAS en sus textos (FR-002) y la tesis no
    la cita como verificada.
  - **Acción**: pedir al autor la edición oficial del artículo 640 (PDF de invias.gov.co) o una
    copia del pliego de un proyecto.

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

- **Cita completa**: Almendariz Rodríguez, C. y Ortiz Aguirre, I. (2022). Determinación de
  porcentaje de desperdicios del acero estructural de refuerzo en diversos elementos de hormigón
  armado perteneciente a la estructura de una vivienda de 2 plantas. *RECIAMUC*, 6(1), 25–39.
  <https://doi.org/10.26820/reciamuc/6.(1).enero.2022.25-39>
- **Enlace**: <https://reciamuc.com/index.php/RECIAMUC/article/view/769>.
- **Estado**: **verificar cita literal**. Los datos bibliográficos se confirmaron en Crossref el
  2026-10-02; la página del artículo no respondió, así que los porcentajes no se comprobaron.
- **Motivo de la propuesta**: dar un orden de magnitud empírico del desperdicio de acero en obra.
- **Pregunta textual del usuario que la originó**: pendiente: pedir al autor.
- **Término del título que respalda**: «desperdicios admisibles».
- **Ubicación prevista en la tesis**: Cap. 2 (desperdicio admisible), como referencia empírica.
- **Advertencias**:
  - Es una fuente **débil**: un solo caso de vivienda.
  - La revista es ecuatoriana y el contexto del caso no es necesariamente colombiano.
  - No usar su porcentaje como umbral normativo ni como valor por defecto de OICA (FR-002).

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
- **Advertencias**: un porcentaje de un APU es un supuesto de presupuesto, no una norma. Ver
  INF-015: el APU puede referirse solo a la pérdida irrecuperable.

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

- **Cita completa**: Russell, S. y Norvig, P. *Artificial Intelligence: A Modern Approach*.
  Pearson. Edición (4.ª, 2020/2021) y capítulo de búsqueda local y algoritmos genéticos por fijar.
- **Enlace**: no aplica (libro).
- **Estado**: **verificar edición y páginas**.
- **Motivo de la propuesta**: respaldar que los algoritmos genéticos son una técnica de IA
  (búsqueda local y computación evolutiva).
- **Pregunta textual del usuario que la originó**: pendiente: pedir al autor.
- **Término del título que respalda**: «con Inteligencia Artificial».
- **Ubicación prevista en la tesis**: Cap. 2 §2.4.
- **Advertencias**: citar la edición que se consulte físicamente o en biblioteca, con capítulo y
  página.

---

## REF-HOLLAND-1975 — Origen de los algoritmos genéticos

- **Cita completa**: Holland, J. H. (1975). *Adaptation in Natural and Artificial Systems*.
  University of Michigan Press. Edición y páginas por fijar.
- **Enlace**: no aplica (libro).
- **Estado**: **verificar edición y páginas**.
- **Motivo de la propuesta**: fuente original de los algoritmos genéticos.
- **Pregunta textual del usuario que la originó**: pendiente: pedir al autor.
- **Término del título que respalda**: «con Inteligencia Artificial».
- **Ubicación prevista en la tesis**: Cap. 2 §2.4.
- **Advertencias**: hay reimpresiones (MIT Press, 1992); usar la que se consulte.

---

## REF-GOLDBERG-1989 — Algoritmos genéticos en búsqueda y optimización

- **Cita completa**: Goldberg, D. E. (1989). *Genetic Algorithms in Search, Optimization, and
  Machine Learning*. Addison-Wesley. Páginas por fijar.
- **Enlace**: no aplica (libro).
- **Estado**: **verificar edición y páginas**.
- **Motivo de la propuesta**: referencia clásica de selección por torneo, cruce, mutación y
  elitismo, que usa el motor de OICA.
- **Pregunta textual del usuario que la originó**: pendiente: pedir al autor.
- **Término del título que respalda**: «con Inteligencia Artificial».
- **Ubicación prevista en la tesis**: Cap. 2 §2.4.
- **Advertencias**: verificar en el libro qué operadores describe antes de atribuirle cada uno.

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

