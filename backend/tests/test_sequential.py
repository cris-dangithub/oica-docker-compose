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
    def test_perdida_exacta_y_capacidad_insuficiente(self):
        options = {'perdida_mm': '1', 'minimo_activo': False}
        for size, pieces, expected in [(1, 1, 0), (2.001, 2, .001)]:
            p = normalize([row('a', 1, pieces)], [{'diametro': '#3', 'longitud_m': size, 'cantidad': 1}], options=options)
            r = optimize(p)
            self.assertAlmostEqual(r['metrics']['perdida_corte_kg'], expected)
            self.assertEqual(r['metrics']['sobrante_final_kg'], 0)
        p = normalize([row('a', 1, 2)], [{'diametro': '#3', 'longitud_m': 2, 'cantidad': 1}], options=options)
        with self.assertRaises(Infeasible):
            optimize(p)
        p = normalize([row('a', 1)], [{'diametro': '#3', 'longitud_m': 1.0005, 'cantidad': 1}], options=options)
        with self.assertRaises(Infeasible):
            optimize(p)

    def test_descarte_por_operacion_y_fin_etapa(self):
        catalog = [{'diametro': '#3', 'longitud_m': 3, 'cantidad': None}]
        opts = {'perdida_activa': False, 'modo_minimo': 'manual', 'minimo_m': '2.5'}
        a = optimize(normalize([row('a', 1, 2)], catalog, options=opts))
        b = optimize(normalize([row('a', 1, 2)], catalog, options={**opts, 'descarte': 'fin_etapa'}))
        self.assertEqual(a['metrics']['barras'], 2)
        self.assertEqual(a['metrics']['descartado_kg'], 4)
        self.assertEqual(b['metrics']['barras'], 1)
        self.assertEqual(b['metrics']['descartado_kg'], 1)
        c = optimize(normalize([row('a', 1), row('b', 1, group=2)], catalog,
                               options={**opts, 'descarte': 'fin_etapa'}))
        self.assertEqual(c['metrics']['barras'], 2)

    def test_minimo_fijo_igualdad_y_exclusion(self):
        opts = {'perdida_activa': False}
        p = normalize([row('a', 2), row('b', 1, group=3)],
                      [{'diametro': '#3', 'longitud_m': 3, 'cantidad': 1}],
                      [{'diametro': '#3', 'longitud_m': .9, 'cantidad': 10},
                       {'diametro': '#8', 'longitud_m': .1, 'cantidad': 1}], opts)
        self.assertEqual(p['resolved_parameters']['minimos_por_diametro_m'], {'#3': '1'})
        self.assertEqual(len(p['excluded_inventory']), 1)
        r = optimize(p)
        self.assertEqual(r['metrics']['barras'], 1)
        self.assertEqual(r['metrics']['desperdicio_porcentaje'], 0)
        self.assertEqual(r['inventory'], [{'diametro': '#8', 'longitud_m': '0.1', 'cantidad': 1}])

    def test_parametros_invalidos_y_compatibilidad(self):
        from cutting.parameters import parse
        self.assertEqual(parse({'proceso': 'cizalla'})['perdida_mm'], '0')
        for patch in [{'perdida_mm': '-1'}, {'perdida_mm': 'NaN'}, {'minimo_m': 0},
                      {'minimo_m': 'Infinity'}, {'minimo_activo': 'false'}, {'descarte': 'otro'}, {'xxx': 1}]:
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                normalize([row('a', 1)], options=patch)
        legacy = optimize(normalize([row('a', 2, 5)]))
        off = optimize(normalize([row('a', 2, 5)], options={'perdida_activa': False, 'minimo_activo': False}))
        self.assertEqual(legacy['bars'], off['bars'])

    def test_objetivo_global_y_balance_no_premian_sobrantes_hipoteticos(self):
        catalog = [{'diametro': '#3', 'longitud_m': l, 'cantidad': None} for l in (6, 9)]
        opts = {'perdida_activa': False}
        a = optimize(normalize([row('a', 4)], catalog, options=opts))
        b = optimize(normalize([row('a', 4), row('b', 4, group=2)], catalog, options=opts))
        self.assertEqual(a['metrics']['masa_inicial_kg'], 6)
        self.assertEqual(b['metrics']['masa_inicial_kg'], 9)
        for r in (a, b):
            m = r['metrics']
            self.assertAlmostEqual(m['masa_inicial_kg'], m['piezas_kg'] + m['perdida_corte_kg']
                                   + m['descartado_kg'] + m['sobrante_final_kg'])

    def test_huellas_separan_condiciones_y_validador_rechaza_perdida_alterada(self):
        data = [row('a', 1, 2)]
        hashes = {normalize(data, options={'perdida_activa': k, 'minimo_activo': t})['hash']
                  for k in (True, False) for t in (True, False)}
        self.assertEqual(len(hashes), 4)
        p = normalize(data, options={})
        r = optimize(p)
        r['bars'][0]['kerf'] += 1
        with self.assertRaises(ValueError):
            validate(p, r['bars'], r['inventory'])

    def test_reglas_agrupadas_con_validador_independiente(self):
        import random
        rng = random.Random(723)
        for case in range(100):
            data = [row(i, rng.randint(1, 9) / 10, rng.randint(1, 40), rng.randint(1, 4)) for i in range(8)]
            p = normalize(data, [{'diametro': '#3', 'longitud_m': 3, 'cantidad': None}], options={
                'perdida_mm': str(rng.choice([0, 1, 30])), 'minimo_m': str(rng.choice([.1, .8, 2.5])),
                'modo_minimo': 'manual', 'descarte': rng.choice(['inmediato', 'fin_etapa'])})
            genome = tuple((rng.random(), rng.randrange(3)) for _ in data)
            a, _ = decode(p['orders'], p['stock'], genome, rules=p['rules'])
            b, bars = decode(p['orders'], p['stock'], genome, record=True, rules=p['rules'])
            self.assertEqual(a, b, f'Caso {case}')
            from collections import Counter
            from decimal import Decimal
            inv = Counter((b['diametro'], b['remaining']) for b in bars if b['remaining'])
            inventory = [{'diametro': d, 'longitud_m': str(Decimal(l) / p['scale']), 'cantidad': q} for (d, l), q in inv.items()]
            validate(p, bars, inventory)

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
