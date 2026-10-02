"""Artefactos de una ejecución validada; Excel completo y vistas acotadas."""
from decimal import Decimal
from html import escape
from pathlib import Path
import json

from .analysis import patrones_de
from .nominal import ROTULO
from .domain import validate
from .io import export_inventory
from .patterns import secuencia_legible


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


NO_DISPONIBLE = 'no disponible'
ESTADOS = {'dentro': 'Dentro de lo admisible', 'excede': 'Excede', 'sin_evaluar': 'Sin evaluar'}
COLUMNAS_ADMISIBILIDAD = ['ambito', 'diametro', 'desperdicio_pct', 'umbral_desperdicio_pct', 'estado',
                          'diferencia_pp', 'irrecuperable_kg', 'irrecuperable_pct', 'reutilizable_kg',
                          'reutilizable_pct']


def admisibilidad_rows(analisis):
    """Filas de la hoja Admisibilidad (contracts/artefactos.md): proyecto primero."""
    if not analisis.get('admisibilidad'):
        return [{'ambito': NO_DISPONIBLE}]
    umbral = analisis.get('umbral_desperdicio_pct')
    perdidas = analisis.get('perdidas', {})
    def fila(ambito, diametro, evaluacion, medidas):
        return {'ambito': ambito, 'diametro': diametro, 'desperdicio_pct': evaluacion['desperdicio_pct'],
                'umbral_desperdicio_pct': umbral, 'estado': ESTADOS[evaluacion['estado']],
                'diferencia_pp': evaluacion['diferencia_pp'],
                'irrecuperable_kg': medidas['irrecuperable']['kg'], 'irrecuperable_pct': medidas['irrecuperable']['pct'],
                'reutilizable_kg': medidas['reutilizable']['kg'], 'reutilizable_pct': medidas['reutilizable']['pct']}
    rows = [fila('proyecto', '', analisis['admisibilidad']['proyecto'], perdidas)]
    for evaluacion in analisis['admisibilidad']['por_diametro']:
        rows.append(fila('diametro', evaluacion['diametro'], evaluacion,
                         perdidas['por_diametro'][evaluacion['diametro']]))
    return rows


def resumen_analisis(analisis):
    """Escalares del análisis para la hoja Metricas."""
    if not analisis:
        return []
    proyecto = (analisis.get('admisibilidad') or {}).get('proyecto') or {}
    perdidas = analisis.get('perdidas') or {}
    cota = analisis.get('cota') or {}
    calculada = cota.get('estado') == 'calculada'
    values = {'analisis_version': analisis.get('version'),
              'umbral_desperdicio_pct': analisis.get('umbral_desperdicio_pct'),
              'admisibilidad_estado': ESTADOS.get(proyecto.get('estado'), NO_DISPONIBLE),
              'perdida_irrecuperable_pct': (perdidas.get('irrecuperable') or {}).get('pct'),
              'reutilizable_pct': (perdidas.get('reutilizable') or {}).get('pct'),
              'aprovechamiento_pct': analisis.get('aprovechamiento_pct'),
              'cota_desperdicio_pct': (cota.get('proyecto') or {}).get('desperdicio_pct'),
              'cota_ajustada': cota.get('ajustada') if calculada else None,
              'brecha_pp': (cota.get('proyecto') or {}).get('brecha_pp')}
    return [{'indicador': k, 'valor': NO_DISPONIBLE if v is None else v} for k, v in values.items()]


COLUMNAS_COTA = ['ambito', 'diametro', 'material_m', 'material_kg', 'desperdicio_cota_pct',
                  'simple_desperdicio_pct', 'barras_minimas', 'desperdicio_plan_pct', 'brecha_pp', 'ajustada',
                  'estado']


