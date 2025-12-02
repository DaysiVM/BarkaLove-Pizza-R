import flet as ft
import os
from datetime import datetime

# Colores consistentes con el resto de la app
NEGRO = "#1F1F1F"
CREMA = "#FFF8E7"


def pantalla_admin_respaldo(page: ft.Page, mostrar_pantalla):
    page.bgcolor = CREMA

    # Seguridad: solo admin
    is_admin = page.session.get("admin_auth") is True
    if not is_admin:
        page.snack_bar = ft.SnackBar(ft.Text("Necesitas sesión de admin.", color="white"), bgcolor="#E63946")
        page.snack_bar.open = True
        page.update()
        mostrar_pantalla("admin_login")
        return

    # Header (no modificar según indicación) — mantiene navegación hacia admin
    header = ft.Row(
        [
            ft.Text("Respaldo de datos", size=24, weight=ft.FontWeight.BOLD, color=NEGRO),
            ft.Row(
                [
                    ft.ElevatedButton("Volver", on_click=lambda e: mostrar_pantalla("admin"), height=40),
                ],
                spacing=8
            )
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    # --- DASHBOARD INDICATORS ---
    # Tarjeta: Último respaldo exitoso (destacada a la izquierda)
    ultimo_card = ft.Container(
        bgcolor="white",
        border_radius=12,
        padding=16,
        width=420,
        content=ft.Column(
            [
                ft.Text("Último respaldo exitoso", size=18, weight=ft.FontWeight.W_600, color=NEGRO),
                ft.Text("Fecha y Hora: 01/12/2025 - 08:58 PM", size=14, color=NEGRO),
                ft.Text("Tamaño: 2.1 GB", size=14, color=NEGRO),
                ft.Text("Tipo: Automático", size=14, color=NEGRO),
                ft.Text("Ubicación: C:\\RESPALDOS-DIC2025", size=14, color=NEGRO),
                ft.Container(height=8),
                ft.Text("✔ Correcto", size=16, color="#2A9D8F", weight=ft.FontWeight.W_600),
            ],
            spacing=4,
        ),
    )

    # Tarjeta: Respaldo fallido reciente (a la par)
    fallido_card = ft.Container(
        bgcolor="white",
        border_radius=12,
        padding=16,
        width=420,
        content=ft.Column(
            [
                ft.Text("Respaldo fallido reciente", size=18, weight=ft.FontWeight.W_600, color=NEGRO),
                ft.Text("0 errores detectados", size=14, color=NEGRO),
            ],
            spacing=6,
        ),
    )

    indicators = ft.Row([
        ultimo_card,
        ft.Container(width=16),
        fallido_card,
    ], spacing=12)

    # --- HELPERS ---
    def mostrar_snack(msg: str, color: str = "#2196F3"):
        page.snack_bar = ft.SnackBar(ft.Text(msg, color="white"), bgcolor=color)
        page.snack_bar.open = True
        page.update()

    def ConfirmRestore(_):
        mostrar_snack("Restauración iniciada (placeholder)", "#FFD54F")
        dlg = getattr(page, 'dialog', None)
        if dlg:
            dlg.open = False
            page.update()

    def CancelRestore(_):
        dlg = getattr(page, 'dialog', None)
        if dlg:
            dlg.open = False
            page.update()

    def OpenRestoreModal(backup_info: dict | None = None):
        bi = backup_info or {"fecha": "-", "tipo": "-", "tamaño": "-", "ubicacion": "-", "version": "-"}

        fecha_ctrl = ft.Text(value=str(bi.get("fecha", "-")), color=NEGRO)
        tipo_ctrl = ft.Text(value=str(bi.get("tipo", "-")), color=NEGRO)
        version_ctrl = ft.Text(value=str(bi.get("version", "-")), color=NEGRO)

        radio_group = ft.RadioGroup([])
        radio_system = ft.Radio(value="system", label="¿Restaurar sistema completo?", group=radio_group)
        radio_files = ft.Radio(value="files", label="Restaurar archivos individuales", group=radio_group)

        warning = ft.Container(
            content=ft.Text("La restauración sobrescribirá datos actuales. Esto no se puede deshacer.", color="#5D4037"),
            bgcolor="#FFF9C4",
            padding=ft.padding.all(12),
            border_radius=8,
        )

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Restaurar desde copia de seguridad", color=NEGRO),
            content=ft.Column([
                ft.Row([ft.Text("Versión:", color=NEGRO), version_ctrl], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([ft.Text("Fecha y Hora:", color=NEGRO), fecha_ctrl], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([ft.Text("Tipo:", color=NEGRO), tipo_ctrl], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(height=8),
                radio_system,
                radio_files,
                ft.Container(height=8),
                warning,
            ], spacing=8),
            actions=[
                ft.ElevatedButton("Restaurar Ahora", on_click=ConfirmRestore, bgcolor="#2A9D8F"),
                ft.TextButton("Cancelar", on_click=CancelRestore),
            ],
        )

        page.dialog = dialog
        page.dialog.open = True
        page.update()

    def OpenRestoreModalFromRow(e, backup):
        OpenRestoreModal(backup)

    def MostrarDetalles(backup):
        # Navegar a una pantalla dedicada de detalle
        mostrar_pantalla("respaldo_detalle", backup=backup)

    def MostrarErrores(backup=None):
        if backup is None or backup.get('estado') == 'Correcto':
            mostrar_snack('Sin errores')
            return
        # Para el placeholder mostramos una alerta con texto simulado
        contenido = ft.Column([
            ft.Text(f"Errores de la copia {backup.get('version', '-')}", color=NEGRO),
            ft.Container(height=8),
            ft.Text("(Detalle de errores simulado)", color=NEGRO),
        ])
        dlg = ft.AlertDialog(
            title=ft.Text("Errores en la copia", color=NEGRO),
            content=contenido,
            actions=[ft.TextButton("Cerrar", on_click=lambda e: (setattr(page, 'dialog', None), page.update()))],
        )
        page.dialog = dlg
        page.dialog.open = True
        page.update()

    def RunManualBackup(_event, tipo_ctrl=None):
        tipo = tipo_ctrl.value if tipo_ctrl is not None else "-"
        mostrar_snack(f"Generando respaldo manual (simulado) - {tipo}")
        dlg = getattr(page, 'dialog', None)
        if dlg:
            dlg.open = False
            page.update()

    def OpenManualBackupModal(_):
        tipo_dd = ft.Dropdown(options=[ft.dropdown.Option("Completo"), ft.dropdown.Option("Incremental")], value="Completo")
        modal = ft.AlertDialog(
            title=ft.Text("Generar Respaldo Manual", color=NEGRO),
            content=ft.Column([
                ft.Text("Selecciona tipo de respaldo:", color=NEGRO),
                tipo_dd,
            ], spacing=8),
            actions=[
                ft.ElevatedButton("Iniciar", on_click=lambda e, td=tipo_dd: RunManualBackup(e, td), bgcolor="#FFD93D", color="#1565C0"),
                ft.TextButton("Cerrar", on_click=lambda e: (setattr(page, 'dialog', None), page.update())),
            ],
        )
        page.dialog = modal
        page.dialog.open = True
        page.update()

    def OpenBackupFolder(_):
        ruta = r"C:\RESPALDOS-DIC2025"
        try:
            if os.path.exists(ruta):
                os.startfile(ruta)
                mostrar_snack(f"Carpeta abierta: {ruta}")
            else:
                mostrar_snack(f"Ruta no encontrada: {ruta}", "#E63946")
        except Exception as ex:
            mostrar_snack(f"Error abriendo carpeta: {ex}", "#E63946")

    def SaveAutomationConfig(_event=None, freq_ctrl=None, retention_ctrl=None, default_ctrl=None):
        try:
            freq = freq_ctrl.value if freq_ctrl is not None else "-"
            retention = retention_ctrl.value if retention_ctrl is not None else "-"
            default = default_ctrl.value if default_ctrl is not None else "-"
            mostrar_snack(f"Configuración guardada: {freq}, retención={retention}, tipo={default}")
        except Exception:
            mostrar_snack("Error guardando configuración", "#E63946")
        dlg = getattr(page, 'dialog', None)
        if dlg:
            dlg.open = False
            page.update()

    def BackToBackupScreen(_):
        dlg = getattr(page, 'dialog', None)
        if dlg:
            dlg.open = False
            page.update()

    def OpenAutomationConfig(_):
        freq_dd = ft.Dropdown(options=[ft.dropdown.Option("Diario"), ft.dropdown.Option("Semanal"), ft.dropdown.Option("Mensual")], value="Diario")
        retention_tf = ft.TextField(value="7")
        default_dd = ft.Dropdown(options=[ft.dropdown.Option("Completo"), ft.dropdown.Option("Incremental")], value="Completo")

        modal = ft.AlertDialog(
            title=ft.Text("Configurar Automatización", color=NEGRO),
            content=ft.Column([
                ft.Text("Frecuencia:", color=NEGRO),
                freq_dd,
                ft.Container(height=8),
                ft.Text("Retención (cantidad de copias):", color=NEGRO),
                retention_tf,
                ft.Container(height=8),
                ft.Text("Tipo de backup predeterminado:", color=NEGRO),
                default_dd,
            ], spacing=8),
            actions=[
                ft.ElevatedButton("Guardar", on_click=lambda e, f=freq_dd, r=retention_tf, d=default_dd: SaveAutomationConfig(e, f, r, d), bgcolor="#FFD93D", color="#1565C0"),
                ft.TextButton("Volver", on_click=BackToBackupScreen),
            ],
        )
        page.dialog = modal
        page.dialog.open = True
        page.update()

    # --- Botones de acción ---
    btn_manual = ft.ElevatedButton("Generar Respaldo Manual", bgcolor="#FFD93D", color="#1565C0", on_click=lambda e: mostrar_pantalla("manual_backup"), height=44)
    btn_automation = ft.ElevatedButton("Configurar Automatización", bgcolor="#FFD93D", color="#1565C0", on_click=lambda e: mostrar_pantalla("automation_config"), height=44)

    actions_row = ft.Row([btn_manual, ft.Container(width=12), btn_automation], alignment=ft.MainAxisAlignment.START)

    # --- Tabla de backups ---
    backups = [
        {"fecha": "01/12/2025 - 08:58 PM", "tipo": "Completo", "tamaño": "2.1 GB", "estado": "Correcto", "ubicacion": "Servidor/Nube", "version": "v15"},
        {"fecha": "01/12/2025 - 06:00 AM", "tipo": "Incremental", "tamaño": "230 MB", "estado": "Correcto", "ubicacion": "Servidor", "version": "v14"},
        {"fecha": "30/11/2025 - 08:00 PM", "tipo": "Completo", "tamaño": "2.0 GB", "estado": "Fallido", "ubicacion": "Servidor", "version": "v13"},
    ]

    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Fecha y Hora", color=NEGRO)),
            ft.DataColumn(ft.Text("Tipo", color=NEGRO)),
            ft.DataColumn(ft.Text("Tamaño", color=NEGRO)),
            ft.DataColumn(ft.Text("Estado", color=NEGRO)),
            ft.DataColumn(ft.Text("Ubicación", color=NEGRO)),
            ft.DataColumn(ft.Text("Versión", color=NEGRO)),
            ft.DataColumn(ft.Text("Acción", color=NEGRO)),
        ],
        rows=[],
        width="100%",
    )

    for b in backups:
        estado_color = "#2A9D8F" if b["estado"] == "Correcto" else "#D32F2F"
        action_row = ft.Row([
            ft.TextButton("Restaurar", on_click=lambda e, bk=b: OpenRestoreModalFromRow(e, bk)),
            ft.TextButton("Detalles", on_click=lambda e, bk=b: MostrarDetalles(bk)),
            ft.TextButton("Errores", on_click=lambda e, bk=b: MostrarErrores(bk)),
        ], spacing=6)

        row = ft.DataRow(cells=[
            ft.DataCell(ft.Text(b["fecha"], color=NEGRO)),
            ft.DataCell(ft.Text(b["tipo"], color=NEGRO)),
            ft.DataCell(ft.Text(b["tamaño"], color=NEGRO)),
            ft.DataCell(ft.Text(b["estado"], color=estado_color)),
            ft.DataCell(ft.Text(b["ubicacion"], color=NEGRO)),
            ft.DataCell(ft.Text(b["version"], color=NEGRO)),
            ft.DataCell(action_row),
        ])
        table.rows.append(row)

    layout = ft.Column([
        header,
        ft.Divider(),
        indicators,
        ft.Container(height=12),
        ft.Text("Restauración", size=20, weight=ft.FontWeight.W_600, color=NEGRO),
        ft.Text("Selecciona una copia de la tabla y presiona 'Restaurar' para abrir el panel de restauración.", color=NEGRO),
        ft.Container(height=12),
        actions_row,
        ft.Container(height=16),
        ft.Text("Copias de Seguridad Realizadas", size=18, weight=ft.FontWeight.W_600, color=NEGRO),
        ft.Container(table, expand=True),
    ], spacing=12)

    root = ft.Container(layout, padding=16)
    return root


def mostrar_msg(page: ft.Page, texto: str):
    page.snack_bar = ft.SnackBar(ft.Text(texto, color="white"), bgcolor="#2196F3")
    page.snack_bar.open = True
    page.update()
