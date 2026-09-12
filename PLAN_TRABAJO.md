# Plan de Trabajo — OICA Tesis

> **Última actualización:** 2026-09-12
> **Estado global:** Monorepo e infraestructura implementados; validación final y VPS pendientes
> **Bloque activo:** F — Producción, CI/CD y desarrollo nativo

---

## Resumen de fases

| Fase | Nombre | Estado | Prioridad |
|------|--------|--------|-----------|
| 0 | Organización y persistencia de contexto | ✅ Completada | — |
| A | Corrección de bugs críticos (server.py) | ✅ Completada | CRÍTICA |
| B | Agrupación por diámetro en el AG | ✅ Completada | CRÍTICA |
| C | Validación end-to-end | ✅ Completada | ALTA |
| D | Reutilización de desperdicios previos | ⏳ Bloqueada por INF-alcance | MEDIA |
| E | Actualización del documento de tesis | 🔄 Listo para iniciar | ALTA |
| F | Producción, CI/CD y desarrollo nativo | 🔄 Código implementado; cierre pendiente | ALTA |

---

## Bloque A — Corrección de bugs críticos en `server.py`

**Objetivo:** Hacer que los endpoints `/files` (filtro perfil), `DELETE /file/<id>` y `POST /reprocess/<id>` no fallen con `AttributeError`.

**Complejidad:** Baja — son correcciones de nombres de atributos.

**Dependencias:** Ninguna.

**Riesgos:** Bajo — correcciones quirúrgicas, no cambian lógica.

**Archivos afectados:**
- `services/backend/server.py`

**Bugs a corregir:**

| Línea | Bug | Corrección |
|-------|-----|-----------|
| 212 | `UploadedFile.filename` | `UploadedFile.file_name` |
| 222 | `UploadedFile.perfil` | JOIN con `ProcessingResult.perfil_usado` o eliminar filtro |
| 303 | `uploaded_file.processing_results` | `uploaded_file.results` |
| 311, 352 | `uploaded_file.uploaded_file_path` | `uploaded_file.file_path` |
| 360, 370, 371 | `uploaded_file.perfil` | obtener de `uploaded_file.results[0].perfil_usado` |

**Criterio de finalización:** `server.py` importa sin errores y los 3 endpoints responden correctamente.

**Inferencias relacionadas:** INF-004

**Estado:** ✅ Completado — 2026-05-06

Correcciones aplicadas:
- L212: `UploadedFile.filename` → `UploadedFile.file_name`
- L217: `UploadedFile.status` → `UploadedFile.processing_status` (bug adicional encontrado)
- L220-222: filtro por perfil reescrito con subquery via `ProcessingResult.perfil_usado`
- L303: `uploaded_file.processing_results` → `uploaded_file.results`
- L311: `uploaded_file.uploaded_file_path` → `uploaded_file.file_path`
- L352: `uploaded_file.uploaded_file_path` → `uploaded_file.file_path`
- L360-371: lógica de perfil reescrita (se obtiene de `uploaded_file.results[0].perfil_usado`; se eliminó el update inválido de `uploaded_file.perfil`)

---

## Bloque B — Agrupación por diámetro en el AG

**Objetivo:** El algoritmo genético debe procesar las piezas agrupadas por `N° de Barra` (diámetro). Actualmente procesa todas las piezas juntas, lo que es físicamente incorrecto.

**Complejidad:** Media-Alta — requiere modificar el flujo en `celery_worker.py` y posiblemente el output formatter.

**Dependencias:** INF-001 debe ser validada por el usuario primero.

**Riesgos:** Medio — cambia la lógica de negocio central. Requiere prueba end-to-end después.

**Archivos afectados:**
- `services/backend/celery_worker.py` — función `process_file_task`
- `services/backend/genetic_algorithm/output_formatter.py` — posiblemente
- `services/backend/utils/artifact_generator.py` — posiblemente

**Criterio de finalización:** Al subir una cartilla con múltiples diámetros, los resultados muestran planes de corte separados por diámetro.

**Inferencias relacionadas:** INF-001 [VALIDADA], INF-006 [CONSOLIDADA]

**Estado:** ✅ Completado — 2026-05-06

Cambios aplicados en `services/backend/celery_worker.py`:
- Eliminada la transformación que aplanaba todas las piezas en un solo `df_ag`.
- El AG ahora se ejecuta una vez por cada `N° de Barra` (diámetro) presente en la cartilla.
- Cada grupo recibe sus longitudes comerciales propias desde `barras_estandar.json` (con fallback a 6/9/12 m si la clave no existe).
- Cada `patron` se enriquece con `diametro` y `masa_por_metro_kg` (densidad lineal real, derivada de la propia cartilla del grupo). Reemplaza la constante `0.888` que era válida solo para barra #8.
- Métricas globales reorganizadas: `metricas_por_diametro`, `total_grupos`, `total_patrones`.
- `progress_callback` reemplazado por `make_group_progress_callback(grupo_idx, total_grupos, diametro_str)`. El rango 30-70% se reparte equitativamente entre grupos.
- La columna `diametro` se agrega a los registros enviados al `artifact_generator` (es una columna extra, no rompe la validación).

Pendiente: corroborar end-to-end (Bloque C) y, si el PDF/Excel actual no muestra el diámetro, enriquecer las plantillas para hacerlo visible. Lo evalúo en el Bloque C.

---

## Bloque C — Validación end-to-end

**Objetivo:** Levantar el sistema completo con Docker Compose y ejecutar el flujo completo con `Planilla_Cartilla.xlsx`. Verificar que todos los pasos funcionan: upload → procesamiento → descarga de artefactos.

**Complejidad:** Media — depende de que A y B estén completos.

