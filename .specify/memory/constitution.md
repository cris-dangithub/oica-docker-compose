<!--
Sync Impact Report
==================
Versión: plantilla sin llenar → 1.0.0 (primera ratificación; MAJOR inicial)

Principios definidos (antes: marcadores de plantilla):
- [PRINCIPLE_1_NAME] → I. Validez física y de dominio (NO NEGOCIABLE)
- [PRINCIPLE_2_NAME] → II. Coherencia título–objetivos–aplicación–documento
- [PRINCIPLE_3_NAME] → III. Evidencia reproducible y motor versionado
- [PRINCIPLE_4_NAME] → IV. El algoritmo genético optimiza; las demás técnicas miden
- [PRINCIPLE_5_NAME] → V. Honestidad técnica y académica con trazabilidad
- Nuevo: VI. Simplicidad y compatibilidad con lo existente

Secciones añadidas:
- Restricciones técnicas y operativas (antes [SECTION_2_NAME])
- Flujo de trabajo y puertas de calidad (antes [SECTION_3_NAME])
- Governance completada

Secciones eliminadas: ninguna.

Decisiones cerradas con el usuario (2026-10-02):
- Commits, push, PR, merge y despliegue: solo con orden explícita para esa ocasión.
- Pruebas: obligatorias en dominio, motor, métricas y artefactos, con puerta de regresión;
  sin TDD estricto.
- Cambios que alteren el plan: permitidos con aprobación, nueva VERSION del motor y
  re-ejecución de los ensayos afectados.
- Precedencia: la constitución prevalece sobre AGENTS.md y CLAUDE.md.

Plantillas dependientes:
- .specify/templates/plan-template.md ✅ sin cambios (lee los gates de este archivo en tiempo
  de ejecución)
- .specify/templates/spec-template.md ✅ sin cambios
- .specify/templates/tasks-template.md ✅ sin cambios
- .specify/templates/checklist-template.md ✅ sin cambios

TODO de seguimiento (fuera del alcance de este comando):
- CLAUDE.md desactualizado frente a esta constitución: dice que el código vive en services/,
  que el worker usa eventlet (backend/AGENTS.md dice Celery prefork), la tabla de bugs usa
  rutas antiguas y fija «no hacer commits — nunca». Alinear con el Principio VI, la sección
  de flujo y la decisión sobre commits.
- specs/001-alineacion-titulo-tesis/spec.md (Assumptions) y su checklist dicen que la
  constitución es una plantilla vacía: actualizar esa nota.
- Registrar la ratificación en .claude/memory/HISTORICAL_CONTEXT.md.
-->

# OICA Constitution

## Core Principles

### I. Validez física y de dominio (NO NEGOCIABLE)

Ningún plan de corte se presenta como válido si viola la física del problema.

- Una pieza MUST cortarse solo de una barra de su mismo diámetro.
- El plan MUST satisfacer exactamente la demanda de la cartilla, sin piezas faltantes ni
  sobrantes. MUST respetar la capacidad de cada barra, incluida la pérdida por corte; el orden
  de las etapas; y las cantidades disponibles del inventario adicional.
- Cada resultado MUST pasar el validador independiente (código separado del optimizador) que
  comprueba demanda, diámetro, capacidad y etapas. Si falla, el resultado MUST NOT mostrarse
  como válido y MUST exponer el motivo.
- Las métricas de desperdicio y aprovechamiento MUST calcularse por masa, según la definición
  vigente (INF-012). Aprovechamiento y desperdicio MUST sumar 100 %.
- Un desperdicio menor que una cota inferior válida MUST tratarse como error de dominio
  visible, nunca como un logro.

**Razón**: si la aplicación produce un resultado físicamente imposible, se invalida toda la
evidencia del Cap. 4 y, con ella, la tesis.

### II. Coherencia título–objetivos–aplicación–documento

El título de la tesis es fijo palabra por palabra (decisión del autor, 2026-10-02). Cada término
del título MUST tener respaldo verificable en la aplicación o en el documento, y al menos una
fuente con estado de verificación declarado.

- Los objetivos los aporta el autor. Un agente MUST NOT inventar, añadir ni reformular
  objetivos académicos sin evidencia en `docs/tesis-doc/` y sin aprobación del autor.
- Toda contradicción entre documento y aplicación MUST registrarse en `INFERENCIAS_TESIS.md` y
  en `.claude/diagnostics/` (`ACADEMIC_RISKS.md` o `ARCHITECTURE_WARNINGS.md`).
- Si una contradicción afecta los objetivos académicos, MUST NOT resolverse sin validación del
  usuario. Un bug técnico evidente (atributo incorrecto, unidad errónea) sí puede corregirse
  directamente, y debe registrarse.
- Si un objetivo no es alcanzable con la arquitectura actual, o el proyecto pierde sentido
  académico, la implementación MUST detenerse y el hallazgo MUST documentarse.

**Razón**: el jurado evalúa la coherencia entre título, objetivos, método, aplicación y
resultados. Una brecha oculta es más grave que una brecha declarada.

