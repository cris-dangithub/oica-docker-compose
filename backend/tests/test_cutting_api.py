"""Integración HTTP/worker con SQLite en memoria y broker simulado.

El cálculo y los archivos son reales. No se conecta a Redis/PostgreSQL externos.
"""
import copy
import importlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, MagicMock


class CuttingApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory(prefix='oica-api-test-')
        with patch.dict(os.environ, {'DATABASE_URL': 'sqlite://', 'UPLOAD_PATH': cls.directory.name}):
            cls.server = importlib.import_module('server')
        cls.app = cls.server.app
        if not str(cls.app.config['SQLALCHEMY_DATABASE_URI']).startswith('sqlite:'):
            raise RuntimeError('Estas pruebas requieren una base aislada en memoria')
        cls.app.config['TESTING'] = True
        cls.db = cls.server.db

    @classmethod
    def tearDownClass(cls):
        cls.directory.cleanup()

    def setUp(self):
        self.context = self.app.app_context()
        self.context.push()
        self.db.create_all()
        raw = self.db.engine.raw_connection()
        raw.create_function('pg_try_advisory_lock', 1, lambda value: True)
        raw.create_function('pg_advisory_unlock', 1, lambda value: True)
        raw.close()
        self.client = self.app.test_client()

    def tearDown(self):
        self.db.session.remove()
        self.db.drop_all()
        self.context.pop()

    @staticmethod
    def data():
        cartilla = ('N° Orden;N° de Barra;Longitud total (m);Cantidad;Grupo de Ejecución;Masa total (kg)\n'
                    'a;#3;6;1;1;6\nb;#3;2;1;2;2\nc;#3;0.9;1;3;0.9\n')
        return {'file': (io.BytesIO(cartilla.encode()), 'cartilla.csv'), 'perfil': 'rapido',
                'catalogo': '[{"diametro":"#3","longitud_m":9,"cantidad":1}]', 'visuales': 'false'}

    def upload(self, options=None):
        data = self.data()
        if options is not None:
            data['parametros_corte'] = json.dumps(options)
        with patch.object(self.server.process_file_task, 'apply_async', return_value=MagicMock(id='process_1')):
            response = self.client.post('/upload', data=data)
        self.assertEqual(response.status_code, 202, response.json)
        return response.json['file_id']

    def test_validacion_antes_de_encolar(self):
        for catalog in ('[{"diametro":"#3","longitud_m":0,"cantidad":1}]', '[null]', '{}', 'null'):
            with self.subTest(catalog=catalog):
                data = self.data(); data['catalogo'] = catalog
                with patch.object(self.server.process_file_task, 'apply_async') as enqueue:
                    response = self.client.post('/upload', data=data)
                self.assertEqual(response.status_code, 400)
                enqueue.assert_not_called()
                self.assertEqual(self.server.UploadedFile.query.count(), 0)

    def test_bloqueo_reproceso_y_borrado_activo(self):
        file_id = self.upload()
        self.assertEqual(self.client.post(f'/reprocess/{file_id}', json={}).status_code, 409)
        self.assertEqual(self.client.delete(f'/file/{file_id}').status_code, 409)

    def test_worker_y_roundtrip_inventario(self, physical=False):
        import celery_worker as worker
        from cutting.io import read_rows
        from cutting.domain import normalize
        from cutting.optimizer import optimize
        file_id = self.upload({} if physical else None)
        record = self.db.session.get(self.server.UploadedFile, file_id)
        with patch.dict(os.environ, {'UPLOAD_PATH': self.directory.name}), \
             patch.object(worker, 'create_flask_app', return_value=self.app), \
             patch.object(worker, 'redis_client'), patch.object(worker, 'publish_progress'), \
             patch.object(worker.process_file_task, 'update_state'):
            worker.process_file_task.push_request(id=f'process_{file_id}')
            try:
                outcome = worker.process_file_task.run(file_id, 'rapido')
            finally:
                worker.process_file_task.pop_request()
        self.assertEqual(outcome['status'], 'completed')
        # El worker usó otro contexto/sesión; renovar el mapa de identidad del test.
        self.db.session.expire_all()
        result = self.server.ProcessingResult.query.one()
        self.assertEqual(result.metricas['piezas'], 3)
        self.assertEqual(result.metricas['barras'], 1)
        response = self.client.get(f'/descargar-inventario/{result.storage_uuid}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('OICA_cartilla_v1_rapido_inventario.xlsx', response.headers['Content-Disposition'])
        inventory = read_rows(io.BytesIO(response.data), 'inventario.xlsx')
        excel = self.client.get(f'/descargar-excel/{result.storage_uuid}')
        self.assertIn('OICA_cartilla_v1_rapido_resultados.xlsx', excel.headers['Content-Disposition'])
        excel.close()
        if physical:
            self.assertEqual(inventory, [])
            self.assertAlmostEqual(result.metricas['perdida_corte_kg'], .003)
            self.assertAlmostEqual(result.metricas['descartado_kg'], .097)
            self.assertEqual(result.execution_config['parametros_resueltos']['minimos_por_diametro_m'], {'#3': '0.9'})
            import pandas as pd
            sheets = pd.read_excel(result.excel_path, sheet_name=None)
            self.assertAlmostEqual(sheets['Descartados']['descartado_m'].sum(), .097)
            self.assertAlmostEqual(sheets['Barras']['perdida_corte_m'].sum(), .003)
            # Auditar las trazas después del roundtrip JSON de la base de datos.
            from decimal import Decimal
            from cutting.domain import validate
            p = normalize(read_rows(record.file_path), record.execution_config['catalog'],
                          options=record.execution_config['parametros_corte'])
            def units(value):
                return int(Decimal(str(value)) * p['scale'])
            persisted = [{'bar_id': b['bar_id'], 'stock_id': b['stock_id'], 'diametro': b['diametro'],
                'longitud': units(b['barra_origen_longitud']), 'remaining': units(b['desperdicio_resultante']),
                'kerf': units(b['perdida_corte_m']), 'discarded': units(b['descartado_m']),
                'cuts': b['trazabilidad_cortes'], 'discard_events': b['descartes_fin_etapa']}
                for b in result.resultados]
            self.assertTrue(validate(p, persisted, inventory)['valido'])
        else:
            self.assertEqual(inventory[0]['longitud_m'], '0.1')
        new_rows = [{'N° Orden': 1, 'N° de Barra': '#3', 'Cantidad': 1,
                     'Longitud total (m)': '.1', 'Masa total (kg)': '.1'}]
        if not physical:
            reused = optimize(normalize(new_rows, [], inventory))
            self.assertEqual(reused['metrics']['desperdicio_porcentaje'], 0)
        self.assertEqual(record.execution_config['inventory'], [])
        self.assertTrue(Path(result.excel_path).is_file())
        self.assertIsNone(result.pdf_path)
        with patch.object(worker.process_file_task, 'apply_async', return_value=MagicMock(id='reprocess_1_x')):
            response = self.client.post(f'/reprocess/{file_id}', json={'perfil': 'profundo'})
        self.assertEqual(response.status_code, 202)
        self.assertEqual(record.active_profile, 'profundo')
        self.assertEqual(record.execution_config['parametros_corte']['perdida_activa'], physical)
        if physical:
            original_snapshot = dict(result.execution_config)
            with patch.dict(os.environ, {'UPLOAD_PATH': self.directory.name}), \
                 patch.object(worker, 'create_flask_app', return_value=self.app), \
                 patch.object(worker, 'redis_client'), patch.object(worker, 'publish_progress'), \
                 patch.object(worker.process_file_task, 'update_state'):
                worker.process_file_task.push_request(id='reprocess_1_x')
                try:
                    second = worker.process_file_task.run(file_id, 'profundo')
                finally:
                    worker.process_file_task.pop_request()
            self.assertEqual(second['status'], 'completed')
            self.db.session.expire_all()
            versions = self.server.ProcessingResult.query.order_by(self.server.ProcessingResult.version_number).all()
            self.assertEqual(len(versions), 2)
            self.assertEqual(versions[1].execution_config, original_snapshot)

    def test_nombres_de_descarga(self):
        """Spec 002, FR-036: OICA_<proyecto>_v<versión>_<perfil>_<tipo>.<ext>, sin el UUID interno."""
        from types import SimpleNamespace
        def version(file_name, numero=2, perfil='balanceado'):
            return SimpleNamespace(uploaded_file=SimpleNamespace(file_name=file_name),
                                   version_number=numero, perfil_usado=perfil)
        nombre = self.server.nombre_descarga
        v2 = version('002-ingeBigTest.xlsx')
        self.assertEqual(nombre(v2, 'excel'), 'OICA_002-ingeBigTest_v2_balanceado_resultados.xlsx')
        self.assertEqual(nombre(v2, 'pdf'), 'OICA_002-ingeBigTest_v2_balanceado_plan_corte.pdf')
        self.assertEqual(nombre(v2, 'imagen'), 'OICA_002-ingeBigTest_v2_balanceado_nesting.png')
        self.assertEqual(nombre(v2, 'inventario'), 'OICA_002-ingeBigTest_v2_balanceado_inventario.xlsx')
        # Nombre largo: el proyecto se recorta a 40 caracteres.
        self.assertEqual(nombre(version('a' * 60 + '.xlsx', 1, 'rapido'), 'excel'),
                         f"OICA_{'a' * 40}_v1_rapido_resultados.xlsx")
        # Versión histórica sin perfil registrado.
        self.assertEqual(nombre(version('cartilla.csv', 1, None), 'pdf'), 'OICA_cartilla_v1_plan_corte.pdf')
        # Espacios, tildes y símbolos quedan en ASCII seguro; sin nada utilizable, «proyecto».
        self.assertEqual(nombre(version('Cartilla N°2 diseño.xlsx', 3, 'profundo'), 'imagen'),
                         'OICA_Cartilla_N2_diseno_v3_profundo_nesting.png')
        for vacio in ('', '°°°.xlsx', None):
            with self.subTest(file_name=vacio):
                self.assertEqual(nombre(version(vacio, 1, 'rapido'), 'inventario'),
                                 'OICA_proyecto_v1_rapido_inventario.xlsx')

    def test_worker_con_condiciones_fisicas(self):
        self.test_worker_y_roundtrip_inventario(physical=True)

    def test_parametros_http_y_estimacion(self):
        defaults = self.client.get('/parametros-corte').json['defaults']
        self.assertTrue(defaults['perdida_activa'] and defaults['minimo_activo'])
        data = self.data(); data['parametros_corte'] = json.dumps(defaults)
        with patch.object(self.server.redis_client, 'get', return_value='entorno'):
            response = self.client.post('/estimate', data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['parametros_corte']['minimos_por_diametro_m'], {'#3': '0.9'})
        for value in ['[]', '{"perdida_mm":"NaN"}', '{"minimo_m":0}']:
            data = self.data(); data['parametros_corte'] = value
            with patch.object(self.server.process_file_task, 'apply_async') as enqueue:
                response = self.client.post('/upload', data=data)
            self.assertEqual(response.status_code, 400)
            enqueue.assert_not_called()

    def test_estimacion_sin_evidencia(self):
        with patch.object(self.server.redis_client, 'get', return_value='entorno'):
            response = self.client.post('/estimate', data=self.data())
        self.assertEqual(response.status_code, 200, response.json)
        self.assertIsNone(response.json['remaining_seconds'])
        self.assertEqual(response.json['calibration'], 'calibrando')

    def run_worker(self, file_id, task_id, perfil='rapido'):
        import celery_worker as worker
        with patch.dict(os.environ, {'UPLOAD_PATH': self.directory.name}), \
             patch.object(worker, 'create_flask_app', return_value=self.app), \
             patch.object(worker, 'redis_client'), patch.object(worker, 'publish_progress'), \
             patch.object(worker.process_file_task, 'update_state'):
            worker.process_file_task.push_request(id=task_id)
            try:
                return worker.process_file_task.run(file_id, perfil)
            finally:
                worker.process_file_task.pop_request()

    def test_umbral_invalido_no_encola(self):
        for value in ('0', '100', '-1', 'abc', 'NaN', 'inf'):
            with self.subTest(umbral=value):
                data = self.data(); data['umbral_desperdicio_pct'] = value
                with patch.object(self.server.process_file_task, 'apply_async') as enqueue:
                    response = self.client.post('/upload', data=data)
                self.assertEqual(response.status_code, 400)
                self.assertIn('Umbral de desperdicio admisible inválido', response.json['error'])
                enqueue.assert_not_called()
                self.assertEqual(self.server.UploadedFile.query.count(), 0)

    def test_umbral_se_guarda_fuera_del_problema(self):
        for value, expected in (('7,5', 7.5), ('7.5', 7.5), ('', None), (None, None)):
            with self.subTest(umbral=value):
                data = self.data()
                if value is not None:
                    data['umbral_desperdicio_pct'] = value
                with patch.object(self.server.process_file_task, 'apply_async', return_value=MagicMock(id='p')):
                    response = self.client.post('/upload', data=data)
                self.assertEqual(response.status_code, 202, response.json)
                record = self.db.session.get(self.server.UploadedFile, response.json['file_id'])
                self.assertEqual(record.execution_config['umbral_desperdicio_pct'], expected)
                self.assertNotIn('umbral_desperdicio_pct', record.execution_config['parametros_corte'])

    def test_estimacion_ignora_umbral(self):
        with patch.object(self.server.redis_client, 'get', return_value='entorno'):
            base = self.client.post('/estimate', data=self.data())
            data = self.data(); data['umbral_desperdicio_pct'] = '5'
            with_umbral = self.client.post('/estimate', data=data)
        self.assertEqual(base.status_code, 200)
        self.assertEqual(base.json, with_umbral.json)

    def test_umbral_al_reprocesar(self):
        data = self.data(); data['umbral_desperdicio_pct'] = '5'
        with patch.object(self.server.process_file_task, 'apply_async', return_value=MagicMock(id='p')):
            file_id = self.client.post('/upload', data=data).json['file_id']
        record = self.db.session.get(self.server.UploadedFile, file_id)
        record.processing_status = 'completed'
        self.db.session.commit()
        cases = [({'perfil': 'rapido'}, 202, 5.0), ({'umbral_desperdicio_pct': 12}, 202, 12.0),
                 ({'umbral_desperdicio_pct': 150}, 400, 12.0), ({'umbral_desperdicio_pct': None}, 202, None)]
        for body, status, expected in cases:
            with self.subTest(body=body):
                with patch.object(self.server.process_file_task, 'apply_async', return_value=MagicMock(id='r')) as enqueue:
                    response = self.client.post(f'/reprocess/{file_id}', json=body)
                self.assertEqual(response.status_code, status, response.json)
                self.assertEqual(enqueue.called, status == 202)
                self.db.session.expire_all()
                record = self.db.session.get(self.server.UploadedFile, file_id)
                self.assertEqual(record.execution_config['umbral_desperdicio_pct'], expected)
                record.processing_status = 'completed'
                self.db.session.commit()

    def test_worker_guarda_admisibilidad_y_umbral_por_version(self):
        data = self.data(); data['umbral_desperdicio_pct'] = '50'
        with patch.object(self.server.process_file_task, 'apply_async', return_value=MagicMock(id='p')):
            file_id = self.client.post('/upload', data=data).json['file_id']
        self.assertEqual(self.run_worker(file_id, f'process_{file_id}')['status'], 'completed')
        with patch.object(self.server.process_file_task, 'apply_async', return_value=MagicMock(id='r')):
            self.assertEqual(self.client.post(f'/reprocess/{file_id}', json={'umbral_desperdicio_pct': None}).status_code, 202)
        self.assertEqual(self.run_worker(file_id, 'r')['status'], 'completed')
        self.db.session.expire_all()
        first, second = self.server.ProcessingResult.query.order_by(self.server.ProcessingResult.version_number).all()
        self.assertEqual(first.execution_config['umbral_desperdicio_pct'], 50.0)
        self.assertEqual(second.execution_config['umbral_desperdicio_pct'], None)
        # El umbral no cambia el plan ni la huella del problema.
        self.assertEqual(first.resultados, second.resultados)
        self.assertEqual(first.execution_config['input_hash'], second.execution_config['input_hash'])
        self.assertEqual(first.metricas['analisis']['admisibilidad']['proyecto']['estado'], 'dentro')
        self.assertEqual(second.metricas['analisis']['admisibilidad']['proyecto']['estado'], 'sin_evaluar')
        detail = self.client.get(f'/file/{file_id}').json
        self.assertIsNone(detail['umbral_desperdicio_pct'])
        latest = detail['processing_results'][0]
        self.assertEqual(latest['admisibilidad_estado'], 'sin_evaluar')
        self.assertTrue(latest['valido'])
        self.assertEqual(latest['analisis']['version'], 'analisis-1')
        listed = self.client.get('/files').json['files'][0]['processing_results']
        self.assertNotIn('analisis', listed[0])
        self.assertEqual([r['admisibilidad_estado'] for r in listed], ['sin_evaluar', 'dentro'])
        import pandas as pd
        sheets = pd.read_excel(first.excel_path, sheet_name=None)
        admisibilidad = sheets['Admisibilidad'].to_dict('records')
        self.assertEqual(admisibilidad[0]['ambito'], 'proyecto')
        self.assertEqual(admisibilidad[0]['estado'], 'Dentro de lo admisible')
        self.assertEqual(admisibilidad[0]['umbral_desperdicio_pct'], 50)
        self.assertEqual([r['diametro'] for r in admisibilidad[1:]], ['#3'])
        cota = sheets['Cota'].to_dict('records')
        self.assertEqual(cota[0]['ambito'], 'proyecto')
        self.assertEqual([r['diametro'] for r in cota[1:]], ['#3'])
        self.assertLessEqual(cota[0]['simple_desperdicio_pct'], cota[0]['desperdicio_plan_pct'] + 1e-9)
        # La cartilla de prueba usa 1 kg/m para #3 (nominal 0,560): aviso no bloqueante.
        avisos = sheets['Avisos'].to_dict('records')
        self.assertEqual(avisos[0]['diametro'], '#3')
        self.assertIn('NSR-10', avisos[0]['estado'])
        compra = sheets['Resumen de compra']
        self.assertEqual(int(compra['barras'].sum()), first.metricas['barras'])
        self.assertEqual(list(compra.columns), ['diametro', 'longitud_m', 'origen', 'barras', 'masa_kg',
                                                'aprovechamiento_pct'])
        # Spec 002: «Metricas» se reparte entre «Resumen» (legible) y «Trazabilidad» (técnico).
        resumen = sheets['Resumen']
        indicadores = dict(zip(resumen['indicador'], resumen['valor']))
        self.assertEqual(indicadores['Estado de admisibilidad'], 'Dentro de lo admisible')
        trazabilidad = dict(zip(sheets['Trazabilidad']['dato'], sheets['Trazabilidad']['valor']))
        self.assertEqual(trazabilidad['analisis_version'], 'analisis-1')

    def test_pdf_con_admisibilidad(self):
        from cutting.analysis import analizar
        from cutting.domain import normalize
        from cutting.optimizer import optimize
        from cutting.report import generate, admisibilidad_html
        p = normalize([{'N° Orden': 'p', 'N° de Barra': '#3', 'Cantidad': 2,
                        'Longitud total (m)': 2.5, 'Masa total (kg)': 5}], options={})
        r = optimize(p)
        r['metrics']['analisis'] = analizar(p, r, 1.0)
        html = admisibilidad_html(r['metrics']['analisis'])
        self.assertIn('Excede', html)
        from cutting.report import compra_html, cota_html
        self.assertIn('Resumen de compra', compra_html(r['metrics']['analisis']))
        self.assertIn('Cota inferior', cota_html(r['metrics']['analisis']))
        self.assertIn('no se identificó un máximo normativo', html)
        files = generate(p, r, Path(self.directory.name) / 'admisible', 'Proyecto', True)
        self.assertEqual(Path(files['pdf_path']).read_bytes()[:4], b'%PDF')

    def test_artefactos_visuales_acotados(self):
        from cutting.domain import normalize
        from cutting.optimizer import optimize
        from cutting.report import generate
        from PIL import Image
        p = normalize([{'N° Orden': 'pedido', 'N° de Barra': '#3', 'Cantidad': 2,
                        'Longitud total (m)': 2, 'Masa total (kg)': 4}])
        r = optimize(p)
        files = generate(p, r, Path(self.directory.name) / 'visuales', '<Proyecto>', True)
        self.assertEqual(Path(files['pdf_path']).read_bytes()[:4], b'%PDF')
        with Image.open(files['graph_image_path']) as image:
            # Límite fijo e independiente del número de barras (BUG-005); 9 MP por los 200 dpi (R-04).
            self.assertLessEqual(image.width * image.height, 9_000_000)
        import pandas as pd
        sheets = pd.read_excel(files['excel_path'], sheet_name=None)
        # Spec 002: la primera hoja es «Resumen»; las piezas se cuentan en «Barras».
        self.assertEqual(int(sheets['Barras']['piezas_por_barra'].sum()), 2)
        patrones = sheets['Patrones']
        self.assertEqual(int(patrones['repeticiones'].sum()), len(sheets['Barras']))
        self.assertTrue(set(sheets['Barras']['patron_id']) <= set(patrones['patron_id']))
        self.assertEqual(list(patrones.columns), ['patron_id', 'diametro', 'origen', 'longitud_m', 'secuencia',
                                                  'repeticiones', 'aprovechamiento_pct', 'perdida_corte_m',
                                                  'descartado_m', 'saldo_m'])

    def test_artefactos_por_patrones_acotados(self):
        # Más de 150 patrones distintos: PDF y PNG muestran los más repetidos y avisan.
        from cutting.domain import normalize
        from cutting.optimizer import optimize
        from cutting.report import generate, patrones_html
        from PIL import Image
        # 340 piezas de 1,3 a 2,317 m en barras de 2,5 m: una pieza por barra, 340 patrones.
        rows = [{'N° Orden': f'p{i}', 'N° de Barra': '#3', 'Cantidad': 1,
                 'Longitud total (m)': round(1.3 + i * 0.003, 3), 'Masa total (kg)': round(1.3 + i * 0.003, 3)}
                for i in range(340)]
        catalog = [{'diametro': '#3', 'longitud_m': 2.5, 'cantidad': None}]
        p = normalize(rows, catalog)
        r = optimize(p)
        files = generate(p, r, Path(self.directory.name) / 'patrones', 'Proyecto', True)
        html = patrones_html(p, r)
        self.assertIn('Se omitieron', html)
        self.assertEqual(Path(files['pdf_path']).read_bytes()[:4], b'%PDF')
        with Image.open(files['graph_image_path']) as image:
            # Límite fijo e independiente del número de barras (BUG-005); 9 MP por los 200 dpi (R-04).
            self.assertLessEqual(image.width * image.height, 9_000_000)

    def version_guardada(self, status='completed', valido=True, sin_traza=False, alterar_top=False):
        """ProcessingResult como lo guarda el worker (spec 002, ruta de patrones)."""
        import uuid
        from cutting.analysis import analizar
        from cutting.domain import normalize
        from cutting.optimizer import optimize
        from cutting.report import legacy_patterns
        p = normalize([{'N° Orden': '12', 'N° de Barra': '#3', 'Cantidad': 3, 'Longitud total (m)': 2.5,
                        'Masa total (kg)': 7.5},
                       {'N° Orden': '7', 'N° de Barra': '#3', 'Cantidad': 4, 'Longitud total (m)': 1.2,
                        'Grupo de Ejecución': 2, 'Masa total (kg)': 4.8}], options={})
        r = optimize(p)
        r['metrics']['analisis'] = analizar(p, r)
        metricas = json.loads(json.dumps(r['metrics']))
        metricas['valido'] = valido
        if alterar_top:
            metricas['analisis']['patrones']['top'][0]['repeticiones'] += 1
        resultados = json.loads(json.dumps(legacy_patterns(p, r)))
        if sin_traza:
            for registro in resultados:
                registro.pop('trazabilidad_cortes')
        archivo = self.server.UploadedFile(file_path='x.xlsx', file_name='x.xlsx', file_extension='xlsx')
        self.db.session.add(archivo)
        self.db.session.flush()
        version = self.server.ProcessingResult(uploaded_file_id=archivo.id, version_number=1,
                                               storage_uuid=str(uuid.uuid4()), resultados=resultados,
                                               metricas=metricas, cartilla=[], result_status=status)
        self.db.session.add(version)
        self.db.session.commit()
        return version, r

    def test_patrones_de_una_version(self):
        version, r = self.version_guardada()
        antes = (version.updated_at, copy.deepcopy(version.resultados))
        response = self.client.get(f'/patrones/{version.storage_uuid}')
        self.assertEqual(response.status_code, 200, response.json)
        data = response.json
        self.assertTrue(data['disponible'])
        self.assertEqual((data['storage_uuid'], data['version_number'], data['motor']),
                         (version.storage_uuid, 1, r['metrics']['motor']))
        self.assertEqual(data['totales']['barras'], len(r['bars']))
        self.assertEqual(sum(p['repeticiones'] for p in data['patrones']), len(r['bars']))
        self.assertEqual({x['pedido']: x['piezas'] for x in data['pedidos']}, {'7': 4, '12': 3})
        for clave in ('escala_m', 'diametros', 'etapas', 'origenes'):
            self.assertIn(clave, data)
        # Solo lectura (FR-024): la fila no cambia, y una segunda llamada da lo mismo.
        self.db.session.refresh(version)
        self.assertEqual((version.updated_at, version.resultados), antes)
        self.assertEqual(self.client.get(f'/patrones/{version.storage_uuid}').json, data)

    def test_patrones_no_disponibles(self):
        for opciones, motivo in [({'status': 'processing'}, 'plan terminado'),
                                 ({'status': 'error_validation'}, 'plan terminado'),
                                 ({'valido': False}, 'verificación'),
                                 ({'valido': None}, 'verificación'),
                                 ({'sin_traza': True}, 'trazabilidad de cortes')]:
            with self.subTest(opciones):
                version, _ = self.version_guardada(**opciones)
                response = self.client.get(f'/patrones/{version.storage_uuid}')
                self.assertEqual(response.status_code, 200)
                self.assertFalse(response.json['disponible'])
                self.assertIn(motivo, response.json['motivo'])
                self.assertNotIn('patrones', response.json)

    def test_patrones_con_error_en_artefactos(self):
        # El plan quedó guardado aunque fallaran los artefactos: el explorador no depende de ellos.
        version, _ = self.version_guardada(status='error_generation')
        self.assertTrue(self.client.get(f'/patrones/{version.storage_uuid}').json['disponible'])

    def test_patrones_version_inexistente(self):
        response = self.client.get('/patrones/00000000-0000-4000-8000-000000000000')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, {'error': 'Versión no encontrada'})

    def test_patrones_inconsistentes(self):
        version, _ = self.version_guardada(alterar_top=True)
        response = self.client.get(f'/patrones/{version.storage_uuid}')
        self.assertEqual(response.status_code, 500)
        self.assertIn('Patrones inconsistentes', response.json['error'])
        self.assertNotIn('patrones', response.json)


if __name__ == '__main__':
    unittest.main()
