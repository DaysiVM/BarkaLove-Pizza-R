import flet as ft

NEGRO = "#1F1F1F"
CREMA = "#FFF8E7"


def pantalla_manual_backup(page: ft.Page, mostrar_pantalla):
    page.bgcolor = CREMA

    header = ft.Row([
        ft.Text("Generar Respaldo Manual", size=22, weight=ft.FontWeight.BOLD, color=NEGRO),
        ft.ElevatedButton("Volver", on_click=lambda e: mostrar_pantalla("admin_respaldo"), height=40)
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    # Controles solicitados
    tipo_dd = ft.Dropdown(label="Tipo de Respaldo", options=[ft.dropdown.Option("Completo"), ft.dropdown.Option("Incremental")], value=None)

    destino_dd = ft.Dropdown(label="Destino del Respaldo", options=[ft.dropdown.Option("Carpeta local predeterminada"), ft.dropdown.Option("Servidor/Nube")], value="Carpeta local predeterminada")

    compresion_dd = ft.Dropdown(label="Nivel de Compresión", options=[ft.dropdown.Option("Ninguna"), ft.dropdown.Option("Media"), ft.dropdown.Option("Máxima")], value="Ninguna")

    encriptacion_dd = ft.Dropdown(label="Encriptación", options=[ft.dropdown.Option("No"), ft.dropdown.Option("AES-256")], value=None)

    notificacion_dd = ft.Dropdown(label="Notificación al finalizar", options=[ft.dropdown.Option("Ninguna"), ft.dropdown.Option("Mostrar mensaje en la pantalla"), ft.dropdown.Option("Enviar correo electrónico")], value="Ninguna")

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

        # Simular guardado inmediato
        page.snack_bar = ft.SnackBar(ft.Text("Se guardó correctamente", color="white"), bgcolor="#2A9D8F")
        page.snack_bar.open = True
        page.update()
        # Volver a la pantalla de respaldos
        mostrar_pantalla("admin_respaldo")

    def confirmar_respaldo(_ev, tipo, destino, compresion, encriptacion, notificacion, email):
        # Cerrar confirm dialog
        if page.dialog:
            page.dialog.open = False
        # Simular ejecución
        detalle = f"Generando respaldo manual (simulado) - {tipo}; destino={destino}; comp={compresion}; enc={encriptacion}; notif={notificacion}"
        if email:
            detalle += f"; email={email}"
        page.snack_bar = ft.SnackBar(ft.Text(detalle, color="white"), bgcolor="#2196F3")
        page.snack_bar.open = True
        page.update()
        # Volver a lista de respaldos
        mostrar_pantalla("admin_respaldo")

    body = ft.Column([
        ft.Container(height=8),
        tipo_dd,
        destino_dd,
        compresion_dd,
        encriptacion_dd,
        ft.Container(height=8),
        notificacion_dd,
        email_tf,
        ft.Container(height=8),
        aviso_overwrite,
        ft.Container(height=12),
        ft.Row([
            ft.ElevatedButton("Guardar", on_click=ejecutar_simulacion, bgcolor="#FFD93D", color="#1565C0", width=240),
            ft.Container(width=32),
            ft.TextButton("Volver", on_click=lambda e: mostrar_pantalla("admin_respaldo"), width=240),
        ], alignment=ft.MainAxisAlignment.START)
    ], spacing=8)

    root = ft.Container(ft.Column([header, ft.Divider(), body]), padding=16)
    return root
