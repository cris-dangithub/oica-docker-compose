# QA del rediseño

## Baseline 2026-09-29

- Docker Compose: seis servicios saludables.
- Rutas principales: OK por HTTP.
- Capturas: desktop 1440×1000, tablet 768×1024 y mobile 390×844.
- Producción contrastada en inicio y archivos.
- axe-core: fallos registrados en `UI-AUDIT.md`.

## `/subir-cartilla` — 2026-09-29

- Build/lint/typecheck OK.
- axe-core: 0 violaciones en desktop 1440, tablet 820 y mobile 390 (vacío y con archivo).
- Sin overflow horizontal ni errores de consola; menú móvil verificado.
- Método: `next dev -p 3100` con `/api/**` redirigido por Playwright al stack
  Docker en `http://localhost` (solo GET). Chromium de `~/.cache/ms-playwright`
  con `libgbm1`/`libwayland-server0` extraídos sin sudo (`apt-get download` +
  `dpkg-deb -x`) y `LD_LIBRARY_PATH`.
- Capturas: [`qa/subir-cartilla/`](./qa/subir-cartilla/).
- Envío real verificado en el E2E. Pendiente: navegación completa por teclado.

## `/archivos` — 2026-09-29

- Build/lint/typecheck OK; axe-core 0 violaciones en lista, diálogo, vacío y error, en tres viewports.
- La QA bloquea peticiones no-GET para proteger la base local.
- Capturas: [`qa/archivos/`](./qa/archivos/).
- Reproceso y eliminación reales verificados en el E2E (ver abajo).

## E2E contra backend real — 2026-09-29

Estimar, enviar, progreso por WebSocket, descargar, reprocesar y eliminar con una
cartilla de prueba de nombre único; base limpia al final. Detalle en `STATE.md`,
capturas en [`qa/e2e/`](./qa/e2e/).

## Inicio, tutorial y contacto — 2026-09-29

- axe-core 0 violaciones en tres viewports; sin overflow ni errores; capturas en [`qa/paginas/`](./qa/paginas/).

## Evidencia

- Capturas AS-IS: [`baseline/`](./baseline/).
- Comparación de direcciones: [directions-comparison.png](./directions-comparison.png).
- Script de auditoría: [`../../scripts/audit-ui-baseline.cjs`](../../scripts/audit-ui-baseline.cjs).

## Pendiente para cierre

- Visual QA Figma vs implementación.
- Responsive: mobile, tablet, desktop normal y ancho.
- Navegación por teclado y focus visible.
- Contraste WCAG AA.
- Labels, `aria-*`, semántica y hit targets.
- Flujos: cargar, estimar, procesar, progreso, filtrar, descargar, reprocesar y eliminar.
- `npm run typecheck`, `npm run lint`, `npm run build` y tests relevantes.

