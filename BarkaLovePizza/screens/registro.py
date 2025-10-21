import flet as ft
import random
from datetime import datetime
from utils.pedidos import guardar_pedido, actualizar_pedido, obtener_pedido

def pantalla_registro(page, masa, salsa, checkbox_ingredientes, ingredientes, mostrar_pantalla, pedido_enviado_ref, pedido_finalizado_ref, current_order_ref, editar_orden=None):
    rojo = "#E63946"
    amarillo = "#FFD93D"

    def guardar_pedido_click(e):
        if not masa.value or not salsa.value:
            page.snack_bar = ft.SnackBar(ft.Text("Selecciona masa y salsa antes de continuar.", color="white"), bgcolor=rojo)
            page.snack_bar.open = True
            page.update()
            return
        ingredientes_seleccionados = [c.label for c in checkbox_ingredientes if c.value]
        if editar_orden is None:
            numero_orden = random.randint(1000, 9999)
            pedido = {
                "orden": numero_orden,
                "masa": masa.value,
                "salsa": salsa.value,
                "ingredientes": ingredientes_seleccionados,
                "hora": datetime.now().isoformat(),
            }
            guardar_pedido(pedido)
            pedido_enviado_ref[0] = True
            pedido_finalizado_ref[0] = False
            current_order_ref[0] = numero_orden
            # Navegar a la pantalla de preparación a través del dispatcher principal
            mostrar_pantalla('preparar', numero_orden=numero_orden)
        else:
            # actualizar pedido existente
            pedido = {
                "orden": editar_orden,
                "masa": masa.value,
                "salsa": salsa.value,
                "ingredientes": ingredientes_seleccionados,
            }
            try:
                actualizar_pedido(pedido)
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"Error al actualizar: {ex}", color="white"), bgcolor=rojo)
                page.snack_bar.open = True
                page.update()
                return
            # volver a inicio o a preparar según flujo
            mostrar_pantalla("inicio")

    controles_ingredientes = [
        ft.Row([ft.Image(src=i["img"], width=35, height=35), checkbox_ingredientes[idx]]) 
        for idx, i in enumerate(ingredientes)
    ]

    # Si estamos editando, cargar datos del pedido y rellenar controles
    if editar_orden is not None:
        existente = obtener_pedido(editar_orden)
        if existente:
            masa.value = existente.get('masa')
            salsa.value = existente.get('salsa')
            for c in checkbox_ingredientes:
                c.value = c.label in existente.get('ingredientes', [])
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Pedido a editar no encontrado.", color="white"), bgcolor=rojo)
            page.snack_bar.open = True
            page.update()

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
