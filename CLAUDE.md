# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> **La constitución prevalece.** Las reglas no negociables viven en
> `.specify/memory/constitution.md` (v1.0.0, 2026-10-02). Este archivo es una guía operativa: si
> algo aquí la contradice, rige la constitución y este archivo se corrige.

---

## Qué es este proyecto

**OICA** es una aplicación web de tesis de pregrado que optimiza el corte de barras de acero
comercial (6, 9 y 12 metros) mediante un algoritmo genético. Es un monorepo:

- `backend/`: Flask y Socket.IO (gevent), y el worker de Celery. El motor de corte vigente está en
  `backend/cutting/`, versión `secuencial-2`, con el análisis `analisis-1` de la spec 001.
- `frontend/`: Next.js 15, React 19 y Node 22.
- `config/`, `scripts/`, `docker-compose.yaml` y los `compose.*.yaml`: infraestructura.
- `services/`: copias históricas locales. **No editarlas ni borrarlas**; no se despliegan.

Ver `AGENTS.md` para la infraestructura y los `AGENTS.md` de `backend/` y `frontend/` antes de
tocar esos componentes.

Archivos de referencia:

- Documento de tesis: `docs/tesis-doc/` (Markdown, 4 capítulos) y `docs/tesis-doc/Referencias.md`
  (fichas de fuentes con su estado de verificación).
- Inferencias activas: `INFERENCIAS_TESIS.md`.
- Estado del proyecto: `.claude/context/CURRENT_STATE.md`.
- Plan de trabajo: `PLAN_TRABAJO.md`.
- Especificaciones de Spec Kit: `specs/<NNN>-<nombre>/` (spec, plan, research, data-model,
  contracts, quickstart, tasks).
- Tests manuales: `tests/data/<NNN>/ANALISIS_RESULTADOS.md`.
- Evidencia experimental: `tests/benchmarks/` (JSONL y JSON; nunca se sobrescriben).

---

## Prioridades de trabajo (en orden estricto)

1. **Funcionalidad correcta de la aplicación**: antes que la UI y antes que los documentos.
2. **Coherencia entre la app y los objetivos de la tesis**: si hay contradicción, se detiene y se
   documenta.
3. **Completar el documento de tesis**: solo después de que la app esté validada.

---

## Metodología general

Se trabaja por **bloques grandes**, registrados en `PLAN_TRABAJO.md`. Una funcionalidad nueva sigue
el flujo de Spec Kit: `/speckit-specify` → `/speckit-clarify` (si hay ambigüedad) →
`/speckit-plan` → `/speckit-tasks` → `/speckit-analyze` → `/speckit-implement`. Cada `plan.md`
debe evaluar los principios I–VI de la constitución en su «Constitution Check».

Para cada bloque:

1. Explicar el objetivo del bloque.
2. Revisar los archivos relevantes.
3. Registrar las inferencias necesarias en `INFERENCIAS_TESIS.md`.
4. Ejecutar los cambios.
5. Verificar que no se rompió nada (puertas de calidad, abajo).
6. Mostrar un resumen de lo hecho.
7. Preguntar por las inferencias críticas no resueltas.

---

## Restricciones absolutas

- **Commits, push, PR, merge y despliegues**: solo con una instrucción explícita del usuario
  **para esa ocasión**. La autorización no se extiende a otras ocasiones ni a otras ramas.
- **No borrar archivos** sin explicar por qué y qué impacto tiene. `services/` nunca se borra.
- **No cambiar la arquitectura completa** sin justificarlo explícitamente.
- **No inventar objetivos académicos** sin evidencia en el documento o en el código.
- **No justificar artificialmente** una tesis o aplicación incoherente.
- **No ocultar riesgos** técnicos ni académicos.
- Si el proyecto no tiene sentido académico, **detener la implementación y documentarlo**.
- **Disco escaso en C:**: antes de construir imágenes, instalar dependencias o generar volúmenes
  grandes de datos, avisar con una estimación de espacio y esperar aprobación. Nunca
  `docker system prune` (menos aún en la VPS compartida). Las imágenes huérfanas de OICA se retiran
  solo por ID, después de verificar que las nuevas arrancan sanas.

