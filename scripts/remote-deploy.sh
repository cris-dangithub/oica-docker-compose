#!/usr/bin/env bash
set -Eeuo pipefail
sha=${1:?Se requiere SHA}
[[ $sha =~ ^[a-f0-9]{40}(-[0-9]+)?$ ]] || exit 1
[[ ${VPS_HOST:-} =~ ^[a-zA-Z0-9][a-zA-Z0-9.-]*$ && ${VPS_USER:-} =~ ^[a-z_][a-z0-9_-]*$ ]] || { echo 'Host/usuario SSH inválido'; exit 1; }
[[ ${VPS_PORT:-22} =~ ^[0-9]+$ ]] || exit 1
root=${OICA_ROOT:-/opt/oica}
[[ $root =~ ^/[a-zA-Z0-9_/-]+$ && $root != / && $root != *..* ]] || { echo 'Ruta OICA inválida'; exit 1; }
action=${ACTION:-deploy}
[[ $action =~ ^(deploy|reset|rollback)$ ]] || exit 1
backup=${BACKUP:-true}
[[ $backup == true || $backup == false ]] || exit 1
if [[ $action == reset ]]; then
    [[ ${CONFIRMATION:-} == 'BORRAR OICA PRODUCTION' ]] || exit 1
fi
ssh_args=(-o BatchMode=yes -o StrictHostKeyChecking=yes -o ServerAliveInterval=15 -o ServerAliveCountMax=4 -p "${VPS_PORT:-22}")
target="$VPS_USER@$VPS_HOST"
if [[ $action != rollback ]]; then
    # Los únicos valores interpolados han sido restringidos arriba.
    scp -o BatchMode=yes -o StrictHostKeyChecking=yes -P "${VPS_PORT:-22}" release.tar.gz "$target:$root/releases/$sha.tar.gz"
    # Extracción atómica: una transferencia fallida no deja una entrega parcial.
    ssh "${ssh_args[@]}" "$target" bash -s -- "$root" "$sha" <<'REMOTE'
set -Eeuo pipefail
root=$1
release_id=$2
exec 9>"$root/operation.lock"
flock -w 3600 9
if [[ ! -d $root/releases/$release_id ]]; then
    stage=$(mktemp -d "$root/releases/.incoming-XXXXXXXX")
    trap 'rm -rf -- "$stage"' EXIT
    tar -xzf "$root/releases/$release_id.tar.gz" -C "$stage"
    mv "$stage" "$root/releases/$release_id"
fi
REMOTE
fi
# shellcheck disable=SC2029
ssh "${ssh_args[@]}" "$target" "OICA_ROOT='$root' bash '$root/releases/$sha/scripts/deploy.sh' '$action' '$sha' 'BORRAR OICA PRODUCTION' '$backup'"
