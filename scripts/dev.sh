#!/usr/bin/env bash
# Un supervisor sencillo: Ctrl+C cierra solo los procesos de esta sesión.
set -Eeuo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT"
[[ -f .env.development ]] || { echo 'Ejecuta primero ./scripts/setup-dev.sh'; exit 1; }
set -a
# shellcheck source=/dev/null
source .env.development
set +a
mkdir -p .runtime
exec 9>.runtime/dev.lock
flock -n 9 || { echo 'Ya hay una sesión de desarrollo activa.'; exit 1; }
for port in 3000 5000; do
    if ss -ltnH "sport = :$port" | read -r _; then
        echo "Puerto $port ocupado. Detén el stack Docker u otro proceso antes de iniciar."; exit 1
    fi
done
.venv-backend/bin/python -c 'import os, psycopg2, redis; psycopg2.connect(os.environ["DATABASE_URL"]).close(); redis.Redis.from_url(os.environ["REDIS_URL"]).ping()'
.venv-backend/bin/python scripts/migrate.py
pids=()
# Invocada por los traps.
# shellcheck disable=SC2329
cleanup() {
    trap - EXIT INT TERM
    for pid in "${pids[@]}"; do kill -- "-$pid" 2>/dev/null || true; done
    for pid in "${pids[@]}"; do wait "$pid" 2>/dev/null || true; done
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
# Los argumentos se expanden dentro del proceso hijo.
# shellcheck disable=SC2016
setsid bash -c 'cd "$1/backend"; exec "$1/.venv-backend/bin/python" server.py' _ "$ROOT" & pids+=("$!")
# Los argumentos se expanden dentro del proceso hijo.
# shellcheck disable=SC2016
setsid bash -c 'cd "$1/backend"; exec "$1/.venv-worker/bin/python" -m celery -A celery_worker.celery worker --loglevel=info --concurrency=1 --hostname=oica-dev@%h' _ "$ROOT" & pids+=("$!")
# Los argumentos se expanden dentro del proceso hijo.
# shellcheck disable=SC2016
setsid bash -c 'cd "$1/frontend"; exec npm run dev -- --hostname 127.0.0.1' _ "$ROOT" & pids+=("$!")
echo 'OICA: http://localhost — Ctrl+C para detener.'
set +e
wait -n "${pids[@]}"
status=$?
set -e
echo "Un proceso terminó (código $status); cerrando la sesión."
exit "$status"
