#!/usr/bin/env bash
# Ensayo destructivo SOLO en un proyecto temporal propio, después de publicar
# las imágenes verificadas. No ejecutar en la VPS ni contra datos existentes.
set -Eeuo pipefail
[[ ${OICA_RUN_DESTRUCTIVE_TESTS:-} == 1 ]] || { echo 'Se requiere OICA_RUN_DESTRUCTIVE_TESTS=1 para este ensayo aislado.'; exit 1; }
[[ ${GITHUB_ACTIONS:-} == true ]] || { echo 'Este ensayo está reservado al runner desechable de GitHub Actions.'; exit 1; }
[[ -d delivery && -f delivery/images.env ]] || { echo 'Falta la entrega de CI.'; exit 1; }
# Reserva conservadora para volúmenes, respaldos pequeños y metadatos.
free_mb=$(df -Pm "${RUNNER_TEMP:?}" | awk 'NR==2 {print $4}')
(( free_mb >= 2048 )) || { echo 'Se requieren al menos 2 GB libres para el ensayo.'; exit 1; }
root=$(mktemp -d "$RUNNER_TEMP/oica-test-XXXXXXXX")
project=${root##*/}
project=${project,,}
release_id="${GITHUB_SHA:?}-${GITHUB_RUN_ID:?}"
release="$root/releases/$release_id"
mkdir -p "$release" "$root/shared"
cp -R delivery/. "$release/"
cat > "$root/shared/production.env" <<'ENV'
POSTGRES_USER=oica_test
POSTGRES_DB=oica_test
POSTGRES_PASSWORD=solo_ensayo_efimero
SECRET_KEY=solo_ensayo_efimero
HTTP_PORT=8081
HTTP_BIND=127.0.0.1
ALLOWED_ORIGINS=http://localhost:8081
ENV
export OICA_ROOT="$root" OICA_PROJECT="$project" OICA_TLS=false
export OICA_SHARED_DIR="$root/shared" MAINTENANCE_DIR="$root/shared/maintenance"
# El entorno del runner prevalece sobre --env-file en Compose.
# Separar el ensayo del stack oica-ci, que sigue escuchando en 8080.
export HTTP_PORT=8081 HTTP_BIND=127.0.0.1 ALLOWED_ORIGINS=http://localhost:8081
dc() {
    docker compose -p "$project" --env-file "$root/shared/production.env" \
        --env-file "$release/images.env" -f "$release/docker-compose.yaml" "$@"
}
cleanup() {
    local code=$? service diagnostic
    if (( code != 0 )); then
        dc ps -a || true
        # Anotaciones cortas por servicio: GitHub trunca mensajes largos.
        for service in nginx backend migrate; do
            diagnostic=$(dc logs --no-color --tail=15 "$service" 2>&1 | tail -c 2000) || true
            diagnostic=${diagnostic//'%'/'%25'}
            diagnostic=${diagnostic//$'\r'/'%0D'}
            diagnostic=${diagnostic//$'\n'/'%0A'}
            printf '::error title=Diagnóstico %s::%s\n' "$service" "$diagnostic"
        done
    fi
    # Solo los recursos creados por este ensayo, nunca los de producción.
    dc down --volumes --remove-orphans || true
    return "$code"
}
trap cleanup EXIT
unrelated=$(docker compose -p oica-ci ps -q | sort)
bash "$release/scripts/deploy.sh" deploy "$release_id"
python3 scripts/smoke_e2e.py http://localhost:8081 tests/fixtures/small.xlsx --keep
dc exec -T backend python - < scripts/verify_smoke_domain.py

# Dejar un reprocesamiento en cola y comprobar su interrupción explícita.
dc stop -t 10 celery_worker
task_id=$(python3 - <<'PY'
import json, urllib.request
base='http://localhost:8081/api'
with urllib.request.urlopen(base+'/files?search=smoke') as response:
    file_id=json.load(response)['files'][0]['id']
request=urllib.request.Request(f'{base}/reprocess/{file_id}', data=b'{"perfil":"rapido"}', headers={'Content-Type':'application/json'})
with urllib.request.urlopen(request) as response:
    print(json.load(response)['task_id'])
PY
)
bash "$release/scripts/deploy.sh" deploy "$release_id"
python3 - "$task_id" <<'PY'
import json, sys, urllib.request
with urllib.request.urlopen('http://localhost:8081/api/status/'+sys.argv[1]) as response:
    assert json.load(response)['state']=='FAILURE'
PY

# Reset con respaldo y restauración real de base + artefactos.
bash "$release/scripts/deploy.sh" reset "$release_id" 'BORRAR OICA PRODUCTION' true
python3 - <<'PY'
import json, urllib.request
with urllib.request.urlopen('http://localhost:8081/api/files') as response:
    assert json.load(response)['total']==0
PY
backup_name=$(python3 - "$root/backups" <<'PY'
from pathlib import Path
import sys
print(sorted(p.name for p in Path(sys.argv[1]).iterdir() if (p/'COMPLETE').is_file())[-1])
PY
)
bash "$release/scripts/restore.sh" "$backup_name" 'RESTAURAR OICA PRODUCTION'
dc exec -T backend python - < scripts/verify_smoke_domain.py

# Nueva entrega compatible y rollback: mismos datos, esquema e imágenes.
next_id="${release_id}1"
mkdir "$root/releases/$next_id"
cp -R delivery/. "$root/releases/$next_id/"
bash "$release/scripts/deploy.sh" deploy "$next_id"
bash "$release/scripts/deploy.sh" rollback "$release_id"
dc exec -T backend python - < scripts/verify_smoke_domain.py

# También comprobar reset sin respaldo y aislamiento del otro stack de CI.
before=$(find "$root/backups" -name COMPLETE -type f | wc -l)
bash "$release/scripts/deploy.sh" reset "$release_id" 'BORRAR OICA PRODUCTION' false
after=$(find "$root/backups" -name COMPLETE -type f | wc -l)
[[ $before == "$after" ]]
[[ $(docker compose -p oica-ci ps -q | sort) == "$unrelated" ]]
echo 'OK: actualización, interrupción, reset con/sin respaldo, restauración, rollback y aislamiento.'
