"""
Módulo para la inicialización de población del algoritmo genético.

Este módulo implementa diferentes estrategias para crear la población inicial
del algoritmo genético, incluyendo métodos heurísticos, aleatorios e híbridos.
"""

import random
import copy
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd

from .chromosome import Cromosoma, Patron
from .chromosome_utils import (
    crear_patron_corte,
    validar_cromosoma_completitud,
    calcular_sumario_piezas_en_cromosoma
)
from .optimal_analyzer import analizar_casos_homogeneos, calcular_solucion_optima_homogenea


# ─────────────────────────────────────────────────────────────────────────────
# Helpers internos
# ─────────────────────────────────────────────────────────────────────────────

def _construir_barras_para_usar(barras_disponibles, desperdicios_disponibles, preferir_grandes=True):
    """Construye la lista de barras ordenada, desperdicios primero."""
    barras = []
    for d in desperdicios_disponibles:
        barras.append({'longitud': d['longitud'], 'tipo': 'desperdicio'})
    for b in sorted(barras_disponibles, key=lambda x: x['longitud'], reverse=preferir_grandes):
        barras.append({'longitud': b['longitud'], 'tipo': 'estandar'})
    return barras


def _abrir_barra(barras_para_usar, longitud_pieza):
    """Abre la barra más pequeña que puede contener al menos una pieza de `longitud_pieza`."""
    for barra in barras_para_usar:
        if barra['longitud'] >= longitud_pieza:
            return barra
    return None


def _colocar_en_barra(barra_abierta, id_pedido, longitud, cantidad):
    """Coloca `cantidad` piezas en una barra abierta, consolidando entradas del mismo id_pedido."""
    entry = next(
        (p for p in barra_abierta['piezas_cortadas'] if p['id_pedido'] == id_pedido),
        None
    )
    if entry:
        entry['cantidad_pieza_en_patron'] += cantidad
    else:
        barra_abierta['piezas_cortadas'].append({
            'id_pedido': id_pedido,
            'longitud_pieza': longitud,
            'cantidad_pieza_en_patron': cantidad
        })
    barra_abierta['longitud_restante'] = round(barra_abierta['longitud_restante'] - longitud * cantidad, 6)


def _patrones_desde_barras(barras_abiertas):
    """Convierte la lista de barras abiertas a objetos Patron."""
    return [
        Patron(
            origen_barra_longitud=b['origen_barra_longitud'],
            origen_barra_tipo=b['origen_barra_tipo'],
            piezas_cortadas=b['piezas_cortadas']
        )
        for b in barras_abiertas
    ]


# ─────────────────────────────────────────────────────────────────────────────
# Heurísticas de generación — versiones con cantidades agrupadas
# ─────────────────────────────────────────────────────────────────────────────

