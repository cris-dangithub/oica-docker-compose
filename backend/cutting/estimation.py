"""Estimación empírica conservadora; no deriva tiempo del porcentaje de avance."""
import hashlib
import os
from pathlib import Path
import platform


def environment_key():
    digest = hashlib.sha256()
    for path in sorted(Path(__file__).parent.glob('*.py')):
        digest.update(path.read_bytes())
    digest.update(f'{platform.python_version()}:{platform.machine()}:{os.cpu_count()}'.encode())
    # Distinguir límites de CPU y memoria de los contenedores.
    for name in ('cpu.max', 'memory.max'):
        path = Path('/sys/fs/cgroup') / name
        if path.exists():
            digest.update(path.read_bytes())
    return digest.hexdigest()


def estimate(samples, elapsed=0):
    values = sorted(float(s) for s in samples if s is not None and float(s) > 0)
    if len(values) < 5:
        return {'calibration': 'calibrando', 'estimated_total_seconds': None,
                'remaining_seconds': None, 'samples': len(values)}
    low, high = values[0] * .8, values[-1] * 1.2
    if elapsed > high:
        return {'calibration': 'fuera_del_rango_observado', 'estimated_total_seconds': [low, high],
                'remaining_seconds': None, 'samples': len(values)}
    return {'calibration': 'estimacion_empirica', 'estimated_total_seconds': [low, high],
            'remaining_seconds': [max(0, low - elapsed), high - elapsed], 'samples': len(values)}
