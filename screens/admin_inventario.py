from __future__ import annotations
import flet as ft
from typing import Dict, Any
import utils.inventario as inv

# Paleta estética
ROJO = "#E63946"
VERDE = "#2A9D8F"
CREMA = "#FFF8E7"
NEGRO = "#1F1F1F"
AMARILLO = "#FFC300"
AZUL = "#2196F3"
GRIS = "#9E9E9E"
GRIS_OSCURO = "#565656"
BLANCO = "#FFFFFF"


def pantalla_admin_inventario(page: ft.Page, mostrar_pantalla):
    page.clean()
    page.bgcolor = CREMA
    page.scroll = "auto"

    # ===================== TOP =====================
    titulo = ft.Text("Inventario de Ingredientes", size=26, color=ROJO, weight="bold")

    btn_volver = ft.ElevatedButton(
        "Volver",
        bgcolor=GRIS_OSCURO,
        color=BLANCO,
        icon=ft.Icons.ARROW_BACK,
        height=42,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
        on_click=lambda _: mostrar_pantalla("admin"),
    )

    txt_buscar = ft.TextField(
        label="Buscar ingrediente",
        width=250,
        color=NEGRO,
        on_change=lambda e: cargar_lista(),
    )

    btn_agregar = ft.ElevatedButton(
        "Agregar",
        bgcolor=VERDE,
        color=BLANCO,
        icon=ft.Icons.ADD,
        height=42,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
        on_click=lambda _: dialogo_agregar(),
    )

    top_bar = ft.Row(
        [
            btn_volver,
            titulo,
            ft.Container(expand=True),
            txt_buscar,
            btn_agregar,
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    # ===================== LISTA =====================
    alert_banner = ft.Container(visible=False)
    lista_column = ft.Column(spacing=12, expand=True)

    # ===================== FUNCIONES =====================

    def barra_stock(cant: int, minv: int):
        porc = 0 if minv == 0 else min(1, cant / (minv * 2))

        if cant <= minv:
            color = ROJO
        elif cant <= minv * 1.5:
            color = AMARILLO
        else:
            color = VERDE

        return ft.ProgressBar(
            value=porc,
            bgcolor="#DDD",
            color=color,
            width=300,
            height=10,
        )

    def cargar_lista():
        lista_column.controls.clear()
        q = (txt_buscar.value or "").strip().lower()

        items = inv.listar_inventario()
        alertas = []

        if q:
            items = [i for i in items if q in i["ingrediente"].lower()]

        for item in items:
            if item["cantidad_actual"] <= item["stock_minimo"]:
                alertas.append(item["ingrediente"])
            lista_column.controls.append(row_item(item))

        if alertas:
            alert_banner.visible = True
            alert_banner.content = ft.Container(
                bgcolor=AMARILLO,
                padding=10,
                border_radius=8,
                content=ft.Text(
                    f"⚠ Stock bajo: {', '.join(alertas)}",
                    color=NEGRO,
                    weight="bold"
                )
            )
        else:
            alert_banner.visible = False

        page.update()

    def row_item(it: Dict[str, Any]):
        nombre = it["ingrediente"]
        cant = it["cantidad_actual"]
        minimo = it["stock_minimo"]
        unidad = it.get("unidad", "unidades")

        return ft.Container(
            bgcolor=BLANCO,
            border_radius=12,
            padding=16,
            shadow=ft.BoxShadow(blur_radius=6, spread_radius=1, color="#00000020"),
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(nombre, size=20, weight="bold", color=NEGRO),
                            ft.Text(f"({unidad})", size=14, color=GRIS),
                            ft.Container(expand=True),
                        ]
                    ),
                    ft.Row(
                        [
                            ft.Text(f"Cantidad: {cant}", size=14),
                            ft.Text(f"Mínimo: {minimo}", size=14, color=GRIS_OSCURO),
                        ]
                    ),
                    barra_stock(cant, minimo),
                    ft.Row(
                        [
                            ft.IconButton(icon=ft.Icons.REMOVE, bgcolor=ROJO, icon_color=BLANCO,
                                          on_click=lambda _, n=nombre: ajustar(n, -1)),
                            ft.IconButton(icon=ft.Icons.ADD, bgcolor=VERDE, icon_color=BLANCO,
                                          on_click=lambda _, n=nombre: ajustar(n, +1)),

                            ft.Container(expand=True),

                            ft.IconButton(icon=ft.Icons.EDIT, icon_color=AZUL,
                                          on_click=lambda _, i=it: dialogo_editar(i)),
                            ft.IconButton(icon=ft.Icons.DELETE, icon_color=ROJO,
                                          on_click=lambda _, n=nombre: dialogo_eliminar(n)),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    )
                ]
            )
        )

    def ajustar(nombre, delta):
        ok = inv.ajustar_cantidad(nombre, delta)

        page.snack_bar = ft.SnackBar(
            content=ft.Text("Actualizado" if ok else "Error", color=BLANCO),
            bgcolor=VERDE if ok else ROJO,
        )
        page.snack_bar.open = True
        cargar_lista()

    # ===================== AGREGAR =====================
        # ===================== AGREGAR =====================
    def dialogo_agregar():
        nombre = ft.TextField(label="Nombre")
        cantidad = ft.TextField(label="Cantidad inicial")
        minimo = ft.TextField(label="Stock mínimo")
        unidad = ft.TextField(label="Unidad (porciones, unidades, etc.)")

        content = ft.Container(
            width=380,
            padding=10,
            content=ft.Column([nombre, cantidad, minimo, unidad], spacing=10)
        )

        def confirmar(_):
            try:
                c = int(cantidad.value)
                m = int(minimo.value)
            except:
                return

            ok = inv.agregar_ingrediente(
                nombre.value, c, m, unidad.value
            )

            dialog.open = False
            page.update()

            page.snack_bar = ft.SnackBar(
                content=ft.Text("Ingrediente agregado" if ok else "Ya existe", color=BLANCO),
                bgcolor=VERDE if ok else ROJO,
            )
            page.snack_bar.open = True
            cargar_lista()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Agregar Ingrediente"),
            content=content,
            actions_alignment="center",
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: close(dialog)),
                ft.TextButton("Agregar", on_click=confirmar),
            ],
        )
        page.open(dialog)

    # ===================== EDITAR =====================
    def dialogo_editar(item):
        nombre = ft.TextField(label="Nombre", value=item["ingrediente"])
        cantidad = ft.TextField(label="Cantidad", value=str(item["cantidad_actual"]))
        minimo = ft.TextField(label="Stock mínimo", value=str(item["stock_minimo"]))
        unidad = ft.TextField(label="Unidad", value=item["unidad"])

        content = ft.Container(
            width=380,
            padding=10,
            content=ft.Column([nombre, cantidad, minimo, unidad], spacing=10)
        )

        def confirmar(_):
            try:
                c = int(cantidad.value)
                m = int(minimo.value)
            except:
                return

            ok = inv.actualizar_ingrediente(
                item["ingrediente"],
                nombre.value,
                c,
                m,
                unidad.value,
            )

            dialog.open = False
            page.update()

            page.snack_bar = ft.SnackBar(
                content=ft.Text("Ingrediente actualizado" if ok else "Error", color=BLANCO),
                bgcolor=VERDE if ok else ROJO,
            )
            page.snack_bar.open = True
            cargar_lista()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Editar Ingrediente"),
            content=content,
            actions_alignment="center",
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: close(dialog)),
                ft.TextButton("Guardar", on_click=confirmar),
            ],
        )
        page.open(dialog)

    # ===================== ELIMINAR =====================
    def dialogo_eliminar(nombre):
        content = ft.Container(
            width=320,
            padding=10,
            content=ft.Text(f"¿Eliminar '{nombre}'?")
        )

        def confirmar(_):
            ok = inv.eliminar_ingrediente(nombre)
            dialog.open = False
            page.update()

            page.snack_bar = ft.SnackBar(
                content=ft.Text("Eliminado" if ok else "Error", color=BLANCO),
                bgcolor=ROJO,
            )
            page.snack_bar.open = True
            cargar_lista()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Eliminar Ingrediente"),
            content=content,
            actions_alignment="center",
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: close(dialog)),
                ft.TextButton("Eliminar", on_click=confirmar),
            ],
        )
        page.open(dialog)

    def close(d):
        d.open = False
        page.update()


    # ===================== MONTAJE FINAL =====================
    root = ft.Container(
        padding=20,
        content=ft.Column(
            [
                top_bar,
                ft.Divider(),
                alert_banner,
                lista_column
            ],
            expand=True
        )
    )

    page.add(root)
    cargar_lista()

    return root
