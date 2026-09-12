# Estado actual del proyecto

> Actualizado: 2026-09-12, reanudación después de reparación de WSL con e2fsck.
> Bloque activo: F — Producción, CI/CD y desarrollo nativo.

## Objetivo y estado real

El código del monorepo, Compose, proxy, workflows y scripts de operación está implementado. **No declarar producción desplegada ni validación final completa**: faltan el build final de las imágenes Python, los ensayos reales de reset/restauración y el acceso a la VPS.

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
- Se retiraron solo los dos gitlinks del índice. Rama local: `production`, todavía siguiendo `origin/main`.
- Fast-forward a e8fa70a incorporó dos commits remotos de documentación. Con aprobación del usuario se creó el commit 0330943 de implementación. El push falló por falta de credenciales HTTPS y el token de gh es inválido. La rama predeterminada remota no se modificó.
- Compose: Nginx, Next.js, Flask, Celery, PostgreSQL, Redis y migrador temporal. Puerto predeterminado 80; API relativa /api y Socket.IO /socket.io.
- Imágenes con código, sin montajes de fuentes; secretos externos, volúmenes persistentes y requisitos Python fijados. Dockerfiles finales eliminan compiladores temporales, pero su build quedó interrumpido.
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

El usuario autorizó commit y push. La comprobación de `gh auth status` confirma que el token local de GitHub es inválido, incluso fuera del aislamiento; renovar con `gh auth login -h github.com` antes de publicar. Se corrigió `.gitignore` para excluir solo `/app/` en la raíz y conservar `frontend/src/app/` en la entrega. La configuración SSH del entorno GitHub `production` y el acceso a la VPS siguen pendientes.

1. Elegir dónde ejecutar la compilación final. Estimación local conservadora: 1–3 GB adicionales transitorios, variable según caché. No ejecutarla sin aviso/autorización del usuario; preferir GitHub si no hay margen físico suficiente.
2. Validar imágenes finales, migraciones repetibles y recuperación en un entorno desechable con espacio suficiente. El ensayo real ya está programado en CI mediante scripts/test_operations_ci.sh; aún no se ha ejecutado.
3. Configurar SSH, GHCR y secrets/environment GitHub; comprobar arquitectura x86_64, distribución, espacio y puertos reales de la VPS.
4. Publicar production y cambiar rama predeterminada remota solo mediante acciones explícitamente autorizadas; no hacer commits sin instrucción expresa.
5. Preparar HTTPS para oica.cris-munoz.me y efectuar el primer despliegue vacío.

## Contexto académico preservado

Bloques A/B/C completados. Test 002 completó rápido, balanceado y profundo; balanceado obtuvo mejor eficiencia, y profundo sigue afectado por BUG-006. BUG-002 y BUG-006 continúan pendientes. D depende de INF-008 (reutilización de desperdicios). INF-011 valida el cambio a monorepo y operación en VPS.

Los commits incorporados ampliaron Cap. 4 a 212 líneas; la antigua afirmación «Cap. 4 vacío» está desactualizada. Su revisión académica queda fuera de este bloque, sin inventar completitud ni validar resultados por inferencia.

Guía operativa: `docs/DEPLOYMENT.md`. Diagnóstico y riesgos: `.claude/diagnostics/2026-09-12-produccion.md`.
