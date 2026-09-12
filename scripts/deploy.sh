#!/usr/bin/env bash
# deploy SHA | reset SHA CONFIRMACION BACKUP | rollback SHA
set -Eeuo pipefail
# shellcheck source=scripts/ops-common.sh
source "$(dirname -- "${BASH_SOURCE[0]}")/ops-common.sh"
action=${1:-}; sha=${2:-}
[[ $action =~ ^(deploy|reset|rollback)$ ]] || { echo 'Uso: deploy.sh deploy|reset|rollback SHA [confirmación] [true|false]'; exit 1; }
release=$(release_path "$sha")
verify_release "$release"
previous=$(current_release || true)
backup=true
if [[ $action == reset ]]; then
    [[ ${3:-} == 'BORRAR OICA PRODUCTION' ]] || { echo 'Confirmación incorrecta'; exit 1; }
    backup=${4:-true}
    [[ $backup == true || $backup == false ]] || { echo 'backup debe ser true o false'; exit 1; }
fi
if [[ $action == rollback ]]; then
    if [[ -z $previous ]] || ! compatible_schema "$release" "$previous"; then
        echo 'Rollback incompatible con el esquema; requiere restauración explícita.'; exit 1
    fi
fi
# Una entrega fallida al descargar no interrumpe el servicio actual.
dc "$release" pull db redis backend celery_worker frontend nginx migrate
maintenance_on
changed_schema=false
reset_started=false
recover() {
    code=$?
    trap - ERR
    maintenance_on
    echo "Operación fallida ($code)."
    if [[ $reset_started == false && -n $previous && $changed_schema == false ]]; then
        if dc "$previous" up -d --no-build --wait --wait-timeout 180 db redis backend celery_worker frontend; then
            maintenance_off
            dc "$previous" up -d --no-build --wait --wait-timeout 120 nginx || maintenance_on
            echo 'Se intentó recuperar la entrega anterior. Revisar salud y logs.'
        fi
    else
        echo 'Mantenimiento activo. Recuperar con el respaldo; no se revierte SQL automáticamente.'
    fi
    exit "$code"
}
trap recover ERR
if [[ -n $previous ]]; then
    dc "$previous" stop -t 10 backend celery_worker
    if [[ $backup == true ]]; then backup_data "$previous"; fi
fi
if [[ $action == reset ]]; then
    reset_started=true
    # Recursos dedicados al proyecto, sin prune ni volúmenes ajenos.
    dc "${previous:-$release}" down --volumes --remove-orphans
fi
dc "$release" up -d --no-build --wait --wait-timeout 120 db redis
if [[ -n $previous && $action != reset ]]; then
    dc "$previous" run --rm --no-deps -T backend python scripts/interrupt_jobs.py
    if ! compatible_schema "$release" "$previous"; then changed_schema=true; fi
fi
dc "$release" run --rm --no-deps -T migrate
# Compose requiere también que su servicio migrate quede terminado exitosamente.
dc "$release" up -d --no-build --wait --wait-timeout 240 backend celery_worker frontend
maintenance_off
dc "$release" up -d --no-build --wait --wait-timeout 120 nginx
if [[ $TLS == true ]]; then
    dc "$release" exec -T nginx wget -q --no-check-certificate -O /dev/null https://127.0.0.1/api/health
else
    dc "$release" exec -T nginx wget -q -O /dev/null http://127.0.0.1/api/health
fi
if [[ -n $previous && $previous != "$release" ]]; then ln -sfn "$previous" "$ROOT/previous"; fi
ln -sfn "$release" "$ROOT/current"
trap - ERR
prune_owned_history
echo "OICA desplegada: $sha"
