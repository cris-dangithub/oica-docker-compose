# Plan de Trabajo — OICA Tesis

> **Última actualización:** 2026-09-13
> **Estado global:** Motor secuencial y aplicación local validados; cierre académico pendiente
> **Bloque activo:** H — Pérdida de corte y mínimo reutilizable configurables

---

## Resumen de fases

| Fase | Nombre | Estado | Prioridad |
|------|--------|--------|-----------|
| 0 | Organización y persistencia de contexto | ✅ Completada | — |
| A | Corrección de bugs críticos (server.py) | ✅ Completada | CRÍTICA |
| B | Agrupación por diámetro en el AG | ✅ Completada | CRÍTICA |
| C | Validación end-to-end | ✅ Completada | ALTA |
| D | Reutilización de desperdicios previos | Integrada en G por decisión del usuario | ALTA |
| E | Actualización del documento de tesis | Capítulos 1–4 reformulados; revisión académica pendiente | ALTA |
| F | Producción, CI/CD y desarrollo nativo | 🔄 Código implementado; cierre pendiente | ALTA |
| G | Corte secuencial, inventarios y caso 002 | Completado en localhost; cierre académico pendiente | ALTA |

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
- [x] Completar build final de imágenes Python y comprobar su ejecución en GitHub Actions.
- [x] Ensayar reset/restauración y rollback con datos en un entorno desechable (CI 34691570574).
- [ ] Instalar y probar el entorno nativo completo con Python 3.12/Node 22.
- [ ] Activar puerto 80 del stack local final y configurar/desplegar VPS/HTTPS.
- [x] Crear commit de implementación con autorización del usuario (0330943).
- [x] Publicar rama production mediante Git por SSH y configurar su seguimiento remoto.
- [x] Cambiar default remoto a production (usuario), confirmado mediante API pública.
- [x] Completar ensayo de recuperación de GitHub Actions.
- [ ] Preparar VPS y completar despliegue: falló Transferir y actualizar en 34691570574.

**Restricción actual:** C: tiene 6 GB libres (99 % usado); no ejecutar builds ni instalaciones significativas sin avisar al usuario con estimación. No efectuar limpiezas, mounts ni cambios de permisos globales. Ver CURRENT_STATE.md para el estado exacto.


## Bloque G — Implementación aprobada el 2026-09-13

Contrato y comandos: `docs/CORTE_SECUENCIAL.md`. Decisiones INF-008 e INF-012.
Los bloques A–F anteriores describen hitos históricos; no certifican el nuevo motor.

| Tarea | Dependencia | Aceptación | Estado |
|---|---|---|---|
| G1 Normalizar 001/002 e inventarios | Decisiones del usuario | Identidad de fila, números válidos, escala exacta | Implementado y probado |
| G2 Validador independiente | G1 | Demanda, etapas, capacidad, stock y métrica | 11 pruebas, 60 casos diferenciales |
| G3 AG secuencial con saldos agrupados | G2 | Herencia real, elitismo y evaluación igual al plan detallado | Implementado; 34 ensayos válidos |
| G4 Inventario importable/exportable | G3 | Roundtrip y saldo físico sin doble conteo | Integración aislada y artefactos 002 pasan |
| G5 Instantáneas, API y frontend | G4 | Carga, reproceso, inventario, estados y estimación | Build y E2E local pasan |
| G6 Comparación 002 y regresión 001 | G3 | Cinco semillas/perfil, métricas y código identificados | Piloto completado |
| G7 Actualizar tesis | G6 | Alcance y resultados contrastables, sin promesas no medidas | Capítulos 1–4 actualizados para revisión |
| G8 Despliegue local y E2E real | G5 + presupuesto autorizado | Migración, imágenes, HTTP/WS y artefactos de 002 | Completado: localhost:80, Chrome, dos versiones 002 auditadas |

No hacer commits ni descartar cambios previos. No repetir builds ni generar todos
los artefactos por semilla. El caso 683 queda fuera de la evaluación académica.


Cierre G: evidencia en `tests/benchmarks/2026-09-13-integracion-local.json`. Se
conservaron cinco versiones de 001 para calibrar la estimación, dos de 002 y una
carga técnica de reimportación. La VPS queda fuera de este cierre local.

Publicación G autorizada por el usuario el 2026-09-13: rama nueva, commit, push
y PR hacia production. No fusionar ni hacer push directo a production.

Actualización: PR #1 fusionado por el usuario; `production` local sincronizada con
origin en 33a5328. El usuario informa publicación en producción. El siguiente bloque
propuesto es cierre académico y reproducibilidad; todavía no autoriza implementar
nuevas funcionalidades ni modificar los supuestos del modelo.

## Bloque H — Ampliación aprobada tras G

La aprobación posterior «Implement the plan» reemplaza la restricción de alcance
del párrafo anterior. Decisiones funcionales explícitas consolidadas en INF-012.

| Tarea | Dependencia | Aceptación | Estado |
|---|---|---|---|
| H1 Contrato y referencias | Aprobación del usuario | Defaults editables, sin atribuirlos a una ley | Implementado |
| H2 Normalización y balance | H1 | Precisión exacta, exclusión inicial y validador independiente | Implementado y pruebas pasan |
| H3 Evaluación agrupada | H2 | Kerf y descarte por operación/etapa; objetivo global | Implementado; diferencial 100 casos pasa |
| H4 API e instantáneas | H2 | Compatibilidad, parámetros en ETA y reproceso preservado | Integración aislada pasa |
| H5 UI y artefactos | H3/H4 | Checks, trazabilidad y cuatro categorías de material | Implementado; tipos/lint pasan |
| H6 Evaluación 001/002 | H3 | Cuatro escenarios, cinco semillas/perfil y controles | Completada: 136 ensayos + 12 controles válidos; artefactos finales 001/002 pasan |
| H7 Coherencia académica | H6 | Capítulos y resultados sin extrapolación física | Capítulos 1–4 actualizados; revisión del director pendiente |
| H8 E2E de imágenes nuevas | H5/H6 y presupuesto de disco | Carga, WS, descargas, reproceso y auditoría | Completado: imágenes nuevas saludables, Chrome 002 id 38 y HTTP/WS 001 id 39; cuatro versiones auditadas |
| H9 Entrega revisable | H7/H8 | Diff y descripción de PR; sin merge automático | Commit 01c4dcc y push completados; creación de PR falla HTTP 401, pendiente gh auth login |

H6 cerrado: proceso de matriz con salida 0, 136 combinaciones únicas, 92/67.443
piezas exactas, una huella de código y balances auditados. Borrador de entrega:
`.claude/context/PR_BLOQUE_H.md`. No dejar la matriz como «en curso» al reanudar.

H8 cerrado tras autorización de reintento: C: 8,3 GB libres antes y después,
dependencias reutilizadas, build y 83 pruebas en imagen nueva pasan. Sin pendiente
de reconstrucción local. Permanecen revisión académica y publicación no solicitada.