def cota_rows(analisis):
    """Filas de la hoja Cota (contracts/artefactos.md): proyecto primero."""
    cota = analisis.get('cota')
    if not cota:
        return [{'ambito': NO_DISPONIBLE}]
    estado = 'calculada' if cota['estado'] == 'calculada' else f"no disponible: {cota.get('motivo') or ''}"
    plan = {e['diametro']: e['desperdicio_pct'] for e in analisis['admisibilidad']['por_diametro']}
    rows = [{'ambito': 'proyecto', 'diametro': '', 'material_kg': cota['proyecto']['material_kg'],
             'desperdicio_cota_pct': cota['proyecto']['desperdicio_pct'],
             'simple_desperdicio_pct': cota['proyecto']['simple_desperdicio_pct'],
             'desperdicio_plan_pct': analisis['admisibilidad']['proyecto']['desperdicio_pct'],
             'brecha_pp': cota['proyecto'].get('brecha_pp'),
             'ajustada': cota['ajustada'] if cota['estado'] == 'calculada' else None, 'estado': estado}]
    for item in cota['por_diametro']:
        rows.append({'ambito': 'diametro', 'diametro': item['diametro'], 'material_m': item['material_m'],
                     'material_kg': item['material_kg'], 'desperdicio_cota_pct': item['desperdicio_pct'],
                     'simple_desperdicio_pct': item['simple']['desperdicio_pct'],
                     'barras_minimas': item['simple']['barras_minimas'],
                     'desperdicio_plan_pct': plan.get(item['diametro']), 'brecha_pp': item.get('brecha_pp'),
                     'ajustada': item['ajustada'] if cota['estado'] == 'calculada' else None, 'estado': estado})
    return rows


def cota_html(analisis):
    """Sección «Cota inferior por patrones y brecha» del PDF."""
    cota = analisis.get('cota')
    if not cota:
        return f'<h2>Cota inferior por patrones y brecha</h2><p>{NO_DISPONIBLE}.</p>'
    simple = cota['proyecto']['simple_desperdicio_pct']
    if cota['estado'] != 'calculada':
        return ('<h2>Cota inferior por patrones y brecha</h2>'
                f"<p>Cota por patrones: no disponible ({escape(cota.get('motivo') or '')}). "
                f'Cota simple (aprovechamiento perfecto): {simple:.3f}%.</p>')
    proyecto = cota['proyecto']
    ajuste = '' if cota['ajustada'] else ' Cota no ajustada: válida, pero puede ser más holgada.'
    return ('<h2>Cota inferior por patrones y brecha</h2>'
            f"<p>Ningún plan puede bajar de {proyecto['desperdicio_pct']:.3f}% de desperdicio "
            f"(Gilmore–Gomory, relajación lineal; etapas relajadas). Cota simple: {simple:.3f}%. "
            f"Brecha del plan: {proyecto['brecha_pp']:.3f} pp.{ajuste} La cota mide la calidad del plan; "
            'no lo construye ni prueba optimalidad.</p>')


COLUMNAS_AVISOS = ['diametro', 'masa_cartilla_kg_m', 'masa_nominal_kg_m', 'diferencia_relativa_pct', 'estado']


def avisos_rows(analisis):
    """Filas de la hoja Avisos; una fila «Sin avisos» si no hay discrepancias."""
    avisos = analisis.get('avisos_masa')
    if avisos is None:
        return [{'diametro': NO_DISPONIBLE}]
    estados = {'aviso': f'difiere más de 1 % de la {ROTULO}', 'no_contrastado': 'sin valor nominal: no contrastado'}
    return [{**a, 'estado': estados[a['estado']]} for a in avisos] or [{'diametro': 'Sin avisos'}]


