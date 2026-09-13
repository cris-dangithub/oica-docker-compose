"""Audita una versión persistida, sin cambiar archivos ni datos.

Uso: docker compose exec -T backend python - ID < scripts/verify_sequential_result.py
"""
from collections import Counter
from decimal import Decimal
import json
import os
import sys

import pandas as pd
import psycopg2

from cutting.domain import normalize, validate
from cutting.io import read_rows


def main():
    file_id = int(sys.argv[1])
    with psycopg2.connect(os.environ['DATABASE_URL']) as connection:
        with connection.cursor() as cursor:
            cursor.execute('''SELECT f.file_path, r.execution_config, r.resultados,
                r.metricas, r.inventory_path, r.excel_path, r.version_number
                FROM uploaded_files f JOIN processing_results r ON r.uploaded_file_id=f.id
                WHERE f.id=%s ORDER BY r.version_number''', (file_id,))
            versions = cursor.fetchall()
    if not versions:
        raise ValueError('Archivo sin versiones')
    for path, config, patterns, metrics, inventory, excel, version in versions:
        if metrics.get('motor') != 'secuencial-1':
            raise ValueError('Esta auditoría requiere el motor secuencial')
        problem = normalize(read_rows(path), config.get('catalog'), config.get('inventory'))
        assert problem['hash'] == config['input_hash'], 'Entradas diferentes de la instantánea'
        orders = {o['row_id']: o for o in problem['orders']}
        scale = problem['scale']
        def units(value):
            scaled = Decimal(str(value)) * scale
            assert scaled == scaled.to_integral_value(), 'Precisión de longitud alterada'
            return int(scaled)
        bars = []
        for pattern in patterns:
            cuts = []
            assert len(pattern['cortes_realizados']) == len(pattern['piezas_obtenidas'])
            for length, piece in zip(pattern['cortes_realizados'], pattern['piezas_obtenidas']):
                assert units(length) == units(piece['longitud'])
                order = orders[piece['row_id']]
                assert str(piece['id_pedido']) == order['pedido']
                cuts.append({'row_id': piece['row_id'], 'grupo': piece['grupo_ejecucion'],
                             'longitud': units(length), 'cantidad': 1})
            bars.append({'bar_id': pattern['bar_id'], 'stock_id': pattern['stock_id'],
                         'diametro': pattern['diametro'], 'longitud': units(pattern['barra_origen_longitud']),
                         'remaining': units(pattern['desperdicio_resultante']), 'cuts': cuts})
        checked = validate(problem, bars, read_rows(inventory))
        for key in ('piezas', 'barras', 'desperdicio_porcentaje', 'masa_inicial_kg', 'sobrante_final_kg'):
            assert abs(checked[key] - metrics[key]) < 1e-7, f'Métrica persistida incorrecta: {key}'
        cuts = pd.read_excel(excel, sheet_name='Cortes').to_dict('records')
        demand = Counter()
        for cut in cuts:
            order = orders[cut['fila_origen']]
            assert cut['grupo_ejecucion'] == order['grupo']
            assert cut['diametro'] == order['diametro']
            assert units(cut['longitud_m']) == order['longitud']
            demand[cut['fila_origen']] += cut['cantidad']
        assert demand == Counter({o['row_id']: o['cantidad'] for o in orders.values()})
        print(json.dumps({'file_id': file_id, 'version': version, 'perfil': metrics['perfil'],
                          'valido': checked['valido'], 'piezas': checked['piezas'],
                          'barras': checked['barras'], 'desperdicio_porcentaje': checked['desperdicio_porcentaje'],
                          'motor_segundos': metrics['duracion_segundos'],
                          'artefactos_segundos': metrics.get('artifacts_seconds'),
                          'pipeline_segundos': metrics.get('pipeline_seconds')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
