# screens/ver_orden.py
from __future__ import annotations
import flet as ft
from datetime import datetime
from typing import Optional, Dict, Any
from utils.pedidos import obtener_pedido

# Colores
ROJO = "#E63946"
CREMA = "#FFF8E7"
NEGRO = "#1F1F1F"
GRIS = "#9E9E9E"

def _parse_hora(hora_val) -> str:
    """
    Intenta convertir valores comunes de 'hora' a formato legible.
    Si falla, devuelve la representación original o "—".
    """
    if not hora_val:
        return "—"
    # Si ya es datetime
    if isinstance(hora_val, datetime):
        return hora_val.strftime("%d/%m/%Y %H:%M")
    # si es string ISO
    try:
        return datetime.fromisoformat(str(hora_val)).strftime("%d/%m/%Y %H:%M")
    except Exception:
        pass
    # intento parseo corto dd/mm/yyyy hh:mm
    try:
        return datetime.strptime(str(hora_val), "%d/%m/%Y %H:%M").strftime("%d/%m/%Y %H:%M")
    except Exception:
        pass
    # fallback: devolver como string
    try:
        return str(hora_val)
    except Exception:
        return "—"

def pantalla_ver_orden(page: ft.Page, numero_orden: Optional[int], mostrar_pantalla):
    """
    Muestra la factura / detalle de una orden.
    - numero_orden: número de orden (int) o None
    - mostrar_pantalla: función del router para navegar
    """
    page.bgcolor = CREMA
    page.scroll = ft.ScrollMode.AUTO
    page.clean()

    pedido: Optional[Dict[str, Any]] = None
    try:
        if numero_orden is not None:
            pedido = obtener_pedido(numero_orden)
        else:
            pedido = None
    except Exception:
        # si obtener_pedido requiere otro comportamiento, toleramos fallos
        pedido = None

    if not pedido:
        no_encontrado = ft.Column(
            [
                ft.Text("Orden no encontrada", size=24, color=ROJO, weight=ft.FontWeight.BOLD),
                ft.TextButton("⬅ Volver", on_click=lambda _: mostrar_pantalla("inicio"))
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
        )
        page.add(ft.Container(content=no_encontrado, alignment=ft.alignment.center, expand=True))
        page.update()
        return None

    # Campos principales
    fecha_hora = _parse_hora(pedido.get("hora"))
    cliente = pedido.get("cliente", pedido.get("nombre", "—"))
    metodo = pedido.get("metodo_pago", "—")
    total = pedido.get("total_visual", 0)
    moneda = pedido.get("moneda_visual", "USD")
    items = pedido.get("items") or []

    # Titulo / encabezado
    titulo = ft.Text("Factura / Detalle de Orden", size=28, color=ROJO, weight=ft.FontWeight.BOLD)
    encabezado = ft.Column(
        [
            ft.Text(f"Orden #{pedido.get('orden','—')}", size=18, color=NEGRO, weight=ft.FontWeight.BOLD),
            ft.Text(f"Fecha y hora: {fecha_hora}", size=14, color=NEGRO),
            ft.Text(f"Cliente: {cliente}", size=14, color=NEGRO),
            ft.Text(f"Método de pago: {metodo}", size=14, color=NEGRO),
        ],
        spacing=4,
        horizontal_alignment=ft.CrossAxisAlignment.START,
    )

    # Lista de items
    def item_row(it: Dict[str, Any], idx: int):
        cantidad = it.get("cantidad", it.get("qty", 1))
        tam = it.get("tamano", it.get("tamano_pizza", "N/D"))
        masa = it.get("masa", "") or ""
        salsa = it.get("salsa", "") or ""
        det = f"{cantidad}× {tam} — {masa} + {salsa}"
        ings = ", ".join(it.get("ingredientes") or [])
        return ft.Column(
            [
                ft.Text(f"Producto {idx+1}", size=16, weight=ft.FontWeight.BOLD),
                ft.Text(det, size=14, color=NEGRO),
                ft.Text(f"Ingredientes: {ings if ings else 'Sin extras'}", size=14, color=NEGRO),
                ft.Divider(),
            ],
            spacing=4,
        )

    items_list = ft.Column([item_row(it, i) for i, it in enumerate(items)], spacing=6)

    total_line = ft.Text(f"Total: {total} {moneda}", size=18, weight=ft.FontWeight.BOLD, color=NEGRO)

    # Botón salir / volver
    btn_salir = ft.ElevatedButton(
        "Salir",
        on_click=lambda _: mostrar_pantalla("inicio"),
        bgcolor=ROJO,
        color="white",
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        width=220,
        height=44
    )

    # Tarjeta principal (centrada)
    tarjeta = ft.Container(
        content=ft.Column(
            [
                titulo,
                ft.Divider(),
                encabezado,
                ft.Container(height=8),
                items_list,
                ft.Container(height=8),
                total_line,
                ft.Container(height=12),
                btn_salir,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8
        ),
        bgcolor="white",
        padding=20,
        border_radius=12,
        width=560
    )

    root = ft.Container(content=tarjeta, alignment=ft.alignment.center, expand=True, bgcolor=CREMA)
    page.add(root)
    page.update()
    return root
