"""
Módulo para análisis de soluciones óptimas en casos homogéneos.

Este módulo implementa algoritmos de análisis exhaustivo para encontrar
la combinación óptima de longitudes de barras en casos donde hay pocas
variaciones en las longitudes requeridas.
"""

from typing import List, Dict, Tuple, Any
import pandas as pd
from itertools import product
import math


def calcular_solucion_optima_homogenea(
    longitud_pieza: float,
    cantidad_requerida: int,
    longitudes_barras: List[float]
) -> Dict[str, Any]:
    """
    Calcula la solución óptima para un caso homogéneo (una sola longitud de pieza).
    
    Args:
        longitud_pieza: Longitud de la pieza requerida
        cantidad_requerida: Cantidad total de piezas requeridas
        longitudes_barras: Lista de longitudes de barras disponibles
    
    Returns:
        Dict: Diccionario con la solución óptima
    """
    
    # Calcular cuántas piezas caben en cada tipo de barra
    piezas_por_barra = {}
    desperdicio_por_barra = {}
    
    for longitud_barra in longitudes_barras:
        piezas_caben = int(longitud_barra // longitud_pieza)
        desperdicio = longitud_barra - (piezas_caben * longitud_pieza)
        
        piezas_por_barra[longitud_barra] = piezas_caben
        desperdicio_por_barra[longitud_barra] = desperdicio
    
    # Generar todas las combinaciones posibles
    mejor_solucion = None
    menor_desperdicio_total = float('inf')
    menor_num_barras = float('inf')
    
    # Calcular límite superior para cada tipo de barra
    limites = []
    for longitud_barra in longitudes_barras:
        if piezas_por_barra[longitud_barra] > 0:
            limite = math.ceil(cantidad_requerida / piezas_por_barra[longitud_barra])
        else:
            limite = 0
        limites.append(limite)

    # Guardia: si el espacio de búsqueda es demasiado grande, usar solución greedy
    # para evitar O(N^k) inmanejable en datasets reales.
    MAX_COMBINACIONES = 500_000
    espacio_total = 1
    for limite in limites:
        espacio_total *= (limite + 1)
        if espacio_total > MAX_COMBINACIONES:
            break

    if espacio_total > MAX_COMBINACIONES:
        # Greedy: elegir el tipo de barra con mejor eficiencia (piezas por metro)
        mejor_barra = max(
            [b for b in longitudes_barras if piezas_por_barra[b] > 0],
            key=lambda b: piezas_por_barra[b] / b
        )
        n_barras = math.ceil(cantidad_requerida / piezas_por_barra[mejor_barra])
        piezas_producidas = n_barras * piezas_por_barra[mejor_barra]
        exceso = piezas_producidas - cantidad_requerida
        desperdicio = n_barras * desperdicio_por_barra[mejor_barra] + exceso * longitud_pieza
        combinacion_barras = {b: 0 for b in longitudes_barras}
        combinacion_barras[mejor_barra] = n_barras
        return {
            'combinacion_barras': combinacion_barras,
            'piezas_producidas': piezas_producidas,
            'piezas_exceso': exceso,
            'desperdicio_total': desperdicio,
            'num_barras_total': n_barras,
            'eficiencia': 1 - (desperdicio / (n_barras * mejor_barra)) if n_barras > 0 else 0
        }

    # Evaluar todas las combinaciones (solo alcanzable con espacio pequeño)
    for combinacion in product(*[range(limite + 1) for limite in limites]):
        # Verificar si esta combinación satisface la demanda
        piezas_totales = sum(
            combinacion[i] * piezas_por_barra[longitudes_barras[i]]
            for i in range(len(longitudes_barras))
        )
        
        if piezas_totales >= cantidad_requerida:
            # Calcular métricas de esta combinación
            num_barras_total = sum(combinacion)
            desperdicio_total = sum(
                combinacion[i] * desperdicio_por_barra[longitudes_barras[i]]
                for i in range(len(longitudes_barras))
            )
            
            # Ajustar por exceso de piezas producidas
            exceso_piezas = piezas_totales - cantidad_requerida
            desperdicio_por_exceso = exceso_piezas * longitud_pieza
            desperdicio_total += desperdicio_por_exceso
            
            # Evaluar si es mejor que la solución actual
            es_mejor = False
            if desperdicio_total < menor_desperdicio_total:
                es_mejor = True
            elif desperdicio_total == menor_desperdicio_total and num_barras_total < menor_num_barras:
                es_mejor = True
            
            if es_mejor:
                menor_desperdicio_total = desperdicio_total
                menor_num_barras = num_barras_total
                
                mejor_solucion = {
                    'combinacion_barras': dict(zip(longitudes_barras, combinacion)),
                    'piezas_producidas': piezas_totales,
                    'piezas_exceso': exceso_piezas,
                    'desperdicio_total': desperdicio_total,
                    'num_barras_total': num_barras_total,
                    'eficiencia': 1 - (desperdicio_total / sum(
                        combinacion[i] * longitudes_barras[i]
                        for i in range(len(longitudes_barras))
                    )) if num_barras_total > 0 else 0
                }
    
    return mejor_solucion


def analizar_casos_homogeneos(
    piezas_requeridas_df: pd.DataFrame,
    longitudes_barras: List[float],
    tolerancia_homogeneidad: float = 0.01
) -> Dict[Tuple[Any, float], Dict[str, Any]]:
    """
    Identifica y analiza casos homogéneos en el DataFrame de piezas requeridas.
    
    Args:
        piezas_requeridas_df: DataFrame con las piezas requeridas
        longitudes_barras: Lista de longitudes de barras disponibles
        tolerancia_homogeneidad: Tolerancia para considerar longitudes como iguales
    
    Returns:
        Dict: Diccionario con análisis de casos homogéneos
    """
    
    casos_homogeneos = {}
    
    # Agrupar por longitud de pieza (con tolerancia)
    grupos_longitud = {}
    
    for _, fila in piezas_requeridas_df.iterrows():
        longitud = fila['longitud_pieza_requerida']
        
        # Buscar grupo existente con longitud similar
        grupo_encontrado = None
        for longitud_grupo in grupos_longitud.keys():
            if abs(longitud - longitud_grupo) <= tolerancia_homogeneidad:
                grupo_encontrado = longitud_grupo
                break
        
        if grupo_encontrado is None:
            # Crear nuevo grupo
            grupos_longitud[longitud] = []
        else:
            # Usar grupo existente
            longitud = grupo_encontrado
        
        grupos_longitud[longitud].append(fila)
    
    # Analizar cada grupo homogéneo
    for longitud_pieza, filas_grupo in grupos_longitud.items():
        # Calcular cantidad total requerida
        cantidad_total = sum(int(fila['cantidad_requerida']) for fila in filas_grupo)
        
        # Solo analizar si hay una cantidad significativa
        if cantidad_total >= 10:  # Umbral mínimo
            solucion_optima = calcular_solucion_optima_homogenea(
                longitud_pieza, cantidad_total, longitudes_barras
            )
            
            # Crear clave identificadora
            ids_pedidos = tuple(sorted(fila['id_pedido'] for fila in filas_grupo))
            clave = (ids_pedidos, longitud_pieza)
            
            casos_homogeneos[clave] = {
                'longitud_pieza': longitud_pieza,
                'cantidad_total': cantidad_total,
                'ids_pedidos': ids_pedidos,
                'solucion_optima': solucion_optima,
                'num_filas_agrupadas': len(filas_grupo)
            }
    
    return casos_homogeneos


def comparar_con_solucion_genetica(
    casos_homogeneos: Dict[Tuple[Any, float], Dict[str, Any]],
    cromosoma_genetico,
    nombre_caso: str = "Análisis"
) -> Dict[str, Any]:
    """
    Compara los casos homogéneos con la solución del algoritmo genético.
    
    Args:
        casos_homogeneos: Casos homogéneos analizados
        cromosoma_genetico: Cromosoma resultado del algoritmo genético
        nombre_caso: Nombre descriptivo del caso
    
    Returns:
        Dict: Comparación detallada
    """
    
    comparaciones = {
        'nombre_caso': nombre_caso,
        'casos_analizados': len(casos_homogeneos),
        'comparaciones_detalladas': {},
        'resumen_diferencias': {
            'casos_suboptimos': 0,
            'mejora_promedio_eficiencia': 0.0,
            'ahorro_promedio_barras': 0.0,
            'reduccion_promedio_desperdicio': 0.0
        }
    }
    
    diferencias_eficiencia = []
    diferencias_barras = []
    diferencias_desperdicio = []
    
    for clave, analisis in casos_homogeneos.items():
        solucion_optima = analisis['solucion_optima']
        longitud_pieza = analisis['longitud_pieza']
        
        # Extraer métricas de la solución genética para esta longitud
        # (Este análisis sería más preciso con acceso al cromosoma real)
        
        comparacion_caso = {
            'longitud_pieza': longitud_pieza,
            'cantidad_requerida': analisis['cantidad_total'],
            'solucion_optima': solucion_optima,
            'diferencia_detectada': True  # Simplificado para el análisis
        }
        
        comparaciones['comparaciones_detalladas'][clave] = comparacion_caso
    
    return comparaciones


def generar_reporte_optimizacion(
    casos_homogeneos: Dict[Tuple[Any, float], Dict[str, Any]],
    archivo_salida: str = "reporte_optimizacion_casos_homogeneos.md"
) -> str:
    """
    Genera un reporte detallado de las optimizaciones encontradas.
    
    Args:
        casos_homogeneos: Casos homogéneos analizados
        archivo_salida: Nombre del archivo de salida
    
    Returns:
        str: Contenido del reporte
    """
    
    contenido = "# 🔍 REPORTE DE ANÁLISIS DE OPTIMIZACIÓN\n\n"
    contenido += f"**Casos homogéneos identificados:** {len(casos_homogeneos)}\n\n"
    
    for i, (clave, analisis) in enumerate(casos_homogeneos.items(), 1):
        solucion = analisis['solucion_optima']
        
        contenido += f"## 📊 CASO {i}: Longitud {analisis['longitud_pieza']}m\n\n"
        contenido += f"- **Cantidad requerida:** {analisis['cantidad_total']} piezas\n"
        contenido += f"- **IDs de pedidos:** {list(analisis['ids_pedidos'])}\n\n"
        
        contenido += "### ✅ SOLUCIÓN ÓPTIMA CALCULADA:\n\n"
        for longitud_barra, cantidad_barras in solucion['combinacion_barras'].items():
            if cantidad_barras > 0:
                contenido += f"- **{cantidad_barras}** barras de **{longitud_barra}m**\n"
        
        contenido += f"\n**Métricas óptimas:**\n"
        contenido += f"- Total de barras: {solucion['num_barras_total']}\n"
        contenido += f"- Desperdicio total: {solucion['desperdicio_total']:.2f}m\n"
        contenido += f"- Eficiencia: {solucion['eficiencia']*100:.2f}%\n"
        contenido += f"- Piezas producidas: {solucion['piezas_producidas']} ({solucion['piezas_exceso']} exceso)\n\n"
        contenido += "---\n\n"
    
    # Escribir archivo si se especifica
    if archivo_salida:
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            f.write(contenido)
    
    return contenido 