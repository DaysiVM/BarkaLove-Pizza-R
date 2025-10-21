import flet as ft
import random
from datetime import datetime
from utils.pedidos import guardar_pedido

def pantalla_registro(page, masa, salsa, checkbox_ingredientes, ingredientes, mostrar_pantalla, pedido_enviado_ref):
    rojo = "#E63946"
    amarillo = "#FFD93D"

    def guardar_pedido_click(e):
        if not masa.value or not salsa.value:
            page.snack_bar = ft.SnackBar(ft.Text("Selecciona masa y salsa antes de continuar.", color="white"), bgcolor=rojo)
            page.snack_bar.open = True
            page.update()
            return

        numero_orden = random.randint(1000, 9999)
        pedido = {
            "orden": numero_orden,
            "masa": masa.value,
            "salsa": salsa.value,
            "ingredientes": [c.label for c in checkbox_ingredientes if c.value],
            "hora": datetime.now().isoformat(),
        }
        guardar_pedido(pedido)
        pedido_enviado_ref[0] = True
        from screens.preparar import mostrar_carga_pizza
        mostrar_carga_pizza(page, numero_orden, mostrar_pantalla)

    controles_ingredientes = [
        ft.Row([ft.Image(src=i["img"], width=35, height=35), checkbox_ingredientes[idx]]) 
        for idx, i in enumerate(ingredientes)
    ]

    return ft.Column(
        [
            ft.Text("Registrar pedido 🍕", size=24, color=rojo, weight="bold"),
            ft.Image(src="pizza_base.png", width=200, height=200),
            masa,
            salsa,
            ft.Column(controles_ingredientes, spacing=10),
            ft.ElevatedButton("Enviar pizza", bgcolor=amarillo, color="black", on_click=guardar_pedido_click),
            ft.TextButton("⬅ Volver", on_click=lambda _: mostrar_pantalla("inicio")),
        ],
        spacing=10,
        horizontal_alignment="center"
    )
