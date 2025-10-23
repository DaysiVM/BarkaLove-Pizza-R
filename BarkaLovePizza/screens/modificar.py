from __future__ import annotations
from datetime import datetime, timedelta
import flet as ft
from utils.pedidos import obtener_pedido, actualizar_pedido

# Paleta
ROJO = "#E63946"
AMARILLO = "#FFD93D"
CREMA = "#FFF8E7"
NEGRO = "#1F1F1F"
AZUL = "#2196F3"
VERDE = "#2A9D8F"
GRIS = "#9E9E9E"

# Ingredientes soportados (alineados con registro)
INGREDIENTES_DEFECTO = [
    "Queso extra", "Pepperoni", "Champiñones", "Aceitunas", "Pimientos", "Jamón", "Piña"
]

# Íconos por ingrediente (mismos assets que usas en registro)
ING_ICON = {
    "Queso extra": "queso.png",
    "Pepperoni": "pepperoni.png",
    "Champiñones": "champi.png",
    "Aceitunas": "aceitunas.png",
    "Pimientos": "pimientos.png",
    "Jamón": "jamon.png",
    "Piña": "pina.png",
}

def _snack(page: ft.Page, msg: str, bg: str = VERDE):
    page.snack_bar = ft.SnackBar(ft.Text(msg, color="white"), bgcolor=bg)
    page.snack_bar.open = True
    page.update()

def _is_modificable(pedido: dict, minutos: int = 5) -> bool:
    try:
        t = datetime.fromisoformat(pedido["hora"])
        return datetime.now() - t < timedelta(minutes=minutos)
    except Exception:
        return False

