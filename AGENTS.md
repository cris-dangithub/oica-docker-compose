# AGENTS.md

## What this repo is

Docker Compose orchestration for **OICA** (steel bar cutting optimizer). This repo contains only Docker config, DB schema, and a setup script. The actual application code lives in two **separate repositories** cloned at runtime into `services/` (which is `.gitignored`):

- **Backend** (Flask + Celery): `github.com/cris-dangithub/oica-steel-cutting-optimizer` → `services/backend/`
- **Frontend** (Next.js 15): `github.com/cris-dangithub/tesis-frontend` → `services/frontend/`

Do not create or edit files under `services/` — changes will be lost on next `init.sh` run and are not tracked by this repo's git.

## Setup and commands

```bash
# Full setup (installs Docker/Node if missing, clones repos, builds & starts everything)
sudo chmod +x ./init.sh && ./init.sh

# WARNING: init.sh runs `sudo rm -rf services` before cloning — it destroys local changes

# Rebuild after config changes
docker compose up -d --build

# Rebuild a single service
docker compose build backend celery_worker

# Logs
docker compose logs -f backend
docker compose logs -f celery_worker
```

There is no Makefile, no CI, no test runner, and no linting configured in this repo.

## Architecture (5 services)

| Service | Container | Port | Notes |
|---------|-----------|------|-------|
| `db` | postgres:15-alpine | 5432 | Schema from `config/backend/init.sql` (runs only on first volume creation) |
| `redis` | redis:7-alpine | 6379 | Celery broker + pub/sub for real-time progress |
| `backend` | Python 3.12-alpine | 5000 | Flask + Socket.IO server (`server.py`) |
| `celery_worker` | Python 3.12-alpine | — | Same codebase as backend, different Dockerfile + entrypoint |
| `frontend` | node:22-alpine | 80→3000 | Runs `npm install && npm run build && npm start` in container |

Dependency chain: `frontend → backend → db (healthy), redis (healthy)` and `celery_worker → db, redis`.

Both `backend` and `celery_worker` mount `./services/backend` and share `./app/data/filestore` for file storage.

## Key constraints an agent would miss

- **Python 3.12 only** — `psycopg2-binary 2.9.9` is incompatible with Python 3.13. Do not bump the base image.
- **Duplicate `requirements.txt`** — The source of truth is `config/backend/requirements.txt` and `config/celery_worker/requirements.txt`. These must be manually synced to `services/backend/requirements.txt` before building because Docker COPY cannot reach outside the build context. After editing config requirements, run:
  ```bash
  cp config/backend/requirements.txt services/backend/requirements.txt
  ```
- **No `.env` file** — All environment variables are inline in `docker-compose.yaml`. Credentials are dev-only defaults (no secrets management).
- **`init.sql` is not a migration tool** — It only runs on first PostgreSQL volume creation. To apply schema changes to an existing DB, either drop the volume (`docker volume rm oica-app_postgres_data`) or run SQL manually. See `config/backend/migration_remove_unique_document_number.sql` for the migration pattern.
- **Backend vs Celery differences** — Both use the same source code but: backend uses `gevent` for WebSocket, celery_worker uses `eventlet`. Their `requirements.txt` files differ on this dependency.
- **Frontend has no custom Dockerfile** — It uses the stock `node:22-alpine` image with an inline `command`. Config at `config/frontend/` is just a `.gitkeep`. See `services/frontend/AGENTS.md` for frontend-specific guidance.

## Directory layout

```
config/
  backend/Dockerfile          # Flask server image
  backend/requirements.txt    # Python deps (source of truth for backend)
  backend/init.sql            # PostgreSQL schema (2 tables, triggers, indices)
  celery_worker/Dockerfile    # Celery worker image
  celery_worker/requirements.txt  # Python deps (source of truth for worker)
app/data/filestore/           # Shared volume: UUID-based artifact directories
services/                     # .gitignored — cloned repos live here at runtime
```

## Language

Project documentation, comments, DB schema, and commit messages are in **Spanish**. Follow this convention.
