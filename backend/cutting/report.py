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
from .formato import NO_DISPONIBLE, con_signo, metros, numero


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


ESTADOS = {'dentro': 'Dentro de lo admisible', 'excede': 'Excede', 'sin_evaluar': 'Sin evaluar'}
PERFILES = {'rapido': 'Rápido', 'balanceado': 'Balanceado', 'profundo': 'Profundo'}


def cobertura(mostrados, total_patrones, total_barras):
    """Patrones y barras que representa una vista acotada (R-13; data-model §6).

    Las barras salen de los mismos patrones mostrados, así que no pueden desalinearse.
    """
    n, b = len(mostrados), sum(p['repeticiones'] for p in mostrados)
    pct = 100 * b / total_barras if total_barras else 0.0
    porcentaje = numero(pct, 1).removesuffix(',0')
    return {'n': n, 'm': total_patrones, 'b': b, 't': total_barras, 'pct': pct,
            'texto': f'Se muestran {numero(n, 0)} de {numero(total_patrones, 0)} patrones, que cubren '
                     f'{numero(b, 0)} de {numero(total_barras, 0)} barras ({porcentaje} %)'}


VERIFICADO = 'Plan verificado: demanda, diámetro, capacidad, etapas e inventario.'
ORIGENES = {'comercial': 'Compra', 'adicional': 'Inventario adicional'}
COLUMNAS_RESUMEN = ['indicador', 'valor', 'unidad']
COLUMNAS_TOTALES = ['diametro', 'origen', 'barras', 'masa_kg']


def _barras_por_origen(analisis, origen):
    lineas = analisis.get('resumen_compra')
    return None if lineas is None else sum(l['barras'] for l in lineas if l['origen'] == origen)


def resumen_rows(problem, result, analisis):
    """Hoja «Resumen», bloque 1 (contracts/artefactos.md §1.1): nombre legible, valor y unidad.

    Un dato faltante se rotula; nunca queda una celda vacía ambigua (data-model §2).
    """
    m = result['metrics']
    perdidas = analisis.get('perdidas') or {}
    irrecuperable = perdidas.get('irrecuperable') or {}
    reutilizable = perdidas.get('reutilizable') or {}
    proyecto = (analisis.get('admisibilidad') or {}).get('proyecto') or {}
    umbral = analisis.get('umbral_desperdicio_pct')
    cota = analisis.get('cota') or {}
    calculada = cota.get('estado') == 'calculada'
    cota_proyecto = cota.get('proyecto') or {}
    verificado = (analisis.get('verificacion') or {}).get('valido', m.get('valido'))
    filas = [
        ('Estado de verificación', VERIFICADO if verificado else 'Plan no verificado', ''),
        ('Piezas producidas', m.get('piezas'), 'piezas'),
        ('Barras utilizadas', m.get('barras'), 'barras'),
        ('Barras compradas', _barras_por_origen(analisis, 'comercial'), 'barras'),
        ('Barras tomadas del inventario', _barras_por_origen(analisis, 'adicional'), 'barras'),
        ('Patrones de corte distintos', (analisis.get('patrones') or {}).get('total'), 'patrones'),
        ('Masa de barras utilizadas', m.get('masa_inicial_kg'), 'kg'),
        ('Masa incorporada en piezas', m.get('piezas_kg'), 'kg'),
        ('Pérdida por corte', m.get('perdida_corte_kg'), 'kg'),
        ('Descartado (retazos bajo el mínimo)', m.get('descartado_kg'), 'kg'),
        ('Pérdida irrecuperable', irrecuperable.get('kg'), 'kg'),
        ('Pérdida irrecuperable', irrecuperable.get('pct'), '%'),
        ('Saldo reutilizable final', reutilizable.get('kg'), 'kg'),
        ('Saldo reutilizable final', reutilizable.get('pct'), '%'),
        ('Desperdicio en masa', m.get('desperdicio_porcentaje'), '%'),
        ('Aprovechamiento', analisis.get('aprovechamiento_pct'), '%'),
        ('Desperdicio admisible definido por el usuario', 'sin umbral' if umbral is None else umbral, '%'),
        ('Estado de admisibilidad', ESTADOS.get(proyecto.get('estado'), NO_DISPONIBLE), ''),
        ('Diferencia frente al umbral', proyecto.get('diferencia_pp'), 'pp'),
        ('Cota inferior por patrones', cota_proyecto.get('desperdicio_pct') if calculada
         else f"{NO_DISPONIBLE}: {cota.get('motivo') or 'sin cota calculada'}", '%'),
        ('Brecha del plan frente a la cota', cota_proyecto.get('brecha_pp') if calculada else None, 'pp')]
    return [{'indicador': i, 'valor': NO_DISPONIBLE if v is None else v, 'unidad': u} for i, v, u in filas]


