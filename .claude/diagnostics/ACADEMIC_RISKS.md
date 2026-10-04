# Riesgos Académicos

> Inconsistencias entre el documento de tesis y la aplicación, gaps de alcance, problemas metodológicos y riesgos que afectan la validez académica del proyecto.

---

## RIESGO-AC-001 — AG ignora diámetro de barra

**Severidad:** CRÍTICA

**Descripción:**
El algoritmo genético procesa todas las piezas juntas sin importar el diámetro (`N° de Barra`). Un plan de corte que asigna piezas de diámetro #4 y #8 a la misma barra es físicamente imposible. Si se presenta este resultado en el Cap. 4, la tesis sería técnicamente incorrecta.

**Evidencia:**
- `services/backend/celery_worker.py` líneas 396-402: `N° de Barra` ignorado en la transformación a `df_ag`.

**Impacto académico:**
- El Cap. 4 no puede mostrar resultados válidos hasta que esto se resuelva.
- La comparativa con la "Cartilla N°1" sería inválida.

**Inferencias relacionadas:** INF-001, INF-006

**Estado:** [PENDIENTE — bloquea Cap. 4]

---

## RIESGO-AC-002 — Capítulo 3 describe arquitectura que no existe

**Severidad:** ALTA

**Descripción:**
La sección 3.3.3 (Desarrollo del Frontend) del Capítulo 3 describe una arquitectura con AWS Lambda, S3 y presigned URLs. Esta arquitectura fue descartada. El código actual usa Docker Compose con almacenamiento local.

**Evidencia:**
- `docs/tesis-doc/03_Capitulo3.md` sección 3.3.3.
- No hay ninguna referencia a AWS en el código de producción.

**Impacto académico:**
- El documento es inconsistente con la implementación real.
- Un evaluador que lea el Cap. 3 no entendería cómo funciona la app real.

**Inferencias relacionadas:** INF-003

**Estado:** [CONFIRMADO — pendiente actualización en Bloque E]

---

## RIESGO-AC-003 — Objetivo de reutilización de desperdicios no implementado

**Severidad:** MEDIA

**Descripción:**
El Objetivo Específico 3 del Capítulo 1 menciona "registrar la reutilización de los desperdicios de barras de acero de proyectos anteriores". El código siempre pasa `desperdicios_previos = []`, haciendo que este objetivo no se cumpla en ninguna ejecución.

**Evidencia:**
- `services/backend/celery_worker.py`: `desperdicios_previos = []`
- `docs/tesis-doc/01_Capitulo1.md`: Objetivo Específico 3.

**Impacto académico:**
- Si este objetivo no se implementa, debe eliminarse de los objetivos o ajustarse el alcance en el documento.
- El Cap. 4 no puede mostrar resultados de reutilización.

**Inferencias relacionadas:** INF-008

**Estado:** [PENDIENTE — requiere decisión del usuario sobre alcance]

---

## RIESGO-AC-004 — Capítulo 4 sin resultados reales

**Severidad:** ALTA

**Descripción:**
El Capítulo 4 (Análisis de Resultados) tiene apenas 16 líneas de contenido real. No hay tablas de resultados cuantitativos, no hay análisis de eficiencia, no hay comparativa completa con la Cartilla N°1.

**Evidencia:**
- `docs/tesis-doc/04_Capitulo4.md`: 16 líneas, una imagen, texto introductorio.

**Impacto académico:**
- Sin Cap. 4 completo, la tesis no puede entregarse.
- El Cap. 4 depende de que la app funcione correctamente (Bloques A, B, C).

**Inferencias relacionadas:** INF-005

**Estado:** [CONFIRMADO — bloqueado hasta Bloque C]

---

## RIESGO-AC-005 — Abstract y keywords vacíos

**Severidad:** MEDIA

**Descripción:**
El Capítulo 1 del documento tiene el Abstract y los Keywords completamente vacíos (solo tiene el texto de la plantilla).

