"""Presentación de resultados (spec 002): Excel, PDF y PNG legibles sin alterar el plan."""
import tempfile
import unittest
from pathlib import Path

from cutting.domain import normalize
from cutting.optimizer import optimize


def row(order, length, quantity=1, group=1, diam='#3', mass_per_m=None):
    return {'N° Orden': order, 'Longitud total (m)': length, 'Cantidad': quantity,
            'Grupo de Ejecución': group, 'N° de Barra': diam,
            'Masa total (kg)': length * quantity * (mass_per_m or 1)}


# Dos diámetros y dos etapas, con condiciones físicas por defecto (disco y mínimo automático).
ROWS = [row('a', 2.5, 3, 1), row('b', 1.2, 4, 2), row('c', 0.8, 5, 2, '#4', 0.994),
        row('d', 3.7, 2, 1, '#4', 0.994)]
INVENTARIO = [{'diametro': '#3', 'longitud_m': 4, 'cantidad': 1}]


def caso(directory, visuals=False, inventory=None, umbral=None, version=None, rows=ROWS):
    """normalize → optimize → analizar → generate, como el worker."""
    from cutting.analysis import analizar
    from cutting.report import generate
    problem = normalize(rows, None, inventory, {})
    result = optimize(problem, seed=0)
    result['metrics']['analisis'] = analizar(problem, result, umbral)
    files = generate(problem, result, Path(directory), 'Proyecto <prueba>', visuals, version=version)
    return problem, result, files


def hojas(files):
    import pandas as pd
    return pd.read_excel(files['excel_path'], sheet_name=None)


class AyudantesTests(unittest.TestCase):
    """T003: formato con coma decimal y cobertura de las vistas acotadas."""

    def test_numero_punto_decimal_sin_miles(self):
        from cutting.report import numero
        # Enmienda 3 (FR-032): punto decimal y sin separador de miles, como la plantilla de la tesis.
        self.assertEqual(numero(152039.574), '152039.57')
        self.assertEqual(numero(7.5958, 3), '7.596')
        self.assertEqual(numero(13955, 0), '13955')
        self.assertEqual(numero(-1.264, 3), '-1.264')
        self.assertEqual(numero(0), '0.00')
        self.assertEqual(numero(None), 'no disponible')

    def test_cobertura_total(self):
        from cutting.report import cobertura
        patrones = [{'repeticiones': 3}, {'repeticiones': 2}]
        c = cobertura(patrones, 2, 5)
        self.assertEqual((c['n'], c['m'], c['b'], c['t']), (2, 2, 5, 5))
        self.assertEqual(c['pct'], 100)
        self.assertEqual(c['texto'], 'Se muestran 2 de 2 patrones, que cubren 5 de 5 barras (100 %)')

    def test_cobertura_parcial(self):
        from cutting.report import cobertura
        c = cobertura([{'repeticiones': 2199}, {'repeticiones': 1775}], 136, 13955)
        self.assertLessEqual(c['b'], c['t'])
        self.assertEqual(c['b'], 3974)
        self.assertIn('2 de 136 patrones', c['texto'])
        self.assertIn('3974 de 13955 barras (28.5 %)', c['texto'])

    def test_cobertura_con_plan_real(self):
        from cutting.analysis import patrones_de
        from cutting.report import cobertura, mas_repetidos
        problem = normalize(ROWS, None, None, {})
        result = optimize(problem, seed=0)
        patrones = patrones_de(problem, result)[0]
        completa = cobertura(patrones, len(patrones), len(result['bars']))
        self.assertEqual(completa['b'], completa['t'])
        parcial = cobertura(mas_repetidos(patrones, 1), len(patrones), len(result['bars']))
        self.assertLessEqual(parcial['b'], parcial['t'])


ORDEN_HOJAS = ['Resumen', 'Resumen de compra', 'Patrones', 'Cortes', 'Barras', 'Descartados', 'Admisibilidad',
               'Cota', 'Avisos', 'Inventario', 'Inventario excluido', 'Parámetros', 'Trazabilidad']
