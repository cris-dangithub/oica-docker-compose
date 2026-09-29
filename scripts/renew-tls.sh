#!/usr/bin/env bash
set -Eeuo pipefail
# shellcheck source=scripts/ops-common.sh
source "$(dirname -- "${BASH_SOURCE[0]}")/ops-common.sh"
[[ $PROXY_MODE != host ]] || { echo "TLS gestionado por el host; renovación Docker omitida."; exit 0; }
release=$(current_release)
dc "$release" run --rm --no-deps -T certbot renew --webroot -w /var/www/certbot --quiet
dc "$release" exec -T nginx nginx -t
dc "$release" exec -T nginx nginx -s reload