**Evidencia:**
- `docs/tesis-doc/01_Capitulo1.md` líneas 3-9.

**Impacto académico:**
- El abstract es uno de los primeros elementos que evalúa el comité.

**Inferencias relacionadas:** Ninguna

**Estado:** [CONFIRMADO — pendiente en Bloque E]

---

## RIESGO-AC-006 — Secciones del Marco Teórico con notas sin completar

**Severidad:** MEDIA

**Descripción:**
El Capítulo 2 tiene al menos 4 secciones marcadas con `> Nota:` que indican contenido pendiente:
- Completar con información de Next.js.
- Hablar de Docker como open source.
- Hablar sobre qué subrama de IA se usa (algoritmo genético vs IA generativa vs predictiva).
- Buscar y completar literal 2.2 (clasificación de problemas de corte).
- Completar literal 2.3 (algoritmos clásicos — menos IA, verificar bibliografía).

**Evidencia:**
- `docs/tesis-doc/02_Capitulo2.md` múltiples líneas con `> Nota:`.

**Impacto académico:**
- El Marco Teórico incompleto puede ser señalado por el comité evaluador.

**Estado:** [CONFIRMADO — pendiente en Bloque E]

---

## RIESGO-AC-007 — Guía de la app con afirmaciones sin respaldo en código ni tesis

**Severidad:** MEDIA (visible para usuarios y evaluadores de la app)

**Descripción:**
El glosario/FAQ de `/tutorial` (`frontend/src/components/tutorial/TutorialGuide.tsx`) contenía:
- "Método Búfalo" como técnica de optimización: no aparece en `backend/` ni en `docs/tesis-doc/`.
- "#4 pesa aproximadamente 0.668 kg/m": la plantilla (`TablaBarras`) y la NSR-10 dan 0,994 kg/m.
- "Método intensivo… máxima eficiencia": el perfil se llama Profundo y el Cap. 3 declara que no se afirma que más población siempre mejore.
- "Solo XLSX" y "unos segundos": la app acepta XLSX/CSV y el tiempo depende del tamaño (hay estimador).

**Resolución (2026-09-29, rediseño Bloque J):** corregido como error factual evidente. Se eliminó
"Método Búfalo", se corrigió la masa, se renombró el perfil con los parámetros del Cap. 3 y se
añadieron términos del Cap. 3 (grupo de ejecución, catálogo, inventario, pérdida por corte,
mínimo reutilizable, inventario final).

**Pendiente de validación del usuario:** confirmar que "Método Búfalo" no corresponde a una
referencia que los autores quieran conservar; si la tiene, debe citarse en el Marco Teórico antes
de reincorporarla.

**Estado:** [RESUELTO EN APP — pendiente confirmación sobre "Método Búfalo"]

---

## RIESGO-AC-008 — Título propuesto incoherente con el modelo implementado

**Severidad:** ALTA (afecta portada, resumen y defensa)

**Descripción:**
El título propuesto el 2026-09-29 afirma «Inteligencia Artificial», «desperdicios admisibles»,
«enfoque basado en patrones de corte y nesting» y alcance «en Colombia». El Cap. 2 §2.1 excluye
nesting bidimensional y modelos de IA distintos del algoritmo genético; el modelo minimiza el
desperdicio sin umbral admisible; la evaluación usa dos cartillas sin generalización. Además, el
título vigente dice «aplicación local», aunque la aplicación está desplegada como web.

**Inferencias relacionadas:** INF-014, INF-012, INF-011