# contracts/artefactos.md §1.1: (indicador, unidad), en orden.
INDICADORES = [
    ('Estado de verificación', ''), ('Piezas producidas', 'piezas'), ('Barras utilizadas', 'barras'),
    ('Barras compradas', 'barras'), ('Barras tomadas del inventario', 'barras'),
    ('Patrones de corte distintos', 'patrones'), ('Masa de barras utilizadas', 'kg'),
    ('Masa incorporada en piezas', 'kg'), ('Pérdida por corte', 'kg'),
    ('Descartado (retazos bajo el mínimo)', 'kg'), ('Pérdida irrecuperable', 'kg'), ('Pérdida irrecuperable', '%'),
    ('Saldo reutilizable final', 'kg'), ('Saldo reutilizable final', '%'), ('Desperdicio en masa', '%'),
    ('Aprovechamiento', '%'), ('Desperdicio admisible definido por el usuario', '%'),
    ('Estado de admisibilidad', ''), ('Diferencia frente al umbral', 'pp'),
    ('Cota inferior por patrones', '%'), ('Brecha del plan frente a la cota', 'pp')]


def resumen(files):
    """Bloque de indicadores (desde la fila 1) y bloque «Totales de compra» (por su título)."""
    import pandas as pd
    from openpyxl import load_workbook
    indicadores = pd.read_excel(files['excel_path'], sheet_name='Resumen', nrows=len(INDICADORES))
    hoja = load_workbook(files['excel_path'], read_only=True)['Resumen']
    titulo = next(i for i, (celda,) in enumerate(hoja.iter_rows(max_col=1, values_only=True), 1)
                  if celda == 'Totales de compra')
    totales = pd.read_excel(files['excel_path'], sheet_name='Resumen', skiprows=titulo)
    return indicadores, totales


class ExcelResumenTests(unittest.TestCase):
    """US1 (FR-001 a FR-004): «Resumen» primero, con indicadores legibles y totales de compra."""

    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        cls.problem, cls.result, cls.files = caso(Path(cls.directory.name) / 'base', umbral=50.0)
        cls.inv = caso(Path(cls.directory.name) / 'inventario', inventory=INVENTARIO,
                       rows=[row('a', 3.5, 3), row('b', 1.0, 2)])

    @classmethod
    def tearDownClass(cls):
        cls.directory.cleanup()

    def test_orden_de_hojas_sin_metricas(self):
        from openpyxl import load_workbook
        libro = load_workbook(self.files['excel_path'], read_only=True)
        self.assertEqual(libro.sheetnames, ORDEN_HOJAS)
        self.assertNotIn('Metricas', libro.sheetnames)

    def test_indicadores_legibles_en_orden(self):
        indicadores, _ = resumen(self.files)
        self.assertEqual(list(indicadores.columns), ['indicador', 'valor', 'unidad'])
        self.assertEqual(list(zip(indicadores['indicador'], indicadores['unidad'].fillna(''))), INDICADORES)
        self.assertFalse(indicadores['valor'].isna().any(), 'ningún indicador queda como celda vacía')
        valores = list(indicadores['valor'])
        m = self.result['metrics']
        self.assertEqual(valores[1], m['piezas'])
        self.assertEqual(valores[2], m['barras'])
        self.assertAlmostEqual(valores[14], m['desperdicio_porcentaje'])
        self.assertEqual(valores[17], 'Dentro de lo admisible')

    def test_totales_de_compra_coinciden_con_el_detalle(self):
        import pandas as pd
        for _, result, files in [(self.problem, self.result, self.files), self.inv]:
            _, totales = resumen(files)
            detalle = pd.read_excel(files['excel_path'], sheet_name='Resumen de compra')
            filas = {r['diametro']: r for r in totales.to_dict('records')}
            comprado = filas['Total comprado']
            inventario = filas.get('Total tomado del inventario', {'barras': 0, 'masa_kg': 0})
            self.assertEqual(comprado['barras'] + inventario['barras'], len(result['bars']))
            self.assertAlmostEqual(comprado['masa_kg'] + inventario['masa_kg'], detalle['masa_kg'].sum())
            self.assertEqual(comprado['barras'], detalle.loc[detalle['origen'] == 'comercial', 'barras'].sum())
        _, totales = resumen(self.inv[2])
        self.assertIn('Total tomado del inventario', set(totales['diametro']))
        self.assertIn('Inventario adicional', set(totales['origen']))
        _, totales = resumen(self.files)
        self.assertNotIn('Total tomado del inventario', set(totales['diametro']))

    def test_resumen_de_compra_sin_filas_de_total(self):
        import pandas as pd
        detalle = pd.read_excel(self.files['excel_path'], sheet_name='Resumen de compra')
        self.assertFalse(detalle['diametro'].astype(str).str.startswith('Total').any())
        self.assertEqual(int(detalle['barras'].sum()), len(self.result['bars']))


