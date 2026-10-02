# Implementation Plan: Alineación de OICA con el título fijo de la tesis

**Branch**: `001-alineacion-titulo-tesis` (sin rama propia; se trabaja en `production`) |
**Date**: 2026-10-02 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-alineacion-titulo-tesis/spec.md`

## Summary

Cada término del título fijo debe tener un respaldo verificable, sin cambiar el plan que
produce el motor `secuencial-2`. La técnica es añadir una capa de **análisis posterior a la
optimización**: una función única, `cutting.analysis.analizar`, que el worker ejecuta entre
`optimize()` y `report.generate()`. Calcula seis cosas:

- la admisibilidad frente a un umbral opcional del usuario, guardado fuera de la huella del
  problema;
- la separación entre pérdida irrecuperable y saldo reutilizable;
- la agrupación del plan en patrones de corte;
- el resumen de compra y la verificación visible;
- la cota inferior Gilmore–Gomory, con scipy/HiGHS y un certificado lagrangiano que la hace
  válida aunque no converja;
- el aviso de masa nominal NSR-10 (Título C, Tabla C.3.5.3-2, verificada en T003).

Los resultados se guardan en `metricas.analisis`, sin migración. Se presentan en el Excel (cinco
hojas nuevas), en el PDF y PNG por patrones y en una nueva página `/archivos/[id]`, que incluye
la comparación de versiones. La evidencia existente se protege con la repetición de las 136
combinaciones y los 12 controles como regresión. La cota de esos ensayos se calcula sin
ejecutar el AG. El documento y `Referencias.md` se completan al final (US6).

## Technical Context

**Language/Version**: Python 3.12 (backend y worker); TypeScript con Next.js 15 / React 19
sobre Node 22 (frontend)

**Primary Dependencies**:
- Flask y Flask-SocketIO (gevent), Celery y SQLAlchemy;
- pandas 3.0.2, numpy 2.4.4, openpyxl, matplotlib y WeasyPrint;
- **nueva: scipy 1.18.1**, para `linprog` con HiGHS. Hay rueda musllinux cp312 x86_64 de
  37,5 MB y requiere `numpy>=2.0,<2.8`.

**Storage**: PostgreSQL 15. Se usan las columnas JSONB existentes (`execution_config`,
`metricas`), sin migración nueva. Los artefactos van en `UPLOAD_PATH`.

**Testing**:
- `unittest` (`backend/tests/`, con el Flask test client y SQLite);
- `scripts/check_cutting_container.py` (en el contenedor y con el código en memoria);
- `npm run typecheck`, `lint` y `build`, más axe.

**Target Platform**: contenedores Docker `python:3.12-alpine` (backend y worker) y Node 22
(frontend), detrás de Nginx. Local en WSL2 y producción en VPS.

**Project Type**: aplicación web (monorepo `backend/` + `frontend/`)

**Performance Goals**: el pipeline de 002 crece como máximo 25 % (SC-007). La cota tiene un
presupuesto de 2 s por diámetro y 4 s por plan (6 s en el borrador; se redujo por el margen medido de SC-007).

**Constraints**:
- El plan y las métricas son idénticos a la línea base (SC-002).
- Artefactos dentro de los límites actuales: PDF de 150 filas y PNG de 60 elementos a dpi 100.
- El espacio en C: es escaso (9,3 GB el 2026-10-02), así que la reconstrucción de imágenes
  requiere aprobación.

**Scale/Scope**: cartilla 002 con 67.443 piezas, cinco diámetros (#3–#7) y miles de barras; se
añaden una página de frontend y cinco hojas de Excel.

Ningún punto queda en NEEDS CLARIFICATION: todos se resolvieron en [research.md](research.md).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Evaluación previa | Tras el diseño |
|---|---|---|
| I. Validez física y de dominio | PASS. El validador `domain.validate` no cambia. Una cota mayor que el desperdicio es error de dominio (FR-015). La verificación se hace visible (FR-029). | PASS. La cota se certifica con duales y mochila exacta (R-02), y es válida aunque el LP no converja. Las invariantes de patrones y compra se comprueban en código y en pruebas. |
| II. Coherencia título–objetivos–app–documento | PASS. Cada término tiene respaldo (tabla de trazabilidad abajo) y los objetivos son los del autor (FR-024). | PASS. `Referencias.md` con estado de verificación (R-13). El documento se actualiza al final (US6). |
| III. Evidencia reproducible y motor versionado | PASS. `VERSION` sigue en `secuencial-2`; se añade `analisis.version = 'analisis-1'`. El umbral queda fuera de la huella. | PASS. Se repiten los 136 + 12 como regresión (R-03), sin nueva evidencia para el Cap. 4. La cota de los ensayos se calcula sin ejecutar el AG (R-12). Los registros históricos se leen como «no disponible». |
| IV. El AG optimiza; las demás técnicas miden | PASS. La cota, los patrones y la admisibilidad son métricas (FR-016). | PASS. `analizar` recibe el resultado ya validado y no devuelve barras. La cota no alimenta al optimizador. |
| V. Honestidad y trazabilidad | PASS. Sin umbral por defecto; los textos de la app no nombran normas no verificadas (FR-002, FR-018, tarea T003). Las fuentes llevan estado de verificación. | PASS. La tabla NSR-10 se verificó en T003 (Tabla C.3.5.3-2, p. C-47); INVIAS e IDU siguen sin verificar y la app no las nombra. La cota se rotula «no ajustada» o «no disponible» cuando corresponde. |
| VI. Simplicidad y compatibilidad | **Desviación**: dependencia nueva (scipy). Sin servicios nuevos ni migraciones. | Desviación justificada en Complexity Tracking. Los módulos nuevos van dentro de `backend/cutting/`. `optimizer.py`, `physical.py`, `parameters.py`, `normalize` y `validate` no cambian. Los artefactos respetan sus límites. |

**Resultado del gate**: PASS, con una desviación justificada (scipy). La reconstrucción de
imágenes sigue sujeta a aprobación del usuario.

## Project Structure

### Documentation (this feature)

```text
specs/001-alineacion-titulo-tesis/
├── spec.md
├── plan.md              # Este archivo
├── research.md          # Fase 0
├── data-model.md        # Fase 1
├── quickstart.md        # Fase 1
├── contracts/
│   ├── http-api.md
│   ├── artefactos.md
│   └── ui.md
├── checklists/requirements.md
└── tasks.md             # Fase 2 (/speckit-tasks; no lo crea este comando)
```

### Source Code (repository root)

```text
backend/
├── cutting/
│   ├── analysis.py          # NUEVO: analizar(problem, result, umbral) → metricas['analisis']
│   ├── patterns.py          # NUEVO: agrupación en patrones, patron_id e invariantes
│   ├── bound.py             # NUEVO: cota Gilmore–Gomory (scipy diferido), certificado y cota simple
│   ├── nominal.py           # NUEVO: tabla NSR-10 y avisos de masa
│   ├── report.py            # MOD: hojas nuevas, patron_id, PDF y PNG por patrones
│   ├── optimizer.py, physical.py, parameters.py, domain.py   # SIN CAMBIOS
│   └── estimation.py        # SIN CAMBIOS (la calibración se reinicia sola por la firma del código)
├── server.py                # MOD: umbral en uploaded_configuration y reprocess
├── celery_worker.py         # MOD: llamada a analizar y error de dominio
├── models/uploaded_file.py  # MOD: to_dict expone valido, umbral y analisis
└── tests/
    ├── test_analisis.py     # NUEVO: patrones, admisibilidad, compra, cota, NSR-10, umbral fuera de la huella
    └── test_cutting_api.py  # MOD: umbral en upload y reprocess, 400 sin encolar, campos en /file