### III. Evidencia reproducible y motor versionado

Todo resultado MUST ser reproducible y atribuible a una versión concreta del motor.

- Cada ejecución MUST registrar la versión del motor (`cutting.VERSION`, hoy `secuencial-2`),
  la huella de la entrada, la semilla, el perfil y los parámetros resueltos. Con la misma
  entrada, parámetros, semilla y versión, el plan y sus métricas MUST ser idénticos.
- La huella del problema MUST incluir solo lo que altera el plan. Los datos de presentación o
  evaluación (por ejemplo, el umbral de desperdicio admisible) MUST NOT entrar en la huella ni
  en la estimación de tiempo.
- Un cambio que altere el plan producido requiere aprobación explícita del usuario, una nueva
  `VERSION` del motor y volver a ejecutar los ensayos afectados. La evidencia anterior MUST
  quedar ligada a su versión y MUST NOT presentarse como evidencia de la nueva.
- Los 136 ensayos y los 12 controles de `secuencial-2` (cartillas 001 y 002) son la línea base.
  Las funciones de medición o reporte MUST NOT invalidarlos ni exigir que se repitan.
- Los registros históricos (base de datos, artefactos, benchmarks) MUST NOT modificarse. Si les
  faltan campos nuevos, MUST mostrarse sin error, como «no disponible».
- Los resultados del Cap. 4 MUST provenir de ejecuciones reales con evidencia conservada en
  `tests/benchmarks/` o `tests/data/`.

**Razón**: un resultado sin versión ni semilla no se puede defender ante el jurado ni
reproducir en otra máquina.

### IV. El algoritmo genético optimiza; las demás técnicas miden

El único optimizador que produce el plan de corte es el algoritmo genético. Se encuadra como
técnica de Inteligencia Artificial (computación evolutiva).

- Las heurísticas (FFD, BFD y similares) MAY usarse como población inicial o como referencia
  comparativa, pero MUST NOT sustituir al AG como productor del plan.
- La cota inferior por patrones (Gilmore–Gomory, relajación lineal), la agrupación en patrones
  de corte, la evaluación de admisibilidad y cualquier otra métrica MUST NOT construir ni
  modificar el plan: son solo métricas derivadas.
- La aplicación y el documento MUST NOT afirmar que el plan es óptimo. La calidad se expresa
  como brecha frente a una cota y frente a las heurísticas de referencia.
- Añadir otro optimizador de producción requiere enmendar esta constitución.

**Razón**: los objetivos de la tesis comprometen un AG. Mezclar optimizadores diluye el aporte
y rompe la comparabilidad de la evidencia.

### V. Honestidad técnica y académica con trazabilidad

- Los riesgos técnicos y académicos MUST registrarse en `.claude/diagnostics/` y nunca
  ocultarse. Las suposiciones importantes MUST registrarse como `INF-XXX` en
  `INFERENCIAS_TESIS.md`, consolidando las similares en vez de duplicarlas.
- Toda fuente citada MUST tener una ficha en `docs/tesis-doc/Referencias.md` con su estado de
  verificación. Una fuente no verificada MUST NOT presentarse como verificada.
- Una exigencia normativa MUST NOT afirmarse sin una fuente verificada. Por ejemplo: ninguna
  norma colombiana fija un porcentaje máximo de desperdicio de acero, así que la aplicación no
  propone un umbral por defecto.
- El documento de tesis MUST describir solo lo que la aplicación ya hace y está validado. No se
  escriben conclusiones definitivas sobre funciones no validadas, y las notas `> Nota:` del
  autor son tareas pendientes que se respetan.
- Los datos de las cartillas 001 y 002 son confidenciales. MUST presentarse anonimizados, y el
  repositorio, el documento y los artefactos MUST NOT identificar la obra.

**Razón**: la credibilidad académica depende de declarar los límites y la procedencia de cada
afirmación.

### VI. Simplicidad y compatibilidad con lo existente

- El código nuevo MUST encajar en la arquitectura vigente: Next.js (frontend), Flask y
  Socket.IO (backend), Celery (worker), PostgreSQL, Redis y Nginx. Un servicio, capa o patrón
  nuevo MUST justificarse en la sección «Complexity Tracking» del plan y requiere aprobación
  del usuario.
- Backend y worker comparten el código de `backend/`. Todo cambio MUST considerar a ambos.
- Una dependencia nueva requiere revisión de compatibilidad (Python 3.12, Node 22, constraints)
  y aprobación previa del usuario si implica reconstruir imágenes o instalar paquetes.
- Las migraciones son solo de adición: MUST NOT editarse una migración aplicada; MUST
  agregarse una nueva en `config/backend/migrations/`.
- Los artefactos (Excel, PDF, PNG) MUST respetar sus límites de tamaño y memoria vigentes. Si
  el contenido no cabe, se muestra una muestra declarada y el total va en el Excel.
- El código muerto, duplicado o incoherente MUST marcarse antes de eliminarse. Ningún archivo
  MUST NOT borrarse sin explicar por qué y qué impacto tiene.