class PdfInicioTests(unittest.TestCase):
    """US1 (FR-009, FR-011): encabezado, verificación, indicadores y compra al principio del PDF."""

    @classmethod
    def setUpClass(cls):
        from cutting.analysis import analizar, patrones_de
        from cutting.report import pdf_html
        cls.problem = normalize(ROWS, None, None, {})
        cls.result = optimize(cls.problem, seed=0)
        cls.result['metrics']['analisis'] = analizar(cls.problem, cls.result, 50.0)
        patrones = patrones_de(cls.problem, cls.result)[0]
        cls.html = pdf_html(cls.problem, cls.result, cls.result['metrics']['analisis'], patrones,
                            'Proyecto <prueba> & co', 3, [])

    def test_encabezado(self):
        self.assertIn('Proyecto &lt;prueba&gt; &amp; co', self.html)
        self.assertNotIn('<prueba>', self.html)
        self.assertIn('Versión 3', self.html)
        self.assertIn('Perfil Rápido', self.html)
        self.assertIn('hora de Colombia', self.html)

    def test_sin_version(self):
        from cutting.analysis import patrones_de
        from cutting.report import pdf_html
        html = pdf_html(self.problem, self.result, self.result['metrics']['analisis'],
                        patrones_de(self.problem, self.result)[0], 'P', None, [])
        self.assertIn('Versión no asignada', html)

    def test_orden_de_las_primeras_secciones(self):
        posiciones = [self.html.index(texto) for texto in
                      ('Plan verificado', 'Indicadores clave', 'Resumen de compra', 'Total comprado')]
        self.assertEqual(posiciones, sorted(posiciones))
        self.assertLess(self.html.index('Total comprado'), self.html.index('Patrones de corte'))

    def test_formato_decimal(self):
        from cutting.report import numero
        m = self.result['metrics']
        self.assertIn(f"{numero(m['desperdicio_porcentaje'])} %", self.html)
        cota = self.result['metrics']['analisis']['cota']
        if cota['estado'] == 'calculada':
            self.assertIn(numero(cota['proyecto']['desperdicio_pct'], 3), self.html)
            # FR-032: las diferencias en pp llevan signo explícito, como en la pantalla.
            from cutting.report import con_signo
            self.assertIn(f"Brecha del plan: {con_signo(cota['proyecto']['brecha_pp'], 3)} pp", self.html)


ROWS_340 = [{'N° Orden': f'p{i}', 'N° de Barra': '#3', 'Cantidad': 1,
             'Longitud total (m)': round(1.3 + i * 0.003, 3), 'Masa total (kg)': round(1.3 + i * 0.003, 3)}
            for i in range(340)]
CATALOGO_340 = [{'diametro': '#3', 'longitud_m': 2.5, 'cantidad': None}]