def avisos_html(analisis):
    """Secciones «Aprovechamiento» y «Avisos de masa nominal NSR-10» del PDF."""
    partes = []
    if analisis.get('aprovechamiento_pct') is not None:
        partes.append(f"<h2>Aprovechamiento</h2><p>{analisis['aprovechamiento_pct']:.3f}% del material "
                      'queda en piezas (100 % menos el desperdicio en masa).</p>')
    avisos = analisis.get('avisos_masa')
    if avisos is None:
        return ''.join(partes)
    filas = ''.join(
        f"<tr><td>{escape(a['diametro'])}</td><td>{a['masa_cartilla_kg_m']:.4f}</td>"
        f"<td>{'—' if a['masa_nominal_kg_m'] is None else format(a['masa_nominal_kg_m'], '.3f')}</td>"
        f"<td>{'—' if a['diferencia_relativa_pct'] is None else format(a['diferencia_relativa_pct'], '+.2f') + '%'}</td></tr>"
        for a in avisos)
    cuerpo = (f'<table><tr><th>Diámetro</th><th>Cartilla (kg/m)</th><th>Nominal (kg/m)</th><th>Diferencia</th></tr>'
              f'{filas}</table><p>El aviso no bloquea el plan; revisar la masa por metro de la cartilla.</p>'
              if avisos else '<p>Sin avisos: la masa por metro de cada diámetro coincide con la nominal (±1 %).</p>')
    partes.append(f'<h2>Avisos de masa nominal NSR-10</h2><p>Referencia: {escape(ROTULO)}.</p>{cuerpo}')
    return ''.join(partes)


COLUMNAS_COMPRA = ['diametro', 'longitud_m', 'origen', 'barras', 'masa_kg', 'aprovechamiento_pct']
COLUMNAS_PATRONES = ['patron_id', 'diametro', 'origen', 'longitud_m', 'secuencia', 'repeticiones',
                     'aprovechamiento_pct', 'perdida_corte_m', 'descartado_m', 'saldo_m']
LIMITE_PDF_PATRONES = 150
LIMITE_PNG_PATRONES = 60


def patrones_rows(problem, patrones):
    """Filas de la hoja Patrones (contracts/artefactos.md)."""
    scale = problem['scale']
    return [{'patron_id': p['patron_id'], 'diametro': p['diametro'], 'origen': p['origen'],
             'longitud_m': float(Decimal(p['longitud']) / scale), 'secuencia': secuencia_legible(problem, p),
             'repeticiones': p['repeticiones'],
             'aprovechamiento_pct': float(100 * Decimal(p['piezas']) / p['longitud']),
             'perdida_corte_m': float(Decimal(p['kerf']) / scale),
             'descartado_m': float(Decimal(p['discarded']) / scale),
             'saldo_m': float(Decimal(p['remaining']) / scale)} for p in patrones]


def mas_repetidos(patrones, limite):
    """Los patrones más repetidos primero; el orden estable conserva el de la hoja."""
    return sorted(patrones, key=lambda p: -p['repeticiones'])[:limite]


def patrones_html(problem, result, patrones=None):
    """Tabla de patrones del PDF, acotada a los más repetidos (FR-009)."""
    if patrones is None:
        patrones = patrones_de(problem, result)[0]
    muestra = mas_repetidos(patrones, LIMITE_PDF_PATRONES)
    filas = ''.join(
        f"<tr><td>{escape(r['patron_id'])}</td><td>{escape(r['diametro'])}</td><td>{escape(r['origen'])}</td>"
        f"<td>{r['longitud_m']:g} m</td><td>{escape(r['secuencia'])}</td><td>{r['repeticiones']}</td>"
        f"<td>{r['aprovechamiento_pct']:.2f}%</td><td>{r['saldo_m']:g} m</td></tr>"
        for r in patrones_rows(problem, muestra))
    omitidos = len(patrones) - len(muestra)
    aviso = (f'Se omitieron {omitidos} patrones; el Excel contiene el total de {len(patrones)} patrones.'
             if omitidos else f'Se muestran los {len(patrones)} patrones del plan.')
    return (f'<h2>Patrones de corte</h2><p>{len(patrones)} patrones para {len(result["bars"])} barras. '
            f'{aviso} La vista barra por barra está en el Excel (hojas Barras y Cortes).</p>'
            '<table><tr><th>Patrón</th><th>Diámetro</th><th>Origen</th><th>Barra</th><th>Secuencia por etapa</th>'
            f'<th>Repeticiones</th><th>Aprovechamiento</th><th>Saldo</th></tr>{filas}</table>')
VERIFICADO = 'Plan verificado: demanda, diámetro, capacidad, etapas e inventario.'


