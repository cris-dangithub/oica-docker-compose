"""Cota inferior de material por patrones de corte (Gilmore–Gomory), solo como métrica.

Spec 001, FR-012 a FR-016; research R-02. Por diámetro se resuelve la relajación lineal

    min Σ_k L_k·Σ_{p∈k} x_p   s.a.   Σ_p a_ip·x_p ≥ n_i,   Σ_{p∈k} x_p ≤ u_k (inventario finito)

por generación de columnas: el maestro con HiGHS (scipy, importado de forma diferida) y el
pricing con una mochila exacta en enteros escalados. Se relajan el orden de etapas, los saldos
entre etapas y los descartes. La pérdida por corte e se modela como Σ(l+e)·a ≤ L+e, que exige
al menos m−1 separaciones para m piezas (la última puede agotar la barra sin corte).

La validez no depende del solver: con cualquier dual y ≥ 0 se calcula una cota lagrangiana
certificada con la mochila exacta. Si el solver falla o no converge, la cota sigue siendo
válida, aunque más holgada («no ajustada»). La cota nunca construye ni modifica el plan.
"""
from collections import defaultdict
from decimal import Decimal
from math import gcd
import time

import numpy as np

LIMITE_DIAMETRO_S = 2.0
# El total queda por debajo del margen medido para SC-007 (≤ 25 % sobre 19,14 s en 002).
LIMITE_TOTAL_S = 4.0
MAX_ITERACIONES = 200
TOLERANCIA = 1e-9


def _linprog():
    """Import diferido: sin scipy, la cota se informa como «no disponible» (research R-01)."""
    from scipy.optimize import linprog
    return linprog


def datos(problem, d):
    """Piezas agregadas (longitud, demanda total) y tipos de barra del diámetro, en enteros."""
    demanda = defaultdict(int)
    for o in problem['orders']:
        if o['diametro'] == d:
            demanda[o['longitud']] += o['cantidad']
    tipos = {}
    for s in problem['stock']:
        if s['diametro'] != d:
            continue
        # Fuentes de igual longitud se suman; si alguna es ilimitada (None), el tipo lo es.
        if s['longitud'] not in tipos:
            tipos[s['longitud']] = s['cantidad']
        elif tipos[s['longitud']] is None or s['cantidad'] is None:
            tipos[s['longitud']] = None
        else:
            tipos[s['longitud']] += s['cantidad']
    return (sorted(demanda.items()),
            [{'longitud': L, 'cantidad': u} for L, u in sorted(tipos.items())],
            problem['rules'].get('kerf', 0))


