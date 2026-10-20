
import sqlite3

conexion = sqlite3.connect('RiderExpress.db')
conexion.execute("PRAGMA foreign_keys = ON")
cursor = conexion.cursor()

# TABLA RIDERS
cursor.execute('''CREATE TABLE IF NOT EXISTS Riders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    vehiculo TEXT NOT NULL,
    barrio TEXT
)''')

# TABLA PLATOS
cursor.execute('''CREATE TABLE IF NOT EXISTS Platos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    restaurante TEXT NOT NULL,
    tipo_categoria TEXT NOT NULL,
    precio REAL NOT NULL
)''')

# TABLA USUARIOS
cursor.execute('''CREATE TABLE IF NOT EXISTS Usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    saldo REAL NOT NULL,
    barrio TEXT
)''')

# TABLA CATEGORIA
cursor.execute('''CREATE TABLE IF NOT EXISTS Categoria (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_categoria TEXT NOT NULL
)''')

# TABLA RESTAURANTE
cursor.execute('''CREATE TABLE IF NOT EXISTS Restaurante (
    nombre TEXT PRIMARY KEY,
    barrio TEXT NOT NULL
)''')

# TABLA PEDIDOS
cursor.execute('''CREATE TABLE IF NOT EXISTS Pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    rider_id INTEGER,
    fecha TEXT DEFAULT CURRENT_TIMESTAMP,
    estado TEXT DEFAULT 'pendiente',
    total REAL NOT NULL DEFAULT 0,
    FOREIGN KEY (usuario_id) REFERENCES Usuarios(id),
    FOREIGN KEY (rider_id) REFERENCES Riders(id)
)''')

# TABLA DETALLE PEDIDO
cursor.execute('''CREATE TABLE IF NOT EXISTS DetallePedido (
    pedido_id INTEGER NOT NULL,
    plato_id INTEGER NOT NULL,
    cantidad INTEGER NOT NULL CHECK (cantidad > 0),
    precio_unitario REAL NOT NULL,
    PRIMARY KEY (pedido_id, plato_id),
    FOREIGN KEY (pedido_id) REFERENCES Pedidos(id),
    FOREIGN KEY (plato_id) REFERENCES Platos(id)
)''')

# TABLA TRAMOS (GRAFO PARA DIJKSTRA)
cursor.execute('''CREATE TABLE IF NOT EXISTS Tramo (
    origen TEXT NOT NULL,
    destino TEXT NOT NULL,
    minutos INTEGER NOT NULL CHECK (minutos > 0),
    PRIMARY KEY (origen, destino)
)''')

# ACTUALIZAR TABLAS ANTIGUAS SI YA EXISTEN
# CREATE TABLE IF NOT EXISTS no añade columnas nuevas.

def agregar_columna(tabla, columna, tipo):
    cursor.execute(f"PRAGMA table_info({tabla})")
    columnas = [fila[1] for fila in cursor.fetchall()]

    if columna not in columnas:
        cursor.execute(
            f"ALTER TABLE {tabla} ADD COLUMN {columna} {tipo}"
        )

agregar_columna("Riders", "nombre", "TEXT")
agregar_columna("Riders", "barrio", "TEXT")
agregar_columna("Usuarios", "nombre", "TEXT")
agregar_columna("Usuarios", "barrio", "TEXT")

# GUARDAR CAMBIOS
conexion.commit()

print("Base de datos creada y actualizada correctamente")

# MOSTRAR LAS TABLAS
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")

for tabla in cursor.fetchall():
    print(tabla[0])

conexion.close()
