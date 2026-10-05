#!/usr/bin/env python3
"""Genera las cartillas sintéticas 003 (vivienda) y 004 (edificio) del Bloque N.

Son datos sintéticos para evaluar el motor de corte con tamaños y mezclas de diámetros que 001 y
002 no cubren. No son un diseño estructural ni certifican cumplimiento de la NSR-10: las longitudes
salen de una geometría ficticia y de los supuestos S-01 a S-14 (INF-018), documentados en el
MEMORIA_DESPIECE.md de cada cartilla.

Todo se calcula en Decimal desde tablas fijas, sin azar. El XLSX se escribe sin compresión y con
fechas fijas, de modo que la misma versión de openpyxl produce los mismos bytes. Los archivos se
crean de forma exclusiva (nunca se sobrescriben); --verificar regenera en memoria y compara.

    PYTHONUTF8=1 python scripts/generar_cartillas_sinteticas.py [--cartilla 003] [--verificar]
"""
import argparse
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal as D, ROUND_CEILING
import hashlib
import io
import json
from pathlib import Path
import re
import sys
import zipfile

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / 'backend'))
from cutting.nominal import MASA_NOMINAL_KG_M  # noqa: E402  (fuente única de kg/m)

ENCABEZADOS = ('N° Orden', 'Elemento', 'N° de Barra', 'Longitud total (m)', 'Cantidad',
               'Grupo de Ejecución', 'Masa total (kg)')
ANCHOS = {'B': 26, 'C': 14.33, 'D': 17.89, 'F': 20.22, 'G': 16.89}
# Diámetro nominal en mm: NSR-10, Tabla C.3.5.3-2 (REF-NSR10-TABLA).
DB_MM = {'#2': '6.4', '#3': '9.5', '#4': '12.7', '#5': '15.9', '#6': '19.1', '#7': '22.2',
         '#8': '25.4', '#9': '28.7', '#10': '32.3', '#11': '35.8', '#14': '43', '#18': '57.3'}
FECHA = datetime(2026, 10, 4)
FECHA_W3C = b'2026-10-04T00:00:00Z'

PASO = D('0.05')                 # S-08
L_MAX = D('12')                  # barra comercial más larga del catálogo
FC, FY = D(21), D(420)           # S-01, en MPa
R_ZAPATA, R_VC, R_PORTICO, R_LOSA = D('0.075'), D('0.05'), D('0.04'), D('0.02')  # S-03
GANCHO_SISMICO = D('0.10')       # S-05: 75 mm de extensión más el doblez, por gancho de 135°
ESTRIBO = '#3'                   # S-10
ANCLAJE_ESCALERA = D('0.30')     # S-09


def arriba(valor, paso=PASO):
    """Redondea hacia arriba al múltiplo de `paso` (S-08)."""
    return (valor / paso).to_integral_value(rounding=ROUND_CEILING) * paso


def veces(longitud, separacion):
    return int((longitud / separacion).to_integral_value(rounding=ROUND_CEILING))


def db(diam):
    return D(DB_MM[diam]) / 1000


def gancho(diam):
    """Extensión del gancho estándar de 90°: 12 db (S-04, C.7.1.2)."""
    return arriba(12 * db(diam))


def desarrollo(diam):
    """ld en tracción, caso favorable de C.12.2.2 con ψt = ψe = λ = 1 (S-01, S-06)."""
    k = D('2.1') if int(diam[1:]) <= 6 else D('1.7')
    return FY / (k * FC.sqrt()) * db(diam)


def traslapo(diam):
    """Empalme clase B = 1.3 ld, no menor de 300 mm (S-06, C.12.15.1)."""
    return arriba(max(D('1.3') * desarrollo(diam), D('0.30')))


def dividir(total, diam):
    """Tramos de una barra continua de longitud desarrollada `total` (S-07).

    Tramos de 12.00 m y un resto, unidos por traslapos. Si el resto queda por debajo de
    max(2 traslapos, 2 m), los dos últimos tramos se igualan.
    """
    total = arriba(total)
    if total <= L_MAX:
        return [total]
    lap = traslapo(diam)
    n = 2
    while n * L_MAX < total + (n - 1) * lap:
        n += 1
    resto = total + (n - 1) * lap - (n - 1) * L_MAX
    tramos = [L_MAX] * (n - 1) + [arriba(resto)]
    if tramos[-1] < max(2 * lap, D(2)):
        par = arriba((L_MAX + resto) / 2)
        tramos[-2:] = [par, par]
    return tramos


def estribo(b, h, r):
    """Estribo cerrado con dos ganchos sísmicos (S-05)."""
    return arriba(2 * (b - 2 * r) + 2 * (h - 2 * r) + 2 * GANCHO_SISMICO)


def grapa(b, r):
    """Gancho suplementario con dos ganchos sísmicos (S-05)."""
    return arriba(b - 2 * r + 2 * GANCHO_SISMICO)


