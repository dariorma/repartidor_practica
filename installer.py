import sqlite3
conexion = sqlite3.connect('RiderExpress.db')
cursor = conexion.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS Riders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehiculo TEXT NOT NULL
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Platos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    restaurante TEXT NOT NULL,
    tipo_categoria TEXT NOT NULL,
    precio REAL NOT NULL
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    saldo REAL NOT NULL
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Categoria (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_categoria TEXT NOT NULL
)''')