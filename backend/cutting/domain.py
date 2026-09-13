"""Contrato de entrada y validador independiente del algoritmo genético."""
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation
import hashlib
import json


def decimal(value):
    try:
        result = Decimal(str(value).strip().replace(',', '.'))
    except (InvalidOperation, ValueError):
        raise ValueError(f'Número inválido: {value}') from None
    if not result.is_finite():
        raise ValueError(f'Número no finito: {value}')
    return result


def positive(value, integer=False):
    number = decimal(value)
    if number <= 0 or (integer and number != number.to_integral_value()):
        raise ValueError(f'Se requiere un número positivo{" entero" if integer else ""}: {value}')
    return int(number) if integer else number


def diameter(value):
    text = str(value).strip().lstrip('#')
    return f'#{positive(text, integer=True)}'


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(',', ':')).encode()).hexdigest()


def default_catalog():
    return [{'diametro': f'#{d}', 'longitud_m': length, 'cantidad': None}
            for d in (3, 4, 5, 6, 7, 8, 9, 10, 11, 14, 18) for length in (6, 9, 12)]


def normalize(rows, catalog=None, inventory=None):
    """Escala exacta de longitudes. La identidad es la fila, no el rótulo del pedido."""
    orders, lengths, densities = [], [], defaultdict(list)
    for index, row in enumerate(rows, 2):
        # Plantillas Excel: ignorar únicamente filas sin datos de demanda.
        fields = ['N° Orden', 'N° de Barra', 'Longitud total (m)', 'Cantidad']
        if all(row.get(k) in (None, '') for k in fields):
            continue
        if row.get('N° Orden') in (None, ''):
            raise ValueError(f'Fila {index}: falta N° Orden')
        length = positive(row.get('Longitud total (m)'))
        quantity = positive(row.get('Cantidad'), integer=True)
        diam = diameter(row.get('N° de Barra'))
        group = positive(row.get('Grupo de Ejecución', 1), integer=True)
        mass = positive(row.get('Masa total (kg)'))
        densities[diam].append(mass / (length * quantity))
        orders.append({'row_id': index, 'pedido': str(row['N° Orden']), 'diametro': diam,
                       'grupo': group, 'longitud': length, 'cantidad': quantity})
        lengths.append(length)
    if not orders:
        raise ValueError('La cartilla no contiene pedidos')
    rho = {}
    for diam, values in densities.items():
        # Solo tolerar error numérico de fórmulas XLSX, no diferencias físicas.
        if max(values) - min(values) > min(values) * Decimal('0.000001'):
            raise ValueError(f'Masa por metro inconsistente para {diam}; corregir la cartilla')
        rho[diam] = str(values[0])
    stock = []
    for source, entries in [('comercial', default_catalog() if catalog is None else catalog),
                            ('adicional', inventory or [])]:
        if not isinstance(entries, list):
            raise ValueError('El inventario y el catálogo deben ser listas')
        seen = set()
        for index, entry in enumerate(entries):
            diam = diameter(entry.get('diametro'))
            length = positive(entry.get('longitud_m'))
            unlimited = source == 'comercial' and entry.get('cantidad') is None
            quantity = None if unlimited else positive(entry.get('cantidad'), integer=True)
            if source == 'comercial' and (diam, length) in seen:
                raise ValueError(f'Longitud comercial duplicada: {diam}, {length}')
            seen.add((diam, length))
            stock.append({'stock_id': f'{source}:{index}', 'origen': source,
                          'diametro': diam, 'longitud': length, 'cantidad': quantity})
            lengths.append(length)
    scale = 10 ** max(0, max(-v.normalize().as_tuple().exponent for v in lengths))
    for item in orders + stock:
        item['longitud'] = int(item['longitud'] * scale)
    problem = {'orders': orders, 'stock': stock, 'scale': scale, 'densities': rho}
    problem['hash'] = fingerprint(problem)
    return problem


def validate(problem, bars, final_inventory):
    """Reconstruye demanda y saldos desde las barras raíz; no confía en fitness."""
    orders = {o['row_id']: o for o in problem['orders']}
    stock = {s['stock_id']: s for s in problem['stock']}
    actual, consumed, expected_inventory = Counter(), Counter(), Counter()
    used_mass = waste_mass = Decimal(0)
    seen = set()
    detail = defaultdict(lambda: {'longitud_inicial': 0, 'sobrante_final': 0, 'barras': 0})
    for bar in bars:
        if bar['bar_id'] in seen:
            raise ValueError('Barra raíz duplicada')
        seen.add(bar['bar_id'])
        source = stock.get(bar['stock_id'])
        if source is None or bar['diametro'] != source['diametro'] or bar['longitud'] != source['longitud']:
            raise ValueError('Origen de barra inconsistente')
        consumed[source['stock_id']] += 1
        remaining, last_group = bar['longitud'], 0
        if not bar['cuts']:
            raise ValueError('Una barra no utilizada no pertenece al plan de corte')
        for cut in bar['cuts']:
            order = orders.get(cut['row_id'])
            if order is None or order['diametro'] != bar['diametro']:
                raise ValueError('Pedido inexistente o mezcla de diámetros')
            if cut['grupo'] != order['grupo'] or cut['longitud'] != order['longitud']:
                raise ValueError('Se alteró la longitud o el grupo del pedido')
            if cut['grupo'] < last_group:
                raise ValueError('Consumo desde una etapa futura')
            count = positive(cut['cantidad'], integer=True)
            remaining -= cut['longitud'] * count
            if remaining < 0:
                raise ValueError('Corte físicamente imposible')
            actual[cut['row_id']] += count
            last_group = cut['grupo']
        if remaining != bar['remaining']:
            raise ValueError('Saldo incorrecto de barra')
        diam = bar['diametro']
        density = Decimal(problem['densities'][diam])
        used_mass += Decimal(bar['longitud']) / problem['scale'] * density
        waste_mass += Decimal(remaining) / problem['scale'] * density
        detail[diam]['longitud_inicial'] += bar['longitud']
        detail[diam]['sobrante_final'] += remaining
        detail[diam]['barras'] += 1
        if remaining:
            expected_inventory[(diam, remaining)] += 1
    if actual != Counter({o['row_id']: o['cantidad'] for o in orders.values()}):
        raise ValueError('La solución no satisface exactamente cada pedido')
    for source in stock.values():
        if source['cantidad'] is not None:
            unused = source['cantidad'] - consumed[source['stock_id']]
            if unused < 0:
                raise ValueError('Inventario consumido más de una vez')
            if unused:
                expected_inventory[(source['diametro'], source['longitud'])] += unused
    output_inventory = Counter()
    for row in final_inventory:
        length = positive(row['longitud_m']) * problem['scale']
        if length != length.to_integral_value():
            raise ValueError('Se alteró la precisión del inventario final')
        output_inventory[(diameter(row['diametro']), int(length))] += positive(row['cantidad'], integer=True)
    if expected_inventory != output_inventory:
        raise ValueError('Inventario final inconsistente')
    return {'valido': True, 'piezas': sum(actual.values()), 'barras': len(bars),
            'masa_inicial_kg': float(used_mass), 'sobrante_final_kg': float(waste_mass),
            'desperdicio_porcentaje': float(100 * waste_mass / used_mass),
            'por_diametro': dict(detail), 'escala_longitudes': problem['scale']}
