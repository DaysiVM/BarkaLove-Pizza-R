import flet as ft

def pantalla_inicio(pedido_enviado, pedido_finalizado, mostrar_pantalla):
    # Colores
    rojo = "#E63946"
    amarillo = "#FFD93D"
    crema = "#FFF8E7"
    negro = "#1F1F1F"

    # --- Topbar con botón Administración (sin función aún) ---
    btn_admin = ft.ElevatedButton(
        "Administración",
        bgcolor=rojo,
        color="white",
        height=36,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        on_click=lambda _: None,  # sin acción (se implementará más adelante)
    )
    topbar = ft.Container(
        content=ft.Row(
            controls=[ft.Container(expand=True), btn_admin],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.padding.only(left=16, right=16, top=12, bottom=4),
        bgcolor=crema,
    )

    # --- Contenido central, más grande y agradable ---
    logo = ft.Image(src="BarkaLovelogo.png", width=260, height=260, fit=ft.ImageFit.CONTAIN)

    titulo = ft.Text(
        "🍕 Barka Love Pizza",
        size=36,
        weight=ft.FontWeight.BOLD,
        color=rojo,
        text_align=ft.TextAlign.CENTER,
    )

    subtitulo = ft.Text(
        "¡Arma tu pizza y haz tu pedido en minutos!",
        size=18,
        color=negro,
        text_align=ft.TextAlign.CENTER,
    )

    btn_registrar = ft.ElevatedButton(
        "Registrar nuevo pedido",
        bgcolor=amarillo,
        color=negro,
        width=280,
        height=56,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
        on_click=lambda _: mostrar_pantalla("registro"),
    )

    controles = [
        logo,
        titulo,
        subtitulo,
        btn_registrar,
    ]

    # Mostrar "Modificar pedido" solo si hay un pedido enviado y no finalizado
    if pedido_enviado and not pedido_finalizado:
        controles.append(
            ft.ElevatedButton(
                "Modificar pedido",
                bgcolor=rojo,
                color="white",
                width=280,
                height=50,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
                on_click=lambda _: mostrar_pantalla("modificar"),
            )
        )

    centro = ft.Container(
        content=ft.Column(
            controles,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=16,
        ),
        padding=24,
        bgcolor=crema,
        alignment=ft.alignment.center,
        expand=True,
    )

    # --- Root: topbar + centro (apila verticalmente) ---
    root = ft.Column(
        controls=[topbar, centro],
        spacing=0,
        expand=True,
    )

    return root
