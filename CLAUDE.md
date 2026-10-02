# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Qué es este proyecto

**OICA** es una aplicación web de tesis de pregrado que optimiza el corte de barras de acero comercial (6, 9 y 12 metros) mediante algoritmos genéticos. El repositorio contiene la orquestación Docker y el documento de tesis. El código real vive en repos separados clonados en `services/` (gitignored). Ver `AGENTS.md` para detalles de infraestructura.

Documento de tesis: `docs/tesis-doc/` (Markdown, 4 capítulos).
Inferencias activas: `INFERENCIAS_TESIS.md`.
Estado del proyecto: `.claude/context/CURRENT_STATE.md`.
Plan de trabajo: `PLAN_TRABAJO.md`.
Tests manuales: `tests/data/<NNN>/ANALISIS_RESULTADOS.md` — cada carpeta numerada contiene el XLSX de entrada y el análisis completo de los artefactos generados (Excel, PDF, PNG), incluyendo bugs encontrados y verificación matemática.

---

## Prioridades de trabajo (en orden estricto)

1. **Funcionalidad correcta de la aplicación** — antes que UI, antes que docs.
2. **Coherencia entre la app y los objetivos de la tesis** — si hay contradicción, se detiene y se documenta.
3. **Completar el documento de tesis** — solo después de que la app esté validada.

---

## Metodología general

Se trabaja por **bloques grandes**. Para cada bloque:

1. Explicar objetivo del bloque.
2. Revisar archivos relevantes.
3. Registrar inferencias necesarias en `INFERENCIAS_TESIS.md`.
4. Ejecutar cambios.
5. Verificar que no se rompió nada.
6. Mostrar resumen de lo hecho.
7. Hacer preguntas sobre inferencias críticas no resueltas.

---

## Restricciones absolutas

- **No hacer commits** — nunca, en ninguna sesión.
- **No borrar archivos** sin explicar por qué y qué impacto tiene.
- **No cambiar arquitectura completa** sin justificarlo explícitamente.
- **No inventar objetivos académicos** sin evidencia en el documento o código.
- **No justificar artificialmente** una tesis o aplicación incoherente.
- **No ocultar riesgos** técnicos o académicos.
- Si el proyecto no tiene sentido académico, **detener implementación y documentarlo**.

---

## Reglas técnicas

- Código nuevo debe ser coherente con la arquitectura existente (Flask, Celery, Next.js).
- Si hay código muerto, duplicado o incoherente, marcarlo antes de eliminarlo.
- Python: usar Python 3.12. No actualizar dependencias sin revisar compatibilidad.
- `requirements.txt` tiene dos fuentes de verdad: `config/backend/` y `config/celery_worker/`. Sincronizar antes de build.
- Backend usa `gevent`; worker usa `eventlet`. No mezclar.
- Todo cambio en backend debe considerar si el celery worker también requiere el mismo cambio (comparten código fuente en `services/backend/`).
- No agregar `.env` — las vars de entorno están inline en `docker-compose.yaml`.

---

## Reglas académicas

- La aplicación debe alinearse con el título, los objetivos (Cap. 1) y la metodología (Cap. 3).
- Si el documento dice una cosa y la app hace otra, registrar la contradicción en `INFERENCIAS_TESIS.md`.
- No escribir conclusiones definitivas en el documento si la app aún no está validada.
- No asumir que la app es correcta sin pruebas reales de ejecución.
- Los resultados del Cap. 4 solo se redactan después de pruebas reales con las cartillas de prueba.
- Las notas con `> Nota:` en el documento son tareas pendientes explícitas del autor.

---

## Manejo de inferencias

Toda suposición importante se registra en `INFERENCIAS_TESIS.md` usando el formato de `INF-XXX`.

Reglas:
- Antes de agregar una inferencia nueva, verificar que no exista una similar.
- Si existe una similar, consolidar o actualizar la existente, no duplicar.
- Cambiar el estado de inferencias resueltas en la misma sesión.
- Nunca dejar una inferencia en estado `[PENDIENTE]` si ya fue resuelta.
- Si el usuario rechaza una inferencia, marcarla `[RECHAZADA]` y registrar la razón.

---

## Manejo de contradicciones

Si se detecta una contradicción entre el documento de tesis y la aplicación:

1. Registrar en `.claude/diagnostics/ARCHITECTURE_WARNINGS.md` o `ACADEMIC_RISKS.md` según el tipo.
2. Crear o actualizar la inferencia correspondiente en `INFERENCIAS_TESIS.md`.
3. No resolver la contradicción sin validación del usuario si afecta objetivos académicos.
4. Sí resolver sin validación si es un bug técnico obvio (atributo incorrecto, etc.).

---

## Honestidad técnica y académica

- Si el código no cumple lo que la tesis dice, se documenta la brecha, no se oculta.
- Si el algoritmo genético produce resultados inválidos por un bug de dominio, se declara antes de presentar cualquier resultado.
- Si una sección del documento está incorrecta o desactualizada, se marca explícitamente.
- Si un objetivo de la tesis no es alcanzable con la arquitectura actual, se reporta.

---

## Persistencia entre sesiones

