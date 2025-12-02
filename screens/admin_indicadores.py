import flet as ft

NEGRO = "#1F1F1F"
CREMA = "#FFF8E7"


def pantalla_admin_indicadores(page: ft.Page, mostrar_pantalla):
    page.bgcolor = CREMA

    header = ft.Row([
        ft.Text("Indicadores", size=24, weight=ft.FontWeight.BOLD, color=NEGRO),
        ft.ElevatedButton("Volver", on_click=lambda e: mostrar_pantalla("admin"), height=40),
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    # Sidebar: filtros de rango
    rango_rg = ft.RadioGroup()
    opcion_semana = ft.Radio(label="Esta semana", value="semana", group=rango_rg)
    opcion_mes = ft.Radio(label="Este mes", value="mes", group=rango_rg)
    opcion_custom = ft.Radio(label="Personalizado", value="custom", group=rango_rg)

    fecha_inicio = ft.DatePicker(label="Desde")
    fecha_fin = ft.DatePicker(label="Hasta")

    sidebar = ft.Column([
        ft.Text("Filtros de rango", weight=ft.FontWeight.W_600, color=NEGRO),
        ft.Container(height=8),
        opcion_semana,
        opcion_mes,
        opcion_custom,
        ft.Container(height=12),
        fecha_inicio,
        fecha_fin,
    ], spacing=6, width=260)

    # Métricas superiores: tres paneles
    card_prod = ft.Container(
        bgcolor="white",
        padding=12,
        border_radius=8,
        width=320,
        content=ft.Column([
            ft.Text("Productividad", weight=ft.FontWeight.W_600, color=NEGRO),
            ft.Text("87% tareas completadas / totales", color=NEGRO),
            ft.Text("Rendimiento +12% vs ayer", color="#2A9D8F"),
        ], spacing=6),
    )

    card_time = ft.Container(
        bgcolor="white",
        padding=12,
        border_radius=8,
        width=320,
        content=ft.Column([
            ft.Text("Tiempos", weight=ft.FontWeight.W_600, color=NEGRO),
            ft.Text("10 minutos por tarea", color=NEGRO),
            ft.Text("Tendencia -3 minutos vs la semana pasada", color="#1565C0"),
        ], spacing=6),
    )

    card_err = ft.Container(
        bgcolor="white",
        padding=12,
        border_radius=8,
        width=320,
        content=ft.Column([
            ft.Row([ft.Text("Errores", weight=ft.FontWeight.W_600, color=NEGRO), ft.Icon(ft.icons.WARNING, color="#FFD54F")]),
            ft.Text("6 errores", color=NEGRO),
            ft.Text("Nivel de riesgo: Medio", color="#F9A825"),
        ], spacing=6),
    )

    top_metrics = ft.Row([card_prod, ft.Container(width=12), card_time, ft.Container(width=12), card_err], alignment=ft.MainAxisAlignment.START)

    # Gráfica comparativa (placeholder)
    grafica = ft.Container(
        bgcolor="white",
        padding=12,
        border_radius=8,
        expand=True,
        content=ft.Column([
            ft.Text("Vista comparativa", weight=ft.FontWeight.W_600, color=NEGRO),
            ft.Container(height=8),
            ft.Text("(Comparación entre productividad y tiempo de procesamiento)", color=NEGRO),
            ft.Container(height=12),
            ft.Container(height=180, bgcolor="#F5F5F5", content=ft.Text("[Gráfica placeholder]", color=NEGRO), alignment=ft.alignment.center())
        ], spacing=6),
    )

    # Paneles inferiores
    resumen = ft.Container(
        bgcolor="white",
        padding=12,
        border_radius=8,
        width=420,
        content=ft.Column([
            ft.Text("Resumen de la semana", weight=ft.FontWeight.W_600, color=NEGRO),
            ft.Container(height=8),
            ft.Text("Tareas completadas: 342", color=NEGRO),
            ft.Text("Tareas pendientes: 48", color=NEGRO),
            ft.Text("Tiempo promedio: 25 min", color=NEGRO),
            ft.Text("Tasa de éxito: 96.5%", color=NEGRO),
        ], spacing=6),
    )

    # Errores por módulo con barras
    def barra_errores(count, max_count=10):
        value = min(count / max_count, 1.0)
        return ft.Row([ft.Text(str(count), width=28, color=NEGRO), ft.Container(width=8), ft.ProgressBar(value=value, width=220)])

    errores_mod = ft.Container(
        bgcolor="white",
        padding=12,
        border_radius=8,
        expand=True,
        content=ft.Column([
            ft.Text("Errores por módulo", weight=ft.FontWeight.W_600, color=NEGRO),
            ft.Container(height=8),
            ft.Text("Autenticación", color=NEGRO),
            barra_errores(3, max_count=10),
            ft.Container(height=6),
            ft.Text("Procesamiento", color=NEGRO),
            barra_errores(5, max_count=10),
            ft.Container(height=6),
            ft.Text("Base de datos", color=NEGRO),
            barra_errores(2, max_count=10),
            ft.Container(height=6),
            ft.Text("API externa", color=NEGRO),
            barra_errores(2, max_count=10),
        ], spacing=6),
    )

    bottom_row = ft.Row([resumen, ft.Container(width=12), errores_mod], alignment=ft.MainAxisAlignment.START)

    main_column = ft.Column([
        ft.Text("Productividad, tiempos y errores", size=16, color=NEGRO),
        ft.Container(height=12),
        top_metrics,
        ft.Container(height=16),
        grafica,
        ft.Container(height=16),
        bottom_row,
    ], spacing=12)

    layout = ft.Row([sidebar, ft.Container(width=16), ft.Container(main_column, expand=True)])

    root = ft.Container(ft.Column([header, ft.Divider(), layout]), padding=16)
    return root
