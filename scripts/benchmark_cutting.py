#!/usr/bin/env python3
"""Ensayo reproducible del mismo núcleo usado por Celery; sin artefactos por defecto."""
import argparse
import json
import platform
from pathlib import Path
import resource
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))
from cutting.domain import normalize
from cutting.io import read_rows, file_hash
from cutting.optimizer import optimize


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('cartilla')
    parser.add_argument('--perfil', choices=['rapido', 'balanceado', 'profundo'], default='rapido')
    parser.add_argument('--metodo', choices=['ag', 'ffd', 'bfd'], default='ag')
    parser.add_argument('--semilla', type=int, default=0)
    parser.add_argument('--inventario')
    parser.add_argument('--catalogo', help='JSON con catálogo comercial')
    parser.add_argument('--salida', help='Resumen JSON opcional; nunca escribe patrones o imágenes')
    args = parser.parse_args()
    started = time.perf_counter()
    catalog = json.loads(Path(args.catalogo).read_text()) if args.catalogo else None
    problem = normalize(read_rows(args.cartilla), catalog,
                        read_rows(args.inventario) if args.inventario else None)
    read_seconds = time.perf_counter() - started
    last = [0.0]
    def progress(data):
        now = time.monotonic()
        if now - last[0] >= 15:
            print(f"{data['diametro']} {data['phase']} gen={data['generation']} "
                  f"transcurrido={data['elapsed_seconds']:.1f}s", file=sys.stderr, flush=True)
            last[0] = now
    result = optimize(problem, args.perfil, args.semilla, args.metodo, progress)
    report = result['metrics']
    report.update({'archivo_sha256': file_hash(args.cartilla), 'lectura_segundos': read_seconds,
                   'python': platform.python_version(), 'plataforma': platform.platform(),
                   'memoria_maxima_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                   'artefactos_generados': False})
    serialized = json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False)
    if args.salida:
        # Creación exclusiva: nunca sobreescribir evidencia anterior.
        with open(args.salida, 'x', encoding='utf-8') as output:
            output.write(serialized + '\n')
    print(serialized)


if __name__ == '__main__':
    main()
