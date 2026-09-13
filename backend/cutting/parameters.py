"""Parámetros explícitos del modelo; las referencias no son exigencias legales."""
from decimal import Decimal

REFERENCES = {
    'disco': {'valor_mm': '1', 'nota': 'Espesor nominal; medir la pérdida real del equipo.',
              'url': 'https://www.hilti.com.ph/c/CLS_POWER_TOOL_INSERT_7126/CLS_ABRASIVES_7126/r6473822'},
    'cizalla': {'valor_mm': '0', 'nota': 'Idealización editable, no medición ni requisito legal.'},
    'automatico': {'nota': 'Menor longitud demandada por diámetro en toda la cartilla.',
                   'url': 'https://www.joams.com/uploadfile/2013/1024/20131024100240137.pdf',
                   'doi': '10.12720/joams.1.3.313-316'},
}


def defaults():
    return {'perdida_activa': True, 'proceso': 'disco', 'perdida_mm': '1',
            'minimo_activo': True, 'modo_minimo': 'automatico',
            'minimo_m': '0.5', 'descarte': 'inmediato'}


def parse(options):
    from .domain import decimal, positive
    base = defaults()
    if options is None:
        base.update(perdida_activa=False, minimo_activo=False)
    else:
        if not isinstance(options, dict) or set(options) - set(base):
            raise ValueError('Parámetros de corte desconocidos')
        base.update(options)
        if 'perdida_mm' not in options and base['proceso'] == 'cizalla':
            base['perdida_mm'] = '0'
    for key in ('perdida_activa', 'minimo_activo'):
        if type(base[key]) is not bool:
            raise ValueError(f'{key} debe ser booleano')
    if base['proceso'] not in ('disco', 'cizalla') or base['modo_minimo'] not in ('automatico', 'manual'):
        raise ValueError('Proceso o modo de mínimo inválido')
    if base['descarte'] not in ('inmediato', 'fin_etapa'):
        raise ValueError('Momento de descarte inválido')
    loss = decimal(base['perdida_mm'])
    if loss < 0:
        raise ValueError('La pérdida debe ser mayor o igual a cero')
    base['perdida_mm'] = str(loss)
    base['minimo_m'] = str(positive(base['minimo_m']))
    return base


def resolve(options, orders):
    p = parse(options)
    thresholds = {}
    if p['minimo_activo']:
        for o in orders:
            d = o['diametro']
            thresholds[d] = min(thresholds.get(d, o['longitud']), o['longitud'])
        if p['modo_minimo'] == 'manual':
            thresholds = {d: Decimal(p['minimo_m']) for d in thresholds}
    loss = Decimal(p['perdida_mm']) / 1000 if p['perdida_activa'] else Decimal(0)
    return p, loss, thresholds
