# Implementation Plan: Presentación de resultados para el usuario

**Branch**: `feat/spec-002-presentacion-resultados` | **Date**: 2026-10-03 · enmendado 2026-10-04 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/002-presentacion-resultados/spec.md`

## Summary

Reorganizar y completar lo que ve el usuario en cuatro salidas, sin tocar el plan de corte:

- **Excel**: hoja «Resumen» legible con totales de compra al inicio; hoja «Trazabilidad» al final;
  sin «Metricas» ni `stock_id`; parámetros legibles; nuevo orden de hojas.
- **PDF**: lo útil primero (compra y patrones) y los datos técnicos al final. Encabezado con
  versión, perfil y fecha; imagen de nesting incrustada; línea de cobertura; coma decimal.
- **Imagen**: medidas sobre las piezas, leyenda, 200 dpi y cobertura.
- **Pantalla**:
  - **Explorador interactivo de todos los patrones** (enmienda 2026-10-04): dibujo a escala
    común, filtros por diámetro, etapa, origen y pedido, orden seleccionable, y detalle con
    pedidos y rangos de barras.
  - Totales de compra.
  - Sin la tarjeta de cota simple.

**Enmienda 2026-10-04**:

- El explorador sustituye la sección estática de los diez más repetidos.
- Se retira `analisis-2`: el análisis no cambia.
- Los patrones se reconstruyen bajo demanda desde `ProcessingResult.resultados` con una **única
  ruta nueva de solo lectura**, `GET /patrones/<storage_uuid>`, que reutiliza `patterns.agrupar`
  y `report.patrones_rows`.

El enfoque técnico está en [research.md](research.md) (R-01 a R-19). Los formatos, en
[contracts/artefactos.md](contracts/artefactos.md), [contracts/ui.md](contracts/ui.md) y
[contracts/api-patrones.md](contracts/api-patrones.md).

## Technical Context

**Language/Version**: Python 3.12 (backend y worker); TypeScript con Node 22 (frontend).

**Primary Dependencies**: las existentes, sin dependencias nuevas.
- Backend: pandas y openpyxl (Excel), WeasyPrint (PDF), matplotlib (PNG) y Flask (la ruta
  nueva).
- Frontend: Next.js 15 y React 19, con los primitivos de `components/ui/`. El explorador se
  dibuja con HTML y CSS: sin librerías de gráficos (R-17).

**Storage**: PostgreSQL, columnas JSON `processing_results.metricas` y `resultados`. Sin
migraciones ni datos nuevos guardados: tras la enmienda, `analisis` no cambia. Los artefactos van
en `UPLOAD_PATH/<storage_uuid>/`.

**Testing**:
- Backend: `unittest`, ejecutado con `scripts/check_cutting_container.py --all-tests` en el
  contenedor del backend. La ruta nueva se prueba con el cliente de pruebas de Flask y SQLite en
  memoria, como `test_cutting_api.py`.
- Regresión: `--comparar`, sobre 148 registros.
- Artefactos: `--artifacts-smoke` y `scripts/verify_sequential_result.py`.
- Frontend: `npm run typecheck`, `lint` y `build`, más axe. No hay runner de pruebas del
  frontend, y no se añade uno.

**Target Platform**: contenedores Linux (Docker Compose) en local y en la VPS; navegador moderno
de escritorio, tableta y teléfono.

**Project Type**: aplicación web (monorepo `backend/` + `frontend/`).

**Performance Goals**:
- El tiempo total de la 002 no crece más de 10 % sobre la mediana vigente de 26,75 s (SC-007).
- La generación de la imagen y del PDF sigue acotada.
- La ruta de patrones responde en ≤ 2 s con la 002 (SC-009). La medición exploratoria da unos
  0,5 s (R-18).
- La interacción del explorador es inmediata, < 200 ms (SC-012).

**Constraints**:
- No se tocan `optimizer.py`, `physical.py`, `parameters.py`, ni `normalize` y `validate`.
- No se toca `analysis.py`: se retira `analisis-2`.
- El formato del inventario final no cambia.
- El tamaño de la imagen sigue acotado (BUG-005).
- El backend corre con gevent: el `json.loads` de unos 12,5 MB ocupa unos 0,3 s, mitigado con una
  caché LRU por `storage_uuid` (R-18).
- C: tiene poco espacio libre: reconstruir imágenes requiere aprobación.

**Scale/Scope**:
- Cartilla 002: 13.955 barras, 136 patrones, 67.443 piezas, 137 pedidos y 145 rangos de barras.
- Backend:
  - `report.py`;
  - un módulo puro nuevo, `vista_patrones.py`;
  - una ruta nueva en `server.py`;
  - la llamada del worker.
- Frontend: tres componentes existentes ajustados, el explorador nuevo
  (`file-detail/patterns/`) y seis tokens de color.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Evaluación previa | Tras el diseño (incluida la enmienda) |
|---|---|---|
| I. Validez física y de dominio | PASS. El validador no cambia y `generate()` sigue llamando a `validate()` antes de escribir. | PASS. Los totales de compra y la cobertura se derivan de datos ya validados (R-06, R-13). La vista de patrones comprueba sus invariantes (Σ repeticiones, pedidos y coherencia con `analisis.patrones`) y, si alguna falla, devuelve un error en lugar de datos (R-16, data-model §8.3). |
| II. Coherencia título–objetivos–app–documento | PASS. Hace visibles en la web «patrones de corte» y «nesting» (FR-015) y la compra con totales (objetivo 1). | PASS. El explorador muestra en la web los patrones reales y su nesting lineal. Ningún texto nuevo afirma optimalidad ni normas no verificadas, y la cota simple deja de destacarse. |
| III. Evidencia reproducible y motor versionado | PASS. `VERSION` sigue en `secuencial-2` y el análisis sigue en `analisis-1` (sin cambios de cálculo ni de versión). El umbral sigue fuera de la huella. | PASS. «Trazabilidad» conserva todos los datos técnicos y los parámetros resueltos en JSON (R-07). La vista de patrones **solo lee** `resultados`: no ejecuta el AG ni regenera artefactos, y coincide con el Excel por construcción (R-16). Regresión de 148 registros con 0 diferencias (FR-021). |
| IV. El AG optimiza; las demás técnicas miden | PASS. Solo cambia la presentación de métricas ya derivadas. | PASS. `report.py`, `analysis.py` y `vista_patrones.py` no devuelven barras al optimizador ni lo alimentan. |
| V. Honestidad técnica y académica | PASS. La cobertura evita que una vista acotada parezca el plan completo. | PASS. El PDF, el PNG y el explorador declaran cuántos patrones y barras muestran (con filtros incluidos). Lo que falta en las versiones históricas se rotula «no disponible», con su motivo. El riesgo del bloqueo de gevent queda declarado (R-18). |
| VI. Simplicidad y compatibilidad | PASS. Sin dependencias, servicios ni migraciones nuevas. | PASS, con una adición justificada: una **ruta HTTP de solo lectura** (contracts/api-patrones.md). Es necesaria porque `GET /file/<id>` no envía `resultados` (unos 12,5 MB) y no conviene enviarlos. Sin librerías de gráficos ni de pruebas. Se reutilizan `agrupar`, `patrones_rows`, `secuencia_legible`, `form-controls` y el patrón de diagrama de `page.tsx`. Los tokens `data/stage-*` se registran en el sistema visual (R-17). La regla de diseño 12 («no cambiar la API para resolver un problema visual») no aplica: es una funcionalidad nueva aprobada por el usuario, no un arreglo visual. |

**Resultado del gate**: PASS. La única adición (una ruta de solo lectura) está justificada en
Complexity Tracking. La reconstrucción de imágenes para el E2E sigue sujeta a la aprobación del
usuario.

## Project Structure

### Documentation (this feature)

```text
specs/002-presentacion-resultados/
├── plan.md              # Este archivo
├── research.md          # Fase 0: decisiones técnicas (R-10 retirada; R-16 a R-19 de la enmienda)
├── data-model.md        # Fase 1: estructuras derivadas; §8 vista de patrones
├── quickstart.md        # Fase 1: guía de validación; §7 explorador
├── contracts/
│   ├── artefactos.md    # Excel, PDF, PNG e inventario (sustituye en parte al de la spec 001)
│   ├── ui.md            # Detalle del proyecto (sustituye en parte al de la spec 001); §5 explorador
│   └── api-patrones.md  # Enmienda: GET /patrones/<storage_uuid>
├── checklists/requirements.md
└── tasks.md             # Fase 2 (/speckit-tasks)
```

### Source Code (repository root)

```text
backend/
├── cutting/
│   ├── report.py            # Excel, PDF y PNG: cambios principales (sin cambios para el explorador)
│   └── vista_patrones.py    # Nuevo (enmienda): barras_desde_resultados, vista; reutiliza
│                            #   patterns.agrupar y report.patrones_rows
├── server.py                # Nueva ruta GET /patrones/<storage_uuid>, con LRU por uuid
├── celery_worker.py         # Número de versión antes de generate(); pasa version a generate()
└── tests/
    ├── test_report_presentacion.py   # Nuevo: hojas, resumen, totales, PDF, PNG, cobertura
    ├── test_vista_patrones.py        # Nuevo (enmienda): reconstrucción = agrupar = hoja Patrones; invariantes §8.3
    └── test_cutting_api.py           # Actualizar: «Resumen»/«Trazabilidad» en vez de «Metricas»; ruta /patrones