Al iniciar una nueva sesión:

1. Leer `.claude/context/CURRENT_STATE.md` para entender el estado actual.
2. Leer `PLAN_TRABAJO.md` para entender el bloque activo.
3. Leer `INFERENCIAS_TESIS.md` para inferencias pendientes.
4. Verificar si el diagnóstico previo sigue siendo válido leyendo los archivos clave.

Al finalizar una sesión de trabajo significativa, actualizar:
- `.claude/context/CURRENT_STATE.md` — con el estado actual real.
- `PLAN_TRABAJO.md` — marcar tareas completadas.
- `INFERENCIAS_TESIS.md` — actualizar estados de inferencias.

---

## Agentes especializados disponibles

Ver `.claude/agents/` para agentes con responsabilidades específicas:

- `thesis-architect.md` — coherencia entre tesis y app
- `application-debugger.md` — bugs y correcciones técnicas
- `academic-reviewer.md` — calidad académica del documento
- `implementation-planner.md` — planificación de bloques de trabajo
- `inference-manager.md` — gestión del sistema de inferencias
- `context-manager.md` — persistencia de contexto entre sesiones

---

## Compatibilidad con otros agentes AI

Este repositorio está configurado para funcionar con **Claude Code** (este archivo) y con **OpenAI Codex** (`AGENTS.md`).

Ambos comparten el mismo sistema de estado persistente en `.claude/`:
- `.claude/context/CURRENT_STATE.md` — estado vivo del proyecto
- `.claude/memory/HISTORICAL_CONTEXT.md` — historial de decisiones
- `INFERENCIAS_TESIS.md` — inferencias activas
- `PLAN_TRABAJO.md` — plan de trabajo

Las restricciones, metodología y convenciones son idénticas en ambos archivos. Si se actualiza una regla en `CLAUDE.md`, revisar si también aplica a `AGENTS.md` y viceversa. El estado persistente es compartido — cualquier agente que trabaje aquí debe leer y actualizar los mismos archivos de contexto.

---

## Estado de testing manual

Los tests manuales viven en `tests/data/<NNN>/`. Cada carpeta contiene:
- El XLSX de entrada (`NNN-nombre.xlsx`)
- `ANALISIS_RESULTADOS.md` con análisis completo: coherencia entre artefactos, bugs encontrados, verificación matemática, y observaciones sobre el AG.

**Leer el análisis del test más reciente antes de tocar `artifact_generator.py` o `celery_worker.py`.**

### Bugs confirmados en testing (pendientes de corrección)

| ID | Archivo | Línea | Descripción | Severidad |
|----|---------|-------|-------------|-----------|
| ~~BUG-001~~ | ~~`utils/artifact_generator.py`~~ | ~~100~~ | ~~Eficiencia mezclaba unidades kg/m~~ | ✅ Corregido 2026-05-06 |
| BUG-002 | `celery_worker.py` | 492 | Columna `cantidad_requerida` en Excel de resultados contiene `len(cortes)` (número de cortes por barra), no la demanda original. Semántica confusa para el ingeniero. | MEDIA |
| ~~BUG-003~~ | ~~`genetic_algorithm/population.py`~~ | ~~41/148/259~~ | ~~FFD/BFD/Aleatorio expandían cantidades a ítems individuales en loops de N piezas, haciendo el AG inviable para datasets reales. Corregido con representación agrupada O(R×B).~~ | ✅ Corregido 2026-05-13 |
| ~~BUG-004~~ | ~~`genetic_algorithm/optimal_analyzer.py`~~ | ~~58~~ | ~~Búsqueda exhaustiva O(N^k) en `calcular_solucion_optima_homogenea`. 2774 piezas × 3 longitudes de barra = ~3,560M combinaciones → cuelgue de 8+ horas. Corregido: guard >500k → fallback greedy.~~ | ✅ Corregido 2026-05-13 |

### Hallazgos de usabilidad (mejoras deseables)

| ID | Descripción |
|----|-------------|
| MEJORA-001 | PDF y PNG no muestran agrupación por diámetro. El Excel sí tiene columna `diametro`, pero el PDF lista todas las barras en secuencia sin indicar #5/#4/#3. |

### Cobertura de tests actuales

| Test | Dataset | Perfiles probados | Diámetros | Resultado |
|------|---------|-------------------|-----------|-----------|
| 001 | 16 piezas vigas | rapido/balanceado/profundo | #3, #4, #5 | Todos convergen — dataset demasiado pequeño para diferenciar perfiles |
| 002 | 137 órdenes, 67.443 piezas | En progreso | #3, #4, #5, #6, #7 | Pendiente — requería BUG-003 corregido primero |

---

## Comandos rápidos de infraestructura

```bash
# Levantar todo
docker compose up -d --build

# Logs
docker compose logs -f backend
docker compose logs -f celery_worker

# Reset base de datos (borra todo)
docker compose down -v && docker compose up -d --build

# Sincronizar requirements antes de build
cp config/backend/requirements.txt services/backend/requirements.txt

# Reconstruir solo backend y worker
docker compose build backend celery_worker
```

Idioma del proyecto: **Español** (docs, comentarios, commits, DB schema).
