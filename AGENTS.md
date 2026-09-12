# AGENTS.md

> Leer primero «Cómo iniciar una sesión» antes de hacer cambios.

## Repositorio

Monorepo OICA (optimizador de cortes de acero): `backend/` (Flask/Celery), `frontend/` (Next.js) e infraestructura Docker/GitHub Actions. La rama local de entrega es `production`.

Las carpetas `services/` son copias históricas locales y no se usan en el despliegue. **No editarlas ni borrarlas**: conservan los cambios anteriores y sus repositorios Git originales.

## Arranque y verificaciones

```bash
docker compose up                         # http://localhost, primera instalación vacía
./init.sh                                 # build + up -d --wait, no destructivo
./scripts/setup-dev.sh                    # preparación Ubuntu/Debian, Python 3.12/Node 22
./scripts/dev.sh                          # desarrollo nativo, Ctrl+C cierra la sesión
(cd frontend && npm run typecheck && npm run lint && npm run build)
python3 -m unittest discover -s tests/deployment -v
```

Docker mantiene seis servicios: Nginx, frontend, backend, celery_worker, db (PostgreSQL 15), redis (Redis 7), más el servicio temporal `migrate`. Solo Nginx publica puertos. HTTP usa `/api/`, WebSocket `/socket.io/`. Producción añade HTTPS para `oica.cris-munoz.me` mediante `compose.production.yaml`.

## Restricciones técnicas

- **Python 3.12**, Node **22**. No subir versiones mayores sin validar dependencias.
- Requisitos canónicos en `config/backend/` y `config/celery_worker/`, con archivo común y constraints. No copiar requisitos a `services/`.
- Configuración sensible en `.env`/`.env.development` locales o `/opt/oica/shared/production.env` en VPS; nunca versionar secretos.
- Migraciones numeradas en `config/backend/migrations/`, ejecutadas por `scripts/migrate.py`. No modificar una migración aplicada: agregar otra. `init.sql` es referencia del esquema inicial; no se monta automáticamente en PostgreSQL.
- Backend y worker comparten `UPLOAD_PATH`. Los volúmenes persisten entre actualizaciones normales.
- Nunca usar `docker system prune` en la VPS compartida. Reset solo desde la operación explícita de OICA con confirmación y respaldo configurable.
- Ver `docs/DEPLOYMENT.md` para SSH, GHCR, certificados, rollback y restauración.
- Leer los AGENTS.md de backend/frontend antes de modificar esos componentes.

## Idioma

Documentación, comentarios, interfaz y commits en español.

---

## Contexto académico

Este repositorio es el trabajo de tesis de pregrado de su autor. La aplicación y el documento de tesis se desarrollan en paralelo. Esto tiene consecuencias importantes para cualquier agente que trabaje aquí:

- La aplicación debe ser **coherente con los objetivos del documento de tesis** (`docs/tesis-doc/`).
- No toda decisión técnica es libre — algunas están condicionadas por los objetivos académicos del Cap. 1.
- Los resultados que genere la app serán presentados en el Cap. 4. Si los resultados son inválidos por un bug de dominio, la tesis entera queda comprometida.
- El documento de tesis tiene secciones desactualizadas que describen arquitecturas ya descartadas. No tomarlas como referencia técnica.

---

## Cómo iniciar una sesión

Antes de hacer cualquier cambio, leer en este orden:

1. **`.claude/context/CURRENT_STATE.md`** — Estado global, bloque activo, preguntas pendientes del usuario.
2. **`PLAN_TRABAJO.md`** — Bloques de trabajo priorizados con dependencias y criterios de finalización.
3. **`INFERENCIAS_TESIS.md`** (índice rápido) — Inferencias `[PENDIENTE]` de prioridad Alta que bloquean trabajo.

Si el estado registrado no coincide con el código real (spot check), actualizar `.claude/context/CURRENT_STATE.md`.

Presentar al usuario un resumen: qué se hizo antes, qué está pendiente, cuál es la pregunta crítica sin resolver.

