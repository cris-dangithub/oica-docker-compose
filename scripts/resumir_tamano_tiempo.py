#!/usr/bin/env python3
"""Resume tiempo y desperdicio según el tamaño de la cartilla (OE2, Bloque N). Solo lee.

Describe cada cartilla desde su XLSX con el mismo cutting.io y cutting.domain del motor, agrega la
matriz de tamaño por cartilla, escenario, método y perfil, y por diámetro con la evolución del AG.
Además compara los registros de 001 y 002 con la línea base del 2026-09-13 sin los campos de reloj
(IGNORED del arnés y evolucion[d].seconds): deben coincidir. La salida JSON se crea de forma
exclusiva y el script sale con código 1 si hay diferencias con la línea base.

    PYTHONUTF8=1 python scripts/resumir_tamano_tiempo.py --matriz M.jsonl --output S.json
"""
import argparse
from collections import defaultdict
import hashlib
import importlib.util
import json
from pathlib import Path
from statistics import median
import sys

ROOT = Path(__file__).resolve().parents[1]
BASE = 'tests/benchmarks/2026-09-13-fisico-matriz-final.jsonl'
sys.path.insert(0, str(ROOT / 'backend'))
from cutting.domain import normalize  # noqa: E402
from cutting.io import read_rows  # noqa: E402

_spec = importlib.util.spec_from_file_location('check_cutting_container', ROOT / 'scripts/check_cutting_container.py')
harness = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(harness)


def leer(path):
    return [json.loads(line) for line in (ROOT / path).read_text(encoding='utf-8').splitlines() if line.strip()]


def sha256(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def rango(valores):
    return {'mediana': median(valores), 'min': min(valores), 'max': max(valores)}


def describir(nombre):
    problema = normalize(read_rows(ROOT / harness.DATASETS[nombre]), options=None)
    por_diametro = defaultdict(lambda: {'filas': 0, 'piezas': 0, 'longitudes': set()})
    for orden in problema['orders']:
        d = por_diametro[orden['diametro']]
        d['filas'] += 1
        d['piezas'] += orden['cantidad']
        d['longitudes'].add(orden['longitud'])
    diametros = sorted(por_diametro, key=lambda d: int(d[1:]))
    return {
        'archivo': harness.DATASETS[nombre],
        'filas': len(problema['orders']),
        'piezas': sum(o['cantidad'] for o in problema['orders']),
        'etapas': len({o['grupo'] for o in problema['orders']}),
        'longitudes_distintas': len({o['longitud'] for o in problema['orders']}),
        'por_diametro': {d: {'filas': por_diametro[d]['filas'], 'piezas': por_diametro[d]['piezas'],
                             'longitudes_distintas': len(por_diametro[d]['longitudes'])}
                         for d in diametros},
    }


def sin_reloj(registro):
    resultado = {k: v for k, v in registro.items() if k not in harness.IGNORED}
    if isinstance(resultado.get('evolucion'), dict):
        resultado['evolucion'] = {d: {k: v for k, v in e.items() if k != 'seconds'}
                                  for d, e in resultado['evolucion'].items()}
    return resultado


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--matriz', required=True, help='JSONL de la matriz de tamaño')
    parser.add_argument('--base', default=BASE, help='Línea base de 001 y 002')
    parser.add_argument('--output', required=True, help='JSON nuevo en tests/benchmarks/ (no se sobrescribe)')
    args = parser.parse_args()
    registros, base = leer(args.matriz), leer(args.base)
    nombres = sorted({r['dataset'] for r in registros})
    cartillas = {n: describir(n) for n in nombres}
    for nombre, cartilla in cartillas.items():
        cartilla['masa_kg'] = next(r['piezas_kg'] for r in registros if r['dataset'] == nombre)

    grupos = defaultdict(list)
    for r in registros:
        grupos[(r['dataset'], r['escenario'], r['metodo'], r['perfil'])].append(r)
    tiempos = [{'dataset': d, 'escenario': e, 'metodo': m, 'perfil': p, 'n': len(rs),
                'duracion_segundos': rango([r['duracion_segundos'] for r in rs]),
                'desperdicio_porcentaje': rango([r['desperdicio_porcentaje'] for r in rs]),
                'barras': rango([r['barras'] for r in rs])}
               for (d, e, m, p), rs in sorted(grupos.items())]

    evolucion = defaultdict(list)
    for r in registros:
        if r['metodo'] == 'ag':
            for diametro, e in r['evolucion'].items():
                evolucion[(r['dataset'], r['escenario'], r['perfil'], diametro)].append(e)
    por_diametro = []
    for (d, e, p, diametro), es in sorted(evolucion.items()):
        tamano = cartillas[d]['por_diametro'][diametro]
        por_diametro.append({
            'dataset': d, 'escenario': e, 'perfil': p, 'diametro': diametro,
            'filas': tamano['filas'], 'piezas': tamano['piezas'], 'n': len(es),
            'segundos': rango([x['seconds'] for x in es]),
            'evaluaciones': rango([x['evaluaciones'] for x in es]),
            'generaciones': rango([x['generaciones'] for x in es]),
            'ms_por_evaluacion': rango([1000 * x['seconds'] / x['evaluaciones'] for x in es if x['evaluaciones']]),
        })

    clave = lambda r: (r['dataset'], r['escenario'], r['metodo'], r['perfil'], r['seed'])
    esperados = {clave(r): r for r in base}
    comparados, diferencias, razones = 0, [], defaultdict(list)
    for r in registros:
        if clave(r) not in esperados:
            continue
        comparados += 1
        esperado, obtenido = sin_reloj(esperados[clave(r)]), sin_reloj(r)
        distintos = sorted(k for k in set(esperado) | set(obtenido) if esperado.get(k) != obtenido.get(k))
        if distintos:
            diferencias.append({'registro': list(clave(r)), 'campos': distintos})
        razones[(r['dataset'], r['perfil'] if r['metodo'] == 'ag' else r['metodo'])].append(
            r['duracion_segundos'] / esperados[clave(r)]['duracion_segundos'])

    resumen = {
        'fuentes': {args.matriz: sha256(args.matriz), args.base: sha256(args.base)},
        'entorno': sorted({(r['python'], r['plataforma']) for r in registros}),
        'cartillas': cartillas,
        'tiempos': tiempos,
        'por_diametro': por_diametro,
        'linea_base': {'registros_comparados': comparados, 'con_diferencias': len(diferencias),
                       'diferencias': diferencias,
                       'razon_tiempo_frente_a_base': [{'dataset': d, 'perfil_o_metodo': p, **rango(v)}
                                                      for (d, p), v in sorted(razones.items())]},
    }
    with open(ROOT / args.output, 'x', encoding='utf-8') as salida:
        json.dump(resumen, salida, ensure_ascii=False, indent=1)
        salida.write('\n')
    for nombre, c in cartillas.items():
        filas = [t for t in tiempos if t['dataset'] == nombre and t['escenario'] == 'ambos']
        texto = ', '.join(f"{t['perfil'] if t['metodo'] == 'ag' else t['metodo']} "
                          f"{t['duracion_segundos']['mediana']:.2f}s" for t in filas)
        print(f"{nombre}: {c['filas']} filas, {c['piezas']} piezas; ambos: {texto}")
    print(f'Línea base: {comparados} registros comparados, {len(diferencias)} con diferencias')
    if diferencias:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
