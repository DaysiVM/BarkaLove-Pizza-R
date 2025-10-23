# screens/kds.py
import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

import flet as ft

from utils.kds import listar_pedidos, actualizar_estado
import utils.recetas as rx  # para guía de receta vigente


# Paleta consistente con el proyecto
ROJO = "#E63946"
AMARILLO = "#FFD93D"
AZUL = "#2196F3"
VERDE = "#2A9D8F"
NEGRO = "#1F1F1F"
CREMA = "#FFF8E7"
BLANCO = "#FFFFFF"
GRIS_CLARO = "#EDEDED"


def _parse_dt(s: Optional[str]) -> Optional[datetime]:
    if not s:
        return None
    # acepta formatos ISO o "YYYY-MM-DD HH:MM:SS"
    try:
        if "T" in s:
            return datetime.fromisoformat(s.replace("Z", ""))
        return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
    except Exception:
        try:
            return datetime.fromisoformat(s)
        except Exception:
            return None


def _mins_since(s: Optional[str]) -> Optional[float]:
    dt = _parse_dt(s)
    if not dt:
        return None
    return (datetime.now() - dt).total_seconds() / 60.0


def pantalla_kds(page: ft.Page, mostrar_pantalla):
    """
    KDS: 4 columnas (Confirmado, Horno, Empaque, Listo).
    - Auto-poll cada 3s (HU: <5s).
    - Cards limpias, texto negro uniforme.
    - Al seleccionar un pedido se muestra a la derecha la 'Guía receta vigente' (utils.recetas.vigente).
    - Alerta visual si estado == 'horno' y el tiempo supera tiempo_min + tolerancia (parpadeo simple).
    """
    page.bgcolor = CREMA
    page.scroll = ft.ScrollMode.AUTO
    page.clean()

    # ===== Responsive helpers =====
    def bp():
        w = page.width or 1280
        size = "xs" if w < 900 else ("md" if w < 1280 else "lg")
        return size, w

    state = {
        "pad": 16,
        "col_w": 320,
        "card_h": 140,
        "title_size": 28,
        "col_title": 18,
        "body": 14,
        "guide_w": 360,
        "poll_secs": 3,
        "active": True,  # para cortar el bucle de refresco si sales de esta pantalla
    }

    def recompute_sizes():
        size, w = bp()
        if size == "lg":
            state.update(col_w=360, guide_w=380, title_size=30, col_title=18, body=14)
        elif size == "md":
            state.update(col_w=320, guide_w=360, title_size=28, col_title=17, body=14)
        else:
            state.update(col_w=min(380, int(w * 0.95)), guide_w=min(380, int(w * 0.95)),
                         title_size=26, col_title=16, body=14)

    recompute_sizes()

    # ===== Título y barra superior =====
    titulo = ft.Text("KDS • Cocina", size=state["title_size"], color=ROJO, weight=ft.FontWeight.BOLD)

    # Filtros simples
    dd_filtro_tipo = ft.Dropdown(
        label="Filtrar por tipo de pizza",
        options=[ft.dropdown.Option("Todos")] + [ft.dropdown.Option(t) for t in rx.listar_tipos()],
        value="Todos",
        width=240,
        color=NEGRO,
        text_size=14,
    )
    dd_filtro_estado = ft.Dropdown(
        label="Estado",
        options=[ft.dropdown.Option("Todos"), ft.dropdown.Option("confirmado"),
                 ft.dropdown.Option("horno"), ft.dropdown.Option("empaque"), ft.dropdown.Option("listo")],
        value="Todos",
        width=180,
        color=NEGRO,
        text_size=14,
    )

    # Botón volver a inicio
    btn_volver = ft.ElevatedButton(
        "⬅ Inicio", bgcolor=ROJO, color="white",
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        on_click=lambda _: mostrar_pantalla("inicio"),
        height=36,
    )

    topbar = ft.Row(
        controls=[titulo, ft.Container(expand=True), dd_filtro_tipo, dd_filtro_estado, btn_volver],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # ===== Columnas (listas) =====
    col_confirmado_title = ft.Text("Confirmado", size=state["col_title"], color=NEGRO, weight=ft.FontWeight.BOLD)
    col_horno_title = ft.Text("Horno", size=state["col_title"], color=NEGRO, weight=ft.FontWeight.BOLD)
    col_empaque_title = ft.Text("Empaque", size=state["col_title"], color=NEGRO, weight=ft.FontWeight.BOLD)
    col_listo_title = ft.Text("Listo", size=state["col_title"], color=NEGRO, weight=ft.FontWeight.BOLD)

    col_confirmado_list = ft.ListView(expand=True, spacing=10, padding=0, auto_scroll=False)
    col_horno_list = ft.ListView(expand=True, spacing=10, padding=0, auto_scroll=False)
    col_empaque_list = ft.ListView(expand=True, spacing=10, padding=0, auto_scroll=False)
    col_listo_list = ft.ListView(expand=True, spacing=10, padding=0, auto_scroll=False)

    def col_box(title_ctrl, list_ctrl):
        return ft.Container(
            bgcolor=BLANCO,
            border_radius=12,
            padding=10,
            width=state["col_w"],
            content=ft.Column([title_ctrl, ft.Divider(), list_ctrl], spacing=8, expand=True),
        )

    col_confirmado = col_box(col_confirmado_title, col_confirmado_list)
    col_horno = col_box(col_horno_title, col_horno_list)
    col_empaque = col_box(col_empaque_title, col_empaque_list)
    col_listo = col_box(col_listo_title, col_listo_list)

    # ===== Panel de Guía a la derecha =====
    guia_title = ft.Text("Guía receta vigente", size=18, color=NEGRO, weight=ft.FontWeight.W_600)
    guia_list = ft.Column([], spacing=4)
    guia_horno = ft.Text("", size=14, color=NEGRO)
    guia_box = ft.Container(
        bgcolor=BLANCO,
        border_radius=12,
        padding=12,
        width=state["guide_w"],
        content=ft.Column([guia_title, ft.Divider(), guia_list, ft.Divider(), guia_horno], spacing=8),
    )

    # Texto inferior con ayuda breve
    hint = ft.Text(
        "Consejo: toca un pedido para ver su guía vigente. Actualiza estados con los botones en cada tarjeta.",
        size=12, color=NEGRO,
    )

    # ===== Grid principal =====
    grid = ft.ResponsiveRow(
        controls=[
            ft.Container(col_confirmado, padding=0, col={"xs": 12, "md": 6, "lg": 3}),
            ft.Container(col_horno,      padding=0, col={"xs": 12, "md": 6, "lg": 3}),
            ft.Container(col_empaque,    padding=0, col={"xs": 12, "md": 6, "lg": 3}),
            ft.Container(col_listo,      padding=0, col={"xs": 12, "md": 6, "lg": 3}),
            ft.Container(guia_box,       padding=0, col={"xs": 12, "md": 12, "lg": 12}),
        ],
        columns=12, spacing=12, run_spacing=12,
    )

    root = ft.Container(
        content=ft.Column([topbar, ft.Container(height=8), grid, ft.Container(height=6), hint],
                          spacing=6, expand=True),
        padding=state["pad"], expand=True, bgcolor=CREMA,
    )

    page.add(root)
    page.update()

    # ===== Lógica de renderizado =====
    selected_pedido: Optional[Dict[str, Any]] = None

    def _badge(txt: str, color_bg: str):
        return ft.Container(
            bgcolor=color_bg, padding=ft.padding.symmetric(2, 6),
            border_radius=20, content=ft.Text(txt, size=12, color="white")
        )

    def _estado_color(estado: str) -> str:
        return {
            "confirmado": AZUL,
            "horno": AMARILLO,
            "empaque": "#8E24AA",  # morado
            "listo": VERDE,
        }.get(estado, GRIS_CLARO)

    def _render_card(p: Dict[str, Any]) -> ft.Control:
        """
        Tarjeta de pedido:
        - Encabezado: #orden — tipo — estado(badge)
        - Detalle corto: cliente, tamaño/masa/salsa, ingredientes, tiempo transcurrido
        - Acciones por estado
        - Si está 'horno' y excede tiempo objetivo (receta vigente) → borde rojo + badge ALERTA
        """
        orden = p.get("orden") or p.get("id") or "—"
        cliente = p.get("cliente") or "—"
        tipo = p.get("receta_tipo") or "—"
        estado = p.get("estado") or "confirmado"
        tamano = p.get("tamano") or "—"
        masa = p.get("masa") or "—"
        salsa = p.get("salsa") or "—"
        ing_list = p.get("ingredientes") or []
        fecha = p.get("fecha") or p.get("hora")
        mins = _mins_since(fecha)
        mins_txt = f"{mins:.1f} min" if mins is not None else "—"

        # Alerta sobrecocción si está en horno y supera tiempo objetivo
        alerta = False
        alerta_msg = ""
        if estado == "horno" and tipo:
            ver = rx.vigente(tipo)
            if ver and ver.horno:
                tmin = ver.horno.get("tiempo_min") or 0
                tol = (ver.horno.get("tol") or {}).get("tiempo", 0)
                objetivo = tmin + tol
                if mins is not None and mins > objetivo:
                    alerta = True
                    alerta_msg = f"⚠ Sobretiempo: {mins_txt} > {objetivo} min"

        # Encabezado
        title = ft.Row(
            [
                ft.Text(f"#{orden} — {tipo}", size=16, weight=ft.FontWeight.W_600, color=NEGRO),
                ft.Container(expand=True),
                _badge(estado.upper(), _estado_color(estado)),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # Línea de detalle
        linea_1 = ft.Text(f"Cliente: {cliente}", size=13, color=NEGRO)
        linea_2 = ft.Text(f"{tamano} • {masa} + {salsa}", size=13, color=NEGRO)
        linea_3 = ft.Text(f"Ingr.: {', '.join(ing_list) if ing_list else '—'}", size=13, color=NEGRO)
        linea_4 = ft.Text(f"Tiempo: {mins_txt}", size=12, color=NEGRO)

        # Acciones por estado
        def _set_estado(nuevo: str):
            ok = actualizar_estado(p.get("id") or p.get("orden"), nuevo)
            if ok:
                # feedback visual simple
                page.snack_bar = ft.SnackBar(ft.Text(f"Pedido #{orden} → {nuevo}", color="white"), bgcolor=VERDE)
                page.snack_bar.open = True
                page.update()
                # Forzar un refresh inmediato
                _refresh_lists()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("No se pudo actualizar el estado.", color="white"), bgcolor=ROJO)
                page.snack_bar.open = True
                page.update()

        # Botonera
        botones: List[ft.Control] = []
        if estado == "confirmado":
            botones = [
                ft.ElevatedButton("A horno", bgcolor=AMARILLO, color=NEGRO, height=32,
                                  on_click=lambda _: _set_estado("horno")),
            ]
        elif estado == "horno":
            botones = [
                ft.ElevatedButton("Empacar", bgcolor=AZUL, color="white", height=32,
                                  on_click=lambda _: _set_estado("empaque")),
            ]
        elif estado == "empaque":
            botones = [
                ft.ElevatedButton("Listo", bgcolor=VERDE, color="white", height=32,
                                  on_click=lambda _: _set_estado("listo")),
            ]
        else:
            # listo
            botones = [
                ft.ElevatedButton("↺ Reabrir (Empaque)", bgcolor="#8E24AA", color="white", height=32,
                                  on_click=lambda _: _set_estado("empaque")),
            ]

        # Tarjeta
        border_color = ROJO if alerta else GRIS_CLARO
        alerta_row = ft.Row(
            [ft.Text(alerta_msg, size=12, color=ROJO)] if alerta else [],
            alignment=ft.MainAxisAlignment.START,
        )

        card = ft.Container(
            bgcolor=BLANCO,
            border_radius=10,
            padding=10,
            border=ft.border.all(2, border_color),
            content=ft.Column(
                [
                    title,
                    linea_1,
                    linea_2,
                    linea_3,
                    ft.Row([linea_4] + ([ _badge("ALERTA", ROJO) ] if alerta else []),
                           alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    alerta_row,
                    ft.Row(botones, spacing=8),
                ],
                spacing=4,
            ),
            on_click=lambda _: _select_pedido(p),
        )
        return card

    # ===== Carga y filtrado =====
    def _passes_filters(p: Dict[str, Any]) -> bool:
        tipo_sel = dd_filtro_tipo.value
        est_sel = dd_filtro_estado.value
        if tipo_sel and tipo_sel != "Todos":
            if (p.get("receta_tipo") or "").lower() != (tipo_sel or "").lower():
                return False
        if est_sel and est_sel != "Todos":
            if (p.get("estado") or "confirmado") != est_sel:
                return False
        return True

    def _refresh_lists():
        col_confirmado_list.controls.clear()
        col_horno_list.controls.clear()
        col_empaque_list.controls.clear()
        col_listo_list.controls.clear()

        data = listar_pedidos()  # trae todo
        # Ordenar por fecha asc (más antiguos arriba)
        def _key(p):
            dt = _parse_dt(p.get("fecha") or p.get("hora"))
            return dt or datetime.min

        for p in sorted(data, key=_key):
            if not _passes_filters(p):
                continue
            estado = p.get("estado") or "confirmado"
            ctrl = _render_card(p)
            if estado == "confirmado":
                col_confirmado_list.controls.append(ctrl)
            elif estado == "horno":
                col_horno_list.controls.append(ctrl)
            elif estado == "empaque":
                col_empaque_list.controls.append(ctrl)
            else:
                col_listo_list.controls.append(ctrl)

        page.update()

    # ===== Guía receta vigente (panel derecho) =====
    def _pm_str(n, tol, unidad="g"):
        return f"{n} ± {tol} {unidad}"

    def _select_pedido(p: Dict[str, Any]):
        nonlocal selected_pedido
        selected_pedido = p
        _render_guide()

    def _render_guide():
        guia_list.controls.clear()
        guia_horno.value = ""
        if not selected_pedido:
            guia_list.controls.append(ft.Text("Seleccione un pedido para ver la guía.", size=14, color=NEGRO))
            page.update()
            return

        tipo = selected_pedido.get("receta_tipo")
        ver = rx.vigente(tipo) if tipo else None

        # Cabecera
        guia_title.value = f"Guía receta vigente — {tipo or 'N/D'}"
        if not ver:
            guia_list.controls.append(ft.Text("No hay receta vigente para este tipo.", size=14, color=NEGRO))
            page.update()
            return

        ing = ver.ingredientes or {}
        # Masa y Salsa siempre
        if "Masa" in ing:
            d = ing["Masa"]; guia_list.controls.append(ft.Text(f"• Masa:  {_pm_str(d['gramos'], d['tol'])}", size=14, color=NEGRO))
        if "Salsa" in ing:
            d = ing["Salsa"]; guia_list.controls.append(ft.Text(f"• Salsa: {_pm_str(d['gramos'], d['tol'])}", size=14, color=NEGRO))

        # SOLO los toppings que el pedido incluyó (limpio y útil para cocina)
        pedido_toppings = selected_pedido.get("ingredientes") or []
        for t in pedido_toppings:
            if t in ing:
                d = ing[t]
                guia_list.controls.append(ft.Text(f"• {t}: {_pm_str(d['gramos'], d['tol'])}", size=14, color=NEGRO))

        # Horno
        h = ver.horno or {}
        guia_horno.value = (
            f"Horno objetivo: "
            f"{_pm_str(h.get('temp_c', 0), (h.get('tol') or {}).get('temp', 0), '°C')}  •  "
            f"{_pm_str(h.get('tiempo_min', 0), (h.get('tol') or {}).get('tiempo', 0), 'min')}"
        )
        page.update()

    # ===== Polling asíncrono (cada 3s) =====
    async def _poll_loop():
        # Primer render
        _refresh_lists()
        while state["active"]:
            await asyncio.sleep(state["poll_secs"])
            if not state["active"]:
                break
            _refresh_lists()
            # si hay pedido seleccionado, re-evaluar guía (por si cambió tipo / receta)
            if selected_pedido:
                _render_guide()

    # Lanzar tarea
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        asyncio.run(_poll_loop())
    else:
        asyncio.create_task(_poll_loop())

    # ===== Handlers de filtros =====
    def on_change_filters(_):
        _refresh_lists()

    dd_filtro_tipo.on_change = on_change_filters
    dd_filtro_estado.on_change = on_change_filters

    # ===== on_resize =====
    def on_resize(_):
        recompute_sizes()
        # ajustar anchos de columnas y guía
        for cont in [col_confirmado, col_horno, col_empaque, col_listo]:
            cont.width = state["col_w"]
        guia_box.width = state["guide_w"]
        titulo.size = state["title_size"]
        page.update()

    page.on_resize = on_resize

    # ===== Limpieza al salir (por si tu router reusa page) =====
    def _dispose():
        state["active"] = False

    # Puedes enganchar _dispose en tu router cuando cambies de pantalla
    # o si manejas un stack de pantallas, llamar _dispose() manualmente.
    # Aquí lo devolvemos por si lo quieres usar.
    return root
