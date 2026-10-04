# Estado persistente del rediseño de OICA

> Actualizado: 2026-10-04

## Fase actual

**Design System v1 — code-first.** Foundations, primitives, navegación y la
primera pantalla (`/subir-cartilla`) están migradas y validadas (typecheck,
lint, build y QA con axe-core en tres viewports). `/archivos`, inicio, tutorial y contacto también migradas:
**todas las pantallas están en el Design System v1**. Siguiente: limpieza legacy,
reconstrucción de la imagen Docker y sincronización con Figma.
Figma sigue pendiente por cuota MCP (ADR-UI-006).

Continuidad: la fase C2 la inició Codex y se interrumpió por límite de uso en
`C2.c`; Claude Code la retomó y cerró C2.c–C2.e el 2026-09-29.

## Fases terminadas

- Preparación de capacidades: skills `figma-use`, `figma-create-new-file`, `figma-generate-design`, `figma-generate-library` y `figma-design-to-code` verificadas y leídas.
- Figma conectado con la cuenta de Cristian Daniel Muñoz Quintero y plan personal Starter.
- Discovery del frontend, rutas, estados, dependencias y stack local.
- Baseline visual local en desktop, tablet y mobile; contraste con producción.
- Auditoría automatizada inicial con Playwright y axe-core.
- Inventario y clasificación de componentes.
- Tres direcciones visuales creadas sobre la misma pantalla representativa.
- Dirección B aprobada y registrada en `DECISIONS.md`.

## Dirección aprobada

**B — Industrial Clarity**, con numerales monoespaciados y precisión geométrica
de A. Ver `DESIGN-DIRECTION.md` y ADR-UI-004.

## Archivo de Figma

- Nombre: `OICA — Product Design`
- URL: https://www.figma.com/design/pQYp8TECtmWQLDcHISqfZP
- File key: `pQYp8TECtmWQLDcHISqfZP`
- Página de exploraciones: `00 — Exploraciones` (`3:2`)
- Comparación: `Direcciones visuales — Configurar optimización` (`3:3`)
- Direcciones: A (`5:10`), B (`5:113`), C (`5:216`)

## Blockers

- El plan Figma Starter mantiene agotado el límite de llamadas MCP. La primera
  inspección posterior a la aprobación fue rechazada antes de ejecutar código;
  no hubo escritura parcial. Hace falta esperar la renovación del cupo o ampliar
  el plan para crear foundations, variables y componentes en Figma.
- La segunda conexión Figma disponible requiere reautenticación y no corresponde
  usarla para el archivo sin verificar su identidad. La conexión propietaria
  válida es la de `cristiandaniel8080@gmail.com`.

## Pantallas migradas

- `/subir-cartilla` (FileUpload, CuttingOptions, PhysicalOptions, TimingInfo).
- `/archivos` (FilesTable: filtros, tabla desktop, tarjetas mobile, diálogos, paginación).
- `/` inicio (hero, diagrama ilustrativo de corte, flujo, capacidades; sin imagen remota).
- `/tutorial` (h1, navegación interna, pasos, tabla de perfiles, glosario, FAQ desplegable).
- `/contact-us` (tarjetas del equipo, formulario con labels; mismo Formspree).

## Componentes migrados

- Foundations: tokens CSS semánticos en `globals.css` y mapeo en `tailwind.config.ts`.
- Primitives: `Button`, `Card`, `Alert`, `Badge`, `Progress`, `Input`, `Select`,
  `Textarea`, `Field`, `CheckboxField`, `Dialog` (`components/ui/`). `Progress` admite `hideLabel`.
- Shell: `Navbar` responsive con menú móvil; `layout.tsx` con `lang="es"`,
  metadata real y landmark `<main>`.
- Detalle del proyecto (spec 002): explorador de patrones (`components/file-detail/patterns/`),
  totales de compra en `PurchaseSummary` y `QualitySection` sin la tarjeta de cota simple. Tokens
  nuevos `color/data/stage-1…6` (documentados en `DESIGN-SYSTEM.md`). Pendiente en Figma (regla
  13) mientras siga bloqueado el cupo MCP.

## Tareas pendientes

1. Limpieza legacy (paso 8 de `MIGRATION.md`).
2. Reconstruir la imagen Docker del frontend (requiere estimar espacio en C: y aprobación).
3. Cerrar Phase 0 de Figma y sincronizar foundations cuando se renueve el cupo.
4. Completar las demás pantallas y estados.
5. Crear componentes/patrones equivalentes en Figma.
6. Ejecutar QA visual, responsive, accesibilidad y regresión.

## Último QA realizado

### 2026-10-04 — explorador de patrones (spec 002)

