"""Patrones de corte (spec 001, FR-007 a FR-011): agrupa barras cortadas de forma idéntica.

Es una vista del plan ya validado: no lo modifica. Dos barras comparten patrón solo si
coinciden en diámetro, origen, longitud, secuencia de cortes por etapa, pérdida por corte,
descarte (incluidos los eventos de fin de etapa) y saldo final.
"""
from collections import Counter, defaultdict


def clave(bar):
    """Identidad del patrón; la ruta sin pérdida física no trae kerf ni descartes (valen 0)."""
    return (bar['diametro'], bar['origen'], bar['longitud'],
            tuple((c['grupo'], c['longitud'], c['cantidad']) for c in bar['cuts']),
            bar.get('kerf', 0), bar.get('discarded', 0), bar['remaining'],
            tuple((e['grupo'], e['longitud']) for e in bar.get('discard_events', [])))


def agrupar(problem, bars):
    """Devuelve (patrones, patron_por_barra) con identificadores deterministas P-<diámetro>-<nnn>.

    Orden: diámetro natural, repeticiones descendentes y, a igualdad, la clave del patrón.
    """
    grupos = defaultdict(list)
    for bar in bars:
        grupos[clave(bar)].append(bar['bar_id'])
    ordenados = sorted(grupos.items(), key=lambda item: (int(item[0][0].lstrip('#')), -len(item[1]), item[0]))
    patrones, patron_por_barra, contador = [], {}, Counter()
    for key, bar_ids in ordenados:
        diam, origen, longitud, secuencia, kerf, discarded, remaining, eventos = key
        contador[diam] += 1
        patron_id = f'P-{diam}-{contador[diam]:03d}'
        patrones.append({'patron_id': patron_id, 'diametro': diam, 'origen': origen, 'longitud': longitud,
                         'secuencia': [list(c) for c in secuencia], 'kerf': kerf, 'discarded': discarded,
                         'remaining': remaining, 'discard_events': [list(e) for e in eventos],
                         'piezas': sum(l * q for _, l, q in secuencia), 'repeticiones': len(bar_ids)})
        patron_por_barra.update(dict.fromkeys(bar_ids, patron_id))
    return patrones, patron_por_barra


def verificar(problem, patrones, bars):
    """FR-011: Σ repeticiones = barras y la expansión de patrones reproduce la demanda exacta."""
    if sum(p['repeticiones'] for p in patrones) != len(bars):
        raise ValueError('Patrones inconsistentes: las repeticiones no suman las barras del plan')
    demanda = Counter()
    for p in patrones:
        for grupo, longitud, cantidad in p['secuencia']:
            demanda[(p['diametro'], grupo, longitud)] += cantidad * p['repeticiones']
    esperado = Counter()
    for o in problem['orders']:
        esperado[(o['diametro'], o['grupo'], o['longitud'])] += o['cantidad']
    if demanda != esperado:
        raise ValueError('Patrones inconsistentes: la expansión no reproduce la demanda')


def secuencia_legible(problem, patron):
    """«E1: 2×2,35 m + 1×1,10 m | E2: 3×0,80 m» (contracts/artefactos.md)."""
    def metros(value):
        return f'{value / problem["scale"]:.3f}'.rstrip('0').rstrip('.').replace('.', ',')
    etapas = []
    for grupo, longitud, cantidad in patron['secuencia']:
        texto = f'{cantidad}×{metros(longitud)} m'
        if etapas and etapas[-1][0] == grupo:
            etapas[-1][1].append(texto)
        else:
            etapas.append((grupo, [texto]))
    return ' | '.join(f'E{grupo}: ' + ' + '.join(cortes) for grupo, cortes in etapas)
