"""Pruebas de seguridad de scripts con un Docker simulado: nunca tocan la VPS."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[2]
SHA = 'a' * 40
OLD = 'b' * 40


class OperationsTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root/'shared').mkdir()
        (self.root/'shared/production.env').write_text('POSTGRES_PASSWORD=test\n')
        (self.root/'bin').mkdir()
        fake = self.root/'bin/docker'
        fake.write_text('''#!/usr/bin/env python3
import os,sys,json
with open(os.environ['DOCKER_LOG'],'a') as f: f.write(json.dumps(sys.argv[1:])+'\\n')
if os.environ.get('FAIL_NGINX')=='1' and 'up' in sys.argv and 'nginx' in sys.argv: sys.exit(14)
if os.environ.get('FAIL_PULL')=='1' and 'pull' in sys.argv: sys.exit(12)
if os.environ.get('FAIL_BACKUP')=='1' and any('pg_dump' in arg for arg in sys.argv): sys.exit(13)
''')
        fake.chmod(0o755)
        self.log = self.root/'docker.log'
        self.env = {**os.environ, 'PATH':str(self.root/'bin')+':'+os.environ['PATH'],
                    'OICA_ROOT':str(self.root), 'OICA_PROJECT':'oica-test-ops',
                    'OICA_TLS':'false', 'DOCKER_LOG':str(self.log)}
        self.release(SHA)

    def tearDown(self):
        self.temp.cleanup()

    def release(self, sha, schema='SELECT 1;'):
        path = self.root/'releases'/sha
        path.mkdir(parents=True)
        (path/'config/backend/migrations').mkdir(parents=True)
        (path/'config/backend/migrations/001.sql').write_text(schema)
        (path/'schema.sha256').write_text(hashlib.sha256(schema.encode()).hexdigest()+'  config/backend/migrations/001.sql\n')
        (path/'images.env').write_text('\n'.join(f'{key}_IMAGE=ghcr.io/example/oica-{key.lower()}@sha256:'+('1'*64) for key in ('BACKEND','WORKER','FRONTEND'))+'\n')
        return path

    def run_op(self, *args, extra=None):
        return subprocess.run(['bash',str(REPO/'scripts/deploy.sh'),*args],env={**self.env, **(extra or {})},capture_output=True,text=True,timeout=10)

    def calls(self):
        return [json.loads(line) for line in self.log.read_text().splitlines()] if self.log.exists() else []

    def test_reset_requires_exact_confirmation(self):
        result=self.run_op('reset',SHA,'incorrecta','false')
        self.assertNotEqual(result.returncode,0)
        self.assertFalse(any('down' in c for c in self.calls()))

    def test_reset_only_removes_dedicated_project(self):
        result=self.run_op('reset',SHA,'BORRAR OICA PRODUCTION','false')
        self.assertEqual(result.returncode,0,result.stderr+result.stdout)
        calls=self.calls()
        self.assertEqual(len([c for c in calls if 'down' in c and '--volumes' in c]),1)
        for call in calls:
            self.assertIn('oica-test-ops',call)
            self.assertNotIn('prune',call)
        self.assertEqual((self.root/'current').resolve(),self.root/'releases'/SHA)

    def test_failed_pull_does_not_interrupt_running_app(self):
        result=self.run_op('deploy',SHA,extra={'FAIL_PULL':'1'})
        self.assertNotEqual(result.returncode,0)
        self.assertFalse((self.root/'shared/maintenance/enabled').exists())
        self.assertFalse(any('stop' in c or 'down' in c for c in self.calls()))

    def test_failed_backup_prevents_reset(self):
        previous=self.release(OLD)
        (self.root/'current').symlink_to(previous)
        result=self.run_op('reset',SHA,'BORRAR OICA PRODUCTION','true',extra={'FAIL_BACKUP':'1'})
        self.assertNotEqual(result.returncode,0)
        self.assertFalse(any('down' in c for c in self.calls()))
        self.assertEqual((self.root/'current').resolve(),previous)

    def test_incompatible_rollback_never_stops_app(self):
        previous=self.release(OLD,'SELECT 2;')
        (self.root/'current').symlink_to(previous)
        result=self.run_op('rollback',SHA)
        self.assertNotEqual(result.returncode,0)
        self.assertFalse(any('stop' in c or 'down' in c for c in self.calls()))

    def test_failed_reset_health_keeps_maintenance(self):
        result = self.run_op('reset', SHA, 'BORRAR OICA PRODUCTION', 'false', extra={'FAIL_NGINX': '1'})
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue((self.root/'shared/maintenance/enabled').exists())
        self.assertFalse((self.root/'current').exists())

    def test_separate_build_of_same_commit_has_own_release(self):
        release_id = SHA + '-12345'
        path = self.release(release_id)
        result = self.run_op('deploy', release_id)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertEqual((self.root/'current').resolve(), path)

    def test_restore_requires_confirmation(self):
        result = subprocess.run(['bash', str(REPO/'scripts/restore.sh'), 'invalid', 'incorrecta'],
                                env=self.env, capture_output=True, text=True, timeout=10)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.calls(), [])

    def test_arbitrary_project_is_rejected(self):
        result=self.run_op('reset',SHA,'BORRAR OICA PRODUCTION','false',extra={'OICA_PROJECT':'another-app'})
        self.assertNotEqual(result.returncode,0)
        self.assertEqual(self.calls(),[])

    def test_changed_migration_is_rejected_before_pull(self):
        (self.root/'releases'/SHA/'config/backend/migrations/001.sql').write_text('DROP TABLE x;')
        result=self.run_op('deploy',SHA)
        self.assertNotEqual(result.returncode,0)
        self.assertFalse(any('pull' in c for c in self.calls()))


if __name__=='__main__':
    unittest.main()
