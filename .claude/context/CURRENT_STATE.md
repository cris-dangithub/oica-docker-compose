# Estado actual — 2026-10-03

## Documento Word de la tesis (`docs/tesis-doc/Tesis_F.docx`, 2026-10-03)

A pedido del usuario se generó `Tesis_F.docx` (61 páginas, sin commit) sobre la plantilla USCO
(`Downloads/Tesis.docx`): estilos, numeración de títulos, secciones, encabezados y logo de la
plantilla. Contenido: capítulos 1–4 de `docs/tesis-doc/*.md` reorganizados según la plantilla, más
un Cap. 5 de conclusiones **preliminares** por objetivo, dos anexos (cartillas anonimizadas y
evidencia) y bibliografía APA limitada a fuentes con ficha o marcadas «pendiente de verificación».
Del borrador «Tesis final 1» solo se tomó contexto cualitativo (motivación, clasificación 1D/2D,
arquitectura, tabla NSR-10 C.3.5.3-2 con masas verificadas); sus resultados no se usaron
(RIESGO-AC-010). Convenciones de la plantilla: decimales con punto, miles sin separador, márgenes
simétricos de 2.54 cm, capítulos en página impar. 15 «Nota pendiente» resaltadas marcan tareas del
autor. Generador y figuras en el scratchpad de la sesión (no versionados). Pendiente: procedencia de
la cartilla 001, revisión del director, fichas del software y de las fuentes heredadas.

## Bloque K — Alineación con el título fijo de la tesis (spec 001)

El usuario fijó el título palabra por palabra («Diseño y desarrollo de una aplicación web con
Inteligencia Artificial … con desperdicios admisibles mediante el enfoque basado en patrones de
corte y nesting»). INF-014 quedó [VALIDADA] con sus decisiones: umbral admisible ingresado por el
usuario, sin valor legal (no hay norma colombiana con un máximo); patrones de corte agregados y
cota Gilmore–Gomory como métrica; nesting lineal; 001/002 de una obra colombiana confidencial y
anonimizada.

El usuario aportó los objetivos vigentes (distintos de los del 13 de septiembre) y aceptó ajustar
su redacción. Cap. 1 §1.3 está actualizado con esa redacción, pendiente del director; el resto
del documento sigue sin tocar.

Spec Kit: constitución v1.0.0 ratificada (`.specify/memory/constitution.md`; prevalece sobre
AGENTS.md/CLAUDE.md). `specs/001-alineacion-titulo-tesis/` tiene spec, checklist, `plan.md`,
`research.md`, `data-model.md`, `contracts/` (http-api, artefactos, ui) y `quickstart.md`.
`.specify/feature.json` es local e ignorado: si falta, usar
`SPECIFY_FEATURE_DIRECTORY=specs/001-alineacion-titulo-tesis`.

Decisiones del plan (2026-10-02):
- Cota Gilmore–Gomory con scipy 1.18.1/HiGHS (rueda musllinux cp312 verificada en PyPI) y
  certificado lagrangiano (INF-016).
- Umbral en `execution_config.umbral_desperdicio_pct`, fuera de la huella, editable al
  reprocesar.
- Nueva página `/archivos/[id]`.
- Regresión repitiendo los 136 + 12 en el contenedor actual (sin evidencia nueva).
- INF-015 [PENDIENTE]: el umbral se compara con el desperdicio de INF-012.

