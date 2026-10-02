# Advertencias de Arquitectura

> Inconsistencias de arquitectura, decisiones de diseño cuestionables, y advertencias que afectan la mantenibilidad o corrección del sistema.

---

## ARCH-WARN-001 — AG no agrupa por diámetro (contradicción con dominio del problema)

**Tipo:** Inconsistencia lógica de dominio

**Descripción:**
El algoritmo genético recibe todas las piezas requeridas juntas, sin importar el tipo de barra (`N° de Barra`). En el dominio real del problema, cada pieza tiene un diámetro específico y solo puede cortarse de una barra del mismo diámetro.

**Flujo actual (incorrecto):**
```
Excel con 3 diámetros → df_ag con todas las piezas juntas → AG → 1 plan de corte mezclado
```

**Flujo esperado:**
```
Excel con 3 diámetros → Agrupar por N° de Barra → AG por grupo → 3 planes de corte separados → Unificar output
```

**Archivos afectados:**
- `services/backend/celery_worker.py` (transformación a df_ag)
- `services/backend/genetic_algorithm/output_formatter.py` (output por grupo)

**Resolución:** Pendiente INF-001

---

## ARCH-WARN-002 — Inconsistencia en nombres de atributos entre modelo y servidor

**Tipo:** Desalineación de interfaz

**Descripción:**
El modelo `UploadedFile` en `models/uploaded_file.py` y el servidor `server.py` usan nombres diferentes para los mismos atributos. Esto es consecuencia de una refactorización parcial.

**Casos específicos:**
- Modelo: `file_name`, Servidor: `filename`
- Modelo: relación `results`, Servidor: `processing_results`
- Modelo: `file_path`, Servidor: `uploaded_file_path`
- Modelo: no tiene `perfil`, Servidor: accede a `uploaded_file.perfil`

**Resolución:** Bloque A corrige estos bugs. Para el futuro, evitar refactorizaciones sin actualizar todos los consumidores.

---

## ARCH-WARN-003 — Dos instancias de Flask en el proceso Celery

**Tipo:** Diseño subóptimo

**Descripción:**
El worker Celery crea una segunda instancia de Flask (`create_flask_app()`) para tener contexto de base de datos. Esto es una solución válida pero introduce riesgo: si la segunda instancia falla, el error se silencia con `except: pass`.

**Patrón más robusto:** Usar el patrón de `celery.init_app(app)` con una sola instancia de Flask configurada como factory.

**Archivos afectados:**
- `services/backend/celery_worker.py`

**Prioridad:** Baja — funciona pero es frágil. Considerar en refactorización futura.

---

## ARCH-WARN-004 — Frontend usa `prompt()` para selección de perfil en reprocesamiento

**Tipo:** UX problemático

**Descripción:**
`FilesTable.tsx` usa `window.prompt()` para que el usuario seleccione el perfil al reprocesar. Esta no es una UI apropiada para producción o para demostración académica.

**Evidencia:**
- `services/frontend/src/components/FilesTable.tsx` líneas 209-215.

**Impacto:**
- Experiencia de usuario mala.
- En algunos navegadores, `prompt()` está bloqueado por defecto.

**Corrección propuesta:** Modal con selector de perfil.

**Prioridad:** Media — afecta funcionalidad de reprocesamiento desde la UI.

---

## ARCH-WARN-005 — `document_number` en UploadedFile está deprecated pero sigue en uso

**Tipo:** Deuda técnica

**Descripción:**
El campo `document_number` en `UploadedFile` está marcado como `[DEPRECATED]` en el código pero todavía es:
- Usado en `server.py` para auto-rellenar desde el nombre del archivo.
- Referenciado en `artifact_generator.py` como metadato del documento.
- Parte del schema SQL con índice.

**Resolución real:** O se limpia completamente o se elimina el comentario de deprecated. Estado ambiguo genera confusión.

**Prioridad:** Baja — funcional, pero confuso para quien lee el código.

---

## ARCH-WARN-006 — Contradicción activa entre INF-001 e INF-006

**Tipo:** Contradicción de inferencias

**Descripción:**
INF-001 pregunta si el AG debe agrupar por diámetro. INF-006 pregunta si es un bug o diseño. Aunque apuntan en la misma dirección, son técnicamente dos preguntas diferentes. Si el usuario responde INF-001 como "sí, agrupar", INF-006 queda respondida automáticamente como "es un bug". Estas inferencias deben consolidarse una vez el usuario responda INF-001.

**Acción:** Cuando INF-001 sea respondida, consolidar INF-006 con ella y archivar una de las dos.
