import flet as ft
import asyncio
from utils.pedidos import obtener_pedido

# Paleta
ROJO = "#E63946"
VERDE = "#2A9D8F"
CREMA = "#FFF8E7"
NEGRO = "#1F1F1F"
AMARILLO = "#FFD93D"


async def pantalla_preparar(page, pedido, mostrar_pantalla, pedido_finalizado_ref=None, current_order_ref=None):
    """
    Fases:
      1) 🥫 Preparación  -> "Modificar pedido" (amarillo, pequeño) visible
      2) 🔥 Horno        -> no modificable
      3) 📦 Empaque      -> no modificable
    Final: "¡Pizza lista!" + aparece "Salir" (rojo, pequeño)
    """
    # ===== Setup base =====
    page.bgcolor = CREMA
    page.scroll = ft.ScrollMode.AUTO
    page.clean()

    # Traer datos completos del pedido si solo llegó la orden
    numero_orden = pedido.get("orden")
    pedido_full = obtener_pedido(numero_orden) if numero_orden is not None else pedido
    if not pedido_full:
        pedido_full = pedido or {}

    cliente = pedido_full.get("cliente") or pedido_full.get("nombre") or "—"

    # ===== Responsive helpers =====
    def bp():
        w = page.width or 1280
        return "xs" if w < 900 else ("md" if w < 1280 else "lg"), w

    state = {
        "img_size": 420,
        "title_size": 30,
        "status_size": 24,
        "phase_size": 18,
        "box_w": 520,
        "pad": 20,
        "btn_w": 120,  # botones pequeños
        "btn_h": 30,
        "info_size": 16,
    }

    def recompute_sizes():
        size, w = bp()
        if size == "lg":
            state.update(img_size=420, title_size=30, status_size=24, phase_size=18,
                         box_w=520, pad=20, btn_w=120, btn_h=30, info_size=16)
        elif size == "md":
            state.update(img_size=340, title_size=28, status_size=22, phase_size=17,
                         box_w=460, pad=16, btn_w=116, btn_h=28, info_size=15)
        else:
            state.update(img_size=260, title_size=26, status_size=20, phase_size=16,
                         box_w=min(420, int((w or 420) * 0.92)), pad=14, btn_w=112, btn_h=26, info_size=14)

    recompute_sizes()

    # ===== Imágenes / GIF (con assets_dir correcto, usar SOLO el nombre del archivo) =====
    # Deben existir en BarkaLovePizza/assets:
    #   - pizza_loading.gif
    #   - pizza_lista.png
    image_control = ft.Image(
        src="pizza_loading.gif",
        width=state["img_size"],
        height=state["img_size"],
        fit=ft.ImageFit.CONTAIN,
        gapless_playback=True,
    )

    # ===== Textos y fases =====
    titulo = ft.Text("🍕 BarkaLove Pizza", size=state["title_size"], color=ROJO, weight=ft.FontWeight.BOLD)
    txt_estado = ft.Text("Preparando tu pizza...", size=state["status_size"], color=ROJO, weight=ft.FontWeight.BOLD)

    phases = [("Preparación", "🥫"), ("Horno", "🔥"), ("Empaque", "📦")]
    fase_actual = ft.Text(
        f"{phases[0][1]}  Fase: {phases[0][0]}",
        size=state["phase_size"],
        color=NEGRO,
        weight=ft.FontWeight.W_600,
        text_align=ft.TextAlign.CENTER,
    )

    progreso_bar = ft.ProgressBar(value=0, color=AMARILLO, bgcolor="#E0E0E0", width=state["box_w"])

    # ===== Botones (pequeños) =====
    def on_modificar(_):
        if current_order_ref and current_order_ref[0]:
            mostrar_pantalla("registro", editar_orden=current_order_ref[0])
        else:
            mostrar_pantalla("registro")

    btn_modificar = ft.ElevatedButton(
        "Modificar",
        bgcolor=AMARILLO,
        color=NEGRO,
        width=state["btn_w"],
        height=state["btn_h"],
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        on_click=on_modificar,
        visible=True,   # solo fase 1
    )

    def on_salir(_):
        mostrar_pantalla("inicio")

    btn_salir = ft.ElevatedButton(
        "Salir",
        bgcolor=ROJO,
        color="white",
        width=state["btn_w"],
        height=state["btn_h"],
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        on_click=on_salir,
        visible=False,  # solo al finalizar
    )

    info_min = ft.Text(
        f"Cliente: {cliente}   •   Orden: #{numero_orden if numero_orden is not None else '—'}",
        size=state["info_size"],
        color=NEGRO,
        text_align=ft.TextAlign.CENTER,
    )

    # ===== Layout =====
    layout = ft.Column(
        [
            titulo,
            txt_estado,
            image_control,
            fase_actual,
            progreso_bar,
            ft.Row([btn_salir], alignment=ft.MainAxisAlignment.CENTER),      # aparece al final
            ft.Container(height=6),
            ft.Row([btn_modificar], alignment=ft.MainAxisAlignment.CENTER),  # solo en Fase 1
            ft.Container(height=6),
            info_min,
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10,
    )

    root = ft.Container(
        content=layout,
        alignment=ft.alignment.center,
        expand=True,
        padding=state["pad"],
        bgcolor=CREMA,
    )

    page.add(root)
    page.update()

    # ===== Fases =====
    TOTAL_PREP_SECONDS = 60
    phase_duration = TOTAL_PREP_SECONDS / 3

    async def run_fases():
        for i, (name, emoji) in enumerate(phases):
            fase_actual.value = f"{emoji}  Fase: {name}"
            progreso_bar.value = (i + 1) / len(phases)
            btn_modificar.visible = (i == 0)  # solo en Preparación
            page.update()
            await asyncio.sleep(phase_duration)

        # Final
        fase_actual.value = "✅  Fase: Finalizada"
        progreso_bar.value = 1
        image_control.src = "pizza_lista.png"  # imagen final exacta
        txt_estado.value = "¡Pizza lista! 🍕"
        txt_estado.color = VERDE
        btn_modificar.visible = False
        btn_salir.visible = True        # ahora sí mostramos "Salir"
        page.update()

        if pedido_finalizado_ref is not None:
            pedido_finalizado_ref[0] = True
        if current_order_ref is not None:
            current_order_ref[0] = numero_orden

    await run_fases()

    # ===== on_resize =====
    def on_resize(e):
        recompute_sizes()
        image_control.width = state["img_size"]
        image_control.height = state["img_size"]
        titulo.size = state["title_size"]
        txt_estado.size = state["status_size"]
        fase_actual.size = state["phase_size"]
        progreso_bar.width = state["box_w"]
        btn_salir.width = state["btn_w"]; btn_salir.height = state["btn_h"]
        btn_modificar.width = state["btn_w"]; btn_modificar.height = state["btn_h"]
        info_min.size = state["info_size"]
        root.padding = state["pad"]
        page.update()

    page.on_resize = on_resize


def mostrar_carga_pizza(page, numero_orden, mostrar_pantalla, pedido_finalizado_ref=None, current_order_ref=None):
    """Compat sincrónica: ejecuta o agenda la coroutine según haya loop."""
    pedido = {"orden": numero_orden}
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        asyncio.run(pantalla_preparar(page, pedido, mostrar_pantalla, pedido_finalizado_ref, current_order_ref))
    else:
        asyncio.create_task(pantalla_preparar(page, pedido, mostrar_pantalla, pedido_finalizado_ref, current_order_ref))
