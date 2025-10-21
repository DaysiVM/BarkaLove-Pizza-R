import flet as ft

def pantalla_inicio(pedido_enviado, pedido_finalizado, mostrar_pantalla):
    rojo = "#E63946"
    amarillo = "#FFD93D"

    controles = [
        ft.Image(src="BarkaLovelogo.png", width=200, height=200),
        ft.Text("🍕 Barka Love Pizza", size=26, weight="bold", color=rojo),
        ft.Text(
            "¡Arma tu pizza y haz tu pedido en minutos!",
            color="black", size=16, text_align="center"
        ),
        ft.ElevatedButton(
            "Registrar nuevo pedido",
            bgcolor=amarillo,
            color="black",
            on_click=lambda _: mostrar_pantalla("registro")
        ),
    ]

    # Mostrar modificar solo si hay un pedido enviado y aún no se está preparando o ya finalizó
    if pedido_enviado and not pedido_finalizado:
        controles.append(
            ft.ElevatedButton(
                "Modificar pedido",
                bgcolor=rojo,
                color="white",
                on_click=lambda _: mostrar_pantalla("modificar")
            )
        )

    return ft.Column(
        controles,
        alignment="center",
        horizontal_alignment="center",
        spacing=20
    )
