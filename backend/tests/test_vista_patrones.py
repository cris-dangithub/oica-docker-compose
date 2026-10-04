"""Vista de patrones del explorador (spec 002, US2): reconstrucción de solo lectura desde `resultados`."""
import copy
import json
import unittest
from collections import Counter

from cutting.domain import normalize
from cutting.optimizer import optimize


def row(order, length, quantity=1, group=1, diam='#3', mass_per_m=None):
    return {'N° Orden': order, 'Longitud total (m)': length, 'Cantidad': quantity,
            'Grupo de Ejecución': group, 'N° de Barra': diam,
            'Masa total (kg)': length * quantity * (mass_per_m or 1)}


# Dos diámetros, dos etapas y pedidos numéricos repetidos en varias filas.
ROWS = [row('12', 2.5, 3, 1), row('2', 1.2, 4, 2), row('12', 0.8, 5, 2, '#4', 0.994),
        row('7', 3.7, 2, 1, '#4', 0.994), row('2', 1.9, 6, 1)]
# 340 patrones distintos (caso de test_artefactos_por_patrones_acotados).
ROWS_340 = [{'N° Orden': f'p{i}', 'N° de Barra': '#3', 'Cantidad': 1,
             'Longitud total (m)': round(1.3 + i * 0.003, 3), 'Masa total (kg)': round(1.3 + i * 0.003, 3)}
            for i in range(340)]


def guardado(rows, options=None, catalog=None, analizar=True):
    """Plan como lo persiste el worker: `legacy_patterns` en JSON, y métricas con o sin análisis."""
    from cutting.analysis import analizar as analizar_plan
    from cutting.report import legacy_patterns
    problem = normalize(rows, catalog, None, options)
    result = optimize(problem, seed=0)
    if analizar:
        result['metrics']['analisis'] = analizar_plan(problem, result)
    resultados = json.loads(json.dumps(legacy_patterns(problem, result)))
    metricas = json.loads(json.dumps(result['metrics']))
    return problem, result, resultados, metricas


