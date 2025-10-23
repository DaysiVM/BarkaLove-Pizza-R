# screens/registro.py (registro + receta vigente con guía a la izquierda e imagen por tipo + KDS)
import flet as ft
import random
from datetime import datetime
import time

from utils.pedidos import guardar_pedido, actualizar_pedido
from utils.kds import registrar_pedido
import utils.recetas as rx  # receta vigente


def pantalla_registro(
    page,
    masa,
    salsa,
    checkbox_ingredientes,
    ingredientes,
    mostrar_pantalla,
    pedido_enviado_ref,
    pedido_finalizado_ref,
    current_order_ref,
    editar_orden=None
):
    # ====== Estilo base y helpers ======
    page.session.set("inicio_registro_ts", time.monotonic())
    page.scroll = ft.ScrollMode.AUTO
    rojo = "#E63946"; amarillo = "#FFD93D"; negro = "#1F1F1F"; crema = "#FFF8E7"; azul = "#2196F3"; blanco = "#FFFFFF"

    # Breakpoints por ancho y ajustes por altura
    def bp():
        w = page.width or 1280
        h = page.height or 800
        size = "xs" if w < 900 else ("md" if w < 1280 else "lg")
        return size, w, h

    state = {"field_w": 320, "pizza_size": 560, "cart_h": 420, "title_size": 32, "ing_img": 32, "pad": 16}
    def recompute_sizes():
        size, w, h = bp()
        if size == "lg":
            state.update(field_w=320, pizza_size=560, cart_h=420)
        elif size == "md":
            state.update(field_w=300, pizza_size=420, cart_h=360)
        else:
            state.update(field_w=min(280, int(w * 0.9)), pizza_size=320, cart_h=300)
        if h < 740:
            state["pizza_size"] = max(280, int(state["pizza_size"] * 0.9))
            state["cart_h"] = max(260, int(state["cart_h"] * 0.9))
    recompute_sizes()

    # ====== Campos de cliente ======
    nombre_cliente = ft.TextField(
        label="Nombre del cliente",
        hint_text="Ej. Juan Pérez",
        width=state["field_w"],
        color=negro,
        text_size=16
    )

    # Selectores (inyectados por router)
    masa.color = negro; masa.text_size = 16; masa.width = state["field_w"]
    salsa.color = negro; salsa.text_size = 16; salsa.width = state["field_w"]

    # ====== TAMAÑO ======
    tamano = ft.Dropdown(
        label="Tamaño", width=state["field_w"], color=negro, text_size=16,
        options=[ft.dropdown.Option("Individual"), ft.dropdown.Option("Familiar")],
    )

    # ====== INGREDIENTES extra (Jamón, Piña) + estilo ======
    chk_jamon = ft.Checkbox(label="Jamón", value=False)
    chk_pina  = ft.Checkbox(label="Piña",  value=False)
    for c in [chk_jamon, chk_pina] + list(checkbox_ingredientes):
        c.label_style = ft.TextStyle(color=negro, size=16)
    ingredientes_ext = list(ingredientes) + [
        {"img": "jamon.png", "nombre": "Jamón"},
        {"img": "pina.png", "nombre": "Piña"}
    ]
    checkbox_ext = list(checkbox_ingredientes) + [chk_jamon, chk_pina]

    # ====== CANTIDAD ======
    cantidad_valor = ft.Text("1", size=18, color=negro)
    def incrementar(_):
        v = int(cantidad_valor.value)
        if v < 10:
            cantidad_valor.value = str(v+1); page.update()
    def decrementar(_):
        v = int(cantidad_valor.value)
        if v > 1:
            cantidad_valor.value = str(v-1); page.update()
    cantidad_row = ft.Row(
        [
            ft.Text("Cantidad:", color=negro, size=16, weight=ft.FontWeight.W_600),
            ft.IconButton(icon=ft.Icons.REMOVE, on_click=decrementar, bgcolor=amarillo, tooltip="-"),
            cantidad_valor,
            ft.IconButton(icon=ft.Icons.ADD, on_click=incrementar, bgcolor=amarillo, tooltip="+"),
        ], alignment=ft.MainAxisAlignment.START, spacing=8
    )

    # ====== PREVIEW DE PIZZA ======
    pizza_imagen = ft.Image(
        src="pizza_base.png",
        width=state["pizza_size"],
        height=state["pizza_size"],
        fit=ft.ImageFit.CONTAIN
    )

    def imagen_por_tipo(tipo: str | None) -> str:
        t = (tipo or "").lower()
        if "pepperoni" in t:
            return "Pepperoni-pizza.png"
        # Hawaiana (jamón + piña)
        if "hawa" in t or (("jam" in t or "jamón" in t) and ("piñ" in t or "pina" in t)):
            return "Pina-pizza.png"
        if "jam" in t or "jamón" in t:
            return "Jamon-pizza.png"
        if "piñ" in t or "pina" in t:
            return "Pina-pizza.png"
        return "pizza_base.png"

    # ====== Alerta ======
    alert_text = ft.Text("", size=16, color=rojo, weight=ft.FontWeight.W_700, text_align=ft.TextAlign.CENTER)
    def show_alert(msg): alert_text.value = msg; page.update()
    def clear_alert(*_):
        if alert_text.value:
            alert_text.value = ""; page.update()
    for ctrl in [masa, salsa, tamano]: ctrl.on_change = clear_alert

    # ====== Carrito ======
    carrito_items = []
    carrito_list = ft.ListView(expand=True, spacing=6, padding=0, auto_scroll=False)
    carrito_header = ft.Text("Productos agregados", size=18, weight=ft.FontWeight.BOLD, color=negro)
    carrito_total  = ft.Text("Total de productos: 0", size=14, color=negro)
    carrito_precio = ft.Text("Total a pagar: $0", size=16, weight=ft.FontWeight.W_600, color=negro)

    metodo_pago = ft.Dropdown(
        label="Método de pago", width=state["field_w"], color=negro, text_size=16,
        options=[ft.dropdown.Option("Efectivo"), ft.dropdown.Option("Tarjeta"), ft.dropdown.Option("Transferencia")],
        on_change=clear_alert,
    )

    def _total_unidades(): return sum(int(it.get("cantidad", 1)) for it in carrito_items)

    def eliminar_item(idx):
        def _h(_):
            if 0 <= idx < len(carrito_items):
                carrito_items.pop(idx); refresh_carrito()
        return _h

    def refresh_carrito():
        carrito_list.controls.clear()
        for idx, it in enumerate(carrito_items, start=0):
            t = it.get("tamano") or "Tamaño N/D"
            tipo = it.get("receta_tipo") or "N/D"
            resumen = (
                f'{it["cantidad"]}× {t} — {it["masa"]} + {it["salsa"]} | '
                f'{", ".join(it["ingredientes"]) if it["ingredientes"] else "Sin extras"}'
            )
            carrito_list.controls.append(
                ft.Container(
                    bgcolor="#FFFFFF",
                    padding=10,
                    border_radius=8,
                    content=ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text(
                                        f"Producto {idx+1} — {tipo}",
                                        size=16,
                                        weight=ft.FontWeight.W_600,
                                        color=negro,
                                    ),
                                    ft.Text(resumen, size=14, color=negro),
                                ],
                                spacing=2,
                                expand=True,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                tooltip="Eliminar",
                                on_click=eliminar_item(idx),
                                bgcolor=rojo,
                                icon_color="white",
                                width=36,
                                height=36,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                )
            )
        carrito_total.value = f"Total de productos: {len(carrito_items)}"
        carrito_precio.value = f"Total a pagar: ${_total_unidades() * 10}"
        page.update()

    # ====== Tipo de pizza (receta) + Guía vigente ======
    tipos_receta = rx.listar_tipos()
    dd_receta = ft.Dropdown(
        label="Tipo de pizza (receta)",
        width=state["field_w"],
        color=negro, text_size=16,
        options=[ft.dropdown.Option(t) for t in tipos_receta] if tipos_receta else [],
        value=(tipos_receta[0] if tipos_receta else None),
    )

    guia_titulo = ft.Text("Guía receta vigente", size=16, color=negro, weight=ft.FontWeight.W_600)
    guia_list = ft.Column([], spacing=4)
    guia_receta_container = ft.Container(bgcolor=blanco, border_radius=10, padding=10)

    def pm_str(n, tol, unidad="g"):
        return f"{n} ± {tol} {unidad}"

    def refresh_guia_receta(*_):
        guia_list.controls.clear()
        tipo = dd_receta.value
        ver = rx.vigente(tipo) if tipo else None
        if not ver:
            guia_list.controls.append(ft.Text("No hay receta vigente para este tipo.", size=14, color=negro))
        else:
            ing = ver.ingredientes or {}
            if "Masa" in ing:
                guia_list.controls.append(ft.Text(f"• Masa:  {pm_str(ing['Masa']['gramos'], ing['Masa']['tol'])}", size=14, color=negro))
            if "Salsa" in ing:
                guia_list.controls.append(ft.Text(f"• Salsa: {pm_str(ing['Salsa']['gramos'], ing['Salsa']['tol'])}", size=14, color=negro))

            # Mostrar SOLO ingredientes seleccionados (útil para cocina)
            seleccionados = [c.label for c in checkbox_ext if c.value]
            for sel in seleccionados:
                if sel in ing:
                    d = ing[sel]
                    guia_list.controls.append(ft.Text(f"• {sel}: {pm_str(d['gramos'], d['tol'])}", size=14, color=negro))

            # Horno objetivo
            h = ver.horno or {}
            guia_list.controls.append(ft.Divider())
            guia_list.controls.append(
                ft.Text(
                    f"Horno: {pm_str(h.get('temp_c',0), (h.get('tol') or {}).get('temp',0), '°C')}  •  "
                    f"{pm_str(h.get('tiempo_min',0), (h.get('tol') or {}).get('tiempo',0), 'min')}",
                    size=14, color=negro
                )
            )
        guia_receta_container.content = ft.Column([guia_titulo, guia_list], spacing=6)
        page.update()

    # ingredientes cambian solo la guía (no la imagen)
    def on_ingredientes_change(_=None):
        refresh_guia_receta()
    for c in checkbox_ext:
        c.on_change = on_ingredientes_change

    # al cambiar el tipo, actualizar imagen y guía
    def on_tipo_change(_=None):
        pizza_imagen.src = imagen_por_tipo(dd_receta.value)
        refresh_guia_receta()
        page.update()
    if dd_receta.options:
        dd_receta.on_change = on_tipo_change
    # primera carga de guía + imagen por tipo
    on_tipo_change()

    # ====== Agregar producto ======
    def agregar_producto_click(_):
        faltantes = []
        if not masa.value: faltantes.append("tipo de masa")
        if not salsa.value: faltantes.append("salsa")
        if not tamano.value: faltantes.append("tamaño")
        if not dd_receta.value: faltantes.append("tipo de pizza (receta)")
        if faltantes:
            show_alert(f"Para agregar un producto falta: {', '.join(faltantes)}.")
            return

        ingredientes_sel = [c.label for c in checkbox_ext if c.value]
        carrito_items.append({
            "masa": masa.value,
            "salsa": salsa.value,
            "tamano": tamano.value,
            "ingredientes": ingredientes_sel,
            "cantidad": int(cantidad_valor.value),
            "receta_tipo": dd_receta.value,
        })
        refresh_carrito()
        clear_alert()
        page.snack_bar = ft.SnackBar(ft.Text("Producto agregado al carrito.", color="white"), bgcolor="#4CAF50")
        page.snack_bar.open = True; page.update()

    btn_agregar_producto = ft.ElevatedButton(
        "Agregar producto", bgcolor=azul, color="white", width=220, height=48,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)), on_click=agregar_producto_click,
    )

    # ====== Confirmar / Cancelar ======
    def cancelar_pedido_click(_):
        if carrito_items:
            carrito_items.clear(); refresh_carrito(); clear_alert()
            page.snack_bar = ft.SnackBar(ft.Text("Se vació el carrito de productos.", color="white"), bgcolor=rojo)
            page.snack_bar.open = True; page.update()
        else:
            show_alert("No hay productos en el carrito para borrar.")

    def _armar_pedido_base(numero_orden=None, items=None):
        items = items or carrito_items
        unidades = _total_unidades()
        first = items[0]
        receta_tipo = first.get("receta_tipo") or dd_receta.value
        receta_vig = rx.vigente(receta_tipo) if receta_tipo else None
        return {
            "orden": numero_orden,
            "cliente": nombre_cliente.value,
            "metodo_pago": metodo_pago.value,
            "items": items,
            "hora": datetime.now().isoformat(),
            "masa": first["masa"],
            "salsa": first["salsa"],
            "tamano": first.get("tamano"),
            "ingredientes": first["ingredientes"],
            "cantidad": first["cantidad"],
            "total_visual": unidades * 10,
            "moneda_visual": "USD",
            "receta_tipo": receta_tipo,
            "receta_version": (receta_vig.version_id if receta_vig else None),
        }

    def _enviar_a_kds(pedido_dict: dict):
        """Registra el pedido confirmado en el KDS (HU: <5s)."""
        first = pedido_dict["items"][0] if pedido_dict.get("items") else {}
        pedido_kds = {
            "id": pedido_dict.get("orden"),
            "orden": pedido_dict.get("orden"),
            "cliente": pedido_dict.get("cliente"),
            "receta_tipo": pedido_dict.get("receta_tipo") or first.get("receta_tipo"),
            "tamano": pedido_dict.get("tamano") or first.get("tamano"),
            "masa": pedido_dict.get("masa") or first.get("masa"),
            "salsa": pedido_dict.get("salsa") or first.get("salsa"),
            "ingredientes": pedido_dict.get("ingredientes") or first.get("ingredientes", []),
            "estado": "confirmado",
            # 'fecha' la agrega utils.kds.registrar_pedido
        }
        try:
            registrar_pedido(pedido_kds)
        except Exception:
            # Si algo falla, no bloqueamos el flujo de caja
            pass

    def guardar_pedido_click(e):
        if hasattr(e, "control"): e.control.disabled = True; page.update()
        try:
            if not nombre_cliente.value:
                show_alert("Indica el nombre del cliente."); return
            if not metodo_pago.value:
                show_alert("Selecciona el método de pago."); return

            if len(carrito_items) == 0:
                falt = []
                if not masa.value:   falt.append("tipo de masa")
                if not salsa.value:  falt.append("salsa")
                if not tamano.value: falt.append("tamaño")
                if not dd_receta.value: falt.append("tipo de pizza (receta)")
                if falt:
                    show_alert(f"Selecciona {', '.join(falt)} o agrega un producto al carrito.")
                    return
                ingredientes_sel = [c.label for c in checkbox_ext if c.value]
                carrito_items.append({
                    "masa": masa.value, "salsa": salsa.value, "tamano": tamano.value,
                    "ingredientes": ingredientes_sel, "cantidad": int(cantidad_valor.value),
                    "receta_tipo": dd_receta.value,
                })
                refresh_carrito()

            if editar_orden is None:
                numero_orden = random.randint(1000, 9999)
                pedido = _armar_pedido_base(numero_orden=numero_orden)
                guardar_pedido(pedido)

                # === Registro automático en cocina (KDS) ===
                _enviar_a_kds(pedido)

                pedido_enviado_ref[0] = True
                pedido_finalizado_ref[0] = False
                current_order_ref[0] = numero_orden
                clear_alert()
                page.snack_bar = ft.SnackBar(
                    ft.Text(f"Pedido #{numero_orden} registrado con {len(carrito_items)} producto(s).", color="white"),
                    bgcolor="#4CAF50",
                )
                page.snack_bar.open = True; page.update()
                mostrar_pantalla("preparar", numero_orden=numero_orden)
            else:
                items_final = carrito_items or [{
                    "masa": masa.value, "salsa": salsa.value, "tamano": tamano.value,
                    "ingredientes": [c.label for c in checkbox_ext if c.value],
                    "cantidad": int(cantidad_valor.value),
                    "receta_tipo": dd_receta.value,
                }]
                pedido = _armar_pedido_base(numero_orden=editar_orden, items=items_final)
                actualizar_pedido(pedido)
                clear_alert()
                page.snack_bar = ft.SnackBar(ft.Text("Pedido actualizado correctamente.", color="white"), bgcolor="#4CAF50")
                page.snack_bar.open = True; page.update()
                mostrar_pantalla("inicio")

        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error al registrar pedido: {ex}", color="white"), bgcolor=rojo)
            page.snack_bar.open = True; page.update()
        finally:
            if hasattr(e, "control"): e.control.disabled = False; page.update()

    btn_confirmar_derecha = ft.ElevatedButton(
        "Confirmar pedido", bgcolor=amarillo, color=negro, width=state["field_w"], height=50,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)), on_click=guardar_pedido_click,
    )
    btn_cancelar_derecha = ft.ElevatedButton(
        "Cancelar pedido", bgcolor=rojo, color="white", width=state["field_w"], height=46,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)), on_click=cancelar_pedido_click,
    )

    # ====== Controles de ingredientes (con imágenes) ======
    controles_ingredientes = [
        ft.Row([ft.Image(src=i["img"], width=state["ing_img"], height=state["ing_img"]), checkbox_ext[idx]])
        for idx, i in enumerate(ingredientes_ext)
    ]
    ingredientes_list_col = ft.Column(controles_ingredientes, spacing=6, scroll=ft.ScrollMode.AUTO)

    # ====== Bloque "Guía (izq) / Ingredientes (der)" ======
    guia_cell = ft.Container(guia_receta_container, padding=0, col={"xs": 12, "md": 6, "lg": 6})
    ing_cell = ft.Container(
        ft.Column([ft.Text("Ingredientes extras:", size=18, color=negro, weight=ft.FontWeight.BOLD), ingredientes_list_col], spacing=6),
        padding=0, col={"xs": 12, "md": 6, "lg": 6},
    )
    guia_ing_grid = ft.ResponsiveRow(controls=[guia_cell, ing_cell], columns=12, spacing=12, run_spacing=12)

    # ====== Formulario izquierda ======
    formulario_col = ft.Column(
        [
            ft.Text("Registrar pedido 🍕", size=state["title_size"], color=rojo, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            nombre_cliente,
            dd_receta,
            masa,
            salsa,
            tamano,
            cantidad_row,
            guia_ing_grid,
        ],
        spacing=10, alignment=ft.MainAxisAlignment.START, expand=False,
    )

    # ====== Columna central ======
    btn_volver = ft.ElevatedButton(
        "⬅ Volver", bgcolor=rojo, color="white", width=200, height=44,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        on_click=lambda _: mostrar_pantalla("inicio"),
    )
    col_central = ft.Column(
        [alert_text, ft.Container(content=pizza_imagen, alignment=ft.alignment.center),
         ft.Row([btn_agregar_producto, btn_volver], alignment=ft.MainAxisAlignment.CENTER, spacing=12)],
        alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=12, expand=True,
    )

    # ====== Columna derecha ======
    carrito_box = ft.Container(content=carrito_list, bgcolor=blanco, border_radius=10, padding=10,
                               width=state["field_w"], height=state["cart_h"])
    carrito_col = ft.Column(
        [carrito_header, carrito_box, carrito_total, carrito_precio, ft.Divider(), metodo_pago,
         btn_confirmar_derecha, btn_cancelar_derecha],
        spacing=10, alignment=ft.MainAxisAlignment.START, expand=False,
    )

    # ====== Layout ======
    form_cell   = ft.Container(formulario_col, padding=0, col={"xs": 12, "md": 4, "lg": 4})
    center_cell = ft.Container(col_central,     padding=0, col={"xs": 12, "md": 5, "lg": 5})
    cart_cell   = ft.Container(carrito_col,     padding=0, col={"xs": 12, "md": 3, "lg": 3})
    grid = ft.ResponsiveRow(
        controls=[form_cell, center_cell, cart_cell],
        columns=12,
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.START,
        run_spacing=12,
        spacing=12,
    )
    root = ft.Container(content=grid, bgcolor=crema, padding=state["pad"], expand=True, alignment=ft.alignment.top_center)

    # ====== on_resize ======
    def on_resize(_):
        recompute_sizes()
        fw = state["field_w"]
        for ctrl in [nombre_cliente, dd_receta, masa, salsa, tamano, metodo_pago]:
            ctrl.width = fw
        pizza_imagen.width = state["pizza_size"]; pizza_imagen.height = state["pizza_size"]
        page.update()
    page.on_resize = on_resize

    return root
