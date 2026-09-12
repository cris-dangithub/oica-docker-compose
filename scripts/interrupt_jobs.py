"""Ejecutar únicamente con backend y worker detenidos en despliegues."""
import os
import psycopg2
import redis

message = 'Procesamiento interrumpido por actualización. Vuelve a procesar el archivo.'
with psycopg2.connect(os.environ['DATABASE_URL']) as connection:
    with connection.cursor() as cursor:
        cursor.execute("UPDATE uploaded_files SET processing_status='error_processing', status_details=%s WHERE processing_status NOT IN ('completed', 'error_validation', 'error_processing', 'error_generation')", (message,))
        print(f'Archivos interrumpidos: {cursor.rowcount}')
        cursor.execute("UPDATE processing_results SET result_status='error_generation', error_message=%s WHERE result_status='processing'", (message,))
# Redis es exclusivo de OICA. Eliminar cola y resultados evita estados antiguos
# y entregas reservadas recuperadas por el broker tras reiniciar el worker.
redis.Redis.from_url(os.environ['REDIS_URL']).flushdb()
