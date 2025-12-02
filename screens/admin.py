# screens/admin.py
from __future__ import annotations
import flet as ft
import utils.recetas as rx
import utils.kds as kds

ROJO = "#E63946"
CREMA = "#FFF8E7"
NEGRO = "#1F1F1F"
AMARILLO = "#FFD93D"
AZUL = "#2196F3"
VERDE = "#2A9D8F"
GRIS = "#9E9E9E"


def pantalla_admin(page: ft.Page, mostrar_pantalla):
    page.bgcolor = CREMA
    page.clean()

    # --- Guard: requiere sesión admin ---
    is_admin = page.session.get("admin_auth") is True
    if not is_admin:
        # redirige a login si no autenticado
        page.snack_bar = ft.SnackBar(ft.Text("Necesitas iniciar sesión de admin.", color="white"), bgcolor=ROJO)
        page.snack_bar.open = True
        page.update()
        mostrar_pantalla("admin_login")
        return

    usuario = page.session.get("admin_user") or "admin"

    def logout(_):
        page.session.remove("admin_auth")
        page.session.remove("admin_user")
        page.update()
        mostrar_pantalla("inicio")

    # --- UI ---
    header = ft.Row(
        [
            ft.Text("Panel de Administración", size=26, color=ROJO, weight=ft.FontWeight.BOLD, expand=True),
            ft.Text(f"👤 {usuario}", size=14, color=GRIS),
            ft.ElevatedButton("Cerrar sesión", bgcolor=ROJO, color="white", height=36,
                              style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                              on_click=logout),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    # Tarjetas (cada una será su propia pantalla en siguientes pasos)
    card_recetas = ft.Container(
        bgcolor="white",
        border_radius=12,
        padding=16,
        content=ft.Column(
            [
                ft.Text("Recetas estandarizadas", size=18, weight=ft.FontWeight.W_600, color=NEGRO),
                ft.Text("Administra versiones, activa receta vigente y revisa historial.", size=14, color=GRIS),
                ft.Container(height=8),
                ft.ElevatedButton(
                    "Abrir",
                    bgcolor=AMARILLO, color=NEGRO, height=40,
                    on_click=lambda _: mostrar_pantalla("admin_recetas")  # Próxima pantalla
                ),
            ],
            spacing=6,
        ),
    )

    card_kds = ft.Container(
        bgcolor="white",
        border_radius=12,
        padding=16,
        content=ft.Column(
            [
                ft.Text("KDS (Cocina)", size=18, weight=ft.FontWeight.W_600, color=NEGRO),
                ft.Text("Visualiza pedidos confirmados y marca como listos.", size=14, color=GRIS),
                ft.Container(height=8),
                ft.ElevatedButton(
                    "Abrir",
                    bgcolor=AZUL, color="white", height=40,
                    on_click=lambda _: mostrar_pantalla("kds")  # Pantalla propia ya lista si la agregas
                ),
            ],
            spacing=6,
        ),
    )

    card_respaldo = ft.Container(
        bgcolor="white",
        border_radius=12,
        padding=16,
        content=ft.Column(
            [
                ft.Text("Respaldo de datos", size=18, weight=ft.FontWeight.W_600, color=NEGRO),
                ft.Text("Gestiona copias de seguridad: crear, restaurar y descargar.", size=14, color=GRIS),
                ft.Container(height=8),
                ft.ElevatedButton(
                    "Abrir",
                    bgcolor=VERDE, color="white", height=40,
                    on_click=lambda _: mostrar_pantalla("admin_respaldo")
                ),
            ],
            spacing=6,
        ),
    )

    card_manuales_usuario = ft.Container(
        bgcolor="white",
        border_radius=12,
        padding=16,
        content=ft.Column(
            [
                ft.Text("Manuales de Usuario", size=18, weight=ft.FontWeight.W_600, color=NEGRO),
                ft.Text("Visualiza y abre manuales de usuario en formato PDF.", size=14, color=GRIS),
                ft.Container(height=8),
                ft.ElevatedButton(
                    "Abrir",
                    bgcolor=VERDE, color="white", height=40,
                    on_click=lambda _: mostrar_pantalla("manuales_usuario")
                ),
            ],
            spacing=6,
        ),
    )

    grid = ft.ResponsiveRow(
        controls=[
            ft.Container(card_recetas, col={"xs": 12, "md": 6, "lg": 6}),
            ft.Container(card_kds, col={"xs": 12, "md": 6, "lg": 6}),
            ft.Container(card_respaldo, col={"xs": 12, "md": 6, "lg": 6}),
            ft.Container(card_manuales_usuario, col={"xs": 12, "md": 6, "lg": 6}),
        ],
        columns=12,
        spacing=12,
        run_spacing=12,
    )

    layout = ft.Column([header, ft.Divider(), grid], spacing=10)
    root = ft.Container(layout, padding=16, bgcolor=CREMA, expand=True)
    return root