config/backend/requirements-common.txt, constraints.txt   # MOD: scipy==1.18.1

scripts/
├── check_cutting_container.py   # MOD: modo de comparación contra la línea base (R-03)
└── cota_ensayos.py              # NUEVO: cota de los ensayos registrados (R-12)

frontend/src/
├── app/archivos/[id]/page.tsx              # NUEVO: detalle y comparación de versiones
├── components/file-detail/*.tsx            # NUEVO: secciones del detalle
├── components/file-upload.tsx              # MOD: campo de umbral
├── components/FilesTable.tsx               # MOD: insignia, enlace y umbral en el reproceso
└── components/tutorial/TutorialGuide.tsx   # MOD: glosario

docs/tesis-doc/Referencias.md, 01–04_Capitulo*.md          # US6 (al final)
INFERENCIAS_TESIS.md, .claude/diagnostics/ACADEMIC_RISKS.md # FR-026
```

**Structure Decision**: monorepo web existente. La lógica nueva va como módulos de dominio en
`backend/cutting/`, que comparten el backend y el worker. No se crean servicios, paquetes ni
migraciones. `services/` no se toca.

## Orden de implementación sugerido (insumo para `/speckit-tasks`)

1. **Base sin scipy**:
   - `nominal.py`, `patterns.py` y la admisibilidad, las pérdidas y la compra en
     `analysis.py`;
   - `bound.py` con import diferido y estado `no_disponible`;
   - pruebas unitarias;
   - regresión de los 136 + 12 en el contenedor actual (R-03).
2. **Integración**: worker, `to_dict`, umbral en la API (con sus pruebas) y artefactos
   (`report.py`).
3. **Frontend**: campo de umbral, insignia, `/archivos/[id]`, reproceso y glosario; typecheck,
   lint, build y axe.
4. **Dependencia**: **pedir aprobación** con estimación de espacio. Solo con ella, añadir scipy
   a requisitos y constraints y reconstruir backend y worker; los requisitos no se tocan antes,
   para que ninguna reconstrucción incidental ni la CI descarguen scipy. Ejecutar las pruebas de
   la cota, la fuerza bruta, `cota_ensayos.py` y SC-007.
5. **E2E local** según [quickstart.md](quickstart.md).
6. **Documento**: `Referencias.md`, capítulos 1–4 (FR-021 a FR-025) y archivos de control
   (FR-026).

## Trazabilidad

| Requisito | Respaldo en el diseño |
|---|---|
| FR-001–FR-006 | R-04, R-05; [http-api](contracts/http-api.md); [ui](contracts/ui.md); data-model §1, §2.1 |
| FR-007–FR-011 | R-06, R-10; [artefactos](contracts/artefactos.md); data-model §2.3 |
| FR-012–FR-017 | R-01, R-02, R-12; data-model §2.4 |
| FR-018–FR-020 | R-05, R-08, R-11; data-model §2.5 |
| FR-021–FR-026 | R-13; orden de implementación, paso 6 |
| FR-027–FR-029 | R-07, R-11; data-model §2.2; [ui](contracts/ui.md) |
| SC-001, SC-009 | Tabla término → respaldo (abajo) |
| SC-002 | R-03; quickstart 2–3 |
| SC-003 | Página de detalle e insignia; quickstart 6 |
| SC-004, SC-005 | R-06; quickstart 11 |
| SC-006 | R-02, R-12; quickstart 4–5 |
| SC-007 | Presupuesto de la cota; quickstart 16 |
| SC-008 | R-13 |
| SC-010 | R-07; quickstart 10 |

| Término del título | Respaldo |
|---|---|
| Diseño y desarrollo / aplicación web | App Next.js + Flask desplegada; documento corregido de «local» a «web» (FR-023) |
| Inteligencia Artificial | AG como computación evolutiva (glosario, Cap. 2, fuentes R-13) |
| distribución eficiente | Aprovechamiento, resumen de compra y brecha frente a la cota |
| barras de 6, 9 y 12 m | Catálogo por defecto y resumen de compra por longitud |
| en Colombia | Aviso NSR-10; procedencia anonimizada de 001/002; fuentes INVIAS, IDU y Res. 472 |
| desperdicios admisibles | Umbral del usuario, evaluación por proyecto y diámetro, pérdida irrecuperable |
| enfoque basado en patrones de corte | Agrupación en patrones y cota Gilmore–Gomory |
| nesting | Nesting lineal (1D): PNG por patrones y definición con fuente |

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Dependencia nueva `scipy==1.18.1` (Principio VI); obliga a reconstruir las imágenes de backend y worker | La cota Gilmore–Gomory necesita resolver LP con duales fiables en cada iteración de generación de columnas; HiGHS es el estándar robusto | **Simplex propio en numpy**: el usuario lo descartó (más código propio que validar). **highspy** (6,6 MB, mismo solver): queda como alternativa si el espacio impide scipy, pero el usuario eligió scipy. **Sin cota**: incumple FR-012 y el término «patrones de corte». Mitigación: import diferido (la app funciona sin scipy, con la cota «no disponible») y reconstrucción solo con aprobación y estimación de espacio. |
