import importlib
import os

# Las bases de datos se abren con rutas relativas ('rutas.db'):
# así funciona aunque lancemos app.py desde otra carpeta.
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import pedidos
import grafo


# Piezas opcionales (las de los compañeros que aún pueden no estar listas)

def _importar_opcional(*nombres):
    """Intenta importar un módulo por varios nombres posibles; None si falla."""
    for nombre in nombres:
        try:
            return importlib.import_module(nombre)
        except Exception:  # no existe, o tiene errores todavía
            continue
    return None


turno = _importar_opcional("turno", "Turnos")


def _funcion(modulo, nombre):
    """Devuelve modulo.nombre si existe, o None."""
    return getattr(modulo, nombre, None) if modulo else None


# Entrada de datos (con validación: el usuario se equivoca, la app no se cae)

def pedir_entero(mensaje, minimo=None, maximo=None, vacio_ok=False):
    """Pide un entero. Si vacio_ok y pulsa Enter, devuelve None."""
    while True:
        texto = input(mensaje).strip()
        if texto == "" and vacio_ok:
            return None
        try:
            valor = int(texto)
        except ValueError:
            print("  ⚠ Escribe un número entero.")
            continue
        if minimo is not None and valor < minimo:
            print(f"  ⚠ Debe ser como mínimo {minimo}.")
            continue
        if maximo is not None and valor > maximo:
            print(f"  ⚠ Debe ser como máximo {maximo}.")
            continue
        return valor


def elegir_de_lista(titulo, opciones):
    """Muestra una lista numerada y devuelve la opción elegida."""
    print(f"\n{titulo}")
    for i, opcion in enumerate(opciones, start=1):
        print(f"  {i}. {opcion}")
    return opciones[pedir_entero("Elige un número: ", 1, len(opciones)) - 1]


def pausa():
    input("\n(Enter para volver al menú) ")


# Opciones del menú

def ver_usuarios():
    pedidos.mostrar_usuarios()


def ver_carta():
    plazas = pedidos.plazas_con_platos()
    if not plazas:
        print("\nTodavía no hay platos dados de alta en ninguna plaza.")
        return
    plaza = elegir_de_lista("¿De qué plaza quieres ver la carta?", plazas)
    pedidos.mostrar_platos(plaza)


def hacer_pedido():
    plazas = pedidos.plazas_con_platos()
    if not plazas:
        print("\nNo se puede pedir: todavía no hay platos dados de alta.")
        return

    pedidos.mostrar_usuarios()
    usuario_id = pedir_entero("\nID del usuario que pide: ", 1)

    plaza = elegir_de_lista("¿En qué plaza quieres pedir?", plazas)
    pedidos.mostrar_platos(plaza)

    # Un pedido recoge todos sus platos en la misma plaza.
    productos = []
    print("\nAñade platos (deja el ID vacío para terminar).")
    while True:
        plato_id = pedir_entero("  ID del plato: ", 1, vacio_ok=True)
        if plato_id is None:
            break
        cantidad = pedir_entero("  Cantidad: ", 1)
        productos.append((plato_id, cantidad))

    if not productos:
        print("\nPedido cancelado: no has elegido ningún plato.")
        return

    try:
        pedido_id = pedidos.crear_pedido(usuario_id, productos)
    except ValueError as error:      # reglas de negocio de pedidos.py
        print(f"\n✗ No se pudo crear el pedido: {error}")
    except Exception as error:       # cualquier otro fallo (BD bloqueada...)
        print(f"\n✗ Error inesperado al crear el pedido: {error}")
    else:
        print(f"\n✓ Pedido #{pedido_id} creado (estado: pendiente).")


def ver_pedidos():
    pedidos.mostrar_pedidos()


def _cargar_grafo():
    """Carga el grafo; si rutas.db está vacía o rota, lo cuenta sin romper."""
    try:
        return grafo.construir_grafo()
    except Exception as error:
        print(f"\n✗ No se pudo cargar el mapa de rutas: {error!r}")
        print("  Revisa que rutas.db exista y que los nombres de sus plazas")
        print("  coincidan con los de grafo.NODOS.")
        return None


def calcular_ruta():
    mapa = _cargar_grafo()
    if mapa is None:
        return

    origen = elegir_de_lista("Plaza de ORIGEN:", grafo.NODOS)
    destino = elegir_de_lista("Plaza de DESTINO:", grafo.NODOS)

    camino, minutos = grafo.dijkstra(mapa, origen, destino)
    if not camino:
        print(f"\nNo hay ruta entre {origen} y {destino}.")
        return
    print(f"\nRuta más rápida: {minutos} min")
    print("  " + " -> ".join(camino))


def rider_mas_cercano():
    """Pendiente de compañero: grafo.rider_mas_cercano(mapa, plaza)."""
    buscar = _funcion(grafo, "rider_mas_cercano")
    if buscar is None:
        print("\n(Pendiente) Aún no existe rider_mas_cercano en grafo.py / rutas.py.")
        return
    mapa = _cargar_grafo()
    if mapa is None:
        return

    plaza = elegir_de_lista("¿A qué plaza debe llegar el rider (recogida)?", grafo.NODOS)
    resultado = buscar(mapa, plaza)
    if not resultado:
        print("\nNo hay ningún rider disponible que pueda llegar.")
        return
    # Contrato esperado: (id_rider, nombre, camino, minutos)
    rider_id, nombre, camino, minutos = resultado
    print(f"\nRider más cercano: {nombre} (#{rider_id}) a {minutos} min")
    print("  " + " -> ".join(camino))


def ver_turno():
    """Pendiente de compañero: turno.repartos_sin_solape()."""
    planificar = _funcion(turno, "repartos_sin_solape")
    if planificar is None:
        print("\n(Pendiente) turno.py aún no ofrece repartos_sin_solape().")
        return
    elegidos = planificar()
    print("\nRepartos que caben en el turno sin solaparse:")
    for reparto in elegidos:
        print(f"  - {reparto}")


# Menú principal

MENU = [
    ("Ver usuarios",                    ver_usuarios),
    ("Ver carta de un plaza",          ver_carta),
    ("Hacer un pedido",                 hacer_pedido),
    ("Ver pedidos",                     ver_pedidos),
    ("Calcular ruta más rápida",        calcular_ruta),
    ("Buscar rider más cercano",        rider_mas_cercano),
    ("Planificar turno de repartos",    ver_turno),
]


def main():
    print("=" * 40)
    print("        RIDEREXPRESS - Madrid")
    print("=" * 40)

    while True:
        print("\nMENÚ")
        for i, (texto, _) in enumerate(MENU, start=1):
            print(f"  {i}. {texto}")
        print("  0. Salir")

        opcion = pedir_entero("\nOpción: ", 0, len(MENU))
        if opcion == 0:
            print("\n¡Hasta pronto!")
            break

        try:
            MENU[opcion - 1][1]()
        except KeyboardInterrupt:
            print("\n(Operación cancelada)")
        except Exception as error:   # última red: el menú nunca se cae
            print(f"\n✗ Algo ha fallado: {error!r}")
        pausa()


if __name__ == "__main__":
    main()