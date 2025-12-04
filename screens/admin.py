# screens/admin.py
from __future__ import annotations
import flet as ft
import asyncio
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional

# utilidades del proyecto (si no existen, código maneja excepciones)
try:
    from utils.kds import listar_pedidos
except Exception:
    def listar_pedidos():
        return []

try:
    import utils.inventario as invmod
except Exception:
    invmod = None

try:
    import utils.recetas as rx
except Exception:
    rx = None

# pantallas hijas (opcional)
try:
    import screens.manuales_usuario as mu
except Exception:
    mu = None

# Paleta
ROJO = "#E63946"
CREMA = "#FFF8E7"
NEGRO = "#1F1F1F"
AMARILLO = "#FFD93D"
AZUL = "#2196F3"
VERDE = "#2A9D8F"
GRIS = "#9E9E9E"

# Config
REFRESH_SECONDS = 60
COST_RATIO = 0.50
SPARK_WIDTH = 20


def _format_dt(dt: Optional[datetime]) -> str:
    if not dt:
        return "—"
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def _mini_sparkline(values: List[float], width: int = SPARK_WIDTH) -> str:
    if not values:
        return ""
    n = min(width, len(values))
    vals = values[-n:]
    lo = min(vals)
    hi = max(vals)
    if hi == lo:
        return "".join("▮" for _ in vals)
    chars = "▱▂▃▄▅▆▇█"
    out = []
    for v in vals:
        norm = (v - lo) / (hi - lo)
        idx = int(norm * (len(chars) - 1))
        out.append(chars[idx])
    return "".join(out)


