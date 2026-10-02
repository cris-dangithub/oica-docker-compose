"""Análisis posterior a la optimización (spec 001): métricas derivadas de un plan ya validado.

Nunca construye ni modifica el plan (constitución, Principio IV). El umbral de desperdicio
admisible es un dato de evaluación: no forma parte del problema ni de su huella.
"""
import copy
from decimal import Decimal

from . import bound, nominal, patterns

VERSION_ANALISIS = 'analisis-1'
COMPROBACIONES = ['demanda', 'diametro', 'capacidad', 'etapas', 'inventario']


def masa(problem, diametro, longitud_escalada):
    """Masa en kg de una longitud escalada del diámetro indicado."""
    return float(_masa(problem, diametro, longitud_escalada))


def _masa(problem, diametro, longitud_escalada):
    return Decimal(longitud_escalada) / problem['scale'] * Decimal(problem['densities'][diametro])


def _porcentaje(parte, total):
    return float(100 * Decimal(parte) / Decimal(total)) if total else 0.0


def _diametros(por_diametro):
    """Orden natural de diámetros: #3, #4, …, #18."""
    return sorted(por_diametro, key=lambda d: int(str(d).lstrip('#')))


def evaluar_admisibilidad(problem, metrics, umbral):
    """Estado frente al umbral por proyecto y por diámetro (FR-003).

    Usa el desperdicio por masa de INF-012 (sobrante final + pérdida por corte + descartes
    sobre la masa de barras usadas). Un empate cuenta como «dentro».
    """
    def evaluar(desperdicio):
        if umbral is None:
            return {'estado': 'sin_evaluar', 'desperdicio_pct': desperdicio, 'diferencia_pp': None}
        return {'estado': 'dentro' if desperdicio <= umbral else 'excede',
                'desperdicio_pct': desperdicio, 'diferencia_pp': desperdicio - umbral}

    por_diametro = []
    for diam in _diametros(metrics['por_diametro']):
        detail = metrics['por_diametro'][diam]
        waste = detail['sobrante_final'] + detail.get('perdida_corte', 0) + detail.get('descartado', 0)
        por_diametro.append({'diametro': diam, **evaluar(_porcentaje(waste, detail['longitud_inicial']))})
    return {'proyecto': evaluar(metrics['desperdicio_porcentaje']), 'por_diametro': por_diametro}


def perdidas(problem, metrics):
    """Pérdida irrecuperable (corte + descartes) frente a saldo reutilizable final (FR-004)."""
    def medida(kg, total):
        return {'kg': kg, 'pct': _porcentaje(Decimal(str(kg)), Decimal(str(total)))}

    total = metrics['masa_inicial_kg']
    por_diametro = {}
    for diam in _diametros(metrics['por_diametro']):
        detail = metrics['por_diametro'][diam]
        inicial = _masa(problem, diam, detail['longitud_inicial'])
        irrecuperable = _masa(problem, diam, detail.get('perdida_corte', 0) + detail.get('descartado', 0))
        reutilizable = _masa(problem, diam, detail['sobrante_final'])
        por_diametro[diam] = {
            'irrecuperable': {'kg': float(irrecuperable), 'pct': _porcentaje(irrecuperable, inicial)},
            'reutilizable': {'kg': float(reutilizable), 'pct': _porcentaje(reutilizable, inicial)}}
    return {'irrecuperable': medida(metrics['perdida_irrecuperable_kg'], total),
            'reutilizable': medida(metrics['sobrante_final_kg'], total),
            'por_diametro': por_diametro}


def resumen_compra(problem, result):
    """Barras por diámetro, longitud y origen, con masa y aprovechamiento (FR-027).

    Las barras de origen «adicional» salen del inventario: se listan aparte y no son compra.
    La suma por (diámetro, longitud) es igual a las barras raíz del plan.
    """
    grupos = {}
    for bar in result['bars']:
        key = (bar['diametro'], bar['longitud'], bar['origen'])
        grupo = grupos.setdefault(key, {'barras': 0, 'piezas': 0})
        grupo['barras'] += 1
        grupo['piezas'] += sum(c['longitud'] * c['cantidad'] for c in bar['cuts'])
    lineas = []
    for (diam, longitud, origen), grupo in sorted(
            grupos.items(), key=lambda item: (int(item[0][0].lstrip('#')), item[0][1], item[0][2] != 'comercial')):
        material = _masa(problem, diam, longitud * grupo['barras'])
        lineas.append({'diametro': diam, 'longitud_m': float(Decimal(longitud) / problem['scale']),
                       'origen': origen, 'barras': grupo['barras'], 'masa_kg': float(material),
                       'aprovechamiento_pct': _porcentaje(_masa(problem, diam, grupo['piezas']), material)})
    return lineas


