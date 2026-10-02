"""Capa de análisis posterior a la optimización (spec 001); sin Flask, Celery ni archivos."""
import copy
import unittest
from cutting.domain import normalize
from cutting.optimizer import optimize


def row(order, length, quantity=1, group=1, diam='#3', mass_per_m=None):
    return {'N° Orden': order, 'Longitud total (m)': length, 'Cantidad': quantity,
            'Grupo de Ejecución': group, 'N° de Barra': diam,
            'Masa total (kg)': length * quantity * (mass_per_m or 1)}


def plan(rows, catalog=None, options=None, seed=0, inventory=None):
    problem = normalize(rows, catalog, inventory, options)
    return problem, optimize(problem, seed=seed)


class InvarianciaTests(unittest.TestCase):
    """El análisis es una métrica: no cambia el plan, la huella ni la búsqueda (FR-005, FR-016)."""

    ROWS = [row('a', 2.5, 3, 1), row('b', 1.2, 4, 2), row('c', 0.8, 5, 2, '#4', 0.994)]

    def test_analizar_no_altera_el_plan(self):
        from cutting.analysis import analizar
        problem, result = plan(self.ROWS, options={})
        bars, inventory, metrics = (copy.deepcopy(result[k]) for k in ('bars', 'inventory', 'metrics'))
        analisis = analizar(problem, result, 7.5)
        self.assertEqual(result['bars'], bars)
        self.assertEqual(result['inventory'], inventory)
        self.assertEqual(result['metrics'], metrics)
        self.assertEqual(analisis['version'], 'analisis-1')
        self.assertEqual(analisis['umbral_desperdicio_pct'], 7.5)
        self.assertTrue(analisis['verificacion']['valido'])

    def test_umbral_fuera_de_la_huella(self):
        # El worker normaliza con estas claves de la configuración; el umbral nunca llega allí.
        config = {'catalog': None, 'inventory': [], 'parametros_corte': {}}
        with_umbral = {**config, 'umbral_desperdicio_pct': 5.0}
        hashes = {normalize(self.ROWS, c['catalog'], c['inventory'], c['parametros_corte'])['hash']
                  for c in (config, with_umbral)}
        self.assertEqual(len(hashes), 1)

    def test_misma_semilla_mismo_plan(self):
        _, first = plan(self.ROWS, options={}, seed=3)
        _, second = plan(self.ROWS, options={}, seed=3)
        self.assertEqual(first['bars'], second['bars'])