def mochila(capacidad, pesos, valores, cotas):
    """Mochila acotada exacta en pesos enteros: (valor máximo, cantidades por ítem)."""
    dp = np.zeros(capacidad + 1)
    elecciones = []
    for i, (peso, valor, cota) in enumerate(zip(pesos, valores, cotas)):
        cota = min(cota, capacidad // peso) if peso > 0 else 0
        if valor <= 0 or cota <= 0:
            continue
        paso = 1
        while cota > 0:  # división binaria: cada bloque cabe porque cota·peso ≤ capacidad
            unidades = min(paso, cota)
            cota -= unidades
            paso *= 2
            w, v = peso * unidades, valor * unidades
            candidato = dp[:-w] + v if w else dp + v
            toma = candidato > dp[w:]
            dp[w:] = np.where(toma, candidato, dp[w:])
            elecciones.append((i, unidades, w, toma))
    cantidades, c = [0] * len(pesos), capacidad
    for i, unidades, w, toma in reversed(elecciones):
        if c >= w and toma[c - w]:
            cantidades[i] += unidades
            c -= w
    return float(dp[capacidad]), cantidades


def _precios(items, tipos, e, y):
    """Mejor valor z_k y patrón por tipo de barra para los duales y."""
    pesos = [l + e for l, _ in items]
    cotas = [q for _, q in items]
    return [mochila(t['longitud'] + e, pesos, y, cotas) for t in tipos]


def certificado(items, tipos, e, y, precios=None):
    """Cota lagrangiana válida para cualquier y ≥ 0 (en longitud escalada).

    LB(θ) = θ·Σ n_i·y_i + Σ_{k finito} u_k·min(0, L_k − θ·z_k), con θ ≤ L_k/z_k para las
    barras ilimitadas. z_k se infla 1e-9 para cubrir el error de coma flotante.
    """
    y = [max(0.0, float(v)) for v in y]
    precios = precios or _precios(items, tipos, e, y)
    z = [valor * (1 + TOLERANCIA) for valor, _ in precios]
    base = sum(q * v for (_, q), v in zip(items, y))
    techo = min([t['longitud'] / zk for t, zk in zip(tipos, z) if t['cantidad'] is None and zk > 0],
                default=float('inf'))
    candidatos = {techo, 1.0} | {t['longitud'] / zk for t, zk in zip(tipos, z)
                                 if t['cantidad'] is not None and zk > 0}
    mejor = 0.0
    for theta in candidatos:
        if not 0 <= theta <= techo or theta == float('inf'):
            continue
        lb = theta * base + sum(t['cantidad'] * min(0.0, t['longitud'] - theta * zk)
                                for t, zk in zip(tipos, z) if t['cantidad'] is not None)
        mejor = max(mejor, lb)
    return mejor


def _redondear(material, tipos):
    """Techo al múltiplo del mcd de las L_k: el material de un plan es combinación entera de ellas.

    Un valor que excede a un múltiplo solo por error de coma flotante (≤ 1e-9 relativo) no
    sube al siguiente: el certificado ya se rebajó al inflar z_k.
    """
    g = 0
    for t in tipos:
        g = gcd(g, t['longitud'])
    g = g or 1
    if material <= 0:
        return 0
    veces = material / g
    cercano = round(veces)
    if abs(veces - cercano) <= 1e-9 * max(1.0, veces):
        return int(cercano) * g
    return int(np.ceil(veces)) * g


def cota_simple(problem, d):
    """Aprovechamiento perfecto: material ≥ longitud total de las piezas (FR-013)."""
    items, tipos, _ = datos(problem, d)
    total = sum(l * q for l, q in items)
    mayor = max((t['longitud'] for t in tipos), default=0)
    return {'material': _redondear(total, tipos), 'longitud_piezas': total,
            'barras_minimas': -(-total // mayor) if mayor else 0}


def cota_diametro(problem, d, max_iter=MAX_ITERACIONES, limite_s=LIMITE_DIAMETRO_S, linprog=None):
    """Generación de columnas con certificado; devuelve material mínimo escalado y su ajuste."""
    linprog = linprog or _linprog()
    inicio = time.perf_counter()
    items, tipos, e = datos(problem, d)
    n_items = len(items)
    demanda = np.array([q for _, q in items], dtype=float)
    finitos = [k for k, t in enumerate(tipos) if t['cantidad'] is not None]
    columnas = []
    for k, t in enumerate(tipos):  # patrones homogéneos iniciales
        for i, (l, q) in enumerate(items):
            if l + e <= t['longitud'] + e:
                a = [0] * n_items
                a[i] = min(q, (t['longitud'] + e) // (l + e))
                columnas.append((k, tuple(a)))
    # Variables artificiales caras: el maestro restringido siempre es factible.
    castigo = 2.0 * max(t['longitud'] for t in tipos)
    vistas = set(columnas)
    y, precios, valor_maestro, convergio, iteraciones = None, None, None, False, 0
    for iteraciones in range(1, max_iter + 1):
        restante = limite_s - (time.perf_counter() - inicio)
        if restante <= 0:
            break
        m = len(columnas)
        costo = np.array([tipos[k]['longitud'] for k, _ in columnas] + [castigo] * n_items, dtype=float)
        demanda_a = np.zeros((n_items, m + n_items))
        for j, (_, a) in enumerate(columnas):
            demanda_a[:, j] = a
        demanda_a[:, m:] = np.eye(n_items)
        stock_a = np.zeros((len(finitos), m + n_items))
        for fila, k in enumerate(finitos):
            for j, (kk, _) in enumerate(columnas):
                if kk == k:
                    stock_a[fila, j] = 1
        a_ub = np.vstack([-demanda_a, stock_a])
        b_ub = np.concatenate([-demanda, [tipos[k]['cantidad'] for k in finitos]])
        res = linprog(costo, A_ub=a_ub, b_ub=b_ub, bounds=(0, None), method='highs',
                      options={'time_limit': max(0.05, restante)})
        if res.status != 0:
            break
        marginales = -np.asarray(res.ineqlin.marginals)
        y = np.maximum(0.0, marginales[:n_items])
        penal = dict(zip(finitos, np.maximum(0.0, marginales[n_items:])))
        valor_maestro = float(res.fun)
        precios = _precios(items, tipos, e, y)
        nuevas = []
        for k, (z, a) in enumerate(precios):
            columna = (k, tuple(a))
            if z > tipos[k]['longitud'] + penal.get(k, 0.0) + TOLERANCIA * tipos[k]['longitud'] and columna not in vistas:
                nuevas.append(columna)
        if not nuevas:
            convergio = True
            break
        columnas.extend(nuevas)
        vistas.update(nuevas)
    certificada = certificado(items, tipos, e, y, precios) if y is not None else 0.0
    simple = cota_simple(problem, d)['longitud_piezas']
    material = _redondear(max(certificada, simple), tipos)
    ajustada = bool(convergio and valor_maestro is not None
                    and abs(certificada - valor_maestro) <= 1e-6 * max(1.0, valor_maestro))
    return {'diametro': d, 'material': material, 'material_m': material / problem['scale'],
            'ajustada': ajustada, 'iteraciones': iteraciones, 'columnas': len(columnas),
            'segundos': time.perf_counter() - inicio}


def _desperdicio(piezas, material):
    return float(100 * (1 - Decimal(piezas) / Decimal(material))) if material else 0.0


def cota_plan(problem, metrics, limite_total_s=LIMITE_TOTAL_S):
    """Cota por diámetro y del proyecto, en masa (data-model §2.4); la brecha la añade el análisis.

    Nunca lanza: si falta scipy o el solver falla, devuelve estado «no_disponible» con su motivo
    y conserva la cota simple, que no depende del solver (Principio IV: una métrica no puede
    impedir entregar un plan válido).
    """
    inicio = time.perf_counter()
    diametros = sorted(metrics['por_diametro'], key=lambda d: int(str(d).lstrip('#')))
    escala = Decimal(problem['scale'])

    def kg(d, longitud):
        return Decimal(longitud) / escala * Decimal(problem['densities'][d])

    filas, piezas_kg, simple_kg = [], Decimal(0), Decimal(0)
    for d in diametros:
        simple = cota_simple(problem, d)
        piezas = kg(d, simple['longitud_piezas'])
        piezas_kg += piezas
        simple_kg += kg(d, simple['material'])
        filas.append({'diametro': d, 'material_m': None, 'material_kg': None, 'desperdicio_pct': None,
                      'ajustada': False,
                      'simple': {'material_m': float(Decimal(simple['material']) / escala),
                                 'desperdicio_pct': _desperdicio(piezas, kg(d, simple['material'])),
                                 'barras_minimas': simple['barras_minimas']},
                      '_piezas_kg': piezas})
    proyecto = {'material_kg': None, 'desperdicio_pct': None,
                'simple_desperdicio_pct': _desperdicio(piezas_kg, simple_kg)}

    def resultado(estado, motivo=None):
        for fila in filas:
            fila.pop('_piezas_kg', None)
        return {'estado': estado, 'motivo': motivo, 'ajustada': estado == 'calculada' and all(
            f['ajustada'] for f in filas), 'proyecto': proyecto, 'por_diametro': filas}

    try:
        linprog = _linprog()
    except Exception as error:  # ImportError u otro fallo de carga
        return resultado('no_disponible', f'scipy no disponible: {error}')
    material_kg = Decimal(0)
    try:
        for fila in filas:
            restante = limite_total_s - (time.perf_counter() - inicio)
            cota = cota_diametro(problem, fila['diametro'], limite_s=max(0.1, min(LIMITE_DIAMETRO_S, restante)),
                                 linprog=linprog)
            masa = kg(fila['diametro'], cota['material'])
            material_kg += masa
            fila.update({'material_m': cota['material_m'], 'material_kg': float(masa),
                         'desperdicio_pct': _desperdicio(fila['_piezas_kg'], masa), 'ajustada': cota['ajustada'],
                         'iteraciones': cota['iteraciones'], 'columnas': cota['columnas'],
                         'segundos': cota['segundos']})
    except Exception as error:
        for fila in filas:
            fila.update({'material_m': None, 'material_kg': None, 'desperdicio_pct': None, 'ajustada': False})
        return resultado('no_disponible', f'{type(error).__name__}: {error}')
    proyecto.update({'material_kg': float(material_kg), 'desperdicio_pct': _desperdicio(piezas_kg, material_kg)})
    return resultado('calculada')
