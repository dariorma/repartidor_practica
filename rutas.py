import sqlite3

conn = sqlite3.connect('rutas.db')

cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS Rutas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    origen TEXT NOT NULL,
    destino TEXT NOT NULL,
    tiempo INTEGER NOT NULL
)''')

cursor.execute('''Insert INTO Rutas (origen, destino, tiempo) VALUES
    ('Plaza de Castilla', 'Plaza de Lima', 5),
    ('Plaza de Lima', 'Nuevos Ministerios', 2),
    ('Nuevos Ministerios', 'Gregorio Marañón', 3),
    ('Gregorio Marañón', 'Plaza de Colón', 4),
    ('Plaza de Colón', 'Plaza de Cibeles', 3),
    ('Plaza de Cibeles', 'Plaza de Neptuno', 2),
    ('Plaza de Neptuno', 'Atocha', 3),
    ('Plaza de Cibeles', 'Puerta de Alcalá', 2),
    ('Puerta de Alcalá', 'Plaza de Colón', 3),
    ('Puerta de Alcalá', 'Manuel Becerra', 5),
    ('Manuel Becerra', 'Las Ventas', 4),
    ('Plaza de Cibeles', 'Puerta del Sol', 5),
    ('Puerta del Sol', 'Plaza de Callao', 3),
    ('Plaza de Callao', 'Plaza de España', 4),
    ('Puerta del Sol', 'Plaza de Neptuno', 4),
    ('Plaza de Callao', 'Glorieta de Bilbao', 5),
    ('Glorieta de Bilbao', 'Alonso Martínez', 3),
    ('Alonso Martínez', 'Plaza de Colón', 4),
    ('Alonso Martínez', 'Gregorio Marañón', 4),
    ('Glorieta de Bilbao', 'Glorieta de Quevedo', 3),
    ('Glorieta de Quevedo', 'Moncloa', 5),
    ('Moncloa', 'Plaza de España', 5),
    ('Moncloa', 'Nuevos Ministerios', 8),
    ('Plaza de España', 'Príncipe Pío', 4),
    ('Príncipe Pío', 'Puerta de Toledo', 6),
    ('Puerta de Toledo', 'Puerta del Sol', 7),
    ('Puerta de Toledo', 'Glorieta de Embajadores', 5),
    ('Glorieta de Embajadores', 'Atocha', 4),
    ('Glorieta de Embajadores', 'Plaza de Legazpi)', 5),
    ('Atocha', 'Plaza.de Legazpi)', 5),
    ('Plaza.de Legazpi)', 'Plaza Elíptica)', 5),
    ('Plaza Elíptica)', 'Puerta.de Toledo)', 8)
''')




try:


    cursor.execute("""
        UPDATE Rutas
        SET
            origen = TRIM(REPLACE(REPLACE(origen, '.', ' '), ')', '')),
            destino = TRIM(REPLACE(REPLACE(destino, '.', ' '), ')', ''))
        WHERE
            origen LIKE '%)%'
            OR destino LIKE '%)%'
            OR origen LIKE '%.%'
            OR destino LIKE '%.%';
    """)

    conn.commit()

    print("Rutas corregidas correctamente.")

except sqlite3.OperationalError as e:
    print("Error en la base de datos:", e)

finally:
    if 'conn' in locals():
        conn.close()

conn.commit()
conn.close()