def pantalla_modificar(
    page: ft.Page,
    masa_inyectada,
    salsa_inyectada,
    checkbox_iny,
    mostrar_pantalla,
    id_orden: int | None = None,
):
    page.bgcolor = CREMA
    page.scroll = ft.ScrollMode.AUTO
    page.clean()

    # ====== Carga ======
    if id_orden is None:
        _snack(page, "No se recibió el número de orden para modificar.", ROJO)
        return ft.Column(
            [ft.Text("Error: falta número de orden", size=22, color=ROJO, weight=ft.FontWeight.BOLD),
             ft.TextButton("⬅ Volver a preparar", on_click=lambda _: mostrar_pantalla("preparar"))],
            horizontal_alignment="center", spacing=10
        )

    pedido = obtener_pedido(id_orden)
    if not pedido:
        _snack(page, f"Pedido #{id_orden} no encontrado.", ROJO)
        return ft.Column(
            [ft.Text(f"Pedido #{id_orden} no encontrado", size=22, color=ROJO, weight=ft.FontWeight.BOLD),
             ft.TextButton("⬅ Volver", on_click=lambda _: mostrar_pantalla("inicio"))],
            horizontal_alignment="center", spacing=10
        )

    if not _is_modificable(pedido, minutos=5):
        return ft.Column(
            [
                ft.Text("Modificar pedido 🛠️", size=26, color=ROJO, weight=ft.FontWeight.BOLD),
                ft.Text(f"Orden #{pedido['orden']} • Cliente: {pedido.get('cliente','—')}", size=16, color=NEGRO),
                ft.Container(height=8),
                ft.Text("La ventana de modificación (5 min) ha expirado.", size=16, color=ROJO, weight=ft.FontWeight.BOLD),
                ft.TextButton("⬅ Volver a preparar", on_click=lambda _: mostrar_pantalla("preparar", numero_orden=pedido["orden"])),
            ],
            horizontal_alignment="center", spacing=10
        )

    items_orig = pedido.get("items") or []
    first = (items_orig[0] if items_orig else {
        "masa": pedido.get("masa"),
        "salsa": pedido.get("salsa"),
        "tamano": pedido.get("tamano"),
        "ingredientes": pedido.get("ingredientes") or [],
        "cantidad": pedido.get("cantidad", 1),
    })

    # ====== Controles ======
    masa_dd = ft.Dropdown(
        label="Tipo de masa",
        options=[ft.dropdown.Option("Delgada"), ft.dropdown.Option("Gruesa")],
        value=first.get("masa"), width=300, color=NEGRO, text_size=16
    )
    salsa_dd = ft.Dropdown(
        label="Salsa",
        options=[ft.dropdown.Option("Tomate"), ft.dropdown.Option("BBQ")],
        value=first.get("salsa"), width=300, color=NEGRO, text_size=16
    )
    tamano_dd = ft.Dropdown(
        label="Tamaño",
        options=[ft.dropdown.Option("Individual"), ft.dropdown.Option("Familiar")],
        value=first.get("tamano"), width=300, color=NEGRO, text_size=16
    )

    # Ingredientes con ícono como en registro
    # Orden: los de defecto y luego cualquier otro que trajera el pedido
    set_all_ings = list(dict.fromkeys(INGREDIENTES_DEFECTO + (first.get("ingredientes") or [])))
    chk_controles: list[ft.Checkbox] = []
    ing_rows: list[ft.Control] = []

    def make_ing_row(nombre: str, checked: bool) -> ft.Control:
        chk = ft.Checkbox(label=nombre, value=checked)
        chk.label_style = ft.TextStyle(color=NEGRO, size=16)
        chk_controles.append(chk)
        icon_src = ING_ICON.get(nombre, "queso.png")
        return ft.Row([
            ft.Image(src=icon_src, width=32, height=32),
            chk
        ], spacing=8, alignment=ft.MainAxisAlignment.START)

    prev_set = set(first.get("ingredientes") or [])
    for ing in set_all_ings:
        ing_rows.append(make_ing_row(ing, ing in prev_set))

    # Cantidad
    cantidad_val = ft.Text(str(first.get("cantidad", 1)), size=18, color=NEGRO)
    def inc(_):
        v = int(cantidad_val.value)
        cantidad_val.value = str(min(10, v+1))
        page.update()
        actualizar_imagen_pizza()
    def dec(_):
        v = int(cantidad_val.value)
        cantidad_val.value = str(max(1,  v-1))
        page.update()
        actualizar_imagen_pizza()
    cantidad_row = ft.Row(
        [ft.Text("Cantidad:", color=NEGRO, size=16, weight=ft.FontWeight.W_600),
         ft.IconButton(icon=ft.Icons.REMOVE, on_click=dec, bgcolor=AMARILLO, tooltip="-"),
         cantidad_val,
         ft.IconButton(icon=ft.Icons.ADD, on_click=inc, bgcolor=AMARILLO, tooltip="+")],
        spacing=8
    )

    # ====== Imagen dinámica (misma lógica que registro) ======
    pizza_imagen = ft.Image(src="pizza_base.png", width=360, height=360, fit=ft.ImageFit.CONTAIN, gapless_playback=True)
    def actualizar_imagen_pizza(e=None):
        seleccionados = [c.label for c in chk_controles if c.value]
        if   "Pepperoni"   in seleccionados: pizza_imagen.src = "Pepperoni-pizza.png"
        elif "Jamón"       in seleccionados: pizza_imagen.src = "Jamon-pizza.png"
        elif "Pimientos"   in seleccionados: pizza_imagen.src = "Pimientos-pizza.png"
        elif "Champiñones" in seleccionados: pizza_imagen.src = "Champiñones-pizza.png"
        elif "Aceitunas"   in seleccionados: pizza_imagen.src = "Aceitunas-pizza.png"
        elif "Piña"        in seleccionados: pizza_imagen.src = "Pina-pizza.png"
        elif "Queso extra" in seleccionados: pizza_imagen.src = "cheese-pizza.png"
        else:                                 pizza_imagen.src = "pizza_base.png"
        page.update()
    for c in chk_controles:
        c.on_change = actualizar_imagen_pizza
    actualizar_imagen_pizza()

    # ====== Acciones ======
    def guardar(_):
        nuevos_ings = [c.label for c in chk_controles if c.value]
        first_edit = {
            "masa": masa_dd.value,
            "salsa": salsa_dd.value,
            "tamano": tamano_dd.value,
            "ingredientes": nuevos_ings,
            "cantidad": int(cantidad_val.value),
        }
        new_items = list(items_orig) if items_orig else [first_edit]
        if new_items:
            new_items[0] = first_edit
        else:
            new_items = [first_edit]

        pedido_edit = {
            **pedido,
            "items": new_items,
            "masa": first_edit["masa"],
            "salsa": first_edit["salsa"],
            "tamano": first_edit["tamano"],
            "ingredientes": first_edit["ingredientes"],
            "cantidad": first_edit["cantidad"],
            "total_visual": sum(int(it.get("cantidad", 1)) for it in new_items) * 10,
            "moneda_visual": pedido.get("moneda_visual", "USD"),
        }
        try:
            actualizar_pedido(pedido_edit)
            _snack(page, "Pedido actualizado correctamente.", VERDE)
            mostrar_pantalla("preparar", numero_orden=pedido["orden"])
        except Exception as ex:
            _snack(page, f"Error al actualizar: {ex}", ROJO)

    def cancelar(_):
        _snack(page, "Modificación cancelada; se mantiene el pedido original.", AMARILLO)
        mostrar_pantalla("preparar", numero_orden=pedido["orden"])

    btn_guardar = ft.ElevatedButton(
        "Guardar cambios", bgcolor=AMARILLO, color=NEGRO, width=220, height=44,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)), on_click=guardar
    )
    btn_cancelar = ft.ElevatedButton(
        "Cancelar", bgcolor=GRIS, color="white", width=180, height=42,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)), on_click=cancelar
    )
    btn_volver = ft.TextButton("⬅ Volver a preparar", on_click=lambda _: mostrar_pantalla("preparar", numero_orden=pedido["orden"]))

    # ====== UI ======
    titulo = ft.Text("Modificar pedido 🛠️", size=28, color=ROJO, weight=ft.FontWeight.BOLD)
    info   = ft.Text(f"Orden #{pedido['orden']} • Cliente: {pedido.get('cliente','—')}", size=16, color=NEGRO)

    columna_izq = ft.Column(
        [
            ft.Text("Cambios rápidos", size=18, color=NEGRO, weight=ft.FontWeight.BOLD),
            masa_dd, salsa_dd, tamano_dd, cantidad_row,
            ft.Text("Ingredientes:", size=18, color=NEGRO, weight=ft.FontWeight.BOLD),
            ft.Column(ing_rows, spacing=6, scroll=ft.ScrollMode.AUTO, height=220),
        ],
        spacing=10, expand=False,
    )

    columna_der = ft.Column(
        [
            ft.Text("Vista previa", size=18, color=NEGRO, weight=ft.FontWeight.BOLD),
            ft.Container(pizza_imagen, alignment=ft.alignment.center),
            ft.Container(height=8),
            ft.Row([btn_guardar, btn_cancelar], alignment=ft.MainAxisAlignment.CENTER, spacing=12),
            ft.Container(height=8),
            btn_volver,
        ],
        spacing=10, expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    grid = ft.ResponsiveRow(
        controls=[
            ft.Container(ft.Column([titulo, info, ft.Divider(), columna_izq], spacing=10),
                         col={"xs": 12, "md": 6, "lg": 5}),
            ft.Container(columna_der, col={"xs": 12, "md": 6, "lg": 7}),
        ],
        columns=12, spacing=12, run_spacing=12,
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.START
    )

    root = ft.Container(grid, bgcolor=CREMA, padding=16, expand=True, alignment=ft.alignment.top_center)
    page.add(root); page.update()
    return root
