import flet as ft

ROJO = "#E63946"
CREMA = "#FFF8E7"
NEGRO = "#1F1F1F"
GRIS = "#9E9E9E"
AZUL = "#2196F3"


def pantalla_programar_mantenimiento(page: ft.Page, mostrar_pantalla, title: str | None = None):
    page.bgcolor = CREMA

    header = ft.Row([
        ft.Text("Programar mantenimiento", size=24, color=AZUL, weight=ft.FontWeight.BOLD, expand=True),
        ft.ElevatedButton("Volver", bgcolor=AZUL, color="white", height=36, on_click=lambda e: mostrar_pantalla("admin_indicadores")),
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    titulo = ft.Text(title or "Programar mantenimiento", size=16, weight=ft.FontWeight.W_700, color=NEGRO)

    lbl = ft.Text("Selecciona la fecha de mantenimiento:", size=14, color=NEGRO)
    date_picker = ft.DatePicker()

    def guardar(e):
        # Guardar en session (simple persistencia en memoria)
        scheduled = page.session.get("scheduled_maint", [])
        scheduled.append({
            "title": title,
            "date": date_picker.value.isoformat() if date_picker.value is not None else "",
        })
        page.session["scheduled_maint"] = scheduled
        page.snack_bar = ft.SnackBar(ft.Text("Mantenimiento programado."), bgcolor=AZUL)
        page.snack_bar.open = True
        page.update()
        mostrar_pantalla("admin_indicadores")

    btn_save = ft.ElevatedButton("Guardar", bgcolor=AZUL, color="white", on_click=guardar)
    btn_cancel = ft.TextButton("Cancelar", on_click=lambda e: mostrar_pantalla("admin_indicadores"))

    body = ft.Column([
        titulo,
        ft.Container(height=8),
        lbl,
        date_picker,
        ft.Container(height=12),
        ft.Row([btn_save, ft.Container(width=12), btn_cancel], alignment=ft.MainAxisAlignment.START)
    ], spacing=8)

    layout = ft.Column([header, ft.Divider(), body], spacing=12)
    root = ft.Container(layout, padding=16, bgcolor=CREMA, expand=True)
    return root