def estribos_uniformes(libre, s):
    """Primer estribo a 0.05 m de cada cara y separación constante."""
    return veces(libre - D('0.10'), s) + 1


def estribos_confinados(libre, zona, s1, s2):
    """Zonas de longitud `zona` en cada extremo con s1 y el centro con s2 (S-09)."""
    if libre <= 2 * zona:
        return estribos_uniformes(libre, s1)
    return 2 * (veces(zona - D('0.05'), s1) + 1) + max(0, veces(libre - 2 * zona, s2) - 1)


def bastones(luces, apoyo, r, diam):
    """Longitud de los bastones superiores en cada apoyo: un tercio de la luz libre a cada lado."""
    resultado = []
    for i in range(len(luces) + 1):
        lados = [luces[j] for j in (i - 1, i) if 0 <= j < len(luces)]
        longitud = sum((luz - apoyo) / 3 for luz in lados) + apoyo
        if len(lados) == 1:
            longitud += gancho(diam) - r
        resultado.append(longitud)
    return resultado


@dataclass(frozen=True)
class Columna:
    b: D           # sección cuadrada b × b
    diam: str
    barras: int
    grapas: int    # ganchos suplementarios por juego de estribos


@dataclass(frozen=True)
class Viga:
    b: D
    h: D
    diam: str
    superior: int  # barras continuas
    inferior: int
    bastones: int  # bastones superiores por apoyo


@dataclass(frozen=True)
class Modelo:
    codigo: str
    archivo: str
    titulo: str
    sistema: str
    luces_x: tuple
    luces_y: tuple
    altura: D                # altura de entrepiso
    desplante: D             # del fondo de la zapata al nivel 0
    columnas: tuple          # una Columna por piso
    zapatas: dict            # tipo -> lado de la zapata cuadrada
    zapata_h: D
    zapata_diam: str
    zapata_s: D
    vc: Viga
    vc_s: D
    vigas: tuple             # una Viga por losa (sobre cada piso)
    viga_s1: D
    viga_s2: D
    col_so: D
    col_s: D
    vigueta_s: D
    vigueta_diam: str
    vigueta_inferior: int
    loseta_diam: str
    loseta_s: D
    escalera_tramos: int     # tramos por piso
    escalera_ancho: D
    escalera_huella: D       # proyección horizontal de un tramo
    escalera_long: tuple     # (diámetro, separación)
    escalera_trans: tuple


MODELOS = {
    '003': Modelo(
        codigo='003', archivo='003-sinteticaVivienda.xlsx',
        titulo='Vivienda de dos pisos (sintética)',
        sistema='pórticos de concreto reforzado con losa aligerada en una dirección',
        luces_x=(D('3.50'), D('4.00'), D('3.50')), luces_y=(D('4.50'), D('4.50')),
        altura=D('2.70'), desplante=D('1.20'),
        columnas=(Columna(D('0.30'), '#5', 4, 0),) * 2,
        zapatas={'esquina': D('1.00'), 'borde': D('1.20'), 'interior': D('1.40')},
        zapata_h=D('0.30'), zapata_diam='#4', zapata_s=D('0.15'),
        vc=Viga(D('0.25'), D('0.30'), '#4', 2, 2, 0), vc_s=D('0.15'),
        vigas=(Viga(D('0.25'), D('0.35'), '#5', 2, 2, 1),) * 2,
        viga_s1=D('0.075'), viga_s2=D('0.15'), col_so=D('0.10'), col_s=D('0.20'),
        vigueta_s=D('0.75'), vigueta_diam='#4', vigueta_inferior=2,
        loseta_diam='#3', loseta_s=D('0.25'),
        escalera_tramos=1, escalera_ancho=D('1.00'), escalera_huella=D('3.92'),
        escalera_long=('#4', D('0.15')), escalera_trans=('#3', D('0.20'))),
    '004': Modelo(
        codigo='004', archivo='004-sinteticaEdificio.xlsx',
        titulo='Edificio de cinco pisos (sintético)',
        sistema='pórticos de concreto reforzado con losa aligerada en una dirección',
        luces_x=(D('5.00'), D('5.50'), D('5.50'), D('5.00')),
        luces_y=(D('5.00'), D('6.00'), D('5.00')),
        altura=D('3.00'), desplante=D('1.80'),
        columnas=(Columna(D('0.45'), '#7', 8, 2),) * 2 + (Columna(D('0.40'), '#6', 8, 2),) * 3,
        zapatas={'esquina': D('1.60'), 'borde': D('2.00'), 'interior': D('2.40')},
        zapata_h=D('0.45'), zapata_diam='#5', zapata_s=D('0.15'),
        vc=Viga(D('0.35'), D('0.45'), '#6', 3, 3, 0), vc_s=D('0.15'),
        vigas=(Viga(D('0.30'), D('0.45'), '#6', 2, 3, 2),) * 2
              + (Viga(D('0.30'), D('0.45'), '#5', 2, 3, 2),) * 3,
        viga_s1=D('0.10'), viga_s2=D('0.20'), col_so=D('0.10'), col_s=D('0.20'),
        vigueta_s=D('0.80'), vigueta_diam='#4', vigueta_inferior=2,
        loseta_diam='#3', loseta_s=D('0.25'),
        escalera_tramos=2, escalera_ancho=D('1.20'), escalera_huella=D('2.52'),
        escalera_long=('#4', D('0.15')), escalera_trans=('#3', D('0.20'))),
}


