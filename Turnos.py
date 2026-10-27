"""Asigna pedidos a riders y calcula sus horarios estimados."""

from datetime import datetime, timedelta

import grafo
from pedidos import conectar


def preparar_tabla(conn):
    """Añade los campos necesarios sin borrar los datos existentes."""
    columnas = {
        fila["name"]
        for fila in conn.execute("PRAGMA table_info(Pedidos)")
    }

    nuevas = [
        "inicio_estimado",
        "recogida_estimada",
        "fin_estimado",
        "ruta_recogida",
        "ruta_entrega",
    ]

    for columna in nuevas:
        if columna not in columnas:
            conn.execute(
                f"ALTER TABLE Pedidos ADD COLUMN {columna} TEXT"
            )


def texto_fecha(fecha):
    return fecha.strftime("%Y-%m-%d %H:%M:%S")


def buscar_ruta(mapa, origen, destino):
    """Devuelve una ruta y su duración; infinito si no es posible."""
    if origen not in mapa or destino not in mapa:
        return [], float("inf")

    return grafo.dijkstra(mapa, origen, destino)


def repartos_sin_solape():
    """
    Asigna los pedidos pendientes sin solapar los viajes de cada rider.

    Es una planificación estimada:
    - Empieza en el momento de ejecutar esta opción.
    - Permite esperar si todos los riders están ocupados.
    - Supone recogida inmediata, sin tiempo de preparación.
    - No marca automáticamente los pedidos como entregados.
    """
    mapa = grafo.construir_grafo()
    ahora = datetime.now().replace(microsecond=0)
    conn = conectar()

    try:
        conn.execute("BEGIN IMMEDIATE")
        preparar_tabla(conn)

        riders = [
            dict(fila)
            for fila in conn.execute(
                "SELECT id, nombre, barrio FROM Riders ORDER BY id"
            )
        ]

        if not riders:
            conn.commit()
            return ["No hay riders registrados."]

        # Situación prevista de cada rider.
        disponibles = {}
        ubicaciones = {}
        avisos = []

        for rider in riders:
            rider_id = rider["id"]
            disponibles[rider_id] = ahora
            ubicaciones[rider_id] = rider["barrio"]

            # Recupera sus repartos activos de ejecuciones anteriores.
            anteriores = conn.execute(
                """
                SELECT p.id, p.fin_estimado, u.barrio AS destino
                FROM Pedidos p
                JOIN Usuarios u ON u.id = p.usuario_id
                WHERE p.rider_id = ?
                  AND p.estado IN ('pendiente', 'asignado', 'en_reparto')
                ORDER BY p.fin_estimado, p.id
                """,
                (rider_id,),
            ).fetchall()

            for anterior in anteriores:
                if not anterior["fin_estimado"]:
                    # No podemos saber cuándo queda libre.
                    disponibles[rider_id] = None
                    avisos.append(
                        f"Rider {rider['nombre']} no disponible para "
                        f"planificar: el pedido #{anterior['id']} "
                        "ya lo tiene asignado, pero no tiene hora de fin."
                    )
                    break

                fin = datetime.fromisoformat(
                    anterior["fin_estimado"]
                )

                disponibles[rider_id] = max(
                    disponibles[rider_id], fin
                )
                ubicaciones[rider_id] = anterior["destino"]

        pendientes = conn.execute(
            """
            SELECT p.id, u.barrio AS destino,
                   (
                       SELECT r.barrio
                       FROM DetallePedido dp
                       JOIN Platos pl ON pl.id = dp.plato_id
                       JOIN Restaurante r
                         ON r.nombre = pl.restaurante
                       WHERE dp.pedido_id = p.id
                       LIMIT 1
                   ) AS origen
            FROM Pedidos p
            JOIN Usuarios u ON u.id = p.usuario_id
            WHERE p.estado = 'pendiente'
              AND p.rider_id IS NULL
            ORDER BY p.id
            """
        ).fetchall()

        for pedido in pendientes:
            ruta_entrega, minutos_entrega = buscar_ruta(
                mapa, pedido["origen"], pedido["destino"]
            )

            if not ruta_entrega:
                avisos.append(
                    f"Pedido #{pedido['id']}: no hay ruta válida "
                    "del restaurante al cliente. Sigue pendiente."
                )
                continue

            mejor = None

            for rider in riders:
                rider_id = rider["id"]

                if disponibles[rider_id] is None:
                    continue

                ruta_recogida, minutos_recogida = buscar_ruta(
                    mapa,
                    ubicaciones[rider_id],
                    pedido["origen"],
                )

                if not ruta_recogida:
                    continue

                inicio = disponibles[rider_id]
                recogida = inicio + timedelta(
                    minutes=minutos_recogida
                )
                fin = recogida + timedelta(
                    minutes=minutos_entrega
                )

                # Elegimos quien pueda entregar antes.
                if mejor is None or fin < mejor["fin"]:
                    mejor = {
                        "rider_id": rider_id,
                        "inicio": inicio,
                        "recogida": recogida,
                        "fin": fin,
                        "ruta_recogida": ruta_recogida,
                    }

            if mejor is None:
                avisos.append(
                    f"Pedido #{pedido['id']}: no hay un rider "
                    "con disponibilidad y ruta conocidas. "
                    "Sigue pendiente."
                )
                continue

            conn.execute(
                """
                UPDATE Pedidos
                SET rider_id = ?,
                    estado = 'asignado',
                    inicio_estimado = ?,
                    recogida_estimada = ?,
                    fin_estimado = ?,
                    ruta_recogida = ?,
                    ruta_entrega = ?
                WHERE id = ?
                """,
                (
                    mejor["rider_id"],
                    texto_fecha(mejor["inicio"]),
                    texto_fecha(mejor["recogida"]),
                    texto_fecha(mejor["fin"]),
                    " -> ".join(mejor["ruta_recogida"]),
                    " -> ".join(ruta_entrega),
                    pedido["id"],
                ),
            )

            # Su siguiente reparto empezará al terminar este,
            # desde la ubicación donde entrega al cliente.
            rider_id = mejor["rider_id"]
            disponibles[rider_id] = mejor["fin"]
            ubicaciones[rider_id] = pedido["destino"]

        resultados = mostrar_plan(conn)
        conn.commit()

        return resultados + avisos or [
            "No hay pedidos pendientes ni repartos activos planificados."
        ]

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def mostrar_plan(conn):
    """Devuelve los textos que app.py mostrará en la opción 7."""
    filas = conn.execute(
        """
        SELECT p.*, r.nombre AS rider, u.nombre AS usuario
        FROM Pedidos p
        JOIN Riders r ON r.id = p.rider_id
        JOIN Usuarios u ON u.id = p.usuario_id
        WHERE p.estado IN ('asignado', 'en_reparto')
          AND p.inicio_estimado IS NOT NULL
          AND p.recogida_estimada IS NOT NULL
          AND p.fin_estimado IS NOT NULL
        ORDER BY p.inicio_estimado, p.id
        """
    ).fetchall()

    resultados = []

    for fila in filas:
        inicio = datetime.fromisoformat(fila["inicio_estimado"])
        recogida = datetime.fromisoformat(fila["recogida_estimada"])
        fin = datetime.fromisoformat(fila["fin_estimado"])

        hasta_restaurante = (recogida - inicio).total_seconds() / 60
        hasta_cliente = (fin - recogida).total_seconds() / 60
        total = (fin - inicio).total_seconds() / 60

        resultados.append(
            f"\nPedido #{fila['id']} | Cliente: {fila['usuario']}\n"
            f"    Rider: {fila['rider']} (ID {fila['rider_id']})\n"
            f"    Estado: {fila['estado']}\n"
            f"    Inicio estimado: {inicio:%d/%m/%Y %H:%M:%S}\n"
            f"    Hasta restaurante: {hasta_restaurante:g} min\n"
            f"    Recogida estimada: {recogida:%d/%m/%Y %H:%M:%S}\n"
            f"    Restaurante -> cliente: {hasta_cliente:g} min\n"
            f"    Duración del reparto: {total:g} min\n"
            f"    Entrega estimada: {fin:%d/%m/%Y %H:%M:%S}\n"
            f"    Ruta de recogida: {fila['ruta_recogida']}\n"
            f"    Ruta de entrega: {fila['ruta_entrega']}"
        )

    return resultados


if __name__ == "__main__":
    for resultado in repartos_sin_solape():
        print(resultado)