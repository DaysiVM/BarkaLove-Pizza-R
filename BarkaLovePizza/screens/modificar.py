from datetime import datetime
import flet as ft
from utils.pedidos import cargar_pedidos, pedidos_modificables

def pantalla_modificar(page, masa, salsa, checkbox_ingredientes, mostrar_pantalla):
    rojo = "#E63946"
    lista = []
    for p in cargar_pedidos():
        hora_pedido = datetime.fromisoformat(p["hora"])
        if p in pedidos_modificables():
            lista.append(ft.TextButton(
                f"Modificar Orden #{p['orden']}",
                on_click=lambda e, pid=p['orden']: mostrar_pantalla('registro', editar_orden=pid)
            ))
        else:
            lista.append(ft.Text(f"Orden #{p['orden']} (No modificable)", color="grey"))

    return ft.Column(
        [
            ft.Text("Modificar pedido 🛠️", size=24, color=rojo, weight="bold"),
            *lista,
            ft.TextButton("⬅ Volver", on_click=lambda _: mostrar_pantalla("inicio")),
        ],
        spacing=10,
        horizontal_alignment="center"
    )

def modificar(page, id_orden, masa, salsa, checkbox_ingredientes, mostrar_pantalla):
    pedidos = cargar_pedidos()
    pedido = next((p for p in pedidos if p["orden"] == id_orden), None)
    if not pedido:
        page.snack_bar = ft.SnackBar(ft.Text("Pedido no encontrado.", color="white"), bgcolor="#E63946")
        page.snack_bar.open = True
        page.update()
        return

    masa.value = pedido["masa"]
    salsa.value = pedido["salsa"]
    for c in checkbox_ingredientes:
        c.value = c.label in pedido["ingredientes"]

    mostrar_pantalla("registro")
