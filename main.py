# main.py
import flet as ft
from flet import Dropdown, Checkbox
from screens.registro import pantalla_registro
from screens.modificar import pantalla_modificar
from screens.inicio import pantalla_inicio

# Si tienes otros screens, los cargamos bajo demanda en el router


ingredientes_data = [
    {"label": "Queso extra",   "img": "queso.png"},
    {"label": "Pepperoni",     "img": "pepperoni.png"},
    {"label": "Champiñones",   "img": "champi.png"},
    {"label": "Aceitunas",     "img": "aceitunas.png"},
    {"label": "Pimientos",     "img": "pimientos.png"},
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

    # Elementos compartidos (se reusan para consistencia visual)
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

    # Router simple
    def mostrar_pantalla(nombre, **kwargs):
        page.clean()

        if nombre == "inicio":
            page.add(pantalla_inicio(pedido_enviado_ref[0], pedido_finalizado_ref[0], mostrar_pantalla))

        elif nombre == "registro":
            editar_orden = kwargs.get("editar_orden")
            page.add(
                pantalla_registro(
                    page, masa, salsa, checkbox_ingredientes, ingredientes_data,
                    mostrar_pantalla, pedido_enviado_ref, pedido_finalizado_ref, current_order_ref,
                    editar_orden=editar_orden
                )
            )

        elif nombre == "preparar":
            numero_orden = kwargs.get("numero_orden")
            if numero_orden is not None:
                # Import lazy para no bloquear
                from screens.preparar import mostrar_carga_pizza
                mostrar_carga_pizza(page, numero_orden, mostrar_pantalla, pedido_finalizado_ref, current_order_ref)

        elif nombre == "modificar":
            page.add(
                pantalla_modificar(
                    page, masa, salsa, checkbox_ingredientes, mostrar_pantalla,
                    id_orden=kwargs.get("id_orden")
                )
            )

        elif nombre == "ver_orden":
            from screens.ver_orden import pantalla_ver_orden
            page.add(pantalla_ver_orden(page, kwargs.get("numero_orden"), mostrar_pantalla))

        elif nombre == "admin_login":
            from screens.admin_login import pantalla_admin_login
            page.add(pantalla_admin_login(page, mostrar_pantalla))

        elif nombre == "admin":
            from screens.admin import pantalla_admin
            page.add(pantalla_admin(page, mostrar_pantalla))

        elif nombre == "admin_recetas":
            from screens.admin_recetas import pantalla_admin_recetas
            page.add(pantalla_admin_recetas(page, mostrar_pantalla))

        elif nombre == "admin_indicadores":
            from screens.admin_indicadores import pantalla_admin_indicadores
            page.add(pantalla_admin_indicadores(page, mostrar_pantalla))

        elif nombre == "admin_respaldo":
            from screens.admin_respaldo import pantalla_admin_respaldo
            page.add(pantalla_admin_respaldo(page, mostrar_pantalla))

        elif nombre == "errores_kpi":
            from screens.errores_kpi import pantalla_errores_kpi
            page.add(pantalla_errores_kpi(page, mostrar_pantalla))

        elif nombre == "manual_backup":
            from screens.manual_backup import pantalla_manual_backup
            page.add(pantalla_manual_backup(page, mostrar_pantalla))

        elif nombre == "respaldo_detalle":
            from screens.respaldo_detalle import pantalla_respaldo_detalle
            page.add(pantalla_respaldo_detalle(page, kwargs.get("backup"), mostrar_pantalla))

        elif nombre == "respaldo_proceso":
            from screens.respaldo_proceso import pantalla_respaldo_proceso
            page.add(pantalla_respaldo_proceso(page, mostrar_pantalla))

        elif nombre == "automation_config":
            from screens.automation_config import pantalla_automation_config
            page.add(pantalla_automation_config(page, mostrar_pantalla))

        elif nombre == "programar_mantenimiento":
            from screens.programar_mantenimiento import pantalla_programar_mantenimiento
            page.add(pantalla_programar_mantenimiento(page, mostrar_pantalla, title=kwargs.get("title")))
        elif nombre == "programar_mantenimiento_confirm":
            from screens.programar_mantenimiento import pantalla_programar_mantenimiento_confirm
            page.add(pantalla_programar_mantenimiento_confirm(page, mostrar_pantalla, title=kwargs.get("title"), date=kwargs.get("date"), time=kwargs.get("time")))

        elif nombre == "kds":
            from screens.kds import pantalla_kds
            page.add(pantalla_kds(page, mostrar_pantalla))

        elif nombre == "manuales_usuario":
            from screens.manuales_usuario import pantalla_manuales_usuario
            page.add(pantalla_manuales_usuario(page, mostrar_pantalla))

        elif nombre == "videos_tutoriales":
            from screens.videos_tutoriales import pantalla_videos_tutoriales
            page.add(pantalla_videos_tutoriales(page, mostrar_pantalla))

        page.update()

    # Pantalla inicial
    mostrar_pantalla("inicio")


# Ejecutar app
ft.app(target=main, assets_dir="assets")
