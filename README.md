# OICA — Optimizador de cortes de acero

Monorepo con Flask, Celery, Next.js, PostgreSQL, Redis y Nginx.

El motor secuencial planifica por diámetro y etapa, reutiliza sobrantes y admite inventario importable/exportable. Consultar [el contrato de corte, las pruebas 001/002 y los comandos de benchmark](docs/CORTE_SECUENCIAL.md). El modelo supone pérdida por corte cero y sus resultados requieren validación física antes de ejecutarse en obra.

```bash
# Aplicación completa en http://localhost
docker compose up

# Desarrollo Linux/WSL sin Docker (Python 3.12 + Node 22)
./scripts/setup-dev.sh   # Preparación inicial
./scripts/dev.sh        # Uso diario, Ctrl+C para cerrar
```

Un push a `production` ejecuta las verificaciones y despliega en la VPS mediante GitHub Actions. Es necesario configurar primero SSH, GHCR y el dominio. El workflow manual permite reconstruir OICA con borrado de datos y respaldo opcional.

Consultar **[la guía de instalación, despliegue y recuperación](docs/DEPLOYMENT.md)** para configurar `oica.cris-munoz.me`, secretos, HTTPS, backups y rollback.

- `backend/`: aplicación Python y algoritmo genético.
- `frontend/`: aplicación Next.js.
- `config/`: imágenes, proxy, requisitos y migraciones.
- `scripts/`: desarrollo, pruebas y operación.
- `.github/workflows/`: CI, producción y rollback.

El código de `services/` es una copia local histórica excluida del despliegue. Los volúmenes Docker conservan los datos en actualizaciones normales. La aplicación no tiene autenticación: los archivos son compartidos por todos los visitantes.