def compra_html(analisis):
    """Sección «Resumen de compra» del PDF; las barras de inventario no son compra."""
    lineas = analisis.get('resumen_compra')
    if lineas is None:
        return f'<h2>Resumen de compra</h2><p>{NO_DISPONIBLE}.</p>'
    filas = ''.join(
        f"<tr><td>{escape(l['diametro'])}</td><td>{l['longitud_m']:g} m</td>"
        f"<td>{'Compra' if l['origen'] == 'comercial' else 'Inventario adicional'}</td>"
        f"<td>{l['barras']}</td><td>{l['masa_kg']:.3f} kg</td><td>{l['aprovechamiento_pct']:.2f}%</td></tr>"
        for l in lineas)
    return ('<h2>Resumen de compra</h2><table><tr><th>Diámetro</th><th>Longitud</th><th>Origen</th>'
            f'<th>Barras</th><th>Masa</th><th>Aprovechamiento</th></tr>{filas}</table>'
            '<p>Las barras de inventario adicional se toman del inventario y no se compran.</p>')


def admisibilidad_html(analisis):
    """Secciones «Desperdicio» y «Admisibilidad» del PDF."""
    if not analisis.get('admisibilidad'):
        return f'<h2>Admisibilidad</h2><p>{NO_DISPONIBLE}.</p>'
    perdidas = analisis['perdidas']
    proyecto = analisis['admisibilidad']['proyecto']
    umbral = analisis.get('umbral_desperdicio_pct')
    estado = ESTADOS[proyecto['estado']]
    if proyecto['diferencia_pp'] is not None:
        estado += f" ({proyecto['diferencia_pp']:+.3f} pp frente al umbral de {umbral:.2f}%)"
    filas = ''.join(
        f"<tr><td>{escape(e['diametro'])}</td><td>{e['desperdicio_pct']:.3f}%</td>"
        f"<td>{escape(ESTADOS[e['estado']])}</td>"
        f"<td>{'' if e['diferencia_pp'] is None else format(e['diferencia_pp'], '+.3f') + ' pp'}</td></tr>"
        for e in analisis['admisibilidad']['por_diametro'])
    return (f"<h2>Desperdicio</h2><p>Pérdida irrecuperable (corte y descartes): "
            f"{perdidas['irrecuperable']['kg']:.3f} kg ({perdidas['irrecuperable']['pct']:.3f}%). "
            f"Saldo reutilizable final: {perdidas['reutilizable']['kg']:.3f} kg "
            f"({perdidas['reutilizable']['pct']:.3f}%).</p>"
            f"<h2>Admisibilidad</h2><p>Proyecto: {escape(estado)}.</p>"
            f"<table><tr><th>Diámetro</th><th>Desperdicio</th><th>Estado</th><th>Diferencia</th></tr>{filas}</table>"
            f"<p>El umbral lo define el usuario; no se identificó un máximo normativo.</p>")


