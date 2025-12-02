# screens/kds.py
import flet as ft
import asyncio
import os
import re
from datetime import datetime, timedelta

from utils.kds import listar_pedidos, actualizar_estado
# La receta vigente es opcional, pero si existe la usamos para mostrar guía
try:
    import utils.recetas as rx
except Exception:
    rx = None

# ======= Paleta =======
ROJO = "#E63946"
VERDE = "#2A9D8F"
CREMA = "#FFF8E7"
NEGRO = "#1F1F1F"
AMARILLO = "#FFD93D"
AZUL = "#2196F3"
GRIS_CLARO = "#F4F4F4"
BLANCO = "#FFFFFF"

# ======= Dónde están los logs de cocción =======
LOG_PATH = os.path.join(os.path.dirname(__file__), "..", "utils", "logs", "coccion.log")
LOG_PATH = os.path.abspath(LOG_PATH)


def _read_recent_alerts(minutes_back: int = 2):
    """
    Lee utils/logs/coccion.log y devuelve un diccionario:
      { orden_id:int -> {"mensajes": [str], "last_ts": datetime} }
    Solo incluye eventos dentro de los últimos `minutes_back` minutos.
    """
    results = {}
    if not os.path.exists(LOG_PATH):
        return results

    now = datetime.now()
    limit = now - timedelta(minutes=minutes_back)

    # Formato de línea:
    # [YYYY-mm-dd HH:MM:SS] ALERTA_SOBRECOCCION | Pedido #123 | ...
    # [YYYY-mm-dd HH:MM:SS] ALERTA_SENSOR | Pedido #123 | ...
    pattern = re.compile(
        r"^\[(?P<ts>[\d\-:\s]+)\]\s+(?P<tipo>ALERTA_[A-Z_]+)\s\|\s+Pedido\s+#(?P<id>\d+)\s\|\s+(?P<msg>.+)$"
    )

    try:
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            for line in f:
                m = pattern.match(line.strip())
                if not m:
                    continue
                ts = datetime.strptime(m.group("ts"), "%Y-%m-%d %H:%M:%S")
                if ts < limit:
                    continue
                pid = int(m.group("id"))
                msg = f"{m.group('tipo').replace('_', ' ')} — {m.group('msg')}"
                d = results.get(pid, {"mensajes": [], "last_ts": ts})
                d["mensajes"].append(msg)
                if ts > d.get("last_ts", ts):
                    d["last_ts"] = ts
                results[pid] = d
    except Exception:
        # si el archivo está en uso, devolvemos lo que tengamos
        pass

    return results


def _estado_badge_color(estado: str) -> str:
    estado = (estado or "").lower()
    if "prepa" in estado:
        return AMARILLO
    if "horno" in estado:
        return AZUL
    if "empaq" in estado:
        return "#9C27B0"  # morado
    if "list" in estado or "final" in estado:
        return VERDE
    return NEGRO


def _human_delta(iso_or_none: str) -> str:
    try:
        if not iso_or_none:
            return "—"
        dt = datetime.fromisoformat(iso_or_none)
        delta = datetime.now() - dt
        s = int(delta.total_seconds())
        if s < 60:
            return f"{s}s"
        m = s // 60
        return f"{m}m {s%60}s"
    except Exception:
        return "—"


def _mini_guia(tipo: str | None):
    """Si hay receta vigente, retornamos (texto_guia, temp, tiempo)."""
    if not rx or not tipo:
        return "Receta: —", None, None
    try:
        ver = rx.vigente(tipo)
        if not ver or not ver.horno:
            return "Receta: —", None, None
        h = ver.horno or {}
        temp = h.get("temp_c")
        tmin = h.get("tiempo_min")
        return f"Receta: {tipo} • Objetivo {temp}°C • {tmin} min", temp, tmin
    except Exception:
        return "Receta: —", None, None


