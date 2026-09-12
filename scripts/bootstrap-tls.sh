#!/usr/bin/env bash
# Emisión inicial standalone: requiere puerto 80 libre y DNS apuntando aquí.
set -Eeuo pipefail
ROOT=${OICA_ROOT:-/opt/oica}
email=${1:?Uso: bootstrap-tls.sh correo@example.com}
[[ -d $ROOT/shared ]] || { echo 'Ejecuta bootstrap-vps.sh primero'; exit 1; }
exec 9>"$ROOT/operation.lock"
flock -w 60 9
if ss -ltnH 'sport = :80' | read -r _; then echo 'Puerto 80 ocupado; no se detendrá ningún servicio automáticamente.'; exit 1; fi
docker run --rm -p 80:80 -v "$ROOT/shared/letsencrypt:/etc/letsencrypt" -v "$ROOT/shared/acme:/var/www/certbot" certbot/certbot:v4.0.0 certonly --standalone --non-interactive --agree-tos --email "$email" -d oica.cris-munoz.me
# Renovación usa webroot; no necesita detener Nginx.
# La tarea resuelve current en cada ejecución, por lo que sigue los despliegues.
cron_line="17 3 * * * OICA_ROOT=$ROOT /bin/bash $ROOT/current/scripts/renew-tls.sh >> $ROOT/renew-tls.log 2>&1"
({ crontab -l 2>/dev/null || true; } | sed '\|/current/scripts/renew-tls.sh|d'; printf '%s\n' "$cron_line") | crontab -
echo 'Certificado emitido y renovación diaria instalada a las 03:17.' 
