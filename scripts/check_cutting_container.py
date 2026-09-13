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

RUNNER = r'''
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
for dataset in payload['datasets']:
    raw = base64.b64decode(dataset['content'])
    problem = normalize(read_rows(io.BytesIO(raw), dataset['name']))
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
            with tempfile.TemporaryDirectory(prefix='oica-artefactos-') as directory:
                files = generate(problem, r, directory, dataset['name'], True)
                sheets = pd.read_excel(files['excel_path'], sheet_name=None)
                assert set(sheets) == {'Barras', 'Cortes', 'Inventario', 'Metricas'}
                actual = Counter()
                for row in sheets['Cortes'].to_dict('records'):
                    actual[int(row['fila_origen'])] += int(row['cantidad'])
                assert actual == Counter({o['row_id']: o['cantidad'] for o in problem['orders']})
                assert len(sheets['Barras']) == m['barras']
                inventory = read_rows(files['inventory_path'])
                validate(problem, r['bars'], inventory)
                assert Path(files['pdf_path']).read_bytes().startswith(b'%PDF')
                with Image.open(files['graph_image_path']) as picture:
                    assert picture.width * picture.height <= 3_000_000
                # La serialización de compatibilidad también se mide, sin guardarla.
                m['json_compatibilidad_bytes'] = len(json.dumps(legacy_patterns(problem, r)).encode())
                m['artefactos_bytes'] = {key: Path(path).stat().st_size for key, path in files.items()}
                m['artefactos_verificados'] = True
            m['artefactos_y_verificacion_segundos'] = time.perf_counter() - started
        m.update({'dataset': dataset['name'], 'archivo_sha256': sha256(raw).hexdigest(),
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
    parser.add_argument('--profiles', nargs='+', default=['rapido', 'balanceado', 'profundo'])
    parser.add_argument('--output')
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
               'artifacts_smoke': args.artifacts_smoke,
               'all_tests': args.all_tests, 'test_names': names,
               'datasets': [{'name': Path(p).name, 'content': base64.b64encode(Path(p).read_bytes()).decode()}
                            for p in args.dataset],
               'runs': [('ffd', 'rapido', 0), ('bfd', 'rapido', 0)] +
                       [('ag', profile, seed) for profile in args.profiles for seed in range(args.seeds)]}
    if args.artifacts_smoke:
        payload['runs'] = [('ag', 'rapido', 0)]
    output = open(args.output, 'x', encoding='utf-8') if args.output else None
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
                print(f"{m['dataset']} {m['metodo']} {m['perfil']} semilla={m['seed']}: "
                      f"{m['duracion_segundos']:.2f}s, desperdicio={m['desperdicio_porcentaje']:.4f}%, "
                      f"piezas={m['piezas']}, valido={m['valido']}", flush=True)
                if m.get('artefactos_verificados'):
                    print(f"Artefactos verificados: {sum(m['artefactos_bytes'].values())} bytes; "
                          f"generación y verificación: {m['artefactos_y_verificacion_segundos']:.2f}s", flush=True)
            if process.wait():
                raise SystemExit(process.returncode)
    finally:
        if output:
            output.close()


if __name__ == '__main__':
    main()
