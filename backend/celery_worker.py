"""
Celery Worker Configuration
Procesa tareas asíncronas de procesamiento de archivos
"""
import os
import uuid
import time
import json
import redis
import pandas as pd
import shutil
from celery import Celery
from datetime import datetime

# Crear instancia de Celery
celery = Celery(
    'oica_tasks',
    broker=os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
    backend=os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
)

# Export para importación en server.py
celery_app = celery

celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='America/Bogota',
    enable_utc=True,
    task_track_started=True,
    task_send_sent_event=True,
    worker_prefetch_multiplier=1,
    task_default_queue='oica',
    broker_connection_retry_on_startup=True
)

# Cliente Redis para Pub/Sub (progreso en tiempo real)
redis_client = redis.Redis.from_url(
    os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
    decode_responses=True
)


# ============================================================================
# FUNCIONES HELPER (deben estar ANTES de process_file_task)
# ============================================================================

def publish_progress(task_id, progress, state, message, **extra_data):
    """
    Publica actualización de progreso a Redis Pub/Sub para WebSocket.
    También almacena el progreso en Redis con TTL de 5 minutos.
    
    Args:
        task_id: ID de la tarea Celery
        progress: Porcentaje de progreso (0-100)
        state: Estado de la tarea (VALIDATING, PROCESSING, etc.)
        message: Mensaje descriptivo
        **extra_data: Datos adicionales opcionales
    """
    try:
        data = {
            'task_id': task_id,
            'progress': progress,
            'state': state,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            **extra_data
        }
        
        # 1. Publicar a canal Pub/Sub para WebSocket en tiempo real
        channel = f'task_progress:{task_id}'
        redis_client.publish(channel, json.dumps(data))
        
        # 2. Almacenar en Redis como clave para consultas HTTP
        redis_client.setex(
            f'task_progress:{task_id}',  # key
            300,  # TTL: 5 minutos (300 segundos)
            json.dumps(data)
        )
        
        print(f'[Celery] Publicado progreso {progress}% para {task_id}')
    except Exception as e:
        print(f'[Celery] Error publicando progreso: {e}')


def validate_content(df):
    """
    Valida el contenido del DataFrame según Pregunta 4.
    
    Returns:
        list: Lista de errores encontrados (vacía si todo OK)
    """
    errors = []
    
    # Validar tipos y valores positivos (con rangos)
    numeric_cols_with_range = {
        'Longitud total (m)': (0.1, 100),  # min, max
        'Masa total (kg)': (0.01, 50000)
    }
    
    # Validar solo tipo y valor positivo (sin rango)
    numeric_cols_no_range = ['Cantidad']
    
    # Validar columnas con rango
    for col, (min_val, max_val) in numeric_cols_with_range.items():
        if col in df.columns:
            # Convertir a numérico
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Verificar NaN
            nan_rows = df[df[col].isna()].index.tolist()
            if nan_rows:
                errors.append(f"{col}: valores no numéricos en filas {nan_rows[:5]}")
            
            # Verificar positivos
            negative_rows = df[df[col] <= 0].index.tolist()
            if negative_rows:
                errors.append(f"{col}: valores negativos o cero en filas {negative_rows[:5]}")
            
            # Verificar rangos
            out_of_range = df[(df[col] < min_val) | (df[col] > max_val)].index.tolist()
            if out_of_range:
                errors.append(f"{col}: valores fuera de rango [{min_val}-{max_val}] en filas {out_of_range[:5]}")
    
    # Validar columnas sin rango (solo tipo y positivo)
    for col in numeric_cols_no_range:
        if col in df.columns:
            # Convertir a numérico
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Verificar NaN
            nan_rows = df[df[col].isna()].index.tolist()
            if nan_rows:
                errors.append(f"{col}: valores no numéricos en filas {nan_rows[:5]}")
            
            # Verificar positivos
            negative_rows = df[df[col] <= 0].index.tolist()
            if negative_rows:
                errors.append(f"{col}: valores negativos o cero en filas {negative_rows[:5]}")
    
    return errors


def create_flask_app():
    """Crea instancia de aplicación Flask para contexto"""
    from flask import Flask
    
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    from models import db
    db.init_app(app)
    
    return app


# ============================================================================
# TAREA PRINCIPAL DE CELERY
# ============================================================================