class NestingTests(unittest.TestCase):
    """US3 (FR-012 a FR-014): medidas, leyenda, 200 dpi, tamaño acotado y páginas de 18 patrones."""

    @classmethod
    def setUpClass(cls):
        from cutting.analysis import patrones_de
        cls.directory = tempfile.TemporaryDirectory()
        cls.problem = normalize(ROWS_340, CATALOGO_340, None, None)
        cls.result = optimize(cls.problem, seed=0)
        cls.patrones = patrones_de(cls.problem, cls.result)[0]

    @classmethod
    def tearDownClass(cls):
        cls.directory.cleanup()

    def test_png_200_dpi_y_acotado(self):
        from PIL import Image
        from cutting.report import generate
        files = generate(self.problem, self.result, Path(self.directory.name) / 'png', 'P', True)
        with Image.open(files['graph_image_path']) as imagen:
            self.assertAlmostEqual(imagen.info['dpi'][0], 200, delta=1)
            self.assertLessEqual(imagen.width * imagen.height, 9_000_000)
            self.assertGreater(imagen.width * imagen.height, 3_000_000, 'más resolución que antes (R-04)')

    def test_bloques_del_pdf(self):
        import math
        from cutting.report import imagenes_nesting, mas_repetidos
        for total in (5, 18, 19, 340):
            with self.subTest(total):
                patrones = self.patrones[:total]
                muestra = mas_repetidos(patrones, 60)
                bloques = imagenes_nesting(self.problem, muestra, len(patrones), len(self.result['bars']))
                self.assertEqual(len(bloques), math.ceil(min(60, total) / 18))

    def test_leyenda_de_etapas_y_tramos(self):
        import matplotlib.pyplot as plt
        from cutting.analysis import patrones_de
        from cutting.report import dibujar_nesting
        problem = normalize(ROWS, None, None, {})
        result = optimize(problem, seed=0)
        patrones = patrones_de(problem, result)[0]
        fig, etiquetas = dibujar_nesting(problem, patrones, len(patrones), len(result['bars']))
        plt.close(fig)
        self.assertEqual(etiquetas, ['E1', 'E2', 'Pérdida por corte', 'Descarte', 'Saldo reutilizable'])

    def test_rotulo_solo_si_cabe(self):
        from cutting.report import cabe_rotulo
        pulgadas_por_metro = 9.5 / 12
        self.assertTrue(cabe_rotulo(0.37, '0.37', pulgadas_por_metro))
        self.assertTrue(cabe_rotulo(4.2, '4.2', pulgadas_por_metro))
        self.assertFalse(cabe_rotulo(0.1, '0.1', pulgadas_por_metro))
        self.assertFalse(cabe_rotulo(0.2, '0.215', pulgadas_por_metro))


class CoberturaPdfTests(unittest.TestCase):
    """US3 (FR-010, SC-003): la tabla y las imágenes declaran qué parte del plan muestran."""

    def html(self, rows, catalog=None, options=None, imagenes=()):
        from cutting.analysis import patrones_de
        from cutting.report import patrones_html
        problem = normalize(rows, catalog, None, options)
        result = optimize(problem, seed=0)
        patrones = patrones_de(problem, result)[0]
        imagenes = None if imagenes is None else list(imagenes)
        return problem, result, patrones, patrones_html(problem, result, patrones, imagenes)

    def test_todos_los_patrones_cuando_caben(self):
        from cutting.report import cobertura, mas_repetidos
        _, result, patrones, html = self.html(ROWS, options={})
        tabla = cobertura(mas_repetidos(patrones, 150), len(patrones), len(result['bars']))
        self.assertEqual(tabla['b'], tabla['t'])
        self.assertIn(f"Tabla: {tabla['texto']}", html)
        self.assertIn('(100 %)', html)
        self.assertNotIn('Se omitieron', html)

    def test_mas_de_150_patrones(self):
        from cutting.report import cobertura, mas_repetidos
        _, result, patrones, html = self.html(ROWS_340, CATALOGO_340, imagenes=['iVBORw0KGgo='])
        tabla = cobertura(mas_repetidos(patrones, 150), len(patrones), len(result['bars']))
        imagenes = cobertura(mas_repetidos(patrones, 60), len(patrones), len(result['bars']))
        self.assertEqual(tabla['b'], sum(p['repeticiones'] for p in mas_repetidos(patrones, 150)))
        self.assertIn(f"Tabla: {tabla['texto']}", html)
        self.assertIn(f"Imágenes: {imagenes['texto']}", html)
        self.assertIn('Se omitieron 190 patrones', html)
        self.assertEqual(html.count('<tr><td>P-#3-'), 150)
        self.assertIn('src="data:image/png;base64,iVBORw0KGgo="', html)

    def test_imagen_no_disponible(self):
        _, _, _, html = self.html(ROWS, options={}, imagenes=None)
        self.assertIn('Imagen de nesting no disponible', html)


