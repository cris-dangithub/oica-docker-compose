# Plan de Trabajo — OICA Tesis

> **Última actualización:** 2026-10-04
> **Estado global:** Motor secuencial validado; dirección visual aprobada y Design System v1 en preparación
> **Bloque activo:** N — Corpus ampliado con cartillas sintéticas (rama `feat/cartillas-sinteticas`); M en curso

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
| J | Rediseño visual y Design System | Dirección B aprobada; implementación code-first autorizada | ALTA |
| K | Alineación con el título fijo (spec 001) | ✅ Cerrada (2026-10-04): en producción; queda la redacción de fuentes pendientes | ALTA |
| L | Presentación de resultados y explorador de patrones (spec 002) | ✅ Cerrada (2026-10-04): en producción con el PR #7 | ALTA |
| M | Tesis tras la spec 002 (capítulos 3 y 4, cifras con punto decimal) | 🔄 En curso | ALTA |
| N | Corpus ampliado: cartillas sintéticas 003 y 004, procedencia de 001 y 002 | 🔄 En curso: cartillas generadas, en revisión (CP-1) | ALTA |

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
| H9 Entrega revisable | H7/H8 | Diff y descripción de PR; sin merge automático | Commit y push completados; PR #2 abierto y verificado hacia production, sin fusionar |

H6 cerrado: proceso de matriz con salida 0, 136 combinaciones únicas, 92/67.443
piezas exactas, una huella de código y balances auditados. Borrador de entrega:
`.claude/context/PR_BLOQUE_H.md`. No dejar la matriz como «en curso» al reanudar.

H8 cerrado tras autorización de reintento: C: 8,3 GB libres antes y después,
dependencias reutilizadas, build y 83 pruebas en imagen nueva pasan. Sin pendiente
de reconstrucción local. Permanecen revisión académica y publicación no solicitada.


## Bloque I — Proxy Docker o Nginx del host

- [x] Selector de env con modo container por defecto y host con puertos loopback.
- [x] Adaptar despliegue, recuperación/restauración, rollback, TLS y paquete CI.
- [x] Guía y plantilla del sitio externo; prompt local excluido de Git.
- [x] Validar configuración Compose y 16 pruebas con Docker simulado sin builds.
- [x] Publicación autorizada por el usuario; rama de revisión `feat/nginx-host-opcional`.
- [ ] Agente con SSH: configurar sitio, TLS, acceso al marcador y validar transición.

Aceptación final: HTTPS/API/Socket.IO/artefactos y mantenimiento operativos con
host, otros sitios intactos y actualización normal sin Nginx Docker ni pérdida
de volúmenes. Este criterio requiere pruebas en VPS, aún no realizadas.

## Bloque J — Rediseño visual y Design System

**Objetivo:** reemplazar el lenguaje visual actual por un sistema coherente,
accesible, responsive, mantenible y sincronizado entre Figma y código, sin alterar
la funcionalidad ni los contratos del optimizador.

- [x] Verificar capacidades, conexión y skills de Figma.
- [x] Crear estado persistente en `docs/oica-redesign/`.
- [x] Inventariar frontend, rutas, estados, estilos y componentes.
- [x] Levantar/validar OICA y capturar baseline desktop/tablet/mobile.
- [x] Ejecutar auditoría inicial de accesibilidad con axe-core.
- [x] Clasificar componentes KEEP/REFACTOR/MERGE/REPLACE/REMOVE.
- [x] Crear archivo `OICA — Product Design` y tres exploraciones visuales.
- [x] Aprobar dirección: B Industrial Clarity con rasgos de precisión de A.
- [x] Fijar arquitectura de tokens, foundations y alcance de componentes v1.
- [x] Autorizar implementación code-first y sincronización posterior de Figma.
- [x] Crear foundations, tokens y primitives del Design System v1 en código.
- [ ] Crear patrones de producto y pantallas en Figma.
- [x] Migrar tokens, componentes y pantallas en código (todas las rutas, 2026-09-29).
- [ ] Completar QA visual, responsive, accesibilidad y regresión.
- [ ] Limpiar únicamente CSS/componentes/assets demostrablemente obsoletos.

**Limitación operativa:** el plan Figma Starter agotó el cupo MCP. La inspección
y consulta de librerías fueron rechazadas antes de ejecutar cambios. Por decisión
del usuario se continúa code-first con la especificación versionada y se
sincronizará Figma después; Figma sigue siendo un criterio final.

## Bloque K — Alineación con el título fijo de la tesis (spec 001)

**Objetivo:** dar respaldo verificable en la app y en el documento a cada término del título
fijo, sin alterar el plan de `secuencial-2` (constitución v1.0.0).