def totales_compra_rows(analisis):
    """Hoja «Resumen», bloque 2 (data-model §3): por diámetro y origen, y totales; coincide con el detalle."""
    lineas = analisis.get('resumen_compra')
    if lineas is None:
        return [{'diametro': NO_DISPONIBLE}]
    grupos = {}
    for l in lineas:
        grupo = grupos.setdefault((l['diametro'], l['origen']), {'barras': 0, 'masa_kg': 0.0})
        grupo['barras'] += l['barras']
        grupo['masa_kg'] += l['masa_kg']
    claves = sorted(grupos, key=lambda k: (int(k[0].lstrip('#')), k[1] != 'comercial'))
    # Redondeo a 6 decimales: sin ruido de coma flotante en el Excel, muy por debajo del gramo.
    rows = [{'diametro': d, 'origen': ORIGENES[o], 'barras': grupos[(d, o)]['barras'],
             'masa_kg': round(grupos[(d, o)]['masa_kg'], 6)} for d, o in claves]
    for origen, rotulo in [('comercial', 'Total comprado'), ('adicional', 'Total tomado del inventario')]:
        parte = [grupos[k] for k in claves if k[1] == origen]
        if origen == 'comercial' or parte:
            rows.append({'diametro': rotulo, 'origen': ORIGENES[origen], 'barras': sum(g['barras'] for g in parte),
                         'masa_kg': round(sum(g['masa_kg'] for g in parte), 6)})
    return rows
# Escalares de las métricas que la hoja «Resumen» ya muestra con nombre legible (data-model §4).
EN_RESUMEN = {'piezas', 'barras', 'masa_inicial_kg', 'piezas_kg', 'perdida_corte_kg', 'descartado_kg',
              'perdida_irrecuperable_kg', 'sobrante_final_kg', 'desperdicio_porcentaje',
              'umbral_desperdicio_pct', 'admisibilidad_estado', 'perdida_irrecuperable_pct', 'reutilizable_pct',
              'aprovechamiento_pct', 'cota_desperdicio_pct', 'brecha_pp'}
ORDEN_TRAZABILIDAD = ['valido', 'escala_longitudes', 'motor', 'input_hash', 'seed', 'perfil', 'metodo',
                      'duracion_segundos', 'analisis_version', 'analisis_segundos', 'cota_ajustada']


def trazabilidad_rows(problem, result, analisis):
    """Hoja «Trazabilidad» (FR-005): lo necesario para reproducir la versión, sin perder nada de «Metricas»."""
    datos = {k: v for k, v in result['metrics'].items()
             if isinstance(v, (str, int, float, bool)) and k not in EN_RESUMEN}
    datos.update({r['indicador']: r['valor'] for r in resumen_analisis(analisis) if r['indicador'] not in EN_RESUMEN})
    orden = [k for k in ORDEN_TRAZABILIDAD if k in datos] + [k for k in datos if k not in ORDEN_TRAZABILIDAD]
    rows = [{'dato': k, 'valor': datos[k]} for k in orden]
    # Los parámetros resueltos exactos, para reproducir el plan ahora que «Parámetros» es legible (R-07).
    rows.append({'dato': 'parametros_resueltos',
                 'valor': json.dumps(problem.get('resolved_parameters', {}), ensure_ascii=False, sort_keys=True)})
    return rows


def _cifra(texto):
    """'1.000' → '1'; '0.37' → '0,37' (parámetros guardados como texto decimal)."""
    return format(Decimal(texto).normalize(), 'f').replace('.', ',')


def _referencia(ficha):
    if not ficha:
        return ''
    return ' · '.join(p for p in (ficha.get('nota'), ficha.get('doi') and f"DOI {ficha['doi']}", ficha.get('url')) if p)


