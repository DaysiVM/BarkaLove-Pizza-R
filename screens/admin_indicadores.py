import flet as ft

NEGRO = "#1F1F1F"
CREMA = "#FFF8E7"


def pantalla_admin_indicadores(page: ft.Page, mostrar_pantalla):
    page.bgcolor = CREMA

    header = ft.Row([
        ft.Text("Indicadores", size=24, weight=ft.FontWeight.BOLD, color=NEGRO),
        ft.ElevatedButton("Volver", on_click=lambda e: mostrar_pantalla("admin"), height=40),
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    body = ft.Column([
        ft.Text("Productividad, tiempos y errores", size=16, color=NEGRO),
        ft.Container(height=12),
        ft.Text("Espacio reservado para indicadores.", color=NEGRO),
    ], spacing=8)

    root = ft.Container(ft.Column([header, ft.Divider(), body]), padding=16)
    return root
