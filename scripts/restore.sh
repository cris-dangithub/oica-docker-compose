#!/usr/bin/env bash
# Restauración explícita de un respaldo local a su entrega original.
set -Eeuo pipefail
# shellcheck source=scripts/ops-common.sh
source "$(dirname -- "${BASH_SOURCE[0]}")/ops-common.sh"
name=${1:-}
[[ ${2:-} == 'RESTAURAR OICA PRODUCTION' ]] || { echo 'Se requiere confirmación RESTAURAR OICA PRODUCTION'; exit 1; }
[[ $name =~ ^[0-9]{8}T[0-9]{6}Z-([a-f0-9]{40}(-[0-9]+)?)$ ]] || { echo 'Nombre de respaldo inválido'; exit 1; }
sha=${BASH_REMATCH[1]}
backup="$BACKUPS/$name"
[[ -f $backup/COMPLETE && ! -L $backup ]] || { echo 'Respaldo incompleto'; exit 1; }
(cd "$backup" && sha256sum --check SHA256SUMS)
release=$(release_path "$sha")
verify_release "$release"
cmp "$backup/schema.sha256" "$release/schema.sha256"
cmp "$backup/images.env" "$release/images.env"
# Validar rutas del archivo antes de extraer en el volumen.
python3 - "$backup/filestore.tar.gz" <<'PY'
import sys,tarfile
from pathlib import PurePosixPath
with tarfile.open(sys.argv[1]) as archive:
    for item in archive:
        path=PurePosixPath(item.name)
        if path.is_absolute() or '..' in path.parts or not (item.isfile() or item.isdir()):
            raise SystemExit('Archivo de respaldo con entradas no permitidas')
PY
dc "$release" pull db redis backend celery_worker frontend nginx migrate
maintenance_on
# Un fallo posterior al borrado conserva el modo mantenimiento para recuperar.
trap 'maintenance_on' ERR
previous=$(current_release || true)
dc "${previous:-$release}" stop -t 10 backend celery_worker
# Borrado acotado a los tres volúmenes OICA; conserva respaldos y certificados.
dc "${previous:-$release}" down --volumes --remove-orphans
dc "$release" up -d --no-build --wait db redis
# Variables del contenedor, no del host.
# shellcheck disable=SC2016
dc "$release" exec -T db sh -c 'pg_restore --exit-on-error --no-owner -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < "$backup/database.dump"
dc "$release" run --rm --no-deps -T --entrypoint tar backend -C /usr/src/app/data/filestore -xzf - < "$backup/filestore.tar.gz"
dc "$release" run --rm --no-deps -T backend python scripts/interrupt_jobs.py
dc "$release" up -d --no-build --wait --wait-timeout 240 backend celery_worker frontend
maintenance_off
dc "$release" up -d --no-build --wait --wait-timeout 120 nginx
ln -sfn "$release" "$ROOT/current"
trap - ERR
echo 'Respaldo restaurado. Las tareas incompletas requieren reprocesamiento.'
