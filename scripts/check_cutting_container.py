#!/usr/bin/env python3
"""Verificar código actual en Python 3.12 existente, cargándolo solo en memoria.

No construye imágenes ni instala paquetes. Las pruebas de artefactos usan un
directorio temporal pequeño que se retira al finalizar; no cambian datos de la app.
El resumen opcional se crea de forma exclusiva en el host.
"""
import argparse
import base64
import json
from pathlib import Path
import subprocess
import sys

PROFILES = ['rapido', 'balanceado', 'profundo']
# Nombre del campo `dataset` de las líneas base → cartilla del repositorio.
DATASETS = {'001-pruebaInicial.xlsx': 'tests/data/001/001-pruebaInicial.xlsx',
            '002-ingeBigTest.xlsx': 'tests/data/002/002-ingeBigTest.xlsx',
            '003-sinteticaVivienda.xlsx': 'tests/data/003/003-sinteticaVivienda.xlsx',
            '004-sinteticaEdificio.xlsx': 'tests/data/004/004-sinteticaEdificio.xlsx'}
# Claves temporales, de entorno o añadidas después de la línea base: no se comparan.
IGNORED = {'duracion_segundos', 'timings', 'memoria_maxima_kib', 'codigo_sha256', 'python', 'plataforma',
           'artefactos_generados', 'analisis', 'analisis_segundos', 'artifacts_seconds', 'pipeline_seconds',
           'dataset', 'escenario'}

# Cargador de fuentes en memoria, reutilizado por scripts/cota_ensayos.py.
FINDER = r'''
import sys, json, base64, io, importlib.abc, importlib.util, platform, resource, unittest
payload = json.load(sys.stdin)
class Sources(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    def find_spec(self, fullname, path=None, target=None):
        if fullname in payload['sources']:
            package = fullname in ('cutting', 'models', 'genetic_algorithm', 'tests')
            spec = importlib.util.spec_from_loader(fullname, self, is_package=package)
            spec.origin = '/usr/src/app/' + fullname.replace('.', '/') + ('/__init__.py' if package else '.py')
            spec.has_location = True
            return spec
    def create_module(self, spec): return None
    def exec_module(self, module):
        module.__file__ = module.__spec__.origin
        exec(compile(payload['sources'][module.__name__], module.__file__, 'exec'), module.__dict__)
sys.meta_path.insert(0, Sources())
if sys.version_info[:2] != (3, 12):
    raise RuntimeError('Esta verificación requiere Python 3.12')
'''

