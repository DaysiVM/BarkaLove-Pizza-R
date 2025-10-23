import flet as ft
from datetime import datetime
from utils.pedidos import obtener_pedido

ROJO = "#E63946"
CREMA = "#FFF8E7"
NEGRO = "#1F1F1F"

def pantalla_ver_orden(page: ft.Page, numero_orden: int, mostrar_pantalla):
    page.bgcolor = CREMA
    page.scroll = ft.ScrollMode.AUTO
    page.clean()

    pedido = obtener_pedido(numero_orden) if numero_orden is not None else None

    if not pedido:
        page.add(ft.Column([
            ft.Text("Orden no encontrada", size=24, color=ROJO, weight="bold"),
            ft.TextButton("⬅ Volver", on_click=lambda _: mostrar_pantalla("inicio"))
        ], horizontal_alignment="center", spacing=10))
        page.update()
        return

    try:
        dt = datetime.fromisoformat(pedido.get("hora", ""))
        fecha_hora = dt.strftime("%d/%m/%Y %H:%M")
    except Exception:
        fecha_hora = pedido.get("hora") or "—"

    cliente = pedido.get("cliente", "—")
    metodo = pedido.get("metodo_pago", "—")
    total = pedido.get("total_visual", 0)
    moneda = pedido.get("moneda_visual", "USD")
    items = pedido.get("items") or []

    titulo = ft.Text("Factura / Detalle de Orden", size=28, color=ROJO, weight=ft.FontWeight.BOLD)

    encabezado = ft.Column([
        ft.Text(f"Orden #{pedido.get('orden','—')}", size=18, color=NEGRO, weight=ft.FontWeight.BOLD),
        ft.Text(f"Fecha y hora: {fecha_hora}", size=14, color=NEGRO),
        ft.Text(f"Cliente: {cliente}", size=14, color=NEGRO),
        ft.Text(f"Método de pago: {metodo}", size=14, color=NEGRO),
    ], spacing=4)

    def item_row(it, idx):
        det = f"{it.get('cantidad',1)}× {it.get('tamano','N/D')} — {it.get('masa','')} + {it.get('salsa','')}"
        ings = ", ".join(it.get("ingredientes") or [])
        return ft.Column([
            ft.Text(f"Producto {idx+1}", size=16, weight=ft.FontWeight.BOLD),
            ft.Text(det, size=14, color=NEGRO),
            ft.Text(f"Ingredientes: {ings if ings else 'Sin extras'}", size=14, color=NEGRO),
            ft.Divider(),
        ], spacing=2)

    items_list = ft.Column([item_row(it, i) for i, it in enumerate(items)], spacing=6)
    total_line = ft.Text(f"Total: {total} {moneda}", size=18, weight=ft.FontWeight.BOLD, color=NEGRO)

    # ⬇️ Cambiado: ahora dice "Salir" y vuelve a inicio
    btn_salir = ft.ElevatedButton(
        "Salir",
        on_click=lambda _: mostrar_pantalla("inicio"),
        bgcolor=ROJO,
        color="white",
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        width=220,
        height=44
    )

    tarjeta = ft.Container(
        content=ft.Column([
            titulo,
            ft.Divider(),
            encabezado,
            ft.Container(height=8),
            items_list,
            ft.Container(height=8),
            total_line,
            ft.Container(height=12),
            btn_salir,
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
        bgcolor="white",
        padding=20,
        border_radius=12,
        width=560
    )

    root = ft.Container(content=tarjeta, alignment=ft.alignment.center, expand=True, bgcolor=CREMA)
    page.add(root)
    page.update()
    return root
