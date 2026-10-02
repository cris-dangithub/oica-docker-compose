# Riesgos Técnicos

> Bugs, deuda técnica, problemas de integración y riesgos que afectan la funcionalidad de la aplicación.

---

## RIESGO-TEC-001 — Bugs críticos en server.py

**Severidad:** CRÍTICA

**Descripción:**
`services/backend/server.py` tiene 5 bugs de atributos incorrectos que causan `AttributeError` en runtime al usar los endpoints de filtrado por perfil, eliminación y reprocesamiento.

**Bugs específicos:**

| Línea | Código incorrecto | Corrección |
|-------|-------------------|------------|
| 212 | `UploadedFile.filename` | `UploadedFile.file_name` |
| 222 | `UploadedFile.perfil` | No existe en modelo — requiere lógica diferente |
| 303 | `uploaded_file.processing_results` | `uploaded_file.results` |
| 311, 352 | `uploaded_file.uploaded_file_path` | `uploaded_file.file_path` |
| 360, 370, 371 | `uploaded_file.perfil` | `uploaded_file.results[0].perfil_usado` |

**Impacto:** Los endpoints `/files` (con filtro perfil), `DELETE /file/<id>` y `POST /reprocess/<id>` fallan.

**Inferencias relacionadas:** INF-004

**Estado:** [CONFIRMADO — pendiente corrección en Bloque A]

---

## RIESGO-TEC-002 — Filtro por perfil requiere JOIN con ProcessingResult

**Severidad:** ALTA

**Descripción:**
El endpoint `GET /files` acepta un filtro `?perfil=rapido` pero el perfil no es una columna directa en `UploadedFile`. El perfil está en `ProcessingResult.perfil_usado`. Filtrar requiere un JOIN o una subquery.

**Evidencia:**
- `services/backend/server.py` línea 222: `query = query.filter(UploadedFile.perfil == perfil)`
- `services/backend/models/uploaded_file.py`: `UploadedFile` no tiene columna `perfil`.

**Impacto:** El filtro por perfil en la lista de archivos no funciona.

**Corrección propuesta:**
```python
# Opción A: Subquery
from sqlalchemy import exists
subq = db.session.query(ProcessingResult.uploaded_file_id).filter(
    ProcessingResult.perfil_usado == perfil
).subquery()
query = query.filter(UploadedFile.id.in_(subq))

# Opción B: Eliminar el filtro por perfil (más simple, menos funcionalidad)
```

**Inferencias relacionadas:** INF-004

**Estado:** [CONFIRMADO — pendiente decisión sobre Opción A vs B]

---

## RIESGO-TEC-003 — Duplicación de requirements.txt sin mecanismo de sincronización

**Severidad:** MEDIA

**Descripción:**
El `requirements.txt` de producción existe en dos lugares: `config/backend/requirements.txt` (fuente de verdad) y `services/backend/requirements.txt` (copia para Docker build). No hay mecanismo automático de sincronización. Si se olvida sincronizar, el Docker build usa dependencias desactualizadas.

**Evidencia:**
- `AGENTS.md` documenta este problema explícitamente.
- No hay script de sincronización automática.

**Impacto:** Builds inconsistentes si se agrega una dependencia.

**Corrección propuesta:** Script en `Makefile` o hook de pre-build en `docker-compose.yaml`.

**Estado:** [CONFIRMADO — deuda técnica conocida, baja prioridad]

---

## RIESGO-TEC-004 — Celery Worker recibe contexto Flask duplicado

**Severidad:** BAJA-MEDIA

**Descripción:**
El worker crea su propio contexto Flask en `create_flask_app()` dentro de la tarea Celery. Si hay un error en la creación del contexto Flask secundario, el worker falla silenciosamente en el bloque `except: pass`.

**Evidencia:**
- `services/backend/celery_worker.py` líneas 142-153: `create_flask_app()`
- Líneas 588-596: `except: pass` en el handler de error.

**Impacto:** Si la segunda instancia de Flask no puede conectar a la BD, el error se ignora y el estado en BD queda inconsistente.

**Estado:** [IDENTIFICADO — baja prioridad, no bloquea funcionalidad principal]

---

## RIESGO-TEC-005 — Mass unitaria calculada con densidad genérica

**Severidad:** BAJA

**Descripción:**
En `celery_worker.py` línea 473, la masa de cada barra se calcula con un factor fijo `0.888 kg/m` (aproximación para barra #8). Esto es incorrecto para otros diámetros. La masa real depende del diámetro.

**Evidencia:**
```python
masa_kg = barra_longitud * 0.888  # Peso aproximado kg/m para barra #8
```

**Impacto:** Los datos de masa en los artefactos generados son incorrectos para diámetros diferentes al #8.

**Corrección propuesta:** Usar `barras_estandar.json` para obtener la masa por unidad de longitud según el diámetro real.

**Estado:** [IDENTIFICADO — pendiente corrección cuando se resuelva INF-001]

---

## RIESGO-TEC-006 — Servicios Docker inactivos

**Severidad:** INFORMATIVA

**Descripción:**
Actualmente no hay contenedores corriendo. La app no está disponible para pruebas.

**Acción para resolver:**
```bash
docker compose up -d --build
```

**Estado:** [INFORMATIVO — el usuario levanta los servicios cuando decida ejecutar pruebas]