---

## Reglas técnicas

- El código nuevo debe encajar en la arquitectura vigente: Next.js, Flask y Socket.IO, Celery,
  PostgreSQL, Redis y Nginx. Si hay código muerto, duplicado o incoherente, marcarlo antes de
  eliminarlo.
- **Python 3.12 y Node 22.** No actualizar dependencias sin revisar compatibilidad. Una
  dependencia nueva requiere aprobación previa si obliga a reconstruir imágenes.
- **Requisitos**: la fuente canónica es `config/backend/requirements-common.txt` más
  `config/backend/constraints.txt`.
  - `config/backend/requirements.txt` añade gevent; `config/celery_worker/requirements.txt`
    añade eventlet.
  - **No copiar requisitos a `services/`.**
- **Servidores**:
  - El backend usa gevent (Socket.IO con `async_mode='gevent'`).
  - El worker corre Celery con pool **prefork** y concurrencia 1. eventlet está en sus
    requisitos, pero no es el pool en uso.
  - No mezclar las dependencias de uno en el otro: el contenedor del worker no tiene gevent.
- Backend y worker comparten el código de `backend/`: todo cambio debe considerar a ambos.
- **Motor y evidencia** (constitución, Principio III):
  - No modificar `backend/cutting/optimizer.py`, `physical.py`, `parameters.py`, ni `normalize` y
    `validate` de `domain.py`, sin aprobación, una nueva `VERSION` del motor y la repetición de
    los ensayos afectados.
  - Las métricas y los reportes (`analysis.py`, `report.py`, etc.) nunca alteran el plan.
- **Migraciones**: numeradas en `config/backend/migrations/`; nunca editar una ya aplicada.
- **Configuración sensible**: en `.env` y `.env.development` locales (hay plantillas `.example`)
  o en `/opt/oica/shared/production.env` en la VPS. **Nunca versionar secretos.**
- **UI**: antes de cambiar la interfaz, leer `docs/oica-redesign/AI-DESIGN-RULES.md` y
  `docs/oica-redesign/STATE.md`.

---

## Puertas de calidad

- **Dominio, motor, métricas o artefactos**: pruebas automatizadas de sus invariantes y la batería
  completa del backend sin fallos.
- **Cambios que puedan afectar el plan**: regresión contra la línea base de 136 ensayos y 12
  controles (`--comparar`), con 0 diferencias.
- **Frontend**: `npm run typecheck`, `npm run lint` y `npm run build` sin errores. En cambios de UI,
  sin violaciones nuevas de axe.
- **Scripts de despliegue u operación**: `python3 -m unittest discover -s tests/deployment -v`.
- **No declarar algo verificado sin haberlo ejecutado.** Si se omite una puerta, decirlo.

---

## Reglas académicas

- La aplicación debe alinearse con el título fijo (INF-014), los objetivos (Cap. 1) y la
  metodología (Cap. 3).
- Si el documento dice una cosa y la app hace otra, registrar la contradicción en
  `INFERENCIAS_TESIS.md`.
- No escribir conclusiones definitivas en el documento si la app aún no está validada.
- No asumir que la app es correcta sin pruebas reales de ejecución.
- Los resultados del Cap. 4 solo se redactan con ejecuciones reales y su evidencia en
  `tests/benchmarks/` o `tests/data/`. Una regresión confirma la línea base; no es evidencia nueva.
- **Fuentes**: toda fuente citada necesita su ficha en `docs/tesis-doc/Referencias.md`. Una fuente
  no verificada no se presenta como verificada, ni en la tesis ni en los textos de la app.
- Las cartillas 001 y 002 son de una obra colombiana confidencial: presentarlas anonimizadas.
- Las notas con `> Nota:` en el documento son tareas pendientes explícitas del autor.

---

## Manejo de inferencias

Toda suposición importante se registra en `INFERENCIAS_TESIS.md` con el formato `INF-XXX`.

Reglas:

