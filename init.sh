#!/usr/bin/env bash
# Arranque no destructivo. No instala Docker ni clona/borra repositorios.
set -Eeuo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
command -v docker >/dev/null || { echo 'Instala Docker Engine y el plugin Compose v2.'; exit 1; }
docker compose version >/dev/null
docker compose up -d --build --wait
