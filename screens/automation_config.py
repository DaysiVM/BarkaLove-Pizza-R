import flet as ft

# Colores consistentes con la app
NEGRO = "#1F1F1F"
CREMA = "#FFF8E7"


def pantalla_automation_config(page: ft.Page, mostrar_pantalla):
    page.bgcolor = CREMA

    # Header con título y volver
    header = ft.Row(
        [
            ft.Text("Configurar Automatización de Respaldos", size=24, weight=ft.FontWeight.BOLD, color=NEGRO),
            ft.Row([
                ft.ElevatedButton("Volver", on_click=lambda e: mostrar_pantalla("admin_respaldo"), height=40),
            ], spacing=8),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    # Controles: envolvemos cada control en un contenedor blanco con padding para mayor claridad
    freq_dd = ft.Dropdown(
        options=[ft.dropdown.Option("Diario"), ft.dropdown.Option("Semanal"), ft.dropdown.Option("Mensual")],
        value=None,
    )

    hora_tf = ft.TextField(hint_text="HH:MM (24h)")

    retencion_tf = ft.TextField(value="7", hint_text="Ej: 7 (días o versiones)")

    tipo_dd = ft.Dropdown(
        options=[ft.dropdown.Option("Completo"), ft.dropdown.Option("Incremental")],
        value=None,
    )

    destino_dd = ft.Dropdown(
        options=[
            ft.dropdown.Option(r"Carpeta local predeterminada (C:\\RESPALDOS-DIC2025)"),
            ft.dropdown.Option("Servidor/Nube"),
        ],
        value=None,
    )

    def mostrar_snack(msg: str, color: str = "#2196F3"):
        page.snack_bar = ft.SnackBar(ft.Text(msg, color="white"), bgcolor=color)
        page.snack_bar.open = True
        page.update()

    def validar_hora(h: str) -> bool:
        try:
            parts = h.split(":")
            if len(parts) != 2:
                return False
            hh = int(parts[0])
            mm = int(parts[1])
            return 0 <= hh <= 23 and 0 <= mm <= 59
        except Exception:
            return False

    def guardar_config(e):
        freq = freq_dd.value
        tipo = tipo_dd.value
        hora = hora_tf.value.strip() if hora_tf.value else ""
        ret = retencion_tf.value.strip() if retencion_tf.value else ""

        if not freq:
            mostrar_snack("Seleccione la frecuencia de backups", "#E63946")
            return
        if not tipo:
            mostrar_snack("Seleccione el tipo predeterminado de backup", "#E63946")
            return
        if hora and not validar_hora(hora):
            mostrar_snack("Hora inválida. Use formato HH:MM (24h)", "#E63946")
            return

        # validar retención como entero positivo
        try:
            ret_i = int(ret)
            if not (1 <= ret_i <= 365):
                mostrar_snack("Retención debe estar entre 1 y 365", "#E63946")
                return
        except Exception:
            mostrar_snack("Retención inválida (ingrese un número)", "#E63946")
            return

        destino = destino_dd.value or "No especificado"

        # Guardar la configuración en session (simulación de persistencia)
        config = {
            "frecuencia": freq,
            "hora": hora or None,
            "retencion": ret_i,
            "tipo": tipo,
            "destino": destino,
            "guardado_en": str(ft.datetime.datetime.now()) if hasattr(ft, 'datetime') else None,
        }
        try:
            page.session["automation_config"] = config
        except Exception:
            # page.session puede no estar disponible en algunos entornos; simplemente mostrar guardado
            pass

        # Confirmación visual y volver
        mostrar_snack(f"Automatización guardada: {freq}, {hora or 'hora no definida'}, retención={ret_i}, tipo={tipo}")
        mostrar_pantalla("admin_respaldo")

    # Botones (solo Guardar — el Volver está disponible en la navegación principal)
    btn_guardar = ft.ElevatedButton("Guardar", on_click=guardar_config, bgcolor="#2A9D8F", width=140)

    # Layout principal: cada campo en su propio panel para evitar solapamientos
    field_style = dict(bgcolor="white", padding=ft.padding.all(12), border_radius=8)

    freq_panel = ft.Container(content=ft.Column([ft.Text("Frecuencia de backups", weight=ft.FontWeight.W_600, color=NEGRO), freq_dd], spacing=6), width=560, **field_style)
    hora_panel = ft.Container(content=ft.Column([ft.Text("Hora de ejecución", weight=ft.FontWeight.W_600, color=NEGRO), hora_tf], spacing=6), width=360, **field_style)
    retencion_panel = ft.Container(content=ft.Column([ft.Text("Retención de copias", weight=ft.FontWeight.W_600, color=NEGRO), retencion_tf], spacing=6), width=300, **field_style)
    tipo_panel = ft.Container(content=ft.Column([ft.Text("Tipo predeterminado de backup", weight=ft.FontWeight.W_600, color=NEGRO), tipo_dd], spacing=6), width=360, **field_style)
    destino_panel = ft.Container(content=ft.Column([ft.Text("Destino de almacenamiento (opcional)", weight=ft.FontWeight.W_600, color=NEGRO), destino_dd], spacing=6), width=560, **field_style)

    body = ft.Column(
        [
            header,
            ft.Divider(),
            ft.Container(height=8),
            freq_panel,
            ft.Container(height=8),
            ft.Row([hora_panel, ft.Container(width=12), retencion_panel]),
            ft.Container(height=8),
            tipo_panel,
            ft.Container(height=8),
            destino_panel,
            ft.Container(height=16),
            ft.Row([btn_guardar], alignment=ft.MainAxisAlignment.START),
        ],
        spacing=12,
    )

    root = ft.Container(body, padding=16)
    return root
