import sqlite3
from contextlib import closing
with closing(get_conn()) as conn:
    with closing(conn.cursor()) as cursor:
        repartos = conn.execute(
            "SELECT barrio FROM Usuarios"
        ).fetchall()
        
elegidos, fin_ultimo = [], "00:00"
for r in repartos:
    if r["inicio"] >= fin_ultimo:
        elegidos.append(r["barrio"])
        fin_ultimo = r["fin"]
print(elegidos)
