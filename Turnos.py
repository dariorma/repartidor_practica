"""Turnos: el voraz de repartos sin solapar.

Un rider solo puede hacer un reparto a la vez. Cada pedido pendiente es un
reparto con un intervalo:

    inicio = fecha del pedido
    fin    = inicio + minutos del camino más rápido (Dijkstra) restaurante -> usuario

Algoritmo voraz (selección de actividades): ordenar por hora de FIN y quedarse
con cada reparto que empiece cuando ya ha terminado el último elegido.
Así se maximiza el número de repartos que caben en el turno.
"""

from contextlib import closing
from datetime import datetime, timedelta

import grafo
from pedidos import conectar


def _cargar_repartos():
    """Lee los pedidos pendientes y calcula su intervalo (inicio, fin)."""
    mapa = grafo.construir_grafo()

    with closing(conectar()) as conn:
        filas = conn.execute(
            '''SELECT p.id, p.fecha, u.barrio AS destino,
                      (SELECT pl.restaurante
                       FROM DetallePedido dp
                       JOIN Platos pl ON pl.id = dp.plato_id
                       WHERE dp.pedido_id = p.id LIMIT 1) AS origen
               FROM Pedidos p
               JOIN Usuarios u ON u.id = p.usuario_id
               WHERE p.estado = 'pendiente' '''
        ).fetchall()

    repartos = []
    for f in filas:
        if f['origen'] not in mapa or f['destino'] not in mapa:
            continue  # plaza que no está en el grafo: no se puede calcular
        _, minutos = grafo.dijkstra(mapa, f['origen'], f['destino'])
        if minutos == float('inf'):
            continue  # sin ruta posible
        inicio = datetime.fromisoformat(f['fecha'])
        repartos.append({
            'pedido': f['id'],
            'origen': f['origen'],
            'destino': f['destino'],
            'inicio': inicio,
            'fin': inicio + timedelta(minutes=minutos),
        })
    return repartos


def elegir_sin_solape(repartos):
    """El voraz: ordena por fin y elige los que no se solapan."""
    elegidos, fin_ultimo = [], datetime.min
    for r in sorted(repartos, key=lambda r: r['fin']):
        if r['inicio'] >= fin_ultimo:
            elegidos.append(r)
            fin_ultimo = r['fin']
    return elegidos


def repartos_sin_solape():
    """Lo que usa app.py: lista de textos, uno por reparto elegido."""
    elegidos = elegir_sin_solape(_cargar_repartos())
    return [
        f"Pedido #{r['pedido']}: {r['origen']} -> {r['destino']} "
        f"({r['inicio']:%H:%M} - {r['fin']:%H:%M})"
        for r in elegidos
    ]


if __name__ == "__main__":
    for linea in repartos_sin_solape():
        print(linea)