class FormatoTests(unittest.TestCase):
    """Enmienda 2 (FR-032, FR-033; research R-20): un solo formato para lo que lee el usuario."""

    def test_modulo_comun(self):
        from cutting import formato, report
        self.assertEqual(formato.numero(152039.574), '152039.57')
        self.assertEqual(formato.numero(13955, 0), '13955')
        self.assertEqual(formato.con_signo(1.2644, 3), '+1.264')
        self.assertEqual(formato.con_signo(-1.14), '-1.14')
        self.assertEqual(formato.metros(4.2), '4.2 m')
        self.assertEqual(formato.metros(12), '12 m')
        self.assertIs(report.numero, formato.numero, 'report reutiliza el módulo común')

    def test_mensaje_de_dominio_con_punto_decimal(self):
        from unittest.mock import patch
        from cutting.analysis import analizar
        problem = normalize(ROWS, None, None, {})
        result = optimize(problem, seed=0)
        cota = {'estado': 'calculada', 'motivo': None, 'ajustada': True,
                'proyecto': {'material_kg': 1.0, 'desperdicio_pct': 99.123456, 'simple_desperdicio_pct': 0.5},
                'por_diametro': [{'diametro': d, 'material_m': 1.0, 'material_kg': 1.0, 'desperdicio_pct': None,
                                  'ajustada': True,
                                  'simple': {'material_m': 1.0, 'desperdicio_pct': 99.123456, 'barras_minimas': 1}}
                                 for d in ('#3', '#4')]}
        with patch('cutting.bound.cota_plan', return_value=cota):
            with self.assertRaises(ValueError) as error:
                analizar(problem, result)
        mensaje = str(error.exception)
        self.assertIn('Error de dominio', mensaje)
        self.assertIn('(99.123456 %)', mensaje)
        self.assertNotRegex(mensaje, r'\d,\d')

    def test_repeticiones_del_png_sin_separador_de_miles(self):
        import matplotlib.pyplot as plt
        from cutting.report import dibujar_nesting
        problem = normalize(ROWS, None, None, {})
        patron = {'patron_id': 'P-#3-001', 'diametro': '#3', 'origen': 'comercial', 'longitud': 12000,
                  'secuencia': [[1, 2500, 4]], 'kerf': 0, 'discarded': 0, 'remaining': 2000,
                  'discard_events': [], 'piezas': 10000, 'repeticiones': 2199}
        fig, _ = dibujar_nesting(problem, [patron], 1, 2199)
        etiquetas = [t.get_text() for t in fig.axes[0].get_yticklabels()]
        plt.close(fig)
        self.assertEqual(etiquetas, ['P-#3-001 ×2199'])