def ejes(luces):
    posiciones = [D(0)]
    for luz in luces:
        posiciones.append(posiciones[-1] + luz)
    return posiciones


def nombre_losa(m, piso):
    return 'cubierta' if piso == len(m.columnas) else f'losa nivel {piso + 1}'


def generar(m):
    """Filas de la cartilla: (grupo, elemento, diámetro, longitud) -> cantidad, ordenadas."""
    piezas = defaultdict(int)

    def agregar(grupo, elemento, diam, longitud, cantidad):
        if cantidad > 0:
            piezas[(grupo, elemento, diam, arriba(longitud))] += cantidad

    xs, ys = ejes(m.luces_x), ejes(m.luces_y)
    largo_x, largo_y = xs[-1], ys[-1]
    n_col = len(xs) * len(ys)
    pisos = len(m.columnas)
    # Líneas de vigas: cada eje en x recorre luces_x y cada eje en y recorre luces_y.
    lineas = [m.luces_x] * len(ys) + [m.luces_y] * len(xs)
    c1 = m.columnas[0]

    # Grupo 1: cimentación (S-12).
    for x in xs:
        for y in ys:
            extremos = (x in (xs[0], xs[-1])) + (y in (ys[0], ys[-1]))
            lado = m.zapatas[{2: 'esquina', 1: 'borde', 0: 'interior'}[extremos]]
            barras = veces(lado - 2 * R_ZAPATA, m.zapata_s) + 1
            agregar(1, 'Zapatas', m.zapata_diam,
                    lado - 2 * R_ZAPATA + 2 * gancho(m.zapata_diam), 2 * barras)
    # Arranques: del fondo de la zapata a la mitad del piso 1 más el traslapo (S-14).
    agregar(1, 'Arranques de columnas', c1.diam,
            m.desplante - R_ZAPATA + gancho(c1.diam) + m.altura / 2 + traslapo(c1.diam),
            n_col * c1.barras)
    for luces in lineas:
        total = sum(luces) + c1.b - 2 * R_VC + 2 * gancho(m.vc.diam)
        for tramo in dividir(total, m.vc.diam):
            agregar(1, 'Vigas de cimentación', m.vc.diam, tramo, m.vc.superior + m.vc.inferior)
        for luz in luces:
            agregar(1, 'Vigas de cimentación', ESTRIBO, estribo(m.vc.b, m.vc.h, R_VC),
                    estribos_uniformes(luz - c1.b, m.vc_s))

    for piso in range(1, pisos + 1):
        col, viga = m.columnas[piso - 1], m.vigas[piso - 1]
        losa = nombre_losa(m, piso)

        # Grupo 2k: columnas del piso k. Empalmes a media altura (S-14).
        elemento = f'Columnas piso {piso}'
        if piso < pisos:
            longitud = m.altura + traslapo(col.diam)
        else:
            longitud = m.altura / 2 - R_PORTICO + gancho(col.diam)
        agregar(2 * piso, elemento, col.diam, longitud, n_col * col.barras)
        libre = m.altura - viga.h
        zona = max(libre / 6, col.b, D('0.50'))
        juegos = estribos_confinados(libre, zona, m.col_so, m.col_s) + veces(viga.h, m.col_so)
        agregar(2 * piso, elemento, ESTRIBO, estribo(col.b, col.b, R_PORTICO), n_col * juegos)
        agregar(2 * piso, elemento, ESTRIBO, grapa(col.b, R_PORTICO), n_col * juegos * col.grapas)

        # Grupo 2k+1: vigas, viguetas, loseta y escalera de la losa sobre el piso k.
        grupo = 2 * piso + 1
        for luces in lineas:
            total = sum(luces) + col.b - 2 * R_PORTICO + 2 * gancho(viga.diam)
            for tramo in dividir(total, viga.diam):
                agregar(grupo, f'Vigas {losa}', viga.diam, tramo, viga.superior + viga.inferior)
            for longitud in bastones(luces, col.b, R_PORTICO, viga.diam):
                agregar(grupo, f'Vigas {losa}', viga.diam, longitud, viga.bastones)
            for luz in luces:
                agregar(grupo, f'Vigas {losa}', ESTRIBO, estribo(viga.b, viga.h, R_PORTICO),
                        estribos_confinados(luz - col.b, 2 * viga.h, m.viga_s1, m.viga_s2))
        # Viguetas paralelas al eje y, apoyadas en las vigas de los ejes en x.
        viguetas = sum(max(1, veces(luz - viga.b, m.vigueta_s) - 1) for luz in m.luces_x)
        total = largo_y + viga.b - 2 * R_PORTICO + 2 * gancho(m.vigueta_diam)
        for tramo in dividir(total, m.vigueta_diam):
            agregar(grupo, f'Viguetas {losa}', m.vigueta_diam, tramo,
                    viguetas * m.vigueta_inferior)
        for longitud in bastones(m.luces_y, viga.b, R_PORTICO, m.vigueta_diam):
            agregar(grupo, f'Viguetas {losa}', m.vigueta_diam, longitud, viguetas)
        # Loseta: barras rectas en las dos direcciones, ancladas en las vigas de borde.
        for largo, ancho in ((largo_x, largo_y), (largo_y, largo_x)):
            for tramo in dividir(largo + viga.b - 2 * R_PORTICO, m.loseta_diam):
                agregar(grupo, f'Loseta {losa}', m.loseta_diam, tramo,
                        veces(ancho, m.loseta_s) + 1)
        # Escalera del piso k al k+1; la cubierta no tiene acceso (S-13).
        if piso < pisos:
            elemento = f'Escalera piso {piso}'
            subida = m.altura / m.escalera_tramos
            inclinada = (m.escalera_huella ** 2 + subida ** 2).sqrt()
            (d_long, s_long), (d_trans, s_trans) = m.escalera_long, m.escalera_trans
            barras = veces(m.escalera_ancho - 2 * R_LOSA, s_long) + 1
            tramos = m.escalera_tramos
            agregar(grupo, elemento, d_long,
                    inclinada + 2 * (ANCLAJE_ESCALERA + gancho(d_long)), tramos * barras)
            agregar(grupo, elemento, d_long,
                    inclinada / 4 + ANCLAJE_ESCALERA + gancho(d_long), tramos * 2 * barras)
            agregar(grupo, elemento, d_trans,
                    m.escalera_ancho - 2 * R_LOSA + 2 * gancho(d_trans),
                    tramos * (veces(inclinada, s_trans) + 1))

    filas = []
    orden = sorted(piezas.items(), key=lambda kv: (kv[0][0], int(kv[0][2][1:]), -kv[0][3], kv[0][1]))
    for numero, ((grupo, elemento, diam, longitud), cantidad) in enumerate(orden, 1):
        masa = D(MASA_NOMINAL_KG_M[diam]) * longitud * cantidad
        filas.append({'orden': numero, 'elemento': elemento, 'diametro': diam,
                      'longitud': longitud, 'cantidad': cantidad, 'grupo': grupo, 'masa': masa})
    validar_filas(filas)
    return filas