class AdmisibilidadTests(unittest.TestCase):
    """US1: umbral opcional frente al desperdicio por masa de INF-012 (FR-003, FR-004)."""

    # Dos diámetros, pérdida por corte activa y saldos para que ambos tengan desperdicio.
    ROWS = [row('a', 2.5, 3, 1), row('b', 1.2, 4, 2), row('c', 0.8, 5, 2, '#4', 0.994),
            row('d', 3.7, 2, 1, '#4', 0.994)]

    def setUp(self):
        self.problem, self.result = plan(self.ROWS, options={})
        self.metrics = self.result['metrics']

    def evaluar(self, umbral):
        from cutting.analysis import evaluar_admisibilidad
        return evaluar_admisibilidad(self.problem, self.metrics, umbral)

    def test_proyecto_igual_a_desperdicio_registrado(self):
        proyecto = self.evaluar(None)['proyecto']
        self.assertAlmostEqual(proyecto['desperdicio_pct'], self.metrics['desperdicio_porcentaje'], delta=1e-9)

    def test_estados_y_diferencia(self):
        waste = self.metrics['desperdicio_porcentaje']
        self.assertEqual(self.evaluar(None)['proyecto'],
                         {'estado': 'sin_evaluar', 'desperdicio_pct': waste, 'diferencia_pp': None})
        dentro = self.evaluar(waste + 1)['proyecto']
        self.assertEqual(dentro['estado'], 'dentro')
        self.assertAlmostEqual(dentro['diferencia_pp'], -1)
        excede = self.evaluar(waste / 2)['proyecto']
        self.assertEqual(excede['estado'], 'excede')
        self.assertAlmostEqual(excede['diferencia_pp'], waste / 2)
        # Empate exacto: dentro de lo admisible.
        self.assertEqual(self.evaluar(waste)['proyecto']['estado'], 'dentro')

    def test_por_diametro_ponderado_por_masa(self):
        from decimal import Decimal
        por_diametro = {d['diametro']: d for d in self.evaluar(5.0)['por_diametro']}
        self.assertEqual(sorted(por_diametro), ['#3', '#4'])
        total_desperdicio = total_inicial = Decimal(0)
        for diam, detail in self.metrics['por_diametro'].items():
            rho = Decimal(self.problem['densities'][diam])
            waste = detail['sobrante_final'] + detail['perdida_corte'] + detail['descartado']
            self.assertAlmostEqual(por_diametro[diam]['desperdicio_pct'],
                                   float(100 * Decimal(waste) / detail['longitud_inicial']), delta=1e-9)
            self.assertEqual(por_diametro[diam]['estado'],
                             'dentro' if por_diametro[diam]['desperdicio_pct'] <= 5.0 else 'excede')
            total_desperdicio += Decimal(waste) * rho
            total_inicial += Decimal(detail['longitud_inicial']) * rho
        # La agregación por masa reproduce el desperdicio del proyecto.
        self.assertAlmostEqual(float(100 * total_desperdicio / total_inicial),
                               self.metrics['desperdicio_porcentaje'], delta=1e-9)

    def test_perdidas_irrecuperable_y_reutilizable(self):
        from cutting.analysis import perdidas
        p = perdidas(self.problem, self.metrics)
        total = self.metrics['masa_inicial_kg']
        self.assertAlmostEqual(p['irrecuperable']['kg'], self.metrics['perdida_irrecuperable_kg'])
        self.assertAlmostEqual(p['reutilizable']['kg'], self.metrics['sobrante_final_kg'])
        self.assertAlmostEqual(p['irrecuperable']['pct'], 100 * self.metrics['perdida_irrecuperable_kg'] / total)
        self.assertAlmostEqual(p['reutilizable']['pct'], 100 * self.metrics['sobrante_final_kg'] / total)
        self.assertGreater(p['irrecuperable']['kg'], 0)
        self.assertAlmostEqual(p['irrecuperable']['pct'] + p['reutilizable']['pct'],
                               self.metrics['desperdicio_porcentaje'])
        self.assertEqual(sorted(p['por_diametro']), ['#3', '#4'])

    def test_analizar_incluye_admisibilidad(self):
        from cutting.analysis import analizar
        analisis = analizar(self.problem, self.result, None)
        self.assertEqual(analisis['admisibilidad']['proyecto']['estado'], 'sin_evaluar')
        self.assertIn('irrecuperable', analisis['perdidas'])


class ResumenCompraTests(unittest.TestCase):
    """US2: barras por diámetro, longitud y origen; el inventario no cuenta como compra (FR-027)."""

    def compra(self, problem, result):
        from cutting.analysis import resumen_compra
        return resumen_compra(problem, result)

    def test_suma_por_diametro_y_longitud_igual_al_plan(self):
        from collections import Counter
        problem, result = plan(AdmisibilidadTests.ROWS, options={})
        lineas = self.compra(problem, result)
        esperado = Counter((b['diametro'], b['longitud']) for b in result['bars'])
        obtenido = Counter()
        for linea in lineas:
            obtenido[(linea['diametro'], round(linea['longitud_m'] * problem['scale']))] += linea['barras']
        self.assertEqual(obtenido, esperado)
        self.assertEqual([l['diametro'] for l in lineas], sorted((l['diametro'] for l in lineas),
                         key=lambda d: int(d[1:])))

    def test_masa_y_aprovechamiento(self):
        from decimal import Decimal
        problem, result = plan(AdmisibilidadTests.ROWS, options={})
        for linea in self.compra(problem, result):
            bars = [b for b in result['bars'] if b['diametro'] == linea['diametro'] and b['origen'] == linea['origen']
                    and b['longitud'] == round(linea['longitud_m'] * problem['scale'])]
            rho = Decimal(problem['densities'][linea['diametro']])
            masa = Decimal(sum(b['longitud'] for b in bars)) / problem['scale'] * rho
            piezas = Decimal(sum(c['longitud'] * c['cantidad'] for b in bars for c in b['cuts'])) / problem['scale'] * rho
            self.assertAlmostEqual(linea['masa_kg'], float(masa))
            self.assertAlmostEqual(linea['aprovechamiento_pct'], float(100 * piezas / masa))
            self.assertLessEqual(linea['aprovechamiento_pct'], 100)

    def test_inventario_adicional_va_aparte(self):
        rows = [row('a', 3.5, 3), row('b', 1.0, 2)]
        inventory = [{'diametro': '#3', 'longitud_m': 4, 'cantidad': 1}]
        problem, result = plan(rows, options={}, inventory=inventory)
        lineas = self.compra(problem, result)
        adicional = [l for l in lineas if l['origen'] == 'adicional']
        self.assertEqual(sum(l['barras'] for l in adicional),
                         sum(1 for b in result['bars'] if b['origen'] == 'adicional'))
        self.assertTrue(adicional, 'el plan debería usar la barra de inventario')
        self.assertEqual({l['origen'] for l in lineas}, {'comercial', 'adicional'})

    def test_longitudes_no_estandar(self):
        catalog = [{'diametro': '#3', 'longitud_m': 7.5, 'cantidad': None}]
        problem, result = plan([row('a', 2.4, 5)], catalog=catalog)
        self.assertEqual({l['longitud_m'] for l in self.compra(problem, result)}, {7.5})

    def test_analizar_incluye_compra_y_verificacion(self):
        from cutting.analysis import analizar
        problem, result = plan(AdmisibilidadTests.ROWS, options={})
        analisis = analizar(problem, result)
        self.assertTrue(analisis['verificacion']['valido'])
        self.assertEqual(analisis['verificacion']['comprobaciones'],
                         ['demanda', 'diametro', 'capacidad', 'etapas', 'inventario'])
        self.assertEqual(sum(l['barras'] for l in analisis['resumen_compra']), len(result['bars']))