**Estado:** [EN MITIGACIÓN — 2026-10-02] El usuario fijó el título palabra por palabra y aportó
los objetivos vigentes; se aceptó su redacción ajustada (Cap. 1 §1.3 actualizado). La alineación de
la app con cada término se especifica en `specs/001-alineacion-titulo-tesis/spec.md` y se
planificó en `plan.md` (2026-10-02; cota con scipy, INF-016; umbral frente a INF-012, INF-015).
Implementado y validado el 2026-10-02: la app respalda cada término del título (umbral, patrones,
cota, nesting lineal en el PNG, aviso NSR-10, resumen de compra y detalle web). Cap. 1–4 y
`Referencias.md` están actualizados. Sigue **en mitigación** por:
- revisión del director (objetivos e INF-015);
- fuentes sin verificar: IDU (por localizar), fuente de «nesting lineal», páginas de Holland y
  Goldberg, y la cita literal de Russell-Norvig.
  - Ya verificadas: Res. 472/2017 y 1257/2021 (2026-10-02); INVIAS 2022 art. 640 y RECIAMUC
    2022, con los PDF del autor (2026-10-03).
  - Russell-Norvig tiene verificadas edición, sección y página;
- la «pregunta textual del usuario» de cada ficha, que no quedó registrada.

---

## RIESGO-AC-009 — OE5 sin comparación con datos de compra de una obra real

**Severidad:** MEDIA (afecta la evaluación del Cap. 4 y la defensa del objetivo 5)

**Descripción:**
El objetivo específico 5 pide evaluar la eficiencia con un proyecto real. La cartilla 002 es de una
obra colombiana real, pero solo se tiene su demanda: no hay facturas, remisiones ni resumen de compra.
Una búsqueda pública (2026-10-02) no encontró proyectos colombianos con cartilla y resumen de compra.
Por decisión del usuario, por ahora OE5 se evalúa con heurísticas de referencia y con la cota inferior
por patrones de corte (Gilmore–Gomory). No se debe afirmar que OICA supera el desperdicio real de obra.

**Mitigación:** cota y brecha (spec 001, FR-012 a FR-017 y FR-025). Si el usuario consigue al menos
los kg comprados por diámetro de una obra colombiana, se añade como comparación anonimizada.

**Inferencias relacionadas:** INF-014, INF-012

**Estado:** [PENDIENTE — dato de compra real a cargo del usuario]

---

## RIESGO-AC-010 — Borrador Word «Tesis final 1» con resultados y fuentes sin respaldo

**Severidad:** ALTA (el borrador circula fuera del repositorio y podría entregarse así)

**Descripción:**
Al generar `docs/tesis-doc/Tesis_F.docx` (2026-10-03) se contrastó el borrador del autor
«Tesis final 1» (PDF del 2026-10-03) con el documento vigente en Markdown. El borrador:
- conserva en el Cap. 4 el caso histórico de 683 piezas, retirado por decisión del autor, con cifras
  incoherentes entre sí (10.76 % de desperdicio frente a 3.2 % «estimado»; 89.24 % frente a 97 %);
- afirma un ahorro de 9–14 % y una eficiencia «típica» manual de 75–80 % sin fuente;
- muestra una captura antigua de la interfaz con «método Búfalo» (ver RIESGO-AC-007);
- cita la NTC 2289, la ASTM A706, una tabla de diámetros en milímetros, el precio del acero en 2025
  y libros generales de HTML/CSS/JavaScript sin ficha en `Referencias.md`;
- describe la «Cartilla N°1» como proyecto académico de la asignatura Construcción de edificaciones.
  Las vigas de la cartilla 001 coinciden en longitudes con esa cartilla, mientras que INF-014 registra
  que 001 y 002 provienen de una obra colombiana. La procedencia de 001 no está confirmada.

**Mitigación:** `Tesis_F.docx` se construyó desde `docs/tesis-doc/*.md` y la evidencia de
`tests/benchmarks/`; del borrador solo se tomó contexto cualitativo. Cada punto anterior quedó como
«Nota pendiente» resaltada en el Word. Confirmar con el autor la procedencia de 001.

**Inferencias relacionadas:** INF-014, INF-005

**Estado:** [PENDIENTE — procedencia de 001 y fuentes a cargo del autor]
