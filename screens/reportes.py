import flet as ft

# Colores usados en la app
ROJO = "#E63946"
CREMA = "#FFF8E7"
NEGRO = "#1F1F1F"


def pantalla_reportes(page: ft.Page, mostrar_pantalla):
    """Pantalla de Reportes (versión inicial).

    Muestra el título grande "Reportes Históricos" y un botón para volver.
    Se puede ampliar con filtros, tablas y exportación.
    """
    page.bgcolor = CREMA

    # Título grande
    titulo = ft.Text("Reportes Históricos", size=34, weight=ft.FontWeight.BOLD, color=ROJO)

    # Dropdown para seleccionar tipo de reporte (se mostrará debajo del subtítulo)
    tipo_dd = ft.Dropdown(
        label="",
        options=[
            ft.dropdown.Option("Ventas"),
            ft.dropdown.Option("Gastos"),
            ft.dropdown.Option("Inventario"),
            ft.dropdown.Option("Daños / Incidencias"),
        ],
        value="Ventas",
        width=260,
    )

    header = ft.Row([
        titulo,
        ft.ElevatedButton("Volver", on_click=lambda e: mostrar_pantalla("admin"), height=40),
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    subtitle = ft.Text("Selecciona un tipo de reporte y rango de fechas para ver resultados.", color=NEGRO)

    # Row with the tipo and fechas dropdowns centered below the subtitle
    # Remove textual labels inside the layout box and keep dropdowns compact
    fechas_dd = ft.Dropdown(
        label="",
        options=[
            ft.dropdown.Option("Hoy"),
            ft.dropdown.Option("Últimos 7 días"),
            ft.dropdown.Option("Este mes"),
            ft.dropdown.Option("Año actual"),
        ],
        value="Últimos 7 días",
        width=220,
    )

    # Left-aligned: labels next to controls, stacked vertically, dropdowns aligned
    LABEL_WIDTH = 140
    label_tipo = ft.Container(ft.Text("Tipo de reporte:", size=14, color=NEGRO), width=LABEL_WIDTH)
    label_fechas = ft.Container(ft.Text("Fechas:", size=14, color=NEGRO), width=LABEL_WIDTH)

    # Ensure both dropdowns have same width so boxes align vertically
    DROPDOWN_WIDTH = 260
    tipo_dd.width = DROPDOWN_WIDTH
    fechas_dd.width = DROPDOWN_WIDTH

    tipo_row = ft.Row([label_tipo, tipo_dd], alignment=ft.MainAxisAlignment.START, spacing=12)
    fechas_row = ft.Row([label_fechas, fechas_dd], alignment=ft.MainAxisAlignment.START, spacing=12)

    controls_column = ft.Column([tipo_row, fechas_row], horizontal_alignment=ft.CrossAxisAlignment.START, spacing=8)

    layout = ft.Column([header, ft.Divider(), subtitle, controls_column], spacing=12)
    root = ft.Container(layout, padding=16, bgcolor=CREMA, expand=True)
    return root
