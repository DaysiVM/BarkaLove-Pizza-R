import flet as ft

NEGRO = "#1F1F1F"
CREMA = "#FFF8E7"


def pantalla_manual_backup(page: ft.Page, mostrar_pantalla):
    page.bgcolor = CREMA

    header = ft.Row([
        ft.Text("Generar Respaldo Manual", size=22, weight=ft.FontWeight.BOLD, color=NEGRO),
        ft.ElevatedButton("Volver", on_click=lambda e: mostrar_pantalla("admin_respaldo"), height=40)
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    # Controles solicitados (paneles claros como en automation_config)
    field_style = dict(bgcolor="white", padding=ft.padding.all(12), border_radius=8)

    tipo_dd = ft.Dropdown(options=[ft.dropdown.Option("Completo"), ft.dropdown.Option("Incremental")], value=None)
    tipo_panel = ft.Container(content=ft.Column([ft.Text("Tipo de Respaldo", weight=ft.FontWeight.W_600, color=NEGRO), tipo_dd], spacing=6), width=520, **field_style)

    destino_dd = ft.Dropdown(options=[ft.dropdown.Option("Carpeta local predeterminada"), ft.dropdown.Option("Servidor/Nube")], value="Carpeta local predeterminada")
    destino_panel = ft.Container(content=ft.Column([ft.Text("Destino del Respaldo", weight=ft.FontWeight.W_600, color=NEGRO), destino_dd], spacing=6), width=520, **field_style)

    compresion_dd = ft.Dropdown(options=[ft.dropdown.Option("Ninguna"), ft.dropdown.Option("Media"), ft.dropdown.Option("Máxima")], value="Ninguna")
    compresion_panel = ft.Container(content=ft.Column([ft.Text("Nivel de Compresión", weight=ft.FontWeight.W_600, color=NEGRO), compresion_dd], spacing=6), width=360, **field_style)

    encriptacion_dd = ft.Dropdown(options=[ft.dropdown.Option("No"), ft.dropdown.Option("AES-256")], value=None)
    encriptacion_panel = ft.Container(content=ft.Column([ft.Text("Encriptación", weight=ft.FontWeight.W_600, color=NEGRO), encriptacion_dd], spacing=6), width=360, **field_style)

    notificacion_dd = ft.Dropdown(options=[ft.dropdown.Option("Ninguna"), ft.dropdown.Option("Mostrar mensaje en la pantalla"), ft.dropdown.Option("Enviar correo electrónico")], value="Ninguna")
    notificacion_panel = ft.Container(content=ft.Column([ft.Text("Notificación al finalizar", weight=ft.FontWeight.W_600, color=NEGRO), notificacion_dd], spacing=6), width=520, **field_style)

    # campo opcional para email si el usuario selecciona enviar correo
    email_tf = ft.TextField(label="Email (si aplica)")

    aviso_overwrite = ft.Text("Este respaldo es manual y puede sobrescribir almacenamiento si seleccionas la misma carpeta.", color=NEGRO)

    def ejecutar_simulacion(e):
        # Validaciones
        if not tipo_dd.value:
            page.snack_bar = ft.SnackBar(ft.Text("Selecciona el Tipo de Respaldo (obligatorio)", color="white"), bgcolor="#E63946")
            page.snack_bar.open = True
            page.update()
            return
        if not encriptacion_dd.value:
            page.snack_bar = ft.SnackBar(ft.Text("Selecciona Encriptación (obligatorio)", color="white"), bgcolor="#E63946")
            page.snack_bar.open = True
            page.update()
            return

        # Abrir diálogo de confirmación con resumen
        resumen = f"Tipo: {tipo_dd.value or '-'}\nDestino: {destino_dd.value or '-'}\nCompresión: {compresion_dd.value or '-'}\nEncriptación: {encriptacion_dd.value or '-'}\nNotificación: {notificacion_dd.value or '-'}"

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar Respaldo Manual", color=NEGRO),
            content=ft.Column([ft.Text("Revise la configuración antes de iniciar:", color=NEGRO), ft.Text(resumen, color=NEGRO)], spacing=8),
            actions=[
                ft.ElevatedButton("Confirmar", on_click=lambda ev, t=tipo_dd.value, d=destino_dd.value, c=compresion_dd.value, enc=encriptacion_dd.value, n=notificacion_dd.value, em=email_tf.value: confirmar_respaldo(ev, t, d, c, enc, n, em), bgcolor="#2A9D8F"),
                ft.TextButton("Cancelar", on_click=lambda ev: (setattr(page, 'dialog', None), page.update())),
            ],
        )
        page.dialog = dialog
        page.dialog.open = True
        page.update()

    def confirmar_respaldo(_ev, tipo, destino, compresion, encriptacion, notificacion, email):
        # Cerrar confirm dialog
        if page.dialog:
            page.dialog.open = False
        # Simular ejecución
        detalle = f"Generando respaldo manual (simulado): {tipo}; destino={destino}; comp={compresion}; enc={encriptacion}; notif={notificacion}"
        if email:
            detalle += f"; email={email}"
        page.snack_bar = ft.SnackBar(ft.Text(detalle, color="white"), bgcolor="#2196F3")
        page.snack_bar.open = True
        page.update()
        # Volver a lista de respaldos
        mostrar_pantalla("admin_respaldo")

    body = ft.Column([
        ft.Container(height=8),
        tipo_panel,
        ft.Container(height=8),
        destino_panel,
        ft.Container(height=8),
        ft.Row([compresion_panel, ft.Container(width=12), encriptacion_panel]),
        ft.Container(height=8),
        notificacion_panel,
        ft.Container(height=8),
        email_tf,
        ft.Container(height=8),
        aviso_overwrite,
        ft.Container(height=12),
        ft.Row([
            ft.ElevatedButton("Guardar", on_click=ejecutar_simulacion, bgcolor="#2A9D8F", width=140),
        ], alignment=ft.MainAxisAlignment.START)
    ], spacing=12)

    root = ft.Container(ft.Column([header, ft.Divider(), body]), padding=16)
    return root
