"""Decodificación por lotes con pérdida y descarte, sin expandir la demanda."""
from bisect import bisect_left, insort


def capacity(size, length, kerf, minimum, immediate):
    step = length + kerf
    full, tail = divmod(size, step)
    fits = full + int(kerf > 0 and tail == length)
    if immediate and minimum:
        fits = min(fits, max(1, (size - minimum) // step + 1))
    return fits


def decode_physical(orders, stock, genome, rules, record=False, first_fit=False):
    from .optimizer import Infeasible
    kerf = rules['kerf']
    minimum = rules['thresholds'].get(orders[0]['diametro'], 0)
    immediate = rules['immediate']
    detailed = record or first_fit
    available = [s['cantidad'] for s in stock]
    pools, keys, bars = {}, [], []
    consumed = commercial = count_bars = irreversible = 0
    group = None

    def put(size, value):
        if not size:
            return
        if size not in pools:
            pools[size] = [] if detailed else 0
            insort(keys, size)
        if detailed:
            pools[size].extend(value)
        else:
            pools[size] += value

    def flush():
        nonlocal irreversible
        for size in keys[:bisect_left(keys, minimum)]:
            value = pools.pop(size)
            irreversible += size * (len(value) if detailed else value)
            if detailed:
                for index in value:
                    bars[index]['discarded'] += size
                    bars[index]['discard_events'].append({'grupo': group, 'longitud': size})
                    bars[index]['remaining'] = 0
            keys.remove(size)

    sequence = sorted(range(len(orders)), key=lambda i: (orders[i]['grupo'], genome[i][0], i))
    for i in sequence:
        order = orders[i]
        if group is not None and order['grupo'] != group:
            flush()
        group = order['grupo']
        length, left = order['longitud'], order['cantidad']
        mode = genome[i][1]

        def fits(size):
            return capacity(size, length, kerf, minimum, immediate)

        def rank(j):
            s = stock[j]; size = s['longitud']
            preference = -size if mode == 0 else size if mode == 1 else (size - fits(size) * length) / size
            return preference, s['origen'] != 'adicional', size, j

        stock_order = sorted(range(len(stock)), key=rank)
        while left:
            # Solo tamaño exacto o espacio suficiente para una separación completa.
            pos = bisect_left(keys, length)
            if pos < len(keys) and keys[pos] != length:
                pos = bisect_left(keys, length + kerf)
            if pos < len(keys):
                size = keys[pos]
                if first_fit:
                    viable = [s for s in keys[pos:] if fits(s)]
                    size = min(viable, key=lambda s: min(pools[s]))
                fit = fits(size)
                if detailed:
                    index = min(pools[size]) if first_fit else pools[size][-1]
                    pools[size].remove(index)
                    count = 1
                else:
                    count = min(pools[size], max(1, left // fit))
                    pools[size] -= count
                if not pools[size]:
                    del pools[size]
                    keys.remove(size)
            else:
                j = next((j for j in stock_order if fits(stock[j]['longitud'])
                          and (available[j] is None or available[j] > 0)), None)
                if j is None:
                    raise Infeasible(f"Inventario insuficiente para fila {order['row_id']}")
                s = stock[j]; size = s['longitud']; fit = fits(size)
                count = 1 if detailed else max(1, left // fit)
                if available[j] is not None:
                    count = min(count, available[j]); available[j] -= count
                consumed += size * count
                commercial += size * count if s['origen'] == 'comercial' else 0
                count_bars += count
                if detailed:
                    index = len(bars)
                    bars.append({**s, 'bar_id': f"{s['diametro']}:{index + 1}", 'remaining': size,
                                 'kerf': 0, 'discarded': 0, 'separations': 0, 'cuts': [], 'discard_events': []})
            quantity = min(left, fit)
            exact = size == quantity * length + (quantity - 1) * kerf
            separations = quantity - int(exact)
            loss = separations * kerf
            remaining = size - quantity * length - loss
            discarded = remaining if immediate and remaining < minimum else 0
            remaining -= discarded
            irreversible += (loss + discarded) * count
            left -= quantity * count
            if detailed:
                bar = bars[index]
                bar['remaining'] = remaining
                bar['kerf'] += loss; bar['discarded'] += discarded; bar['separations'] += separations
                if record:
                    bar['cuts'].append({'row_id': order['row_id'], 'pedido': order['pedido'],
                        'grupo': group, 'longitud': length, 'cantidad': quantity,
                        'kerf': loss, 'discarded': discarded, 'separations': separations})
            put(remaining, [index] if detailed else count)
    flush()
    return (consumed, irreversible, commercial, count_bars), bars if record else None
