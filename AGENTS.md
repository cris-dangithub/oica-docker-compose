# AGENTS.md

> Leer primero «Cómo iniciar una sesión» antes de hacer cambios.
>
> **La constitución prevalece.** Las reglas no negociables están en
> `.specify/memory/constitution.md` (v1.0.0, 2026-10-02). Este archivo y `CLAUDE.md` son guías
> operativas: ante un conflicto rige la constitución, y la guía se corrige.

## Repositorio

Monorepo OICA (optimizador de cortes de acero):

- `backend/`: Flask y Celery. El motor vigente está en `backend/cutting/`: `secuencial-2` más el
  análisis `analisis-1`.
- `frontend/`: Next.js.
- Infraestructura Docker y GitHub Actions.

La rama local de entrega es `production`.

Las carpetas `services/` son copias históricas locales y no se usan en el despliegue. **No editarlas ni borrarlas**: conservan los cambios anteriores y sus repositorios Git originales.

## Arranque y verificaciones

```bash
bash scripts/compose.sh up -d --wait      # levantar (respeta OICA_PROXY_MODE); no construye
./init.sh                                 # build + up -d --wait, no destructivo (requiere aprobación por disco)
./scripts/setup-dev.sh                    # preparación Ubuntu/Debian, Python 3.12/Node 22
./scripts/dev.sh                          # desarrollo nativo, Ctrl+C cierra la sesión
(cd frontend && npm run typecheck && npm run lint && npm run build)
python3 -m unittest discover -s tests/deployment -v
python3 scripts/check_cutting_container.py --all-tests --container oica-validation-backend-1
```

Las pruebas del backend van en el contenedor del **backend**: el del worker no tiene gevent. La
regresión del motor (`--comparar` contra la línea base de 148 registros) y otros comandos están en
`CLAUDE.md`.

Docker mantiene seis servicios: Nginx, frontend, backend, celery_worker, db (PostgreSQL 15), redis (Redis 7), más el servicio temporal `migrate`. Solo Nginx publica puertos. HTTP usa `/api/`, WebSocket `/socket.io/`. Nginx limita cargas y reprocesos a 6 por minuto, con ráfaga de 5; al superarlo responde 429. Producción añade HTTPS para `oica.cris-munoz.me` mediante `compose.production.yaml`.

## Restricciones técnicas

- **Python 3.12**, Node **22**. No subir versiones mayores sin validar dependencias.
- **Requisitos**:
  - Canónicos: `config/backend/requirements-common.txt` más `config/backend/constraints.txt`.
  - El backend añade gevent; el worker añade eventlet, aunque corre con pool prefork.
  - No copiar requisitos a `services/`.
- Configuración sensible en `.env`/`.env.development` locales o `/opt/oica/shared/production.env` en VPS; nunca versionar secretos.
- Migraciones numeradas en `config/backend/migrations/`, ejecutadas por `scripts/migrate.py`. No modificar una migración aplicada: agregar otra. `init.sql` es referencia del esquema inicial; no se monta automáticamente en PostgreSQL.
- Backend y worker comparten `UPLOAD_PATH`. Los volúmenes persisten entre actualizaciones normales.
- **Disco escaso en C:**:
  - Antes de construir imágenes, instalar dependencias o generar volúmenes grandes de datos,
    avisar con una estimación de espacio y esperar aprobación.
  - Nunca `docker system prune`, menos aún en la VPS compartida.
  - Las imágenes huérfanas de OICA se retiran solo por ID, tras verificar que las nuevas arrancan
    sanas.
- Reset solo desde la operación explícita de OICA con confirmación y respaldo configurable.
- **Motor**: `optimizer.py`, `physical.py`, `parameters.py`, y `normalize`/`validate` de
  `domain.py`, no se modifican sin aprobación, nueva `VERSION` del motor y repetición de los
  ensayos afectados. Las métricas y los reportes nunca alteran el plan.
- Ver `docs/DEPLOYMENT.md` para SSH, GHCR, certificados, rollback y restauración.
- Leer los AGENTS.md de backend/frontend antes de modificar esos componentes.

## Idioma

Documentación, comentarios, interfaz y commits en español.

## Sistema visual

Antes de modificar UI o estilos del frontend, leer
`docs/oica-redesign/AI-DESIGN-RULES.md` y el estado vigente en
`docs/oica-redesign/STATE.md`.

---

## Contexto académico

Este repositorio es el trabajo de tesis de pregrado de su autor. La aplicación y el documento de tesis se desarrollan en paralelo. Esto tiene consecuencias importantes para cualquier agente que trabaje aquí:

- La aplicación debe ser **coherente con los objetivos del documento de tesis** (`docs/tesis-doc/`) y con el título fijo (INF-014).
- No toda decisión técnica es libre — algunas están condicionadas por los objetivos académicos del Cap. 1.
- Los resultados que genere la app serán presentados en el Cap. 4. Si los resultados son inválidos por un bug de dominio, la tesis entera queda comprometida.
- Toda fuente citada necesita su ficha en `docs/tesis-doc/Referencias.md`. Una fuente no verificada no se presenta como verificada.
- Procedencia de las cartillas (INF-017):
  - 002 es de un proyecto real en Colombia y se obtuvo de un proveedor de acero. Es confidencial:
    presentarla anonimizada, sin nombrar al proveedor.
  - 001 es un ejercicio del curso Construcción de edificaciones (REF-CARTILLA-001).
  - 003 y 004 son sintéticas: no presentarlas como datos de obra.

---

## Cómo iniciar una sesión

Antes de hacer cualquier cambio, leer en este orden:

