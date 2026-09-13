"""Verifica demanda, diámetros, conservación de longitud y artefactos del smoke.
Lee la BD y los archivos existentes; --delete elimina solo las cartillas smoke
al terminar, y se utiliza únicamente dentro del entorno desechable de CI.
"""
from collections import Counter
from pathlib import Path
import math
import os
import sys
import urllib.request
import psycopg2


def identifier(value):
    return str(value).lstrip('#').removesuffix('.0')


with psycopg2.connect(os.environ['DATABASE_URL']) as connection:
    connection.set_session(readonly=True)
    with connection.cursor() as cursor:
        cursor.execute("""SELECT f.id, r.resultados, r.cartilla, r.excel_path,
                                 r.pdf_path, r.graph_image_path, r.inventory_path, r.metricas
                          FROM processing_results r JOIN uploaded_files f
                          ON f.id = r.uploaded_file_id
                          WHERE f.file_name = 'smoke.xlsx'
                          ORDER BY f.id, r.version_number""")
        rows = cursor.fetchall()
assert rows, 'No hay resultados del smoke para verificar'
for file_id, patterns, orders, excel, pdf, png, inventory, metrics in rows:
    expected = Counter()
    actual = Counter()
    for order in orders:
        key = (identifier(order['N° de Barra']), identifier(order['N° Orden']),
               round(float(order['Longitud total (m)']), 6))
        expected[key] += int(order['Cantidad'])
    for pattern in patterns:
        diameter = identifier(pattern['diametro'])
        cuts = pattern['cortes_realizados']
        assert math.isclose(sum(cuts) + pattern['desperdicio_resultante'],
                            pattern['barra_origen_longitud'], abs_tol=0.001)
        assert pattern['desperdicio_resultante'] >= -0.001
        assert len(cuts) == len(pattern['piezas_obtenidas'])
        for piece in pattern['piezas_obtenidas']:
            key = (diameter, identifier(piece['id_pedido']), round(float(piece['longitud']), 6))
            actual[key] += 1
    assert actual == expected, f'Demanda o diámetro incorrecto: {actual - expected}; faltan {expected - actual}'
    for name, signature in ((excel, b'PK'), (pdf, b'%PDF'), (png, b'\x89PNG')):
        with Path(name).open('rb') as artifact:
            assert artifact.read(len(signature)) == signature, name
    if metrics.get('motor') == 'secuencial-1':
        assert metrics['valido'] and metrics['piezas'] == sum(expected.values())
        assert len({p['bar_id'] for p in patterns}) == len(patterns)
        for pattern in patterns:
            stages = [p['grupo_ejecucion'] for p in pattern['piezas_obtenidas']]
            assert stages == sorted(stages), 'Etapas fuera de orden'
        assert Path(inventory).read_bytes().startswith(b'PK')
print(f'OK: {len(rows)} versiones conservan demanda, diámetro, longitudes y artefactos.')
if '--delete' in sys.argv:
    for file_id in sorted({row[0] for row in rows}):
        request = urllib.request.Request(f'http://localhost:5000/file/{file_id}', method='DELETE')
        with urllib.request.urlopen(request, timeout=10) as response:
            assert response.status == 200
    print('OK: eliminación de las cartillas de prueba de CI.')
