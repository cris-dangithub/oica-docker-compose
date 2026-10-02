# Workflow de la Tesis OICA

> Define el flujo completo del proyecto, las validaciones necesarias, los criterios de avance y el manejo de incertidumbre.

---

## Flujo general de fases

```
FASE 0: Organización         → FASE A: Bugs críticos
FASE A: Bugs críticos        → FASE B: Lógica de dominio (si INF-001 validada)
FASE B: Lógica de dominio    → FASE C: Validación end-to-end
FASE C: Validación           → FASE D: Features adicionales (opcional)
FASE C: Validación           → FASE E: Documento de tesis
FASE E: Documento            → ENTREGA FINAL
```

---

## Validaciones requeridas por fase

### Antes de iniciar Bloque A
- [x] Diagnóstico del repo completado.
- [x] Bugs identificados y documentados en INF-004.
- [x] No requiere validación del usuario.

### Antes de iniciar Bloque B
- [ ] INF-001 respondida por el usuario (agrupación por diámetro).
- [ ] INF-006 respondida o consolidada con INF-001.
- [ ] Bloque A completado.

### Antes de iniciar Bloque C
- [ ] Bloque A completado.
- [ ] Bloque B completado (o alcance de Bloque B definido).
- [ ] Contenedores Docker disponibles para levantar.

### Antes de iniciar Bloque E
- [ ] Bloque C completado (app funciona end-to-end).
- [ ] Resultados reales de pruebas disponibles para Cap. 4.
- [ ] INF-002 respondida (nombres de perfiles para el documento).
- [ ] INF-008 respondida (alcance de reutilización de desperdicios).

---

## Checkpoints de validación

### Checkpoint A — Backend funcional
**Criterio:** Los endpoints `/files`, `DELETE /file/<id>` y `POST /reprocess/<id>` responden sin `AttributeError`.
**Cómo verificar:**
```bash
docker compose up -d --build
curl http://localhost:5000/health
curl "http://localhost:5000/files?perfil=balanceado"
```

### Checkpoint B — AG por diámetro
**Criterio:** Al subir una cartilla con 3 diámetros distintos, el resultado muestra 3 grupos de patrones de corte.
**Cómo verificar:** Upload de `Planilla_Cartilla.xlsx` y revisar el resultado en BD o en la UI.

### Checkpoint C — Flujo completo
**Criterio:** Se puede hacer upload → procesamiento → descarga de PDF, Excel e imagen sin errores.
**Cómo verificar:** Flujo manual completo desde la UI en `http://localhost:80`.

---

## Manejo de contradicciones

### Tipo 1: Código contradice documento

1. Registrar en `INFERENCIAS_TESIS.md` (nueva INF o actualizar existente).
2. Registrar en `.claude/diagnostics/ARCHITECTURE_WARNINGS.md`.
3. Si es crítico para resultados académicos: detener avance y consultar al usuario.
4. Si es de documentación: marcar para actualización en Bloque E.

### Tipo 2: Dos inferencias se contradicen

1. Registrar en `.claude/diagnostics/ARCHITECTURE_WARNINGS.md`.
2. Marcar ambas inferencias como relacionadas.
3. Preguntar al usuario cuál prevalece.
4. Archivar la que queda obsoleta.

### Tipo 3: El código no cumple un objetivo de la tesis

1. Registrar en `ACADEMIC_RISKS.md`.
2. Evaluar si es un bug (corrección técnica) o un gap de alcance (decisión del usuario).
3. Si es gap de alcance: crear INF de categoría `Alcance`.
4. Si el gap invalida la tesis: detener implementación y reportar.

---

## Cuándo detener implementación

Detener y consultar al usuario cuando:

1. Un bug de lógica de dominio haría que todos los resultados sean físicamente inválidos.
2. Un objetivo de la tesis no tiene implementación posible con la arquitectura actual.
3. Hay 3+ inferencias `[PENDIENTE]` de prioridad Alta que bloquean el mismo componente.
4. El documento de tesis y el código tienen versiones completamente diferentes del mismo feature.

No detener por:
- Bugs de atributos o nombres (corrección directa).
- Documentación desactualizada (marcar para Bloque E).
- Features secundarios no implementados si el core funciona.

---

## Manejo de incertidumbre

| Nivel de certeza | Acción |
|-----------------|--------|
| Certeza alta (bug obvio) | Corregir directamente |
| Certeza media (comportamiento dudoso) | Crear INF, asumir lo más razonable, documentarlo |
| Certeza baja (decisión académica) | Crear INF, detenerse, preguntar |
| Sin evidencia suficiente | No asumir, documentar como `[PENDIENTE]` |

---

## Coordinación de agentes

```
context-manager
    → Al iniciar: presenta estado de sesión
    → Al finalizar: actualiza CURRENT_STATE.md

implementation-planner
    → Define qué bloque ejecutar
    → Verifica que las dependencias estén cubiertas

thesis-architect
    → Verifica coherencia tesis-app antes de cada bloque
    → Detecta brechas y las reporta

application-debugger
    → Ejecuta correcciones técnicas
    → Reporta bugs nuevos a inference-manager

inference-manager
    → Gestiona INFERENCIAS_TESIS.md
    → Alerta sobre contradicciones

academic-reviewer
    → Activo solo en Bloque E
    → Revisa calidad del documento
```

---

## Cómo continuar futuras sesiones

Al inicio de cualquier sesión futura:

1. Leer `.claude/context/CURRENT_STATE.md` (estado global).
2. Leer `PLAN_TRABAJO.md` (bloque activo y pendientes).
3. Revisar índice de `INFERENCIAS_TESIS.md` (inferencias `[PENDIENTE]` de Alta prioridad).
4. Verificar si el código en `services/backend/server.py` ya tiene las correcciones del Bloque A.
5. Presentar resumen al usuario usando el formato de context-manager.

**Regla crítica:** No asumir que el trabajo previo está hecho. Verificar en el código.

---

## Evolución del sistema de inferencias

Las inferencias evolucionan en el tiempo. Un buen sistema:

- Comienza con inferencias `[PENDIENTE]`.
- Las resuelve en la misma sesión o en la siguiente.
- Archiva las `[OBSOLETA]` y `[CONSOLIDADA]` para no contaminar el archivo activo.
- No crece indefinidamente — máximo 15 inferencias activas. Si supera esto, consolidar.

Señal de que el sistema está funcionando mal:
- Más de 5 inferencias de la misma categoría sin resolver.
- Inferencias que nadie lee ni actualiza.
- El usuario no sabe qué preguntas están pendientes.
