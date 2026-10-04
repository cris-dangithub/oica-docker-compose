#!/usr/bin/env python3
"""Tiempo de la vista de patrones del explorador sin reconstruir imágenes (spec 002, SC-009; tarea T025).

Carga `backend/cutting` del árbol de trabajo en memoria dentro del contenedor del backend (como
`check_cutting_container.py`) y, en solo lectura, mide sobre una versión guardada:
la lectura de `resultados` y `metricas` desde PostgreSQL, `vista_patrones.vista(...)` y el total.
No escribe en la base. El resumen se crea de forma exclusiva (nunca sobrescribe).

Por defecto elige la versión `secuencial-2` válida con más barras (la cartilla 002 en el stack local).
"""
import argparse
import importlib.util
import json
from pathlib import Path
import statistics
import subprocess

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location('check_cutting_container', ROOT / 'scripts/check_cutting_container.py')
harness = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(harness)

RUNNER = harness.FINDER + r'''
import time
from server import app, db
from models.uploaded_file import ProcessingResult
from cutting.vista_patrones import vista
with app.app_context():
    candidato = payload['resultado_id']
    if candidato is None:
        filas = db.session.query(ProcessingResult.id, ProcessingResult.metricas).filter_by(result_status='completed').all()
        validas = [(m.get('barras', 0), i) for i, m in filas
                   if m and m.get('motor') == 'secuencial-2' and m.get('valido') is True]
        candidato = max(validas)[1]
    for _ in range(payload['repeticiones']):
        db.session.expire_all()
        inicio = time.perf_counter()
        registro = db.session.get(ProcessingResult, candidato)
        resultados, metricas = registro.resultados, registro.metricas
        leido = time.perf_counter()
        v = vista(resultados, metricas)
        fin = time.perf_counter()
        texto = json.dumps(v, ensure_ascii=False)
        print(json.dumps({'resultado_id': candidato, 'storage_uuid': registro.storage_uuid,
                          'motor': metricas.get('motor'), 'valido': metricas.get('valido'),
                          'lectura_s': leido - inicio, 'vista_s': fin - leido, 'total_s': fin - inicio,
                          'json_bytes': len(texto.encode()), 'patrones': v['totales']['patrones'],
                          'barras': v['totales']['barras'],
                          'rangos': sum(len(p['barras']['rangos']) for p in v['patrones']),
                          'pedidos': len(v['pedidos']),
                          'vista': v if payload['incluir_vista'] else None}, ensure_ascii=False), flush=True)
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--container', default='oica-validation-backend-1')
    parser.add_argument('--resultado-id', type=int, help='Id de ProcessingResult; por defecto, el de más barras')
    parser.add_argument('--repeticiones', type=int, default=3)
    parser.add_argument('--output', required=True, help='Resumen JSON nuevo en tests/benchmarks/ (no se sobrescribe)')
    parser.add_argument('--vista-json', help='Guardar también la respuesta de la vista (fuera del repositorio)')
    args = parser.parse_args()
    sources = {('cutting' if p.stem == '__init__' else 'cutting.' + p.stem): p.read_text()
               for p in (ROOT / 'backend/cutting').glob('*.py')}
    payload = {'sources': sources, 'resultado_id': args.resultado_id, 'repeticiones': args.repeticiones,
               'incluir_vista': bool(args.vista_json)}
    if Path(args.output).exists():
        parser.error(f'{args.output} ya existe: la evidencia no se sobrescribe')
    process = subprocess.run(['docker', 'exec', '-i', args.container, 'python', '-B', '-c', RUNNER],
                             input=json.dumps(payload), capture_output=True, text=True, check=True)
    medidas = [json.loads(line) for line in process.stdout.splitlines() if line.startswith('{')]
    if args.vista_json:
        Path(args.vista_json).write_text(json.dumps(medidas[-1]['vista'], ensure_ascii=False), encoding='utf-8')
    for m in medidas:
        m.pop('vista')
    totales = [m['total_s'] for m in medidas]
    resumen = {'tarea': 'T025', 'criterio': 'SC-009: mediana total ≤ 2 s con la cartilla 002',
               'descripcion': 'Lectura de resultados y metricas desde PostgreSQL + vista_patrones.vista, '
                              'código del árbol de trabajo cargado en memoria; solo lectura',
               'mediciones': medidas, 'mediana_total_s': statistics.median(totales),
               'mediana_lectura_s': statistics.median(m['lectura_s'] for m in medidas),
               'mediana_vista_s': statistics.median(m['vista_s'] for m in medidas)}
    resumen['cumple'] = resumen['mediana_total_s'] <= 2
    with open(args.output, 'x', encoding='utf-8') as output:
        json.dump(resumen, output, ensure_ascii=False, indent=1)
        output.write('\n')
    print(f"Versión {medidas[0]['resultado_id']}: {medidas[0]['patrones']} patrones, {medidas[0]['barras']} barras, "
          f"{medidas[0]['rangos']} rangos, {medidas[0]['pedidos']} pedidos, {medidas[0]['json_bytes']} bytes de JSON; "
          f"mediana total {resumen['mediana_total_s']:.3f} s (lectura {resumen['mediana_lectura_s']:.3f} s, "
          f"vista {resumen['mediana_vista_s']:.3f} s); cumple SC-009: {resumen['cumple']}")
    if not resumen['cumple']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