def pantalla_kds(page: ft.Page, mostrar_pantalla):
    """
    KDS: Panel simple de cocina con estados y alertas visuales.
    - Filtro por estado
    - Búsqueda por #orden o cliente
    - Refresco automático
    - Botones de cambio de estado en cada tarjeta
    """
    page.bgcolor = CREMA
    page.scroll = ft.ScrollMode.AUTO

    # ===== Top Bar =====
    titulo = ft.Text("👨🏻‍🍳 KDS — Cocina", size=28, color=ROJO, weight=ft.FontWeight.BOLD)

    # Filtros
    dd_estado = ft.Dropdown(
        label="Estado",
        options=[
            ft.dropdown.Option("Todos"),
            ft.dropdown.Option("Preparación"),
            ft.dropdown.Option("Horno"),
            ft.dropdown.Option("Empaque"),
            ft.dropdown.Option("Listo"),
        ],
        value="Todos",
        width=220,
        color=NEGRO,
    )
    txt_buscar = ft.TextField(
        label="Buscar (#orden o cliente)",
        hint_text="Ej. 1234 o Juan",
        width=280,
        color=NEGRO,
        text_size=14,
    )

    btn_refrescar = ft.ElevatedButton(
        "Refrescar",
        icon=ft.Icons.REFRESH,
        bgcolor=AZUL,
        color=BLANCO,
        on_click=lambda _: _repaint(),
        height=40,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
    )

    btn_volver = ft.TextButton(
        "⬅ Volver",
        on_click=lambda _: mostrar_pantalla("admin"),
        style=ft.ButtonStyle(color={"": NEGRO}),
    )

    top = ft.Row(
        controls=[btn_volver, titulo, ft.Container(expand=True), dd_estado, txt_buscar, btn_refrescar],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # ===== Contenedor de tarjetas =====
    grid = ft.ResponsiveRow(columns=12, spacing=12, run_spacing=12)

    cont = ft.Container(
        content=grid,
        padding=12,
        bgcolor=CREMA,
        expand=True,
    )

    # ===== Render helpers =====
    def _acciones(pid: int, estado_actual: str):
        def set_estado(nuevo: str):
            ok = actualizar_estado(pid, nuevo)
            if ok:
                page.snack_bar = ft.SnackBar(ft.Text(f"Orden #{pid}: estado -> {nuevo}", color=BLANCO), bgcolor=VERDE)
                page.snack_bar.open = True
                _repaint()
            else:
                page.snack_bar = ft.SnackBar(ft.Text(f"No se pudo actualizar la orden #{pid}", color=BLANCO), bgcolor=ROJO)
                page.snack_bar.open = True

        # Siguientes estados rápidos
        acciones = []
        estado = (estado_actual or "").lower()
        if "prepa" in estado:
            acciones = [
                ft.ElevatedButton("→ Horno", on_click=lambda _: set_estado("Horno"), bgcolor=AZUL, color=BLANCO, height=36),
            ]
        elif "horno" in estado:
            acciones = [
                ft.ElevatedButton("→ Empaque", on_click=lambda _: set_estado("Empaque"), bgcolor="#9C27B0", color=BLANCO, height=36),
            ]
        elif "empaq" in estado:
            acciones = [
                ft.ElevatedButton("→ Listo", on_click=lambda _: set_estado("Listo"), bgcolor=VERDE, color=BLANCO, height=36),
            ]
        else:
            acciones = []

        # Siempre permitir retroceder y marcar listo
        acciones_extras = [
            ft.OutlinedButton("Preparación", on_click=lambda _: set_estado("Preparación"), height=36),
            ft.OutlinedButton("Horno", on_click=lambda _: set_estado("Horno"), height=36),
            ft.OutlinedButton("Empaque", on_click=lambda _: set_estado("Empaque"), height=36),
            ft.ElevatedButton("Listo", on_click=lambda _: set_estado("Listo"), bgcolor=VERDE, color=BLANCO, height=36),
        ]
        return ft.Row(acciones + acciones_extras, spacing=8, wrap=True)

    def _card(p: dict, alerts_map: dict):
        pid = p.get("id") or p.get("orden")  # por compatibilidad
        cliente = p.get("cliente", "—")
        estado = p.get("estado") or "Preparación"
        tipo = p.get("receta_tipo") or "—"
        tam = p.get("tamano") or "—"
        hora = p.get("hora")  # iso

        # Mini guía receta
        guia_txt, temp_obj, tmin = _mini_guia(tipo)

        # Alertas recientes
        alerts = alerts_map.get(int(pid), {})
        msgs = alerts.get("mensajes", [])
        last_ts = alerts.get("last_ts")

        alerta_banner = None
        if msgs:
            alerta_banner = ft.Container(
                bgcolor=ROJO,
                padding=8,
                border_radius=8,
                content=ft.Column(
                    [ft.Text("⚠ ALERTAS RECIENTES", color=BLANCO, weight=ft.FontWeight.BOLD)]
                    + [ft.Text(f"• {m}", color=BLANCO, size=12) for m in msgs[-3:]],
                    spacing=2
                )
            )

        # Badges
        badge = ft.Container(
            bgcolor=_estado_badge_color(estado),
            padding=ft.padding.symmetric(6, 4),
            border_radius=20,
            content=ft.Text(estado, color=BLANCO, size=12, weight=ft.FontWeight.W_600),
        )
        since = ft.Text(f"Hace: {_human_delta(hora)}", size=12, color=NEGRO)

        # Cabecera
        head = ft.Row(
            [
                ft.Text(f"Orden #{pid}", size=18, weight=ft.FontWeight.BOLD, color=NEGRO),
                badge,
                ft.Container(expand=True),
                since,
            ],
            alignment=ft.MainAxisAlignment.START
        )

        # Info básica
        info = ft.Row(
            [
                ft.Text(f"Cliente: {cliente}", color=NEGRO, size=14),
                ft.Text("•", color=NEGRO),
                ft.Text(f"Tipo: {tipo}", color=NEGRO, size=14),
                ft.Text("•", color=NEGRO),
                ft.Text(f"Tamaño: {tam}", color=NEGRO, size=14),
            ],
            spacing=8,
            wrap=True
        )

        guia_row = ft.Text(guia_txt, color=NEGRO, size=13)

        actions = _acciones(pid, estado)

        # Tarjeta
        body_controls = [head, info, guia_row, ft.Divider()]
        if alerta_banner:
            body_controls = [head, alerta_banner, info, guia_row, ft.Divider()]
        body_controls.append(actions)

        return ft.Container(
            bgcolor=BLANCO,
            border_radius=12,
            padding=12,
            content=ft.Column(body_controls, spacing=8),
            col={"xs": 12, "md": 6, "lg": 4},
        )

    # ===== Pintado principal =====
    def _repaint():
        grid.controls.clear()

        estado_filtro = dd_estado.value or "Todos"
        q = (txt_buscar.value or "").strip().lower()

        # 1) datos base
        if estado_filtro == "Todos":
            pedidos = listar_pedidos()
        else:
            pedidos = listar_pedidos(estado=estado_filtro)

        # 2) filtrar por query (#orden o cliente)
        if q:
            def _match(p):
                pid = str(p.get("id") or p.get("orden") or "")
                cliente = (p.get("cliente") or "").lower()
                return q in pid or q in cliente
            pedidos = [p for p in pedidos if _match(p)]

        # 3) alertas recientes (map)
        alerts_map = _read_recent_alerts(minutes_back=3)

        # 4) ordenar por estado y hora (opc.)
        def _k(p):
            e = (p.get("estado") or "").lower()
            # priorizar no listos
            prio = 0 if ("list" not in e) else 1
            hora = p.get("hora") or ""
            return (prio, hora)
        pedidos.sort(key=_k)

        # 5) render cards
        for p in pedidos:
            grid.controls.append(_card(p, alerts_map))

        page.update()

    # Eventos de filtros
    dd_estado.on_change = lambda e: _repaint()
    txt_buscar.on_change = lambda e: _repaint()

    # ===== Auto-refresh loop =====
    stop_flag = {"stop": False}

    async def _auto_refresher():
        # pequeño ciclo para repintar cada ~2s
        while not stop_flag["stop"]:
            await asyncio.sleep(2.0)
            _repaint()

    # ===== Root =====
    root = ft.Column(
        controls=[top, cont],
        spacing=8,
        expand=True,
    )

    # Montaje
    page.clean()
    page.add(root)
    _repaint()  # primera pintada
    try:
        # correr refresco en background
        asyncio.create_task(_auto_refresher())
    except RuntimeError:
        # si no hay loop (modo blocking), ignorar auto-refresh
        pass

    # Para que al salir de KDS detengamos el refresco,
    # puedes gestionar stop_flag en tu router si lo deseas.
    return root