**Razón**: el proyecto ya está desplegado y validado. Cada pieza nueva aumenta el riesgo en
disco, en reproducibilidad y en el tiempo que queda para la tesis.

## Restricciones técnicas y operativas

- **Versiones**: Python 3.12 y Node 22. No se suben versiones mayores sin validar dependencias.
- **Dependencias**: las fuentes canónicas son `config/backend/` y `config/celery_worker/`, con
  el archivo común y los constraints. MUST NOT copiarse requisitos a `services/`.
- **Copias históricas**: `services/` MUST NOT editarse ni borrarse.
- **Secretos**: viven en `.env` y `.env.development` locales, o en
  `/opt/oica/shared/production.env` en la VPS. MUST NOT versionarse.
- **Recursos locales**: el disco C: tiene poco espacio. Antes de construir imágenes, instalar
  dependencias o generar volúmenes grandes de datos, el agente MUST avisar con una estimación
  de espacio y esperar aprobación.
- **Operaciones destructivas**: MUST NOT usarse `docker system prune` en la VPS compartida.
  Los resets, restauraciones, limpiezas globales y cambios de filesystem o permisos requieren
  confirmación explícita y respaldo.
- **Red**: el frontend usa `/api` y `/socket.io/` relativos. MUST NOT incrustar dominios,
  puertos ni URLs de túneles.
- **Interfaz**: los cambios de UI MUST seguir `docs/oica-redesign/AI-DESIGN-RULES.md` y el
  estado vigente en `docs/oica-redesign/STATE.md`.
- **Idioma**: documentación, comentarios, interfaz, esquema de base de datos y commits van en
  español.

## Flujo de trabajo y puertas de calidad

**Prioridades, en orden estricto**: (1) funcionalidad correcta de la aplicación; (2) coherencia
entre la aplicación y los objetivos de la tesis; (3) documento de tesis, solo después de
validar la aplicación.

**Bloques y Spec Kit**: se trabaja por bloques registrados en `PLAN_TRABAJO.md`. Una
funcionalidad nueva sigue el flujo specify → clarify (si hay ambigüedad) → plan → tasks →
implement. Cada `plan.md` MUST incluir un «Constitution Check» que evalúe los principios I–VI
uno por uno.

**Puertas obligatorias antes de dar un cambio por terminado**:

- Dominio, motor, métricas o artefactos: pruebas automatizadas de sus invariantes, más
  `python -m unittest discover -s tests -p 'test_*.py'` en `backend/` sin fallos.
- Cambios que puedan afectar el plan: puerta de regresión. Con las cartillas 001 y 002 y sus
  semillas registradas, el plan y las métricas MUST coincidir con la línea base, o aplicar el
  Principio III (nueva versión del motor).
- Frontend: `npm run typecheck`, `npm run lint` y `npm run build` sin errores. En cambios de
  UI, sin violaciones nuevas de accesibilidad (axe).
- Scripts de despliegue u operación: `python3 -m unittest discover -s tests/deployment -v`.
- Un cambio no se declara verificado sin haberlo ejecutado. Si se omite una puerta, MUST
  decirse explícitamente.

**Control de versiones**: los commits, push, PR, merge y despliegues se hacen solo con una
instrucción explícita del usuario para esa ocasión. La autorización no se extiende a otras
ocasiones ni a otras ramas.

**Persistencia entre sesiones**: al iniciar, se leen `.claude/context/CURRENT_STATE.md`,
`PLAN_TRABAJO.md` y las inferencias pendientes de `INFERENCIAS_TESIS.md`. Al cerrar una sesión
significativa, se actualizan esos tres archivos y, si cambió la dirección del proyecto,
`.claude/memory/HISTORICAL_CONTEXT.md`.

## Governance

Esta constitución prevalece sobre `AGENTS.md`, `CLAUDE.md`, los `AGENTS.md` de `backend/` y
`frontend/` y las definiciones de `.claude/agents/`. Esos archivos son guías operativas: ante un
conflicto rige la constitución, y la guía se corrige en una tarea aparte.

- **Enmiendas**: se proponen con `/speckit-constitution`, requieren aprobación explícita del
  usuario e incluyen un Sync Impact Report. Las decisiones académicas que dependan del
  director se marcan como pendientes de su revisión.
- **Versionado** (semántico):
  - MAJOR: eliminar o redefinir un principio de forma incompatible.
  - MINOR: añadir un principio o una sección, o ampliar materialmente una regla.
  - PATCH: aclaraciones y redacción.
- **Cumplimiento**:
  - Cada plan MUST pasar el Constitution Check antes de la investigación de la fase 0, y otra
    vez después del diseño.
  - Una violación MUST justificarse en «Complexity Tracking» y aprobarse por el usuario.
  - `/speckit-analyze` trata como CRITICAL todo conflicto con esta constitución.
  - Al cerrar cada bloque se revisa que sus cambios cumplan los principios I–VI.

**Version**: 1.0.0 | **Ratified**: 2026-10-02 | **Last Amended**: 2026-10-02
