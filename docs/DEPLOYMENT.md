# Despliegue y desarrollo de OICA

OICA se mantiene en este repositorio: `backend/`, `frontend/`, configuración y workflows. Las carpetas originales `services/` se conservan como copia local; no se usan para construir ni arrancar. No ejecutar el antiguo instalador desde otra copia: borraba esas carpetas.

## Arranque con Docker

Requiere Docker Engine y Compose v2. Desde la raíz:

```bash
docker compose up
# O, en segundo plano:
./init.sh
```

La primera ejecución construye las imágenes y crea el esquema. Abrir **http://localhost**. Tras editar código, usar `docker compose up -d --build --wait` para reconstruir. Copiar `.env.example` a `.env` solo para cambiar los valores locales. Nunca usar las contraseñas de ejemplo en producción.

Nginx publica 80; Next.js, Flask, PostgreSQL y Redis son internos. `/api/` llega a Flask sin el prefijo y `/socket.io/` admite WebSocket y polling. No hay URLs de backend que configurar al compilar el frontend.

Los volúmenes `postgres_data`, `redis_data` y `filestore` conservan datos. `docker compose down` conserva los volúmenes; `down --volumes` **borra datos**. El código no está montado en producción. `migrate` es un servicio temporal adicional a los seis servicios permanentes.

Para probar mientras otra instalación usa el puerto 80:

```bash
COMPOSE_PROJECT_NAME=oica-test-local HTTP_PORT=8080 ALLOWED_ORIGINS=http://localhost:8080 docker compose up -d --build --wait
```

Usar siempre las mismas variables en los siguientes comandos de ese proyecto.

## Desarrollo sin Docker (Linux/WSL)

Prerequisitos: Python **3.12**, Node **22**, Ubuntu/Debian y sudo para la preparación inicial. En Ubuntu 24.04 Python 3.12 está disponible en apt. En distribuciones anteriores instalar Python 3.12 previamente; el script no agrega repositorios de terceros. Si usas nvm, ejecutar `nvm install 22` y `nvm use 22`.

```bash
./scripts/setup-dev.sh   # Una vez; instala/configura PostgreSQL, Redis y Nginx locales
./scripts/dev.sh         # Uso diario: frontend, backend y worker; Ctrl+C para cerrar
```

Abrir **http://localhost**. Detener previamente el stack Docker si ocupa 80, 3000, 5000, 5432 o 6379. El instalador no detiene ni elimina servicios ajenos. WSL debe permitir arrancar servicios Linux. El archivo `.env.development` queda excluido de Git, con base `oica_dev`, Redis DB 15 y filestore separado en `.runtime/filestore-dev`.

El instalador exige Python/Node correctos antes de crear entornos. Ejecutar nuevamente es seguro para los datos de desarrollo. Nginx, PostgreSQL y Redis quedan como servicios locales; Ctrl+C cierra solo los procesos de la sesión. Redis DB 15 debe estar reservado para OICA desarrollo.

Comandos individuales, después de exportar las variables con `set -a; source .env.development; set +a`:

```bash
.venv-backend/bin/python scripts/migrate.py
(cd backend && ../.venv-backend/bin/python server.py)
(cd backend && ../.venv-worker/bin/python -m celery -A celery_worker.celery worker --concurrency=1 --loglevel=info)
(cd frontend && npm run dev)
```

Los requisitos Python están en `config/backend/` y `config/celery_worker/`; no copiar archivos manualmente a `services/`. Ambos entornos usan el mismo `UPLOAD_PATH` absoluto.

## Primera instalación en la VPS

Destino: `oica.cris-munoz.me`, VPS Linux, 6 CPU / 12 GB RAM, compartida con otras aplicaciones pero con 80/443 libres. Antes de instalar, comprobar `cat /etc/os-release`, `uname -m`, `df -h`, `ss -ltnp` y `docker ps`. Las imágenes del pipeline se construyen para x86_64; una VPS ARM requiere adaptar la plataforma del build antes de desplegar.