def validar_filas(filas):
    grupos = sorted({f['grupo'] for f in filas})
    if grupos != list(range(1, len(grupos) + 1)):
        raise ValueError(f'Etapas no contiguas: {grupos}')
    for f in filas:
        if not (0 < f['longitud'] <= L_MAX) or f['longitud'] % PASO:
            raise ValueError(f'Longitud fuera de regla: {f}')
        if f['diametro'] not in MASA_NOMINAL_KG_M or f['diametro'] == '#2':
            raise ValueError(f'Diámetro fuera del catálogo: {f}')
        if f['cantidad'] <= 0 or f['masa'] != D(MASA_NOMINAL_KG_M[f['diametro']]) * f['longitud'] * f['cantidad']:
            raise ValueError(f'Cantidad o masa inválida: {f}')


def numero(valor):
    """Entero si no tiene decimales; si no, float con representación exacta del decimal."""
    valor = valor.normalize()
    return int(valor) if valor == valor.to_integral_value() else float(valor)


def hash_contenido(filas):
    canonico = [[f['orden'], f['elemento'], f['diametro'], str(f['longitud'].normalize()),
                 f['cantidad'], f['grupo'], str(f['masa'].normalize())] for f in filas]
    return hashlib.sha256(json.dumps(canonico, ensure_ascii=False).encode()).hexdigest()


def libro(filas):
    """Bytes del XLSX con el formato de 001 y 002, masas numéricas y sin fórmulas."""
    from openpyxl import Workbook
    wb = Workbook()
    hoja = wb.active
    hoja.title = 'Hoja1'
    hoja.append(ENCABEZADOS)
    for f in filas:
        hoja.append([f['orden'], f['elemento'], f['diametro'], numero(f['longitud']),
                     f['cantidad'], f['grupo'], numero(f['masa'])])
    for columna, ancho in ANCHOS.items():
        hoja.column_dimensions[columna].width = ancho
    tabla = wb.create_sheet('TablaBarras')
    tabla.append(('N° Barra', 'Diámetro nominal (m)', 'Masa por metro lineal (kg/m)'))
    for diam, masa in MASA_NOMINAL_KG_M.items():
        tabla.append((diam, numero(D(DB_MM[diam]) / 1000), numero(D(masa))))
    wb.properties.creator = 'scripts/generar_cartillas_sinteticas.py'
    wb.properties.created = wb.properties.modified = FECHA
    salida = io.BytesIO()
    wb.save(salida)
    return fijar_zip(salida.getvalue())


