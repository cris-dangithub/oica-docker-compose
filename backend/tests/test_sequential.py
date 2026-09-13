"""Regresiones del contrato físico; sin Flask, Celery, pandas ni archivos."""
import copy
import unittest
from cutting.domain import normalize, validate
from cutting.optimizer import optimize, Infeasible, decode
from cutting.estimation import estimate


def row(order, length, quantity=1, group=1, diam='#3'):
    return {'N° Orden': order, 'Longitud total (m)': length, 'Cantidad': quantity,
            'Grupo de Ejecución': group, 'N° de Barra': diam,
            'Masa total (kg)': length * quantity}


class SequentialTests(unittest.TestCase):
    def test_evaluacion_agrupada_equivale_a_barras_individuales(self):
        import random
        rng = random.Random(102)
        for case in range(60):
            data = [row(i, rng.randint(1, 9) / 10, rng.randint(1, 60), rng.randint(1, 4)) for i in range(12)]
            p = normalize(data, [{'diametro': '#3', 'longitud_m': 3, 'cantidad': None}],
                          [{'diametro': '#3', 'longitud_m': 1.4, 'cantidad': 5}])
            genome = tuple((rng.random(), rng.randrange(3)) for _ in data)
            score, _ = decode(p['orders'], p['stock'], genome)
            detailed_score, _ = decode(p['orders'], p['stock'], genome, record=True)
            self.assertEqual(score, detailed_score, f'Caso {case}')

    def test_estimacion_no_promete_tiempo_sin_datos(self):
        self.assertIsNone(estimate([10, 20])['remaining_seconds'])
        self.assertEqual(estimate([10] * 5, 5)['remaining_seconds'], [3, 7])
        self.assertIsNone(estimate([10] * 5, 30)['remaining_seconds'])

    def test_masa_ponderada_por_diametro(self):
        data = [row('a', 6), {**row('b', 4, diam='#4'), 'Masa total (kg)': 8}]
        p = normalize(data, [{'diametro': '#3', 'longitud_m': 9, 'cantidad': 1},
                             {'diametro': '#4', 'longitud_m': 5, 'cantidad': 1}])
        r = optimize(p)
        self.assertAlmostEqual(r['metrics']['desperdicio_porcentaje'], 100 * 5 / 19)

    def test_reutilizacion_y_doble_conteo(self):
        p = normalize([row('a', 6), row('b', 4, group=3)],
                      [{'diametro': '#3', 'longitud_m': 9, 'cantidad': 1}],
                      [{'diametro': '#3', 'longitud_m': 5, 'cantidad': 1}])
        r = optimize(p)
        self.assertAlmostEqual(r['metrics']['desperdicio_porcentaje'], 100 * 4 / 14)
        self.assertEqual(r['metrics']['barras'], 2)

    def test_cadena_y_sobrante_sin_minimo(self):
        p = normalize([row('a', 6), row('b', 2, group=2), row('c', .9, group=3)],
                      [{'diametro': '#3', 'longitud_m': 9, 'cantidad': 1}])
        r = optimize(p)
        self.assertEqual(len(r['bars']), 1)
        self.assertEqual(r['inventory'][0]['longitud_m'], '0.1')
        self.assertEqual(r['metrics']['masa_inicial_kg'], 9)

    def test_identificador_repetido_no_altera_longitudes(self):
        p = normalize([row('a', 3), row('a', 2)])
        r = optimize(p)
        self.assertEqual(sorted(c['longitud'] for b in r['bars'] for c in b['cuts']), [2, 3])

    def test_inventario_no_usado_excluido_metrica(self):
        p = normalize([row('a', 6)], inventory=[{'diametro': '#8', 'longitud_m': 100, 'cantidad': 20}])
        r = optimize(p)
        self.assertEqual(r['metrics']['desperdicio_porcentaje'], 0)
        self.assertIn({'diametro': '#8', 'longitud_m': '100', 'cantidad': 20}, r['inventory'])

    def test_validador_detecta_corrupcion(self):
        p = normalize([row('a', 3), row('b', 2, group=2)],
                      [{'diametro': '#3', 'longitud_m': 6, 'cantidad': 1}])
        r = optimize(p)
        for mutation in ('cantidad', 'longitud', 'grupo', 'remaining', 'duplicado', 'inventario'):
            bad = copy.deepcopy(r)
            if mutation in ('cantidad', 'longitud', 'grupo'):
                bad['bars'][0]['cuts'][0][mutation] += 1
            elif mutation == 'remaining':
                bad['bars'][0]['remaining'] += 1
            elif mutation == 'duplicado':
                bad['bars'].append(copy.deepcopy(bad['bars'][0]))
            else:
                bad['inventory'] = []
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                validate(p, bad['bars'], bad['inventory'])

    def test_entradas_invalidas(self):
        for field, value in [('Cantidad', 1.5), ('N° de Barra', None),
                             ('Grupo de Ejecución', 0), ('Longitud total (m)', float('nan'))]:
            data = row('a', 2); data[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                normalize([data])
        with self.assertRaises(ValueError):
            normalize([row('a', 2), {**row('b', 2), 'Masa total (kg)': 3}])

    def test_stock_finito_inviable(self):
        p = normalize([row('a', 7, 2)], [{'diametro': '#3', 'longitud_m': 9, 'cantidad': 1}])
        with self.assertRaises(Infeasible):
            optimize(p)

    def test_semilla_y_elitismo(self):
        p = normalize([row('a', 3, 2), row('b', 2, 3), row('c', 1, 5, group=2)])
        a, b = optimize(p, seed=42), optimize(p, seed=42)
        self.assertEqual(a['bars'], b['bars'])
        for m in a['metrics']['evolucion'].values():
            self.assertLessEqual(m['longitud_final'], m['longitud_inicial'])


if __name__ == '__main__':
    unittest.main()