frontend/src/
├── app/globals.css                   # Tokens --color-data-stage-1…6 (enmienda)
└── components/file-detail/
    ├── FileDetail.tsx                # Inserta PatternExplorer entre PurchaseSummary y QualitySection
    ├── PurchaseSummary.tsx           # Totales por diámetro y general
    ├── QualitySection.tsx            # Sin la tarjeta de cota simple
    ├── types.ts                      # VistaPatrones, PatronExplorable, PiezaPatron, RangoBarras…
    └── patterns/                     # Nuevo (enmienda)
        ├── PatternExplorer.tsx       # Carga diferida, estados, filtros, orden, cobertura y lista
        ├── PatternRow.tsx            # Fila-botón con la barra a escala
        ├── PatternDetail.tsx         # Piezas, pedidos y rangos de barras por tramos
        └── filtros.ts                # Funciones puras: filtrar, ordenar, cobertura y aporte por pedido

docs/oica-redesign/DESIGN-SYSTEM.md   # Registrar color/data/stage-1…6 (enmienda)

scripts/
└── check_cutting_container.py   # Solo si la nueva firma de generate() lo exige (argumentos opcionales)
```

`analysis.py` y `test_analisis.py` **ya no cambian**: se retira `analisis-2`.

**Structure Decision**: monorepo web existente.

- Backend: lo nuevo va en `backend/cutting/`, más una ruta en `server.py`, sin blueprints nuevos
  (el proyecto no los usa).
- Frontend: lo nuevo va en `components/file-detail/` (subcarpeta `patterns/`).
- No se crean paquetes ni servicios.

## Complexity Tracking

| Adición | Por qué se necesita | Alternativa más simple descartada y por qué |
|---|---|---|
| Ruta `GET /patrones/<storage_uuid>` (solo lectura) | El explorador necesita todos los patrones con sus pedidos y barras. `GET /file/<id>` no incluye `resultados` (12,5 MB en la 002) y no debe incluirlo. | (a) Guardar todo en `analisis`: hace crecer el JSONB, solo cubre las versiones nuevas y obliga a versionar el análisis. (b) Enviar `resultados` al navegador: unos 12,5 MB por visita. (c) Un `patrones.json` por versión: no cubre las versiones ya procesadas (R-16). |
| Tokens `color/data/stage-1…6` | Las etapas son categorías y el sistema visual no tiene una paleta categórica. | Hardcodear colores: viola las reglas de diseño 1 y 2. |