def fijar_zip(contenido):
    """Reescribe el zip sin compresión, con fechas y permisos fijos: bytes reproducibles."""
    salida = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(contenido)) as origen, \
            zipfile.ZipFile(salida, 'w', zipfile.ZIP_STORED) as destino:
        for info in origen.infolist():
            datos = origen.read(info.filename)
            if info.filename == 'docProps/core.xml':
                datos = re.sub(rb'(<dcterms:(?:created|modified)[^>]*>)[^<]*',
                               rb'\g<1>' + FECHA_W3C, datos)
            nuevo = zipfile.ZipInfo(info.filename, date_time=FECHA.timetuple()[:6])
            nuevo.create_system = 3
            nuevo.external_attr = 0o644 << 16
            destino.writestr(nuevo, datos)
    return salida.getvalue()


def fmt(valor, decimales=None):
    """Punto decimal y sin separador de miles (formato del Bloque M); al menos dos decimales."""
    if decimales is None:
        decimales = max(2, -D(valor).normalize().as_tuple().exponent)
    return f'{valor:.{decimales}f}'


def plural(n, singular, varios):
    return f'{n} {singular if n == 1 else varios}'


def estadisticas(filas):
    por_diam = defaultdict(lambda: {'filas': 0, 'piezas': 0, 'masa': D(0), 'longitudes': set()})
    por_grupo = defaultdict(lambda: {'piezas': 0, 'masa': D(0), 'diametros': set(),
                                     'elementos': []})
    histograma = defaultdict(int)
    comercial = D(0)
    for f in filas:
        d = por_diam[f['diametro']]
        d['filas'] += 1
        d['piezas'] += f['cantidad']
        d['masa'] += f['masa']
        d['longitudes'].add(f['longitud'])
        g = por_grupo[f['grupo']]
        g['piezas'] += f['cantidad']
        g['masa'] += f['masa']
        g['diametros'].add(f['diametro'])
        if f['elemento'] not in g['elementos']:
            g['elementos'].append(f['elemento'])
        histograma[min(int(f['longitud']), 11)] += f['cantidad']
        if f['longitud'] in (6, 9, 12):
            comercial += f['masa']
    return por_diam, por_grupo, histograma, comercial