def generate(problem, result, directory, title='', visuals=True):
    import pandas as pd
    validate(problem, result['bars'], result['inventory'])
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    scale = problem['scale']
    def meters(value):
        return float(Decimal(value) / scale)
    patrones, patron_por_barra = patrones_de(problem, result)
    bars, cuts = [], []
    for b in result['bars']:
        bars.append({'barra_id': b['bar_id'], 'patron_id': patron_por_barra[b['bar_id']],
                     'diametro': b['diametro'], 'origen': b['origen'],
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
    analisis = result['metrics'].get('analisis') or {}
    summary = [{'indicador': k, 'valor': v} for k, v in result['metrics'].items()
               if isinstance(v, (str, int, float, bool))] + resumen_analisis(analisis)
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
        pd.DataFrame(admisibilidad_rows(analisis), columns=COLUMNAS_ADMISIBILIDAD).to_excel(
            writer, sheet_name='Admisibilidad', index=False)
        pd.DataFrame(patrones_rows(problem, patrones), columns=COLUMNAS_PATRONES).to_excel(
            writer, sheet_name='Patrones', index=False)
        pd.DataFrame(cota_rows(analisis), columns=COLUMNAS_COTA).to_excel(writer, sheet_name='Cota', index=False)
        pd.DataFrame(avisos_rows(analisis), columns=COLUMNAS_AVISOS).to_excel(writer, sheet_name='Avisos', index=False)
        compra = analisis.get('resumen_compra')
        pd.DataFrame(compra if compra is not None else [{'diametro': NO_DISPONIBLE}],
                     columns=COLUMNAS_COMPRA).to_excel(writer, sheet_name='Resumen de compra', index=False)
    export_inventory(result['inventory'], files['inventory_path'])
    if not visuals:
        return files
    from weasyprint import HTML
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    m = result['metrics']
    html = f'''<html lang="es"><meta charset="utf-8"><style>
    @page {{ size: A4 landscape; margin: 15mm; }} body {{ font-family: sans-serif; font-size: 10px; }}
    table {{ border-collapse: collapse; width: 100%; }} th,td {{ padding: 4px; border: 1px solid #ccc; }}
    </style><h1>Plan de corte secuencial — {escape(title)}</h1>
    <p><strong>{VERIFICADO}</strong></p>
    <p>Parámetros: {escape(json.dumps(problem.get('resolved_parameters', {}), ensure_ascii=False))}.
    Inventario final proyectado; verificar físicamente antes de usar.</p>
    <p>Motor {escape(m['motor'])}, método {escape(m['metodo'])}, semilla {m['seed']}.</p>
    <p>{m['piezas']} piezas; {m['barras']} barras raíz utilizadas una sola vez.</p>
    <p>Masa incorporada: {m['masa_inicial_kg']:.3f} kg.
    Sobrante final: {m['sobrante_final_kg']:.3f} kg.
    Piezas: {m['piezas_kg']:.3f} kg; pérdida por corte: {m['perdida_corte_kg']:.3f} kg;
    descartado: {m['descartado_kg']:.3f} kg.
    Desperdicio por masa: {m['desperdicio_porcentaje']:.4f}%.</p>
    {avisos_html(analisis)}
    {admisibilidad_html(analisis)}
    {cota_html(analisis)}
    {compra_html(analisis)}
    {patrones_html(problem, result, patrones)}</html>'''
    files['pdf_path'] = str(path / 'plan_corte.pdf')
    HTML(string=html).write_pdf(files['pdf_path'])
    # Nesting lineal por patrones (FR-009/FR-010): lienzo acotado a los patrones más repetidos.
    muestra = mas_repetidos(patrones, LIMITE_PNG_PATRONES)
    fig, ax = plt.subplots(figsize=(14, max(4, len(muestra) * .24)))
    try:
        palette = plt.get_cmap('tab20')
        for y, patron in enumerate(muestra):
            start = 0
            for grupo, longitud, cantidad in patron['secuencia']:
                # Una pieza por rectángulo, con borde fino: el taller distingue cada corte.
                pieza = meters(longitud)
                ax.broken_barh([(start + i * pieza, pieza) for i in range(cantidad)], (y - .4, .8),
                               facecolors=palette(grupo % 20), edgecolor='white', linewidth=.5)
                start += pieza * cantidad
            for key, color in [('kerf', 'black'), ('discarded', 'tomato')]:
                width = meters(patron[key])
                ax.barh(y, width, left=start, color=color)
                start += width
            ax.barh(y, meters(patron['remaining']), left=start, color='lightgray', hatch='//')
        ax.set_yticks(range(len(muestra)), [f"{p['patron_id']} ×{p['repeticiones']}" for p in muestra], fontsize=6)
        ax.invert_yaxis()
        ax.set_xlabel('Longitud (m); etapa por color, negro = corte, rojo = descarte, trama = reutilizable')
        ax.set_title(f"Nesting lineal por patrones de corte: {len(muestra)} de {len(patrones)} patrones "
                     f"({len(result['bars'])} barras)")
        omitidos = len(patrones) - len(muestra)
        if omitidos:
            fig.text(0.01, 0.005, f'{omitidos} patrones omitidos; ver Excel (hoja Patrones).', fontsize=7)
        fig.tight_layout(rect=(0, 0.02, 1, 1))
        files['graph_image_path'] = str(path / 'grafica_cortes.png')
        fig.savefig(files['graph_image_path'], dpi=100)
    finally:
        plt.close(fig)
    return files
