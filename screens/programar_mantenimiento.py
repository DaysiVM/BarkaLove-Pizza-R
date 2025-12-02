import flet as ft
from datetime import date, timedelta

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

    # Dropdown fecha rápida
    date_options = ["Hoy", "Mañana", "En 7 días"]
    ddl_date = ft.Dropdown(
        width=220,
        value="Hoy",
        options=[ft.dropdown.Option(o) for o in date_options],
    )

    # Dropdown hora
    time_options = ["07:00 AM", "07:00 PM"]
    ddl_time = ft.Dropdown(
        width=160,
        value="07:00 AM",
        options=[ft.dropdown.Option(o) for o in time_options],
    )

    def compute_selected_date():
        today = date.today()
        v = ddl_date.value
        if v == "Hoy":
            return today
        if v == "Mañana":
            return today + timedelta(days=1)
        if v == "En 7 días":
            return today + timedelta(days=7)
        return today

    def guardar(e):
        sel_date = compute_selected_date()
        sel_time = ddl_time.value
        sel_iso = sel_date.isoformat()

        # Guardar en session
        scheduled = page.session.get("scheduled_maint", [])
        scheduled.append({"title": title, "date": sel_iso, "time": sel_time})
        page.session["scheduled_maint"] = scheduled

        # Ir a pantalla de confirmación
        mostrar_pantalla("programar_mantenimiento_confirm", title=title, date=sel_iso, time=sel_time)

    btn_save = ft.ElevatedButton("Guardar", bgcolor=AZUL, color="white", on_click=guardar)
    btn_cancel = ft.TextButton("Cancelar", on_click=lambda e: mostrar_pantalla("admin_indicadores"))

    body = ft.Column([
        titulo,
        ft.Container(height=8),
        ft.Row([ft.Text("Fecha:", color=NEGRO), ddl_date, ft.Container(width=24), ft.Text("Hora:", color=NEGRO), ddl_time], alignment=ft.MainAxisAlignment.START),
        ft.Container(height=12),
        ft.Row([btn_save, ft.Container(width=12), btn_cancel], alignment=ft.MainAxisAlignment.START)
    ], spacing=8)

    layout = ft.Column([header, ft.Divider(), body], spacing=12)
    root = ft.Container(layout, padding=16, bgcolor=CREMA, expand=True)
    return root


def pantalla_programar_mantenimiento_confirm(page: ft.Page, mostrar_pantalla, title: str | None = None, date: str | None = None, time: str | None = None):
    page.bgcolor = CREMA

    header = ft.Row([
        ft.Text("Confirmación", size=24, color=AZUL, weight=ft.FontWeight.BOLD, expand=True),
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    texto = ft.Text(f"Mantenimiento programado para {title or ''} el {date} a las {time}", size=16, color=NEGRO)

    btn_volver = ft.ElevatedButton("Volver", bgcolor=AZUL, color="white", on_click=lambda e: mostrar_pantalla("admin_indicadores"))

    body = ft.Column([texto, ft.Container(height=12), btn_volver], spacing=8)
    layout = ft.Column([header, ft.Divider(), body], spacing=12)
    root = ft.Container(layout, padding=16, bgcolor=CREMA, expand=True)
    return root
