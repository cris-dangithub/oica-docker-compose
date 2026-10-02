# Quickstart de validación — feature 001

Esta guía describe escenarios ejecutables que prueban la feature de punta a punta. Los
detalles de estructura están en [data-model.md](data-model.md) y en [contracts/](contracts/).
La columna **scipy** indica si el escenario necesita la imagen reconstruida con scipy (R-01),
que requiere aprobación previa por el espacio en C:.

## Prerrequisitos

- Stack local saludable (`docker compose ps`). Worker: `oica-validation-celery_worker-1`.
- Cartillas: `tests/data/001/001-pruebaInicial.xlsx` y `tests/data/002/002-ingeBigTest.xlsx`.
- Línea base: `tests/benchmarks/2026-09-13-fisico-matriz-final.jsonl` y
  `2026-09-13-fisico-control-{cizalla,fin-etapa}.jsonl`.
- Antes de reconstruir imágenes: comprobar el espacio libre (`df -h /mnt/c`), estimar y pedir
  aprobación.
- Las imágenes llevan el código dentro, sin montajes. Los escenarios E2E (6, 7, 9, 10, 12, 13 y
  15) requieren imágenes reconstruidas con el código nuevo, con aprobación previa (T021).

## Escenarios

| # | Escenario | Cómo | Resultado esperado | scipy |
|---|---|---|---|---|
| 1 | Pruebas backend | `python3 scripts/check_cutting_container.py --all-tests` (código en memoria) o, tras reconstruir, `cd backend && python -m unittest discover -s tests -p 'test_*.py'` | 0 fallos. Las pruebas de la cota se omiten con un motivo explícito si falta scipy. | parcial |
| 2 | Regresión SC-002 | `scripts/check_cutting_container.py` en modo de comparación contra las tres líneas base (136 + 12) | 0 diferencias en las claves no temporales. JSONL nuevo en `tests/benchmarks/`. | no |
| 3 | Umbral sin efecto en el plan | Prueba unitaria: mismas barras y misma `input_hash` con y sin `umbral_desperdicio_pct` | Barras, métricas y huella idénticas (FR-005). | no |
| 4 | Cota frente a ensayos (SC-006, FR-017) | `scripts/cota_ensayos.py` sobre las tres líneas base | En el 100 % de los registros, el desperdicio es ≥ la cota en el proyecto y en cada diámetro. JSONL nuevo. | sí |
| 5 | Cota frente al óptimo | Prueba unitaria con instancias pequeñas resueltas por fuerza bruta, y el caso de una pieza y una barra | `cota ≤ óptimo`; en el caso analítico, `cota = ⌈n/q⌉·L`. | sí |
| 6 | Admisibilidad (US1) | Subir 001 con umbral 5 % y luego reprocesar con 10 % | 5 % da `excede` con diferencia en pp y los diámetros que exceden; 10 % da `dentro`. El desperdicio y las barras son idénticos en ambas versiones. | no* |
| 7 | Sin umbral | Subir 001 sin umbral | Estado «sin evaluar». Se muestran desperdicio, pérdida irrecuperable y saldo reutilizable. | no* |
| 8 | Umbral inválido | `POST /upload` con `0`, `100`, `-1` y `abc` | 400 sin encolar (prueba de API). | no |
| 9 | Comparación de versiones (FR-028) | Procesar 001 con los perfiles rápido, balanceado y profundo; abrir `/archivos/<id>` | La tabla muestra perfil, tiempo, desperdicio, umbral, estado y verificación de cada versión. | no* |
| 10 | Resumen de compra (US2, SC-010) | 002 en `/archivos/<id>` y hoja `Resumen de compra` | Por (diámetro, longitud), la suma de barras es igual a las barras del plan. Las de inventario van aparte. | no* |
| 11 | Patrones (US3, SC-004, SC-005) | 002: hojas `Patrones` y `Barras` | `Σ repeticiones = filas de Barras`; la reconstrucción da la demanda exacta; se mide `filas Barras / filas Patrones` y se registra si es ≥ 5. | no |
| 12 | PDF y PNG por patrones | Descargar los artefactos de 002 | Tabla de patrones acotada con el aviso de omitidos; PNG titulado «Nesting lineal por patrones de corte»; tamaños dentro de los límites actuales. | no |
| 13 | Aviso de masa de referencia (US5) | Copia temporal de 001 con la masa de #4 alterada en más de 1 %, en un directorio temporal y nunca dentro de `tests/data/` | Aviso rotulado «masa nominal NSR-10 (Título C, Tabla C.3.5.3-2)» con diámetro, valor de la cartilla y valor nominal; el plan se genera igualmente. La cartilla original no muestra avisos. | no |
| 14 | Error de dominio (FR-015) | Prueba unitaria inyectando una cota mayor que el desperdicio | La versión queda en `error_processing` con «Error de dominio:». | no |
| 15 | Historial | Abrir versiones anteriores a `analisis-1` (por ejemplo id 36, 38, 39) | Sin errores; los campos nuevos aparecen como «no disponible». No se modifican registros. | no |
| 16 | Rendimiento (SC-007) | `check_cutting_container.py --artifacts-smoke` con 002, balanceado y semilla 0: antes de la feature (T002) y después (T055) | `motor + análisis + artefactos` ≤ 1,25 × base. | sí |
| 17 | Frontend | `cd frontend && npm run typecheck && npm run lint && npm run build`; axe en `/subir-cartilla`, `/archivos` y `/archivos/<id>` a 1440, 820 y 390 px | Sin errores y sin violaciones nuevas de axe. | no |

\* Funciona sin scipy; la sección de la cota muestra «no disponible» hasta reconstruir.

## Cierre

- **Registro de evidencia**: rutas de los JSONL nuevos e ids de las versiones de prueba en
  `.claude/context/CURRENT_STATE.md`.
- **Limpieza**: retirar las cartillas temporales de prueba y los proyectos de QA que se creen.
  La base conserva los proyectos existentes.
- **Lo que no se hace**: commits, push o despliegues sin una orden explícita (constitución,
  Flujo de trabajo).
