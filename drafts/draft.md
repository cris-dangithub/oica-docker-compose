Perfecto. Ahora quiero que evoluciones la estructura persistente de trabajo de esta tesis para convertir este repositorio en un entorno técnico-académico mantenible a largo plazo.

IMPORTANTE:

- NO empieces todavía implementaciones grandes.
- NO rehagas arquitectura todavía.
- NO hagas commits.
- Esta fase es exclusivamente para organización, persistencia de contexto, trazabilidad e inferencias.

Objetivo general:
Construir un entorno de trabajo robusto para desarrollar, validar y terminar tanto la aplicación como la tesis sin pérdida de contexto entre sesiones.

La prioridad principal sigue siendo:

1. Validar que la aplicación tenga sentido respecto a la tesis.
2. Terminar la aplicación.
3. Luego trabajar el documento académico.

---

# Tareas obligatorias

## 1. Crear o mejorar `CLAUDE.md`

Debe contener:

- metodología general,
- prioridades,
- flujo de trabajo,
- restricciones,
- reglas académicas,
- reglas técnicas,
- manejo de inferencias,
- manejo de contradicciones,
- honestidad técnica/académica,
- trabajo por bloques grandes,
- trazabilidad,
- persistencia entre sesiones.

Debe incluir reglas explícitas como:

- No justificar artificialmente una tesis incoherente.
- No asumir objetivos académicos finales sin evidencia suficiente.
- Si el proyecto no tiene sentido, detener implementación y documentarlo.
- Priorizar funcionalidad real sobre UI.
- Toda inferencia importante debe registrarse.
- Las inferencias deben poder consolidarse y evolucionar.

---

# 2. Crear estructura `.claude/`

Estructura mínima esperada:

```text
.claude/
├── agents/
├── context/
├── workflows/
├── templates/
├── memory/
└── diagnostics/
```

---

# 3. Crear agentes especializados

Crear en `.claude/agents/`:

- `thesis-architect.md`
- `application-debugger.md`
- `academic-reviewer.md`
- `implementation-planner.md`
- `inference-manager.md`
- `context-manager.md`

Cada agente debe incluir:

- responsabilidades,
- límites,
- criterios de decisión,
- cuándo actuar,
- cuándo detenerse,
- ejemplos prácticos,
- señales de riesgo,
- y relación con otros agentes.

NO crear placeholders vacíos.

---

# 4. Crear sistema avanzado de inferencias

Actualizar completamente el manejo de inferencias.

Crear o mejorar:

```text
INFERENCIAS_TESIS.md
```

Y crear:

```text
.claude/templates/INFERENCE_TEMPLATE.md
```

Las inferencias ahora deben incluir:

- ID único,
- categoría,
- prioridad,
- estado,
- impacto,
- referencias cruzadas,
- archivos afectados,
- riesgo,
- fecha,
- inferencias relacionadas,
- posibilidad de consolidación.

Estados mínimos:

- `[PENDIENTE]`
- `[VALIDADA]`
- `[RECHAZADA]`
- `[OBSOLETA]`
- `[CONSOLIDADA]`

Categorías mínimas:

- Arquitectura
- Académica
- Datos
- UI/UX
- Metodología
- Flujo de usuario
- Suposición técnica
- Alcance
- Riesgo

Debe existir mecanismo para:

- detectar inferencias duplicadas,
- detectar contradicciones,
- consolidar inferencias antiguas,
- resumir contexto histórico,
- evitar crecimiento descontrolado.

Ejemplo esperado:

```md
## INF-014

### Categoría

Arquitectura

### Prioridad

Alta

### Pregunta inferida

¿La aplicación debe priorizar funcionalidad completa antes de optimización visual?

### Respuesta asumida

Sí. La funcionalidad principal es más importante para validar la tesis.

### Impacto

- frontend/
- backend/
- docs/

### Riesgo

Medio

### Inferencias relacionadas

- INF-003
- INF-008

### Estado

[PENDIENTE]

### Reemplaza

Ninguna

### Puede consolidarse con

- INF-019

### Respuesta del usuario

<!-- pendiente -->
```

---

# 5. Crear memoria persistente

Crear:

```text
.claude/context/CURRENT_STATE.md
```

Debe contener:

- objetivo actual,
- estado global,
- bloque actual,
- hipótesis activas,
- contradicciones detectadas,
- riesgos,
- decisiones recientes,
- próximos pasos,
- preguntas pendientes,
- estado académico,
- estado técnico.

Crear también:

```text
.claude/memory/HISTORICAL_CONTEXT.md
```

Para resumir:

- decisiones antiguas,
- inferencias consolidadas,
- cambios de dirección,
- problemas históricos.

---

# 6. Crear workflow persistente

Crear:

```text
.claude/workflows/THESIS_WORKFLOW.md
```

Debe definir:

- flujo completo del proyecto,
- fases,
- validaciones,
- checkpoints,
- manejo de contradicciones,
- cuándo detener implementación,
- cuándo cuestionar objetivos,
- cómo coordinar agentes,
- cómo manejar incertidumbre,
- cómo evolucionar inferencias.

---

# 7. Crear sistema de diagnósticos

Crear:

```text
.claude/diagnostics/
```

Y dentro:

- `ACADEMIC_RISKS.md`
- `TECHNICAL_RISKS.md`
- `ARCHITECTURE_WARNINGS.md`

Registrar:

- inconsistencias,
- riesgos,
- deuda técnica,
- contradicciones tesis ↔ aplicación,
- features fuera de alcance,
- problemas metodológicos.

---

# 8. Crear o mejorar `PLAN_TRABAJO.md`

Debe incluir:

- bloques grandes,
- prioridad,
- dependencias,
- estado,
- riesgos,
- criterios de finalización,
- complejidad,
- relación con objetivos de tesis.

---

# 9. Actualizar todo usando el diagnóstico actual

Usar el análisis ya realizado previamente para:

- poblar contexto,
- registrar hipótesis,
- registrar inconsistencias,
- registrar riesgos,
- generar primeros checkpoints.

---

# Reglas críticas

- NO hacer commits.
- NO rehacer todavía arquitectura completa.
- NO empezar aún implementaciones masivas.
- NO inventar objetivos académicos sin evidencia.
- NO justificar artificialmente inconsistencias.
- NO ocultar riesgos técnicos o académicos.
- Toda decisión importante debe quedar trazable.
- Todo debe quedar preparado para múltiples sesiones futuras.

---

# Entrega esperada

Al finalizar:

1. Mostrar estructura completa creada.
2. Explicar propósito de cada carpeta.
3. Explicar propósito de cada agente.
4. Explicar cómo interactúan los agentes.
5. Explicar cómo manejar inferencias a largo plazo.
6. Explicar cómo continuar futuras sesiones sin perder contexto.
7. Explicar cuál debería ser el siguiente bloque recomendado.
8. Explicar qué riesgos importantes detectas desde ya en la metodología actual.
