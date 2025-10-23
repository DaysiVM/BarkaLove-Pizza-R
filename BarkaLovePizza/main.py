import flet as ft
from screens.registro import pantalla_registro
from screens.modificar import pantalla_modificar
from flet import Dropdown, Checkbox
from screens.inicio import pantalla_inicio

ingredientes_data = [
    {"label": "Queso extra", "img": "queso.png"},
    {"label": "Pepperoni", "img": "pepperoni.png"},
    {"label": "Champiñones", "img": "champi.png"},
    {"label": "Aceitunas", "img": "aceitunas.png"},
    {"label": "Pimientos", "img": "pimientos.png"},
]

def main(page: ft.Page):
    page.title = "Barka Love Pizza 🍕"
    page.bgcolor = "#FFF8E1"
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"
    page.padding = 20

    # Estado compartido entre pantallas
    pedido_enviado_ref = [False]
    pedido_finalizado_ref = [False]
    current_order_ref = [None]

    # Elementos compartidos
    masa = Dropdown(
        label="Tipo de masa",
        options=[ft.dropdown.Option("Delgada"), ft.dropdown.Option("Gruesa")],
        width=250
    )
    salsa = Dropdown(
        label="Salsa",
        options=[ft.dropdown.Option("Tomate"), ft.dropdown.Option("BBQ"), ft.dropdown.Option("Blanca")],
        width=250
    )
    checkbox_ingredientes = [Checkbox(label=i["label"]) for i in ingredientes_data]

    # Función para mostrar pantallas
    def mostrar_pantalla(nombre, **kwargs):
        page.clean()
        if nombre == "inicio":
            page.add(pantalla_inicio(pedido_enviado_ref[0], pedido_finalizado_ref[0], mostrar_pantalla))
        elif nombre == "registro":
            # permitir pasar editar_orden via kwargs
            editar_orden = kwargs.get('editar_orden')
            page.add(pantalla_registro(
                page, masa, salsa, checkbox_ingredientes, ingredientes_data,
                mostrar_pantalla, pedido_enviado_ref, pedido_finalizado_ref, current_order_ref, editar_orden=editar_orden
            ))
        elif nombre == "preparar":
            # Mostrar la pantalla de preparación usando el wrapper que maneja el loop
            numero_orden = kwargs.get('numero_orden')
            if numero_orden is not None:
                from screens.preparar import mostrar_carga_pizza
                # llamar al wrapper y pasar los refs para que se actualicen cuando termine
                mostrar_carga_pizza(page, numero_orden, mostrar_pantalla, pedido_finalizado_ref, current_order_ref)
        elif nombre == "modificar":
            from screens.modificar import pantalla_modificar
            page.add(pantalla_modificar(
                page, masa, salsa, checkbox_ingredientes, mostrar_pantalla,
                id_orden=kwargs.get("id_orden")
            ))

        elif nombre == "ver_orden":
            from screens.ver_orden import pantalla_ver_orden
            page.add(pantalla_ver_orden(
                page, kwargs.get("numero_orden"), mostrar_pantalla
            ))
        elif nombre == "admin_login":
            from screens.admin_login import pantalla_admin_login
            page.add(pantalla_admin_login(page, mostrar_pantalla))

        elif nombre == "admin":
            from screens.admin import pantalla_admin
            page.add(pantalla_admin(page, mostrar_pantalla))

        # (para más adelante cuando creemos estas pantallas)
        elif nombre == "admin_recetas":
            from screens.admin_recetas import pantalla_admin_recetas
            page.add(pantalla_admin_recetas(page, mostrar_pantalla))
        page.update()

    mostrar_pantalla("inicio")

ft.app(target=main, assets_dir="assets")