- Antes de agregar una inferencia nueva, verificar que no exista una similar.
- Si existe una similar, consolidar o actualizar la existente; no duplicar.
- Cambiar el estado de las inferencias resueltas en la misma sesión.
- Nunca dejar una inferencia en `[PENDIENTE]` si ya fue resuelta.
- Si el usuario rechaza una inferencia, marcarla `[RECHAZADA]` y registrar la razón.

---

## Manejo de contradicciones

Si se detecta una contradicción entre el documento de tesis y la aplicación:

1. Registrarla en `.claude/diagnostics/ARCHITECTURE_WARNINGS.md` o en `ACADEMIC_RISKS.md`, según
   el tipo.
2. Crear o actualizar la inferencia correspondiente en `INFERENCIAS_TESIS.md`.
3. No resolverla sin validación del usuario si afecta los objetivos académicos.
4. Sí resolverla sin validación si es un bug técnico evidente (atributo incorrecto, etc.).

---

## Honestidad técnica y académica

- Si el código no cumple lo que la tesis dice, se documenta la brecha; no se oculta.
- Si el algoritmo genético produce resultados inválidos por un bug de dominio, se declara antes de
  presentar cualquier resultado. Un plan con desperdicio menor que una cota inferior válida es un
  error de dominio.
- Si una sección del documento está incorrecta o desactualizada, se marca explícitamente.
- Si un objetivo de la tesis no es alcanzable con la arquitectura actual, se reporta.

---

## Persistencia entre sesiones

Al iniciar una nueva sesión:

1. Leer `.claude/context/CURRENT_STATE.md` para entender el estado actual.
2. Leer `PLAN_TRABAJO.md` para entender el bloque activo.
3. Leer `INFERENCIAS_TESIS.md` para las inferencias pendientes.
4. Verificar si el diagnóstico previo sigue siendo válido leyendo los archivos clave.

Al finalizar una sesión de trabajo significativa, actualizar:

- `.claude/context/CURRENT_STATE.md`, con el estado actual real.
- `PLAN_TRABAJO.md`, marcando las tareas completadas.
- `INFERENCIAS_TESIS.md`, con el estado de las inferencias.
- `.claude/memory/HISTORICAL_CONTEXT.md`, si hubo cambios de dirección importantes.

Spec Kit guarda el puntero a la feature activa en `.specify/feature.json`, que es local e
ignorado por Git. Si falta, usar `SPECIFY_FEATURE_DIRECTORY=specs/<NNN>-<nombre>`.

---

## Agentes especializados disponibles

Ver `.claude/agents/` para agentes con responsabilidades específicas:

- `thesis-architect.md`: coherencia entre tesis y app.
- `application-debugger.md`: bugs y correcciones técnicas.
- `academic-reviewer.md`: calidad académica del documento.
- `implementation-planner.md`: planificación de bloques de trabajo.
- `inference-manager.md`: gestión del sistema de inferencias.
- `context-manager.md`: persistencia de contexto entre sesiones.

---

## Compatibilidad con otros agentes AI

Este repositorio está configurado para **Claude Code** (este archivo) y para **OpenAI Codex**
(`AGENTS.md`). Ambos comparten la constitución y el estado persistente:

- `.specify/memory/constitution.md`: reglas no negociables.
- `.claude/context/CURRENT_STATE.md`: estado vivo del proyecto.
- `.claude/memory/HISTORICAL_CONTEXT.md`: historial de decisiones.
- `INFERENCIAS_TESIS.md`: inferencias activas.
- `PLAN_TRABAJO.md`: plan de trabajo.

Si se actualiza una regla en `CLAUDE.md`, revisar si también aplica a `AGENTS.md` y viceversa.
Ninguno de los dos puede contradecir la constitución.

---

## Estado de testing manual

Los tests manuales viven en `tests/data/<NNN>/`. Cada carpeta contiene:

- El archivo de entrada (`NNN-nombre.xlsx`).
- `ANALISIS_RESULTADOS.md`, con el análisis completo: coherencia entre artefactos, bugs
  encontrados, verificación matemática y observaciones sobre el AG.

**Leer el análisis del test más reciente antes de tocar `backend/cutting/report.py` o
`backend/celery_worker.py`.**