**Dependencias:** Bloque A completo, Bloque B completo (o definir alcance sin B).

**Riesgos:** Alto — pueden aparecer bugs adicionales no detectados en análisis estático.

**Archivos afectados:**
- Todos los servicios — validación de integración

**Criterio de finalización:**
1. `docker compose ps` muestra todos los servicios `healthy`.
2. Upload de `Planilla_Cartilla.xlsx` retorna `file_id` y `task_id`.
3. El worker procesa y actualiza progreso via WebSocket.
4. Los 3 artefactos (Excel, PDF, PNG) son descargables.
5. Los filtros en `/files` funcionan correctamente.

**Inferencias relacionadas:** INF-007

**Estado:** ✅ Completado — 2026-05-06

Resultados de la validación con `tests/data/001-pruebaInicial.xlsx`:
- Upload → procesamiento → artefactos: flujo completo exitoso en **15.69s**
- AG agrupó por diámetro: **#5** (33 barras), **#4** (1 barra), **#3** (1 barra)
- Los 3 artefactos son válidos: Excel (8K), PDF (16K), PNG (216K — 3154×3476px)
- Filtros `/files?perfil=` y `/files?estado=` funcionan correctamente
- Endpoints de descarga: `/descargar-excel/<uuid>`, `/descargar-pdf/<uuid>`, `/descargar-imagen/<uuid>`

---

## Bloque D — Reutilización de desperdicios previos

**Objetivo:** Implementar el mecanismo para que al reprocesar un archivo, los desperdicios de la versión anterior se pasen como `desperdicios_previos` al AG.

**Complejidad:** Media — actualmente `desperdicios_previos = []` siempre.

**Dependencias:** Bloque B completo, validación del alcance por el usuario.

**Riesgos:** Medio — requiere definir qué constituye un "desperdicio reutilizable".

**Archivos afectados:**
- `services/backend/celery_worker.py`
- `services/backend/genetic_algorithm/output_formatter.py`
- `services/backend/models/uploaded_file.py` — posiblemente nuevo campo

**Criterio de finalización:** Al reprocesar, el AG recibe los desperdicios de la versión anterior y los considera en la optimización.

**Inferencias relacionadas:** Por definir

**Estado:** ⏳ Bloqueada — pendiente decisión de alcance del usuario

---

## Bloque E — Actualización del documento de tesis

**Objetivo:** Actualizar el documento de tesis para que sea coherente con la aplicación final.

**Complejidad:** Alta — trabajo redaccional significativo.

**Dependencias:** Bloque C completo (resultados reales de pruebas).

**Riesgos:** Bajo técnicamente, alto académicamente si se redacta sin resultados reales.

**Tareas dentro de este bloque:**

| Tarea | Archivo | Estado |
|-------|---------|--------|
| Reescribir sección 3.3.3 (Frontend) | `03_Capitulo3.md` | ⏳ Pendiente |
| Completar notas pendientes Cap. 2 | `02_Capitulo2.md` | ⏳ Pendiente |
| Llenar Cap. 4 con resultados reales | `04_Capitulo4.md` | ⏳ Bloqueada por C |
| Agregar sección Docker en Cap. 2 | `02_Capitulo2.md` | ⏳ Pendiente |
| Actualizar nombres de perfiles en doc | `03_Capitulo3.md` | ⏳ Pendiente INF-002 |
| Abstract del documento | `01_Capitulo1.md` | ⏳ Pendiente |

**Inferencias relacionadas:** INF-002, INF-003, INF-005

**Estado:** ⏳ Bloqueada — dependencias no completadas

---

## Preguntas pendientes del usuario

| ID | Pregunta | Bloque que desbloquea |
|----|----------|----------------------|
| INF-001 | ¿El AG debe agrupar por diámetro de barra? | B |
| INF-002 | ¿Cuáles son los nombres finales de los perfiles? | E |
| D-alcance | ¿La reutilización de desperdicios previos está en el alcance? | D |


## Bloque F — Producción, CI/CD y desarrollo nativo

**Objetivo:** push a production despliega OICA en VPS, con localhost:80 por Compose, desarrollo nativo y reset manual explícito.

**Decisiones:** INF-011 validada por el usuario. Monorepo; app pública sin login; VPS con 80/443 libres; dominio oica.cris-munoz.me; primera base vacía; actualizaciones interrumpen tareas; respaldo de reset configurable.

- [x] Preservar originales y copiar código con correcciones a backend/frontend.
- [x] Incorporar commits remotos conocidos por fast-forward y renombrar rama local a production, sin crear commits.
- [x] Compose, imágenes, Nginx, URLs relativas, migraciones y configuración externa.
- [x] Scripts de desarrollo nativo y guía operativa.
- [x] Workflows de CI, publicación SSH, reset y rollback; publicación de imágenes ya verificadas sin segundo build.
- [x] Pruebas del algoritmo (58), E2E inicial, tipos/lint y scripts (10).
- [x] Verificar persistencia y coherencia matemática del smoke tras reparar WSL, solo mediante lecturas.
- [ ] Completar build final de imágenes Python y comprobar su ejecución.
- [ ] Ensayar reset/restauración y rollback con datos en un entorno desechable.
- [ ] Instalar y probar el entorno nativo completo con Python 3.12/Node 22.
- [ ] Activar puerto 80 del stack local final y configurar/desplegar VPS/HTTPS.
- [ ] Publicar rama production y cambiar default remoto cuando se autoricen commits/push.

**Restricción actual:** C: tiene 6 GB libres (99 % usado); no ejecutar builds ni instalaciones significativas sin avisar al usuario con estimación. No efectuar limpiezas, mounts ni cambios de permisos globales. Ver CURRENT_STATE.md para el estado exacto.