class ReconstruccionTests(unittest.TestCase):
    """FR-025 y SC-010: la vista es idéntica a la hoja «Patrones» y a `agrupar` sobre el plan original."""

    CASOS = {'ideal': (ROWS, None, None), 'fisico': (ROWS, {}, None),
             'fin_etapa': (ROWS, {'descarte': 'fin_etapa'}, None),
             'patrones_340': (ROWS_340, None, [{'diametro': '#3', 'longitud_m': 2.5, 'cantidad': None}])}

    def test_igual_a_la_hoja_patrones(self):
        from cutting import patterns
        from cutting.report import patrones_rows
        from cutting.vista_patrones import barras_desde_resultados, vista
        for nombre, (rows, options, catalog) in self.CASOS.items():
            with self.subTest(nombre):
                problem, result, resultados, metricas = guardado(rows, options, catalog)
                originales, por_barra = patterns.agrupar(problem, result['bars'])
                v = vista(resultados, metricas)
                self.assertTrue(v['disponible'])
                columnas = list(patrones_rows(problem, originales)[0])
                self.assertEqual([{k: p[k] for k in columnas} for p in v['patrones']],
                                 patrones_rows(problem, originales))
                reconstruidas = barras_desde_resultados(resultados, metricas['escala_longitudes'])
                self.assertEqual(patterns.agrupar(problem, reconstruidas)[1], por_barra)
                if nombre == 'patrones_340':
                    self.assertEqual(v['totales']['patrones'], 340)

    def test_invariantes(self):
        from cutting.vista_patrones import vista
        for nombre, (rows, options, catalog) in self.CASOS.items():
            with self.subTest(nombre):
                problem, result, resultados, metricas = guardado(rows, options, catalog)
                v = vista(resultados, metricas)
                patrones = v['patrones']
                self.assertEqual(sum(p['repeticiones'] for p in patrones), v['totales']['barras'])
                self.assertEqual(v['totales']['barras'], len(resultados))
                self.assertEqual(v['totales']['patrones'], len(patrones))
                self.assertEqual(v['escala_m'], max(p['longitud_m'] for p in patrones))
                for p in patrones:
                    self.assertEqual(p['barras']['total'], p['repeticiones'])
                    self.assertEqual(sum(r['n'] for r in p['barras']['rangos']), p['repeticiones'])
                    self.assertEqual(len(p['piezas']), len(p['secuencia'].replace(' | ', ' + ').split(' + ')))
                    for pieza in p['piezas']:
                        self.assertEqual(sum(x['piezas'] for x in pieza['pedidos']),
                                         pieza['cantidad'] * p['repeticiones'])
                    self.assertEqual(p['etapas'], sorted({x['etapa'] for x in p['piezas']}))
                demanda = Counter()
                for o in problem['orders']:
                    demanda[o['pedido']] += o['cantidad']
                self.assertEqual({x['pedido']: x['piezas'] for x in v['pedidos']}, dict(demanda))
                aportes = Counter()
                for p in patrones:
                    for pieza in p['piezas']:
                        for x in pieza['pedidos']:
                            aportes[x['pedido']] += x['piezas']
                self.assertEqual(aportes, demanda)

    def test_indices_y_orden_de_pedidos(self):
        from cutting.vista_patrones import vista
        _, _, resultados, metricas = guardado(ROWS, {})
        v = vista(resultados, metricas)
        self.assertEqual([x['pedido'] for x in v['pedidos']], ['2', '7', '12'])
        self.assertEqual(v['diametros'], ['#3', '#4'])
        self.assertEqual(v['etapas'], [1, 2])
        self.assertEqual(v['origenes'], ['comercial'])
        _, _, resultados, metricas = guardado(ROWS_340[:5], None,
                                              [{'diametro': '#3', 'longitud_m': 2.5, 'cantidad': None}])
        self.assertEqual([x['pedido'] for x in vista(resultados, metricas)['pedidos']],
                         ['p0', 'p1', 'p2', 'p3', 'p4'])

    def test_rangos(self):
        from cutting.vista_patrones import rangos
        self.assertEqual(rangos(['#4:7', '#4:2', '#4:1', '#4:3']),
                         [{'desde': '#4:1', 'hasta': '#4:3', 'n': 3}, {'desde': '#4:7', 'hasta': '#4:7', 'n': 1}])
        self.assertEqual(rangos(['#3:10', '#3:9']), [{'desde': '#3:9', 'hasta': '#3:10', 'n': 2}])

    def test_no_altera_lo_recibido(self):
        from cutting.vista_patrones import vista
        _, _, resultados, metricas = guardado(ROWS, {})
        antes = copy.deepcopy((resultados, metricas))
        vista(resultados, metricas)
        self.assertEqual((resultados, metricas), antes)


class NoDisponibleTests(unittest.TestCase):
    """FR-030: versiones que no se pueden reconstruir."""

    def test_sin_datos_reconstruibles(self):
        from cutting.vista_patrones import vista
        _, _, resultados, metricas = guardado(ROWS, {})
        sin_traza = [{k: v for k, v in r.items() if k != 'trazabilidad_cortes'} for r in resultados]
        sin_escala = {k: v for k, v in metricas.items() if k != 'escala_longitudes'}
        for datos, medidas in [(sin_traza, metricas), (resultados, sin_escala), ([], metricas), (None, metricas)]:
            v = vista(datos, medidas)
            self.assertFalse(v['disponible'])
            self.assertIn('trazabilidad de cortes', v['motivo'])


class InconsistenciaTests(unittest.TestCase):
    """FR-025: datos incoherentes producen un error, nunca una vista parcial."""

    def test_top_del_analisis_distinto(self):
        from cutting.vista_patrones import vista
        _, _, resultados, metricas = guardado(ROWS, {})
        metricas['analisis']['patrones']['top'][0]['repeticiones'] += 1
        with self.assertRaisesRegex(ValueError, 'Patrones inconsistentes'):
            vista(resultados, metricas)

    def test_falta_una_barra(self):
        from cutting.vista_patrones import vista
        _, _, resultados, metricas = guardado(ROWS, {})
        with self.assertRaisesRegex(ValueError, 'Patrones inconsistentes'):
            vista(resultados[1:], metricas)

    def test_sin_analisis_no_compara_el_top(self):
        from cutting.vista_patrones import vista
        _, _, resultados, metricas = guardado(ROWS, {}, analizar=False)
        self.assertTrue(vista(resultados, metricas)['disponible'])


if __name__ == '__main__':
    unittest.main()