COLUMNAS_PARAMETROS = ['condicion', 'valor', 'referencia']


def parametros_rows(problem):
    """Hoja «Parámetros» y datos técnicos del PDF (R-08): condiciones de corte en lenguaje normal."""
    p = problem.get('resolved_parameters')
    if not p:
        return [{'condicion': NO_DISPONIBLE, 'valor': '', 'referencia': ''}]
    referencias = p.get('referencias', {})
    rows = [{'condicion': 'Pérdida por corte',
             'valor': f"{p['proceso'].capitalize()}, {_cifra(p['perdida_mm'])} mm" if p['perdida_activa'] else 'Desactivada',
             'referencia': _referencia(referencias.get(p['proceso'])) if p['perdida_activa'] else ''}]
    if not p['minimo_activo']:
        minimo, ficha = 'Desactivado', None
    elif p['modo_minimo'] == 'automatico':
        minimo, ficha = 'Automático: menor longitud demandada por diámetro', referencias.get('automatico')
    else:
        minimo, ficha = f"Manual común: {_cifra(p['minimo_m'])} m", None
    rows.append({'condicion': 'Mínimo reutilizable', 'valor': minimo, 'referencia': _referencia(ficha)})
    for diametro, valor in sorted(p.get('minimos_por_diametro_m', {}).items(), key=lambda kv: int(kv[0].lstrip('#'))):
        rows.append({'condicion': f'Mínimo reutilizable {diametro}', 'valor': f'{_cifra(valor)} m', 'referencia': ''})
    rows.append({'condicion': 'Momento del descarte',
                 'valor': 'Inmediato, tras cada corte' if p['descarte'] == 'inmediato' else 'Al cerrar cada etapa',
                 'referencia': ''})
    rows.append({'condicion': 'Pérdida efectiva aplicada', 'valor': f"{_cifra(p['perdida_efectiva_mm'])} mm",
                 'referencia': ''})
    return rows


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
                  'simple_desperdicio_pct', 'barras_minimas_teoricas_cota_simple', 'desperdicio_plan_pct',
                  'brecha_pp', 'ajustada',
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
                     'barras_minimas_teoricas_cota_simple': item['simple']['barras_minimas'],
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
                f'Con aprovechamiento perfecto, el desperdicio sería {numero(simple, 3)} %.</p>')
    proyecto = cota['proyecto']
    ajuste = '' if cota['ajustada'] else ' Cota no ajustada: válida, pero puede ser más holgada.'
    return ('<h2>Cota inferior por patrones y brecha</h2>'
            f"<p>Ningún plan puede bajar de {numero(proyecto['desperdicio_pct'], 3)} % de desperdicio "
            '(Gilmore–Gomory, relajación lineal; etapas relajadas). '
            f"Brecha del plan: {con_signo(proyecto['brecha_pp'], 3)} pp.{ajuste} Con aprovechamiento perfecto, "
            f'el desperdicio sería {numero(simple, 3)} %. La cota mide la calidad del plan; '
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
    """Sección «Avisos de masa nominal NSR-10» del PDF; el aprovechamiento va en «Indicadores clave»."""
    avisos = analisis.get('avisos_masa')
    if avisos is None:
        return ''
    partes = []
    # La masa nominal NSR-10 se publica con tres decimales; se conservan para poder contrastarla.
    filas = ''.join(
        f"<tr><td>{escape(a['diametro'])}</td><td>{numero(a['masa_cartilla_kg_m'], 3)}</td>"
        f"<td>{'—' if a['masa_nominal_kg_m'] is None else numero(a['masa_nominal_kg_m'], 3)}</td>"
        f"<td>{'—' if a['diferencia_relativa_pct'] is None else con_signo(a['diferencia_relativa_pct']) + ' %'}</td></tr>"
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


def patrones_html(problem, result, patrones=None, imagenes=()):
    """Sección «Patrones de corte» del PDF: cobertura, nesting por páginas y tabla acotada (FR-009, FR-010).

    `imagenes`: bloques PNG en base64 de `imagenes_nesting`; `None` si el dibujo falló y una lista
    vacía si la versión no lleva imágenes.
    """
    if patrones is None:
        patrones = patrones_de(problem, result)[0]
    total_barras = len(result['bars'])
    muestra = mas_repetidos(patrones, LIMITE_PDF_PATRONES)
    tabla = cobertura(muestra, len(patrones), total_barras)
    filas = ''.join(
        f"<tr><td>{escape(r['patron_id'])}</td><td>{escape(r['diametro'])}</td>"
        f"<td>{escape(ORIGENES.get(r['origen'], r['origen']))}</td>"
        f"<td>{metros(r['longitud_m'])}</td><td>{escape(r['secuencia'])}</td><td>{numero(r['repeticiones'], 0)}</td>"
        f"<td>{numero(r['aprovechamiento_pct'])} %</td><td>{metros(r['saldo_m'])}</td></tr>"
        for r in patrones_rows(problem, muestra))
    omitidos = len(patrones) - len(muestra)
    aviso = (f'Se omitieron {numero(omitidos, 0)} patrones; el Excel contiene el total de '
             f'{numero(len(patrones), 0)} patrones.' if omitidos
             else f'Se muestran los {numero(len(patrones), 0)} patrones del plan.')
    if imagenes is None:
        nesting = '<p>Imagen de nesting no disponible para esta versión; la tabla sigue completa.</p>'
    elif imagenes:
        figuras = cobertura(mas_repetidos(patrones, LIMITE_PNG_PATRONES), len(patrones), total_barras)
        nesting = (f"<p>Imágenes: {figuras['texto']}.</p>"
                   + ''.join(f'<img class="nesting" alt="Nesting lineal, página {i} de {len(imagenes)}" '
                             f'src="data:image/png;base64,{imagen}">' for i, imagen in enumerate(imagenes, 1)))
    else:
        nesting = ''
    return (f'<h2>Patrones de corte</h2><p>{numero(len(patrones), 0)} patrones para '
            f'{numero(total_barras, 0)} barras. Cada patrón es una forma de cortar que se repite.</p>'
            f"<p>Tabla: {tabla['texto']}. {aviso} La vista barra por barra está en el Excel "
            '(hojas Barras y Cortes).</p>'
            f'{nesting}'
            '<table class="patrones"><tr><th>Patrón</th><th>Diámetro</th><th>Origen</th><th>Barra</th>'
            '<th>Secuencia por etapa</th><th>Repeticiones</th><th>Aprovechamiento</th><th>Saldo</th></tr>'
            f'{filas}</table>')


NESTING_DPI = 200
NESTING_ANCHO_IN = 11.0
NESTING_ALTO_PATRON_IN = 0.3
# Márgenes fijos del lienzo: etiquetas de patrón a la izquierda; título arriba; leyenda y cobertura abajo.
NESTING_IZQUIERDA_IN, NESTING_DERECHA_IN = 1.3, 0.2
NESTING_ARRIBA_IN, NESTING_ABAJO_IN = 0.45, 1.0
PATRONES_POR_PAGINA = 18
ROTULO_PT = 5


def cabe_rotulo(ancho_m, texto, pulgadas_por_metro):
    """La medida se escribe sobre la pieza solo si cabe a 5 pt (research R-02)."""
    return ancho_m * pulgadas_por_metro >= 0.55 * ROTULO_PT / 72 * len(texto) + 0.03


def dibujar_nesting(problem, muestra, total_patrones, total_barras, titulo='Nesting lineal por patrones de corte'):
    """Figura de nesting acotada: 11 pulgadas de ancho y 0,3 por patrón (R-02 a R-04).

    Devuelve la figura y las etiquetas de su leyenda; quien llama la guarda y la cierra.
    """
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch
    scale = problem['scale']
    def meters(value):
        return float(Decimal(value) / scale)
    alto = NESTING_ALTO_PATRON_IN * len(muestra) + NESTING_ARRIBA_IN + NESTING_ABAJO_IN
    fig = plt.figure(figsize=(NESTING_ANCHO_IN, alto))
    ancho_eje = NESTING_ANCHO_IN - NESTING_IZQUIERDA_IN - NESTING_DERECHA_IN
    ax = fig.add_axes([NESTING_IZQUIERDA_IN / NESTING_ANCHO_IN, NESTING_ABAJO_IN / alto,
                       ancho_eje / NESTING_ANCHO_IN, NESTING_ALTO_PATRON_IN * len(muestra) / alto])
    palette = plt.get_cmap('tab20')
    # tab20 alterna tono oscuro y claro del mismo color: primero los oscuros, luego los claros, para
    # que etapas consecutivas no compartan color. Sin el par rojo (6 y 7), reservado al descarte.
    orden = [i for i in range(0, 20, 2) if i != 6] + [i for i in range(1, 20, 2) if i != 7]
    def color(grupo):
        return palette(orden[(grupo - 1) % len(orden)])
    maximo = max((meters(p['longitud']) for p in muestra), default=1.0)
    pulgadas_por_metro = ancho_eje / maximo
    etapas = sorted({grupo for p in muestra for grupo, _, _ in p['secuencia']})
    for y, patron in enumerate(muestra):
        start = 0
        for grupo, longitud, cantidad in patron['secuencia']:
            pieza = meters(longitud)
            rgb = color(grupo)
            texto = metros(pieza).removesuffix(' m')
            # Texto blanco o negro según la luminancia del color de la etapa.
            tinta = 'black' if 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2] > 0.6 else 'white'
            for _ in range(cantidad):
                # Una pieza por rectángulo, con borde fino: el taller distingue cada corte.
                ax.barh(y, pieza, left=start, height=.8, color=rgb, edgecolor='white', linewidth=.5)
                if cabe_rotulo(pieza, texto, pulgadas_por_metro):
                    ax.text(start + pieza / 2, y, texto, ha='center', va='center', fontsize=ROTULO_PT, color=tinta)
                start += pieza
        for key, tono in [('kerf', 'black'), ('discarded', 'tomato')]:
            width = meters(patron[key])
            ax.barh(y, width, left=start, height=.8, color=tono)
            start += width
        ax.barh(y, meters(patron['remaining']), left=start, height=.8, color='lightgray', hatch='//')
    ax.set_xlim(0, maximo)
    ax.set_ylim(len(muestra) - .5, -.5)
    ax.set_yticks(range(len(muestra)), [f"{p['patron_id']} ×{numero(p['repeticiones'], 0)}" for p in muestra],
                  fontsize=6)
    ax.tick_params(axis='x', labelsize=6)
    ax.set_xlabel('Longitud (m)', fontsize=7)
    ax.set_title(titulo, fontsize=9)
    leyenda = ([Patch(facecolor=color(g), label=f'E{g}') for g in etapas]
               + [Patch(facecolor='black', label='Pérdida por corte'), Patch(facecolor='tomato', label='Descarte'),
                  Patch(facecolor='lightgray', hatch='//', label='Saldo reutilizable')])
    # Debajo del rótulo del eje: hasta 12 entradas por fila; el pie de cobertura va al final.
    fig.legend(handles=leyenda, loc='lower center', ncol=min(len(leyenda), 12), fontsize=6, frameon=False,
               bbox_to_anchor=(0.5, 0.16 / alto))
    pie = cobertura(muestra, total_patrones, total_barras)['texto'] + '.'
    if etapas and etapas[-1] > 18:
        pie += ' Los colores de etapa se repiten desde E19.'
    fig.text(NESTING_IZQUIERDA_IN / NESTING_ANCHO_IN, 0.04 / alto, pie, fontsize=6)
    return fig, [p.get_label() for p in leyenda]


def imagenes_nesting(problem, muestra, total_patrones, total_barras):
    """Bloques PNG en base64 para el PDF: 18 patrones por página, a escala casi real (R-01)."""
    import base64
    import io
    import matplotlib.pyplot as plt
    paginas = [muestra[i:i + PATRONES_POR_PAGINA] for i in range(0, len(muestra), PATRONES_POR_PAGINA)]
    bloques = []
    for numero_pagina, pagina in enumerate(paginas, 1):
        fig, _ = dibujar_nesting(problem, pagina, total_patrones, total_barras,
                                 f'Nesting lineal por patrones de corte (página {numero_pagina} de {len(paginas)})')
        try:
            buffer = io.BytesIO()
            fig.savefig(buffer, format='png', dpi=NESTING_DPI)
        finally:
            plt.close(fig)
        bloques.append(base64.b64encode(buffer.getvalue()).decode('ascii'))
    return bloques


def compra_html(analisis):
    """Sección «Resumen de compra» del PDF, con totales; las barras de inventario no son compra."""
    lineas = analisis.get('resumen_compra')
    if lineas is None:
        return f'<h2>Resumen de compra</h2><p>{NO_DISPONIBLE}.</p>'
    filas = ''.join(
        f"<tr><td>{escape(l['diametro'])}</td><td>{metros(l['longitud_m'])}</td>"
        f"<td>{ORIGENES.get(l['origen'], escape(l['origen']))}</td><td>{numero(l['barras'], 0)}</td>"
        f"<td>{numero(l['masa_kg'])} kg</td><td>{numero(l['aprovechamiento_pct'])} %</td></tr>"
        for l in lineas)
    totales = ''.join(
        f"<tr class=\"total\"><td>{escape(t['diametro'] if t['diametro'].startswith('Total') else 'Total ' + t['diametro'])}"
        f"</td><td></td><td>{escape(t['origen'])}</td><td>{numero(t['barras'], 0)}</td>"
        f"<td>{numero(t['masa_kg'])} kg</td><td></td></tr>"
        for t in totales_compra_rows(analisis))
    return ('<h2>Resumen de compra</h2><table><tr><th>Diámetro</th><th>Longitud</th><th>Origen</th>'
            f'<th>Barras</th><th>Masa</th><th>Aprovechamiento</th></tr>{filas}{totales}</table>'
            '<p>Las barras de inventario adicional se toman del inventario y no se compran.</p>')


def admisibilidad_html(analisis):
    """Secciones «Desperdicio» y «Admisibilidad» por diámetro del PDF."""
    if not analisis.get('admisibilidad'):
        return f'<h2>Admisibilidad</h2><p>{NO_DISPONIBLE}.</p>'
    perdidas = analisis['perdidas']
    proyecto = analisis['admisibilidad']['proyecto']
    umbral = analisis.get('umbral_desperdicio_pct')
    estado = ESTADOS[proyecto['estado']]
    if proyecto['diferencia_pp'] is not None:
        estado += f" ({con_signo(proyecto['diferencia_pp'])} pp frente al umbral de {numero(umbral)} %)"
    filas = ''.join(
        f"<tr><td>{escape(e['diametro'])}</td><td>{numero(e['desperdicio_pct'])} %</td>"
        f"<td>{escape(ESTADOS[e['estado']])}</td>"
        f"<td>{'' if e['diferencia_pp'] is None else con_signo(e['diferencia_pp']) + ' pp'}</td></tr>"
        for e in analisis['admisibilidad']['por_diametro'])
    return (f"<h2>Desperdicio</h2><p>Pérdida irrecuperable (corte y descartes): "
            f"{numero(perdidas['irrecuperable']['kg'])} kg ({numero(perdidas['irrecuperable']['pct'])} %). "
            f"Saldo reutilizable final: {numero(perdidas['reutilizable']['kg'])} kg "
            f"({numero(perdidas['reutilizable']['pct'])} %).</p>"
            f"<h2>Admisibilidad</h2><p>Proyecto: {escape(estado)}.</p>"
            f"<table><tr><th>Diámetro</th><th>Desperdicio</th><th>Estado</th><th>Diferencia</th></tr>{filas}</table>"
            f"<p>El umbral lo define el usuario; no se identificó un máximo normativo.</p>")


def indicadores_html(result, analisis):
    """Sección «Indicadores clave» del PDF (FR-009): compra, desperdicio y admisibilidad."""
    m = result['metrics']
    totales = {t['diametro']: t for t in totales_compra_rows(analisis)}
    comprado = totales.get('Total comprado')
    inventario = totales.get('Total tomado del inventario')
    proyecto = (analisis.get('admisibilidad') or {}).get('proyecto') or {}
    admisibilidad = ESTADOS.get(proyecto.get('estado'), NO_DISPONIBLE)
    if proyecto.get('diferencia_pp') is not None:
        admisibilidad += (f" ({con_signo(proyecto['diferencia_pp'])} pp frente al umbral de "
                          f"{numero(analisis['umbral_desperdicio_pct'])} %)")
    filas = [
        ('Barras a comprar', f"{numero(comprado['barras'], 0)} barras ({numero(comprado['masa_kg'])} kg)"
         if comprado else NO_DISPONIBLE),
        ('Barras tomadas del inventario', numero(inventario['barras'], 0) if inventario else '0'),
        ('Desperdicio en masa', f"{numero(m.get('desperdicio_porcentaje'))} %"),
        ('Aprovechamiento', f"{numero(analisis.get('aprovechamiento_pct'))} %"
         if analisis.get('aprovechamiento_pct') is not None else NO_DISPONIBLE),
        ('Admisibilidad', admisibilidad)]
    cuerpo = ''.join(f'<tr><th>{escape(k)}</th><td>{escape(v)}</td></tr>' for k, v in filas)
    return f'<h2>Indicadores clave</h2><table class="indicadores">{cuerpo}</table>'


def tecnicos_html(problem, result, analisis):
    """Sección final «Datos técnicos» del PDF (FR-009): condiciones legibles y lo necesario para reproducir."""
    m = result['metrics']
    condiciones = ''.join(
        f"<tr><td>{escape(r['condicion'])}</td><td>{escape(r['valor'])}</td><td>{escape(r['referencia'])}</td></tr>"
        for r in parametros_rows(problem))
    return ('<h2>Datos técnicos</h2>'
            '<table><tr><th>Condición de corte</th><th>Valor</th><th>Referencia</th></tr>'
            f'{condiciones}</table>'
            f"<p>Motor {escape(str(m.get('motor')))}, análisis {escape(str(analisis.get('version') or NO_DISPONIBLE))}, "
            f"método {escape(str(m.get('metodo')))}, semilla {m.get('seed')}, "
            f"huella de la entrada {escape(str(m.get('input_hash')))}.</p>"
            f"<p>{numero(m.get('piezas'), 0)} piezas; {numero(m.get('barras'), 0)} barras raíz utilizadas una sola "
            f"vez; masa de barras utilizadas: {numero(m.get('masa_inicial_kg'))} kg.</p>"
            '<p>Inventario final proyectado; verificar físicamente antes de usar.</p>')


def pdf_html(problem, result, analisis, patrones, title, version, imagenes):
    """HTML del PDF (contracts/artefactos.md §2): lo útil primero y los datos técnicos al final.

    `imagenes` son los bloques de nesting en PNG base64 (US3); una lista vacía omite las imágenes.
    """
    from datetime import datetime, timedelta, timezone
    m = result['metrics']
    fecha = datetime.now(timezone(timedelta(hours=-5))).strftime('%Y-%m-%d %H:%M')
    perfil = PERFILES.get(m.get('perfil'), m.get('perfil') or NO_DISPONIBLE)
    rotulo_version = f'Versión {version}' if version is not None else 'Versión no asignada'
    verificado = (analisis.get('verificacion') or {}).get('valido', m.get('valido'))
    estado = VERIFICADO if verificado else 'Plan no verificado.'
    return f'''<html lang="es"><meta charset="utf-8"><style>
    @page {{ size: A4 landscape; margin: 15mm; }} body {{ font-family: sans-serif; font-size: 10px; }}
    table {{ border-collapse: collapse; width: 100%; }} th,td {{ padding: 4px; border: 1px solid #ccc; }}
    th {{ text-align: left; }} tr.total td {{ font-weight: bold; background: #f3f2ed; }}
    table.indicadores {{ width: auto; }} .meta {{ color: #424a52; }}
    img.nesting {{ display: block; width: 100%; break-inside: avoid; page-break-before: always; }}
    </style><h1>Plan de corte — {escape(title)}</h1>
    <p class="meta">{rotulo_version} · Perfil {escape(perfil)} · Generado el {fecha} (hora de Colombia)</p>
    <p><strong>{estado}</strong></p>
    {indicadores_html(result, analisis)}
    {compra_html(analisis)}
    {patrones_html(problem, result, patrones, imagenes)}
    {admisibilidad_html(analisis)}
    {cota_html(analisis)}
    {avisos_html(analisis)}
    {tecnicos_html(problem, result, analisis)}</html>'''


def generate(problem, result, directory, title='', visuals=True, version=None):
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
                     'diametro': b['diametro'], 'origen': b['origen'], 'longitud_m': meters(b['longitud']),
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
    compra = analisis.get('resumen_compra')
    # Orden de hojas de contracts/artefactos.md §1 (FR-001): lo útil primero, lo técnico al final.
    with pd.ExcelWriter(files['excel_path'], engine='openpyxl') as writer:
        indicadores = resumen_rows(problem, result, analisis)
        pd.DataFrame(indicadores, columns=COLUMNAS_RESUMEN).to_excel(writer, sheet_name='Resumen', index=False)
        # Encabezado, indicadores, una fila en blanco y el título del bloque de totales (FR-003).
        fila_titulo = len(indicadores) + 2
        writer.sheets['Resumen'].cell(row=fila_titulo + 1, column=1, value='Totales de compra')
        pd.DataFrame(totales_compra_rows(analisis), columns=COLUMNAS_TOTALES).to_excel(
            writer, sheet_name='Resumen', index=False, startrow=fila_titulo + 1)
        pd.DataFrame(compra if compra is not None else [{'diametro': NO_DISPONIBLE}],
                     columns=COLUMNAS_COMPRA).to_excel(writer, sheet_name='Resumen de compra', index=False)
        pd.DataFrame(patrones_rows(problem, patrones), columns=COLUMNAS_PATRONES).to_excel(
            writer, sheet_name='Patrones', index=False)
        pd.DataFrame(cuts).sort_values(['grupo_ejecucion', 'diametro', 'barra_id']).to_excel(
            writer, sheet_name='Cortes', index=False)
        pd.DataFrame(bars).to_excel(writer, sheet_name='Barras', index=False)
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
        pd.DataFrame(admisibilidad_rows(analisis), columns=COLUMNAS_ADMISIBILIDAD).to_excel(
            writer, sheet_name='Admisibilidad', index=False)
        pd.DataFrame(cota_rows(analisis), columns=COLUMNAS_COTA).to_excel(writer, sheet_name='Cota', index=False)
        pd.DataFrame(avisos_rows(analisis), columns=COLUMNAS_AVISOS).to_excel(writer, sheet_name='Avisos', index=False)
        pd.DataFrame(result['inventory'], columns=['diametro', 'longitud_m', 'cantidad']).to_excel(
            writer, sheet_name='Inventario', index=False)
        pd.DataFrame([{'stock_id': s['stock_id'], 'diametro': s['diametro'],
                       'longitud_m': meters(s['longitud']), 'cantidad': s['cantidad']}
                      for s in problem.get('excluded_inventory', [])],
                     columns=['stock_id', 'diametro', 'longitud_m', 'cantidad']).to_excel(
                         writer, sheet_name='Inventario excluido', index=False)
        pd.DataFrame(parametros_rows(problem), columns=COLUMNAS_PARAMETROS).to_excel(
            writer, sheet_name='Parámetros', index=False)
        pd.DataFrame(trazabilidad_rows(problem, result, analisis), columns=['dato', 'valor']).to_excel(
            writer, sheet_name='Trazabilidad', index=False)
    export_inventory(result['inventory'], files['inventory_path'])
    if not visuals:
        return files
    from weasyprint import HTML
    import matplotlib.pyplot as plt
    # Nesting lineal (FR-012 a FR-014): primero el PNG (hasta 60 patrones) y luego los mismos
    # patrones por páginas de 18 para el PDF. Si el dibujo falla, el PDF se genera igual con
    # «imagen no disponible» y el error se propaga después para que la versión lo registre (R-01).
    muestra = mas_repetidos(patrones, LIMITE_PNG_PATRONES)
    imagenes, error_dibujo = [], None
    try:
        fig, _ = dibujar_nesting(problem, muestra, len(patrones), len(result['bars']))
        try:
            files['graph_image_path'] = str(path / 'grafica_cortes.png')
            fig.savefig(files['graph_image_path'], dpi=NESTING_DPI)
        finally:
            plt.close(fig)
        imagenes = imagenes_nesting(problem, muestra, len(patrones), len(result['bars']))
    except Exception as error:
        imagenes, error_dibujo = None, error
    html = pdf_html(problem, result, analisis, patrones, title, version, imagenes)
    files['pdf_path'] = str(path / 'plan_corte.pdf')
    HTML(string=html).write_pdf(files['pdf_path'])
    if error_dibujo is not None:
        raise error_dibujo
    return files
