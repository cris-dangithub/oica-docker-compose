#!/usr/bin/env bash
# Preparación nativa para Ubuntu/Debian. Nunca ejecuta la app como root.
set -Eeuo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT"
[[ $EUID -ne 0 ]] || { echo 'Ejecuta como usuario habitual; sudo se solicita solo para instalar/configurar.'; exit 1; }
command -v apt-get >/dev/null || { echo 'Este instalador soporta Ubuntu/Debian.'; exit 1; }
sudo apt-get update
sudo apt-get install -y postgresql redis-server nginx libpango-1.0-0 libpangoft2-1.0-0 libcairo2 libgdk-pixbuf-2.0-0 libffi-dev libpq-dev build-essential fonts-dejavu-core fonts-liberation curl ca-certificates python3-venv
# No agregar repositorios externos de Python automáticamente.
command -v python3.12 >/dev/null || { echo 'Instala Python 3.12 con soporte venv (en Ubuntu 24.04: sudo apt-get install python3.12-venv) y repite.'; exit 1; }
[[ $(node -p 'process.versions.node.split(".")[0]' 2>/dev/null) == 22 ]] || { echo 'Instala Node.js 22 (por ejemplo, nvm install 22 && nvm use 22) y repite.'; exit 1; }
for role in backend worker; do
    python3.12 -m venv ".venv-$role"
    req=config/backend/requirements.txt
    [[ $role != worker ]] || req=config/celery_worker/requirements.txt
    ".venv-$role/bin/pip" install -r "$req"
done
(cd frontend && npm ci)
sudo service postgresql start
sudo service redis-server start
if [[ ! -f .env.development ]]; then
    password=$(openssl rand -hex 24)
    secret=$(openssl rand -hex 32)
    sudo -u postgres psql -v ON_ERROR_STOP=1 -v password="$password" <<'SQL'
SELECT format('CREATE ROLE oica_dev LOGIN PASSWORD %L', :'password') WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname='oica_dev') \gexec
SELECT format('ALTER ROLE oica_dev PASSWORD %L', :'password') \gexec
SELECT 'CREATE DATABASE oica_dev OWNER oica_dev' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname='oica_dev') \gexec
SQL
    umask 077
    printf 'DATABASE_URL=postgresql://oica_dev:%s@127.0.0.1:5432/oica_dev\nREDIS_URL=redis://127.0.0.1:6379/15\nUPLOAD_PATH=%q\nSECRET_KEY=%s\nALLOWED_ORIGINS=http://localhost\nMPLBACKEND=Agg\nFLASK_DEBUG=True\n' "$password" "$ROOT/.runtime/filestore-dev" "$secret" > .env.development
fi
mkdir -p .runtime/filestore-dev
# Un sitio explícito para localhost; no eliminar los sitios existentes.
# Variables literales de Nginx.
# shellcheck disable=SC2016
sed -e 's/resolver 127.0.0.11 valid=10s ipv6=off;//' \
    -e 's/set $api backend:5000;/set $api 127.0.0.1:5000;/' \
    -e 's/set $web frontend:3000;/set $web 127.0.0.1:3000;/' \
    -e 's/server_name _;/server_name localhost;/' \
    -e '/if (-f \/maintenance\/enabled)/d' config/nginx/default.conf > .runtime/nginx-dev.conf
sudo install -m 644 .runtime/nginx-dev.conf /etc/nginx/conf.d/oica-dev.conf
sudo nginx -t
sudo service nginx restart
echo 'Preparado. Ejecuta ./scripts/dev.sh (Docker debe estar detenido para liberar puertos).'
