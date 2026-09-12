#!/usr/bin/env bash
# Ejecutar una vez en la VPS con el usuario de despliegue.
set -Eeuo pipefail
ROOT=${OICA_ROOT:-/opt/oica}
if ! command -v docker >/dev/null || ! docker compose version >/dev/null; then
    echo 'Instala Docker Engine y Compose v2: https://docs.docker.com/engine/install/ubuntu/'; exit 1
fi
for command in openssl flock python3 curl crontab ss; do command -v "$command" >/dev/null || { echo "Falta $command"; exit 1; }; done
sudo install -d -m 750 -o "$(id -u)" -g "$(id -g)" "$ROOT"
mkdir -p "$ROOT/shared/maintenance" "$ROOT/shared/letsencrypt" "$ROOT/shared/acme" "$ROOT/backups" "$ROOT/releases"
if [[ ! -f $ROOT/shared/production.env ]]; then
    umask 077
    password=$(openssl rand -hex 32)
    secret=$(openssl rand -hex 32)
    printf 'POSTGRES_DB=oica_db\nPOSTGRES_USER=oica_user\nPOSTGRES_PASSWORD=%s\nSECRET_KEY=%s\nALLOWED_ORIGINS=https://oica.cris-munoz.me\nHTTP_PORT=80\nWORKER_CONCURRENCY=1\n' "$password" "$secret" > "$ROOT/shared/production.env"
fi
echo 'Estructura y secretos preparados. Configura GHCR, SSH y ejecuta bootstrap-tls.sh CORREO antes del primer despliegue.'
