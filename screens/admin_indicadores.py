import flet as ft

ROJO = "#E63946"
CREMA = "#FFF8E7"
NEGRO = "#1F1F1F"
GRIS = "#9E9E9E"
AZUL = "#2196F3"

def pantalla_admin_indicadores(page: ft.Page, mostrar_pantalla):
    page.bgcolor = CREMA

    # Header con botón de volver
    header = ft.Row(
        [
            ft.Text("Indicadores", size=24, color=AZUL, weight=ft.FontWeight.BOLD, expand=True),
            ft.ElevatedButton(
                "Volver",
                bgcolor=AZUL,
                color="white",
                height=36,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                on_click=lambda e: mostrar_pantalla("admin")
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    # Cuadros de KPI
    kpi_row = ft.Row(
        [
            ft.Container(
                content=ft.Column([
                    ft.Text("Pedidos Totales", size=16, weight=ft.FontWeight.BOLD),
                    ft.Text("120", size=20, color=AZUL),
                ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=12,
                bgcolor="white",
                border_radius=10,
                width=180,
                height=100,
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text("Errores Detectados", size=16, weight=ft.FontWeight.BOLD),
                    ft.Text("5", size=20, color=ROJO),
                ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=12,
                bgcolor="white",
                border_radius=10,
                width=180,
                height=100,
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text("Pedidos Completados", size=16, weight=ft.FontWeight.BOLD),
                    ft.Text("95%", size=20, color="#2A9D8F"),
                ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=12,
                bgcolor="white",
                border_radius=10,
                width=180,
                height=100,
            ),
        ],
        spacing=12,
        alignment=ft.MainAxisAlignment.CENTER
    )

    # Placeholder para gráfico
    grafico = ft.Container(
        content=ft.Text("Gráfico placeholder", color=NEGRO),
        height=180,
        bgcolor="white",
        border_radius=10,
        alignment=ft.alignment.center
    )

    # Contenedor principal
    cuerpo = ft.Column(
        [
            ft.Container(
                content=ft.Column([
                    ft.Text("Monitoreo de KPIs", size=18, weight=ft.FontWeight.BOLD, color=NEGRO),
                    ft.Container(height=4),
                    ft.Text("Productividad, tiempos y errores", size=14, color=GRIS),
                ], spacing=4),
                padding=12,
                bgcolor="white",
                border_radius=10
            ),
            # Fila de acciones/controles (visuales, no funcionales)
            ft.Row([
                ft.ElevatedButton("Refrescar", bgcolor=AZUL, color="white", height=36),
                ft.Container(width=8),
                ft.ElevatedButton("Exportar CSV", height=36),
                ft.Container(width=8),
                ft.ElevatedButton("Configurar alertas", height=36),
                ft.Container(width=8),
                ft.Dropdown(label="Ver:", options=[ft.dropdown.Option("Últimas 24h"), ft.dropdown.Option("Última semana"), ft.dropdown.Option("Último mes")], value="Última semana", width=180),
            ], alignment=ft.MainAxisAlignment.START),
            kpi_row,
            grafico
        ],
        spacing=16
    )

    layout = ft.Column([header, ft.Divider(), cuerpo], spacing=12)
    root = ft.Container(layout, padding=16, bgcolor=CREMA, expand=True)
    return root