def pantalla_admin(page: ft.Page, mostrar_pantalla):
    """
    Panel de administración combinado:
      - Dashboard con KPIs + auto-refresh
      - Tarjetas para navegar a pantallas administrativas
    """
    page.bgcolor = CREMA
    page.clean()

    # Guard: requiere sesión admin
    is_admin = page.session.get("admin_auth") is True
    if not is_admin:
        page.snack_bar = ft.SnackBar(ft.Text("Necesitas iniciar sesión de admin.", color="white"), bgcolor=ROJO)
        page.snack_bar.open = True
        page.update()
        mostrar_pantalla("admin_login")
        return

    usuario = page.session.get("admin_user") or "admin"

    def logout(_):
        page.session.remove("admin_auth")
        page.session.remove("admin_user")
        page.update()
        mostrar_pantalla("inicio")

    # Header
    header = ft.Row(
        [
            ft.Text("Panel de Administración", size=26, color=ROJO, weight=ft.FontWeight.BOLD, expand=True),
            ft.Text(f"👤 {usuario}", size=14, color=GRIS),
            ft.ElevatedButton("Cerrar sesión", bgcolor=ROJO, color="white", height=36,
                              style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                              on_click=logout),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    # ---------------- Dashboard (arriba) ----------------
    ventas_lbl = ft.Text("—", size=28, weight=ft.FontWeight.BOLD, color=NEGRO)
    produ_lbl = ft.Text("—", size=28, weight=ft.FontWeight.BOLD, color=NEGRO)
    costos_lbl = ft.Text("—", size=28, weight=ft.FontWeight.BOLD, color=NEGRO)

    last_update_txt = ft.Text("Última actualización: —", size=12, color=GRIS)
    low_stock_txt = ft.Text("", size=12, color=ROJO)

    card_reportes = ft.Container(
        bgcolor="white",
        border_radius=12,
        padding=16,
        content=ft.Column(
            [
                ft.Text("Reportes Históricos", size=18, weight=ft.FontWeight.W_600, color=NEGRO),
                ft.Text("Consulta ventas, gastos, inventario y daños.", size=14, color=GRIS),
                ft.Container(height=8),
                ft.ElevatedButton(
                    "Abrir",
                    bgcolor=AZUL, color="white", height=40,
                    on_click=lambda _: mostrar_pantalla("reportes")
                ),
            ],
            spacing=6,
        ),
    )

    card_comparacion = ft.Container(
        bgcolor="white",
        border_radius=12,
        padding=16,
        content=ft.Column(
            [
                ft.Text("Comparación consumos", size=18, weight=ft.FontWeight.W_600, color=NEGRO),
                ft.Text("Compara consumo entre turnos por rango de fechas.", size=14, color=GRIS),
                ft.Container(height=8),
                ft.ElevatedButton(
                    "Abrir",
                    bgcolor=AZUL, color="white", height=40,
                    on_click=lambda _: mostrar_pantalla("comparacion_consumos")
                ),
            ],
            spacing=6,
        ),
    )

    card_respaldo = ft.Container(
        bgcolor="white",
        border_radius=12,
        padding=16,
        content=ft.Column(
            [
                ft.Text("Respaldo de datos", size=18, weight=ft.FontWeight.W_600, color=NEGRO),
                ft.Text("Gestiona copias de seguridad: crear, restaurar y descargar.", size=14, color=GRIS),
                ft.Container(height=8),
                ft.ElevatedButton(
                    "Abrir",
                    bgcolor=VERDE, color="white", height=40,
                    on_click=lambda _: mostrar_pantalla("admin_respaldo")
                ),
            ],
            spacing=6,
        ),
    )

    btn_refresh = ft.ElevatedButton("Actualizar ahora", icon=ft.Icons.REFRESH, bgcolor=AZUL, color="white", height=36)
    toggle_autorefresh = ft.Switch(label="Auto-refresh", value=True)

    card_documentacion_tecnica = ft.Container(
        bgcolor="white",
        border_radius=12,
        padding=16,
        content=ft.Column(
            [
                ft.Text("Documentación técnica", size=18, weight=ft.FontWeight.W_600, color=NEGRO),
                ft.Text("Abre el PDF de documentación técnica del sistema.", size=14, color=GRIS),
                ft.Container(height=8),
                ft.ElevatedButton(
                    "Abrir",
                    bgcolor=VERDE, color="white", height=40,
                    on_click=lambda _: mostrar_pantalla("documentacion_tecnica")
                ),
            ],
            spacing=6,
        ),
    )

    card_videos_tutoriales = ft.Container(
        bgcolor="white",
        border_radius=12,
        padding=16,
        content=ft.Column(
            [
                ft.Text("Videos tutoriales", size=18, weight=ft.FontWeight.W_600, color=NEGRO),
                ft.Text("Accede a videos de apoyo y tutoriales en YouTube.", size=14, color=GRIS),
                ft.Container(height=8),
                ft.ElevatedButton(
                    "Abrir",
                    bgcolor=AZUL, color="white", height=40,
                    on_click=lambda _: mostrar_pantalla("videos_tutoriales")
                ),
            ],
            spacing=6,
        ),
    )
    card_costos = ft.Container(
        bgcolor="white", border_radius=12, padding=12,
        content=ft.Column([ft.Text("Costos (USD)", size=12, color=GRIS), costos_lbl, spark_costos], spacing=6)
    )

    kpi_row = ft.Row([card_ventas, card_produ, card_costos], spacing=12, alignment=ft.MainAxisAlignment.SPACE_EVENLY)

    grid = ft.ResponsiveRow(
        controls=[
            ft.Container(card_recetas, col={"xs": 12, "md": 6, "lg": 6}),
            ft.Container(card_kds, col={"xs": 12, "md": 6, "lg": 6}),
            ft.Container(card_reportes, col={"xs": 12, "md": 6, "lg": 6}),
            ft.Container(card_comparacion, col={"xs": 12, "md": 6, "lg": 6}),
            ft.Container(card_respaldo, col={"xs": 12, "md": 6, "lg": 6}),
            ft.Container(card_manuales_usuario, col={"xs": 12, "md": 6, "lg": 6}),
            ft.Container(card_videos_tutoriales, col={"xs": 12, "md": 6, "lg": 6}),
            ft.Container(card_documentacion_tecnica, col={"xs": 12, "md": 6, "lg": 6}),
        ],
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    dashboard_box = ft.Container(
        content=ft.Column([dashboard_header, ft.Divider(), kpi_row, ft.Row([last_update_txt, ft.Container(expand=True), low_stock_txt])],
                          spacing=8),
        padding=12, border_radius=12, bgcolor=CREMA
    )

    # ---------------- Cards (funciones) ----------------
    # Nota: el botón "Abrir" se unifica a color AZUL en todas las tarjetas
    def _card(title: str, desc: str, key: str, disabled: bool = False):
        btn = ft.ElevatedButton(
            "Abrir",
            bgcolor=AZUL, color="white", height=40,
            on_click=(lambda _: mostrar_pantalla(key)) if not disabled else None,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        )
        if disabled:
            btn.disabled = True
            btn.tooltip = "Requiere login de administrador"
        return ft.Container(
            bgcolor="white",
            border_radius=12,
            padding=16,
            width=320,
            content=ft.Column(
                [
                    ft.Text(title, size=18, weight=ft.FontWeight.W_600, color=NEGRO),
                    ft.Text(desc, size=14, color=GRIS),
                    ft.Container(height=8),
                    btn,
                ],
                spacing=6,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

    cards = [
        _card("Recetas estandarizadas", "Administra versiones, activa receta vigente y revisa historial.", "admin_recetas"),
        _card("KDS (Cocina)", "Visualiza pedidos confirmados y marca como listos.", "kds", disabled=not is_admin),
        _card("Inventario de ingredientes", "Gestiona cantidades, ajusta stock y revisa alertas cuando el mínimo está alcanzado.", "admin_inventario", disabled=not is_admin),
        _card("Respaldo de datos", "Gestiona copias de seguridad: crear, restaurar y descargar.", "admin_respaldo", disabled=not is_admin),
        _card("Indicadores", "Productividad, tiempos y errores", "admin_indicadores", disabled=not is_admin),
        _card("Manuales de Usuario", "Visualiza y abre manuales de usuario en formato PDF.", "manuales_usuario"),
        _card("Videos tutoriales", "Accede a videos de apoyo y tutoriales en YouTube.", "videos_tutoriales"),
    ]

    # Construimos filas de 2 en 2 y las centramos
    card_rows: List[ft.Control] = []
    for i in range(0, len(cards), 2):
        left = cards[i]
        right = cards[i+1] if (i+1) < len(cards) else ft.Container(width=320)  # placeholder si impar
        row = ft.Row([left, right], alignment=ft.MainAxisAlignment.CENTER, spacing=24)
        card_rows.append(row)

    # ---------------- Dashboard logic ----------------
    stop_flag = {"stop": False}
    last_update_ts: Optional[datetime] = None

    def _collect_metrics():
        ventas_total = 0.0
        produ_total = 0
        series_ventas: List[float] = []
        series_produ: List[int] = []
        series_costos: List[float] = []
        try:
            pedidos = listar_pedidos() or []
        except Exception:
            pedidos = []

        for p in pedidos:
            try:
                v = float(p.get("total_visual", 0) or 0)
            except Exception:
                v = 0.0
            ventas_total += v
            series_ventas.append(v)

            qty_sum = 0
            items = p.get("items") or p.get("productos") or []
            if isinstance(items, list) and items:
                for it in items:
                    try:
                        q = int(it.get("cantidad") or it.get("qty") or 1)
                    except Exception:
                        q = 1
                    qty_sum += q
            else:
                try:
                    qty_sum = int(p.get("cantidad", 0) or 0)
                except Exception:
                    qty_sum = 0
            produ_total += qty_sum
            series_produ.append(qty_sum)

            series_costos.append(v * COST_RATIO)

        if not series_ventas:
            series_ventas = []
            series_produ = []
            series_costos = []

        bajos = []
        try:
            if invmod is not None:
                inv_list = invmod.listar_inventario() or []
                bajos = [i for i in inv_list if int(i.get("cantidad_actual", 0)) <= int(i.get("stock_minimo", 0))]
        except Exception:
            bajos = []

        return {
            "ventas_total": round(ventas_total, 2),
            "produ_total": int(produ_total),
            "costos_total": round(sum(series_costos), 2),
            "series_ventas": series_ventas,
            "series_produ": series_produ,
            "series_costos": series_costos,
            "bajos": bajos,
        }

    def _render_metrics():
        nonlocal last_update_ts
        data = _collect_metrics()
        ventas_lbl.value = f"${data['ventas_total']:,.2f}"
        produ_lbl.value = f"{data['produ_total']}"
        costos_lbl.value = f"${data['costos_total']:,.2f}"

        spark_ventas.value = _mini_sparkline(data["series_ventas"])
        spark_produ.value = _mini_sparkline([float(x) for x in data["series_produ"]])
        spark_costos.value = _mini_sparkline(data["series_costos"])

        bajos = data.get("bajos", [])
        if bajos:
            try:
                nombres = ", ".join(i.get("ingrediente") for i in bajos[:5])
            except Exception:
                nombres = ", ".join(str(i) for i in bajos[:5])
            low_stock_txt.value = f"🔔 Stock bajo: {nombres}"
        else:
            low_stock_txt.value = ""

        last_update_ts = datetime.now()
        last_update_txt.value = f"Última actualización: {_format_dt(last_update_ts)}"
        page.update()

    def _manual_refresh(_e=None):
        try:
            _render_metrics()
            page.snack_bar = ft.SnackBar(ft.Text("Dashboard actualizado", color="white"), bgcolor=VERDE)
            page.snack_bar.open = True
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error refrescando: {ex}", color="white"), bgcolor=ROJO)
            page.snack_bar.open = True
        page.update()

    btn_refresh.on_click = _manual_refresh

    async def _auto_refresher():
        while not stop_flag["stop"]:
            await asyncio.sleep(REFRESH_SECONDS)
            if toggle_autorefresh.value:
                try:
                    _render_metrics()
                except Exception:
                    pass

    # ---------------- Layout & montaje ----------------
    # Combina dashboard + filas de tarjetas (2 en 2 centradas)
    layout_children = [header, ft.Divider(), dashboard_box, ft.Divider()]
    layout_children.extend(card_rows)

    layout = ft.Column(layout_children, spacing=12, expand=True)
    root = ft.Container(layout, padding=16, bgcolor=CREMA, expand=True)
    page.add(root)

    # primera pintada y arranque del refresco
    _render_metrics()

    # Lanzador robusto del auto-refresher: evitar "coroutine was never awaited"
    try:
        loop = asyncio.get_running_loop()
        # si llegamos aquí, hay un loop: creamos la tarea
        loop.create_task(_auto_refresher())
    except RuntimeError:
        # no hay loop corriendo: arrancamos el refresco en un hilo daemon con su propio loop
        def _bg_runner():
            try:
                asyncio.run(_auto_refresher())
            except Exception:
                # prevenir que errores rompan el hilo
                pass

        t = threading.Thread(target=_bg_runner, daemon=True)
        t.start()

    # Nota: para detener el refresco desde fuera, setear stop_flag["stop"] = True
    return root