- [x] Ratificar la constitución de Spec Kit (v1.0.0, 2026-10-02).
- [x] Especificación `specs/001-alineacion-titulo-tesis/spec.md` y checklist.
- [x] Plan y diseño: `plan.md`, `research.md`, `data-model.md`, `contracts/` y `quickstart.md`.
- [x] Tareas (`/speckit-tasks`): `tasks.md`, 56 tareas (T001–T056), ajustadas tras `/speckit-analyze`.
- [x] Base sin scipy: patrones, admisibilidad, compra, NSR-10 y pruebas; regresión 136 + 12.
- [x] Integración en worker, API y artefactos; frontend `/archivos/[id]`.
- [x] Aprobación de espacio y reconstrucción con scipy; cota, `cota_ensayos.py` y SC-007.
- [x] E2E local según `quickstart.md`.
- [x] `Referencias.md`, capítulos 1–4 y archivos de control (US6).
- [x] Reconstruir backend y worker solo en la capa de código para desplegar el PNG por piezas (aprobado y desplegado el 2026-10-02).
- [x] INF-015 cerrada por el autor (2026-10-03): el umbral se compara con el desperdicio total.
- [x] Verificación de INVIAS 640 y Res. 472/1257.
- [ ] Revisión del director (objetivos); verificar IDU y la fuente de «nesting lineal».

**Pendiente del usuario o el director:** datos de compra reales para OE5 (RIESGO-AC-009).

## Bloque L — Presentación de resultados y explorador de patrones (spec 002)

**Objetivo:** reorganizar lo que ve el usuario (Excel, PDF e imagen) y mostrar en la web
**todos** los patrones de corte del proyecto de forma interactiva, sin alterar el plan de
`secuencial-2`. Así se respaldan «patrones de corte» y «nesting» del título ante el taller y el
jurado.

- [x] Especificación, plan, research, data-model, contratos, quickstart y tareas de la spec 002
  (2026-10-03, autora LizethGasca; rama `feat/spec-002-presentacion-resultados`).
- [x] Enmienda del 2026-10-04 aprobada por el usuario:
  - el explorador interactivo de todos los patrones sustituye la sección estática de los diez
    más repetidos;
  - solo visualización: el chequeo de taller queda fuera;
  - prioridad P2.
- [x] `/speckit-clarify` (5 preguntas), con estas decisiones:
  - se retira `analisis-2`;
  - escala común;
  - rangos de barras por tramos de 100;
  - orden del Excel con selector;
  - filtro por pedido con sugerencias.
- [x] `/speckit-plan`: R-16 a R-19 y la ruta de solo lectura `GET /patrones/<uuid>`, que
  reconstruye los patrones desde `resultados` sin ejecutar el AG. La medición exploratoria da
  unos 0,5 s para la 002 (136 patrones y 13.955 barras).
- [x] `/speckit-tasks` (48 tareas) y `/speckit-analyze`, con 5 hallazgos corregidos:
  confidencialidad de pedidos, planes no verificados, suma por pedido, medición sin reconstruir
  y lista por tramos.
- [x] Integración de `production` (cierre de la spec 001) en la rama de la spec 002.
- [x] `/speckit-implement` (2026-10-04): las cinco historias están implementadas.
  - **Backend**: 164 pruebas OK.
  - **Regresión**: 0 diferencias en 148 registros.
  - **SC-007**: ratio 1,07.
  - **SC-009**: 0,47 s.
  - **Frontend**: typecheck, lint y build OK.
  - **Despliegue**: 16 pruebas OK.
  - **Revisión manual** de Excel, PDF y PNG de la 001 y la 002 (§13 de la 002).
- [x] T047 (2026-10-04, aprobado):
  - imágenes reconstruidas;
  - E2E por API con 0 fallos;
  - auditor OK;
  - UI con 51 comprobaciones, 0 fallos y axe en 0 violaciones en 3 anchos;
  - proyectos de QA e imágenes huérfanas retirados.
- [x] Enmienda 2 (2026-10-04, pedida por el usuario): estándar numérico único en toda la app
  (FR-032 a FR-035, R-20).
  - Flujo: spec y diseño, `/speckit-converge` (T049 a T055) y `/speckit-implement`.
  - Verificación: 167 pruebas OK; QA de las 6 pantallas sin fallos; pantalla, PDF y «Resumen»
    coherentes.
- [x] Enmienda 3 (2026-10-04, decisión del usuario): punto decimal y sin separador de miles en toda
  la app, por coherencia con la plantilla USCO.
  - Flujo: spec y diseño, `/speckit-converge` (T056 a T061) y `/speckit-implement`.
  - Stack reconstruido; QA de las 6 pantallas sin fallos.
- [x] Commit y push a la rama del PR #7, y título y descripción del PR actualizados, por
  instrucción del usuario.
- [x] PR #7 fusionado por el usuario en `production` (`5b1e2d5`, 2026-10-04). «Publicar
  producción» terminó con éxito.
  - Verificado en https://oica.cris-munoz.me: inicio 200, `GET /api/patrones/<uuid>` existe (404
    con un uuid inexistente) y las cifras van con punto decimal.