RUNNER = FINDER + r'''
if payload['tests'] or payload.get('api_tests') or payload.get('all_tests'):
    names = payload.get('test_names') if payload.get('all_tests') else ['test_cutting_api' if payload.get('api_tests') else 'test_sequential']
    suite = unittest.defaultTestLoader.loadTestsFromNames(names)
    outcome = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(not outcome.wasSuccessful())
from cutting.domain import normalize
from cutting.io import read_rows
from cutting.optimizer import optimize
from hashlib import sha256
code_hash = sha256(json.dumps(payload['sources'], sort_keys=True).encode()).hexdigest()
if payload.get('compare'):
    # Regresión: reproducir cada registro de la línea base y comparar sus métricas.
    from cutting.parameters import defaults
    allowed = set(defaults())
    contents = {d['name']: base64.b64decode(d['content']) for d in payload['datasets']}
    problems = {}
    for record in payload['compare']:
        raw = contents[record['dataset']]
        options = None if record['escenario'] == 'ideal' else {
            k: v for k, v in record['parametros_corte'].items() if k in allowed}
        key = (record['dataset'], json.dumps(options, sort_keys=True))
        if key not in problems:
            problems[key] = normalize(read_rows(io.BytesIO(raw), record['dataset']), options=options)
        m = optimize(problems[key], record['perfil'], record['seed'], record['metodo'])['metrics']
        m['archivo_sha256'] = sha256(raw).hexdigest()
        def sin_reloj(metrics):
            # `evolucion[d].seconds` es tiempo de reloj; el resto de la evolución sí se compara.
            metrics = dict(metrics)
            if isinstance(metrics.get('evolucion'), dict):
                metrics['evolucion'] = {d: {k: v for k, v in e.items() if k != 'seconds'}
                                        for d, e in metrics['evolucion'].items()}
            return metrics
        expected, m = sin_reloj(record), sin_reloj(m)
        diff = {k: {'esperado': v, 'obtenido': m.get(k, '<ausente>')} for k, v in expected.items()
                if k not in payload['ignored'] and m.get(k, '<ausente>') != v}
        print(json.dumps({'dataset': record['dataset'], 'escenario': record['escenario'],
                          'metodo': record['metodo'], 'perfil': record['perfil'], 'seed': record['seed'],
                          'diferencias': diff, 'ok': not diff}, ensure_ascii=False, allow_nan=False), flush=True)
    sys.exit(0)
for dataset in payload['datasets']:
    raw = base64.b64decode(dataset['content'])
    problem = normalize(read_rows(io.BytesIO(raw), dataset['name']), options=dataset.get('parameters', payload.get('parameters')))
    for method, profile, seed in payload['runs']:
        r = optimize(problem, profile, seed, method)
        m = r['metrics']
        if payload.get('artifacts_smoke'):
            import tempfile, time
            from pathlib import Path
            from collections import Counter
            import pandas as pd
            from PIL import Image
            from cutting.report import generate, legacy_patterns
            from cutting.domain import validate
            started = time.perf_counter()
            if 'cutting.analysis' in payload['sources']:
                # Mismo orden que el worker: análisis del plan validado y luego artefactos.
                from cutting.analysis import analizar
                analysis_started = time.perf_counter()
                m['analisis'] = analizar(problem, r, None)
                m['analisis_segundos'] = time.perf_counter() - analysis_started
                started = time.perf_counter()
            with tempfile.TemporaryDirectory(prefix='oica-artefactos-') as directory:
                files = generate(problem, r, directory, dataset['name'], True)
                sheets = pd.read_excel(files['excel_path'], sheet_name=None)
                # Las hojas originales deben seguir presentes; la spec 001 añade otras. La spec 002
                # reemplaza «Metricas» por «Resumen» y «Trazabilidad» y renombra «Parámetros»; se
                # aceptan ambas formas para medir el código previo en comparaciones intercaladas.
                assert set(sheets) >= {'Barras', 'Cortes', 'Inventario', 'Descartados', 'Inventario excluido'}
                assert set(sheets) >= {'Metricas', 'Parametros'} or set(sheets) >= {'Resumen', 'Trazabilidad', 'Parámetros'}
                if 'cutting.analysis' in payload['sources']:
                    assert set(sheets) >= {'Admisibilidad', 'Resumen de compra', 'Patrones', 'Cota', 'Avisos'}
                    m['patrones_total'] = len(sheets['Patrones'])
                    assert int(sheets['Patrones']['repeticiones'].sum()) == len(sheets['Barras'])
                actual = Counter()
                for row in sheets['Cortes'].to_dict('records'):
                    actual[int(row['fila_origen'])] += int(row['cantidad'])
                assert actual == Counter({o['row_id']: o['cantidad'] for o in problem['orders']})
                assert len(sheets['Barras']) == m['barras']
                inventory = read_rows(files['inventory_path'])
                validate(problem, r['bars'], inventory)
                assert Path(files['pdf_path']).read_bytes().startswith(b'%PDF')
                with Image.open(files['graph_image_path']) as picture:
                    # Límite fijo (BUG-005); 9 MP desde la spec 002 por los 200 dpi (R-04).
                    assert picture.width * picture.height <= 9_000_000
                # La serialización de compatibilidad también se mide, sin guardarla.
                m['json_compatibilidad_bytes'] = len(json.dumps(legacy_patterns(problem, r)).encode())
                m['artefactos_bytes'] = {key: Path(path).stat().st_size for key, path in files.items()}
                m['artefactos_verificados'] = True
            m['artefactos_y_verificacion_segundos'] = time.perf_counter() - started
        m.update({'dataset': dataset['name'], 'escenario': dataset.get('scenario', 'individual'),
                  'archivo_sha256': sha256(raw).hexdigest(),
                  'codigo_sha256': code_hash, 'python': platform.python_version(),
                  'plataforma': platform.platform(),
                  'memoria_maxima_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  'artefactos_generados': bool(payload.get('artifacts_smoke'))})
        print(json.dumps(m, ensure_ascii=False, allow_nan=False), flush=True)
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--container', default='oica-validation-celery_worker-1')
    parser.add_argument('--tests', action='store_true')
    parser.add_argument('--api-tests', action='store_true')
    parser.add_argument('--all-tests', action='store_true')
    parser.add_argument('--artifacts-smoke', action='store_true',
                        help='Un ensayo rápido por cartilla con reportes temporales; comprobar espacio antes')
    parser.add_argument('--dataset', action='append', default=[])
    parser.add_argument('--seeds', type=int, default=5)
    parser.add_argument('--profiles', nargs='+', default=None,
                        help='Por defecto: los tres perfiles; con --artifacts-smoke, solo rapido')
    parser.add_argument('--output')
    parser.add_argument('--parametros-corte', help='Objeto JSON con las condiciones del ensayo')
    parser.add_argument('--matrix', action='store_true', help='Cuatro combinaciones de checks, en serie')
    parser.add_argument('--comparar', action='append', default=[], metavar='RUTA.jsonl',
                        help='Reproducir cada registro de una línea base y exigir 0 diferencias (repetible)')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    sources = {}
    for path in (root / 'backend/cutting').glob('*.py'):
        name = 'cutting' if path.stem == '__init__' else 'cutting.' + path.stem
        sources[name] = path.read_text()
    sources['test_sequential'] = (root / 'backend/tests/test_sequential.py').read_text()
    if args.api_tests or args.all_tests:
        for name, path in [('server', 'backend/server.py'), ('celery_worker', 'backend/celery_worker.py'),
                           ('models', 'backend/models/__init__.py'), ('models.uploaded_file', 'backend/models/uploaded_file.py'),
                           ('test_cutting_api', 'backend/tests/test_cutting_api.py')]:
            sources[name] = (root / path).read_text()
    names = []
    if args.all_tests:
        for folder in ('genetic_algorithm', 'tests'):
            for path in (root / 'backend' / folder).glob('*.py'):
                name = folder if path.stem == '__init__' else folder + '.' + path.stem
                sources[name] = path.read_text()
                if folder == 'tests' and path.stem.startswith('test_'):
                    names.append(name)
    payload = {'sources': sources, 'tests': args.tests, 'api_tests': args.api_tests,
               'parameters': json.loads(args.parametros_corte) if args.parametros_corte else None,
               'artifacts_smoke': args.artifacts_smoke,
               'all_tests': args.all_tests, 'test_names': names,
               'datasets': [{'name': Path(p).name, 'content': base64.b64encode(Path(p).read_bytes()).decode()}
                            for p in args.dataset],
               'runs': [('ffd', 'rapido', 0), ('bfd', 'rapido', 0)] +
                       [('ag', profile, seed) for profile in args.profiles or PROFILES for seed in range(args.seeds)]}
    if args.artifacts_smoke:
        # Un ensayo por perfil pedido (rapido si no se indica), semilla 0.
        payload['runs'] = [('ag', profile, 0) for profile in args.profiles or ['rapido']]
    if args.matrix:
        if args.parametros_corte or args.artifacts_smoke:
            parser.error('--matrix no se combina con parámetros individuales ni artefactos')
        payload['datasets'] = [{**dataset, 'scenario': name, 'parameters': options}
            for name, options in [('ideal', None), ('solo_perdida', {'minimo_activo': False}),
                                  ('solo_minimo', {'perdida_activa': False}), ('ambos', {})]
            for dataset in payload['datasets']]
    if args.comparar:
        if args.matrix or args.artifacts_smoke or args.tests or args.api_tests or args.all_tests:
            parser.error('--comparar no se combina con otros modos')
        records = [json.loads(line) for path in args.comparar
                   for line in Path(path).read_text(encoding='utf-8').splitlines() if line.strip()]
        names = sorted({r['dataset'] for r in records})
        unknown = [n for n in names if n not in DATASETS]
        if unknown:
            parser.error(f'Dataset desconocido en la línea base: {unknown}')
        payload['datasets'] = [{'name': n, 'content': base64.b64encode((root / DATASETS[n]).read_bytes()).decode()}
                               for n in names]
        payload['compare'] = records
        payload['ignored'] = sorted(IGNORED)
    output = open(args.output, 'x', encoding='utf-8') if args.output else None
    differences = 0
    try:
        with subprocess.Popen(['docker', 'exec', '-i', args.container, 'python', '-B', '-c', RUNNER],
                              stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True) as process:
            process.stdin.write(json.dumps(payload))
            process.stdin.close()
            for line in process.stdout:
                if args.tests or args.api_tests or args.all_tests:
                    print(line, end='', flush=True)
                    continue
                m = json.loads(line)
                if output:
                    output.write(line)
                    output.flush()
                if args.comparar:
                    differences += not m['ok']
                    print(f"{m['escenario']} {m['dataset']} {m['metodo']} {m['perfil']} semilla={m['seed']}: "
                          f"{'OK' if m['ok'] else 'DIFERENCIAS ' + ', '.join(m['diferencias'])}", flush=True)
                    continue
                print(f"{m['escenario']} {m['dataset']} {m['metodo']} {m['perfil']} semilla={m['seed']}: "
                      f"{m['duracion_segundos']:.2f}s, desperdicio={m['desperdicio_porcentaje']:.4f}%, "
                      f"piezas={m['piezas']}, valido={m['valido']}", flush=True)
                if m.get('artefactos_verificados'):
                    print(f"Artefactos verificados: {sum(m['artefactos_bytes'].values())} bytes; "
                          f"generación y verificación: {m['artefactos_y_verificacion_segundos']:.2f}s", flush=True)
            if process.wait():
                raise SystemExit(process.returncode)
        if args.comparar:
            print(f'Registros con diferencias: {differences}', flush=True)
            if differences:
                raise SystemExit(1)
    finally:
        if output:
            output.close()


if __name__ == '__main__':
    main()
