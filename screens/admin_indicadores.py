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

    # Placeholder para gráfico
    grafico = ft.Container(
        content=ft.Text("Gráfico placeholder", color=NEGRO),
        height=180,
        bgcolor="white",
        border_radius=10,
        alignment=ft.alignment.center
    )

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
            # Pequeña tarjeta resumen (opcional) para título interno
            ft.Container(
                content=ft.Text("Monitoreo de KPIs", size=18, weight=ft.FontWeight.BOLD, color=NEGRO),
                padding=ft.padding.symmetric(vertical=8, horizontal=12),
                bgcolor="white",
                border_radius=12
            ),
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

            # Sección de detalles (reemplaza el gráfico)
            ft.Container(
                content=ft.Column([
                    ft.Text("Detalles", size=16, weight=ft.FontWeight.BOLD, color=NEGRO),
                    ft.Container(height=8),
                    ft.Text("Resumen de los últimos eventos y observaciones:", size=14, color=GRIS),
                    ft.Container(height=8),
                    ft.Column([
                        ft.Row([ft.Text("• 98 pedidos completados hoy", color=NEGRO)]),
                        ft.Row([ft.Text("• 3 errores reportados en cocina (ver registros)", color=NEGRO)]),
                        ft.Row([ft.Text("• 2 entregas tardías: órdenes #452, #467", color=NEGRO)]),
                        ft.Row([ft.Text("• Tiempo promedio de preparación: 15 minutos", color=NEGRO)]),
                    ], spacing=6)
                ], spacing=8),
                padding=16,
                bgcolor="white",
                border_radius=12,
                width="100%",
                height=200
            )
        ],
        spacing=16
    )

    layout = ft.Column([header, ft.Divider(), cuerpo], spacing=12)
    root = ft.Container(layout, padding=16, bgcolor=CREMA, expand=True)
    return root

