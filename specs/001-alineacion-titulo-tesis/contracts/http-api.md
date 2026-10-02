# Contrato HTTP — cambios de la feature 001

La base es `/api`, a través de Nginx. Solo se listan los cambios; el resto de cada endpoint no
cambia (`backend/server.py`). Los mensajes de error van en español.

## `POST /upload` y `POST /estimate` (multipart)

Campo nuevo, opcional:

| Campo | Tipo | Regla |
|---|---|---|
| `umbral_desperdicio_pct` | texto decimal (`"7.5"` o `"7,5"`) | Vacío o ausente equivale a `null`. Si no está vacío, debe ser finito y cumplir `0 < v < 100`. |

- **Error**: un valor inválido devuelve `400 {"error": "Umbral de desperdicio admisible
  inválido: debe ser un porcentaje mayor que 0 y menor que 100"}`, **antes** de guardar el
  archivo o encolar.
- **Almacenamiento**: `execution_config.umbral_desperdicio_pct`. No se pasa a `normalize()` y no
  altera `input_hash`.
- **`/estimate`**: acepta el campo y lo ignora. La estimación no cambia.

## `POST /reprocess/<id>` (JSON)

```json
{ "perfil": "balanceado", "umbral_desperdicio_pct": 10 }
```

| `umbral_desperdicio_pct` | Efecto |
|---|---|
| clave ausente | Se conserva el umbral vigente del archivo. |
| `null` | Se quita el umbral; la versión nueva queda `sin_evaluar`. |
| número válido | Reemplaza el vigente en `uploaded_files.execution_config`. |
| inválido | `400`, sin encolar y sin modificar nada. |

Los códigos 404 y 409 existentes se mantienen.

## `GET /files` (lista)

Cada elemento de `processing_results[]` añade:

```json
{ "valido": true, "umbral_desperdicio_pct": 10.0,
  "admisibilidad_estado": "dentro" }
```

Si falta el dato, el campo vale `null`: `umbral_desperdicio_pct` y `admisibilidad_estado` son `null` en las versiones anteriores a `analisis-1`; `valido` ya existe en las versiones de `secuencial-2` y solo es `null` en las del motor histórico.

## `GET /file/<id>` (detalle, usado por `/archivos/[id]`)

- **Archivo**: añade `umbral_desperdicio_pct`, el vigente.
- **Cada versión**: añade `valido`, `umbral_desperdicio_pct`, `processing_time_seconds`,
  `perfil_usado` y `analisis`, con la estructura de [data-model.md §2](../data-model.md).
  `analisis` vale `null` en las versiones históricas.

## Worker: estados ante el error de dominio

Si la cota es mayor que el desperdicio del plan, el resultado no se guarda como válido:

- `processing_status = 'error_processing'`;
- `status_details` empieza por `"Error de dominio:"` y nombra el diámetro, el desperdicio y la
  cota.

Los fallos de validación del plan conservan el comportamiento actual: `error_processing` con el
motivo de `domain.validate`.