class TrazabilidadTests(unittest.TestCase):
    """US5 (FR-005 a FR-008, FR-022): datos técnicos al final, parámetros legibles y compatibilidad."""

    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        cls.problem, cls.result, cls.files = caso(Path(cls.directory.name) / 'traza', umbral=50.0)
        cls.sheets = hojas(cls.files)

    @classmethod
    def tearDownClass(cls):
        cls.directory.cleanup()

    def test_trazabilidad_completa(self):
        import json
        from cutting.report import EN_RESUMEN, resumen_analisis
        datos = dict(zip(self.sheets['Trazabilidad']['dato'], self.sheets['Trazabilidad']['valor']))
        for clave in ('valido', 'escala_longitudes', 'motor', 'input_hash', 'seed', 'perfil', 'metodo',
                      'duracion_segundos', 'analisis_version', 'cota_ajustada', 'parametros_resueltos'):
            self.assertIn(clave, datos)
        self.assertEqual(datos['analisis_version'], 'analisis-1')
        self.assertEqual(json.loads(datos['parametros_resueltos']), self.problem['resolved_parameters'])
        # Nada de lo que iba a «Metricas» se pierde: está en «Resumen» o en «Trazabilidad» (data-model §4).
        escalares = [k for k, v in self.result['metrics'].items() if isinstance(v, (str, int, float, bool))]
        for clave in escalares:
            self.assertTrue(clave in datos or clave in EN_RESUMEN, clave)
        analisis = [r['indicador'] for r in resumen_analisis(self.result['metrics']['analisis'])]
        for clave in analisis:
            self.assertTrue(clave in datos or clave in EN_RESUMEN, clave)

    def test_parametros_legibles(self):
        filas = self.sheets['Parámetros']
        self.assertEqual(list(filas.columns), ['condicion', 'valor', 'referencia'])
        valores = dict(zip(filas['condicion'], filas['valor']))
        self.assertEqual(valores['Pérdida por corte'], 'Disco, 1 mm')
        self.assertEqual(valores['Mínimo reutilizable'], 'Automático: menor longitud demandada por diámetro')
        self.assertEqual(valores['Mínimo reutilizable #3'], '1.2 m')
        self.assertEqual(valores['Mínimo reutilizable #4'], '0.8 m')
        self.assertEqual(valores['Momento del descarte'], 'Inmediato, tras cada corte')
        self.assertEqual(valores['Pérdida efectiva aplicada'], '1 mm')
        referencias = dict(zip(filas['condicion'], filas['referencia'].fillna('')))
        self.assertIn('hilti.com', referencias['Pérdida por corte'])
        self.assertIn('DOI 10.12720/joams.1.3.313-316', referencias['Mínimo reutilizable'])
        self.assertNotIn('Parametros', self.sheets)

    def test_parametros_desactivados(self):
        from cutting.report import parametros_rows
        problem = normalize(ROWS, None, None, {'perdida_activa': False, 'minimo_activo': False,
                                               'descarte': 'fin_etapa'})
        valores = {r['condicion']: r['valor'] for r in parametros_rows(problem)}
        self.assertEqual(valores['Pérdida por corte'], 'Desactivada')
        self.assertEqual(valores['Mínimo reutilizable'], 'Desactivado')
        self.assertEqual(valores['Momento del descarte'], 'Al cerrar cada etapa')
        problem = normalize(ROWS, None, None, {'proceso': 'cizalla', 'modo_minimo': 'manual', 'minimo_m': '0.5'})
        valores = {r['condicion']: r['valor'] for r in parametros_rows(problem)}
        self.assertEqual(valores['Pérdida por corte'], 'Cizalla, 0 mm')
        self.assertEqual(valores['Mínimo reutilizable'], 'Manual común: 0.5 m')

    def test_barras_sin_codigo_de_catalogo(self):
        self.assertEqual(list(self.sheets['Barras'].columns),
                         ['barra_id', 'patron_id', 'diametro', 'origen', 'longitud_m', 'piezas_por_barra',
                          'perdida_corte_m', 'descartado_m', 'sobrante_final_m'])

    def test_cota_barras_minimas_teoricas(self):
        columnas = list(self.sheets['Cota'].columns)
        self.assertIn('barras_minimas_teoricas_cota_simple', columnas)
        self.assertNotIn('barras_minimas', columnas)

    def test_inventario_final_sin_cambios(self):
        import pandas as pd
        inventario = pd.read_excel(self.files['inventory_path'], sheet_name=None)
        self.assertEqual(list(inventario), ['Inventario'])
        self.assertEqual(list(inventario['Inventario'].columns), ['diametro', 'longitud_m', 'cantidad'])

    def test_datos_tecnicos_al_final_del_pdf(self):
        from cutting.analysis import patrones_de
        from cutting.report import pdf_html
        html = pdf_html(self.problem, self.result, self.result['metrics']['analisis'],
                        patrones_de(self.problem, self.result)[0], 'P', 1, [])
        tecnicos = html[html.index('<h2>Datos técnicos</h2>'):]
        m = self.result['metrics']
        for texto in ('Disco, 1 mm', 'Automático: menor longitud demandada por diámetro', m['motor'],
                      m['metodo'], f"semilla {m['seed']}", m['input_hash'], 'analisis-1',
                      'Inventario final proyectado; verificar físicamente antes de usar'):
            self.assertIn(texto, tecnicos)
        self.assertNotIn('"referencias"', html, 'sin JSON crudo en el PDF')


if __name__ == '__main__':
    unittest.main()