def patrones_de(problem, result):
    """Lista completa de patrones y su asignación por barra, verificada (FR-011).

    No se persiste en JSONB; la usan los reportes para la hoja Patrones, el PDF y el PNG.
    """
    patrones, patron_por_barra = patterns.agrupar(problem, result['bars'])
    patterns.verificar(problem, patrones, result['bars'])
    return patrones, patron_por_barra


def resumen_patrones(problem, patrones, top=10):
    """Resumen persistido: total, barras, máximo de repeticiones y los más repetidos."""
    mas_repetidos = sorted(patrones, key=lambda p: -p['repeticiones'])[:top]
    return {'total': len(patrones), 'barras': sum(p['repeticiones'] for p in patrones),
            'max_repeticiones': max((p['repeticiones'] for p in patrones), default=0),
            'top': [{'patron_id': p['patron_id'], 'diametro': p['diametro'], 'origen': p['origen'],
                     'longitud_m': float(Decimal(p['longitud']) / problem['scale']),
                     'repeticiones': p['repeticiones'],
                     'aprovechamiento_pct': _porcentaje(p['piezas'], p['longitud'])}
                    for p in mas_repetidos]}


def evaluar_cota(problem, metrics, admisibilidad):
    """Cota inferior por patrones (solo métrica) con la brecha del plan (FR-012 a FR-015).

    Si el desperdicio del plan queda por debajo de una cota válida —la de patrones o, si no está
    disponible, la simple— es un error de dominio: la versión no se presenta como válida.
    """
    cota = bound.cota_plan(problem, metrics)
    plan = {e['diametro']: e['desperdicio_pct'] for e in admisibilidad['por_diametro']}
    plan_proyecto = admisibilidad['proyecto']['desperdicio_pct']

    def comprobar(ambito, desperdicio_plan, desperdicio_cota):
        if desperdicio_cota is not None and desperdicio_plan < desperdicio_cota - 1e-9:
            raise ValueError(f'Error de dominio: en {ambito} el desperdicio del plan ({desperdicio_plan:.6f}%) '
                             f'es menor que la cota inferior ({desperdicio_cota:.6f}%)')
        return None if desperdicio_cota is None else desperdicio_plan - desperdicio_cota

    for item in cota['por_diametro']:
        comprobar(f"el diámetro {item['diametro']}", plan[item['diametro']], item['simple']['desperdicio_pct'])
        item['brecha_pp'] = comprobar(f"el diámetro {item['diametro']}", plan[item['diametro']],
                                      item['desperdicio_pct'])
    comprobar('el proyecto', plan_proyecto, cota['proyecto']['simple_desperdicio_pct'])
    cota['proyecto']['brecha_pp'] = comprobar('el proyecto', plan_proyecto, cota['proyecto']['desperdicio_pct'])
    return cota


def analizar(problem, result, umbral=None):
    """Indicadores de la versión. Trabaja sobre una copia: el plan recibido queda intacto."""
    result = copy.deepcopy(result)
    metrics = result['metrics']
    admisibilidad = evaluar_admisibilidad(problem, metrics, umbral)
    return {'version': VERSION_ANALISIS, 'umbral_desperdicio_pct': umbral,
            'verificacion': {'valido': bool(metrics.get('valido')),
                             'comprobaciones': list(COMPROBACIONES)},
            'aprovechamiento_pct': 100 - metrics['desperdicio_porcentaje'],
            'admisibilidad': admisibilidad,
            'perdidas': perdidas(problem, metrics),
            'resumen_compra': resumen_compra(problem, result),
            'patrones': resumen_patrones(problem, patrones_de(problem, result)[0]),
            'cota': evaluar_cota(problem, metrics, admisibilidad),
            'avisos_masa': nominal.avisos(problem)}
