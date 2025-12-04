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

    # Cuadros de KPI (reordenados: Pedidos Totales, Tiempo, Errores)
    kpi_row = ft.Row(
        [
            ft.Container(
                content=ft.Column([
                    ft.Text("Pedidos Totales", size=16, weight=ft.FontWeight.BOLD, color=NEGRO),
                    ft.Text("120", size=22, color=AZUL, weight=ft.FontWeight.W_700),
                ], spacing=6, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=16,
                bgcolor="white",
                border_radius=12,
                width=200,
                height=110,
            ),
            ft.Container(width=12),
            ft.Container(
                content=ft.Column([
                    ft.Text("Tiempo Promedio", size=16, weight=ft.FontWeight.BOLD, color=NEGRO),
                    ft.Text("10 min", size=22, color=AZUL, weight=ft.FontWeight.W_700),
                ], spacing=6, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=16,
                bgcolor="white",
                border_radius=12,
                width=200,
                height=110,
            ),
            ft.Container(width=12),
            ft.Container(
                content=ft.Column([
                    ft.Text("Errores Detectados", size=16, weight=ft.FontWeight.BOLD, color=NEGRO),
                    ft.Text("5", size=22, color=ROJO, weight=ft.FontWeight.W_700),
                ], spacing=6, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=16,
                bgcolor="white",
                border_radius=12,
                width=200,
                height=110,
            ),
        ],
        spacing=12,
        alignment=ft.MainAxisAlignment.CENTER
    )

    # eliminada la variable placeholder del gráfico (reemplazada por sección de detalles + gráfica simulada)

    # Contenedor principal
    # Descripción principal fuera de la tarjeta blanca (según indicación)
    descripcion = ft.Text(
        "Panel de Monitoreo de KPIs: visualización del rendimiento del BarkaLove Pizza al instante",
        size=14,
        color=NEGRO
    )

    cuerpo = ft.Column(
        [
            descripcion,
            # Selector de rango de fechas (centrado, formato predeterminado)
            ft.Row(
                [
                    ft.Dropdown(
                        width=260,
                        value="Hoy",
                        options=[
                            ft.dropdown.Option("Hoy"),
                            ft.dropdown.Option("Ayer"),
                            ft.dropdown.Option("Esta semana"),
                            ft.dropdown.Option("Este mes"),
                            ft.dropdown.Option("Personalizado"),
                        ],
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER
            ),
            # tarjeta de título removida por petición (se mantiene solo la descripción)
            # Métricas como tarjetas (reemplazan los botones previos)
            ft.Row([
                ft.Container(
                    content=ft.Column([
                        ft.Text("Pedidos Completados", size=14, weight=ft.FontWeight.W_600, color=NEGRO),
                        ft.Text("98", size=20, weight=ft.FontWeight.W_700, color=AZUL),
                    ], spacing=6, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=16,
                    bgcolor="white",
                    border_radius=12,
                    width=200,
                    height=100,
                ),
                ft.Container(width=12),
                ft.Container(
                    content=ft.Column([
                        ft.Text("En Proceso", size=14, weight=ft.FontWeight.W_600, color=NEGRO),
                        ft.Text("16", size=20, weight=ft.FontWeight.W_700, color=AZUL),
                    ], spacing=6, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=16,
                    bgcolor="white",
                    border_radius=12,
                    width=200,
                    height=100,
                ),
                ft.Container(width=12),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Tiempo Promedio de Preparación", size=14, weight=ft.FontWeight.W_600, color=NEGRO),
                        ft.Text("15 min", size=20, weight=ft.FontWeight.W_700, color=AZUL),
                    ], spacing=6, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=16,
                    bgcolor="white",
                    border_radius=12,
                    width=260,
                    height=100,
                ),
                ft.Container(width=12),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Errores Reportados", size=14, weight=ft.FontWeight.W_600, color=NEGRO),
                        ft.Text("3", size=20, weight=ft.FontWeight.W_700, color=ROJO),
                    ], spacing=6, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=16,
                    bgcolor="white",
                    border_radius=12,
                    width=200,
                    height=100,
                    on_click=lambda e: mostrar_pantalla("errores_kpi"),
                ),
                ft.Container(width=12),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Entregas Tardías", size=14, weight=ft.FontWeight.W_600, color=NEGRO),
                        ft.Text("2", size=20, weight=ft.FontWeight.W_700, color=ROJO),
                    ], spacing=6, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=16,
                    bgcolor="white",
                    border_radius=12,
                    width=200,
                    height=100,
                ),
            ], alignment=ft.MainAxisAlignment.START, spacing=8, scroll=True),

            # Sección de detalles (reemplaza el gráfico) — ampliada
            ft.Container(
                content=ft.Column([
                    ft.Text("Detalles", size=18, weight=ft.FontWeight.BOLD, color=NEGRO),
                    ft.Container(height=10),
                    ft.Text("Resumen de los últimos eventos y observaciones:", size=15, color=GRIS),
                    ft.Container(height=10),
                    ft.Column([
                        ft.Row([ft.Text("• 98 pedidos completados hoy", color=NEGRO)]),
                        ft.Row([ft.Text("• 3 errores reportados en cocina (ver registros)", color=NEGRO)]),
                        ft.Row([ft.Text("• 2 entregas tardías: órdenes #452, #467", color=NEGRO)]),
                        ft.Row([ft.Text("• Tiempo promedio de preparación: 15 minutos", color=NEGRO)]),
                    ], spacing=8)
                ], spacing=10),
                padding=ft.padding.all(20),
                bgcolor="white",
                border_radius=12,
                width="100%",
                height=300,
            ),
            # Gráfica simulada: Tiempos vs Productividad (visual de mentira) — ampliada
            ft.Container(
                content=ft.Column([
                    ft.Text("Gráfica: Tiempos vs Productividad", size=18, weight=ft.FontWeight.BOLD, color=NEGRO),
                    ft.Container(height=10),
                    ft.Row([
                        ft.Column([ft.Container(bgcolor=AZUL, width=28, height=160, border_radius=6), ft.Container(height=8), ft.Text("08:00", size=12, color=NEGRO)], alignment=ft.MainAxisAlignment.END),
                        ft.Container(width=14),
                        ft.Column([ft.Container(bgcolor=AZUL, width=28, height=110, border_radius=6), ft.Container(height=8), ft.Text("10:00", size=12, color=NEGRO)], alignment=ft.MainAxisAlignment.END),
                        ft.Container(width=14),
                        ft.Column([ft.Container(bgcolor=AZUL, width=28, height=180, border_radius=6), ft.Container(height=8), ft.Text("12:00", size=12, color=NEGRO)], alignment=ft.MainAxisAlignment.END),
                        ft.Container(width=14),
                        ft.Column([ft.Container(bgcolor=AZUL, width=28, height=130, border_radius=6), ft.Container(height=8), ft.Text("14:00", size=12, color=NEGRO)], alignment=ft.MainAxisAlignment.END),
                        ft.Container(width=14),
                        ft.Column([ft.Container(bgcolor=AZUL, width=28, height=80, border_radius=6), ft.Container(height=8), ft.Text("16:00", size=12, color=NEGRO)], alignment=ft.MainAxisAlignment.END),
                    ], alignment=ft.MainAxisAlignment.START),
                    ft.Container(height=10),
                    ft.Row([ft.Text("Leyenda:", size=12, color=NEGRO), ft.Container(width=8), ft.Container(bgcolor=AZUL, width=14, height=14, border_radius=3), ft.Container(width=8), ft.Text("Productividad (simulada)", size=12, color=NEGRO)], alignment=ft.MainAxisAlignment.START)
                ], spacing=10),
                padding=ft.padding.all(20),
                bgcolor="white",
                border_radius=12,
                width="100%",
                height=320
            )
        ],
        spacing=16
    )

    layout = ft.Column([header, ft.Divider(), cuerpo], spacing=12)
    root = ft.Container(layout, padding=16, bgcolor=CREMA, expand=True)
    return root