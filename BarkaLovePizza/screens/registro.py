# screens/registro.py
import flet as ft
import random
from datetime import datetime
import time
from utils.pedidos import guardar_pedido, actualizar_pedido, obtener_pedido


def pantalla_registro(page, masa, salsa, checkbox_ingredientes, ingredientes,
                      mostrar_pantalla, pedido_enviado_ref, pedido_finalizado_ref,
                      current_order_ref, editar_orden=None):

    # ====== Estilo base ======
    page.session.set("inicio_registro_ts", time.monotonic())
    rojo = "#E63946"
    amarillo = "#FFD93D"
    negro = "#1F1F1F"
    crema = "#FFF8E7"
    azul = "#2196F3"
    S_FIELD_W = 360  # ancho estándar para TODOS los campos

    # ====== Campos de cliente ======
    nombre_cliente = ft.TextField(label="Nombre del cliente", width=S_FIELD_W, color=negro, text_size=18)

    # Forzar color / tamaño / ancho en selectores de masa y salsa (recibidos desde el router)
    masa.color = negro
    salsa.color = negro
    masa.text_size = 18
    salsa.text_size = 18
    masa.width = S_FIELD_W
    salsa.width = S_FIELD_W

    # ====== TAMAÑO (debajo de salsa, SOLO opciones) ======
    tamano = ft.Dropdown(
        label="Tamaño",
        width=S_FIELD_W,
        color=negro,
        text_size=18,
        options=[
            ft.dropdown.Option("Individual"),
            ft.dropdown.Option("Familiar"),
        ],
    )

    # ====== INGREDIENTES: agregar Jamón y Piña y uniformar estilo ======
    chk_jamon = ft.Checkbox(label="Jamón", value=False)
    chk_pina = ft.Checkbox(label="Piña", value=False)
    for c in [chk_jamon, chk_pina]:
        c.label_style = ft.TextStyle(color=negro, size=16)

    for c in checkbox_ingredientes:
        c.label_style = ft.TextStyle(color=negro, size=16)

    ingredientes_ext = list(ingredientes) + [
        {"img": "jamon.png", "nombre": "Jamón"},
        {"img": "pina.png", "nombre": "Piña"},
    ]
    checkbox_ext = list(checkbox_ingredientes) + [chk_jamon, chk_pina]

    # ====== CANTIDAD (+ / -) ======
    cantidad_valor = ft.Text("1", size=22, color=negro)

    def incrementar(e):
        val = int(cantidad_valor.value)
        if val < 10:
            cantidad_valor.value = str(val + 1)
            page.update()

    def decrementar(e):
        val = int(cantidad_valor.value)
        if val > 1:
            cantidad_valor.value = str(val - 1)
            page.update()

    cantidad_row = ft.Row(
        [
            ft.Text("Cantidad:", color=negro, size=18, weight=ft.FontWeight.W_600),
            ft.IconButton(icon=ft.Icons.REMOVE, on_click=decrementar, bgcolor=amarillo),
            cantidad_valor,
            ft.IconButton(icon=ft.Icons.ADD, on_click=incrementar, bgcolor=amarillo),
        ],
        alignment=ft.MainAxisAlignment.START,
        spacing=10,
    )

    # ====== PREVIEW DE PIZZA (grande, centrada) ======
    pizza_size = 720
    pizza_imagen = ft.Image(
        src="pizza_base.png",
        width=pizza_size,
        height=pizza_size,
        fit=ft.ImageFit.CONTAIN,
    )

    # Prioridad de imagen completa: Pepperoni > Jamón > Pimientos > Champiñones > Aceitunas > Piña > Queso extra > base
    def actualizar_imagen_pizza(e=None):
        seleccionados = [c.label for c in checkbox_ext if c.value]
        if "Pepperoni" in seleccionados:
            pizza_imagen.src = "Pepperoni-pizza.png"
        elif "Jamón" in seleccionados:
            pizza_imagen.src = "Jamon-pizza.png"
        elif "Pimientos" in seleccionados:
            pizza_imagen.src = "Pimientos-pizza.png"
        elif "Champiñones" in seleccionados:
            pizza_imagen.src = "Champiñones-pizza.png"
        elif "Aceitunas" in seleccionados:
            pizza_imagen.src = "Aceitunas-pizza.png"
        elif "Piña" in seleccionados:
            pizza_imagen.src = "Pina-pizza.png"
        elif "Queso extra" in seleccionados:
            pizza_imagen.src = "cheese-pizza.png"
        else:
            pizza_imagen.src = "pizza_base.png"
        page.update()

    for c in checkbox_ext:
        c.on_change = actualizar_imagen_pizza

    # ====== Alerta inline (roja) sobre la pizza ======
    alert_text = ft.Text(
        "",
        size=18,
        color=rojo,
        weight=ft.FontWeight.W_700,
        text_align=ft.TextAlign.CENTER,
    )

    def show_alert(msg: str):
        alert_text.value = msg
        page.update()

    def clear_alert(*_):
        if alert_text.value:
            alert_text.value = ""
            page.update()

    # Limpiar alerta cuando el usuario corrige algo relevante
    for ctrl in [masa, salsa, tamano]:
        ctrl.on_change = clear_alert

    # ====== Carrito a la derecha ======
    carrito_items = []  # cada item: {"masa","salsa","tamano","ingredientes","cantidad"}
    carrito_list = ft.ListView(expand=True, spacing=8, padding=0, auto_scroll=False)
    carrito_header = ft.Text("Productos agregados", size=22, weight=ft.FontWeight.BOLD, color=negro)
    carrito_total = ft.Text("Total de productos: 0", size=16, color=negro)
    carrito_precio = ft.Text("Total a pagar: $0", size=18, weight=ft.FontWeight.W_600, color=negro)

    # Método de pago (derecha)
    metodo_pago = ft.Dropdown(
        label="Método de pago",
        width=S_FIELD_W,
        color=negro,
        text_size=18,
        options=[
            ft.dropdown.Option("Efectivo"),
            ft.dropdown.Option("Tarjeta"),
            ft.dropdown.Option("Transferencia"),
        ],
        on_change=clear_alert,
    )

    def _total_unidades():
        return sum(int(it.get("cantidad", 1)) for it in carrito_items)

    def eliminar_item(idx):
        def _handler(e):
            if 0 <= idx < len(carrito_items):
                carrito_items.pop(idx)
                refresh_carrito()
        return _handler

    def refresh_carrito():
        carrito_list.controls.clear()
        for idx, it in enumerate(carrito_items, start=0):
            t = it.get("tamano") or "Tamaño N/D"
            resumen = f'{it["cantidad"]}× {t} — {it["masa"]} + {it["salsa"]} | ' \
                      f'{", ".join(it["ingredientes"]) if it["ingredientes"] else "Sin extras"}'
            carrito_list.controls.append(
                ft.Container(
                    bgcolor="#FFFFFF",
                    padding=12,
                    border_radius=8,
                    content=ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text(f"Producto {idx+1}", size=18, weight=ft.FontWeight.W_600, color=negro),
                                    ft.Text(resumen, size=16, color=negro),
                                ],
                                spacing=4,
                                expand=True,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                tooltip="Eliminar",
                                on_click=eliminar_item(idx),
                                bgcolor=rojo,
                                icon_color="white",
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                )
            )
        carrito_total.value = f"Total de productos: {len(carrito_items)}"
        unidades = _total_unidades()
        carrito_precio.value = f"Total a pagar: ${unidades * 10}"
        page.update()

    # ====== Agregar producto (columna central) ======
    def agregar_producto_click(e):
        faltantes = []
        if not masa.value:
            faltantes.append("tipo de masa")
        if not salsa.value:
            faltantes.append("salsa")
        if not tamano.value:
            faltantes.append("tamaño")
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
        })
        refresh_carrito()
        clear_alert()
        page.snack_bar = ft.SnackBar(ft.Text("Producto agregado al carrito.", color="white"), bgcolor="#4CAF50")
        page.snack_bar.open = True
        page.update()

    btn_agregar_producto = ft.ElevatedButton(
        "Agregar producto",
        bgcolor=azul,
        color="white",
        width=260,
        height=55,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
        on_click=agregar_producto_click,
    )

    # ====== Confirmar / Cancelar pedido (en la derecha) ======
    def cancelar_pedido_click(e):
        if carrito_items:
            carrito_items.clear()
            refresh_carrito()
            clear_alert()
            page.snack_bar = ft.SnackBar(ft.Text("Se vació el carrito de productos.", color="white"), bgcolor=rojo)
            page.snack_bar.open = True
            page.update()
        else:
            show_alert("No hay productos en el carrito para borrar.")

    def guardar_pedido_click(e):
        if hasattr(e, "control"):
            e.control.disabled = True
            page.update()
        try:
            if not nombre_cliente.value:
                show_alert("Indica el nombre del cliente.")
                return
            if not metodo_pago.value:
                show_alert("Selecciona el método de pago.")
                return

            # Permitir confirmar sin carrito si el producto actual está completo
            if len(carrito_items) == 0:
                falt = []
                if not masa.value:
                    falt.append("tipo de masa")
                if not salsa.value:
                    falt.append("salsa")
                if not tamano.value:
                    falt.append("tamaño")
                if falt:
                    show_alert(f"Selecciona {', '.join(falt)} o agrega un producto al carrito.")
                    return

                ingredientes_sel = [c.label for c in checkbox_ext if c.value]
                carrito_items.append({
                    "masa": masa.value,
                    "salsa": salsa.value,
                    "tamano": tamano.value,
                    "ingredientes": ingredientes_sel,
                    "cantidad": int(cantidad_valor.value),
                })
                refresh_carrito()

            if editar_orden is None:
                numero_orden = random.randint(1000, 9999)
                unidades = _total_unidades()
                first = carrito_items[0]
                pedido = {
                    "orden": numero_orden,
                    "cliente": nombre_cliente.value,
                    "metodo_pago": metodo_pago.value,
                    "items": carrito_items,
                    "hora": datetime.now().isoformat(),
                    # Compatibilidad con pantallas previas (primer item)
                    "masa": first["masa"],
                    "salsa": first["salsa"],
                    "tamano": first.get("tamano"),
                    "ingredientes": first["ingredientes"],
                    "cantidad": first["cantidad"],
                    # Total visual: $10 por unidad total
                    "total_visual": unidades * 10,
                    "moneda_visual": "USD",
                }
                guardar_pedido(pedido)
                pedido_enviado_ref[0] = True
                pedido_finalizado_ref[0] = False
                current_order_ref[0] = numero_orden
                clear_alert()
                page.snack_bar = ft.SnackBar(
                    ft.Text(f"Pedido #{numero_orden} registrado con {len(carrito_items)} producto(s).", color="white"),
                    bgcolor="#4CAF50",
                )
                page.snack_bar.open = True
                page.update()
                mostrar_pantalla("preparar", numero_orden=numero_orden)
            else:
                items_final = carrito_items or [{
                    "masa": masa.value,
                    "salsa": salsa.value,
                    "tamano": tamano.value,
                    "ingredientes": [c.label for c in checkbox_ext if c.value],
                    "cantidad": int(cantidad_valor.value),
                }]
                unidades = sum(int(it.get("cantidad", 1)) for it in items_final)
                first = items_final[0]
                pedido = {
                    "orden": editar_orden,
                    "cliente": nombre_cliente.value,
                    "metodo_pago": metodo_pago.value,
                    "items": items_final,
                    "masa": first["masa"],
                    "salsa": first["salsa"],
                    "tamano": first.get("tamano"),
                    "ingredientes": first["ingredientes"],
                    "cantidad": first["cantidad"],
                    "total_visual": unidades * 10,
                    "moneda_visual": "USD",
                }
                actualizar_pedido(pedido)
                clear_alert()
                page.snack_bar = ft.SnackBar(
                    ft.Text("Pedido actualizado correctamente.", color="white"),
                    bgcolor="#4CAF50",
                )
                page.snack_bar.open = True
                page.update()
                mostrar_pantalla("inicio")

        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error al registrar pedido: {ex}", color="white"), bgcolor=rojo)
            page.snack_bar.open = True
            page.update()
        finally:
            if hasattr(e, "control"):
                e.control.disabled = False
                page.update()

    btn_confirmar_derecha = ft.ElevatedButton(
        "Confirmar pedido",
        bgcolor=amarillo,
        color=negro,
        width=S_FIELD_W,
        height=55,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
        on_click=guardar_pedido_click,
    )
    btn_cancelar_derecha = ft.ElevatedButton(
        "Cancelar pedido",
        bgcolor=rojo,
        color="white",
        width=S_FIELD_W,
        height=50,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
        on_click=cancelar_pedido_click,
    )

    # ====== Controles de ingredientes (con imágenes) ======
    controles_ingredientes = [
        ft.Row([ft.Image(src=i["img"], width=40, height=40), checkbox_ext[idx]])
        for idx, i in enumerate(ingredientes_ext)
    ]

    # ====== Formulario izquierda ======
    formulario = ft.Column(
        [
            ft.Text("Registrar pedido 🍕", size=38, color=rojo, weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.LEFT),
            ft.Divider(),
            nombre_cliente,
            masa,
            salsa,
            tamano,      # <— SOLO el dropdown (sin texto lateral)
            cantidad_row,
            ft.Text("Ingredientes:", size=20, color=negro, weight=ft.FontWeight.BOLD),
            ft.Column(controles_ingredientes, spacing=8),
        ],
        spacing=12,
        alignment=ft.MainAxisAlignment.START,
        expand=False,
    )

    # ====== Columna central (alerta + pizza + agregar + volver) ======
    btn_volver = ft.ElevatedButton(
        "⬅ Volver",
        bgcolor=rojo,
        color="white",
        width=260,
        height=50,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
        on_click=lambda _: mostrar_pantalla("inicio"),
    )

    col_central = ft.Column(
        [
            alert_text,
            ft.Container(content=pizza_imagen, alignment=ft.alignment.center, padding=10),
            ft.Column(
                [btn_agregar_producto, btn_volver],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment="center",
                spacing=16,
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=16,
        expand=True,
    )

    # ====== Columna derecha (carrito + totales + pago + confirmar/cancelar) ======
    carrito_col = ft.Column(
        [
            carrito_header,
            ft.Container(
                content=carrito_list,
                bgcolor="#FFFFFF",
                border_radius=12,
                padding=12,
                width=360,
                height=520,
            ),
            carrito_total,
            carrito_precio,
            ft.Divider(),
            metodo_pago,
            btn_confirmar_derecha,
            btn_cancelar_derecha,
        ],
        spacing=12,
        alignment=ft.MainAxisAlignment.START,
        expand=False,
    )

    # ====== Layout final ======
    estructura = ft.Row(
        [
            ft.Container(formulario, width=420),
            ft.VerticalDivider(width=1, color="#E0E0E0"),
            col_central,
            ft.VerticalDivider(width=1, color="#E0E0E0"),
            carrito_col,
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    return ft.Container(
        content=estructura,
        bgcolor=crema,
        padding=30,
        expand=True,
        alignment=ft.alignment.top_center,
    )
