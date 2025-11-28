# OICA - Sistema de Optimización con PostgreSQL y Procesamiento Asíncrono

## 🚀 Arquitectura del Sistema

El sistema ha sido migrado de localStorage a PostgreSQL con procesamiento asíncrono:

- **Frontend**: Next.js 15 con Socket.IO para actualizaciones en tiempo real
- **Backend**: Flask + SQLAlchemy con WebSocket
- **Base de Datos**: PostgreSQL 15 con esquema normalizado
- **Cola de Tareas**: Celery + Redis para procesamiento asíncrono
- **Almacenamiento**: Directorios UUID para aislamiento de versiones

## 📋 Requisitos Previos

- Docker y Docker Compose
- Node.js 18+ (para desarrollo local del frontend)
- Puertos disponibles: 3000 (frontend), 5000 (backend), 5432 (PostgreSQL), 6379 (Redis)

## 🛠️ Instalación y Configuración

### 1. Clonar y preparar el proyecto

```bash
cd /home/cris/projects/01-proyecto_de_grado/oica-docker-compose
```

### 2. Instalar dependencias del frontend

```bash
cd services/frontend
npm install
cd ../..
```

### 3. Levantar servicios con Docker Compose

```bash
docker-compose up --build
```

Esto iniciará:
- **db**: PostgreSQL con schema automático (puerto 5432)
- **redis**: Redis para Celery (puerto 6379)
- **backend**: Flask server (puerto 5000)
- **celery_worker**: Worker para procesamiento asíncrono
- **frontend**: Next.js (puerto 3000)

### 4. Verificar que todos los servicios estén saludables

```bash
# Verificar estado de contenedores
docker-compose ps

# Ver logs del backend
docker-compose logs -f backend

# Ver logs del worker
docker-compose logs -f celery_worker
```

## 🧪 Flujo de Prueba Completo

### Paso 1: Acceder a la aplicación

Abrir navegador en: `http://localhost:3000`

### Paso 2: Subir archivo de prueba

1. Ir a "SUBIR CARTILLA" en el navbar
2. Seleccionar archivo XLSX o CSV con formato esperado:
   - Columnas: `id_pedido`, `numero_barra`, `longitud_pieza_requerida`, `cantidad_requerida`, `grupo_ejecucion`
3. Ingresar número de documento (ej: "12345")
4. Seleccionar perfil de optimización:
   - **Economía**: Más ahorro de material, procesamiento más lento
   - **Balanceado**: Equilibrio entre velocidad y ahorro (recomendado)
   - **Velocidad**: Procesamiento rápido, menor optimización
5. Click en "Enviar"

### Paso 3: Observar procesamiento en tiempo real

La UI mostrará:
- Barra de progreso actualizada en tiempo real vía WebSocket
- Estados: Cargado → Validando → Validado → Procesando → Generando → Completado
- Progreso: 0% → 10% → 20% → 70% → 75% → 100%

### Paso 4: Ver archivos procesados

1. Ir a "ARCHIVOS" en el navbar
2. Tabla con todos los archivos cargados
3. Filtros disponibles:
   - **Búsqueda**: Por nombre de archivo o número de documento
   - **Estado**: uploaded, processing, completed, error_*
   - **Perfil**: economia, balanceado, velocidad
   - **Rango de fechas**: Desde/Hasta

### Paso 5: Descargar resultados

Para cada archivo completado:
- **Botón Excel**: Descarga `resultados_optimizacion.xlsx`
- **Botón PDF**: Descarga `plan_de_corte.pdf` con plantilla HTML formateada
- **Botón IMG**: Descarga `grafica_cortes.png` con visualización de barras

### Paso 6: Reprocesar con diferente perfil

1. Click en botón "Reprocesar" (icono de refresh)
2. Seleccionar nuevo perfil
3. Se creará nueva versión manteniendo versiones anteriores

### Paso 7: Eliminar archivos

1. Click en botón "Eliminar" (icono de papelera)
2. Confirmar eliminación
3. Se borran:
   - Registro en base de datos (uploaded_files + processing_results CASCADE)
   - Directorios UUID del filestore
   - Archivo temporal original

## 📊 Validaciones del Sistema

El sistema valida automáticamente:

1. **Formato de archivo**: Solo XLSX y CSV
2. **Columnas requeridas**: 5 columnas esenciales
3. **Tipos de datos**: 
   - `longitud_pieza_requerida`: numérico
   - `cantidad_requerida`: numérico entero positivo
   - `masa_unitaria_kg`: numérico (si existe)
4. **Rangos de valores**:
   - Longitud: 0.1m - 100m
   - Cantidad: 1 - 10000 unidades
5. **Valores positivos**: No acepta negativos ni ceros

**Comportamiento en errores**:
- Estado cambia a `error_validation`, `error_processing` o `error_generation`
- Mensaje de error detallado en campo `status_details`
- No se generan artefactos incompletos

## 🗄️ Estructura de la Base de Datos

### Tabla: `uploaded_files`
```sql
- id (PK)
- filename
- document_number
- perfil (economia | balanceado | velocidad)
- uploaded_file_path
- status (uploaded, validating, processing, completed, error_*)
- status_details (JSONB)
- created_at, updated_at
```

### Tabla: `processing_results`
```sql
- id (PK)
- uploaded_file_id (FK)
- version_number (1, 2, 3...)
- storage_uuid (UUID v4)
- resultados_df (JSONB con DataFrame)
- metricas (JSONB con estadísticas)
- excel_path, pdf_path, image_path
- status, status_details
- created_at, updated_at
```

