#!/usr/bin/env python3
"""Cota inferior por patrones de los ensayos ya registrados, sin ejecutar el AG (spec 001, FR-017).

Lee las líneas base JSONL, normaliza cada cartilla con los `parametros_corte` del registro
(`None` en el escenario ideal) y calcula la cota con `cutting.bound`, cargando el código en
memoria dentro del contenedor (como `check_cutting_container.py`). Compara la cota con el
desperdicio registrado del proyecto y de cada diámetro. Requiere scipy en la imagen.

Escribe un JSONL nuevo (nunca sobrescribe) y sale con código 1 si algún registro queda por
debajo de su cota o si la cota no se pudo calcular.
"""
import argparse
import base64
import importlib.util
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BASES = ['tests/benchmarks/2026-09-13-fisico-matriz-final.jsonl',
         'tests/benchmarks/2026-09-13-fisico-control-cizalla.jsonl',
         'tests/benchmarks/2026-09-13-fisico-control-fin-etapa.jsonl']
CAMPOS = ('dataset', 'escenario', 'metodo', 'perfil', 'seed', 'parametros_corte',
          'desperdicio_porcentaje', 'por_diametro')

_spec = importlib.util.spec_from_file_location('check_cutting_container', ROOT / 'scripts/check_cutting_container.py')
harness = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(harness)

RUNNER = harness.FINDER + r'''
from cutting.domain import normalize
from cutting.io import read_rows
from cutting.parameters import defaults
from cutting.bound import cota_plan
from cutting.analysis import evaluar_admisibilidad
allowed = set(defaults())
contents = {d['name']: base64.b64decode(d['content']) for d in payload['datasets']}
cache = {}
for record in payload['records']:
    options = None if record['escenario'] == 'ideal' else {
        k: v for k, v in record['parametros_corte'].items() if k in allowed}
    key = (record['dataset'], json.dumps(options, sort_keys=True))
    if key not in cache:
        problem = normalize(read_rows(io.BytesIO(contents[record['dataset']]), record['dataset']), options=options)
        # La cota no depende de la semilla ni del perfil: una vez por (cartilla, condiciones).
        cache[key] = (problem, cota_plan(problem, {'por_diametro': record['por_diametro']}))
    problem, cota = cache[key]
    plan = evaluar_admisibilidad(problem, record, None)
    filas, ok = [], cota['estado'] == 'calculada'
    for item in cota['por_diametro']:
        plan_pct = next(e['desperdicio_pct'] for e in plan['por_diametro'] if e['diametro'] == item['diametro'])
        brecha = None if item['desperdicio_pct'] is None else plan_pct - item['desperdicio_pct']
        ok = ok and brecha is not None and brecha >= -1e-9
        filas.append({'diametro': item['diametro'], 'desperdicio_plan_pct': plan_pct,
                      'cota_pct': item['desperdicio_pct'], 'simple_pct': item['simple']['desperdicio_pct'],
                      'brecha_pp': brecha, 'ajustada': item['ajustada'],
                      'segundos': item.get('segundos'), 'iteraciones': item.get('iteraciones')})
    proyecto = cota['proyecto']
    brecha = None if proyecto['desperdicio_pct'] is None else record['desperdicio_porcentaje'] - proyecto['desperdicio_pct']
    ok = ok and brecha is not None and brecha >= -1e-9
    print(json.dumps({'dataset': record['dataset'], 'escenario': record['escenario'], 'metodo': record['metodo'],
                      'perfil': record['perfil'], 'seed': record['seed'], 'estado': cota['estado'],
                      'motivo': cota['motivo'], 'ajustada': cota['ajustada'],
                      'desperdicio_plan_pct': record['desperdicio_porcentaje'],
                      'cota_pct': proyecto['desperdicio_pct'], 'simple_pct': proyecto['simple_desperdicio_pct'],
                      'brecha_pp': brecha, 'por_diametro': filas, 'ok': ok}, ensure_ascii=False), flush=True)
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--container', default='oica-validation-celery_worker-1')
    parser.add_argument('--base', action='append', help='Línea base JSONL (repetible); por defecto, las tres de 2026-09-13')
    parser.add_argument('--output', required=True, help='JSONL nuevo en tests/benchmarks/ (no se sobrescribe)')
    args = parser.parse_args()
    records = [{k: r[k] for k in CAMPOS} for path in (args.base or BASES)
               for r in map(json.loads, (ROOT / path).read_text(encoding='utf-8').splitlines()) if r]
    names = sorted({r['dataset'] for r in records})
    unknown = [n for n in names if n not in harness.DATASETS]
    if unknown:
        parser.error(f'Dataset desconocido en la línea base: {unknown}')
    sources = {('cutting' if p.stem == '__init__' else 'cutting.' + p.stem): p.read_text()
               for p in (ROOT / 'backend/cutting').glob('*.py')}
    payload = {'sources': sources, 'records': records,
               'datasets': [{'name': n, 'content': base64.b64encode((ROOT / harness.DATASETS[n]).read_bytes()).decode()}
                            for n in names]}
    fallos = 0
    with open(args.output, 'x', encoding='utf-8') as output, subprocess.Popen(
            ['docker', 'exec', '-i', args.container, 'python', '-B', '-c', RUNNER],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True) as process:
        process.stdin.write(json.dumps(payload))
        process.stdin.close()
        for line in process.stdout:
            output.write(line)
            m = json.loads(line)
            fallos += not m['ok']
            cota = 'no disponible' if m['cota_pct'] is None else f"{m['cota_pct']:.4f}%"
            print(f"{m['escenario']} {m['dataset']} {m['metodo']} {m['perfil']} semilla={m['seed']}: "
                  f"plan={m['desperdicio_plan_pct']:.4f}% cota={cota} "
                  f"{'OK' if m['ok'] else 'FALLO ' + (m['motivo'] or 'plan por debajo de la cota')}", flush=True)
        if process.wait():
            raise SystemExit(process.returncode)
    print(f'Registros con fallo: {fallos}', flush=True)
    if fallos:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
