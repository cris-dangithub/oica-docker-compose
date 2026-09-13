"""Artefactos de una ejecución validada; Excel completo y vistas acotadas."""
from decimal import Decimal
from html import escape
from pathlib import Path
import json

from .domain import validate
from .io import export_inventory


def legacy_patterns(problem, result):
    """Compatibilidad de lectura con resultados anteriores; origen contado una vez."""
    records = []
    scale = problem['scale']
    for b in result['bars']:
        cuts, pieces = [], []
        for c in b['cuts']:
            length = float(Decimal(c['longitud']) / scale)
            cuts.extend([length] * c['cantidad'])
            pieces.extend({'id_pedido': c['pedido'], 'row_id': c['row_id'],
                           'grupo_ejecucion': c['grupo'], 'longitud': length}
                          for _ in range(c['cantidad']))
        records.append({'bar_id': b['bar_id'], 'stock_id': b['stock_id'], 'origen': b['origen'],
                        'diametro': b['diametro'], 'barra_origen_longitud': b['longitud'] / scale,
                        'cortes_realizados': cuts, 'piezas_obtenidas': pieces,
                        'desperdicio_resultante': b['remaining'] / scale,
                        'perdida_corte_m': b.get('kerf', 0) / scale,
                        'descartado_m': b.get('discarded', 0) / scale,
                        'trazabilidad_cortes': b['cuts'],
                        'descartes_fin_etapa': b.get('discard_events', []),
                        'masa_por_metro_kg': float(problem['densities'][b['diametro']])})
    return records