**Relación**: 1 UploadedFile → N ProcessingResults (versionamiento)

## 🔧 Arquitectura del Procesamiento Asíncrono

```
Cliente                Backend                 Celery Worker
  |                       |                           |
  | POST /upload          |                           |
  |--------------------->|                           |
  |                       | Guarda archivo temp       |
  |                       | Crea UploadedFile         |
  |                       | Encola tarea              |
  |<---------------------|                           |
  | {task_id, file_id}    |                           |
  |                       |                           |
  | subscribe_task        |                           |
  |--------------------->|                           |
  |                       | apply_async               |
  |                       |------------------------->|
  |                       |                           | 1. Validating (10%)
  |                       |                           | 2. Validated (20%)
  |                       |                           | 3. Processing (20-70%)
  |                       |                           | 4. Generating (75%)
  |                       |                           | 5. Completed (100%)
  |<------ task_update ---|<------ update_state ------|
  | {state, progress}     |                           |
```

## 📁 Estructura de Almacenamiento

```
data/filestore/
├── temp/                          # Archivos temporales subidos
│   └── 1234567890.123_cartilla.xlsx
└── {uuid}/                        # Directorio por versión
    ├── resultados_optimizacion.xlsx
    ├── plan_de_corte.pdf
    └── grafica_cortes.png
```

Cada reprocesamiento crea un nuevo UUID aislado.

## 🔍 Endpoints de la API

### HTTP Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/upload` | Sube archivo y encola procesamiento |
| GET | `/files` | Lista archivos con filtros y paginación |
| GET | `/file/<id>` | Detalle de archivo con todas sus versiones |
| DELETE | `/file/<id>` | Elimina archivo y todas sus versiones |
| POST | `/reprocess/<id>` | Reprocesa archivo con nuevo perfil |
| GET | `/descargar-excel/<uuid>` | Descarga Excel de resultados |
| GET | `/descargar-pdf/<uuid>` | Descarga PDF con plan de corte |
| GET | `/descargar-imagen/<uuid>` | Descarga imagen PNG de gráfica |
| GET | `/health` | Health check (verifica conexión BD) |

### WebSocket Events

| Evento | Dirección | Descripción |
|--------|-----------|-------------|
| `connect` | Cliente → Server | Cliente se conecta |
| `connected` | Server → Cliente | Confirmación de conexión |
| `subscribe_task` | Cliente → Server | Suscripción a tarea específica |
| `subscribed` | Server → Cliente | Confirmación de suscripción |
| `task_update` | Server → Cliente | Actualización de estado y progreso |

## 🐛 Troubleshooting

### Backend no inicia

```bash
# Ver logs del backend
docker-compose logs backend

# Verificar conexión a PostgreSQL
docker-compose exec backend python -c "from models import db; print(db)"
```

### Celery worker no procesa tareas

```bash
# Ver logs del worker
docker-compose logs celery_worker

# Verificar conexión a Redis
docker-compose exec backend redis-cli -h redis ping
```

### WebSocket no conecta

```bash
# Verificar en consola del navegador
# Debe mostrar: [Socket.IO] Conectado al servidor

# Verificar variable de entorno
echo $NEXT_PUBLIC_API_URL
```

### Base de datos no inicializa

```bash
# Conectar a PostgreSQL
docker-compose exec db psql -U oica_user -d oica_db

# Verificar tablas
\dt

# Debería mostrar: uploaded_files, processing_results
```

## 🔄 Reiniciar el Sistema

```bash
# Detener servicios
docker-compose down

# Limpiar volúmenes (BORRA TODOS LOS DATOS)
docker-compose down -v

# Reconstruir e iniciar
docker-compose up --build
```

## 📝 Variables de Entorno

### Backend (.env o docker-compose.yaml)
```bash
DATABASE_URL=postgresql://oica_user:oica_password@db:5432/oica_db
REDIS_URL=redis://redis:6379/0
SECRET_KEY=change-this-in-production
FLASK_DEBUG=False
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:5000
```

## 🎯 Características Implementadas

✅ Migración completa de localStorage a PostgreSQL  
✅ Procesamiento asíncrono con Celery + Redis  
✅ WebSocket para actualizaciones en tiempo real  
✅ Versionamiento de resultados con UUIDs  
✅ Validación de contenido con 5 reglas  
✅ 4 filtros en tabla de archivos  
✅ 3 botones de descarga por archivo  
✅ Reprocesamiento con diferentes perfiles  
✅ Eliminación completa (BD + filestore)  
✅ Estados granulares (8 estados)  
✅ Barra de progreso en tiempo real  
✅ Paginación de resultados  
✅ Sistema single-user sin autenticación  

## 📚 Documentación Adicional

- **Prompt de Especificación**: `tmp/prompt.md`
- **Código Antiguo**: `services/backend/main.py`, `services/backend/server_old.py`
- **Schema SQL**: `config/backend/init.sql`
- **Modelos ORM**: `services/backend/models/uploaded_file.py`
- **Worker Celery**: `services/backend/celery_worker.py`
- **Cliente WebSocket**: `services/frontend/src/lib/socket.ts`

## 🤝 Contacto y Soporte

Para dudas o problemas, revisar logs en:
```bash
docker-compose logs -f backend
docker-compose logs -f celery_worker
```
