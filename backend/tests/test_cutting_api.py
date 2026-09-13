"""Integración HTTP/worker con SQLite en memoria y broker simulado.

El cálculo y los archivos son reales. No se conecta a Redis/PostgreSQL externos.
"""
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
        inventory = read_rows(io.BytesIO(response.data), 'inventario.xlsx')
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

    def test_artefactos_visuales_acotados(self):
        from cutting.domain import normalize
        from cutting.optimizer import optimize
        from cutting.report import generate
        from cutting.io import read_rows
        from PIL import Image
        p = normalize([{'N° Orden': 'pedido', 'N° de Barra': '#3', 'Cantidad': 2,
                        'Longitud total (m)': 2, 'Masa total (kg)': 4}])
        r = optimize(p)
        files = generate(p, r, Path(self.directory.name) / 'visuales', '<Proyecto>', True)
        self.assertEqual(Path(files['pdf_path']).read_bytes()[:4], b'%PDF')
        with Image.open(files['graph_image_path']) as image:
            self.assertLessEqual(image.width * image.height, 3_000_000)
        rows = read_rows(files['excel_path'])
        self.assertEqual(sum(int(row['piezas_por_barra']) for row in rows), 2)


if __name__ == '__main__':
    unittest.main()