def generar_individuo_heuristico_ffd(
    piezas_requeridas_df: pd.DataFrame,
    barras_disponibles: List[Dict[str, Any]],
    desperdicios_disponibles: List[Dict[str, Any]]
) -> Cromosoma:
    """
    Genera un individuo usando First Fit Decreasing (FFD) con representación agrupada.

    Procesa tipos de pieza de mayor a menor longitud. Para cada tipo, llena primero
    las barras ya abiertas (first fit) y luego abre nuevas barras. Opera sobre
    cantidades agrupadas — nunca expande a ítems individuales.
    """
    # Ordenar tipos de pieza por longitud descendente
    ordenes = sorted(
        piezas_requeridas_df.to_dict('records'),
        key=lambda x: x['longitud_pieza_requerida'],
        reverse=True
    )

    barras_para_usar = _construir_barras_para_usar(barras_disponibles, desperdicios_disponibles)
    barras_abiertas = []

    for orden in ordenes:
        id_pedido = orden['id_pedido']
        longitud = float(orden['longitud_pieza_requerida'])
        restante = int(orden['cantidad_requerida'])

        # Fase 1: First Fit — llenar barras ya abiertas de mayor a menor espacio
        for barra_abierta in barras_abiertas:
            if restante <= 0:
                break
            espacio = barra_abierta['longitud_restante']
            if espacio >= longitud:
                caben = int(espacio // longitud)
                a_colocar = min(caben, restante)
                _colocar_en_barra(barra_abierta, id_pedido, longitud, a_colocar)
                restante -= a_colocar

        # Fase 2: Abrir nuevas barras para la demanda restante
        while restante > 0:
            barra_sel = _abrir_barra(barras_para_usar, longitud)
            if barra_sel is None:
                break
            caben = int(barra_sel['longitud'] // longitud)
            a_colocar = min(caben, restante)
            nueva = {
                'origen_barra_longitud': barra_sel['longitud'],
                'origen_barra_tipo': barra_sel['tipo'],
                'piezas_cortadas': [],
                'longitud_restante': float(barra_sel['longitud'])
            }
            _colocar_en_barra(nueva, id_pedido, longitud, a_colocar)
            barras_abiertas.append(nueva)
            restante -= a_colocar
            if barra_sel['tipo'] == 'desperdicio':
                barras_para_usar.remove(barra_sel)

    return Cromosoma(_patrones_desde_barras(barras_abiertas))


def generar_individuo_heuristico_bfd(
    piezas_requeridas_df: pd.DataFrame,
    barras_disponibles: List[Dict[str, Any]],
    desperdicios_disponibles: List[Dict[str, Any]]
) -> Cromosoma:
    """
    Genera un individuo usando Best Fit Decreasing (BFD) con representación agrupada.

    Para cada tipo de pieza (mayor a menor), ordena las barras abiertas por espacio
    restante ascendente (tightest fit) y llena cuantas piezas quepan antes de abrir
    nuevas barras. Opera sobre cantidades agrupadas — nunca expande a ítems individuales.
    """
    ordenes = sorted(
        piezas_requeridas_df.to_dict('records'),
        key=lambda x: x['longitud_pieza_requerida'],
        reverse=True
    )

    barras_para_usar = _construir_barras_para_usar(barras_disponibles, desperdicios_disponibles)
    barras_abiertas = []

    for orden in ordenes:
        id_pedido = orden['id_pedido']
        longitud = float(orden['longitud_pieza_requerida'])
        restante = int(orden['cantidad_requerida'])

        # Fase 1: Best Fit — barras con menos espacio sobrante primero (tightest fit)
        candidatas = sorted(
            [b for b in barras_abiertas if b['longitud_restante'] >= longitud],
            key=lambda b: b['longitud_restante']
        )
        for barra_abierta in candidatas:
            if restante <= 0:
                break
            espacio = barra_abierta['longitud_restante']
            caben = int(espacio // longitud)
            a_colocar = min(caben, restante)
            _colocar_en_barra(barra_abierta, id_pedido, longitud, a_colocar)
            restante -= a_colocar

        # Fase 2: Abrir nuevas barras para la demanda restante
        while restante > 0:
            barra_sel = _abrir_barra(barras_para_usar, longitud)
            if barra_sel is None:
                break
            caben = int(barra_sel['longitud'] // longitud)
            a_colocar = min(caben, restante)
            nueva = {
                'origen_barra_longitud': barra_sel['longitud'],
                'origen_barra_tipo': barra_sel['tipo'],
                'piezas_cortadas': [],
                'longitud_restante': float(barra_sel['longitud'])
            }
            _colocar_en_barra(nueva, id_pedido, longitud, a_colocar)
            barras_abiertas.append(nueva)
            restante -= a_colocar
            if barra_sel['tipo'] == 'desperdicio':
                barras_para_usar.remove(barra_sel)

    return Cromosoma(_patrones_desde_barras(barras_abiertas))


def generar_individuo_aleatorio_con_reparacion(
    piezas_requeridas_df: pd.DataFrame,
    barras_disponibles: List[Dict[str, Any]],
    desperdicios_disponibles: List[Dict[str, Any]]
) -> Cromosoma:
    """
    Genera un individuo diverso mezclando el orden de los tipos de pieza antes de aplicar BFD.

    El orden aleatorio de los tipos produce distintas soluciones en cada llamada sin
    expandir las cantidades a ítems individuales.
    """
    filas = piezas_requeridas_df.to_dict('records')
    random.shuffle(filas)
    piezas_shuffled = pd.DataFrame(filas)
    return generar_individuo_heuristico_bfd(
        piezas_shuffled,
        barras_disponibles,
        desperdicios_disponibles
    )


def reparar_cromosoma(
    cromosoma: Cromosoma,
    piezas_requeridas_df: pd.DataFrame,
    barras_disponibles: List[Dict[str, Any]],
    desperdicios_disponibles: List[Dict[str, Any]]
) -> Cromosoma:
    """
    Repara un cromosoma regenerándolo con BFD sobre los requerimientos originales.

    Dado que BFD ya opera sobre cantidades agrupadas, no se necesita extraer ni
    re-expandir las piezas del cromosoma — se trabaja directamente desde el DataFrame
    de requerimientos.
    """
    return generar_individuo_heuristico_bfd(
        piezas_requeridas_df,
        barras_disponibles,
        desperdicios_disponibles
    )


def generar_individuo_con_analisis_optimo(
    piezas_requeridas_df: pd.DataFrame,
    barras_disponibles: List[Dict[str, Any]],
    desperdicios_disponibles: List[Dict[str, Any]]
) -> Cromosoma:
    """
    Genera un individuo usando análisis óptimo para casos homogéneos y FFD para el resto.
    """
    longitudes_barras = [barra['longitud'] for barra in barras_disponibles]

    casos_homogeneos = analizar_casos_homogeneos(
        piezas_requeridas_df, longitudes_barras, tolerancia_homogeneidad=0.01
    )

    patrones = []
    piezas_procesadas = set()

    for clave, analisis in casos_homogeneos.items():
        ids_pedidos, longitud_pieza = clave
        solucion_optima = analisis['solucion_optima']

        for longitud_barra, cantidad_barras in solucion_optima['combinacion_barras'].items():
            if cantidad_barras > 0:
                piezas_por_barra = int(longitud_barra // longitud_pieza)

                for _ in range(int(cantidad_barras)):
                    piezas_cortadas = []
                    piezas_añadidas = 0

                    for id_pedido in ids_pedidos:
                        if piezas_añadidas >= piezas_por_barra:
                            break

                        fila = piezas_requeridas_df[piezas_requeridas_df['id_pedido'] == id_pedido].iloc[0]
                        cantidad_requerida = int(fila['cantidad_requerida'])

                        piezas_a_añadir = min(
                            cantidad_requerida,
                            piezas_por_barra - piezas_añadidas
                        )

                        if piezas_a_añadir > 0:
                            piezas_cortadas.append({
                                'id_pedido': id_pedido,
                                'longitud_pieza': longitud_pieza,
                                'cantidad_pieza_en_patron': piezas_a_añadir
                            })
                            piezas_añadidas += piezas_a_añadir

                    if piezas_cortadas:
                        patron = Patron(
                            origen_barra_longitud=longitud_barra,
                            origen_barra_tipo='estandar',
                            piezas_cortadas=piezas_cortadas
                        )
                        patrones.append(patron)

        for id_pedido in ids_pedidos:
            piezas_procesadas.add(id_pedido)

    piezas_restantes = piezas_requeridas_df[
        ~piezas_requeridas_df['id_pedido'].isin(piezas_procesadas)
    ]

    if not piezas_restantes.empty:
        cromosoma_restante = generar_individuo_heuristico_ffd(
            piezas_restantes, barras_disponibles, desperdicios_disponibles
        )
        patrones.extend(cromosoma_restante.patrones)

    return Cromosoma(patrones)


def inicializar_poblacion(
    tamaño_poblacion: int,
    piezas_requeridas_df: pd.DataFrame,
    barras_estandar_disponibles: List[Dict[str, Any]],
    desperdicios_reutilizables_previos: List[Dict[str, Any]],
    estrategia_inicializacion: str = 'hibrida',
    config_ga: Optional[Dict[str, Any]] = None
) -> List[Cromosoma]:
    """
    Inicializa una población de cromosomas usando diferentes estrategias.
    """
    if config_ga is None:
        config_ga = {}

    proporcion_heuristicos = config_ga.get('proporcion_heuristicos', 0.6)
    poblacion = []

    if estrategia_inicializacion == 'heuristica':
        for i in range(tamaño_poblacion):
            if i % 2 == 0:
                individuo = generar_individuo_heuristico_ffd(
                    piezas_requeridas_df,
                    barras_estandar_disponibles,
                    desperdicios_reutilizables_previos
                )
            else:
                individuo = generar_individuo_heuristico_bfd(
                    piezas_requeridas_df,
                    barras_estandar_disponibles,
                    desperdicios_reutilizables_previos
                )
            poblacion.append(individuo)

    elif estrategia_inicializacion == 'aleatoria':
        for _ in range(tamaño_poblacion):
            individuo = generar_individuo_aleatorio_con_reparacion(
                piezas_requeridas_df,
                barras_estandar_disponibles,
                desperdicios_reutilizables_previos
            )
            poblacion.append(individuo)

    elif estrategia_inicializacion == 'hibrida':
        num_optimos = min(tamaño_poblacion // 4, 3)
        num_heuristicos = int((tamaño_poblacion - num_optimos) * proporcion_heuristicos)
        num_aleatorios = tamaño_poblacion - num_optimos - num_heuristicos

        for _ in range(num_optimos):
            individuo = generar_individuo_con_analisis_optimo(
                piezas_requeridas_df,
                barras_estandar_disponibles,
                desperdicios_reutilizables_previos
            )
            poblacion.append(individuo)

        for i in range(num_heuristicos):
            if i % 2 == 0:
                individuo = generar_individuo_heuristico_ffd(
                    piezas_requeridas_df,
                    barras_estandar_disponibles,
                    desperdicios_reutilizables_previos
                )
            else:
                individuo = generar_individuo_heuristico_bfd(
                    piezas_requeridas_df,
                    barras_estandar_disponibles,
                    desperdicios_reutilizables_previos
                )
            poblacion.append(individuo)

        for _ in range(num_aleatorios):
            individuo = generar_individuo_aleatorio_con_reparacion(
                piezas_requeridas_df,
                barras_estandar_disponibles,
                desperdicios_reutilizables_previos
            )
            poblacion.append(individuo)

    else:
        raise ValueError(f"Estrategia de inicialización no reconocida: {estrategia_inicializacion}")

    random.shuffle(poblacion)
    return poblacion