1. **`.specify/memory/constitution.md`** — Reglas no negociables.
2. **`.claude/context/CURRENT_STATE.md`** — Estado global, bloque activo, preguntas pendientes del usuario.
3. **`PLAN_TRABAJO.md`** — Bloques de trabajo priorizados con dependencias y criterios de finalización.
4. **`INFERENCIAS_TESIS.md`** (índice rápido) — Inferencias `[PENDIENTE]` de prioridad Alta que bloquean trabajo.

Si el estado registrado no coincide con el código real (spot check), actualizar `.claude/context/CURRENT_STATE.md`.

Presentar al usuario un resumen: qué se hizo antes, qué está pendiente, cuál es la pregunta crítica sin resolver.

---

## Restricciones críticas

- **Commits, push, PR, merge y despliegues**: solo con una instrucción explícita del usuario **para esa ocasión**; la autorización no se extiende a otras ocasiones ni a otras ramas.
- **No borrar archivos** sin explicar el impacto.
- **No cambiar la arquitectura completa** sin justificación.
- **No inventar objetivos académicos** sin evidencia en `docs/tesis-doc/`.
- **No justificar artificialmente** incoherencias entre el documento y la app.
- **No ocultar riesgos técnicos o académicos** — registrarlos en `.claude/diagnostics/`.
- Si la app produce resultados físicamente inválidos (ej: mezclar piezas de diferente diámetro en una barra, o un desperdicio menor que una cota inferior válida), reportarlo antes de avanzar.

---

## Metodología de trabajo

Se trabaja por **bloques grandes** definidos en `PLAN_TRABAJO.md`. Una funcionalidad nueva sigue el flujo de Spec Kit (`specs/<NNN>-<nombre>/`): specify → clarify → plan (con Constitution Check) → tasks → analyze → implement. Para cada bloque:

1. Explicar objetivo del bloque.
2. Revisar archivos relevantes.
3. Registrar inferencias en `INFERENCIAS_TESIS.md` (usar `.claude/templates/INFERENCE_TEMPLATE.md`).
4. Ejecutar cambios.
5. Verificar que no se rompió nada: pruebas del backend, regresión del motor si puede cambiar el plan, typecheck/lint/build del frontend y axe en cambios de UI.
6. Mostrar resumen de lo hecho.
7. Preguntar sobre inferencias críticas `[PENDIENTE]` de Alta prioridad.

**Prioridades (en orden estricto):**
1. Funcionalidad correcta de la app.
2. Coherencia entre app y objetivos de la tesis.
3. Completar el documento de tesis (solo después de validar la app).

---

## Tests manuales

Los tests manuales viven en `tests/data/<NNN>/`. Cada carpeta contiene:
- El XLSX de entrada.
- `ANALISIS_RESULTADOS.md` con análisis de coherencia entre artefactos (Excel/PDF/PNG), bugs encontrados y verificación matemática.

**Leer `tests/data/<NNN>/ANALISIS_RESULTADOS.md` del test más reciente antes de modificar `backend/cutting/report.py` o `backend/celery_worker.py`.**

La evidencia experimental vigente (matriz de 136 ensayos, 12 controles, regresión, cota y tiempos) está en `tests/benchmarks/`; nunca se sobrescribe.

---

## Bugs registrados (estado 2026-10-02)

El worker usa el motor `backend/cutting/` (`secuencial-2`). El motor histórico `backend/genetic_algorithm/` se conserva con sus pruebas. No hay bugs abiertos conocidos en el motor vigente.

| ID | Archivo | Descripción | Estado |
|----|---------|-------------|--------|
| BUG-001 | `utils/artifact_generator.py` (histórico) | Eficiencia mezclaba unidades kg/m | ✅ Corregido 2026-05-06 |
| BUG-002 | `celery_worker.py` (histórico) | `cantidad_requerida` = número de cortes por barra | Motor histórico; no aplica a `secuencial-2` (Excel con Barras, Cortes y Patrones) |
| BUG-003 | `genetic_algorithm/population.py` | Expansión de cantidades a piezas individuales | ✅ Corregido 2026-05-13 |
| BUG-004 | `genetic_algorithm/optimal_analyzer.py` | Búsqueda exhaustiva O(N^k) | ✅ Corregido 2026-05-13 |
| BUG-005 | `utils/artifact_generator.py` (histórico) | PNG proporcional a miles de barras | ✅ Corregido 2026-05-13 |
| BUG-006 | `genetic_algorithm/engine.py` (histórico) | Perfil `profundo` limitado por tiempo | Motor histórico; `secuencial-2` se detiene por generaciones y estancamiento |

Ver detalle histórico en `tests/data/001/ANALISIS_RESULTADOS.md` y `tests/data/002/ANALISIS_RESULTADOS.md` (la sección 12 de 002 cubre la spec 001).

---

## Sistema de inferencias

Toda suposición importante se registra en `INFERENCIAS_TESIS.md`. Reglas:

- Antes de crear una inferencia, verificar que no exista una similar.
- No crear más de 2 inferencias por bloque sin verificar duplicados.
- Actualizar el estado de inferencias resueltas en la misma sesión.
- Usar la plantilla en `.claude/templates/INFERENCE_TEMPLATE.md`.

---

## Al finalizar una sesión

Actualizar:
- `.claude/context/CURRENT_STATE.md` — con estado real post-sesión.
- `PLAN_TRABAJO.md` — marcar tareas completadas.
- `INFERENCIAS_TESIS.md` — actualizar estados de inferencias resueltas.
- `.claude/memory/HISTORICAL_CONTEXT.md` — si hubo cambios de dirección importantes.
