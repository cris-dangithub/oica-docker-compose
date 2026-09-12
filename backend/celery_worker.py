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
    """
    Tarea asíncrona para procesar archivo Excel con algoritmo genético.
    
    Args:
        self: Task instance (para actualizar progreso)
        uploaded_file_id: ID del archivo en BD
        perfil: 'rapido', 'balanceado', o 'intensivo'
    
    Returns:
        dict: Información del resultado procesado
    """
    from models import db
    from models.uploaded_file import UploadedFile, ProcessingResult
    from flask import current_app
    
    print(f"🚀 Iniciando procesamiento - File ID: {uploaded_file_id}, Perfil: {perfil}")
    
    try:
        # Crear contexto de aplicación Flask
        app = create_flask_app()
        
        with app.app_context():
            start_time = time.time()
            
            # 1. ESTADO: VALIDATING
            self.update_state(state='VALIDATING', meta={
                'progress': 10,
                'status': 'Validando archivo...',
                'phase': 'validating'
            })
            publish_progress(
                self.request.id, 10, 'VALIDATING',
                'Validando archivo...', phase='validating'
            )
            
            file_record = UploadedFile.query.get(uploaded_file_id)
            if not file_record:
                raise ValueError(f"Archivo {uploaded_file_id} no encontrado")
            
            file_record.processing_status = 'validating'
            file_record.status_details = 'Validando estructura y contenido...'
            db.session.commit()
            
            # Leer Excel
            if not os.path.exists(file_record.file_path):
                raise FileNotFoundError(f"Archivo no encontrado: {file_record.file_path}")
            
            df = pd.read_excel(file_record.file_path)
            
            # Eliminar filas completamente vacías
            df = df.dropna(how='all')
            
            # Eliminar filas donde todas las columnas numéricas son NaN
            df = df.reset_index(drop=True)
            
            # 2. VALIDAR COLUMNAS OBLIGATORIAS
            columnas_obligatorias = [
                'N° Orden', 'Elemento', 'N° de Barra',
                'Longitud total (m)', 'Cantidad', 'Masa total (kg)'
            ]
            
            missing_cols = [col for col in columnas_obligatorias if col not in df.columns]
            if missing_cols:
                file_record.processing_status = 'error_validation'
                file_record.status_details = f'Columnas faltantes: {", ".join(missing_cols)}'
                db.session.commit()
                raise ValueError(f'Columnas obligatorias faltantes: {missing_cols}')
            
            # 3. VALIDAR CONTENIDO (Pregunta 4)
            validation_errors = validate_content(df)
            if validation_errors:
                file_record.processing_status = 'error_validation'
                file_record.status_details = f'{len(validation_errors)} errores de validación'
                db.session.commit()
                raise ValueError(f'Errores de validación: {validation_errors[:5]}')  # Primeros 5
            
            self.update_state(state='VALIDATED', meta={
                'progress': 20,
                'status': 'Validación exitosa. Iniciando procesamiento...',
                'phase': 'validated'
            })
            publish_progress(
                self.request.id, 20, 'VALIDATED',
                'Validación exitosa. Iniciando procesamiento...', phase='validated'
            )
            
            # 4. ESTADO: PROCESSING
            file_record.processing_status = 'processing'
            file_record.status_details = 'Ejecutando algoritmo genético...'
            db.session.commit()
            
            # Enviar señal de vida durante preparación
            publish_progress(
                self.request.id, 20, 'PROCESSING',
                'Preparando datos para algoritmo genético...', phase='preparing'
            )
            
            # Calcular número de versión
            latest_result = ProcessingResult.query.filter_by(
                uploaded_file_id=uploaded_file_id
            ).order_by(ProcessingResult.version_number.desc()).first()
            
            version_number = (latest_result.version_number + 1) if latest_result else 1
            
            # Generar UUID para almacenamiento
            storage_uuid = str(uuid.uuid4())
            
            print(f"📊 Versión: {version_number}, UUID: {storage_uuid}")
            
            # Señal de vida: Cargando configuración
            publish_progress(
                self.request.id, 20, 'PROCESSING',
                'Cargando barras estándar...', phase='preparing'
            )
            
            # 5. EJECUTAR ALGORITMO GENÉTICO POR DIÁMETRO (INF-001)
            # El AG corre una vez por cada N° de Barra (diámetro), porque
            # físicamente no se pueden cortar piezas de distinto diámetro
            # de la misma barra. Cada diámetro usa solo sus propias longitudes
            # estándar (ver barras_estandar.json).

            from genetic_algorithm.engine import ejecutar_algoritmo_genetico
            from genetic_algorithm.input_adapter import longitudes_a_barras_dict
            from genetic_algorithm.output_formatter import formatear_salida_desde_cromosoma
            from genetic_algorithm.population import generar_individuo_heuristico_ffd
            import json, math

            # Número máximo de barras estimadas para un grupo antes de omitir la
            # evolución genética y devolver directamente la solución heurística FFD.
            # Por encima de este límite la presión evolutiva no puede navegar el
            # espacio de búsqueda en tiempo razonable y FFD ya da una solución
            # cercana al óptimo para grupos homogéneos de gran cantidad.
            MAX_BARRAS_AG = 3000

            # Cargar barras estándar desde JSON
            barras_json_path = os.path.join(os.path.dirname(__file__), 'barras_estandar.json')
            with open(barras_json_path, 'r') as f:
                barras_config = json.load(f)

            # Configuración del AG según perfil
            if perfil == 'rapido':
                config_ga = {'tamaño_poblacion': 20, 'max_generaciones': 30}
            elif perfil == 'balanceado':
                config_ga = {'tamaño_poblacion': 50, 'max_generaciones': 100}
            else:  # profundo
                config_ga = {'tamaño_poblacion': 100, 'max_generaciones': 200}

            # Inicializar desperdicios vacíos (reutilización pendiente — INF-008)
            desperdicios_previos = []

            # Agrupar por N° de Barra. preserve_order=False para procesarlos
            # en orden estable (no afecta correctness, solo log/UX).
            grupos_diametro = list(df.groupby('N° de Barra', sort=False))
            total_grupos = len(grupos_diametro)

            publish_progress(
                self.request.id, 20, 'PROCESSING',
                f'Detectados {total_grupos} diámetros distintos. Iniciando AG por grupo...',
                phase='preparing'
            )

            def make_group_progress_callback(grupo_idx, total_grupos, diametro_str):
                """Genera un callback que escala el progreso del AG (30-70%) al rango asignado al grupo actual."""
                rango_total = 40  # 30-70%
                rango_grupo = rango_total / max(total_grupos, 1)
                base_grupo = 30 + (grupo_idx - 1) * rango_grupo

                operation_names = {
                    'selection': 'Selección',
                    'crossover': 'Cruce',
                    'mutation': 'Mutación',
                    'evaluation': 'Evaluación',
                    'init_population': 'Inicializando población',
                    'eval_initial': 'Evaluando población inicial',
                }

                def cb(generation, total_generations, best_fitness=None, operation=None, current=None, total=None):
                    if total_generations and total_generations > 0:
                        within = generation / total_generations
                    else:
                        within = 0
                    progress = int(base_grupo + within * rango_grupo)
                    op_label = operation_names.get(operation, '')

                    status_msg = f'Diámetro {diametro_str} ({grupo_idx}/{total_grupos})'
                    if generation and total_generations:
                        status_msg += f' · gen {generation}/{total_generations}'
                    if op_label:
                        status_msg += f' · {op_label}'
                    if best_fitness is not None:
                        status_msg += f' (fitness: {best_fitness:.4f})'

                    self.update_state(
                        state='PROCESSING',
                        meta={
                            'progress': progress,
                            'status': status_msg,
                            'phase': 'processing',
                            'diametro': diametro_str,
                            'grupo_actual': grupo_idx,
                            'total_grupos': total_grupos,
                            'generation': generation,
                            'total_generations': total_generations,
                        }
                    )
                    publish_progress(
                        self.request.id, progress, 'PROCESSING', status_msg,
                        phase='processing', diametro=diametro_str,
                        grupo_actual=grupo_idx, total_grupos=total_grupos,
                        generation=generation, total_generations=total_generations
                    )
                    file_record.status_details = status_msg
                    db.session.commit()

                return cb

            # Acumuladores globales
            patrones_corte = []
            desperdicios_nuevos_global = []
            metricas_por_diametro = {}

            for grupo_idx, (diametro_raw, df_grupo) in enumerate(grupos_diametro, start=1):
                diametro_str = str(diametro_raw).strip()

                # Obtener barras estándar para este diámetro.
                # barras_estandar.json usa claves como "#3", "#4"... Si la cartilla
                # ya trae el "#", se respeta. Si no, se intenta agregarlo.
                if diametro_str in barras_config:
                    longitudes_diametro = barras_config[diametro_str]
                elif f'#{diametro_str}' in barras_config:
                    longitudes_diametro = barras_config[f'#{diametro_str}']
                else:
                    # Fallback: usar longitudes comerciales estándar (6, 9, 12 m).
                    # Se registra advertencia para que se vea en logs.
                    print(f'[WARN] Diámetro "{diametro_str}" no está en barras_estandar.json. Usando longitudes 6/9/12 m.')
                    longitudes_diametro = [6.0, 9.0, 12.0]

                barras_disponibles = longitudes_a_barras_dict(longitudes_diametro)

                # Densidad lineal (kg/m) derivada de la cartilla del propio grupo.
                # masa_kg_por_metro = sum(masa_total) / sum(cantidad * longitud)
                metros_grupo = (df_grupo['Cantidad'] * df_grupo['Longitud total (m)']).sum()
                masa_grupo = df_grupo['Masa total (kg)'].sum()
                masa_por_metro = (masa_grupo / metros_grupo) if metros_grupo > 0 else 0.0

                # Construir df_ag solo con piezas de este diámetro
                df_ag = pd.DataFrame({
                    'id_pedido': df_grupo['N° Orden'].astype(str),
                    'longitud_pieza_requerida': df_grupo['Longitud total (m)'],
                    'cantidad_requerida': df_grupo['Cantidad'].astype(int)
                })

                publish_progress(
                    self.request.id,
                    int(30 + (grupo_idx - 1) * (40 / max(total_grupos, 1))),
                    'PROCESSING',
                    f'Optimizando diámetro {diametro_str} ({grupo_idx}/{total_grupos}, {len(df_grupo)} órdenes)',
                    phase='processing'
                )

                grupo_callback = make_group_progress_callback(grupo_idx, total_grupos, diametro_str)

                # Estimar barras mínimas necesarias para este grupo.
                # Si supera MAX_BARRAS_AG se omite la evolución y se devuelve la
                # solución FFD directamente: para grupos muy grandes la evolución
                # genética no puede converger en tiempo razonable y FFD ya ofrece
                # una solución cercana al óptimo.
                max_barra_diametro = max(b['longitud'] for b in barras_disponibles)
                total_m_grupo = (
                    df_ag['cantidad_requerida'] * df_ag['longitud_pieza_requerida']
                ).sum()
                barras_estimadas = math.ceil(total_m_grupo / max_barra_diametro)

                if barras_estimadas > MAX_BARRAS_AG:
                    print(
                        f'[INFO] Grupo {diametro_str}: ~{barras_estimadas} barras estimadas '
                        f'> {MAX_BARRAS_AG} — usando solución FFD directa (sin evolución).'
                    )
                    mejor_cromosoma_grupo = generar_individuo_heuristico_ffd(
                        df_ag, barras_disponibles, desperdicios_previos
                    )
                    metricas_grupo = {
                        'generaciones_ejecutadas': 0,
                        'metodo': 'heuristica_ffd',
                        'razon_fallback': f'barras_estimadas={barras_estimadas} > MAX_BARRAS_AG={MAX_BARRAS_AG}',
                    }
                else:
                    mejor_cromosoma_grupo, metricas_grupo = ejecutar_algoritmo_genetico(
                        df_ag,
                        barras_disponibles,
                        desperdicios_previos,
                        config_ga=config_ga,
                        progress_callback=grupo_callback
                    )

                patrones_grupo, desperdicios_grupo = formatear_salida_desde_cromosoma(mejor_cromosoma_grupo)

                # Enriquecer cada patrón con info del diámetro y masa por metro
                for patron in patrones_grupo:
                    patron['diametro'] = diametro_str
                    patron['masa_por_metro_kg'] = masa_por_metro

                patrones_corte.extend(patrones_grupo)
                desperdicios_nuevos_global.extend(desperdicios_grupo)
                metricas_por_diametro[diametro_str] = metricas_grupo

            # Métricas globales
            desperdicios_nuevos = desperdicios_nuevos_global
            metricas = {
                'por_diametro': metricas_por_diametro,
                'total_grupos': total_grupos,
                'total_patrones': len(patrones_corte),
            }

            # DataFrame de resultados (para cartilla de resultados en BD)
            resultados_df = pd.DataFrame(patrones_corte)
            
            # 6. ESTADO: GENERATING ARTIFACTS
            self.update_state(state='GENERATING', meta={
                'progress': 70,
                'status': 'Preparando generación de artefactos...',
                'phase': 'generating_artifacts'
            })
            publish_progress(
                self.request.id, 70, 'GENERATING',
                'Preparando generación de artefactos...', phase='generating_artifacts'
            )
            
            file_record.processing_status = 'generating_artifacts'
            file_record.status_details = 'Generando artefactos (PDF, imagen, Excel)...'
            db.session.commit()
            
            # 7. GENERAR ARTEFACTOS CON CALLBACKS GRANULARES
            
            # 7.1. Preparar datos
            publish_progress(
                self.request.id, 72, 'GENERATING',
                'Transformando datos para artefactos...', phase='generating_artifacts'
            )
            
            upload_path = os.environ.get('UPLOAD_PATH', '/usr/src/app/data/filestore')
            
            # Transformar resultados_df al formato esperado por artifact_generator
            # Formato esperado: numero_barra, barra_origen_longitud, cortes_realizados (lista), 
            #                   cantidad_requerida, masa_unitaria_kg, desperdicio_m
            
            transformed_data = []
            for idx, patron in enumerate(patrones_corte, start=1):
                barra_longitud = patron['barra_origen_longitud']
                cortes = patron['cortes_realizados']
                desperdicio = patron['desperdicio_resultante']
                diametro = patron.get('diametro', '')

                # Masa real del segmento usando densidad lineal del propio grupo
                # de diámetro (derivada de la cartilla en el bucle por grupo).
                masa_por_metro = patron.get('masa_por_metro_kg', 0.0)
                masa_kg = barra_longitud * masa_por_metro

                transformed_data.append({
                    'numero_barra': idx,
                    'diametro': diametro,
                    'barra_origen_longitud': barra_longitud,
                    'cortes_realizados': cortes,
                    'cantidad_requerida': len(cortes),
                    'masa_unitaria_kg': round(masa_kg, 2),
                    'desperdicio_m': desperdicio
                })
            
            resultados_df_formatted = pd.DataFrame(transformed_data)
            
            # 7.2. Generar Excel
            publish_progress(
                self.request.id, 75, 'GENERATING',
                'Generando archivo Excel...', phase='generating_artifacts'
            )
            
            # Generar artefactos
            try:
                from utils.artifact_generator import generar_artefactos_completos
                
                # 7.3. Generar gráfica y PDF
                publish_progress(
                    self.request.id, 80, 'GENERATING',
                    'Generando gráfica y PDF...', phase='generating_artifacts'
                )
                
                # 7.3. Generar gráfica y PDF
                publish_progress(
                    self.request.id, 80, 'GENERATING',
                    'Generando gráfica y PDF...', phase='generating_artifacts'
                )
                
                excel_path, pdf_path, image_path = generar_artefactos_completos(
                    resultados_df=resultados_df_formatted,
                    storage_uuid=storage_uuid,
                    filestore_base=upload_path,
                    document_number=file_record.document_number or file_record.file_name
                )
                
                artifact_success = True
                print(f"✅ Artefactos generados: Excel, PDF, Imagen")
                
                # 7.4. Guardar en base de datos
                publish_progress(
                    self.request.id, 90, 'GENERATING',
                    'Guardando resultados en base de datos...', phase='saving'
                )
            except Exception as artifact_error:
                print(f"⚠️ Error generando artefactos: {artifact_error}")
                import traceback
                traceback.print_exc()
                artifact_success = False
                excel_path = pdf_path = image_path = None
            
            total_time = time.time() - start_time
            
            # 8. GUARDAR EN BD
            result_status = 'completed' if artifact_success else 'error_generation'
            
            processing_result = ProcessingResult(
                uploaded_file_id=uploaded_file_id,
                version_number=version_number,
                storage_uuid=storage_uuid,
                resultados=resultados_df.to_dict(orient='records'),
                metricas=metricas,
                cartilla=df.to_dict(orient='records'),
                excel_path=excel_path,
                graph_image_path=image_path,
                pdf_path=pdf_path,
                perfil_usado=perfil,
                processing_time_seconds=total_time,
                result_status=result_status,
                error_message=None if artifact_success else 'Error generando artefactos',
                pdf_template_version='v1.0.0'
            )
            
            db.session.add(processing_result)
            
            file_record.processing_status = 'completed'
            file_record.status_details = f'Procesamiento completado en {total_time:.2f}s'
            db.session.commit()
            
            # 9. ACTUALIZAR PROGRESO FINAL
            self.update_state(state='SUCCESS', meta={
                'progress': 100,
                'status': 'Completado exitosamente',
                'phase': 'completed',
                'result_id': processing_result.id,
                'storage_uuid': storage_uuid,
                'version_number': version_number
            })
            publish_progress(
                self.request.id, 100, 'SUCCESS',
                'Completado exitosamente', phase='completed',
                result_id=processing_result.id, storage_uuid=storage_uuid
            )
            
            print(f"✅ Procesamiento completado - Result ID: {processing_result.id}")
            
            return {
                'result_id': processing_result.id,
                'status': 'completed',
                'storage_uuid': storage_uuid,
                'version_number': version_number,
                'processing_time': total_time
            }
    
    except Exception as e:
        print(f"❌ Error en procesamiento: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Actualizar estado de error
        try:
            app = create_flask_app()
            with app.app_context():
                file_record = UploadedFile.query.get(uploaded_file_id)
                if file_record:
                    file_record.processing_status = 'error_processing'
                    file_record.status_details = f'Error: {str(e)[:200]}'
                    db.session.commit()
        except:
            pass
        
        self.update_state(
            state='FAILURE',
            meta={
                'progress': 0,
                'status': f'Error: {str(e)}',
                'phase': 'error',
                'error': str(e)
            }
        )
        publish_progress(
            self.request.id, 0, 'FAILURE',
            f'Error: {str(e)}', phase='error', error=str(e)
        )
        
        raise


if __name__ == '__main__':
    # Para ejecutar worker: celery -A celery_worker.celery worker --loglevel=info
    print("Celery Worker configurado. Usa: celery -A celery_worker.celery worker --loglevel=info")
