"""
=============================================================================
RUTA NICARAO S.A. - Lógica Matemática y Algorítmica (funciones.py)
=============================================================================
"""

import heapq
from datetime import datetime
from typing import Dict, List, Tuple, Any

from entidades import (
    Paquete, Alerta,
    ESTADO_PENDIENTE, ESTADO_ASIGNADO, ESTADO_EN_CAMINO,
    ESTADO_ENTREGADO, ESTADO_INCIDENCIA, ESTADO_CANCELADO
)

TRANSICIONES_PERMITIDAS = {
    ESTADO_PENDIENTE: [ESTADO_ASIGNADO, ESTADO_EN_CAMINO, ESTADO_INCIDENCIA, ESTADO_CANCELADO],
    ESTADO_ASIGNADO: [ESTADO_PENDIENTE, ESTADO_EN_CAMINO, ESTADO_INCIDENCIA, ESTADO_CANCELADO],
    ESTADO_EN_CAMINO: [ESTADO_ENTREGADO, ESTADO_INCIDENCIA, ESTADO_CANCELADO],
    ESTADO_INCIDENCIA: [ESTADO_ASIGNADO, ESTADO_EN_CAMINO, ESTADO_ENTREGADO, ESTADO_CANCELADO],
    ESTADO_ENTREGADO: [], ESTADO_CANCELADO: []
}

def es_transicion_valida(estado_actual: str, nuevo_estado: str) -> bool:
    if estado_actual == nuevo_estado: return True
    return nuevo_estado in TRANSICIONES_PERMITIDAS.get(estado_actual, [])

def dijkstra(grafo: Dict[str, List[Tuple[str, float]]], inicio: str, destino: str) -> Tuple[List[str], float, List[Dict[str, Any]]]:
    if inicio not in grafo or destino not in grafo: raise KeyError("Zona no encontrada.")
    if inicio == destino: return [inicio], 0.0, []

    distancias = {nodo: float('inf') for nodo in grafo}
    distancias[inicio] = 0.0
    predecesores = {nodo: None for nodo in grafo}
    cola = [(0.0, inicio)]
    visitados = set()

    while cola:
        dist_actual, nodo_actual = heapq.heappop(cola)
        if nodo_actual in visitados: continue
        visitados.add(nodo_actual)
        if nodo_actual == destino: break

        for vecino, peso in grafo.get(nodo_actual, []):
            if vecino in visitados: continue
            nueva_dist = dist_actual + peso
            if nueva_dist < distancias[vecino]:
                distancias[vecino] = nueva_dist
                predecesores[vecino] = nodo_actual
                heapq.heappush(cola, (nueva_dist, vecino))

    if distancias[destino] == float('inf'): raise ValueError("Sin ruta viable.")

    ruta, actual = [], destino
    while actual is not None:
        ruta.append(actual); actual = predecesores[actual]
    ruta.reverse()

    tramos = []
    for i in range(len(ruta) - 1):
        u, v = ruta[i], ruta[i + 1]
        tramos.append({"desde": u, "hacia": v, "minutos": next((p for vec, p in grafo[u] if vec == v), 0.0)})
    return ruta, distancias[destino], tramos

PROPOSICIONES_INFO = {
    "P": "El paquete se encuentra en estado 'Pendiente'.",
    "Q": "El paquete tiene una 'Incidencia'.",
    "R": "Cuenta con repartidor asignado.",
    "S": "Supera las 24 horas transcurridas.",
    "T": "El paquete está cerrado."
}

def evaluar_proposiciones_paquete(p: Paquete, ahora: datetime) -> Dict[str, bool]:
    horas = 0.0
    try:
        horas = (ahora - datetime.strptime(p.fecha_registro, "%Y-%m-%d %H:%M:%S")).total_seconds() / 3600.0
    except: pass
    return {"P": p.estado == ESTADO_PENDIENTE, "Q": p.estado == ESTADO_INCIDENCIA, "R": p.repartidor_id is not None, "S": horas > 24.0, "T": p.estado in [ESTADO_ENTREGADO, ESTADO_CANCELADO]}

def generar_alertas_logicas(paquetes: List[Paquete]) -> List[Alerta]:
    ahora = datetime.now(); alertas = []
    for p in paquetes:
        vals = evaluar_proposiciones_paquete(p, ahora)
        P, Q, R, S, T = vals["P"], vals["Q"], vals["R"], vals["S"], vals["T"]
        if T: continue
        comercio = p.comercio_nombre or f"Comercio #{p.comercio_id}"
        if P and S: alertas.append(Alerta(p.codigo, comercio, "DEMORA_CRITICA (P ∧ S)", "Crítica", f"El paquete {p.codigo} lleva más de 24h sin despacharse.", vals, PROPOSICIONES_INFO))
        if Q and (not T): alertas.append(Alerta(p.codigo, comercio, "INCIDENCIA_ACTIVA (Q ∧ ¬T)", "Crítica", f"Incidencia activa en paquete {p.codigo}.", vals, PROPOSICIONES_INFO))
    return alertas