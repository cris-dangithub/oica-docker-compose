# Config - Configuración de Servicios

Esta carpeta contiene la configuración de Docker para cada servicio independiente.

## Estructura

```
config/
├── backend/
│   ├── Dockerfile           # Imagen para Flask server
│   ├── requirements.txt     # Dependencias Python del backend
│   └── init.sql            # Schema inicial de PostgreSQL
│
├── celery_worker/
│   ├── Dockerfile           # Imagen para Celery worker
│   └── requirements.txt     # Dependencias Python (mismo que backend)
│
└── frontend/
    └── (no requiere Dockerfile personalizado, usa imagen node oficial)
```

## Principio de Diseño

**Cada servicio tiene su propia configuración aislada**, aunque compartan dependencias:

### Backend (Flask Server)
- **Propósito**: Servidor HTTP que maneja requests, WebSocket, y encola tareas
- **Base**: Python 3.12-alpine
- **CMD**: `python server.py`
- **Puerto**: 5000
- **Dependencias**: Flask, SQLAlchemy, Socket.IO, Celery (para encolar)

### Celery Worker
- **Propósito**: Procesador asíncrono de tareas pesadas (algoritmo genético)
- **Base**: Python 3.12-alpine
- **CMD**: `celery -A celery_worker.celery_app worker --loglevel=info`
- **Puerto**: N/A (comunica vía Redis)
- **Dependencias**: Celery, SQLAlchemy, pandas, WeasyPrint, matplotlib

**Nota**: Usamos Python 3.12 porque psycopg2-binary 2.9.9 no es compatible con Python 3.13.

### ¿Por qué servicios separados?

1. **Escalabilidad**: Puedes ejecutar múltiples workers sin duplicar el servidor Flask
2. **Aislamiento**: Un crash en el worker no afecta al servidor HTTP
3. **Recursos**: Workers consumen más CPU, backend más I/O de red
4. **Despliegue**: Puedes actualizar workers sin downtime del servidor

## Dependencias Compartidas

Ambos servicios (backend y celery_worker) comparten:
- Código fuente: `services/backend/`
- Base de datos: PostgreSQL
- Cache: Redis
- Filestore: `app/data/filestore/`

**requirements.txt es duplicado intencionalmente** para permitir:
- Builds independientes de Docker
- Versiones específicas por servicio si se necesitan en el futuro
- Claridad en las dependencias de cada servicio

## Build Context

En `docker-compose.yaml`:

```yaml
backend:
  build:
    context: ./services/backend      # Código fuente
    dockerfile: ../../config/backend/Dockerfile  # Configuración

celery_worker:
  build:
    context: ./services/backend      # Mismo código
    dockerfile: ../../config/celery_worker/Dockerfile  # Configuración diferente
```

**Context apunta al código**, **dockerfile a la configuración**.

## Actualizar Dependencias

Cuando agregues una nueva dependencia Python:

1. Edita `config/backend/requirements.txt` (fuente de verdad)
2. Copia a `services/backend/requirements.txt`:
   ```bash
   cp config/backend/requirements.txt services/backend/requirements.txt
   ```
3. Si celery_worker necesita las mismas deps, copia también a `config/celery_worker/requirements.txt`
4. Reconstruye las imágenes:
   ```bash
   docker compose build backend celery_worker
   ```

### ¿Por qué requirements.txt está duplicado?

**Problema de Build Context**: Docker COPY solo puede acceder a archivos dentro del build context.

- Build context de backend: `services/backend/`
- Build context de celery_worker: `services/backend/`
- Dockerfiles están en: `config/backend/` y `config/celery_worker/`

**Solución**: Mantener requirements.txt en ambos lugares:
- `config/backend/requirements.txt` → **Fuente de verdad** (editar aquí)
- `services/backend/requirements.txt` → Copia para build (sincronizar antes de build)
- `config/celery_worker/requirements.txt` → Igual que backend (para documentación)

## Dependencias del Sistema (Alpine)

Ambos Dockerfiles instalan:
- `postgresql-dev`: Para psycopg2-binary
- `gcc`, `musl-dev`, `python3-dev`: Compiladores C para extensiones Python
- `cairo`, `pango`, `gdk-pixbuf`: Para WeasyPrint (generación de PDF)
- `jpeg-dev`, `zlib-dev`, `freetype-dev`: Para Pillow (procesamiento de imágenes)

Total: ~25 paquetes del sistema necesarios para el stack completo.
