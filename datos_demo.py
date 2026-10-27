"""Datos de ejemplo para probar RiderExpress.

Uso (en la carpeta del proyecto):
    python db.py            # crea las tablas (si no existen)
    python datos_demo.py    # mete los datos de ejemplo
    python app.py

Si la base de datos ya tiene datos, no hace nada.
Para borrarlo todo y volver a cargar:  python datos_demo.py --borrar
"""

import sqlite3
import sys
from datetime import date

import pedidos
from pedidos import DB

# Los restaurantes SON plazas del grafo (nombre = barrio = nodo de grafo.NODOS)
RESTAURANTES = ["Puerta del Sol", "Plaza de Callao", "Moncloa", "Atocha",
                "Plaza de Cibeles", "Plaza de Colón", "Glorieta de Bilbao"]

CATEGORIAS = ["Bocadillos", "Arroces", "Tapas", "Hamburguesas", "Postres", "Pizzas"]

# (nombre, restaurante, categoría, precio)
PLATOS = [
    ("Bocata de calamares", "Puerta del Sol",   "Bocadillos",   6.50),
    ("Tortilla de patata",  "Puerta del Sol",   "Tapas",        4.00),
    ("Churros con chocolate", "Puerta del Sol", "Postres",      3.50),
    ("Cocido madrileño",    "Plaza de Callao",  "Tapas",       13.00),
    ("Croquetas caseras",   "Plaza de Callao",  "Tapas",        7.00),
    ("Paella valenciana",   "Moncloa",          "Arroces",     12.00),
    ("Arroz negro",         "Moncloa",          "Arroces",     13.50),
    ("Hamburguesa doble",   "Atocha",           "Hamburguesas", 9.90),
    ("Patatas bravas",      "Atocha",           "Tapas",        5.00),
    ("Pizza margarita",     "Plaza de Cibeles", "Pizzas",       8.50),
    ("Pizza cuatro quesos", "Plaza de Cibeles", "Pizzas",      10.00),
    ("Tarta de queso",      "Plaza de Colón",   "Postres",      5.50),
    ("Ensaladilla rusa",    "Plaza de Colón",   "Tapas",        6.00),
    ("Bocata de jamón",     "Glorieta de Bilbao", "Bocadillos", 5.50),
]

# (nombre, saldo, barrio donde recibe el pedido)
USUARIOS = [
    ("Ana",    50.0, "Plaza de Castilla"),
    ("Luis",   35.0, "Las Ventas"),
    ("Marta",  80.0, "Plaza Elíptica"),
    ("Pablo",  20.0, "Nuevos Ministerios"),
    ("Lucía",  60.0, "Príncipe Pío"),
]

# (nombre, vehículo, barrio donde está)
RIDERS = [
    ("Carlos", "moto",      "Puerta del Sol"),
    ("Sara",   "bici",      "Atocha"),
    ("Iván",   "patinete",  "Moncloa"),
    ("Nuria",  "moto",      "Manuel Becerra"),
]

# (usuario, [(plato, cantidad), ...], hora de inicio)  -> el voraz de turnos
# elegirá los que no se solapen. Duración = tiempo de ruta restaurante->usuario.
PEDIDOS = [
    ("Ana",   [("Bocata de calamares", 2), ("Tortilla de patata", 1)], "10:00"),
    ("Luis",  [("Paella valenciana", 1)],                              "10:05"),
    ("Marta", [("Hamburguesa doble", 2), ("Patatas bravas", 1)],       "10:40"),
    ("Pablo", [("Pizza margarita", 1)],                                "10:45"),
    ("Lucía", [("Tarta de queso", 2)],                                 "11:30"),
]


def tabla_con_datos(conn, tabla):
    return conn.execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()[0] > 0


def main():
    conn = sqlite3.connect(DB)
    conn.execute("PRAGMA foreign_keys = ON")

    try:
        conn.execute("SELECT 1 FROM Pedidos LIMIT 1")
    except sqlite3.OperationalError:
        print("Faltan las tablas. Ejecuta antes:  python db.py")
        return

    if "--borrar" in sys.argv:
        for tabla in ("DetallePedido", "Pedidos", "Platos", "Restaurante",
                      "Categoria", "Usuarios", "Riders"):
            conn.execute(f"DELETE FROM {tabla}")
        conn.execute("DELETE FROM sqlite_sequence")
        conn.commit()
        print("Base de datos vaciada.")
    elif any(tabla_con_datos(conn, t) for t in ("Usuarios", "Platos", "Riders")):
        print("La base de datos ya tiene datos; no toco nada.")
        print("Usa  python datos_demo.py --borrar  para empezar de cero.")
        return

    conn.executemany("INSERT INTO Restaurante (nombre, barrio) VALUES (?, ?)",
                     [(r, r) for r in RESTAURANTES])
    conn.executemany("INSERT INTO Categoria (tipo_categoria) VALUES (?)",
                     [(c,) for c in CATEGORIAS])
    conn.executemany(
        "INSERT INTO Platos (nombre, restaurante, tipo_categoria, precio) VALUES (?, ?, ?, ?)",
        [(n, r, c, p) for n, r, c, p in PLATOS])
    conn.executemany("INSERT INTO Usuarios (nombre, saldo, barrio) VALUES (?, ?, ?)", USUARIOS)
    conn.executemany("INSERT INTO Riders (nombre, vehiculo, barrio) VALUES (?, ?, ?)", RIDERS)
    conn.commit()

    # Los pedidos se crean con crear_pedido (así se prueban también sus reglas)
    # y luego se les pone una hora fija para que el voraz tenga qué elegir.
    hoy = date.today().isoformat()
    for nombre_usuario, lineas, hora in PEDIDOS:
        usuario_id = conn.execute("SELECT id FROM Usuarios WHERE nombre = ?",
                                  (nombre_usuario,)).fetchone()[0]
        productos = []
        for nombre_plato, cantidad in lineas:
            plato_id = conn.execute("SELECT id FROM Platos WHERE nombre = ?",
                                    (nombre_plato,)).fetchone()[0]
            productos.append((plato_id, cantidad))

        pedido_id = pedidos.crear_pedido(usuario_id, productos)
        conn.execute("UPDATE Pedidos SET fecha = ? WHERE id = ?",
                     (f"{hoy} {hora}:00", pedido_id))
        conn.commit()

    print(f"Datos de ejemplo cargados: {len(RESTAURANTES)} restaurantes, "
          f"{len(PLATOS)} platos, {len(USUARIOS)} usuarios, "
          f"{len(RIDERS)} riders y {len(PEDIDOS)} pedidos.")
    conn.close()


if __name__ == "__main__":
    main()