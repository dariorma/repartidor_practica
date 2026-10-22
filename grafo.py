import heapq
import sqlite3

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

def construir_grafo():
    """Devuelve el grafo como { nodo: {vecino: minutos} }"""
    grafo = {nodo: {} for nodo in NODOS}
    conn = sqlite3.connect('rutas.db')
    cursor = conn.cursor()
    cursor.execute("SELECT origen, destino, tiempo FROM Rutas")
    for a, b, minutos in cursor.fetchall():
        grafo[a][b] = minutos
        grafo[b][a] = minutos
    conn.commit()
    conn.close()
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