### Bugs registrados

| ID | Archivo | Estado |
|----|---------|--------|
| BUG-001 | `utils/artifact_generator.py` (motor histórico) | ✅ Corregido 2026-05-06 |
| BUG-002 | `celery_worker.py` histórico: `cantidad_requerida` = número de cortes por barra | Motor histórico; no aplica a `secuencial-2` (el Excel vigente usa Barras/Cortes/Patrones) |
| BUG-003 | `genetic_algorithm/population.py`: expansión de cantidades | ✅ Corregido 2026-05-13 |
| BUG-004 | `genetic_algorithm/optimal_analyzer.py`: búsqueda O(N^k) | ✅ Corregido 2026-05-13 |
| BUG-005 | `utils/artifact_generator.py`: PNG sin límite | ✅ Corregido 2026-05-13 |
| BUG-006 | Perfil `profundo` limitado por tiempo en el motor histórico | Motor histórico; `secuencial-2` para por generaciones y estancamiento |

El motor histórico (`backend/genetic_algorithm/`) se conserva con sus pruebas, pero el worker
usa `backend/cutting/`. No hay bugs abiertos conocidos en el motor vigente.

### Hallazgos de usabilidad

| ID | Descripción | Estado |
|----|-------------|--------|
| MEJORA-001 | PDF y PNG sin agrupación por diámetro | Atendida en la spec 001: patrones identificados `P-<diámetro>-<nnn>` y resumen por diámetro |

### Cobertura de evidencia vigente

| Evidencia | Contenido |
|-----------|-----------|
| `tests/benchmarks/2026-09-13-fisico-matriz-final.jsonl` | 136 ensayos de 001 y 002: 4 escenarios, FFD/BFD y AG con 3 perfiles × 5 semillas |
| `tests/benchmarks/2026-09-13-fisico-control-*.jsonl` | 12 controles (cizalla y fin de etapa) |
| `tests/benchmarks/2026-10-02-regresion-analisis-1.jsonl` | Regresión con `analisis-1`: 0 diferencias en 148 registros |
| `tests/benchmarks/2026-10-02-cota-ensayos.jsonl` | Cota por patrones de los 148 registros (todos con desperdicio ≥ cota) |
| `tests/benchmarks/2026-10-02-sc007-comparacion.json` | Tiempo con y sin la capa de análisis (+8,8 %) |

---

## Comandos rápidos

```bash
# Levantar el stack (respeta OICA_PROXY_MODE de .env; no construye)
bash scripts/compose.sh up -d --wait

# Construir imágenes: SOLO con aprobación y estimación de espacio en C:
bash scripts/compose.sh build backend celery_worker frontend

# Logs
docker compose logs -f backend
docker compose logs -f celery_worker

# Pruebas backend con el código del árbol de trabajo (contenedor del backend: tiene gevent)
python3 scripts/check_cutting_container.py --all-tests --container oica-validation-backend-1

# Regresión contra la línea base (148 registros; debe dar 0 diferencias)
python3 scripts/check_cutting_container.py \
  --comparar tests/benchmarks/2026-09-13-fisico-matriz-final.jsonl \
  --comparar tests/benchmarks/2026-09-13-fisico-control-cizalla.jsonl \
  --comparar tests/benchmarks/2026-09-13-fisico-control-fin-etapa.jsonl \
  --output tests/benchmarks/<fecha>-regresion-<motivo>.jsonl

# Cota de los ensayos registrados (requiere scipy en la imagen)
python3 scripts/cota_ensayos.py --output tests/benchmarks/<fecha>-cota-ensayos.jsonl

# Auditoría de una versión persistida
docker compose exec -T backend python - ID < scripts/verify_sequential_result.py

# Frontend
(cd frontend && npm run typecheck && npm run lint && npm run build)

# Reset de base de datos: DESTRUCTIVO, borra volúmenes. Solo con confirmación explícita y respaldo.
# docker compose down -v
```

Idioma del proyecto: **español** (documentación, comentarios, interfaz, esquema de base de datos y
commits).
