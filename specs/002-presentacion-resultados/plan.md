# Implementation Plan: Presentación de resultados para el usuario

**Branch**: `002-presentacion-resultados` (sin hook de ramas; rama actual `production`) | **Date**: 2026-10-03 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/002-presentacion-resultados/spec.md`

## Summary

Reorganizar y completar lo que ve el usuario en cuatro salidas, sin tocar el plan de corte:

- **Excel**: hoja «Resumen» legible con totales de compra al inicio; hoja «Trazabilidad» al final;
  sin «Metricas» ni `stock_id`; parámetros legibles; nuevo orden de hojas.
- **PDF**: lo útil primero (compra y patrones) y los datos técnicos al final. Encabezado con
  versión, perfil y fecha; imagen de nesting incrustada; línea de cobertura; coma decimal.
- **Imagen**: medidas sobre las piezas, leyenda, 200 dpi y cobertura.
- **Pantalla**: sección «Patrones de corte» con vista previa, totales de compra y sin la tarjeta
  de cota simple.

El análisis pasa a `analisis-2` solo para guardar la secuencia de los patrones más repetidos.
El enfoque técnico está en [research.md](research.md); los formatos, en
[contracts/artefactos.md](contracts/artefactos.md) y [contracts/ui.md](contracts/ui.md).

## Technical Context

**Language/Version**: Python 3.12 (backend y worker); TypeScript con Node 22 (frontend).

**Primary Dependencies**: las existentes, sin dependencias nuevas.
- Backend: pandas y openpyxl (Excel), WeasyPrint (PDF), matplotlib (PNG).
- Frontend: Next.js 15 y React 19, con los primitivos de `components/ui/`.

**Storage**: PostgreSQL, columna JSON `processing_results.metricas`. Sin migraciones: `analisis-2`
solo añade un campo dentro del JSON. Los artefactos van en `UPLOAD_PATH/<storage_uuid>/`.

**Testing**:
- Backend: `unittest`, ejecutado con `scripts/check_cutting_container.py --all-tests` en el
  contenedor del backend.
- Regresión: `--comparar`, sobre 148 registros.
- Artefactos: `--artifacts-smoke` y `scripts/verify_sequential_result.py`.
- Frontend: `npm run typecheck`, `lint` y `build`, más axe.

**Target Platform**: contenedores Linux (Docker Compose) en local y en la VPS; navegador moderno
de escritorio, tableta y teléfono.

**Project Type**: aplicación web (monorepo `backend/` + `frontend/`).

**Performance Goals**: el tiempo total de la 002 no crece más de 10 % sobre la mediana vigente de
26,75 s (SC-007). La generación de la imagen y del PDF sigue acotada.

**Constraints**:
- No se tocan `optimizer.py`, `physical.py`, `parameters.py`, ni `normalize` y `validate`.
- El formato del inventario final no cambia.
- El tamaño de la imagen sigue acotado (BUG-005).
- C: tiene poco espacio libre: reconstruir imágenes requiere aprobación.

**Scale/Scope**:
- Cartilla 002: 13.955 barras, 136 patrones, 67.443 piezas y miles de filas en «Cortes».
- Un módulo backend (`report.py`), una línea de `analysis.py` y la llamada del worker.
- Cuatro componentes frontend (uno nuevo).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Evaluación previa | Tras el diseño |
|---|---|---|
| I. Validez física y de dominio | PASS. El validador no cambia y `generate()` sigue llamando a `validate()` antes de escribir. | PASS. Los totales de compra y la cobertura se derivan de datos ya validados y se comprueban en pruebas (R-06, R-13). |
| II. Coherencia título–objetivos–app–documento | PASS. Hace visibles en la web «patrones de corte» y «nesting» (FR-015) y la compra con totales (objetivo 1). | PASS. Ningún texto nuevo afirma optimalidad ni normas no verificadas; la cota simple deja de destacarse para no inducir lecturas erróneas. |
| III. Evidencia reproducible y motor versionado | PASS. `VERSION` sigue en `secuencial-2`; el análisis pasa a `analisis-2` (versionado explícito). El umbral sigue fuera de la huella. | PASS. «Trazabilidad» conserva todos los datos técnicos y, además, los parámetros resueltos exactos en JSON (R-07). Regresión de 148 registros con 0 diferencias (FR-021). Los artefactos históricos no se regeneran. |
| IV. El AG optimiza; las demás técnicas miden | PASS. Solo cambia la presentación de métricas ya derivadas. | PASS. `report.py` y `analysis.py` no devuelven barras ni alimentan al optimizador. |
| V. Honestidad técnica y académica | PASS. La cobertura evita que una vista acotada parezca el plan completo. | PASS. Las vistas declaran cuántos patrones y barras muestran; lo que falta en versiones históricas se rotula «no disponible». |
| VI. Simplicidad y compatibilidad | PASS. Sin dependencias, servicios ni migraciones nuevas. | PASS. Se reutilizan `patrones_rows`, `cota_rows`, `admisibilidad_rows`, `mas_repetidos`, `secuencia_legible` y los primitivos de UI. El inventario y el auditor siguen compatibles (R-06). |

**Resultado del gate**: PASS, sin desviaciones. La reconstrucción de imágenes para el E2E sigue
sujeta a aprobación del usuario.

## Project Structure

### Documentation (this feature)

```text
specs/002-presentacion-resultados/
├── plan.md              # Este archivo
├── research.md          # Fase 0: decisiones técnicas
├── data-model.md        # Fase 1: estructuras derivadas y cambio de analisis-2
├── quickstart.md        # Fase 1: guía de validación
├── contracts/
│   ├── artefactos.md    # Excel, PDF, PNG e inventario (sustituye en parte al de la spec 001)
│   └── ui.md            # Detalle del proyecto (sustituye en parte al de la spec 001)
├── checklists/requirements.md
└── tasks.md             # Fase 2 (/speckit-tasks)
```

### Source Code (repository root)

```text
backend/
├── cutting/
│   ├── report.py          # Excel, PDF y PNG: cambios principales
│   └── analysis.py        # resumen_patrones con secuencia; VERSION_ANALISIS = 'analisis-2'
├── celery_worker.py       # Número de versión antes de generate(); pasa version a generate()
└── tests/
    ├── test_report_presentacion.py   # Nuevo: hojas, resumen, totales, PDF, PNG, cobertura
    ├── test_cutting_api.py           # Actualizar: lee «Resumen»/«Trazabilidad» en vez de «Metricas»
    └── test_analisis.py              # Actualizar: analisis-2 y secuencia en el top

frontend/src/components/file-detail/
├── FileDetail.tsx         # Inserta PatternsSection
├── PatternsSection.tsx    # Nuevo
├── PurchaseSummary.tsx    # Totales por diámetro y general
├── QualitySection.tsx     # Sin la tarjeta de cota simple
└── types.ts               # PatronResumen.secuencia?, ResumenPatrones

scripts/
└── check_cutting_container.py   # Solo si la nueva firma de generate() lo exige (argumentos opcionales)
```

**Structure Decision**: monorepo web existente. Todo el backend nuevo va en `backend/cutting/` y
el frontend en `components/file-detail/`. No se crean paquetes ni servicios.

## Complexity Tracking

Sin violaciones de la constitución que justificar.
