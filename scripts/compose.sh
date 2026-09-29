#!/usr/bin/env bash
# Compose local con selección de proxy desde .env; sin builds implícitos.
set -Eeuo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
cd "$root"
mode=$(python3 scripts/proxy_config.py .env OICA_PROXY_MODE)
args=(-f docker-compose.yaml)
if [[ $mode == host ]]; then
    args+=(-f compose.host-nginx.yaml)
    export COMPOSE_PROFILES=''
    # Un perfil desactivado no detiene contenedores de ejecuciones anteriores.
    if [[ ${1:-} == up ]]; then docker compose "${args[@]}" stop nginx; fi
fi
exec docker compose "${args[@]}" "$@"
