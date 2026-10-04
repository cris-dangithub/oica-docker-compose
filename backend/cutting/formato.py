"""Formato de las cifras que lee el usuario (spec 002, enmiendas 2 y 3: FR-032, FR-033; research R-20).

Punto decimal, sin separador de miles (como la plantilla USCO de la tesis) y unidades separadas por
un espacio, sin depender de `locale`.
Lo usan los artefactos (`report.py`) y los mensajes de dominio (`analysis.py`); los datos para
máquinas (API, JSON, celdas numéricas del Excel) conservan números nativos (FR-035).
"""

NO_DISPONIBLE = 'no disponible'


def numero(valor, decimales=2):
    """«152039.57»; `None` → «no disponible»."""
    if valor is None:
        return NO_DISPONIBLE
    return f'{valor:.{decimales}f}'


def con_signo(valor, decimales=2):
    """Diferencias con signo explícito: «+1.26» o «-1.14»."""
    return numero(valor, decimales) if valor is None or valor <= 0 else '+' + numero(valor, decimales)


def metros(valor):
    """Longitud legible, hasta tres decimales y sin ceros finales: «4.2 m»."""
    return f'{valor:.3f}'.rstrip('0').rstrip('.') + ' m'
