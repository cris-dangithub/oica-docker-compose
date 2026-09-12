#!/usr/bin/env bash
# Biblioteca de operación. Toda operación remota comparte un bloqueo.
set -Eeuo pipefail
umask 077
ROOT=${OICA_ROOT:-/opt/oica}
[[ $ROOT == /* && $ROOT != / ]] || { echo 'OICA_ROOT debe ser una ruta absoluta dedicada.'; exit 1; }
ROOT=$(realpath -m -- "$ROOT")
SHARED="$ROOT/shared"
RELEASES="$ROOT/releases"
BACKUPS="$ROOT/backups"
PROJECT=${OICA_PROJECT:-oica-production}
[[ $PROJECT =~ ^oica-(production|test-[a-z0-9-]+)$ ]] || { echo 'Nombre de proyecto no permitido.'; exit 1; }
mkdir -p "$SHARED/maintenance" "$RELEASES" "$BACKUPS"
chmod 755 "$SHARED/maintenance"
exec 9>"$ROOT/operation.lock"
flock -w 3600 9 || { echo 'Otra operación sigue activa.'; exit 1; }
export OICA_SHARED_DIR="$SHARED" MAINTENANCE_DIR="$SHARED/maintenance"
[[ -f $SHARED/production.env ]] || { echo 'Falta shared/production.env; ejecuta bootstrap-vps.sh.'; exit 1; }
TLS=${OICA_TLS:-true}
release_path() {
    [[ $1 =~ ^[a-f0-9]{40}(-[0-9]+)?$ ]] || { echo 'Se requiere un SHA completo.' >&2; return 1; }
    printf '%s/%s\n' "$RELEASES" "$1"
}
dc() {
    local release=$1; shift
    local args=(--project-name "$PROJECT" --env-file "$SHARED/production.env" --env-file "$release/images.env" -f "$release/docker-compose.yaml")
    [[ $TLS != true ]] || args+=(-f "$release/compose.production.yaml")
    docker compose "${args[@]}" "$@"
}
maintenance_on() { touch "$SHARED/maintenance/enabled"; chmod 644 "$SHARED/maintenance/enabled"; }
maintenance_off() { rm -f -- "$SHARED/maintenance/enabled"; }
current_release() {
    [[ -L $ROOT/current ]] && readlink -f "$ROOT/current"
}
backup_data() {
    local release=$1 stamp target
    stamp=$(date -u +%Y%m%dT%H%M%SZ)
    target="$BACKUPS/${stamp}-${release##*/}"
    mkdir "$target"
    # Variables del contenedor, no del host.
    # shellcheck disable=SC2016
    dc "$release" exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' > "$target/database.dump"
    dc "$release" run --rm --no-deps -T --entrypoint tar backend -C /usr/src/app/data/filestore -czf - . > "$target/filestore.tar.gz"
    dc "$release" exec -T db pg_restore --list < "$target/database.dump" >/dev/null
    tar -tzf "$target/filestore.tar.gz" >/dev/null
    cp "$release/images.env" "$target/images.env"
    cp "$release/schema.sha256" "$target/schema.sha256"
    (cd "$target" && sha256sum database.dump filestore.tar.gz images.env schema.sha256 > SHA256SUMS)
    touch "$target/COMPLETE"
    echo "Respaldo: $target"
}
compatible_schema() { cmp -s "$1/schema.sha256" "$2/schema.sha256"; }
verify_release() {
    local release=$1
    [[ -f $release/images.env && -f $release/schema.sha256 ]] || { echo 'Entrega incompleta'; return 1; }
    # No permitir referencias flotantes ni valores ejecutables en el manifiesto.
    python3 - "$release/images.env" <<'PY'
import re, sys
from pathlib import Path
values = Path(sys.argv[1]).read_text().splitlines()
keys = set()
for line in values:
    if not re.fullmatch(r'(BACKEND_IMAGE|WORKER_IMAGE|FRONTEND_IMAGE)=ghcr\.io/[a-z0-9_./-]+@sha256:[a-f0-9]{64}', line):
        raise SystemExit('Manifiesto de imágenes inválido')
    key = line.split('=')[0]
    if key in keys: raise SystemExit('Imagen duplicada')
    keys.add(key)
if len(keys) != 3: raise SystemExit('Faltan imágenes')
PY
    (cd "$release" && sha256sum --check schema.sha256)
    dc "$release" config --quiet
}
prune_owned_history() {
    python3 - "$ROOT" <<'PY'
from pathlib import Path
import re, shutil, sys
root = Path(sys.argv[1])
protected = {(root / n).resolve() for n in ('current', 'previous') if (root / n).exists()}
backups = sorted((p for p in (root/'backups').iterdir() if p.is_dir() and not p.is_symlink() and re.fullmatch(r'\d{8}T\d{6}Z-[a-f0-9]{40}(-[0-9]+)?',p.name) and (p/'COMPLETE').exists()), reverse=True)
for p in backups[:7]: protected.add((root/'releases'/p.name.split('-',1)[1]).resolve())
releases = sorted((p for p in (root/'releases').iterdir() if p.is_dir() and not p.is_symlink() and re.fullmatch('[a-f0-9]{40}(-[0-9]+)?',p.name)), key=lambda p:p.stat().st_mtime, reverse=True)
for p in releases[5:]:
    if p.resolve() not in protected: shutil.rmtree(p)
for p in backups[7:]: shutil.rmtree(p)
PY
}
