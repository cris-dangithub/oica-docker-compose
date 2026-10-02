"""Masas nominales NSR-10 y aviso no bloqueante de discrepancia (spec 001, FR-018).

Valores de la NSR-10, Título C, Tabla C.3.5.3-2, p. C-47 (verificada 2026-10-02, ficha
REF-NSR10-TABLA de docs/tesis-doc/Referencias.md); coinciden con la hoja TablaBarras de
Planilla_Cartilla.xlsx. La tolerancia del 1 % es una decisión de diseño de OICA, no un
requisito normativo.
"""
from decimal import Decimal

MASA_NOMINAL_KG_M = {'#2': '0.250', '#3': '0.560', '#4': '0.994', '#5': '1.552', '#6': '2.235',
                     '#7': '3.042', '#8': '3.973', '#9': '5.060', '#10': '6.404', '#11': '7.907',
                     '#14': '11.380', '#18': '20.240'}
TOLERANCIA = Decimal('0.01')
ROTULO = 'masa nominal NSR-10 (Título C, Tabla C.3.5.3-2)'


def avisos(problem):
    """Diámetros cuya masa por metro difiere más de 1 % de la nominal, o sin valor nominal.

    Solo informa: el plan se genera igual. Se compara en Decimal para que el límite exacto
    (1 %) no avise por error de coma flotante.
    """
    resultado = []
    for diam in sorted(problem['densities'], key=lambda d: int(d.lstrip('#'))):
        cartilla = Decimal(problem['densities'][diam])
        nominal = MASA_NOMINAL_KG_M.get(diam)
        if nominal is None:
            resultado.append({'diametro': diam, 'masa_cartilla_kg_m': float(cartilla),
                              'masa_nominal_kg_m': None, 'diferencia_relativa_pct': None,
                              'estado': 'no_contrastado'})
            continue
        nominal = Decimal(nominal)
        diferencia = (cartilla - nominal) / nominal
        if abs(diferencia) > TOLERANCIA:
            resultado.append({'diametro': diam, 'masa_cartilla_kg_m': float(cartilla),
                              'masa_nominal_kg_m': float(nominal),
                              'diferencia_relativa_pct': float(100 * diferencia), 'estado': 'aviso'})
    return resultado
