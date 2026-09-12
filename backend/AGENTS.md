# Backend OICA

Leer primero `../AGENTS.md` y el contexto de sesión. Código fuente versionado del monorepo; no editar las copias históricas en `../services/`.

- Python **3.12**. Servidor: `server.py` (Flask + Socket.IO/gevent). Worker: `celery_worker.py` (Celery prefork, requisitos separados).
- Configuración por `DATABASE_URL`, `REDIS_URL`, `UPLOAD_PATH`, `SECRET_KEY`, `ALLOWED_ORIGINS`. No crear tablas desde el servidor: usar `../scripts/migrate.py`.
- Dependencias fuente: `../config/backend/requirements.txt`, `../config/celery_worker/requirements.txt`, archivo común y constraints. `requirements.txt` local es solo un enlace lógico mediante `-r`.
- Desarrollo: `../scripts/dev.sh`. No usar `main.py`/`server_old.py` para el flujo de producción.
- Pruebas: `python -m unittest discover -s tests -p 'test_*.py'` desde este directorio. E2E: ver `../docs/DEPLOYMENT.md`.
- Preservar separación por diámetro, cantidades agrupadas y límites de artefactos. Leer el análisis del último dataset antes de modificar el worker/generador.
- Código, comentarios y documentación nuevos en español. No hacer commits sin instrucción explícita.