class PatronesTests(unittest.TestCase):
    """US3: barras idénticas forman un patrón «× repeticiones» (FR-007, FR-011)."""

    @staticmethod
    def bar(bar_id, cuts, longitud=900, origen='comercial', diam='#3', remaining=0, kerf=0, discarded=0, events=()):
        return {'bar_id': bar_id, 'stock_id': f'{origen}:0', 'origen': origen, 'diametro': diam,
                'longitud': longitud, 'remaining': remaining, 'kerf': kerf, 'discarded': discarded,
                'discard_events': [{'grupo': g, 'longitud': l} for g, l in events],
                'cuts': [{'row_id': 2, 'pedido': 'x', 'grupo': g, 'longitud': l, 'cantidad': q} for g, l, q in cuts]}

    def agrupar(self, bars, scale=100):
        from cutting.patterns import agrupar
        return agrupar({'scale': scale}, bars)

    def test_barras_identicas_un_patron(self):
        bars = [self.bar(f'#3:{i}', [(1, 300, 3)]) for i in range(4)]
        patrones, por_barra = self.agrupar(bars)
        self.assertEqual(len(patrones), 1)
        self.assertEqual(patrones[0]['repeticiones'], 4)
        self.assertEqual(set(por_barra.values()), {'P-#3-001'})

    def test_etapa_origen_y_balance_distinguen(self):
        base = self.bar('a', [(1, 300, 2)], remaining=300)
        variantes = [self.bar('b', [(2, 300, 2)], remaining=300),                  # otra etapa
                     self.bar('c', [(1, 300, 2)], remaining=300, origen='adicional'),
                     self.bar('d', [(1, 300, 2)], remaining=299, kerf=1),         # otra pérdida
                     self.bar('e', [(1, 300, 2)], remaining=0, discarded=300, events=[(1, 300)])]
        patrones, _ = self.agrupar([base] + variantes)
        self.assertEqual(len(patrones), 5)

    def test_todas_distintas_y_orden_determinista(self):
        bars = [self.bar(f'#3:{i}', [(1, 100 + i, 1)], remaining=800 - i) for i in range(6)]
        first, por_barra = self.agrupar(bars)
        second, _ = self.agrupar(list(reversed(bars)))
        self.assertEqual(len(first), 6)
        self.assertEqual([p['patron_id'] for p in first], [p['patron_id'] for p in second])
        self.assertEqual([p['secuencia'] for p in first], [p['secuencia'] for p in second])
        self.assertEqual(len(set(por_barra.values())), 6)

    def test_invariantes_con_plan_real(self):
        from collections import Counter
        from cutting.patterns import agrupar, verificar
        problem, result = plan(AdmisibilidadTests.ROWS + [row('e', 1.2, 6, 1), row('f', 0.6, 9, 2)], options={})
        patrones, por_barra = agrupar(problem, result['bars'])
        self.assertEqual(sum(p['repeticiones'] for p in patrones), len(result['bars']))
        self.assertEqual(set(por_barra), {b['bar_id'] for b in result['bars']})
        demanda = Counter()
        for p in patrones:
            for grupo, longitud, cantidad in p['secuencia']:
                demanda[(p['diametro'], grupo, longitud)] += cantidad * p['repeticiones']
        esperado = Counter()
        for o in problem['orders']:
            esperado[(o['diametro'], o['grupo'], o['longitud'])] += o['cantidad']
        self.assertEqual(demanda, esperado)
        verificar(problem, patrones, result['bars'])
        for diam in {p['diametro'] for p in patrones}:
            ids = [p['patron_id'] for p in patrones if p['diametro'] == diam]
            self.assertEqual(ids, [f'P-{diam}-{i:03d}' for i in range(1, len(ids) + 1)])

    def test_verificar_detecta_inconsistencias(self):
        from cutting.patterns import agrupar, verificar
        problem, result = plan(AdmisibilidadTests.ROWS, options={})
        patrones, _ = agrupar(problem, result['bars'])
        patrones[0]['repeticiones'] += 1
        with self.assertRaises(ValueError):
            verificar(problem, patrones, result['bars'])

    def test_analizar_resume_patrones(self):
        from cutting.analysis import analizar
        problem, result = plan(AdmisibilidadTests.ROWS, options={})
        resumen = analizar(problem, result)['patrones']
        self.assertEqual(resumen['barras'], len(result['bars']))
        self.assertLessEqual(len(resumen['top']), 10)
        self.assertEqual(resumen['max_repeticiones'], max(p['repeticiones'] for p in resumen['top']))


