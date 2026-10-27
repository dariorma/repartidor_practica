"""Creación de pedidos: restaurantes situados en los nodos de Madrid, sin control de saldo."""

import random
import sqlite3
from pathlib import Path

from grafo import NODOS

DB = Path(__file__).with_name('RiderExpress.db')
PLAZAS = set(NODOS)


def conectar():
    conn = sqlite3.connect(DB)
    conn.execute('PRAGMA foreign_keys = ON')
    conn.row_factory = sqlite3.Row
    return conn


def crear_pedido(usuario_id, productos):
    """Crea un pedido pendiente y devuelve su ID.

    productos: lista de pares (plato_id, cantidad).
    Los platos de un pedido han de proceder de una sola plaza.
    No se consulta ni se descuenta el saldo del usuario.
    """
    if not productos:
        raise ValueError('Debes seleccionar al menos un plato')

    cantidades = {}
    for plato_id, cantidad in productos:
        if type(cantidad) is not int or cantidad <= 0:
            raise ValueError('La cantidad debe ser un entero positivo')
        cantidades[plato_id] = cantidades.get(plato_id, 0) + cantidad

    conn = conectar()
    try:
        conn.execute('BEGIN IMMEDIATE')
        usuario = conn.execute(
            'SELECT nombre, barrio FROM Usuarios WHERE id = ?', (usuario_id,)
        ).fetchone()
        if usuario is None:
            raise ValueError(f'No existe el usuario {usuario_id}')
        if usuario['barrio'] not in PLAZAS:
            raise ValueError('La dirección del usuario debe ser uno de los nodos del grafo')

        plaza_recogida = None
        detalles = []
        total = 0.0

        for plato_id, cantidad in cantidades.items():
            plato = conn.execute(
                '''SELECT p.nombre, p.restaurante, p.precio, r.barrio AS ubicacion
                   FROM Platos p
                   LEFT JOIN Restaurante r ON r.nombre = p.restaurante
                   WHERE p.id = ?''',
                (plato_id,),
            ).fetchone()
            if plato is None:
                raise ValueError(f'No existe el plato con ID {plato_id}')

            # El restaurante es literalmente una de las plazas del grafo.
            plaza = plato['restaurante']
            if plaza not in PLAZAS or plato['ubicacion'] != plaza:
                raise ValueError(f'El plato {plato_id} no está asociado a una plaza válida')

            if plaza_recogida is None:
                plaza_recogida = plaza
            elif plaza_recogida != plaza:
                raise ValueError('Un pedido debe recoger todos los platos en la misma plaza')

            detalles.append((plato_id, cantidad, plato['precio']))
            total += plato['precio'] * cantidad

        total = round(total, 2)
        cursor = conn.execute(
            '''INSERT INTO Pedidos (usuario_id, rider_id, estado, total)
               VALUES (?, NULL, 'pendiente', ?)''',
            (usuario_id, total),
        )
        pedido_id = cursor.lastrowid

        for plato_id, cantidad, precio in detalles:
            conn.execute(
                '''INSERT INTO DetallePedido
                   (pedido_id, plato_id, cantidad, precio_unitario)
                   VALUES (?, ?, ?, ?)''',
                (pedido_id, plato_id, cantidad, precio),
            )

        conn.commit()
        return pedido_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def mostrar_usuarios():
    conn = conectar()
    try:
        print('\nUSUARIOS:')
        for u in conn.execute('SELECT id, nombre, barrio FROM Usuarios ORDER BY id'):
            print(f"  {u['id']}. {u['nombre']} | entrega: {u['barrio']}")
    finally:
        conn.close()


def restaurantes_con_platos():
    conn = conectar()
    try:
        nombres = {fila['restaurante'] for fila in conn.execute(
            '''SELECT DISTINCT p.restaurante
               FROM Platos p JOIN Restaurante r ON r.nombre = p.restaurante
               WHERE r.nombre = r.barrio'''
        )}
        return [plaza for plaza in NODOS if plaza in nombres]
    finally:
        conn.close()


def mostrar_platos(plaza):
    conn = conectar()
    try:
        print(f'\nPLATOS disponibles en {plaza}:')
        for p in conn.execute(
            'SELECT id, nombre, precio FROM Platos WHERE restaurante = ? ORDER BY id',
            (plaza,),
        ):
            print(f"  {p['id']}. {p['nombre']} | {p['precio']:.2f} €")
    finally:
        conn.close()



def mostrar_pedidos():
    conn = conectar()
    try:
        print('\nPEDIDOS:')
        for p in conn.execute(
            '''SELECT p.id, u.nombre AS usuario, u.barrio AS destino,
                      p.estado, p.total, p.rider_id,
                      (SELECT pl.restaurante
                       FROM DetallePedido dp
                       JOIN Platos pl ON pl.id = dp.plato_id
                       WHERE dp.pedido_id = p.id LIMIT 1) AS origen
               FROM Pedidos p JOIN Usuarios u ON u.id = p.usuario_id
               ORDER BY p.id'''
        ):
            print(f"  #{p['id']} | {p['origen']} -> {p['destino']} | "
                  f"{p['usuario']} | {p['estado']} | "
                  f"{p['total']:.2f} € | rider={p['rider_id']}")
    finally:
        conn.close()