- [x] Cierre documental: la spec pasa a «Implementada y cerrada» (commit directo a `production`,
  por instrucción del usuario).

## Bloque M — Tesis tras la spec 002

**Objetivo:** que el documento describa lo que la app ya hace y use el mismo formato numérico que
la app y la plantilla USCO.

- [ ] Cifras de los capítulos 1 a 4 a punto decimal y sin separador de miles. Los valores no
  cambian; los números de sección, las normas y los años no se tocan.
- [ ] Cap. 3: reescribir §3.8 (Excel de 13 hojas, PDF, PNG y formato numérico), corregir §3.9
  «Dónde se presentan» (con el explorador de patrones) y añadir a §3.2 la ruta de solo lectura.
- [ ] Cap. 4: nueva §4.11 con la validación de la spec 002 (regresión 0/148, SC-007, SC-009, E2E
  y QA), y una aclaración de fecha en las «siete hojas» del Excel de 2026-09-13.
- [ ] Regenerar `Tesis_F.docx` desde los `.md` actualizados. Su generador no se versionó.
- [ ] RIESGO-AC-010 (borrador «Tesis final 1»): pendiente del autor.

## Bloque N — Corpus ampliado con cartillas sintéticas

**Objetivo:** que el análisis de resultados cubra tamaños intermedios de cartilla (OE2: tiempo
según el tamaño) y mezclas de diámetros que 001 y 002 no tienen, y corregir la procedencia de 001.
Decisiones del usuario del 2026-10-04 en INF-017; supuestos de despiece en INF-018. El motor no
cambia. Rama `feat/cartillas-sinteticas`, creada desde `origin/production` (`f9599a0`).

- [x] Procedencia aclarada: 002 es un proyecto real con cartilla de un proveedor de acero (anónimo);
  001 es un ejercicio del curso Construcción de edificaciones. Sin datos de compra (RIESGO-AC-009
  aceptado como limitación).
- [x] NSR-10, Título C, verificada para ganchos, recubrimientos, traslapos y separaciones DMO:
  fichas REF-NSR10-GANCHOS-RECUBRIMIENTOS, REF-NSR10-EMPALMES y REF-NSR10-DMO. Ficha
  REF-CARTILLA-001 con los datos del curso pendientes.
- [x] Generador determinista `scripts/generar_cartillas_sinteticas.py` y pruebas
  `tests/cartillas/` (9 OK, `PYTHONUTF8=1 python -m unittest discover -s tests/cartillas -v`).
- [x] Cartillas generadas, con su `MEMORIA_DESPIECE.md`:
  - 003 vivienda: 38 filas, 2958 piezas, #3 a #5, 5 etapas.
  - 004 edificio: 105 filas, 18782 piezas, #3 a #7, 11 etapas.
- [x] **CP-1:** el usuario aprobó las dos cartillas (2026-10-04); INF-018 validada y entradas
  congeladas. Ficha REF-CARTILLA-001 con docente, programa y universidad; falta el periodo.
- [x] **CP-2:** imagen del worker `oica-worker:local` (`a7823883f0cd`, 858 MB; el disco de Docker
  pasó de 1.3 a 2.83 GB) y contenedor suelto `oica-experimentos`. En Windows, siempre `PYTHONUTF8=1`.
- [x] 003 y 004 en `DATASETS`; pruebas de humo válidas; `--artifacts-smoke` correcto
  (`2026-10-04-sinteticas-artefactos.jsonl`); sonda de tiempo: profundo sobre 004 en 9.2 s.
- [x] Matriz única de las 4 cartillas (`2026-10-04-tamano-matriz.jsonl`, 272 registros válidos,
  15 min), controles de 003 y 004 (12 registros), reproducibilidad de los controles (0
  diferencias) y cota (`2026-10-04-cota-tamano.jsonl`, 284 registros, ninguno por debajo). Los 136
  registros de 001 y 002 coinciden con la línea base salvo los tiempos.
- [x] `scripts/resumir_tamano_tiempo.py` y `tests/benchmarks/2026-10-04-tamano-tiempo.json`.
- [ ] **CP-3:** revisión del usuario de `tests/data/003/ANALISIS_RESULTADOS.md` y
  `tests/data/004/ANALISIS_RESULTADOS.md` (redactados).
- [ ] Capítulos 1, 3 y 4 (§4.12 cartillas sintéticas y §4.13 tiempo según tamaño, después de la
  §4.11 del Bloque M), RIESGO-AC-008, nota de procedencia en `tests/data/001/`, CLAUDE.md, AGENTS.md
  y `docs/CORTE_SECUENCIAL.md`.
- [ ] **CP-4:** revisión del Markdown y luego `Tesis_F.docx`, idealmente junto con el Bloque M.
