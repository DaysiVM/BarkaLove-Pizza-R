import flet as ft
import asyncio

rojo = "#E63946"
verde = "#2A9D8F"


async def pantalla_preparar(page, pedido, mostrar_pantalla):
    """Animación asíncrona que muestra la preparación de la pizza.

    Args:
        page: objeto ft.Page
        pedido: dict que contiene al menos la clave 'orden'
        mostrar_pantalla: función para cambiar de pantalla
    """
    txt = ft.Text("Tu pizza está siendo preparada... 🍕", size=18, color=rojo)

    pizza_frames = [
        ft.Image(src="assets/pizza_1.png", width=250, height=250),
        ft.Image(src="assets/pizza_2.png", width=250, height=250),
        ft.Image(src="assets/pizza_3.png", width=250, height=250),
        ft.Image(src="assets/pizza_4.png", width=250, height=250),
        ft.Image(src="assets/pizza_5.png", width=250, height=250),
    ]

    boton_modificar = ft.ElevatedButton(
        "Modificar pedido",
        bgcolor=rojo,
        color="white",
        on_click=lambda _: mostrar_pantalla("modificar")
    )

    contenedor = ft.Column([
        txt,
        pizza_frames[0],
        ft.Text(f"Número de orden: {pedido.get('orden', '')}", size=16, color="black"),
        boton_modificar
    ], alignment="center")

    page.clean()
    page.add(contenedor)
    page.update()

    for frame in pizza_frames:
        contenedor.controls[1] = frame
        page.update()
        await asyncio.sleep(2)  # Duración de cada frame (puedes ajustar)

    txt.value = "¡Pizza lista! 🍕"
    page.update()


def mostrar_carga_pizza(page, numero_orden, mostrar_pantalla):
    """Wrapper sincrónico/compatibilidad para código que importa
    `mostrar_carga_pizza(page, numero_orden, mostrar_pantalla)`.

    Si el event loop ya está corriendo, programa la tarea asíncrona, si no,
    ejecuta la coroutine directamente.
    """
    pedido = {"orden": numero_orden}
    try:
        # Si hay un loop en ejecución, usamos create_task
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # No hay loop; ejecutamos de forma bloqueante
        asyncio.run(pantalla_preparar(page, pedido, mostrar_pantalla))
    else:
        # Programamos la coroutine para que corra en el loop existente
        asyncio.create_task(pantalla_preparar(page, pedido, mostrar_pantalla))
