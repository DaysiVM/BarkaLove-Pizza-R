import flet as ft
from typing import Optional
from datetime import datetime

ROJO = "#E63946"
CREMA = "#FFF8E7"
NEGRO = "#1F1F1F"
GRIS = "#9E9E9E"


def pantalla_admin_actualizaciones(page: ft.Page, mostrar_pantalla):
    page.bgcolor = CREMA
    page.clean()

    # guard
    is_admin = page.session.get("admin_auth") is True
    if not is_admin:
        page.snack_bar = ft.SnackBar(ft.Text("Necesitas iniciar sesión de admin.", color="white"), bgcolor=ROJO)
        page.snack_bar.open = True
        page.update()
        mostrar_pantalla("admin_login")
        return

    header = ft.Row([
        ft.Text("Actualizaciones", size=26, weight=ft.FontWeight.BOLD, color=NEGRO, expand=True),
        ft.ElevatedButton("Volver", bgcolor=ROJO, color="white", on_click=lambda e: mostrar_pantalla("admin"))
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    subtitle = ft.Text("Proceso de actualización remoto", size=16, color=GRIS)

    status_txt = ft.Text("Estado: sin buscar", size=14, color=NEGRO)

    def buscar_actualizaciones(e: ft.ControlEvent):
        status_txt.value = "Buscando actualizaciones..."
        page.update()
        # Simular operación
        import time
        time.sleep(0.5)
        # Resultado simulado
        status_txt.value = f"Última búsqueda: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} — No hay nuevas actualizaciones"
        page.snack_bar = ft.SnackBar(ft.Text("Búsqueda completada", color="white"), bgcolor="#2A9D8F")
        page.snack_bar.open = True
        page.update()

    btn_buscar = ft.ElevatedButton("Buscar actualizaciones", on_click=buscar_actualizaciones, bgcolor="#2A9D8F", color="white")

    body = ft.Column([
        header,
        ft.Container(height=8),
        subtitle,
        ft.Container(height=12),
        status_txt,
        ft.Container(height=12),
        btn_buscar,
    ], spacing=8)

    root = ft.Container(content=body, padding=16, expand=True, bgcolor=CREMA)
    page.add(root)

    return root