@celery.task(bind=True, name='oica_tasks.process_file_task')
def process_file_task(self, uploaded_file_id, perfil):
    """Ejecuta la misma planificación secuencial que el comando de experimentos."""
    from models import db, UploadedFile, ProcessingResult
    from cutting.domain import normalize
    from cutting.io import read_rows, file_hash
    from cutting.optimizer import optimize
    from cutting.report import generate, legacy_patterns
    from cutting.estimation import environment_key, estimate
    from sqlalchemy import text

    app = create_flask_app()
    with app.app_context():
        record = db.session.get(UploadedFile, uploaded_file_id)
        if record is None:
            raise ValueError('Archivo inexistente')
        started = time.perf_counter()
        last_publish, last_commit, last_phase = 0.0, 0.0, None
        samples = []
        env_key = environment_key()
        redis_client.set('cutting_environment_key', env_key)
        problem = None
        lock_connection = db.engine.connect()
        locked = lock_connection.execute(text('SELECT pg_try_advisory_lock(:id)'),
                                         {'id': uploaded_file_id}).scalar()
        lock_connection.commit()
        if not locked:
            lock_connection.close()
            return {'status': 'already_running', 'file_id': uploaded_file_id}
        def progress(data=None, phase='processing', message=None, force=False):
            nonlocal last_publish, last_commit, last_phase
            data = data or {}
            now = time.perf_counter()
            phase = data.get('phase', phase)
            current_stage = data.get('diametro', phase)
            changed = current_stage != last_phase
            if not force and not changed and now - last_publish < 1:
                return
            elapsed = now - started
            done = data.get('diameters_done', 0)
            total = data.get('diameters_total', 1)
            label = message or f"{data.get('diametro', '')} · {phase} · generación {data.get('generation', 0)}"
            pct = 90 if phase == 'generating_artifacts' else int(15 + 70 * done / max(total, 1))
            meta = {'progress': pct, 'status': label, 'phase': phase, 'elapsed_seconds': elapsed,
                    **estimate(samples, elapsed)}
            state = 'GENERATING' if phase == 'generating_artifacts' else 'PROCESSING'
            self.update_state(state=state, meta=meta)
            publish_progress(self.request.id, pct, state, label,
                             **{k: v for k, v in meta.items() if k not in ('progress', 'status')})
            last_publish = now
            # Las suboperaciones del AG no fuerzan escrituras en cada generación.
            if force or now - last_commit >= 5:
                record.status_details = label[:255]
                db.session.commit()
                last_commit = now
            last_phase = current_stage
        try:
            # Exclusión por archivo: protege versiones incluso ante redelivery de Celery.
            record.processing_status = 'validating'
            record.active_task_id = self.request.id
            record.active_profile = perfil
            db.session.commit()
            config = record.execution_config or {}
            rows = read_rows(record.file_path)
            problem = normalize(rows, config.get('catalog'), config.get('inventory'))
            snapshot = {**config, 'input_hash': problem['hash'], 'file_sha256': file_hash(record.file_path),
                        'environment_key': env_key, 'seed': config.get('seed', 0)}
            # Solo muestras del mismo problema, perfil, código y entorno.
            previous = ProcessingResult.query.filter_by(perfil_usado=perfil, result_status='completed').order_by(
                ProcessingResult.id.desc()).limit(200).all()
            samples = [r.metricas.get('pipeline_seconds') for r in previous
                       if r.execution_config and r.execution_config.get('input_hash') == problem['hash']
                       and r.execution_config.get('environment_key') == env_key
                       and r.execution_config.get('visuals', True) == config.get('visuals', True)]
            record.processing_status = 'processing'
            progress(phase='preparing', message='Cartilla e inventario validados', force=True)
            result = optimize(problem, perfil, snapshot['seed'], callback=progress)
            record.processing_status = 'generating_artifacts'
            progress(phase='generating_artifacts', message='Generando Excel e inventario final', force=True)
            storage_uuid = str(uuid.uuid4())
            directory = os.path.join(os.environ.get('UPLOAD_PATH', '/usr/src/app/data/filestore'), storage_uuid)
            artifacts_started = time.perf_counter()
            files = {}
            artifact_error = None
            try:
                files = generate(problem, result, directory, record.file_name, config.get('visuals', True))
            except Exception as error:
                artifact_error = str(error)
                # Retener los artefactos que sí se alcanzaron a generar.
                for key, name in [('excel_path', 'resultados_optimizacion.xlsx'),
                                  ('inventory_path', 'inventario_final.xlsx'),
                                  ('pdf_path', 'plan_corte.pdf'), ('graph_image_path', 'grafica_cortes.png')]:
                    path = os.path.join(directory, name)
                    files[key] = path if os.path.isfile(path) and os.path.getsize(path) else None
            result['metrics']['artifacts_seconds'] = time.perf_counter() - artifacts_started
            result['metrics']['pipeline_seconds'] = time.perf_counter() - started
            latest = ProcessingResult.query.filter_by(uploaded_file_id=uploaded_file_id).order_by(
                ProcessingResult.version_number.desc()).first()
            version = latest.version_number + 1 if latest else 1
            saved = ProcessingResult(uploaded_file_id=uploaded_file_id, version_number=version,
                storage_uuid=storage_uuid, resultados=legacy_patterns(problem, result),
                cartilla=[rows[o['row_id'] - 2] for o in problem['orders']],
                metricas=result['metrics'], execution_config=snapshot,
                perfil_usado=perfil, processing_time_seconds=time.perf_counter() - started,
                result_status='error_generation' if artifact_error else 'completed',
                error_message=artifact_error, pdf_template_version='secuencial-1', **files)
            db.session.add(saved)
            record.processing_status = saved.result_status
            record.status_details = ('Plan validado; error en artefactos: ' + artifact_error)[:255] if artifact_error else 'Plan y artefactos completados'
            db.session.commit()
            response = {'status': saved.result_status, 'storage_uuid': storage_uuid,
                        'version_number': version, 'result_id': saved.id,
                        'processing_time': result['metrics']['pipeline_seconds']}
            publish_progress(self.request.id, 100, 'error_generation' if artifact_error else 'SUCCESS',
                             record.status_details, phase='completed', error=artifact_error,
                             elapsed_seconds=time.perf_counter() - started, **response)
            return response
        except Exception as error:
            db.session.rollback()
            record.processing_status = 'error_validation' if problem is None else 'error_processing'
            record.status_details = str(error)[:255]
            db.session.commit()
            publish_progress(self.request.id, 0, 'FAILURE', str(error), error=str(error), phase='error')
            raise
        finally:
            # Libera cualquier lock de sesión adquirido por esta tarea.
            lock_connection.execute(text('SELECT pg_advisory_unlock(:id)'), {'id': uploaded_file_id})
            lock_connection.commit()
            lock_connection.close()


if __name__ == '__main__':
    # Para ejecutar worker: celery -A celery_worker.celery worker --loglevel=info
    print("Celery Worker configurado. Usa: celery -A celery_worker.celery worker --loglevel=info")