**Spec 001 implementada (2026-10-02): 56/56 tareas de `tasks.md` completas.** Commit en la rama
`feat/spec-001-alineacion-titulo`, autorizado por el usuario. Push y **PR #5 hacia `production`** abiertos
(https://github.com/cris-dangithub/oica-docker-compose/pull/5). Sin merge ni despliegue: requieren una orden
explícita aparte.

Validación:
- **Pruebas**: 124, pasan dentro de la imagen nueva (con scipy 1.18.1) y con el código en memoria
  (`--container oica-validation-backend-1`; el worker no tiene `gevent`).
- **Regresión**: 0 diferencias en 148 registros
  (`tests/benchmarks/2026-10-02-regresion-analisis-1.jsonl`; la del MVP en `…-regresion-mvp-us1`).
- **Cota de los ensayos**: 148/148 con desperdicio ≥ cota y la cota ajustada; 002 con condiciones
  físicas tiene cota de 7,5958 % y brecha del AG balanceado de 1,30 pp (mediana), frente a 2,53 pp
  de FFD/BFD (`…-cota-ensayos.jsonl`).
- **E2E**: 67/67 comprobaciones contra el stack reconstruido. Para la UI se usó Playwright con
  `libgbm` extraído localmente en `tmp/` (sin instalar nada en el sistema): 12/12 pantallas
  correctas a 1440, 820 y 390 px, 0 violaciones axe y sin desbordamiento. Proyectos de QA
  44–47 eliminados; la base conserva sus 6 proyectos.
- **SC-005**: 13.955 barras se agrupan en 136 patrones (102,6 veces menos filas).
- **SC-007**: +8,8 % en una comparación intercalada con el código previo en el mismo contenedor
  (24,58 s frente a 26,75 s). Frente a la base de T002, medida con la imagen anterior, es +40 %,
  pero se debe a deriva del entorno: el código previo también tarda +28 %. Detalle en
  `tests/data/002/ANALISIS_RESULTADOS.md` §12.
- **T003**: NSR-10 verificada (Título C, Tabla C.3.5.3-2, p. C-47; el Título C no contiene
  «desperdicio»). INVIAS 640 e IDU sin copia oficial: **pedir los documentos al autor**.

Imágenes: reconstrucción única aprobada (14 m 55 s). Backend 627 MB y worker 604 MB (+150 MB cada
uno por scipy); frontend 229 MB. Se retiraron solo las tres imágenes huérfanas de OICA. Quedan
836 MB de caché de build, que acelera la próxima construcción. C: tenía 7,7 GB libres al cierre.

**PNG por piezas desplegado (2026-10-02, aprobado por el usuario).**
- Se reconstruyeron backend y worker solo en la capa de código (4,6 s, caché de pip reutilizada).
- 124 pruebas pasan dentro de la imagen.
- Una carga real de 002 (rápido, umbral 10 %) quedó «dentro de lo admisible», con 135 patrones y
  la cota calculada. Su PNG muestra cada pieza separada.
- Se retiraron el proyecto de QA 48 y las dos imágenes huérfanas.
- **Disco**: C: bajó de 7,7 a 4,4 GB libres sin causa atribuible a esta sesión; el disco de WSL
  apenas creció (21 GB usados). Vigilar antes de la próxima construcción.

Documento: Cap. 1 (título fijo, «web», procedencia), Cap. 2 §2.1, 2.4, 2.7 y 2.8, Cap. 3 §3.9,
Cap. 4 §4.10 y `docs/tesis-doc/Referencias.md` (15 fichas). Pendientes académicos: revisión del
director, INF-015 y fuentes sin verificar (RIESGO-AC-008).

`CLAUDE.md` quedó alineado con la constitución el 2026-10-02:
- monorepo y `services/` como copia histórica;
- worker con pool prefork;
- requisitos comunes más constraints;
- commits solo con orden explícita para esa ocasión;
- disco, puertas de calidad, Spec Kit y fuentes;
- BUG-002 y BUG-006 marcados como del motor histórico.

`AGENTS.md` y `HISTORICAL_CONTEXT.md` también quedaron alineados el 2026-10-02.

Fuentes verificadas:
- Res. 472/2017 y 1257/2021.
- **INVIAS 2022 art. 640**: el desperdicio va en el precio unitario (640.7) y no hay máximo; la
  Tabla 640-1 coincide con la NSR-10.
- **RECIAMUC 2022**: 6,77 % de desperdicio en una vivienda en Ecuador.
- Russell-Norvig: edición, sección y página.

PDF en `docs/tesis-doc/fuentes/`: se versionan la fe de erratas de INVIAS y RECIAMUC (1,6 MB). Las
especificaciones INVIAS completas (82 MB) quedan solo en local, ignoradas en `.gitignore`. Pendientes: IDU, la fuente de «nesting lineal» y las páginas de Holland y Goldberg
(préstamo en Internet Archive). Los cambios de fuentes en el Cap. 2 y en `Referencias.md` no tienen
commit (el PR #5 sigue abierto).

**Pregunta pendiente del usuario:** datos de compra reales (facturas o remisiones, al menos kg
por diámetro) de una obra colombiana para OE5. Mientras tanto, OE5 se evalúa con heurísticas y
cota (RIESGO-AC-009). La spec también contempla crear `docs/tesis-doc/Referencias.md`.

## Bloque J — Rediseño visual OICA (estado al 2026-09-29)

Discovery, auditoría AS-IS y tres direcciones visuales completadas sin cambiar
el lenguaje visual del frontend. Stack local saludable en http://localhost; se
capturaron rutas principales en desktop/tablet/mobile y se contrastó producción.
La auditoría Playwright/axe confirmó navegación y tabla móviles incompletas,
contraste insuficiente, controles sin nombre accesible, metadata/lang genéricos y
la imagen rota de la landing. Evidencia y estado persistente en
`docs/oica-redesign/`; riesgos en
`.claude/diagnostics/2026-09-29-redesign-ui-audit.md`.

El usuario aprobó **B — Industrial Clarity**, incorporando métricas
monoespaciadas y precisión geométrica de A. La decisión está registrada como
ADR-UI-004; foundations, paleta con pares AA, dimensiones y alcance v1 están
fijados en `docs/oica-redesign/DESIGN-SYSTEM.md` y `COMPONENT-MAP.md`. El ledger
de Figma es `FIGMA-STATE.json`.

**Code-first en curso (ADR-UI-006).** Migrados: tokens CSS/Tailwind, primitives
(`components/ui/`), `Navbar` responsive, `layout.tsx` (`lang="es"`, metadata,
`<main>`) y **todas las pantallas**: `/subir-cartilla`, `/archivos` (tabla/tarjetas
responsive, diálogos propios), inicio, tutorial y contacto. Tutorial corregido
(RIESGO-AC-007: se quitó "Método Búfalo" sin respaldo; masa #4 = 0,994 kg/m). QA 2026-09-29: typecheck, lint y build OK; axe-core
0 violaciones en 1440/820/390 px; sin overflow. Codex inició la fase C2 y se
cortó por límite de uso en C2.c; Claude Code la retomó y la cerró. Pendiente: limpieza
legacy, rebuild Docker (pedir aprobación por espacio en C:) y Figma. E2E real 2026-09-29 OK (estimar, enviar, WebSocket,
descargar, reprocesar, eliminar) con cartilla de prueba `qa-rediseno-*`, ya
eliminada; la base conserva sus 6 proyectos. El stack Docker local sigue con
la imagen anterior del frontend (no se reconstruyó).

Figma está conectado con la cuenta propietaria. Archivo `OICA — Product Design`:
https://www.figma.com/design/pQYp8TECtmWQLDcHISqfZP. Página de exploraciones
con A Precision Engineering, B Industrial Clarity y C CAD Control Room. Dos
lecturas posteriores a la aprobación —inspección programática y librerías— fueron
rechazadas antes de ejecutarse porque el plan Starter mantiene agotado el límite
MCP. **Bloqueo crítico:** renovar el cupo o ampliar el plan para completar Phase
0 y crear variables/componentes en Figma. La segunda conexión listada requiere
reautenticación y no se usó. No hubo escritura parcial en Figma ni despliegue. Con autorización explícita
del usuario (2026-09-29) el rediseño se publicó en la rama
`feat/rediseno-design-system` con PR hacia `production`. Se preservan todos los cambios ajenos existentes.

## Bloque I — Proxy Docker o Nginx del host

Implementación lista para revisión. El usuario autorizó commit, push y PR hacia
production el 2026-09-18; rama de entrega `feat/nginx-host-opcional`, basada en
production 89dbedd. Sin intervención en VPS.
Selector `OICA_PROXY_MODE=container|host` en `.env` local (usar
`bash scripts/compose.sh up -d --wait`) o shared/production.env para el pipeline.
Override host publica solo loopback 13000/15000. Operación, restauración,
rollback y renovación TLS adaptados; empaquetado CI incluye el override.
Plantilla host y guía añadidas. `PROMPT_VPS_NGINX.md` creado en raíz, ignorado
por Git y Docker. Se preservan todos los cambios ajenos, incluida la eliminación
previa de docs/METODOLOGIA.md.

Validación: 16 tests de operación con Docker/curl simulados pasan; Compose real
config valida servicios y puertos en ambos modos y producción host; sintaxis
Bash correcta. Sin builds, descargas ni cambios al stack local. C: dispone de
4,7 GB: evitar operaciones voluminosas. No se ha probado Nginx host en ejecución.
Pendiente operativo: configuración del sitio/certificados externos,
permisos mínimos del marcador y transición/validación E2E en la otra instancia.
Riesgo operativo en `.claude/diagnostics/2026-09-18-proxy-host.md`.

## Bloque H completado localmente — pérdida por corte y mínimo reutilizable

El usuario aprobó implementar la ampliación. Rama de trabajo:
`feat/perdida-corte-reutilizacion`, basada en production 33a5328. El usuario autorizó
commit, push y PR hacia production. Commit de implementación `01c4dcc` publicado
por SSH con seguimiento remoto. Tras renovar autenticación, se creó y verificó
el PR #2, abierto hacia production desde feat/perdida-corte-reutilizacion:
https://github.com/cris-dangithub/oica-docker-compose/pull/2
PR #2 ya fusionado en production (89dbedd); el trabajo del proxy continúa en feat/nginx-host-opcional. Conservados cambios ajenos.

Implementados parámetros canónicos HTTP, UI con ambos checks activos por defecto,
disco nominal 1 mm/cizalla idealizada 0 mm editables, mínimo automático fijo por
diámetro o manual común, descarte inmediato o al cierre de etapa, exclusión de
inventario inicial y balances separados. Motor `secuencial-2`, evaluación agrupada,
validador independiente, instantáneas y compatibilidad ideal. Sin nueva migración.

83 pruebas backend pasan con código cargado en memoria en Python 3.12 existente;
las siete de API se repitieron tras añadir auditoría del JSON persistido y pasan.
Tipos y lint frontend pasan sin emisión/caché. Matriz final **136/136 completa**,
proceso terminado con código 0, combinaciones únicas y balances globales auditados.
Se añadieron 12 controles válidos de cizalla y fin de etapa. Resultados definitivos:
`tests/benchmarks/2026-09-13-fisico-matriz-final.jsonl` y dos `fisico-control-*`.
002 con ambos checks: rápido 2,09–2,53 s, balanceado 5,31–6,20 s, profundo
10,85–15,50 s de motor; todas las ejecuciones conservan 67.443 piezas.
Máximo acumulado de memoria en la matriz: 115,55 MiB.

Artefactos finales generados y reimportados: 001 95.090 bytes; 002 1.619.999 bytes,
con siete hojas Excel, PDF/PNG acotados e inventario válido. Temporales retirados
por el runner, resumen `2026-09-13-fisico-artefactos-final.jsonl` conservado.
Se auditó además el archivo antiguo id 36 desde PostgreSQL y Excel, cargando el
validador nuevo solo en memoria: sus dos versiones conservan demanda, inventario
y métricas. No se modificaron registros históricos ni se cargaron proyectos nuevos.
Capítulos 1–4 actualizados; 4.8 distingue la matriz nueva del E2E anterior.

**secuencial-2 está activo en http://localhost.** Tras «Vuelve a intentarlo», C:
tenía 8,3 GB libres. Se reconstruyeron las tres imágenes con dependencias en caché
y se activaron juntas; seis servicios saludables, migrador finalizado. Build,
tipos/lint y 83 pruebas dentro de la imagen nueva pasan. No se cambió el esquema.

E2E Chrome Windows: 002 id 38, checks activos y mínimos automáticos visibles,
carga balanceada (18,01 s registrados), reproceso profundo (24,77 s), 33 frames WS,
cero excepciones JS y ocho descargas válidas (cuatro por versión). Las dos versiones
pasan auditoría independiente de JSON/Excel, incluidas pérdida, descarte y saldo.
001 id 39 pasa HTTP, polling, WS, filtros, reportes y reproceso; dos versiones
auditadas con 92 piezas. Instantáneas idénticas entre versiones en ambos archivos.
También se auditó id 36 histórico: dos versiones conservadas sin cambios.
Evidencia: `2026-09-13-fisico-navegador-002.json`, `2026-09-13-fisico-http-001.json`
y `2026-09-13-fisico-integracion-local.json` en tests/benchmarks/.

El bloqueo previo de 2 GB quedó resuelto; no se determinó la causa de la variación
del espacio disponible. Al cierre siguen aproximadamente 8,3 GB libres en C:.
Se reutilizaron todas las dependencias; no hubo limpiezas globales ni cambios de
filesystem o volúmenes. Chrome se cerró y solo se retiró su propio perfil temporal
con la autorización del ensayo. Las cuatro versiones nuevas se conservaron.
No hay preguntas funcionales críticas pendientes; las referencias no sustituyen
calibración física ni revisión del director. Decisiones consolidadas en INF-012.

El registro G siguiente es histórico: sus supuestos ideales siguen disponibles
como control, pero ya no son los únicos parámetros aprobados para nuevas cargas.

## Actualización de publicación

El PR #1 fue fusionado en `production` (33a5328), confirmado por Git remoto.
La rama local volvió a `production` y se actualizó por fast-forward conservando
los cambios ajenos pendientes. El usuario informa que ya quedó subido en producción;
esta sesión no comprobó independientemente el despliegue de la VPS.
Siguiente dirección recomendada: validar supuestos con el director/ingeniero civil,
documentar procedencia de 001/002 y cerrar evaluación reproducible y tesis.

## Bloque G: implementación y validación local completadas

El usuario autorizó implementar el plan y después reconstruir las imágenes con
un presupuesto estimado de 2–4 GB. La aplicación nueva está activa y saludable en
**http://localhost**, proyecto Compose `oica-validation`. `.env` local (ignorado por
Git, sin secretos añadidos) conserva ese nombre y puerto 80 para los comandos habituales.
El usuario autorizó publicar esta entrega en una rama nueva y abrir PR hacia
`production`, reemplazando la petición de push directo. No fusionar el PR ni
desplegar sin nueva instrucción. La VPS no se operó directamente en esta sesión.

### Contrato aprobado

Solo 001/002 como corpus académico; AG; etapas sucesivas con reutilización acumulada
por diámetro; catálogo editable e inventario XLSX/CSV; exportación compatible;
pérdida por corte cero, sin mínimo reutilizable; desperdicio final ponderado por
masa de barras utilizadas una sola vez. 1–5 minutos como objetivo, sin aborto.
Título y objetivos reformulados por autorización del autor, pendientes del director.

### Implementado

- `backend/cutting/`: normalización, validador independiente, AG con evaluación de
  saldos agrupados, trazabilidad por barra y reportes acotados.
- API/worker con instantáneas, tarea activa, reimportación de inventario y estimación.
- Frontend con catálogo, inventario, progreso y descargas.
- Migración 003 aplicada a PostgreSQL local. Los volúmenes y dos versiones previas
  del archivo histórico id 2 permanecen intactos.
- Capítulos 1–4 y `docs/CORTE_SECUENCIAL.md` contrastados con el piloto y el E2E local.

### Evidencia verificada

- Build de las tres imágenes exitoso, incluyendo compilación/tipos/lint de frontend.
- 74 pruebas backend pasan dentro de la imagen nueva; 10 de scripts pasaron antes.
- 34 ensayos de motor válidos; 002 rápido 1,38–1,51 s, balanceado 3,13–3,79 s,
  profundo 5,65–9,15 s. Son tiempos de motor, no de aplicación.
- Chrome real Windows: 002 cargado, progreso y WebSocket, redirección a resultados,
  descargas Excel/PDF/PNG/inventario y reprocesamiento desde la tabla; sin errores JS.
- 002 id 36: v1 balanceado 9,76 s registrados, 7,995 %; v2 profundo 19,97 s,
  7,934 %. La espera medida en navegador para la primera carga fue 20,15 s.
- Ambas versiones pasan auditoría independiente desde JSON persistido y Excel:
  67.443 piezas, diámetros, etapas, capacidad, inventario y métricas exactos.
- 001 id 35 (nombre técnico smoke.xlsx): cinco versiones conservadas; HTTP, WS,
  descargas/reproceso y estimación empírica con cinco muestras (1,04–2,94 s).
- Control de reimportación id 37: consume una pieza #3 de 0,01 m del inventario
  exportado por 002 sin catálogo comercial y conserva exactamente los saldos.
  Es una prueba técnica; no un tercer caso académico ni validación física.

Evidencia: `tests/benchmarks/2026-09-13-integracion-local.json`, resultados de navegador,
series JSONL, captura, huellas de imágenes y freeze de dependencias. La serie anterior
`secuencial.jsonl` es diagnóstica incompleta; la serie final es `agrupado.jsonl`.
Auditoría reproducible: `scripts/verify_sequential_result.py`.

### Pendientes reales

Procedencia y permisos de redistribución de 001/002; licencia de distribución;
revisión bibliográfica y del director; reproducción en otra máquina. Sin certificado
de optimalidad ni validación física del modelo ideal. La captura evidencia mejoras
pendientes de contraste y ancho de tabla; no se amplió esta entrega con cosmética.
No hay una pregunta técnica de alta prioridad que bloquee el uso local actual.

### Almacenamiento y preservación

C: pasó de aproximadamente 8,0 a 7,5 GB libres; sigue al 99 %. No confundir la
capacidad virtual WSL con espacio físico. Se reutilizó caché; algunas capas Python
necesitaron completarse. Se registraron versiones instaladas para la reproducibilidad.
No hubo limpiezas globales, cambios de filesystem ni reinstalación del entorno.
Chrome de prueba cerrado y únicamente su perfil temporal retirado; contenedores
de la app siguen activos. El PostgreSQL antiguo `oica_postgres` sigue detenido.

Preservados `services/`, datasets, borrado previo de `docs/METODOLOGIA.md` y archivos
ajenos sin seguimiento, incluido `tests/data-tests.zip`. No hacer commits sin permiso.

## Registro anterior de producción (histórico, no describe el bloque activo)

# Estado actual del proyecto

> Actualizado: 2026-09-12, reanudación después de reparación de WSL con e2fsck.
> Bloque activo: F — Producción, CI/CD y desarrollo nativo.

## Objetivo y estado real

El código del monorepo, Compose, proxy, workflows y scripts de operación está implementado. **No declarar producción desplegada ni validación final completa**: falta el despliegue en la VPS. Los ensayos reales de recuperación pasaron en GitHub Actions 34691570574. El build final, los tests y el E2E pasaron en GitHub Actions (34686626604).

## Restricción urgente de almacenamiento

El usuario exige comprobar espacio antes de operaciones costosas y detenerse/avisar con una estimación antes de builds, instalaciones o generación significativa de datos. No ejecutar limpiezas destructivas, cambios de filesystem, mounts ni permisos globales sin autorización explícita.

Lecturas tras la reparación:

- WSL: disco virtual de 1007 GB, 37 GB usados, 920 GB disponibles.
- Windows C: 442 GB, 436 GB usados, **6 GB libres, 99 % ocupado**.
- Windows D: 26 GB, 19 GB usados, 7,8 GB libres.
- Docker: 10,75 GB en imágenes, 4,62 GB de caché de build, 255,8 MB de volúmenes. No sumar categorías como si no compartieran capas.
- Frontend local: 481 MB de node_modules y 152 MB de .next; se reutilizaron para verificaciones sin caché.

No se conoce aquí la ubicación física exacta del VHDX ni la causa del fallo. No inferir capacidad física a partir del espacio virtual. Desde la reanudación no se construyeron imágenes, instalaron dependencias, borraron datos ni cambiaron permisos/montajes de carpetas. actionlint se ejecutó con imagen existente, sin red ni bind mounts; las pruebas de scripts usaron archivos temporales pequeños.

## Trabajo implementado

- Código local migrado a `backend/` y `frontend/`, incluyendo correcciones anteriores sin commit. `services/` preservado intacto como copia histórica.
- Se retiraron solo los dos gitlinks del índice. Rama local: `production`, siguiendo `origin/production`.
- Fast-forward a e8fa70a incorporó dos commits remotos de documentación. Con aprobación del usuario se creó el commit 0330943 de implementación. El push falló por falta de credenciales HTTPS y el token de gh es inválido. Posteriormente se publicó por SSH y el usuario cambió la rama predeterminada a production, confirmado mediante API pública.
- Compose: Nginx, Next.js, Flask, Celery, PostgreSQL, Redis y migrador temporal. Puerto predeterminado 80; API relativa /api y Socket.IO /socket.io.
- Imágenes con código, sin montajes de fuentes; secretos externos, volúmenes persistentes y requisitos Python fijados. Dockerfiles finales eliminan compiladores temporales; su build se completó en GitHub Actions.
- Next.js 15.5.25 y overrides compatibles de seguridad. npm audit reportó cero vulnerabilidades antes del incidente.
- CI construye/verifica cada imagen una vez y publica exactamente esa imagen. Entregas SHA-RUN_ID, SSH, rollback, reset con confirmación y respaldo configurable.
- Desarrollo nativo Linux/WSL: setup-dev.sh y dev.sh. La instalación completa no se ejecutó: Python 3.12 no estaba en PATH; Node local predeterminado es 24, aunque los builds Docker usaron Node 22.
- Corrección pequeña del motor: rechazar entrada vacía con ValueError para cumplir su test existente. No se alteró la optimización de cartillas válidas.
- Página legacy /resultados redirige a /archivos. Polling revisa periódicamente pérdida de progreso; fallos de reset/restauración conservan mantenimiento.

## Verificación

Antes de la reparación:

- 58 tests del algoritmo: OK tras validar entrada vacía.
- Build Next.js: OK con Node 22; versiones intermedias de las imágenes arrancaron saludables.
- E2E: carga, progreso WebSocket, polling, filtros, Excel/PDF/PNG, reprocesamiento y borrado: OK.
- Se conservó la cartilla smoke (id 2, dos versiones) para comprobar persistencia.

Después de la reparación:

- 58 tests del algoritmo: repetidos con éxito en el contenedor existente, cargando la validación del motor en memoria y sin modificar sus fuentes/datos.
- Diez tests de seguridad de scripts: OK (Docker simulado, sin tocar contenedores reales).
- TypeScript sin emisión/incremental, ESLint sin caché, sintaxis Bash y AST Python: OK.
- Workflows revisados con actionlint usando imagen existente.
- Stack `oica-validation` activo y saludable en **http://localhost:8088**. El stack antiguo `oica-app` quedó detenido tras el incidente; sus contenedores y volúmenes se conservan.
- Lectura de la BD y los archivos: dos versiones conservan demanda, separación por diámetro, conservación de longitud y firmas de los tres artefactos.

Las imágenes Python activas no deben considerarse la validación del código final de Dockerfiles/constraints. No se migró aún el stack al puerto 80. No se hicieron ensayos destructivos reales de reset/restauración ni se emitió certificado público.

## Pendiente para cerrar F

Seguimiento: 34691155372 confirmó arranque de Nginx y E2E, pero falló la comprobación de interrupción de un reprocesamiento en cola. server.py conservaba completed al encolar; interrupt_jobs.py no podía reconocer la tarea pendiente. Corregido en f2a6692: persistir pending antes de publicar en Celery y recuperar estado anterior si falla el envío. Dos comprobaciones aisladas en memoria confirmaron ambos casos. CI 34691570574 completó correctamente toda la validación y recuperación. El job deploy falló en Transferir y actualizar; falta preparar VPS según último estado del usuario y obtener diagnóstico de transferencia si persiste. Los diagnósticos de CI ahora se emiten por servicio en anotaciones cortas.

Datos confirmados por el usuario para la VPS 169.58.196.25: Ubuntu 24.04.4, x86_64, Compose v5.5.0, 172 GB libres, sin contenedores activos y puertos 80/443 libres. No se ejecutó bootstrap. Correo TLS autorizado: cristiandaniel8080@gmail.com. DNS del dominio resuelve a la IP esperada. El acceso SSH a la VPS está en otra instancia de WSL. CI 34690720017 pasó build y pruebas, pero falló en el arranque de Nginx del ensayo de recuperación; anotación pública truncada, se solicitó al usuario el final del log. No hubo despliegue ni cambios en la VPS.

El usuario autorizó commit y push. La publicación se completó usando Git por SSH: origin ahora es git@github.com:cris-dangithub/oica-docker-compose.git y production se publicó con los commits 0330943 y 7b77062. El token de gh sigue inválido, pero no impide operar Git por SSH. El usuario informa que configuró los secretos; falta comprobar la ejecución del pipeline y el despliegue. La rama predeterminada remota ya es production. La ejecución 34686626604 pasó build, tests, arranque, migraciones, E2E y publicación GHCR; falló el ensayo de recuperación y no desplegó. Se corrige la herencia de HTTP_PORT=8080 del runner para que el ensayo use 8081 y se añaden anotaciones públicas del diagnóstico. Se corrigió `.gitignore` para excluir solo `/app/` en la raíz y conservar `frontend/src/app/` en la entrega.

1. Continuar las validaciones en GitHub; compilación final completada allí. No construir localmente.
2. Imágenes finales, migraciones repetibles y recuperación validadas en el runner desechable (34691570574). No repetir localmente.
3. Configurar SSH, GHCR y secrets/environment GitHub; comprobar arquitectura x86_64, distribución, espacio y puertos reales de la VPS.
4. Publicación y rama predeterminada production completadas; commits y push autorizados por el usuario.
5. Preparar HTTPS para oica.cris-munoz.me y efectuar el primer despliegue vacío.

## Contexto académico preservado

Bloques A/B/C completados. Test 002 completó rápido, balanceado y profundo; balanceado obtuvo mejor eficiencia, y profundo sigue afectado por BUG-006. BUG-002 y BUG-006 continúan pendientes. D depende de INF-008 (reutilización de desperdicios). INF-011 valida el cambio a monorepo y operación en VPS.

Los commits incorporados ampliaron Cap. 4 a 212 líneas; la antigua afirmación «Cap. 4 vacío» está desactualizada. Su revisión académica queda fuera de este bloque, sin inventar completitud ni validar resultados por inferencia.

Guía operativa: `docs/DEPLOYMENT.md`. Diagnóstico y riesgos: `.claude/diagnostics/2026-09-12-produccion.md`.
