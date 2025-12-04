import flet as ft
from datetime import datetime, date, timedelta

# Pantalla: Comparación de consumo entre turnos
def pantalla_comparacion_consumos(page: ft.Page, mostrar_pantalla):
    page.bgcolor = "#FFF8E7"

    # Título grande
    titulo = ft.Text("Comparación de consumo entre turnos", size=34, weight=ft.FontWeight.BOLD, color="#E63946")

    header = ft.Row([
        titulo,
        ft.ElevatedButton("Volver", on_click=lambda e: mostrar_pantalla("admin"), height=40),
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    subtitle = ft.Text("Selecciona dos turnos y un rango de fechas para comparar consumos.", color="#1F1F1F")

    # Controles: Rango de fechas y selección de turnos
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

    turnos = ["Mañana", "Tarde", "Noche"]
    turno_a_dd = ft.Dropdown(label="", options=[ft.dropdown.Option(t) for t in turnos], value=turnos[0], width=180)
    turno_b_dd = ft.Dropdown(label="", options=[ft.dropdown.Option(t) for t in turnos], value=turnos[1], width=180)

    controls = ft.Row([
        ft.Column([
            ft.Text("Fechas:", size=14),
            fechas_dd
        ], spacing=6),
        ft.Column([
            ft.Text("Turno A:", size=14),
            turno_a_dd
        ], spacing=6),
        ft.Column([
            ft.Text("Turno B:", size=14),
            turno_b_dd
        ], spacing=6),
        ft.Column([ft.ElevatedButton("Comparar", on_click=lambda e: actualizar_comparacion())], alignment=ft.MainAxisAlignment.CENTER)
    ], spacing=18)

    # Table container
    tabla_container = ft.Container()

    # Datos simulados de consumo por turno (producto, fecha, turno, cantidad)
    TODAY = date.today()
    def iso(d):
        return d.isoformat()

    SAMPLE = [
        {"fecha": iso(TODAY), "turno": "Mañana", "producto": "Queso", "cantidad": 2.0},
        {"fecha": iso(TODAY), "turno": "Tarde", "producto": "Queso", "cantidad": 1.5},
        {"fecha": iso(TODAY - timedelta(days=1)), "turno": "Mañana", "producto": "Harina", "cantidad": 1.0},
        {"fecha": iso(TODAY - timedelta(days=2)), "turno": "Noche", "producto": "Queso", "cantidad": 0.5},
        {"fecha": iso(TODAY - timedelta(days=5)), "turno": "Tarde", "producto": "Harina", "cantidad": 0.8},
        {"fecha": iso(TODAY.replace(day=1)), "turno": "Mañana", "producto": "Tomate", "cantidad": 0.6},
        {"fecha": iso(TODAY - timedelta(days=3)), "turno": "Tarde", "producto": "Queso", "cantidad": 1.0},
        {"fecha": iso(TODAY - timedelta(days=6)), "turno": "Noche", "producto": "Harina", "cantidad": 0.7},
    ]

    def _parse_date_to_date(val):
        if val is None:
            return None
        if isinstance(val, date) and not isinstance(val, datetime):
            return val
        if isinstance(val, datetime):
            return val.date()
        s = str(val)
        try:
            return datetime.fromisoformat(s).date()
        except Exception:
            pass
        try:
            return datetime.strptime(s, "%Y-%m-%d").date()
        except Exception:
            return None

    def filter_by_date_range(items, field_name, range_label):
        today = date.today()
        result = []
        for it in items:
            d = _parse_date_to_date(it.get(field_name))
            if d is None:
                continue
            if range_label == "Hoy" and d == today:
                result.append(it)
            elif range_label == "Últimos 7 días" and (d >= (today - timedelta(days=6)) and d <= today):
                result.append(it)
            elif range_label == "Este mes" and d.year == today.year and d.month == today.month:
                result.append(it)
            elif range_label == "Año actual" and d.year == today.year:
                result.append(it)
        return result

    def build_comparison_table(turno_a, turno_b, datos):
        # Sumar consumo por producto para cada turno
        suma_a = {}
        suma_b = {}
        productos = set()
        for d in datos:
            prod = d.get("producto")
            t = d.get("turno")
            cant = d.get("cantidad", 0)
            productos.add(prod)
            if t == turno_a:
                suma_a[prod] = suma_a.get(prod, 0) + cant
            if t == turno_b:
                suma_b[prod] = suma_b.get(prod, 0) + cant

        rows = []
        total_a = 0.0
        total_b = 0.0
        for prod in sorted(productos):
            a = suma_a.get(prod, 0)
            b = suma_b.get(prod, 0)
            diff = a - b
            pct = None
            try:
                pct = (diff / b) * 100 if b != 0 else None
            except Exception:
                pct = None
            total_a += a
            total_b += b
            pct_text = f"{pct:.1f}%" if pct is not None else "-"
            rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(prod)),
                ft.DataCell(ft.Text(str(a))),
                ft.DataCell(ft.Text(str(b))),
                ft.DataCell(ft.Text(str(diff))),
                ft.DataCell(ft.Text(pct_text)),
            ]))

        table = ft.DataTable(columns=[
            ft.DataColumn(ft.Text("Producto")),
            ft.DataColumn(ft.Text(f"{turno_a}")),
            ft.DataColumn(ft.Text(f"{turno_b}")),
            ft.DataColumn(ft.Text("Diferencia")),
            ft.DataColumn(ft.Text("% Cambio")),
        ], rows=rows)

        resumen = ft.Container(ft.Column([
            ft.Text(f"Total {turno_a}: {total_a}"),
            ft.Text(f"Total {turno_b}: {total_b}"),
            ft.Text(f"Diferencia total: {total_a - total_b}")
        ], tight=True), padding=8, bgcolor="#FFFFFF", border=ft.border.all(1, ft.Colors.BLACK12))

        return ft.Column([table, ft.Divider(), resumen], spacing=8)

    def actualizar_comparacion(e=None):
        rango = fechas_dd.value or "Últimos 7 días"
        turno_a = turno_a_dd.value or turnos[0]
        turno_b = turno_b_dd.value or turnos[1]
        datos = filter_by_date_range(SAMPLE, "fecha", rango)
        # construir tabla comparativa
        tabla_container.content = build_comparison_table(turno_a, turno_b, datos)
        page.update()

    # Inicializar
    actualizar_comparacion()

    layout = ft.Column([header, ft.Divider(), subtitle, controls, ft.Divider(), tabla_container], spacing=12)
    root = ft.Container(layout, padding=16, bgcolor="#FFF8E7", expand=True)
    return root