- typecheck, lint y build OK con Node 22; imágenes reconstruidas con aprobación.
- **axe-core**: 0 violaciones en 1440, 820 y 390 px, con la lista y con el detalle desplegado,
  sobre la cartilla 002 (135 patrones).
- **Teclado**: Enter abre el detalle y «Cerrar detalle» devuelve el foco a la fila.
- Sin desbordamiento horizontal ni errores de consola.
- Capturas fuera del repositorio (`tmp/qa-spec002/`).
- **Coma decimal en toda la app** (decisión del usuario, 2026-10-04): el detalle del proyecto y
  la lista `/archivos` usan coma decimal y punto de miles, con ayudantes `decimal`/`entero` en
  `file-detail/types.ts`.
  - QA con un `build` local detrás de un proxy hacia el stack: sin cifras con punto decimal, axe
    en 0 violaciones y sin desbordamiento en 1440, 820 y 390 px.
  - La imagen Docker del frontend aún no incluye este cambio.

### 2026-09-29 — inicio, tutorial y contacto migradas

- typecheck, lint y build OK (las tres páginas ya no requieren JS de cliente).
- axe-core: 0 violaciones en 1440/820/390 px en las tres páginas; sin overflow,
  sin errores de consola ni respuestas ≥400 (la imagen rota desapareció).
- Formulario de contacto: no se envió (Formspree es externo; la QA lo bloqueó).
- Capturas en `qa/paginas/`.

### 2026-09-29 — E2E contra backend real

Frontend nuevo (`next dev`) detrás de un proxy local de mismo origen que envía
`/api` y `/socket.io` al Nginx de Docker (sin reconstruir imágenes).
Cartilla `tests/data/001-pruebaInicial.xlsx` con nombre único `qa-rediseno-*`:

- Estimar → `POST /api/estimate` 200; enviar → `POST /api/upload` 202; progreso
  por WebSocket (7 eventos) y redirección a `/archivos` en ~5 s.
- Descarga Excel: `GET /api/descargar-excel/<uuid>` 200 con MIME xlsx.
- Reprocesar con Balanceado → `POST /api/reprocess/:id` 202; v2 visible;
  Eliminar/Reprocesar desactivados mientras corre.
- Eliminar → `DELETE /api/file/:id` 200; estado vacío mostrado.
- 0 errores de consola. Base verificada: 0 proyectos `qa-rediseno`, siguen los 6
  originales.
- Corregido durante la prueba: la etiqueta de progreso mostraba el estado crudo
  del worker (`GENERATING`); ahora se traducen también los estados en
  mayúscula. Los errores 409/404 del backend se muestran en los diálogos.
- Artefacto de entorno descartado: el primer intento de Socket.IO falló porque
  el proxy enviaba `Origin: localhost:3200`; contra Nginx directo conecta bien.
- Capturas en `qa/e2e/`.

### 2026-09-29 — `/archivos` migrada

- typecheck, lint y build OK.
- axe-core: 0 violaciones en 1440/820/390 px para lista con 6 proyectos reales,
  diálogo de reproceso abierto, estado vacío (filtro sin coincidencias) y estado
  de error (`/api/files` forzado a 500). Sin overflow ni errores de consola.
- Diálogos: el foco entra al abrir; Escape cierra; centrados en móvil.
- La QA abortaba toda petición distinta de GET: **no se eliminó ni reprocesó
  nada**. `DELETE /file/:id` y `POST /reprocess/:id` quedan sin prueba real.
- Capturas en `qa/archivos/`.

### 2026-09-29 — `/subir-cartilla` migrada

- `npm run typecheck`, `npm run lint`, `npm run build`: OK.
- axe-core (wcag2a/2aa/21aa) en 1440×1000, 820×1180 y 390×844, estado vacío
  y con cartilla + catálogo abierto: **0 violaciones**; sin overflow horizontal;
  sin errores de consola. Capturas en `qa/subir-cartilla/`.
- No se envió ninguna optimización: `/upload` y `/estimate` no se ejercitaron
  en QA para no crear registros en la base local. Los contratos (FormData,
  Socket.IO, polling) no se modificaron; queda pendiente una prueba de envío real.

### Baseline previa

- Stack Docker: seis servicios saludables en `http://localhost`.
- Rutas: `/`, `/subir-cartilla`, `/archivos`, `/tutorial`, `/contact-us` responden 200; `/resultados` redirige 307 a `/archivos`.
- Baseline: 15 capturas locales más 2 de producción.
- axe-core: fallos serios de contraste y nombre de enlace en todas las rutas; controles sin nombre accesible en carga y archivos; `lang` y metadata incorrectos.
- Producción y local comparten el mismo lenguaje visual y los mismos problemas principales.
