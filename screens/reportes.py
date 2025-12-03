import flet as ft
from datetime import datetime, timedelta
import json
import os

# Colores coherentes
ROJO = "#E63946"
CREMA = "#FFF8E7"
NEGRO = "#1F1F1F"


def pantalla_reportes(page: ft.Page, mostrar_pantalla):
    page.bgcolor = CREMA

    # --- Header: título + selector de tipo ---
    tipo_dd = ft.Dropdown(
        label="Tipo de reporte",
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
        ft.Text("Reportes Históricos", size=26, weight=ft.FontWeight.BOLD, color=ROJO, expand=True),
        ft.Row([
            ft.Text("Tipo de reporte:", size=14, color=NEGRO),
            tipo_dd,
            ft.ElevatedButton("Volver", on_click=lambda e: mostrar_pantalla("admin"), height=40),
        ], spacing=8)
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    # --- Filtros ---
    # Date pickers (DatePicker doesn't accept a 'label' kwarg; show labels separately)
    hoy = datetime.now().date()
    fecha_inicio = ft.DatePicker(value=hoy - timedelta(days=7))
    fecha_fin = ft.DatePicker(value=hoy)

    # Quick ranges
    def aplicar_rango(delta_days: int | None, start_of_month: bool = False, this_year: bool = False):
        if this_year:
            fecha_inicio.value = datetime(hoy.year, 1, 1).date()
            fecha_fin.value = hoy
        elif start_of_month:
            fecha_inicio.value = datetime(hoy.year, hoy.month, 1).date()
            fecha_fin.value = hoy
        elif delta_days is not None:
            fecha_inicio.value = (hoy - timedelta(days=delta_days)).date()
            fecha_fin.value = hoy
        page.update()

    btn_hoy = ft.ElevatedButton("Hoy", on_click=lambda e: aplicar_rango(0), height=36)
    btn_7 = ft.ElevatedButton("Últimos 7 días", on_click=lambda e: aplicar_rango(7), height=36)
    btn_mes = ft.ElevatedButton("Este mes", on_click=lambda e: aplicar_rango(None, start_of_month=True), height=36)
    btn_ano = ft.ElevatedButton("Año actual", on_click=lambda e: aplicar_rango(None, False, True), height=36)

    # --- Data table area ---
    table = ft.DataTable(columns=[], rows=[], width="100%")

    # Totales container
    totals_box = ft.Container(content=ft.Text(""), padding=12, bgcolor="white", border_radius=8)

    # --- Export bar (fixed under results) ---
    def export_excel(_):
        # try to export currently visible rows to CSV (Excel-compatible)
        try:
            export_path = os.path.join(os.getcwd(), "reportes_export.csv")
            rows = []
            for r in table.rows:
                rowvals = []
                for c in r.cells:
                    # get textual representation
                    txt = ""
                    if hasattr(c.content, 'value'):
                        txt = str(c.content.value)
                    else:
                        txt = str(c)
                    rowvals.append(txt)
                rows.append(rowvals)
            import csv
            with open(export_path, "w", newline='', encoding='utf-8') as f:
                w = csv.writer(f)
                # headers
                headers = [col.label.value if hasattr(col.label, 'value') else str(col.label) for col in table.columns]
                w.writerow(headers)
                for r in rows:
                    w.writerow(r)
            page.snack_bar = ft.SnackBar(ft.Text(f"Exportado CSV: {export_path}"), bgcolor="#2A9D8F")
            page.snack_bar.open = True
            page.update()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error exportando: {ex}"), bgcolor=ROJO)
            page.snack_bar.open = True
            page.update()

    def export_pdf(_):
        # Placeholder: inform user
        page.snack_bar = ft.SnackBar(ft.Text("Exportar a PDF: requiere librería adicional (opcional)."), bgcolor="#2196F3")
        page.snack_bar.open = True
        page.update()

    def refresh(_):
        cargar_y_actualizar()

    btn_export_xlsx = ft.ElevatedButton("Exportar Excel", icon=ft.Icon(ft.Icons.INSERT_DRIVE_FILE), on_click=export_excel)
    btn_export_pdf = ft.ElevatedButton("Exportar PDF", icon=ft.Icon(ft.Icons.PICTURE_AS_PDF), on_click=export_pdf)
    btn_refresh = ft.ElevatedButton("↻ Actualizar", on_click=refresh)

    export_bar = ft.Row([btn_export_xlsx, ft.Container(width=8), btn_export_pdf, ft.Container(expand=True), ft.IconButton(ft.Icons.REFRESH, on_click=refresh)], alignment=ft.MainAxisAlignment.START)

    # --- Data sources (sample) ---
    pedidos_path = os.path.join(os.getcwd(), "utils", "pedidos_data.json")
    pedidos_data = []
    try:
        with open(pedidos_path, "r", encoding="utf-8") as f:
            pedidos_data = json.load(f)
    except Exception:
        pedidos_data = []

    # sample gastos/inventario/daños (placeholders)
    gastos = [
        {"fecha": "2025-11-01", "tipo": "Compras", "monto": 120.5, "responsable": "Jose", "obs": "Ingredientes"},
        {"fecha": "2025-11-05", "tipo": "Servicios", "monto": 80.0, "responsable": "Ana", "obs": "Electricidad"},
    ]
    inventario = [
        {"producto": "Queso", "consumida": 20, "restante": 80, "fecha": "2025-11-10"},
    ]
    danos = [
        {"fecha": "2025-11-12", "producto": "Harina", "cantidad": 5, "motivo": "Humedad", "responsable": "Luis"},
    ]

    # --- Helpers: build table based on type and dates ---
    def validar_fechas():
        si = fecha_inicio.value
        sf = fecha_fin.value
        if si is None or sf is None:
            return False, "Selecciona fechas válidas"
        if si > sf:
            return False, "Rango inválido: fecha inicio > fecha fin"
        return True, ""

    def aplicar_filtros(e=None):
        ok, msg = validar_fechas()
        if not ok:
            page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor=ROJO)
            page.snack_bar.open = True
            page.update()
            return
        cargar_y_actualizar()

    btn_apply = ft.ElevatedButton("Aplicar Filtros", on_click=aplicar_filtros, bgcolor="#2196F3", color="white", height=40)

    def parse_date(s: str):
        try:
            return datetime.fromisoformat(s).date()
        except Exception:
            try:
                return datetime.strptime(s, "%Y-%m-%d").date()
            except Exception:
                return None


    def cargar_y_actualizar():
        # Limpia tabla y reconstruye según tipo
        t = tipo_dd.value
        si = fecha_inicio.value
        sf = fecha_fin.value
        table.rows.clear()
        table.columns.clear()

        if t == "Ventas":
            # columnas ventas
            table.columns.extend([
                ft.DataColumn(ft.Text("Fecha", color=NEGRO)),
                ft.DataColumn(ft.Text("Producto", color=NEGRO)),
                ft.DataColumn(ft.Text("Cantidad", color=NEGRO)),
                ft.DataColumn(ft.Text("Precio unitario", color=NEGRO)),
                ft.DataColumn(ft.Text("Total", color=NEGRO)),
                ft.DataColumn(ft.Text("Categoría", color=NEGRO)),
            ])
            total_general = 0.0
            # usar pedidos_data
            for p in pedidos_data:
                dt = parse_date(p.get("fecha", ""))
                if dt is None:
                    continue
                ddate = dt.date()
                if si and sf and not (si <= ddate <= sf):
                    continue
                producto = p.get("receta_tipo", "-")
                cantidad = 1
                precio = 8.5
                total = cantidad * precio
                categoria = p.get("tamano", "-")
                total_general += total
                row = ft.DataRow(cells=[
                    ft.DataCell(ft.Text(dt.strftime("%Y-%m-%d %H:%M:%S"), color=NEGRO)),
                    ft.DataCell(ft.Text(producto, color=NEGRO)),
                    ft.DataCell(ft.Text(str(cantidad), color=NEGRO)),
                    ft.DataCell(ft.Text(f"{precio:.2f}", color=NEGRO)),
                    ft.DataCell(ft.Text(f"{total:.2f}", color=NEGRO)),
                    ft.DataCell(ft.Text(categoria, color=NEGRO)),
                ])
                table.rows.append(row)
            totals_box.content = ft.Column([
                ft.Text(f"Total general: {total_general:.2f}", weight=ft.FontWeight.BOLD, color=NEGRO),
            ])

        elif t == "Gastos":
            table.columns.extend([
                ft.DataColumn(ft.Text("Fecha", color=NEGRO)),
                ft.DataColumn(ft.Text("Tipo de gasto", color=NEGRO)),
                ft.DataColumn(ft.Text("Monto", color=NEGRO)),
                ft.DataColumn(ft.Text("Responsable", color=NEGRO)),
                ft.DataColumn(ft.Text("Observación", color=NEGRO)),
            ])
            total_general = 0.0
            for g in gastos:
                try:
                    ddate = datetime.fromisoformat(g["fecha"]).date()
                except Exception:
                    ddate = None
                if si and sf and ddate and not (si <= ddate <= sf):
                    continue
                total_general += float(g.get("monto", 0))
                row = ft.DataRow(cells=[
                    ft.DataCell(ft.Text(g.get("fecha"), color=NEGRO)),
                    ft.DataCell(ft.Text(g.get("tipo"), color=NEGRO)),
                    ft.DataCell(ft.Text(f"{g.get('monto')}", color=NEGRO)),
                    ft.DataCell(ft.Text(g.get("responsable"), color=NEGRO)),
                    ft.DataCell(ft.Text(g.get("obs"), color=NEGRO)),
                ])
                table.rows.append(row)
            totals_box.content = ft.Column([
                ft.Text(f"Total gastos: {total_general:.2f}", weight=ft.FontWeight.BOLD, color=NEGRO),
            ])

        elif t == "Inventario":
            table.columns.extend([
                ft.DataColumn(ft.Text("Producto", color=NEGRO)),
                ft.DataColumn(ft.Text("Cantidad consumida", color=NEGRO)),
                ft.DataColumn(ft.Text("Cantidad restante", color=NEGRO)),
                ft.DataColumn(ft.Text("Fecha del movimiento", color=NEGRO)),
            ])
            for it in inventario:
                row = ft.DataRow(cells=[
                    ft.DataCell(ft.Text(it.get("producto"), color=NEGRO)),
                    ft.DataCell(ft.Text(str(it.get("consumida")), color=NEGRO)),
                    ft.DataCell(ft.Text(str(it.get("restante")), color=NEGRO)),
                    ft.DataCell(ft.Text(it.get("fecha"), color=NEGRO)),
                ])
                table.rows.append(row)
            totals_box.content = ft.Column([
                ft.Text("Total por producto: ver columna 'Cantidad restante'", color=NEGRO),
            ])

        else:  # Daños
            table.columns.extend([
                ft.DataColumn(ft.Text("Fecha", color=NEGRO)),
                ft.DataColumn(ft.Text("Producto afectado", color=NEGRO)),
                ft.DataColumn(ft.Text("Cantidad dañada", color=NEGRO)),
                ft.DataColumn(ft.Text("Motivo", color=NEGRO)),
                ft.DataColumn(ft.Text("Responsable", color=NEGRO)),
            ])
            for d in danos:
                row = ft.DataRow(cells=[
                    ft.DataCell(ft.Text(d.get("fecha"), color=NEGRO)),
                    ft.DataCell(ft.Text(d.get("producto"), color=NEGRO)),
                    ft.DataCell(ft.Text(str(d.get("cantidad")), color=NEGRO)),
                    ft.DataCell(ft.Text(d.get("motivo"), color=NEGRO)),
                    ft.DataCell(ft.Text(d.get("responsable"), color=NEGRO)),
                ])
                table.rows.append(row)
            totals_box.content = ft.Column([
                ft.Text("Total daños registrados: " + str(len(danos)), color=NEGRO),
            ])

        page.update()

    # inicializar tabla
    cargar_y_actualizar()

    # --- Layout ---
    filtros = ft.Column([
        ft.Text("Rango rápido:"),
        ft.Row([btn_hoy, btn_7, btn_mes, btn_ano], spacing=8),
        ft.Row([
            ft.Column([ft.Text("Desde"), fecha_inicio]),
            ft.Container(width=12),
            ft.Column([ft.Text("Hasta"), fecha_fin]),
            ft.Container(width=12),
            btn_apply,
        ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.START),
    ], spacing=8, width=520)

    content = ft.Column([
        ft.Container(table, expand=True),
        ft.Container(height=8),
        totals_box,
        ft.Divider(),
        export_bar,
    ], expand=True)

    layout = ft.Column([
        header,
        ft.Divider(),
        ft.Row([filtros, content], spacing=16, expand=True),
    ], spacing=12, expand=True)

    root = ft.Container(layout, padding=16, bgcolor=CREMA, expand=True)
    return root