def generate(problem, result, directory, title='', visuals=True):
    import pandas as pd
    validate(problem, result['bars'], result['inventory'])
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    scale = problem['scale']
    def meters(value):
        return float(Decimal(value) / scale)
    bars, cuts = [], []
    for b in result['bars']:
        bars.append({'barra_id': b['bar_id'], 'diametro': b['diametro'], 'origen': b['origen'],
                     'stock_id': b['stock_id'], 'longitud_m': meters(b['longitud']),
                     'piezas_por_barra': sum(c['cantidad'] for c in b['cuts']),
                     'perdida_corte_m': meters(b.get('kerf', 0)),
                     'descartado_m': meters(b.get('discarded', 0)),
                     'sobrante_final_m': meters(b['remaining'])})
        balance = b['longitud']
        previous_group = None
        for operation, c in enumerate(b['cuts'], 1):
            if previous_group is not None and previous_group != c['grupo']:
                balance -= sum(e['longitud'] for e in b.get('discard_events', []) if e['grupo'] == previous_group)
            separations = c.get('separations', c['cantidad'] - int(balance == c['longitud'] * c['cantidad']))
            balance -= c['longitud'] * c['cantidad'] + c.get('kerf', 0) + c.get('discarded', 0)
            previous_group = c['grupo']
            cuts.append({'barra_id': b['bar_id'], 'diametro': b['diametro'],
                         'grupo_ejecucion': c['grupo'], 'lote_en_barra': operation,
                         'separaciones': separations, 'fila_origen': c['row_id'],
                         'pedido': c['pedido'], 'longitud_m': meters(c['longitud']),
                         'cantidad': c['cantidad'], 'perdida_corte_m': meters(c.get('kerf', 0)),
                         'descarte_inmediato_m': meters(c.get('discarded', 0)),
                         'saldo_despues_m': meters(balance)})
    # Evitar que identificadores del usuario se interpreten como fórmulas.
    for c in cuts:
        if str(c['pedido']).startswith(('=', '+', '-', '@')):
            c['pedido'] = "'" + str(c['pedido'])
    files = {'excel_path': str(path / 'resultados_optimizacion.xlsx'),
             'inventory_path': str(path / 'inventario_final.xlsx'),
             'pdf_path': None, 'graph_image_path': None}
    summary = [{'indicador': k, 'valor': v} for k, v in result['metrics'].items()
               if isinstance(v, (str, int, float, bool))]
    with pd.ExcelWriter(files['excel_path'], engine='openpyxl') as writer:
        pd.DataFrame(bars).to_excel(writer, sheet_name='Barras', index=False)
        pd.DataFrame(cuts).sort_values(['grupo_ejecucion', 'diametro', 'barra_id']).to_excel(
            writer, sheet_name='Cortes', index=False)
        pd.DataFrame(result['inventory'], columns=['diametro', 'longitud_m', 'cantidad']).to_excel(
            writer, sheet_name='Inventario', index=False)
        pd.DataFrame(summary).to_excel(writer, sheet_name='Metricas', index=False)
        discarded_rows = []
        for b in result['bars']:
            for operation, c in enumerate(b['cuts'], 1):
                if c.get('discarded', 0):
                    discarded_rows.append({'barra_id': b['bar_id'], 'diametro': b['diametro'],
                        'grupo': c['grupo'], 'lote_en_barra': operation, 'momento': 'inmediato',
                        'descartado_m': meters(c['discarded'])})
            for event in b.get('discard_events', []):
                discarded_rows.append({'barra_id': b['bar_id'], 'diametro': b['diametro'],
                    'grupo': event['grupo'], 'lote_en_barra': None, 'momento': 'fin_etapa',
                    'descartado_m': meters(event['longitud'])})
        pd.DataFrame(discarded_rows, columns=['barra_id', 'diametro', 'grupo', 'lote_en_barra',
                                            'momento', 'descartado_m']).to_excel(
                                                writer, sheet_name='Descartados', index=False)
        pd.DataFrame([{'stock_id': s['stock_id'], 'diametro': s['diametro'],
                       'longitud_m': meters(s['longitud']), 'cantidad': s['cantidad']}
                      for s in problem.get('excluded_inventory', [])],
                     columns=['stock_id', 'diametro', 'longitud_m', 'cantidad']).to_excel(
                         writer, sheet_name='Inventario excluido', index=False)
        pd.DataFrame([{'parametro': k, 'valor': json.dumps(v, ensure_ascii=False)}
                      for k, v in problem.get('resolved_parameters', {}).items()]).to_excel(
                         writer, sheet_name='Parametros', index=False)
    export_inventory(result['inventory'], files['inventory_path'])
    if not visuals:
        return files
    from weasyprint import HTML
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    m = result['metrics']
    sample = cuts[:150]
    table = pd.DataFrame(sample).to_html(index=False, escape=True)
    notice = f'Muestra de {len(sample)} registros de corte; el Excel contiene los {len(cuts)} registros completos.'
    html = f'''<html lang="es"><meta charset="utf-8"><style>
    @page {{ size: A4 landscape; margin: 15mm; }} body {{ font-family: sans-serif; font-size: 10px; }}
    table {{ border-collapse: collapse; width: 100%; }} th,td {{ padding: 4px; border: 1px solid #ccc; }}
    </style><h1>Plan de corte secuencial — {escape(title)}</h1>
    <p>Parámetros: {escape(json.dumps(problem.get('resolved_parameters', {}), ensure_ascii=False))}.
    Inventario final proyectado; verificar físicamente antes de usar.</p>
    <p>Motor {escape(m['motor'])}, método {escape(m['metodo'])}, semilla {m['seed']}.</p>
    <p>{m['piezas']} piezas; {m['barras']} barras raíz utilizadas una sola vez.</p>
    <p>Masa incorporada: {m['masa_inicial_kg']:.3f} kg.
    Sobrante final: {m['sobrante_final_kg']:.3f} kg.
    Piezas: {m['piezas_kg']:.3f} kg; pérdida por corte: {m['perdida_corte_kg']:.3f} kg;
    descartado: {m['descartado_kg']:.3f} kg.
    Desperdicio por masa: {m['desperdicio_porcentaje']:.4f}%.</p>
    <p>{notice}</p>{table}</html>'''
    files['pdf_path'] = str(path / 'plan_corte.pdf')
    HTML(string=html).write_pdf(files['pdf_path'])
    # Una imagen acotada: evita lienzos proporcionales a miles de barras.
    sample_bars = result['bars'][:60]
    fig, ax = plt.subplots(figsize=(14, max(4, len(sample_bars) * .24)))
    try:
        palette = plt.get_cmap('tab20')
        for y, b in enumerate(sample_bars):
            start = 0
            for c in b['cuts']:
                width = meters(c['longitud'] * c['cantidad'])
                ax.barh(y, width, left=start, color=palette(c['grupo'] % 20))
                start += width
            for key, color in [('kerf', 'black'), ('discarded', 'tomato')]:
                width = meters(b.get(key, 0))
                ax.barh(y, width, left=start, color=color)
                start += width
            ax.barh(y, meters(b['remaining']), left=start, color='lightgray', hatch='//')
        ax.set_yticks(range(len(sample_bars)), [b['bar_id'] for b in sample_bars], fontsize=6)
        ax.set_xlabel('Longitud (m); grupo por color, negro = corte, rojo = descarte, trama = reutilizable')
        ax.set_title(f"Muestra: {len(sample_bars)} de {len(result['bars'])} barras. Plan completo en Excel")
        fig.tight_layout()
        files['graph_image_path'] = str(path / 'grafica_cortes.png')
        fig.savefig(files['graph_image_path'], dpi=100)
    finally:
        plt.close(fig)
    return files