---

## Restricciones críticas

- **No hacer commits** — nunca, en ninguna sesión, sin instrucción explícita del usuario.
- **No borrar archivos** sin explicar el impacto.
- **No cambiar la arquitectura completa** sin justificación.
- **No inventar objetivos académicos** sin evidencia en `docs/tesis-doc/`.
- **No justificar artificialmente** incoherencias entre el documento y la app.
- **No ocultar riesgos técnicos o académicos** — registrarlos en `.claude/diagnostics/`.
- Si la app produce resultados físicamente inválidos (ej: mezclar piezas de diferente diámetro en una barra), reportarlo antes de avanzar.

---

## Metodología de trabajo

Se trabaja por **bloques grandes** definidos en `PLAN_TRABAJO.md`. Para cada bloque:

1. Explicar objetivo del bloque.
2. Revisar archivos relevantes.
3. Registrar inferencias en `INFERENCIAS_TESIS.md` (usar `.claude/templates/INFERENCE_TEMPLATE.md`).
4. Ejecutar cambios.
5. Verificar que no se rompió nada.
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

**Leer `tests/data/<NNN>/ANALISIS_RESULTADOS.md` del test más reciente antes de modificar `artifact_generator.py` o `celery_worker.py`.**

---

## Bugs confirmados en testing (estado 2026-05-13)

Bugs de `server.py` (Bloque A) y del AG (Bloque B) ya fueron **corregidos**. Los bugs activos son:

| ID | Archivo | Línea | Descripción | Severidad |
|----|---------|-------|-------------|-----------|
| ~~BUG-001~~ | ~~`utils/artifact_generator.py`~~ | ~~100~~ | ~~Eficiencia mezclaba unidades kg/m~~ | ✅ Corregido 2026-05-06 |
| BUG-002 | `celery_worker.py` | 492 | `cantidad_requerida` en Excel de salida = `len(cortes)` por barra, no la demanda original del pedido. Semántica confusa. | MEDIA |
| ~~BUG-003~~ | ~~`genetic_algorithm/population.py`~~ | ~~41/148/259~~ | ~~FFD/BFD/Aleatorio expandían cantidades a ítems individuales (loop de N piezas), tornando el AG inviable para datasets reales (>1000 piezas). Corregido: representación agrupada, O(R×B) en lugar de O(N×B).~~ | ✅ Corregido 2026-05-13 |
| ~~BUG-004~~ | ~~`genetic_algorithm/optimal_analyzer.py`~~ | ~~58~~ | ~~`calcular_solucion_optima_homogenea` usaba búsqueda exhaustiva O(N^k) sin límite. Para 2774 piezas con 3 longitudes de barra: ~3,560M combinaciones → cuelgue de 8+ horas. Corregido: guard de espacio de búsqueda (>500k → fallback greedy por mejor barra).~~ | ✅ Corregido 2026-05-13 |
| ~~BUG-005~~ | ~~`utils/artifact_generator.py`~~ | ~~264~~ | ~~`generar_imagen_grafica` calculaba figsize proporcional a len(barras) sin límite. Para ~21,000 barras: figura de 16×10,500 pulgadas a 200 DPI → buffer de ~26 GB → MemoryError. Corregido: cap en 300 barras (muestra), alto máx 150 pulgadas, DPI reducido a 100 en muestras.~~ | ✅ Corregido 2026-05-13 |
| BUG-006 | `celery_worker.py` + `genetic_algorithm/engine.py` | 307/392 | Perfil `profundo` no sobreescribe `tiempo_limite_segundos`. El engine aplica 300s/grupo por defecto. Con 100 individuos, cada gen de grupos grandes tarda ~100s → solo 6 gen para #6 vs 45 gen de `balanceado`. Profundo no es más exhaustivo que balanceado para datasets reales. | MEDIA |

Ver detalle completo en `tests/data/001/ANALISIS_RESULTADOS.md` y `tests/data/002/ANALISIS_RESULTADOS.md`.

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
