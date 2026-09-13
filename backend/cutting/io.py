"""Adaptadores de archivos; el núcleo no depende de pandas ni del servidor."""
from pathlib import Path
import csv
import hashlib


def read_rows(source, filename=None):
    import pandas as pd
    name = filename or str(source)
    if name.lower().endswith('.xlsx'):
        frame = pd.read_excel(source, dtype=object)
    elif name.lower().endswith('.csv'):
        # El detector permite archivos españoles separados por punto y coma.
        frame = pd.read_csv(source, sep=None, engine='python', encoding='utf-8-sig', dtype=object)
    else:
        raise ValueError('Se requiere XLSX o CSV')
    frame.columns = [str(c).strip() for c in frame.columns]
    return frame.where(pd.notna(frame), None).to_dict('records')


def file_hash(path):
    h = hashlib.sha256()
    with open(path, 'rb') as stream:
        for chunk in iter(lambda: stream.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def export_inventory(rows, path):
    import pandas as pd
    frame = pd.DataFrame(rows, columns=['diametro', 'longitud_m', 'cantidad'])
    if str(path).lower().endswith('.csv'):
        frame.to_csv(path, index=False, encoding='utf-8-sig')
    else:
        frame.to_excel(path, index=False, sheet_name='Inventario')