try:
    import scipy  # noqa: F401
    HAY_SCIPY = True
except ImportError:
    HAY_SCIPY = False


def optimo_fuerza_bruta(problem, d):
    """Material mínimo exacto (escalado) por enumeración, para instancias pequeñas sin etapas."""
    from functools import lru_cache
    from itertools import product
    from cutting.bound import datos
    items, tipos, e = datos(problem, d)
    largos = [l for l, _ in items]
    barras = sorted(t['longitud'] for t in tipos)

    def cabe(a):
        piezas = sum(a)
        total = sum(q * l for q, l in zip(a, largos))
        return next((L for L in barras if total + max(piezas - 1, 0) * e <= L), None)

    @lru_cache(maxsize=None)
    def f(estado):
        if not any(estado):
            return 0
        primero = next(i for i, q in enumerate(estado) if q)
        mejor = None
        for a in product(*(range(q + 1) for q in estado)):
            if a[primero] == 0:
                continue
            L = cabe(a)
            if L is None:
                continue
            resto = f(tuple(q - x for q, x in zip(estado, a)))
            if resto is not None and (mejor is None or L + resto < mejor):
                mejor = L + resto
        return mejor
    return f(tuple(q for _, q in items))


class CotaTests(unittest.TestCase):
    """US4: cota inferior por patrones, siempre válida, solo como métrica (FR-012 a FR-016)."""

    CATALOGO = [{'diametro': '#3', 'longitud_m': L, 'cantidad': None} for L in (6, 9, 12)]

    def instancias(self, total=20):
        import random
        rng = random.Random(7)
        for _ in range(total):
            largos = rng.sample([1.5, 2.2, 2.7, 3.4, 4.1, 5.5, 7.3], rng.randint(1, 3))
            rows = [row(f'p{i}', l, rng.randint(1, 3)) for i, l in enumerate(largos)]
            if sum(r['Cantidad'] for r in rows) <= 8:
                yield normalize(rows, self.CATALOGO)

    def test_mochila_exacta(self):
        from itertools import product
        from cutting.bound import mochila
        pesos, valores, cotas = [4, 7, 9], [1.1, 2.3, 2.9], [3, 2, 2]
        valor, cantidades = mochila(20, pesos, valores, cotas)
        mejor = max(sum(v * q for v, q in zip(valores, a)) for a in product(*(range(c + 1) for c in cotas))
                    if sum(p * q for p, q in zip(pesos, a)) <= 20)
        self.assertAlmostEqual(valor, mejor)
        self.assertAlmostEqual(sum(v * q for v, q in zip(valores, cantidades)), valor)
        self.assertLessEqual(sum(p * q for p, q in zip(pesos, cantidades)), 20)

    def test_certificado_valido_con_cualquier_dual(self):
        # Sin scipy: cualquier y ≥ 0 da una cota ≤ óptimo (validez independiente del solver).
        import random
        from cutting.bound import datos, certificado
        rng = random.Random(3)
        for problem in self.instancias():
            optimo = optimo_fuerza_bruta(problem, '#3')
            items, tipos, e = datos(problem, '#3')
            for _ in range(5):
                y = [rng.uniform(0, 2 * max(t['longitud'] for t in tipos)) for _ in items]
                self.assertLessEqual(certificado(items, tipos, e, y), optimo + 1e-6)

    def test_cota_simple_valida(self):
        from cutting.bound import cota_simple
        for problem in self.instancias():
            simple = cota_simple(problem, '#3')
            self.assertLessEqual(simple['material'], optimo_fuerza_bruta(problem, '#3'))
            self.assertGreaterEqual(simple['barras_minimas'], 1)

    def test_sin_scipy_no_disponible(self):
        from unittest.mock import patch
        from cutting.bound import cota_plan
        problem, result = plan([row('a', 1.4, 10)], self.CATALOGO)
        with patch('cutting.bound._linprog', side_effect=ImportError('No module named scipy')):
            cota = cota_plan(problem, result['metrics'])
        self.assertEqual(cota['estado'], 'no_disponible')
        self.assertIn('scipy', cota['motivo'])
        self.assertIsNotNone(cota['proyecto']['simple_desperdicio_pct'])

    def test_fallo_del_solver_no_detiene_el_plan(self):
        from unittest.mock import patch
        from cutting.analysis import analizar
        def roto(*args, **kwargs):
            raise RuntimeError('fallo simulado del solver')
        problem, result = plan([row('a', 1.4, 10)], self.CATALOGO)
        with patch('cutting.bound._linprog', return_value=roto):
            analisis = analizar(problem, result)
        self.assertEqual(analisis['cota']['estado'], 'no_disponible')
        self.assertIn('fallo simulado', analisis['cota']['motivo'])

    def test_error_de_dominio(self):
        from unittest.mock import patch
        from cutting.analysis import analizar
        problem, result = plan([row('a', 1.4, 10)], self.CATALOGO)
        waste = result['metrics']['desperdicio_porcentaje']
        falsa = {'estado': 'calculada', 'motivo': None, 'ajustada': True,
                 'proyecto': {'material_kg': 1.0, 'desperdicio_pct': waste + 5, 'simple_desperdicio_pct': 0.0},
                 'por_diametro': [{'diametro': '#3', 'material_m': 1.0, 'material_kg': 1.0,
                                   'desperdicio_pct': waste + 5, 'ajustada': True,
                                   'simple': {'material_m': 1.0, 'desperdicio_pct': 0.0, 'barras_minimas': 1}}]}
        with patch('cutting.bound.cota_plan', return_value=falsa):
            with self.assertRaises(ValueError) as error:
                analizar(problem, result)
        self.assertTrue(str(error.exception).startswith('Error de dominio:'))

    @unittest.skipUnless(HAY_SCIPY, 'scipy no instalado: cota no disponible')
    def test_caso_analitico(self):
        from cutting.bound import cota_diametro
        catalogo = [{'diametro': '#3', 'longitud_m': 6, 'cantidad': None}]
        for options in (None, {}):
            problem = normalize([row('a', 1.4, 10)], catalogo, options=options)
            e, scale = problem['rules']['kerf'], problem['scale']
            L, l = 6 * scale, round(1.4 * scale)
            q = (L + e) // (l + e)
            self.assertEqual(cota_diametro(problem, '#3')['material'], -(-10 // q) * L)

    @unittest.skipUnless(HAY_SCIPY, 'scipy no instalado: cota no disponible')
    def test_cota_menor_o_igual_al_optimo(self):
        from cutting.bound import cota_diametro, cota_simple
        for problem in self.instancias():
            cota = cota_diametro(problem, '#3')
            self.assertLessEqual(cota['material'], optimo_fuerza_bruta(problem, '#3'))
            self.assertLessEqual(cota_simple(problem, '#3')['material'], cota['material'])

    @unittest.skipUnless(HAY_SCIPY, 'scipy no instalado: cota no disponible')
    def test_inventario_limitado_y_perdida_activa(self):
        from cutting.bound import cota_plan
        rows = [row('a', 3.5, 3), row('b', 1.0, 2, 2), row('c', 2.2, 4, 1, '#4', 0.994)]
        inventory = [{'diametro': '#3', 'longitud_m': 4, 'cantidad': 1}]
        problem, result = plan(rows, options={}, inventory=inventory)
        cota = cota_plan(problem, result['metrics'])
        self.assertEqual(cota['estado'], 'calculada')
        por_diametro = result['metrics']['por_diametro']
        for item in cota['por_diametro']:
            material_plan = por_diametro[item['diametro']]['longitud_inicial'] / problem['scale']
            self.assertLessEqual(item['material_m'], material_plan + 1e-9)
        self.assertLessEqual(cota['proyecto']['desperdicio_pct'], result['metrics']['desperdicio_porcentaje'] + 1e-9)

    @unittest.skipUnless(HAY_SCIPY, 'scipy no instalado: cota no disponible')
    def test_sin_converger_sigue_siendo_valida(self):
        from cutting.bound import cota_diametro
        problem = normalize([row('a', 3.5, 4), row('b', 2.4, 4)], [{'diametro': '#3', 'longitud_m': 6, 'cantidad': None}])
        cota = cota_diametro(problem, '#3', max_iter=1)
        self.assertFalse(cota['ajustada'])
        self.assertLessEqual(cota['material'], optimo_fuerza_bruta(problem, '#3'))


class MasaNominalTests(unittest.TestCase):
    """US5: aviso no bloqueante si la masa por metro difiere > 1 % de la NSR-10 (FR-018, FR-019)."""

    def avisos(self, rows):
        from cutting.nominal import avisos
        return avisos(normalize(rows))

    def test_masas_nominales_sin_avisos(self):
        rows = [row('a', 2, 3, diam='#3', mass_per_m=0.56), row('b', 2, 3, diam='#4', mass_per_m=0.994)]
        self.assertEqual(self.avisos(rows), [])

    def test_diferencia_mayor_al_uno_por_ciento(self):
        problem, result = plan([row('a', 2, 3, diam='#4', mass_per_m=1.01)])
        from cutting.nominal import avisos
        resultado = avisos(problem)
        self.assertEqual(len(resultado), 1)
        aviso = resultado[0]
        self.assertEqual((aviso['diametro'], aviso['estado']), ('#4', 'aviso'))
        self.assertAlmostEqual(aviso['masa_cartilla_kg_m'], 1.01)
        self.assertAlmostEqual(aviso['masa_nominal_kg_m'], 0.994)
        self.assertAlmostEqual(aviso['diferencia_relativa_pct'], 100 * (1.01 - 0.994) / 0.994)
        self.assertTrue(result['metrics']['valido'])  # no bloquea el plan

    def test_exactamente_uno_por_ciento_no_avisa(self):
        self.assertEqual(self.avisos([row('a', 2, 3, diam='#3', mass_per_m=0.5656)]), [])

    def test_diametro_sin_valor_nominal(self):
        catalog = [{'diametro': '#13', 'longitud_m': 6, 'cantidad': None}]
        from cutting.nominal import avisos
        resultado = avisos(normalize([row('a', 2, 3, diam='#13', mass_per_m=10)], catalog))
        self.assertEqual(resultado[0]['estado'], 'no_contrastado')
        self.assertIsNone(resultado[0]['masa_nominal_kg_m'])

    def test_analizar_incluye_avisos_y_aprovechamiento(self):
        from cutting.analysis import analizar
        problem, result = plan([row('a', 2, 3, diam='#4', mass_per_m=1.01)])
        analisis = analizar(problem, result)
        self.assertEqual([a['diametro'] for a in analisis['avisos_masa']], ['#4'])
        self.assertAlmostEqual(analisis['aprovechamiento_pct'] + result['metrics']['desperdicio_porcentaje'], 100)
