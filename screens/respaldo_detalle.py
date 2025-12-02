import flet as ft

NEGRO = "#1F1F1F"
CREMA = "#FFF8E7"


def pantalla_respaldo_detalle(page: ft.Page, backup: dict | None, mostrar_pantalla):
    page.bgcolor = CREMA

    b = backup or {"fecha": "-", "tipo": "-", "tamaño": "-", "estado": "-", "ubicacion": "-", "version": "-"}

    header = ft.Row([
        ft.Text("Detalle de copia", size=22, weight=ft.FontWeight.BOLD, color=NEGRO),
        ft.ElevatedButton("Volver", on_click=lambda e: mostrar_pantalla("admin_respaldo"), height=40)
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    body = ft.Column([
        ft.Container(height=8),
        ft.Text(f"Versión: {b.get('version')}", color=NEGRO, size=16),
        ft.Text(f"Fecha y Hora: {b.get('fecha')}", color=NEGRO),
        ft.Text(f"Tipo: {b.get('tipo')}", color=NEGRO),
        ft.Text(f"Tamaño: {b.get('tamaño')}", color=NEGRO),
        ft.Text(f"Ubicación: {b.get('ubicacion')}", color=NEGRO),
        ft.Text(f"Estado: {b.get('estado')}", color=NEGRO),
        ft.Container(height=16),
        ft.Row([
            ft.ElevatedButton("Restaurar esta copia", on_click=lambda e: _confirm_restore_dialog(page, b, mostrar_pantalla), width=300)
        ], alignment=ft.MainAxisAlignment.CENTER)
    ], spacing=8)

    root = ft.Container(ft.Column([header, ft.Divider(), body]), padding=16)
    return root


def _confirm_restore(page: ft.Page):
    page.snack_bar = ft.SnackBar(ft.Text("Restauración iniciada (simulada)", color="white"), bgcolor="#FFD54F")
    page.snack_bar.open = True
    page.update()


def _confirm_restore_dialog(page: ft.Page, backup: dict | None, mostrar_pantalla):
    b = backup or {"version": "-", "fecha": "-", "tipo": "-"}
    contenido = ft.Column([
        ft.Text(f"Versión: {b.get('version')}", color=NEGRO),
        ft.Text(f"Fecha: {b.get('fecha')}", color=NEGRO),
        ft.Text(f"Tipo: {b.get('tipo')}", color=NEGRO),
        ft.Container(height=8),
        ft.Text("La restauración sobrescribirá datos actuales. ¿Desea continuar?", color=NEGRO),
    ], spacing=6)

    def _do_restore(ev):
        # cerrar dialog
        dlg = getattr(page, 'dialog', None)
        if dlg:
            dlg.open = False
        # simular acción de restauración
        page.snack_bar = ft.SnackBar(ft.Text("Restauración iniciada (simulada)", color="white"), bgcolor="#FFD54F")
        page.snack_bar.open = True
        page.update()
        # regresar a la lista de respaldos
        mostrar_pantalla("admin_respaldo")

    dlg = ft.AlertDialog(
        title=ft.Text("Confirmar restauración", color=NEGRO),
        content=contenido,
        actions=[
            ft.ElevatedButton("Confirmar", on_click=_do_restore, bgcolor="#2A9D8F"),
            ft.TextButton("Salir", on_click=lambda e: (setattr(page, 'dialog', None), mostrar_pantalla("admin_respaldo"))),
        ],
    )
    page.dialog = dlg
    page.dialog.open = True
    page.update()


def _open_folder(page: ft.Page, ruta: str | None):
    ruta_real = ruta or r"C:\RESPALDOS-DIC2025"
    try:
        import os
        if os.path.exists(ruta_real):
            os.startfile(ruta_real)
            page.snack_bar = ft.SnackBar(ft.Text(f"Carpeta abierta: {ruta_real}", color="white"), bgcolor="#2196F3")
        else:
            page.snack_bar = ft.SnackBar(ft.Text(f"Ruta no encontrada: {ruta_real}", color="white"), bgcolor="#E63946")
    except Exception as ex:
        page.snack_bar = ft.SnackBar(ft.Text(f"Error abriendo carpeta: {ex}", color="white"), bgcolor="#E63946")
    page.snack_bar.open = True
    page.update()
