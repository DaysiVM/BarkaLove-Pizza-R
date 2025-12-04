import flet as ft
from datetime import datetime, date, timedelta
import os
import subprocess
import sys
HAS_OPENPYXL = True
HAS_REPORTLAB = True
try:
    from openpyxl import Workbook
except Exception:
    HAS_OPENPYXL = False

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Table as RLTable, TableStyle, Paragraph, Spacer
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
except Exception:
    HAS_REPORTLAB = False

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

    # Container where the selected report table will be shown
    tabla_container = ft.Container()
    # Estado actual mostrado (tipo + datos) para usar en export
    current_state = {"tipo": "Ventas", "datos": []}

    # Export buttons (Excel / PDF)
    def _ensure_export_dir():
        d = os.path.join(os.getcwd(), "reportes_export")
        os.makedirs(d, exist_ok=True)
        return d

    def _show_message(msg):
        page.snack_bar = ft.SnackBar(ft.Text(msg))
        page.snack_bar.open = True
        page.update()

    def get_table_data_for(tipo, datos):
        # Return (headers, rows) for the given tipo and datos (list of dicts)
        if tipo == "Ventas":
            headers = ["Fecha", "Producto", "Cantidad", "Precio unitario", "Total", "Categoría"]
            rows = []
            for d in datos:
                fecha = d.get("fecha", "")
                prod = d.get("producto", "")
                cantidad = d.get("cantidad", 0)
                precio = d.get("precio_unitario", 0.0)
                total = cantidad * precio
                cat = d.get("categoria", "")
                rows.append([fecha, prod, cantidad, precio, total, cat])
            return headers, rows
        if tipo == "Gastos":
            headers = ["Fecha", "Tipo de gasto", "Monto", "Responsable", "Observación"]
            rows = []
            for d in datos:
                rows.append([d.get("fecha", ""), d.get("tipo", ""), d.get("monto", 0.0), d.get("responsable", ""), d.get("observacion", "")])
            return headers, rows
        if tipo == "Inventario":
            headers = ["Producto", "Cantidad consumida", "Cantidad restante", "Fecha del movimiento"]
            rows = []
            for d in datos:
                rows.append([d.get("producto", ""), d.get("cantidad_consumida", 0.0), d.get("cantidad_restante", ""), d.get("fecha", "")])
            return headers, rows
        if tipo == "Daños / Incidencias":
            headers = ["Fecha", "Producto afectado", "Cantidad dañada", "Motivo", "Responsable"]
            rows = []
            for d in datos:
                rows.append([d.get("fecha", ""), d.get("producto", ""), d.get("cantidad_danada", 0), d.get("motivo", ""), d.get("responsable", "")])
            return headers, rows
        return [], []

    def export_to_excel(tipo, datos, rango_label):
        if not HAS_OPENPYXL:
            _show_message("Falta 'openpyxl'. Instálalo: python -m pip install openpyxl")
            return
        # si no vienen datos explícitos, usar el estado actual mostrado
        if datos is None:
            datos = current_state.get("datos", [])
            tipo = current_state.get("tipo", tipo)
        headers, rows = get_table_data_for(tipo, datos)
        if not headers:
            _show_message("No hay datos para exportar")
            return
        dirname = _ensure_export_dir()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{tipo.replace(' ', '_')}_{rango_label.replace(' ', '_')}_{timestamp}.xlsx"
        path = os.path.join(dirname, filename)
        wb = Workbook()
        ws = wb.active
        ws.append(headers)
        for r in rows:
            ws.append(r)
        # Añadir totales/subtotales al final
        total_general, totals_por_categoria, totals_por_dia = compute_summaries(tipo, datos)
        ws.append([])
        ws.append(["Total general", total_general])
        if totals_por_categoria:
            ws.append([])
            ws.append(["Totales por categoría"])
            for cat, val in totals_por_categoria.items():
                ws.append([cat, val])
        if totals_por_dia:
            ws.append([])
            ws.append(["Totales por día"])
            for dia, val in totals_por_dia.items():
                ws.append([dia, val])
        wb.save(path)
        # Intentar abrir el archivo automáticamente
        try:
            if os.name == 'nt':
                os.startfile(path)
            else:
                opener = 'open' if sys.platform == 'darwin' else 'xdg-open'
                subprocess.Popen([opener, path])
            _show_message(f"Exportado Excel: {path}")
        except Exception:
            _show_message(f"Exportado Excel: {path} (no se pudo abrir automáticamente)")

    def export_to_pdf(tipo, datos, rango_label):
        if not HAS_REPORTLAB:
            _show_message("Falta 'reportlab'. Instálalo: python -m pip install reportlab")
            return
        # si no vienen datos explícitos, usar el estado actual mostrado
        if datos is None:
            datos = current_state.get("datos", [])
            tipo = current_state.get("tipo", tipo)
        headers, rows = get_table_data_for(tipo, datos)
        if not headers:
            _show_message("No hay datos para exportar")
            return
        dirname = _ensure_export_dir()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{tipo.replace(' ', '_')}_{rango_label.replace(' ', '_')}_{timestamp}.pdf"
        path = os.path.join(dirname, filename)

        doc = SimpleDocTemplate(path, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []
        elements.append(Paragraph(f"{tipo} - {rango_label}", styles['Title']))
        elements.append(Spacer(1, 12))
        table_data = [headers] + rows
        # Convert all items to strings for PDF rendering
        table_data_str = [[str(cell) for cell in row] for row in table_data]
        t = RLTable(table_data_str, hAlign='LEFT')
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F2F2F2')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('ALIGN', (2, 0), (-2, -1), 'RIGHT'),
        ]))
        elements.append(t)
        # Añadir resumen/ totales debajo de la tabla
        total_general, totals_por_categoria, totals_por_dia = compute_summaries(tipo, datos)
        elements.append(Spacer(1, 12))
        styles = getSampleStyleSheet()
        elements.append(Paragraph(f"Total general: {format_currency(total_general)}", styles['Normal']))
        if totals_por_categoria:
            elements.append(Spacer(1, 6))
            elements.append(Paragraph("Totales por categoría:", styles['Heading4']))
            for cat, val in totals_por_categoria.items():
                elements.append(Paragraph(f"{cat}: {format_currency(val)}", styles['Normal']))
        if totals_por_dia:
            elements.append(Spacer(1, 6))
            elements.append(Paragraph("Totales por día:", styles['Heading4']))
            for dia, val in totals_por_dia.items():
                elements.append(Paragraph(f"{dia}: {format_currency(val)}", styles['Normal']))
        doc.build(elements)
        # Intentar abrir el PDF automáticamente
        try:
            if os.name == 'nt':
                os.startfile(path)
            else:
                opener = 'open' if sys.platform == 'darwin' else 'xdg-open'
                subprocess.Popen([opener, path])
            _show_message(f"Exportado PDF: {path}")
        except Exception:
            _show_message(f"Exportado PDF: {path} (no se pudo abrir automáticamente)")

    # Click handlers for export buttons use the currently selected tipo and rango
    def _export_excel_click(e):
        tipo = tipo_dd.value or "Ventas"
        rango = fechas_dd.value or "Últimos 7 días"
        if tipo == "Ventas":
            datos = filter_by_date_range(SAMPLE_VENTAS, "fecha", rango)
        elif tipo == "Gastos":
            datos = filter_by_date_range(SAMPLE_GASTOS, "fecha", rango)
        elif tipo == "Inventario":
            datos = filter_by_date_range(SAMPLE_INVENTARIO, "fecha", rango)
        elif tipo == "Daños / Incidencias":
            datos = filter_by_date_range(SAMPLE_DANOS, "fecha", rango)
        else:
            datos = []
        export_to_excel(tipo, datos, rango)

    def _export_pdf_click(e):
        tipo = tipo_dd.value or "Ventas"
        rango = fechas_dd.value or "Últimos 7 días"
        if tipo == "Ventas":
            datos = filter_by_date_range(SAMPLE_VENTAS, "fecha", rango)
        elif tipo == "Gastos":
            datos = filter_by_date_range(SAMPLE_GASTOS, "fecha", rango)
        elif tipo == "Inventario":
            datos = filter_by_date_range(SAMPLE_INVENTARIO, "fecha", rango)
        elif tipo == "Daños / Incidencias":
            datos = filter_by_date_range(SAMPLE_DANOS, "fecha", rango)
        else:
            datos = []
        export_to_pdf(tipo, datos, rango)

    # Sample datasets for each tipo de reporte (simulated across ranges for testing)
    TODAY = date.today()
    def iso(d):
        return d.isoformat()

    SAMPLE_VENTAS = [
        {"fecha": iso(TODAY), "producto": "Pizza Hawaiana", "cantidad": 2, "precio_unitario": 10.0, "categoria": "Pizzas"},
        {"fecha": iso(TODAY - timedelta(days=1)), "producto": "Bebida Cola", "cantidad": 3, "precio_unitario": 2.5, "categoria": "Bebidas"},
        {"fecha": iso(TODAY - timedelta(days=5)), "producto": "Pizza Pepperoni", "cantidad": 1, "precio_unitario": 12.0, "categoria": "Pizzas"},
        {"fecha": iso(TODAY - timedelta(days=12)), "producto": "Ensalada", "cantidad": 1, "precio_unitario": 6.0, "categoria": "Entradas"},
        {"fecha": iso(TODAY.replace(day=1)), "producto": "Agua", "cantidad": 4, "precio_unitario": 1.5, "categoria": "Bebidas"},
        {"fecha": iso(date(TODAY.year, 1, 15)), "producto": "Promo Año", "cantidad": 10, "precio_unitario": 8.0, "categoria": "Promociones"},
    ]

    SAMPLE_GASTOS = [
        {"fecha": iso(TODAY), "tipo": "Compra insumos", "monto": 25.0, "responsable": "Juan", "observacion": "Harina y queso"},
        {"fecha": iso(TODAY - timedelta(days=3)), "tipo": "Transporte", "monto": 10.0, "responsable": "María", "observacion": "Reparto"},
        {"fecha": iso(TODAY - timedelta(days=30)), "tipo": "Servicios", "monto": 80.0, "responsable": "Admin", "observacion": "Luz"},
    ]

    SAMPLE_INVENTARIO = [
        {"producto": "Queso", "cantidad_consumida": 2.5, "cantidad_restante": 7.5, "fecha": iso(TODAY)},
        {"producto": "Harina", "cantidad_consumida": 1.0, "cantidad_restante": 9.0, "fecha": iso(TODAY - timedelta(days=6))},
        {"producto": "Tomate", "cantidad_consumida": 0.5, "cantidad_restante": 5.0, "fecha": iso(TODAY.replace(day=2))},
    ]

    SAMPLE_DANOS = [
        {"fecha": iso(TODAY - timedelta(days=2)), "producto": "Bebida Cola", "cantidad_danada": 1, "motivo": "Caída", "responsable": "Pedro"},
        {"fecha": iso(TODAY.replace(month=max(1, TODAY.month-1), day=10)), "producto": "Queso", "cantidad_danada": 0.5, "motivo": "Vencimiento", "responsable": "Ana"},
    ]

    def format_currency(v):
        try:
            return f"${v:,.2f}"
        except Exception:
            return str(v)

    def _parse_date_to_date(val):
        if val is None:
            return None
        if isinstance(val, date) and not isinstance(val, datetime):
            return val
        if isinstance(val, datetime):
            return val.date()
        s = str(val)
        # try ISO first
        try:
            return datetime.fromisoformat(s).date()
        except Exception:
            pass
        # try common formats
        for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S"):
            try:
                return datetime.strptime(s, fmt).date()
            except Exception:
                continue
        return None

    def filter_by_date_range(items, field_name, range_label):
        today = date.today()
        if not items:
            return []
        result = []
        for it in items:
            d = _parse_date_to_date(it.get(field_name))
            if d is None:
                continue
            if range_label == "Hoy":
                if d == today:
                    result.append(it)
            elif range_label == "Últimos 7 días":
                if d >= (today - timedelta(days=6)) and d <= today:
                    result.append(it)
            elif range_label == "Este mes":
                if d.year == today.year and d.month == today.month:
                    result.append(it)
            elif range_label == "Año actual":
                if d.year == today.year:
                    result.append(it)
            else:
                # unknown range, include everything
                result.append(it)
        return result

    def build_totals_box(total_general, totals_por_categoria=None, totals_por_dia=None):
        # Build a compact summary box shown below the table
        lines = []
        lines.append(ft.Text(f"Total general: {format_currency(total_general)}", weight=ft.FontWeight.BOLD))
        if totals_por_categoria:
            for cat, val in totals_por_categoria.items():
                lines.append(ft.Text(f"Total {cat}: {format_currency(val)}"))
        if totals_por_dia:
            for dia, val in totals_por_dia.items():
                lines.append(ft.Text(f"{dia}: {format_currency(val)}"))
        box = ft.Container(ft.Column(lines, tight=True), padding=12, bgcolor="#FFFFFF", border=ft.border.all(1, ft.Colors.BLACK12), width=520)
        return box

    def compute_summaries(tipo, datos):
        total_general = 0.0
        totals_por_categoria = {}
        totals_por_dia = {}
        if not datos:
            return total_general, None, None
        if tipo == "Ventas":
            for d in datos:
                cantidad = d.get("cantidad", 0)
                precio = d.get("precio_unitario", 0.0)
                total = cantidad * precio
                total_general += total
                cat = d.get("categoria", "Sin categoría")
                fecha = d.get("fecha", "")
                totals_por_categoria[cat] = totals_por_categoria.get(cat, 0.0) + total
                totals_por_dia[fecha] = totals_por_dia.get(fecha, 0.0) + total
            return total_general, totals_por_categoria, totals_por_dia
        if tipo == "Gastos":
            for d in datos:
                monto = d.get("monto", 0.0)
                total_general += monto
                tipo_g = d.get("tipo", "")
                fecha = d.get("fecha", "")
                totals_por_categoria[tipo_g] = totals_por_categoria.get(tipo_g, 0.0) + monto
                totals_por_dia[fecha] = totals_por_dia.get(fecha, 0.0) + monto
            return total_general, totals_por_categoria, totals_por_dia
        if tipo == "Inventario":
            for d in datos:
                consumida = d.get("cantidad_consumida", 0.0)
                total_general += consumida
            return total_general, None, None
        if tipo == "Daños / Incidencias":
            for d in datos:
                cant = d.get("cantidad_danada", 0)
                total_general += cant
                prod = d.get("producto", "")
                totals_por_categoria[prod] = totals_por_categoria.get(prod, 0) + cant
            return total_general, totals_por_categoria, None
        return total_general, None, None

    def build_sales_table(data):
        # Columns: Fecha, Producto, Cantidad, Precio unitario, Total, Categoría
        rows = []
        total_general = 0.0
        totals_por_categoria = {}
        totals_por_dia = {}
        for d in data:
            cantidad = d.get("cantidad", 0)
            precio = d.get("precio_unitario", 0.0)
            total = cantidad * precio
            total_general += total
            cat = d.get("categoria", "Sin categoría")
            fecha = d.get("fecha", "")
            totals_por_categoria[cat] = totals_por_categoria.get(cat, 0.0) + total
            totals_por_dia[fecha] = totals_por_dia.get(fecha, 0.0) + total
            row = ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(fecha))),
                ft.DataCell(ft.Text(d.get("producto", ""))),
                ft.DataCell(ft.Text(str(cantidad))),
                ft.DataCell(ft.Text(format_currency(precio))),
                ft.DataCell(ft.Text(format_currency(total))),
                ft.DataCell(ft.Text(cat)),
            ])
            rows.append(row)

        table = ft.DataTable(columns=[
            ft.DataColumn(ft.Text("Fecha")),
            ft.DataColumn(ft.Text("Producto")),
            ft.DataColumn(ft.Text("Cantidad")),
            ft.DataColumn(ft.Text("Precio unitario")),
            ft.DataColumn(ft.Text("Total")),
            ft.DataColumn(ft.Text("Categoría")),
        ], rows=rows)

        summary = build_totals_box(total_general, totals_por_categoria, totals_por_dia)
        return ft.Column([table, ft.Divider(), summary], spacing=8)

    def build_expenses_table(data):
        # Columns: Fecha, Tipo de gasto, Monto, Responsable, Observación
        rows = []
        total_general = 0.0
        totals_por_tipo = {}
        totals_por_dia = {}
        for d in data:
            monto = d.get("monto", 0.0)
            total_general += monto
            tipo = d.get("tipo", "")
            fecha = d.get("fecha", "")
            totals_por_tipo[tipo] = totals_por_tipo.get(tipo, 0.0) + monto
            totals_por_dia[fecha] = totals_por_dia.get(fecha, 0.0) + monto
            rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(fecha)),
                ft.DataCell(ft.Text(tipo)),
                ft.DataCell(ft.Text(format_currency(monto))),
                ft.DataCell(ft.Text(d.get("responsable", ""))),
                ft.DataCell(ft.Text(d.get("observacion", ""))),
            ]))

        table = ft.DataTable(columns=[
            ft.DataColumn(ft.Text("Fecha")),
            ft.DataColumn(ft.Text("Tipo de gasto")),
            ft.DataColumn(ft.Text("Monto")),
            ft.DataColumn(ft.Text("Responsable")),
            ft.DataColumn(ft.Text("Observación")),
        ], rows=rows)

        summary = build_totals_box(total_general, totals_por_tipo, totals_por_dia)
        return ft.Column([table, ft.Divider(), summary], spacing=8)

    def build_inventory_table(data):
        # Columns: Producto, Cantidad consumida, Cantidad restante, Fecha del movimiento
        rows = []
        # For inventory totals we'll sum cantidades consumidas
        total_consumido = 0.0
        for d in data:
            consumida = d.get("cantidad_consumida", 0.0)
            total_consumido += consumida
            rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(d.get("producto", ""))),
                ft.DataCell(ft.Text(str(consumida))),
                ft.DataCell(ft.Text(str(d.get("cantidad_restante", "")))),
                ft.DataCell(ft.Text(d.get("fecha", ""))),
            ]))

        table = ft.DataTable(columns=[
            ft.DataColumn(ft.Text("Producto")),
            ft.DataColumn(ft.Text("Cantidad consumida")),
            ft.DataColumn(ft.Text("Cantidad restante")),
            ft.DataColumn(ft.Text("Fecha del movimiento")),
        ], rows=rows)

        summary = build_totals_box(total_consumido, None, None)
        return ft.Column([table, ft.Divider(), summary], spacing=8)

    def build_damages_table(data):
        # Columns: Fecha, Producto afectado, Cantidad dañada, Motivo, Responsable
        rows = []
        total_danado = 0.0
        totals_por_producto = {}
        for d in data:
            cant = d.get("cantidad_danada", 0)
            total_danado += cant
            prod = d.get("producto", "")
            totals_por_producto[prod] = totals_por_producto.get(prod, 0) + cant
            rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(d.get("fecha", ""))),
                ft.DataCell(ft.Text(prod)),
                ft.DataCell(ft.Text(str(cant))),
                ft.DataCell(ft.Text(d.get("motivo", ""))),
                ft.DataCell(ft.Text(d.get("responsable", ""))),
            ]))

        table = ft.DataTable(columns=[
            ft.DataColumn(ft.Text("Fecha")),
            ft.DataColumn(ft.Text("Producto afectado")),
            ft.DataColumn(ft.Text("Cantidad dañada")),
            ft.DataColumn(ft.Text("Motivo")),
            ft.DataColumn(ft.Text("Responsable")),
        ], rows=rows)

        summary = build_totals_box(total_danado, totals_por_producto, None)
        return ft.Column([table, ft.Divider(), summary], spacing=8)

    def _empty_notice():
        return ft.Column([
            ft.Text("No hay datos para este periodo", color=ft.colors.BLACK54),
        ], tight=True)

    def actualizar_tabla(e=None):
        tipo = tipo_dd.value or "Ventas"
        rango = fechas_dd.value or "Últimos 7 días"
        if tipo == "Ventas":
            datos = filter_by_date_range(SAMPLE_VENTAS, "fecha", rango)
            if not datos:
                tabla_container.content = ft.Column([_empty_notice(), ft.Divider(), build_totals_box(0, None, None)])
            else:
                tabla_container.content = build_sales_table(datos)
        elif tipo == "Gastos":
            datos = filter_by_date_range(SAMPLE_GASTOS, "fecha", rango)
            if not datos:
                tabla_container.content = ft.Column([_empty_notice(), ft.Divider(), build_totals_box(0, None, None)])
            else:
                tabla_container.content = build_expenses_table(datos)
        elif tipo == "Inventario":
            datos = filter_by_date_range(SAMPLE_INVENTARIO, "fecha", rango)
            if not datos:
                tabla_container.content = ft.Column([_empty_notice(), ft.Divider(), build_totals_box(0, None, None)])
            else:
                tabla_container.content = build_inventory_table(datos)
        elif tipo == "Daños / Incidencias":
            datos = filter_by_date_range(SAMPLE_DANOS, "fecha", rango)
            if not datos:
                tabla_container.content = ft.Column([_empty_notice(), ft.Divider(), build_totals_box(0, None, None)])
            else:
                tabla_container.content = build_damages_table(datos)
        else:
            tabla_container.content = ft.Text("Tipo de reporte no soportado")
        # Guardar estado actual mostrado para exportación exacta
        current_state["tipo"] = tipo
        current_state["datos"] = locals().get('datos', [])
        page.update()

    # Conectar cambios de filtros
    tipo_dd.on_change = actualizar_tabla
    fechas_dd.on_change = actualizar_tabla

    # Inicializar con el tipo por defecto
    actualizar_tabla()

    # Export buttons row
    export_buttons = ft.Row([
        ft.ElevatedButton("Exportar Excel", on_click=_export_excel_click),
        ft.ElevatedButton("Exportar PDF", on_click=_export_pdf_click),
    ], spacing=12)

    # Compose main layout including the table container
    layout = ft.Column([header, ft.Divider(), subtitle, controls_column, export_buttons, ft.Divider(), tabla_container], spacing=12)
    root = ft.Container(layout, padding=16, bgcolor=CREMA, expand=True)
    return root