def memoria(m, filas, datos):
    """Texto de MEMORIA_DESPIECE.md, generado desde las mismas constantes que la cartilla."""
    por_diam, por_grupo, histograma, comercial = estadisticas(filas)
    piezas = sum(f['cantidad'] for f in filas)
    masa = sum(f['masa'] for f in filas)
    pisos = len(m.columnas)
    xs, ys = ejes(m.luces_x), ejes(m.luces_y)
    area = xs[-1] * ys[-1] * pisos
    diametros = sorted(por_diam, key=lambda d: int(d[1:]))
    longitudes = {f['longitud'] for f in filas}
    l = []
    w = l.append
    w(f'# Memoria de despiece: cartilla {m.codigo}, {m.titulo.lower()}')
    w('')
    w('> Archivo generado por `scripts/generar_cartillas_sinteticas.py`; no se edita a mano.')
    w('> **Cartilla sintética.** La elaboró el autor para evaluar el motor de corte con un tamaño y')
    w('> una mezcla de diámetros que 001 y 002 no cubren. No proviene de una obra, no es un diseño')
    w('> estructural y no certifica cumplimiento de la NSR-10: las longitudes resultan de una')
    w('> geometría ficticia y de los supuestos de la sección 4. Sus resultados no son evidencia de')
    w('> desperdicio en obra (INF-017, INF-018, RIESGO-AC-011).')
    w('')
    w('## 1. Descripción')
    w('')
    w('| Atributo | Valor |')
    w('|---|---|')
    w(f'| Archivo | `tests/data/{m.codigo}/{m.archivo}` |')
    w(f'| Sistema | {m.sistema} |')
    w(f'| Pisos | {pisos}; entrepiso de {fmt(m.altura)} m |')
    w(f'| Ejes en x | {len(xs)}, luces {" / ".join(fmt(v) for v in m.luces_x)} m (total {fmt(xs[-1])} m) |')
    w(f'| Ejes en y | {len(ys)}, luces {" / ".join(fmt(v) for v in m.luces_y)} m (total {fmt(ys[-1])} m) |')
    w(f'| Columnas | {len(xs) * len(ys)} por piso |')
    w(f'| Área construida | {fmt(area)} m² ({pisos} × {fmt(xs[-1] * ys[-1])} m²) |')
    w(f'| Desplante | {fmt(m.desplante)} m del fondo de la zapata al nivel 0 |')
    w('')
    w('## 2. Secciones y refuerzo')
    w('')
    w('| Elemento | Sección (m) | Refuerzo longitudinal | Refuerzo transversal |')
    w('|---|---|---|---|')
    tipos = ', '.join(f'{t} {fmt(v)} × {fmt(v)}' for t, v in m.zapatas.items())
    w(f'| Zapatas aisladas | {tipos}; h = {fmt(m.zapata_h)} | parrilla {m.zapata_diam} @ {fmt(m.zapata_s)} en dos direcciones | — |')
    w(f'| Vigas de cimentación | {fmt(m.vc.b)} × {fmt(m.vc.h)} | {m.vc.superior} + {m.vc.inferior} {m.vc.diam} continuas | estribos {ESTRIBO} @ {fmt(m.vc_s)} |')
    for piso, col in enumerate(m.columnas, 1):
        grapas = f' + {col.grapas} grapas' if col.grapas else ''
        w(f'| Columnas piso {piso} | {fmt(col.b)} × {fmt(col.b)} | {col.barras} {col.diam} | estribos{grapas} {ESTRIBO}: {fmt(m.col_so)} en lo, {fmt(m.col_s)} al centro y {fmt(m.col_so)} en el nudo |')
    for piso, viga in enumerate(m.vigas, 1):
        w(f'| Vigas {nombre_losa(m, piso)} | {fmt(viga.b)} × {fmt(viga.h)} | {viga.superior} + {viga.inferior} {viga.diam} continuas, {plural(viga.bastones, "bastón superior", "bastones superiores")} por apoyo | estribos {ESTRIBO}: {fmt(m.viga_s1)} en 2h, {fmt(m.viga_s2)} al centro |')
    w(f'| Viguetas | @ {fmt(m.vigueta_s)}, paralelas al eje y | {m.vigueta_inferior} {m.vigueta_diam} inferiores continuas, 1 bastón {m.vigueta_diam} por apoyo | sin flejes (S-10) |')
    w(f'| Loseta | — | {m.loseta_diam} @ {fmt(m.loseta_s)} en dos direcciones | — |')
    d_long, s_long = m.escalera_long
    d_trans, s_trans = m.escalera_trans
    w(f'| Escalera | {plural(m.escalera_tramos, "tramo", "tramos")} por piso, ancho {fmt(m.escalera_ancho)}, huella total {fmt(m.escalera_huella)} por tramo | {d_long} @ {fmt(s_long)} inferior y negativos en los apoyos | {d_trans} @ {fmt(s_trans)} |')
    w('')
    w('## 3. Etapas (Grupo de Ejecución)')
    w('')
    w('| Grupo | Contenido | Diámetros | Piezas | Masa (kg) |')
    w('|---|---|---|---|---|')
    for grupo in sorted(por_grupo):
        g = por_grupo[grupo]
        diams = ', '.join(sorted(g['diametros'], key=lambda d: int(d[1:])))
        w(f'| {grupo} | {"; ".join(g["elementos"])} | {diams} | {g["piezas"]} | {fmt(g["masa"], 3)} |')
    w('')
    w('## 4. Supuestos de despiece (S-01 a S-14)')
    w('')
    w('Las páginas son las del PDF del Título C publicado por CAMACOL (Decreto 926 de 2010).')
    w('Fichas en `docs/tesis-doc/Referencias.md`.')
    w('')
    w('| ID | Supuesto | Valor | Fuente |')
    w('|---|---|---|---|')
    tabla_traslapos = ', '.join(f'{d} {fmt(traslapo(d))}' for d in diametros)
    tabla_ganchos = ', '.join(f'{d} {fmt(gancho(d))}' for d in diametros)
    for fila in (
        ('S-01', 'Materiales y factores de ld', "f'c = 21 MPa, fy = 420 MPa, ψt = ψe = λ = 1.0 (sin efecto de barra superior)", 'Supuesto; factores de C.12.2.4, p. C-220 (REF-NSR10-EMPALMES)'),
        ('S-02', 'Diámetros y masas nominales', 'NSR-10, Tabla C.3.5.3-2', 'p. C-47 (REF-NSR10-TABLA)'),
        ('S-03', 'Recubrimiento libre', 'zapatas 75 mm; vigas de cimentación 50 mm; vigas y columnas 40 mm; losas, viguetas y escaleras 20 mm', 'C.7.7.1, pp. C-96 y C-97 (REF-NSR10-GANCHOS-RECUBRIMIENTOS)'),
        ('S-04', 'Gancho estándar de 90°: extensión de 12 db; el doblez no se suma', tabla_ganchos + ' m', 'C.7.1.2, p. C-91 (REF-NSR10-GANCHOS-RECUBRIMIENTOS)'),
        ('S-05', 'Estribos cerrados y grapas con ganchos sísmicos de 135° (extensión 6 db, no menor de 75 mm)', 'se suman 0.10 m por gancho (75 mm más el doblez); estribo = 2(b − 2r) + 2(h − 2r) + 0.20; grapa = (b − 2r) + 0.20', 'C.7.1.4, p. C-91, y C.2.2, p. C-33; los 25 mm del doblez son supuesto'),
        ('S-06', 'Traslapo clase B = 1.3 ld, no menor de 300 mm; ld del caso favorable: 43.64 db hasta #6 y 53.91 db desde #7', tabla_traslapos + ' m', 'C.12.2.2, p. C-218, y C.12.15.1-2, pp. C-240 y C-241 (REF-NSR10-EMPALMES)'),
        ('S-07', 'Barras continuas de más de 12 m: tramos de 12.00 m más el resto; si el resto es menor que max(2 traslapos, 2 m) se igualan los dos últimos. No se modela la posición del empalme', '—', 'Supuesto. C.21.3.4.5 (p. C-366) prohíbe traslapos dentro de los nudos: un despiece real los desplaza'),
        ('S-08', 'Longitudes redondeadas hacia arriba a 0.05 m', '—', 'Supuesto; 123 de las 137 longitudes de 002 son múltiplos de 0.05 m'),
        ('S-09', 'Separaciones', f'vigas: {fmt(m.viga_s1)} en 2h y {fmt(m.viga_s2)} al centro; columnas: {fmt(m.col_so)} en lo = max(ln/6, b, 0.50 m) y {fmt(m.col_s)} al centro; nudos {fmt(m.col_so)}; vigas de cimentación {fmt(m.vc_s)}; parrillas {fmt(m.zapata_s)}; viguetas {fmt(m.vigueta_s)}; loseta {fmt(m.loseta_s)}; escalera {fmt(s_long)} y {fmt(s_trans)}, anclaje {fmt(ANCLAJE_ESCALERA)} m más gancho', 'Vigas y columnas dentro de los límites de DMO: C.21.3.4.6 y C.21.3.4.8 (pp. C-366 y C-367), C.21.3.5.6 a C.21.3.5.11 (pp. C-367 a C-369) (REF-NSR10-DMO). El resto es supuesto'),
        ('S-10', 'Estribos y grapas #3; sin barras #2; viguetas sin flejes', '—', 'C.7.10.5.1, p. C-103, y C.21.3.5.8; #2 no está en el catálogo de OICA'),
        ('S-11', 'Filas agregadas por elemento, diámetro, longitud y etapa', '—', 'Supuesto'),
        ('S-12', 'Etapas: 1 cimentación; columnas del piso k en el grupo 2k; losa sobre el piso k en el grupo 2k + 1', '—', 'Supuesto de secuencia constructiva'),
        ('S-13', 'Fuera del modelo: mampostería, cimentación profunda, aberturas de losa, descansos de escalera, acceso a la cubierta, cambios de sección (dobleces) y alambre de amarre', '—', 'Supuesto'),
        ('S-14', 'Empalmes de columnas a media altura del piso; arranques desde el fondo de la zapata con gancho; la última barra termina con gancho en la cubierta', '—', 'C.21.3.5.3, p. C-367 (REF-NSR10-DMO): traslapos solo en la mitad central'),
    ):
        w('| ' + ' | '.join(fila) + ' |')
    w('')
    w('## 5. Reglas por elemento')
    w('')
    c1, v1 = m.columnas[0], m.vigas[0]
    w(f'- **Zapatas:** barras por dirección = ⌈(lado − 2r) / s⌉ + 1; longitud = lado − 2r + 2 ganchos.')
    w(f'- **Arranques:** desplante − r + gancho + altura / 2 + traslapo.')
    intermedios = 'piso 1' if pisos == 2 else f'pisos 1 a {pisos - 1}'
    w(f'- **Columnas:** {intermedios}: altura + traslapo; piso {pisos}: altura / 2 − r + gancho.')
    w('- **Vigas y vigas de cimentación:** longitud desarrollada = suma de luces + ancho de columna − 2r + 2 ganchos, dividida según S-07; bastones = un tercio de la luz libre a cada lado del apoyo más el ancho del apoyo (en los extremos, más gancho − r).')
    w('- **Viguetas:** por cada luz en x, ⌈(luz − b viga) / s⌉ − 1; barra inferior continua en y y bastones como en vigas.')
    w('- **Loseta:** barras rectas de borde a borde en cada dirección, ⌈ancho / s⌉ + 1.')
    w('- **Escalera:** longitud inclinada √(huella² + subida²); inferiores con anclaje y gancho en cada extremo; negativos de un cuarto de la inclinada más anclaje y gancho; repartición transversal.')
    w('')
    libre = m.altura - v1.h
    zona = max(libre / 6, c1.b, D('0.50'))
    juegos = estribos_confinados(libre, zona, m.col_so, m.col_s) + veces(v1.h, m.col_so)
    bruto = 2 * (c1.b - 2 * R_PORTICO) * 2 + 2 * GANCHO_SISMICO
    w(f'**Ejemplo (estribo de columna del piso 1):** sección {fmt(c1.b)} × {fmt(c1.b)}, r = {fmt(R_PORTICO)}:')
    w(f'2({fmt(c1.b - 2 * R_PORTICO)}) + 2({fmt(c1.b - 2 * R_PORTICO)}) + 2(0.10) = {fmt(bruto)} → {fmt(estribo(c1.b, c1.b, R_PORTICO))} m.')
    w(f'Altura libre {fmt(libre)} m, lo = max({fmt(libre / 6, 3)}, {fmt(c1.b)}, 0.50) = {fmt(zona, 3)} m:')
    w(f'{juegos} juegos por columna y piso, incluidos {veces(v1.h, m.col_so)} en el nudo.')
    w('')
    w('## 6. Estadísticas')
    w('')
    w(f'- Filas: **{len(filas)}**. Piezas: **{piezas}**. Masa: **{fmt(masa, 3)} kg**.')
    w(f'- Diámetros: {", ".join(diametros)}. Etapas: {len(por_grupo)}. Longitudes distintas: {len(longitudes)}.')
    w(f'- Masa por m² construido: {fmt(masa / area, 1)} kg/m² (dato descriptivo, sin rango de referencia).')
    w(f'- Masa en piezas de longitud comercial (6, 9 o 12 m): {fmt(comercial, 3)} kg, {fmt(100 * comercial / masa, 1)} % (en 002: 26.2 %).')
    w('')
    w('| Diámetro | Filas | Piezas | Masa (kg) | % masa | Longitudes distintas | Mínima (m) | Máxima (m) |')
    w('|---|---|---|---|---|---|---|---|')
    for d in diametros:
        x = por_diam[d]
        w(f'| {d} | {x["filas"]} | {x["piezas"]} | {fmt(x["masa"], 3)} | {fmt(100 * x["masa"] / masa, 1)} | {len(x["longitudes"])} | {fmt(min(x["longitudes"]))} | {fmt(max(x["longitudes"]))} |')
    w('')
    w('La mínima por diámetro es el mínimo reutilizable automático que aplica OICA (menor longitud demandada).')
    w('')
    w('| Longitud (m) | Piezas |')
    w('|---|---|')
    for i in range(12):
        etiqueta = f'[{i}, {i + 1})' if i < 11 else '[11, 12]'
        w(f'| {etiqueta} | {histograma.get(i, 0)} |')
    w('')
    w('## 7. Trazabilidad')
    w('')
    w(f'- SHA-256 del XLSX: `{hashlib.sha256(datos).hexdigest()}`')
    w(f'- SHA-256 del contenido (filas canónicas): `{hash_contenido(filas)}`')
    w('- Regenerar en memoria y comparar: `PYTHONUTF8=1 python scripts/generar_cartillas_sinteticas.py --verificar`')
    w('- Las entradas quedan congeladas tras la revisión del usuario; cualquier cambio posterior lleva un nombre de archivo nuevo.')
    return '\n'.join(l) + '\n'


