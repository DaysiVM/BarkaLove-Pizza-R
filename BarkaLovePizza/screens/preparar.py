import flet as ft
import asyncio
import os
import glob

rojo = "#E63946"
verde = "#2A9D8F"


async def pantalla_preparar(page, pedido, mostrar_pantalla, pedido_finalizado_ref=None, current_order_ref=None):
    """Animación asíncrona que muestra la preparación de la pizza.

    Args:
        page: objeto ft.Page
        pedido: dict que contiene al menos la clave 'orden'
        mostrar_pantalla: función para cambiar de pantalla
    """
    txt = ft.Text("Tu pizza está siendo preparada... 🍕", size=18, color=rojo)

    # Si existe un GIF animado en assets, úsalo como animación principal
    # Buscar cualquier archivo pizza_loading.* (gif, webp, png animado, etc.)
    candidates = glob.glob(os.path.join("assets", "pizza_loading.*"))
    gif_path = candidates[0] if candidates else None
    use_gif = bool(gif_path)

    pizza_frames = []
    if not use_gif:
        pizza_frames = [
            ft.Image(src="assets/pizza_1.png", width=250, height=250),
            ft.Image(src="assets/pizza_2.png", width=250, height=250),
            ft.Image(src="assets/pizza_3.png", width=250, height=250),
            ft.Image(src="assets/pizza_4.png", width=250, height=250),
            ft.Image(src="assets/pizza_5.png", width=250, height=250),
        ]

    def on_modificar(_):
        # navegar a pantalla registro en modo edición
        if current_order_ref and current_order_ref[0]:
            mostrar_pantalla('registro', editar_orden=current_order_ref[0])
        else:
            mostrar_pantalla('modificar')

    boton_modificar = ft.ElevatedButton(
        "Modificar pedido",
        bgcolor=rojo,
        color="white",
        on_click=on_modificar
    )

    # Tarea que oculta el botón modificar después de 30 segundos
    async def ocultar_boton_despues(delay_seconds: int = 30):
        try:
            await asyncio.sleep(delay_seconds)
            boton_modificar.visible = False
            # Si la imagen ya fue reemplazada, solo actualizar la página
            page.update()
        except asyncio.CancelledError:
            # si se cancela, no pasa nada
            pass


    # Control de imagen: GIF o primer frame
    image_control = ft.Image(src=gif_path, width=250, height=250) if use_gif else pizza_frames[0]

    contenedor = ft.Column([
        txt,
        image_control,
        ft.Text(f"Número de orden: {pedido.get('orden', '')}", size=16, color="black"),
        boton_modificar
    ], alignment="center")

    page.clean()
    page.add(contenedor)
    page.update()

    # programar la ocultación del botón en background
    asyncio.create_task(ocultar_boton_despues(30))

    # Duración total de preparación (en segundos)
    TOTAL_PREP_SECONDS = 60

    if use_gif:
        # Si usamos GIF, lo mostramos durante TOTAL_PREP_SECONDS
        page.update()
        await asyncio.sleep(TOTAL_PREP_SECONDS)
        # Mostrar imagen final grande
        contenedor.controls[1] = ft.Image(src=os.path.join("assets", "pizza_lista.png"), width=320, height=320)
        txt.value = "¡Pizza lista! 🍕"
        page.update()
        # marcar finalizado
        if pedido_finalizado_ref is not None:
            pedido_finalizado_ref[0] = True
        if current_order_ref is not None:
            current_order_ref[0] = pedido.get('orden')
    else:
        # distribuir TOTAL_PREP_SECONDS en los frames
        per_frame = TOTAL_PREP_SECONDS / max(1, len(pizza_frames))
        for frame in pizza_frames:
            contenedor.controls[1] = frame
            page.update()
            await asyncio.sleep(per_frame)

        # Mostrar imagen final grande
        contenedor.controls[1] = ft.Image(src=os.path.join("assets", "pizza_lista.png"), width=320, height=320)
        txt.value = "¡Pizza lista! 🍕"
        page.update()
        # marcar finalizado
        if pedido_finalizado_ref is not None:
            pedido_finalizado_ref[0] = True
        if current_order_ref is not None:
            current_order_ref[0] = pedido.get('orden')


def mostrar_carga_pizza(page, numero_orden, mostrar_pantalla, pedido_finalizado_ref=None, current_order_ref=None):
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
        asyncio.run(pantalla_preparar(page, pedido, mostrar_pantalla, pedido_finalizado_ref, current_order_ref))
    else:
        # Programamos la coroutine para que corra en el loop existente
        asyncio.create_task(pantalla_preparar(page, pedido, mostrar_pantalla, pedido_finalizado_ref, current_order_ref))
