import flet as ft

NEGRO = "#1F1F1F"
CREMA = "#FFF8E7"


def pantalla_respaldo_proceso(page: ft.Page, mostrar_pantalla):
    page.bgcolor = CREMA

    header = ft.Row([
        ft.Text("Proceso completado", size=22, weight=ft.FontWeight.BOLD, color=NEGRO),
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    body = ft.Column([
        ft.Container(height=24),
        ft.Text("¡Copia de seguridad restaurada!", size=18, weight=ft.FontWeight.W_600, color=NEGRO),
        ft.Container(height=12),
        ft.Text("El proceso de restauración finalizó correctamente.", color=NEGRO),
        ft.Container(height=20),
        ft.ElevatedButton("Volver", on_click=lambda e: mostrar_pantalla("admin_respaldo"), width=240)
    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    root = ft.Container(ft.Column([header, ft.Divider(), body]), padding=16)
    return root
