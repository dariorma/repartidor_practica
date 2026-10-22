import heapq

# Nodos: intersecciones principales de Madrid
NODOS = [
    "Puerta del Sol", "Plaza de Callao", "Plaza de España", "Moncloa",
    "Glorieta de Quevedo", "Glorieta de Bilbao", "Alonso Martínez",
    "Plaza de Colón", "Plaza de Cibeles", "Puerta de Alcalá",
    "Plaza de Neptuno", "Atocha", "Glorieta de Embajadores",
    "Puerta de Toledo", "Plaza Elíptica", "Plaza de Legazpi",
    "Príncipe Pío", "Gregorio Marañón", "Nuevos Ministerios",
    "Plaza de Lima", "Plaza de Castilla", "Manuel Becerra", "Las Ventas",
]

# Aristas: (nodo A, nodo B, tiempo medio en minutos). Son de doble sentido.
ARISTAS = [
    ("Plaza de Castilla", "Plaza de Lima", 5),
    ("Plaza de Lima", "Nuevos Ministerios", 2),
    ("Nuevos Ministerios", "Gregorio Marañón", 3),
    ("Gregorio Marañón", "Plaza de Colón", 4),
    ("Plaza de Colón", "Plaza de Cibeles", 3),
    ("Plaza de Cibeles", "Plaza de Neptuno", 2),
    ("Plaza de Neptuno", "Atocha", 3),
    ("Plaza de Cibeles", "Puerta de Alcalá", 2),
    ("Puerta de Alcalá", "Plaza de Colón", 3),
    ("Puerta de Alcalá", "Manuel Becerra", 5),
    ("Manuel Becerra", "Las Ventas", 4),
    ("Plaza de Cibeles", "Puerta del Sol", 5),
    ("Puerta del Sol", "Plaza de Callao", 3),
    ("Plaza de Callao", "Plaza de España", 4),
    ("Puerta del Sol", "Plaza de Neptuno", 4),
    ("Plaza de Callao", "Glorieta de Bilbao", 5),
    ("Glorieta de Bilbao", "Alonso Martínez", 3),
    ("Alonso Martínez", "Plaza de Colón", 4),
    ("Alonso Martínez", "Gregorio Marañón", 4),
    ("Glorieta de Bilbao", "Glorieta de Quevedo", 3),
    ("Glorieta de Quevedo", "Moncloa", 5),
    ("Moncloa", "Plaza de España", 5),
    ("Moncloa", "Nuevos Ministerios", 8),
    ("Plaza de España", "Príncipe Pío", 4),
    ("Príncipe Pío", "Puerta de Toledo", 6),
    ("Puerta de Toledo", "Puerta del Sol", 7),
    ("Puerta de Toledo", "Glorieta de Embajadores", 5),
    ("Glorieta de Embajadores", "Atocha", 4),
    ("Glorieta de Embajadores", "Plaza de Legazpi", 5),
    ("Atocha", "Plaza de Legazpi", 5),
    ("Plaza de Legazpi", "Plaza Elíptica", 5),
    ("Plaza Elíptica", "Puerta de Toledo", 8),
]


def construir_grafo():
    """Devuelve el grafo como { nodo: {vecino: minutos} }"""
    grafo = {nodo: {} for nodo in NODOS}
    for a, b, minutos in ARISTAS:
        grafo[a][b] = minutos
        grafo[b][a] = minutos
    return grafo


def dijkstra(grafo, origen, destino):
    """Devuelve (camino, tiempo_total) del camino más rápido."""
    tiempos = {nodo: float("inf") for nodo in grafo}
    previo = {nodo: None for nodo in grafo}
    tiempos[origen] = 0
    cola = [(0, origen)]

    while cola:
        tiempo, nodo = heapq.heappop(cola)
        if nodo == destino:
            break
        if tiempo > tiempos[nodo]:
            continue
        for vecino, minutos in grafo[nodo].items():
            nuevo = tiempo + minutos
            if nuevo < tiempos[vecino]:
                tiempos[vecino] = nuevo
                previo[vecino] = nodo
                heapq.heappush(cola, (nuevo, vecino))

    if tiempos[destino] == float("inf"):
        return [], float("inf")

    camino = []
    nodo = destino
    while nodo is not None:
        camino.append(nodo)
        nodo = previo[nodo]
    camino.reverse()
    return camino, tiempos[destino]


if __name__ == "__main__":
    grafo = construir_grafo()
    print(grafo)
    camino, total = dijkstra(grafo, "Plaza Elíptica", "Plaza de Castilla")
    print(f"Tiempo total: {total} min")
    print(" -> ".join(camino))