def producir(codigo):
    m = MODELOS[codigo]
    filas = generar(m)
    datos = libro(filas)
    return m, filas, datos, memoria(m, filas, datos)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--cartilla', action='append', choices=sorted(MODELOS),
                        help='Cartilla a generar; se repite. Por defecto, todas.')
    parser.add_argument('--destino', default=str(REPO / 'tests' / 'data'))
    parser.add_argument('--verificar', action='store_true',
                        help='Regenerar en memoria y comparar con los archivos; no escribe nada.')
    args = parser.parse_args(argv)
    diferencias = 0
    for codigo in args.cartilla or sorted(MODELOS):
        m, filas, datos, texto = producir(codigo)
        carpeta = Path(args.destino) / codigo
        xlsx, md = carpeta / m.archivo, carpeta / 'MEMORIA_DESPIECE.md'
        piezas = sum(f['cantidad'] for f in filas)
        if args.verificar:
            iguales = (xlsx.is_file() and xlsx.read_bytes() == datos and md.is_file()
                       and md.read_text(encoding='utf-8').replace('\r\n', '\n') == texto)
            print(f'{codigo}: {"idéntica" if iguales else "DIFERENTE"} ({len(filas)} filas, {piezas} piezas)')
            diferencias += not iguales
            continue
        carpeta.mkdir(parents=True, exist_ok=True)
        with open(xlsx, 'xb') as salida:
            salida.write(datos)
        with open(md, 'x', encoding='utf-8', newline='\n') as salida:
            salida.write(texto)
        print(f'{xlsx}: {len(filas)} filas, {piezas} piezas, sha256 {hashlib.sha256(datos).hexdigest()}')
    return 1 if diferencias else 0


if __name__ == '__main__':
    sys.exit(main())
