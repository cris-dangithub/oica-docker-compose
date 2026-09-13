"""AG de claves aleatorias: decodificación secuencial con stock finito.

Un gen por orden (prioridad y elección de longitud), no por pieza. El
decodificador garantiza capacidad y disponibilidad; el validador comprueba la
demanda de forma independiente. Cada evaluación tiene su propio inventario.
"""
from bisect import bisect_left, insort
from collections import Counter
from decimal import Decimal
import random
import time

from . import VERSION
from .domain import validate

PROFILES = {'rapido': (20, 30, 8), 'balanceado': (50, 100, 15), 'profundo': (100, 200, 25)}


class Infeasible(ValueError):
    """El orden de colocación no pudo satisfacer el pedido con este inventario."""


def decode_grouped(orders, stock, genome):
    """Evaluación BFD por lotes de saldos idénticos, sin objetos por barra."""
    available = [s['cantidad'] for s in stock]
    pools, keys = Counter(), []
    consumed = commercial = bar_count = 0
    sequence = sorted(range(len(orders)), key=lambda i: (orders[i]['grupo'], genome[i][0], i))
    for i in sequence:
        length, left = orders[i]['longitud'], orders[i]['cantidad']
        mode = genome[i][1]
        def rank(j):
            s = stock[j]; size = s['longitud']
            choice = -size if mode == 0 else size if mode == 1 else (size % length) / size
            return choice, s['origen'] != 'adicional', size, j
        stock_order = sorted(range(len(stock)), key=rank)
        while left:
            pos = bisect_left(keys, length)
            if pos < len(keys):
                size = keys[pos]
                fits = size // length
                count = min(pools[size], max(1, left // fits))
                pools[size] -= count
                if not pools[size]:
                    del pools[size]
                    keys.pop(pos)
            else:
                j = next((j for j in stock_order if stock[j]['longitud'] >= length
                          and (available[j] is None or available[j] > 0)), None)
                if j is None:
                    raise Infeasible(f"Inventario insuficiente para fila {orders[i]['row_id']}")
                size = stock[j]['longitud']
                fits = size // length
                count = max(1, left // fits)
                if available[j] is not None:
                    count = min(count, available[j])
                    available[j] -= count
                consumed += size * count
                commercial += size * count if stock[j]['origen'] == 'comercial' else 0
                bar_count += count
            per_bar = min(left, fits)
            left -= per_bar * count
            remaining = size - per_bar * length
            if remaining:
                if remaining not in pools:
                    insort(keys, remaining)
                pools[remaining] += count
    return (consumed, commercial, bar_count), None


def decode(orders, stock, genome, record=False, first_fit=False, rules=None):
    """Agrupa cantidades dentro de cada barra; las barras raíz nunca se duplican."""
    if rules and (rules['kerf'] or any(rules['thresholds'].values())):
        from .physical import decode_physical
        return decode_physical(orders, stock, genome, rules, record, first_fit)
    if not record and not first_fit:
        return decode_grouped(orders, stock, genome)
    available = [s['cantidad'] for s in stock]
    bars, pools, keys = [], {}, []
    consumed_length = commercial_length = 0
    sequence = sorted(range(len(orders)), key=lambda i: (orders[i]['grupo'], genome[i][0], i))

    def put(index):
        remaining = bars[index][1]
        if remaining > 0:
            if remaining not in pools:
                pools[remaining] = []
                insort(keys, remaining)
            pools[remaining].append(index)

    for i in sequence:
        order = orders[i]
        length, left = order['longitud'], order['cantidad']
        while left:
            pos = bisect_left(keys, length)
            if pos < len(keys):
                if first_fit:
                    remaining = min(keys[pos:], key=lambda k: min(pools[k]))
                    index = min(pools[remaining])
                    pools[remaining].remove(index)
                else:
                    remaining = keys[pos]
                    index = pools[remaining].pop()
                if not pools[remaining]:
                    del pools[remaining]
                    keys.pop(bisect_left(keys, remaining))
            else:
                candidates = [j for j, s in enumerate(stock)
                              if s['longitud'] >= length and (available[j] is None or available[j] > 0)]
                if not candidates:
                    raise Infeasible(f"Inventario insuficiente para fila {order['row_id']}, grupo {order['grupo']}")
                mode = genome[i][1]
                def rank(j):
                    s = stock[j]
                    size = s['longitud']
                    preference = -size if mode == 0 else size if mode == 1 else (size % length) / size
                    return preference, s['origen'] != 'adicional', size, j
                j = min(candidates, key=rank)
                s = stock[j]
                if available[j] is not None:
                    available[j] -= 1
                index = len(bars)
                bars.append([j, s['longitud'], [] if record else None])
                consumed_length += s['longitud']
                if s['origen'] == 'comercial':
                    commercial_length += s['longitud']
            quantity = min(left, bars[index][1] // length)
            bars[index][1] -= quantity * length
            left -= quantity
            if record:
                bars[index][2].append({'row_id': order['row_id'], 'pedido': order['pedido'],
                                       'grupo': order['grupo'], 'longitud': length, 'cantidad': quantity})
            put(index)
    score = (consumed_length, commercial_length, len(bars))
    if not record:
        return score, None
    output = []
    for index, (j, remaining, cuts) in enumerate(bars):
        s = stock[j]
        output.append({'bar_id': f"{s['diametro']}:{index + 1}", 'stock_id': s['stock_id'],
                       'diametro': s['diametro'], 'origen': s['origen'], 'longitud': s['longitud'],
                       'remaining': remaining, 'cuts': cuts})
    return score, output


def optimize(problem, profile='rapido', seed=0, method='ag', callback=None):
    if profile not in PROFILES or method not in ('ag', 'ffd', 'bfd'):
        raise ValueError('Perfil o método inválido')
    rng = random.Random(seed)
    start = time.perf_counter()
    population_size, generations, patience = PROFILES[profile]
    bars, group_metrics = [], {}
    timings = Counter()
    diameters = sorted({o['diametro'] for o in problem['orders']})
    def emit(diam, phase, generation, evaluations):
        if callback:
            callback({'diametro': diam, 'phase': phase, 'generation': generation,
                      'max_generations': generations, 'evaluations': evaluations,
                      'elapsed_seconds': time.perf_counter() - start,
                      'diameters_done': len(group_metrics), 'diameters_total': len(diameters)})

    for diam in diameters:
        dstart = time.perf_counter()
        orders = [o for o in problem['orders'] if o['diametro'] == diam]
        stock = [s for s in problem['stock'] if s['diametro'] == diam]
        descending = tuple((-o['longitud'], 0) for o in orders)
        best_fill = tuple((-o['longitud'], 2) for o in orders)
        smallest = tuple((-o['longitud'], 1) for o in orders)
        cache = {}
        evaluations = 0
        def evaluate(genome):
            nonlocal evaluations
            if genome not in cache:
                before = time.perf_counter()
                try:
                    score, _ = decode(orders, stock, genome, rules=problem.get('rules'))
                except Infeasible:
                    score = (float('inf'),) * 3
                timings['evaluation_seconds'] += time.perf_counter() - before
                evaluations += 1
                if len(cache) >= 256:
                    cache.clear()
                cache[genome] = score
                emit(diam, 'evaluation', generation, evaluations)
            return cache[genome]

        generation = 0
        # En stock de longitudes variables se comparan tres reglas de apertura
        # para ambas heurísticas: mayor, menor y menor residuo relativo.
        # Evita atribuir al AG una ventaja causada solo por una base débil.
        before = time.perf_counter()
        references = []
        for first_fit in (True, False):
            for genome in (descending, best_fill, smallest):
                try:
                    score, _ = decode(orders, stock, genome, first_fit=first_fit, rules=problem.get('rules'))
                except Infeasible:
                    score = (float('inf'),) * 3
                references.append((score, genome, first_fit))
        timings['baseline_seconds'] += time.perf_counter() - before
        winner_score, winner, winner_first_fit = min(references, key=lambda r: r[0])
        if method == 'ffd':
            winner_score, winner, winner_first_fit = min((r for r in references if r[2]), key=lambda r: r[0])
            population = []
        elif method == 'bfd':
            winner_score, winner, winner_first_fit = min((r for r in references if not r[2]), key=lambda r: r[0])
            population = []
        else:
            before = time.perf_counter()
            population = [descending, best_fill, smallest]
            while len(population) < population_size:
                population.append(tuple((rng.random(), rng.randrange(3)) for _ in orders))
            timings['initialization_seconds'] += time.perf_counter() - before
            population.sort(key=evaluate)
            if evaluate(population[0]) < winner_score:
                winner, winner_score, winner_first_fit = population[0], evaluate(population[0]), False
        initial_score = winner_score
        history = [winner_score[0] if winner_score[0] != float('inf') else None]
        stale, reason = 0, 'heuristica' if method != 'ag' else 'generaciones'
        for generation in range(1, generations + 1) if method == 'ag' else ():
            before = time.perf_counter()
            # Elitismo y selección por torneo. Los genes del hijo se conservan
            # durante la decodificación; no se reemplazan por una solución BFD.
            children = population[:2]
            while len(children) < population_size:
                # La población ya está ordenada: no volver a decodificar padres.
                a = population[min(rng.sample(range(len(population)), 3))]
                b = population[min(rng.sample(range(len(population)), 3))]
                child = [a[i] if rng.random() < .5 else b[i] for i in range(len(orders))]
                for i in range(len(child)):
                    if rng.random() < max(.05, 1 / len(child)):
                        child[i] = (rng.random(), rng.randrange(3))
                children.append(tuple(child))
            timings['variation_seconds'] += time.perf_counter() - before
            population = sorted(children, key=evaluate)
            score = evaluate(population[0])
            if score < winner_score:
                winner, winner_score, winner_first_fit = population[0], score, False
                stale = 0
            else:
                stale += 1
            history.append(winner_score[0] if winner_score[0] != float('inf') else None)
            emit(diam, 'generation', generation, evaluations)
            if stale >= patience:
                reason = 'estancamiento'
                break
        if winner_score[0] == float('inf'):
            raise Infeasible(f'No se encontró un plan factible para {diam}; revisar inventario o ampliar la búsqueda')
        before = time.perf_counter()
        checked_score, result = decode(orders, stock, winner, record=True, first_fit=winner_first_fit,
                                       rules=problem.get('rules'))
        if checked_score != winner_score:
            raise ValueError('La evaluación agrupada no coincide con el plan materializado')
        timings['materialization_seconds'] += time.perf_counter() - before
        bars.extend(result)
        group_metrics[diam] = {'metodo': method, 'generaciones': generation, 'evaluaciones': evaluations,
                               'motivo_parada': reason, 'seconds': time.perf_counter() - dstart,
                               'longitud_inicial': initial_score[0] if initial_score[0] != float('inf') else None,
                               'longitud_final': winner_score[0], 'historia_mejor_longitud': history,
                               'ganador_inicial_ffd': winner_first_fit}
    inventory = Counter()
    consumed = Counter(b['stock_id'] for b in bars)
    for b in bars:
        if b['remaining']:
            inventory[(b['diametro'], b['remaining'])] += 1
    for s in problem['stock']:
        if s['cantidad'] is not None:
            remaining = s['cantidad'] - consumed[s['stock_id']]
            if remaining:
                inventory[(s['diametro'], s['longitud'])] += remaining
    final = [{'diametro': d, 'longitud_m': str(Decimal(length) / problem['scale']), 'cantidad': q}
             for (d, length), q in sorted(inventory.items())]
    before = time.perf_counter()
    metrics = validate(problem, bars, final)
    timings['validation_seconds'] += time.perf_counter() - before
    metrics.update({'motor': VERSION, 'input_hash': problem['hash'], 'seed': seed, 'perfil': profile,
                    'metodo': method, 'parametros_corte': problem.get('resolved_parameters'),
                    'duracion_segundos': time.perf_counter() - start,
                    'etapas': sorted({o['grupo'] for o in problem['orders']}),
                    'evolucion': group_metrics, 'timings': dict(timings)})
    return {'bars': bars, 'inventory': final, 'metrics': metrics}
