#!/usr/bin/env bash
set -Eeuo pipefail
# shellcheck source=scripts/ops-common.sh
source "$(dirname -- "${BASH_SOURCE[0]}")/ops-common.sh"
release=$(current_release)
dc "$release" run --rm --no-deps -T certbot renew --webroot -w /var/www/certbot --quiet
dc "$release" exec -T nginx nginx -t
dc "$release" exec -T nginx nginx -s reload
