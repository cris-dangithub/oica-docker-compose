"""Migraciones SQL ordenadas, transaccionales y verificadas por checksum."""
import hashlib
import os
from pathlib import Path
import psycopg2


def migrate():
    directory = Path(os.environ.get('MIGRATIONS_DIR', Path(__file__).resolve().parents[1] / 'migrations'))
    if not directory.is_dir():
        directory = Path(__file__).resolve().parents[1] / 'config/backend/migrations'
    files = sorted(directory.glob('[0-9]*.sql'))
    if not files:
        raise RuntimeError('No se encontraron migraciones')
    with psycopg2.connect(os.environ['DATABASE_URL']) as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT pg_advisory_xact_lock(68421001)')
            cursor.execute('CREATE TABLE IF NOT EXISTS schema_migrations (name TEXT PRIMARY KEY, checksum TEXT NOT NULL, applied_at TIMESTAMPTZ NOT NULL DEFAULT now())')
            cursor.execute('SELECT name, checksum FROM schema_migrations')
            applied = dict(cursor.fetchall())
            if set(applied) - {p.name for p in files}:
                raise RuntimeError('La base tiene migraciones posteriores a esta entrega')
            for path in files:
                sql = path.read_bytes()
                checksum = hashlib.sha256(sql).hexdigest()
                if path.name in applied:
                    if checksum != applied[path.name]:
                        raise RuntimeError(f'Migración alterada: {path.name}')
                    continue
                cursor.execute(sql.decode())
                cursor.execute('INSERT INTO schema_migrations (name, checksum) VALUES (%s, %s)', (path.name, checksum))
                print(f'Aplicada: {path.name}', flush=True)


if __name__ == '__main__':
    migrate()
