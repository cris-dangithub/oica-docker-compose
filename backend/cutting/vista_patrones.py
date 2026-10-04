"""Vista de patrones para el explorador web (spec 002, research R-16 a R-19).

Solo lee el plan ya guardado (`ProcessingResult.resultados`): no ejecuta el AG, no escribe en la
base ni regenera artefactos. Reutiliza `patterns.agrupar` y `report.patrones_rows`, así que los
patrones coinciden con la hoja «Patrones» del Excel por construcción (FR-025).
"""
from collections import Counter, defaultdict
from decimal import Decimal

from . import patterns
from .report import patrones_rows

NO_RECONSTRUIBLE = 'La versión no guarda la trazabilidad de cortes necesaria para reconstruir los patrones'
ORDEN_ORIGENES = ['comercial', 'adicional']


def barras_desde_resultados(resultados, escala):
    """Barras del motor a partir de `legacy_patterns` (data-model §8.1); `None` si no se puede.

    Los valores se guardaron como `entero / escala`; `round(x × escala)` recupera el entero exacto.
    """
    if not resultados or not escala:
        return None
    barras = []
    for r in resultados:
        cortes = r.get('trazabilidad_cortes')
        if cortes is None:
            return None
        barras.append({'bar_id': r['bar_id'], 'diametro': r['diametro'], 'origen': r['origen'],
                       'longitud': round(r['barra_origen_longitud'] * escala), 'cuts': cortes,
                       'kerf': round(r.get('perdida_corte_m', 0) * escala),
                       'discarded': round(r.get('descartado_m', 0) * escala),
                       'remaining': round(r['desperdicio_resultante'] * escala),
                       'discard_events': r.get('descartes_fin_etapa', [])})
    return barras


def rangos(bar_ids):
    """Identificadores `#d:n` agrupados en rangos consecutivos del mismo diámetro (R-18)."""
    claves = sorted((b.rsplit(':', 1)[0], int(b.rsplit(':', 1)[1])) for b in bar_ids)
    salida = []
    for prefijo, n in claves:
        ultimo = salida[-1] if salida else None
        if ultimo and ultimo['prefijo'] == prefijo and ultimo['fin'] == n - 1:
            ultimo['fin'] = n
        else:
            salida.append({'prefijo': prefijo, 'inicio': n, 'fin': n})
    return [{'desde': f"{r['prefijo']}:{r['inicio']}", 'hasta': f"{r['prefijo']}:{r['fin']}",
             'n': r['fin'] - r['inicio'] + 1} for r in salida]


def _pedidos(conteo):
    """Pedidos ordenados numéricamente si todos son números; si no, como texto (contrato)."""
    try:
        claves = sorted(conteo, key=float)
    except ValueError:
        claves = sorted(conteo)
    return [{'pedido': p, 'piezas': conteo[p]} for p in claves]


def _inconsistente(detalle):
    return ValueError(f'Patrones inconsistentes: {detalle}')


def vista(resultados, metricas):
    """Todos los patrones de una versión con piezas, pedidos y rangos de barras (FR-024 a FR-028)."""
    metricas = metricas or {}
    escala = metricas.get('escala_longitudes')
    barras = barras_desde_resultados(resultados, escala)
    if barras is None:
        return {'disponible': False, 'motivo': NO_RECONSTRUIBLE}
    problema = {'scale': escala}
    patrones, patron_por_barra = patterns.agrupar(problema, barras)
    miembros = defaultdict(list)
    for barra in barras:
        miembros[patron_por_barra[barra['bar_id']]].append(barra)
    indice = Counter()
    salida = []
    for patron, fila in zip(patrones, patrones_rows(problema, patrones)):
        propias = miembros[patron['patron_id']]
        piezas = []
        # Todas las barras del patrón comparten la secuencia: el corte i es la pieza i (R-19).
        for i, (grupo, longitud, cantidad) in enumerate(patron['secuencia']):
            conteo = Counter()
            for barra in propias:
                conteo[str(barra['cuts'][i]['pedido'])] += barra['cuts'][i]['cantidad']
            if sum(conteo.values()) != cantidad * patron['repeticiones']:
                raise _inconsistente(f"pedidos de {patron['patron_id']} no suman sus piezas")
            indice.update(conteo)
            piezas.append({'etapa': grupo, 'longitud_m': float(Decimal(longitud) / escala),
                           'cantidad': cantidad, 'pedidos': _pedidos(conteo)})
        salida.append({**fila, 'etapas': sorted({grupo for grupo, _, _ in patron['secuencia']}),
                       'piezas': piezas,
                       'barras': {'total': len(propias), 'rangos': rangos([b['bar_id'] for b in propias])}})
    if sum(p['repeticiones'] for p in patrones) != len(resultados):
        raise _inconsistente('las repeticiones no suman las barras guardadas')
    resumen = (metricas.get('analisis') or {}).get('patrones')
    if resumen:
        repeticiones = {p['patron_id']: p['repeticiones'] for p in patrones}
        if (resumen['total'] != len(patrones) or resumen['barras'] != len(barras)
                or any(repeticiones.get(t['patron_id']) != t['repeticiones'] for t in resumen['top'])):
            raise _inconsistente('no coinciden con el análisis guardado de la versión')
    diametros = sorted({p['diametro'] for p in patrones}, key=lambda d: int(d.lstrip('#')))
    origenes = {p['origen'] for p in patrones}
    return {'disponible': True,
            'escala_m': max((p['longitud_m'] for p in salida), default=0.0),
            'totales': {'patrones': len(patrones), 'barras': len(barras)},
            'diametros': diametros,
            'etapas': sorted({e for p in salida for e in p['etapas']}),
            'origenes': [o for o in ORDEN_ORIGENES if o in origenes] + sorted(origenes - set(ORDEN_ORIGENES)),
            'pedidos': _pedidos(indice),
            'patrones': salida}