1. Instalar [Docker Engine y Compose](https://docs.docker.com/engine/install/ubuntu/), `python3`, `openssl`, `curl`, `cron` y utilidades habituales. Crear un usuario dedicado con SSH por clave y acceso a Docker. Ese acceso equivale a privilegios administrativos: limitar quién posee la clave.
2. Permitir SSH y TCP 80/443 en el firewall/proveedor. No abrir 5432, 6379, 5000 ni 3000. Confirmar registros A y, si existe, AAAA del dominio.
3. Copiar el repositorio a la VPS y, como usuario de despliegue, ejecutar:

```bash
./scripts/bootstrap-vps.sh
./scripts/bootstrap-tls.sh administrador@example.com
```

`bootstrap-vps.sh` prepara `/opt/oica` y genera contraseñas aleatorias en `shared/production.env`, sin sobrescribir secretos existentes. No imprime los secretos. Cambiar `OICA_ROOT` si se necesita una ruta distinta, y configurar la misma variable en GitHub. Usar una ruta sin espacios.

`bootstrap-tls.sh` ocupa temporalmente 80 para emitir el certificado. Se detiene si el puerto está ocupado. Acepta los términos de Let's Encrypt al ejecutarlo y programa renovación diaria a las 03:17. La renovación usa el directorio ACME servido por Nginx; no interrumpe la web. El log queda en `/opt/oica/renew-tls.log`. En la VPS HTTP redirige a HTTPS.

4. Autenticar el usuario de despliegue ante GHCR si los paquetes son privados:

```bash
# Introducir un token con read:packages por stdin, nunca en un argumento literal.
docker login ghcr.io --username TU_USUARIO
```

5. Configurar el environment GitHub **production** y restringirlo a la rama `production`. No exigir aprobación manual en ese environment si se desea despliegue automático en cada push. La disponibilidad de las reglas depende del plan de GitHub.

| Tipo | Nombre | Contenido |
|---|---|---|
| Secret | `VPS_HOST` | IP o nombre SSH de la VPS |
| Secret | `VPS_USER` | Usuario de despliegue |
| Secret | `VPS_SSH_KEY` | Clave privada dedicada |
| Secret | `VPS_KNOWN_HOSTS` | Clave pública SSH del servidor, verificada por un canal independiente |
| Variable | `VPS_PORT` | Puerto SSH; predeterminado 22 |
| Variable | `OICA_ROOT` | Directorio dedicado; predeterminado `/opt/oica` |

No usar `StrictHostKeyChecking=no`. Obtener la huella desde la consola del proveedor y contrastarla antes de guardar `known_hosts`. Para puertos distintos de 22, su entrada debe incluir `[host]:puerto`.

6. Publicar los cambios revisados en `production` y establecerla como rama predeterminada en GitHub. El cambio remoto requiere permisos del propietario. Los scripts no hacen commits, pushes ni eliminan ramas remotas. Conservar `main` hasta comprobar el primer despliegue.

## Flujo de cambios

Crear una rama de trabajo, desarrollar, abrir PR hacia `production` y revisar los checks. Cada push a `production` ejecuta CI, construye imágenes en GitHub y publica en GHCR. La VPS solo descarga imágenes; no necesita Node ni Python de aplicación. CI publica las mismas imágenes que probaron el flujo completo, sin construirlas una segunda vez.

Cada ejecución crea una entrega `SHA-RUN_ID` independiente, incluso al reconstruir el mismo commit. La entrega contiene las tres referencias por digest, configuración, scripts y checksums de migraciones. Los despliegues se serializan con GitHub concurrency y un `flock` en la VPS. GitHub puede reemplazar ejecuciones pendientes por la más reciente; no cancela un despliegue que ya está ejecutándose.

Al actualizar: descargar primero, activar mantenimiento, detener backend/worker con 10 segundos de gracia, respaldar datos, marcar tareas interrumpidas y limpiar la cola exclusiva de OICA, aplicar migraciones y arrancar. Puede haber una interrupción breve. Las cartillas incompletas requieren reprocesamiento; no se reejecutan automáticamente. Los archivos y resultados completados se conservan.

Cada respaldo copia PostgreSQL y filestore mientras no hay escritores. Redis no se restaura: las tareas anteriores se marcan para reprocesamiento. Se conservan las últimas siete copias locales y al menos cinco entregas; también se conservan las entregas referenciadas por respaldos vigentes. Los respaldos no salen de la VPS: para protegerse de pérdida del servidor, copiarlos a almacenamiento externo.

## Reconstruir y borrar los datos

En Actions → **Publicar producción** → Run workflow, seleccionar la rama `production`:

- `action`: `reset`.
- `confirmation`: **BORRAR OICA PRODUCTION**.
- `backup`: activado por defecto; desactivarlo implica borrar sin crear una copia nueva.

Se valida y construye antes de tocar producción. Si el respaldo solicitado falla, se aborta antes del borrado. El reset elimina los volúmenes y contenedores de `oica-production`, incluidos base, cola, originales y artefactos. La base vuelve vacía. Certificados, secretos, respaldos anteriores y aplicaciones ajenas se conservan. Nunca se ejecuta `docker system prune`.

## Recuperación

Actions → **Recuperar versión anterior** acepta un identificador `SHA-RUN_ID` conservado en la VPS. Solo permite rollback cuando las migraciones de ambas entregas son idénticas. Los datos actuales se respaldan y conservan; no se intenta deshacer SQL automáticamente.

Si un despliegue falla sin modificar esquema, se intenta recuperar los contenedores anteriores. Tras un reset o cambio de esquema fallido queda mantenimiento activo y el workflow falla. Revisar logs antes de actuar.

Restaurar explícitamente un respaldo (sustituye todos los datos actuales de OICA):

```bash
OICA_ROOT=/opt/oica bash /opt/oica/current/scripts/restore.sh \
  20260912T120000Z-SHA_COMPLETO-RUN_ID 'RESTAURAR OICA PRODUCTION'
```

El script valida checksums, rutas del archivo y compatibilidad con la entrega original antes de borrar. Si no existe `current` tras una primera instalación fallida, usar el script dentro de la entrega correspondiente en `releases/SHA/scripts/`. Conservar una copia adicional del estado actual si es necesario antes de restaurar.

Logs operativos:

```bash
cd /opt/oica/current
OICA_SHARED_DIR=/opt/oica/shared MAINTENANCE_DIR=/opt/oica/shared/maintenance \
  docker compose -p oica-production --env-file /opt/oica/shared/production.env \
  --env-file images.env -f docker-compose.yaml -f compose.production.yaml logs --tail=100
```

Las contraseñas solo admiten caracteres seguros para la URL PostgreSQL; el bootstrap genera hexadecimal. No cambiar credenciales de una base existente únicamente editando el archivo de entorno: cambiar primero el rol PostgreSQL de forma coordinada.

## Verificaciones y límites

CI ejecuta ShellCheck, validación Compose, tests de los scripts de despliegue, tests del algoritmo, TypeScript, ESLint, build y un flujo completo con fixture pequeño. La prueba end-to-end valida handshake WebSocket, progreso, polling, artefactos, filtros y reprocesamiento; una verificación adicional contrasta demanda y diámetros y elimina el archivo de prueba. En el workflow de producción, después de publicar las imágenes y antes de entregar a la VPS, `scripts/test_operations_ci.sh` ensaya actualización, interrupción de cola, reset con/sin respaldo, restauración y rollback en un proyecto temporal propio. Exige runner GitHub, activación explícita y al menos 2 GB libres; no se ha ejecutado en la sesión local recuperada.

Los scripts de operaciones solo aceptan `oica-production` o nombres `oica-test-*`. Para ensayos locales pueden usarse `OICA_ROOT` temporal y `OICA_TLS=false`; esto no debe configurarse en la VPS pública.

La app es pública por decisión explícita: cualquier visitante puede consultar y borrar archivos compartidos. Se limita carga/reprocesamiento a seis solicitudes por minuto por IP (ráfaga de cinco), 16 MB por petición y un worker inicialmente. Los límites de recursos de producción son configurables; no hay aislamiento por usuario ni protección completa contra abuso. BUG-002 y BUG-006 siguen pendientes y no se modifican los objetivos académicos. Se añadió una validación de entrada vacía al motor para cumplir su test existente; las entradas válidas mantienen el algoritmo previo.


## Almacenamiento en WSL y precauciones locales

Después de reparar WSL, comprobar tanto `df -h .` como `df -h /mnt/c` (y la unidad que aloje el VHDX). El espacio virtual libre no garantiza espacio físico en Windows. No reconstruir ni instalar entornos duplicados si la unidad anfitriona está casi llena.

Antes de un build, consultar `docker system df` sin ejecutar limpiezas. Reutilizar las imágenes/cachés existentes; el build final también puede validarse en GitHub después de publicar los cambios autorizados. Los scripts de desarrollo y el build necesitan espacio adicional: revisar disponibilidad antes de ejecutarlos. No borrar imágenes, volúmenes ni cachés sin identificar su uso y obtener autorización.

Los resets y restauraciones deben ensayarse primero en un entorno desechable con espacio suficiente. La reparación de WSL interrumpió la validación final local: consultar `.claude/context/CURRENT_STATE.md` para distinguir lo verificado de lo pendiente.
