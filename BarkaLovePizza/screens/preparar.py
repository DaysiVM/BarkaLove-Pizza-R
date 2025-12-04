# screens/preparar.py
from __future__ import annotations
import os
import json
import flet as ft
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

# utilidades del proyecto
from utils.pedidos import obtener_pedido
from utils.coccion import ejecutar_coccion_para_pedido, SensorState
from utils.kds import actualizar_estado

# receta vigente (opcional)
try:
    from utils.recetas import vigente as receta_vigente
except Exception:
    receta_vigente = None

# ---------- Paleta y config ----------
ROJO = "#E63946"
VERDE = "#2A9D8F"
CREMA = "#FFF8E7"
NEGRO = "#1F1F1F"
AMARILLO = "#FFD93D"
AZUL = "#2196F3"
GRIS = "#EDEDED"

PROMEDIO_MIN = 7               # fallback tiempo por tipo
UPDATE_INTERVAL_S = 1          # intervalo del loop que calcula tiempos
ESTADOS_CALCULABLES = {"EN_COLA", "EN_HORNO", "EN_PREPARACION", "PREPARACION", "COLA", "HORNO"}
ZERO_DEBOUNCE_CYCLES = 2      # evitar parpadeo cuando la estimación baja a 0
TIME_REF_MIN = 30             # referencia para normalizar barra de progreso de tiempo

# ---------- Helpers de tiempo ----------
def get_tiempo_min_por_tipo(tipo_pizza: Optional[str]) -> int:
    """Intenta obtener tiempo mínimo desde recetas; fallback a PROMEDIO_MIN."""
    try:
        if not tipo_pizza:
            return PROMEDIO_MIN
        if receta_vigente:
            r = receta_vigente(tipo_pizza)
            if r and isinstance(getattr(r, "horno", None), dict):
                tm = r.horno.get("tiempo_min")
                if isinstance(tm, (int, float)) and tm > 0:
                    return int(round(tm))
    except Exception:
        pass
    return PROMEDIO_MIN

def segundos_a_mmss(segundos: int) -> str:
    if segundos < 0:
        segundos = 0
    m = segundos // 60
    s = segundos % 60
    return f"{m:02d}:{s:02d}"

# ---------- Lectura robusta de pedidos activos ----------
def obtener_lista_pedidos_robusta() -> List[Dict[str, Any]]:
    """
    Intenta varias fuentes para obtener lista de pedidos:
      1) utils.pedidos.listar_pedidos_activos (si existe)
      2) llamar a obtener_pedido() sin parámetros (algunas impls)
      3) leer data/pedidos.json como fallback
    """
    # 1) intentar función especializada
    try:
        import utils.pedidos as pedidos_mod
        if hasattr(pedidos_mod, "listar_pedidos_activos"):
            try:
                res = pedidos_mod.listar_pedidos_activos()
                if isinstance(res, list):
                    return res
            except Exception:
                pass
    except Exception:
        pass

    # 2) intentar obtener_pedido sin args
    try:
        res = obtener_pedido()  # puede TypeError si requiere arg
        if isinstance(res, list):
            return res
        if isinstance(res, dict):
            return [res]
    except TypeError:
        pass
    except Exception:
        pass

    # 3) fallback: leer archivo data/pedidos.json
    try:
        path = os.path.join(os.getcwd(), "data", "pedidos.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                txt = f.read().strip()
                if not txt:
                    return []
                parsed = json.loads(txt)
                if isinstance(parsed, list):
                    return parsed
                if isinstance(parsed, dict):
                    return [parsed]
    except Exception:
        pass

    return []

def extraer_tipo_de_pedido(p: Any) -> Optional[str]:
    if not p:
        return None
    if isinstance(p, dict):
        return p.get("receta_tipo") or p.get("tipo_pizza") or p.get("tipo")
    return getattr(p, "receta_tipo", None) or getattr(p, "tipo_pizza", None) or getattr(p, "tipo", None)

def extraer_estado_de_pedido(p: Any) -> Optional[str]:
    if not p:
        return None
    if isinstance(p, dict):
        return (p.get("estado") or p.get("estado_pedido") or p.get("status") or "").upper()
    return (getattr(p, "estado", None) or getattr(p, "status", None) or "").upper()

def calcular_tiempo_espera_segundos_raw() -> Tuple[int, int]:
    pedidos = obtener_lista_pedidos_robusta()
    if not pedidos:
        return 0, 0
    relevantes = []
    for p in pedidos:
        estado = extraer_estado_de_pedido(p) or ""
        if estado and any(e in estado for e in ESTADOS_CALCULABLES):
            relevantes.append(p)
    if not relevantes:
        return 0, 0
    total = 0
    for p in relevantes:
        tipo = extraer_tipo_de_pedido(p)
        tm_min = get_tiempo_min_por_tipo(tipo)
        total += int(tm_min * 60)
    return total, len(relevantes)

# ---------- pantalla_preparar (única, combinada) ----------
async def pantalla_preparar(page: ft.Page, pedido: Dict[str, Any], mostrar_pantalla, pedido_finalizado_ref: Optional[List[Any]] = None, current_order_ref: Optional[List[Any]] = None):
    """
    Pantalla de preparación / horno / empaque.
    - pedido: dict con al menos 'orden' (puede ser parcial).
    - mostrar_pantalla: función router.
    - pedido_finalizado_ref/current_order_ref: referencias tipo [value] para comunicar estado externo.
    """
    page.bgcolor = CREMA
    page.scroll = ft.ScrollMode.AUTO
    page.clean()

    # obtener pedido completo si es posible
    numero_orden = pedido.get("orden")
    try:
        pedido_full = obtener_pedido(numero_orden) if numero_orden is not None else pedido or {}
    except Exception:
        pedido_full = pedido or {}

    if not pedido_full:
        pedido_full = pedido or {}

    cliente = pedido_full.get("cliente") or pedido_full.get("nombre") or "—"
    tipo_pizza = (pedido_full.get("receta_tipo") or pedido_full.get("tipo_pizza") or pedido_full.get("tipo") or "Genérica")
    tamanio = pedido_full.get("tamano") or pedido_full.get("tamano_pizza") or "Individual"

    # responsive helper
    def bp():
        w = page.width or 1280
        return "xs" if w < 900 else ("md" if w < 1280 else "lg"), w

    state = {
        "img_size": 340,
        "title_size": 28,
        "status_size": 20,
        "phase_size": 16,
        "box_w": 560,
        "pad": 18,
        "btn_w": 120,
        "btn_h": 34,
        "info_size": 14,
    }

    def recompute_sizes():
        size, w = bp()
        if size == "lg":
            state.update(img_size=420, title_size=30, status_size=22, phase_size=18, box_w=640, pad=20)
        elif size == "md":
            state.update(img_size=340, title_size=28, status_size=20, phase_size=16, box_w=560, pad=18)
        else:
            state.update(img_size=260, title_size=22, status_size=18, phase_size=14, box_w=min(420, int((w or 420)*0.92)), pad=12)

    recompute_sizes()

    # UI: imagen, titulos, fases, progreso
    image_control = ft.Image(src="pizza_loading.gif", width=state["img_size"], height=state["img_size"], fit=ft.ImageFit.CONTAIN, gapless_playback=True)
    titulo = ft.Text("BarkaLove Pizza", size=state["title_size"], color=ROJO, weight=ft.FontWeight.BOLD)
    txt_estado = ft.Text("Preparando tu pedido", size=state["status_size"], color=ROJO, weight=ft.FontWeight.BOLD)

    # fases: (nombre, descripción)
    phases = [("Preparación", "Preparando ingredientes"), ("Horno", "Cociendo en horno"), ("Empaque", "Empaque y entrega")]
    fase_actual = ft.Text(f"Fase: {phases[0][0]}", size=state["phase_size"], color=NEGRO, weight=ft.FontWeight.W_700)

    progreso_bar = ft.ProgressBar(value=0, color=AMARILLO, bgcolor=GRIS, width=state["box_w"])

    alerta_banner = ft.Text("", size=14, color=ROJO, weight=ft.FontWeight.W_700, text_align=ft.TextAlign.CENTER)

    # audio beep (si existe)
    try:
        beep = ft.Audio(src="beep.wav", autoplay=False)
        page.overlay.append(beep)
    except Exception:
        beep = None

    def play_beep():
        try:
            if beep:
                beep.play()
        except Exception:
            pass

    # botones
    def on_modificar(_):
        if current_order_ref and current_order_ref[0]:
            mostrar_pantalla("modificar", id_orden=current_order_ref[0])
        elif numero_orden is not None:
            mostrar_pantalla("modificar", id_orden=numero_orden)

    btn_modificar = ft.ElevatedButton("Modificar", bgcolor=AMARILLO, color=NEGRO, width=state["btn_w"], height=state["btn_h"], on_click=on_modificar)

    def on_ver_orden(_):
        if numero_orden is not None:
            mostrar_pantalla("ver_orden", numero_orden=numero_orden)

    btn_ver_orden = ft.ElevatedButton("Ver orden", bgcolor=AZUL, color="white", width=state["btn_w"], height=state["btn_h"], on_click=on_ver_orden, visible=False)

    def on_salir(_):
        mostrar_pantalla("inicio")

    btn_salir = ft.ElevatedButton("Salir", bgcolor=ROJO, color="white", width=state["btn_w"], height=state["btn_h"], on_click=on_salir, visible=False)

    info_min = ft.Text(f"Cliente: {cliente}   •   Orden: #{numero_orden if numero_orden is not None else '—'}   •   Tipo: {tipo_pizza}",
                       size=state["info_size"], color=NEGRO, text_align=ft.TextAlign.CENTER)

    # telemetría
    txt_temp = ft.Text("Temp: — °C", size=14, color=NEGRO)
    txt_time = ft.Text("Tiempo: — s", size=14, color=NEGRO)
    telemetria = ft.Row([txt_temp, txt_time], alignment=ft.MainAxisAlignment.CENTER, spacing=14)

    # tiempo estimado
    tiempo_est_text = ft.Text("Tiempo estimado: --:--", size=16, color=NEGRO, weight=ft.FontWeight.W_700)
    tiempo_detalle_text = ft.Text("Pedidos activos: --", size=12, color=NEGRO)
    tiempo_progress = ft.ProgressBar(value=0, color=ROJO, bgcolor=GRIS, width=min(state["box_w"], 360))

    tiempo_box = ft.Column([tiempo_est_text, tiempo_progress, tiempo_detalle_text], tight=True, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6)

    layout = ft.Column(
        [
            titulo,
            txt_estado,
            alerta_banner,
            image_control,
            fase_actual,
            telemetria,
            progreso_bar,
            ft.Row([tiempo_box], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([btn_ver_orden, btn_salir], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
            ft.Container(height=8),
            ft.Row([btn_modificar], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=8),
            info_min,
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10,
    )

    root = ft.Container(content=layout, alignment=ft.alignment.center, expand=True, padding=state["pad"], bgcolor=CREMA)
    page.add(root)
    page.update()

    # ---- loop que calcula tiempos y pedidos activos (con smoothing) ----
    last_nonzero_seconds = None
    zero_streak = 0
    last_displayed_seconds = -1

    ui_lock = asyncio.Lock()
    stop_actualizar = False
    horno_terminado_para_orden = False

    async def actualizar_loop():
        nonlocal last_nonzero_seconds, zero_streak, last_displayed_seconds, stop_actualizar, horno_terminado_para_orden
        try:
            while not stop_actualizar:
                async with ui_lock:
                    if horno_terminado_para_orden:
                        tiempo_est_text.value = "En breve estará lista tu orden!"
                        tiempo_progress.value = 1.0
                        tiempo_detalle_text.value = ""
                        page.update()
                        await asyncio.sleep(1)
                        continue

                    segs, count = calcular_tiempo_espera_segundos_raw()

                    if segs > 0:
                        last_nonzero_seconds = segs
                        zero_streak = 0
                        display = segs
                    else:
                        if last_nonzero_seconds is None:
                            display = 0
                        else:
                            zero_streak += 1
                            if zero_streak >= ZERO_DEBOUNCE_CYCLES:
                                display = 0
                                last_nonzero_seconds = None
                                zero_streak = 0
                            else:
                                display = last_nonzero_seconds

                    if display != last_displayed_seconds:
                        tiempo_est_text.value = f"Tiempo estimado: {segundos_a_mmss(display)}"
                        ratio = min(1.0, display / (TIME_REF_MIN * 60)) if (TIME_REF_MIN * 60) > 0 else 0
                        tiempo_progress.value = ratio
                        tiempo_detalle_text.value = f"Pedidos activos: {count}"
                        page.update()
                        last_displayed_seconds = display
                    else:
                        if tiempo_detalle_text.value != f"Pedidos activos: {count}":
                            tiempo_detalle_text.value = f"Pedidos activos: {count}"
                            page.update()
                await asyncio.sleep(UPDATE_INTERVAL_S)
        except asyncio.CancelledError:
            return

    actualizar_task = asyncio.create_task(actualizar_loop())

    # ---- fases y cocción ----
    TOTAL_PREP_SECONDS = 60
    phase_duration = TOTAL_PREP_SECONDS / 3

    async def run_fases():
        nonlocal horno_terminado_para_orden, stop_actualizar
        for i, (name, desc) in enumerate(phases):
            # UI update fase
            fase_actual.value = f"{name}"
            progreso_bar.value = (i + 1) / len(phases)
            btn_modificar.visible = (i == 0)
            page.update()

            # actualizar estado en KDS (si falla, lo ignoramos)
            try:
                actualizar_estado(numero_orden, name)
            except Exception:
                pass

            if name == "Horno":
                alerta_banner.value = ""
                page.update()

                def on_update_sensor(s: SensorState):
                    async def _u():
                        async with ui_lock:
                            txt_temp.value = f"Temp: {s.temp_actual:.1f} °C"
                            txt_time.value = f"Tiempo: {int(s.tiempo_transcurrido)} s"
                            try:
                                receta_tm_min = get_tiempo_min_por_tipo(tipo_pizza)
                                tm_seg = int(receta_tm_min * 60)
                                restante = tm_seg - int(s.tiempo_transcurrido)
                                if restante < 0:
                                    restante = 0
                                tiempo_est_text.value = f"Tiempo estimado: {segundos_a_mmss(restante)}"
                                ratio = 1.0 - (restante / tm_seg) if tm_seg > 0 else 1.0
                                tiempo_progress.value = max(0.0, min(1.0, ratio))
                                page.update()
                            except Exception:
                                pass
                    try:
                        asyncio.create_task(_u())
                    except Exception:
                        pass

                await ejecutar_coccion_para_pedido(
                    id_pedido=numero_orden or -1,
                    tipo_pizza=tipo_pizza,
                    tamanio=tamanio,
                    duracion_seg=None,
                    on_update=on_update_sensor,
                    on_alerta_visual=lambda m: (setattr(alerta_banner, "value", m) or page.update()),
                    on_alerta_sonora=lambda: play_beep(),
                )

                # horno terminado: breve espera visual
                horno_terminado_para_orden = True
                await asyncio.sleep(phase_duration)
            else:
                await asyncio.sleep(phase_duration)

        # final UI
        fase_actual.value = "Finalizada"
        progreso_bar.value = 1
        image_control.src = "pizza_lista.png"
        txt_estado.value = "Pedido listo"
        txt_estado.color = VERDE
        btn_modificar.visible = False
        btn_ver_orden.visible = True
        btn_salir.visible = True
        page.update()

        try:
            actualizar_estado(numero_orden, "Listo")
        except Exception:
            pass

        if pedido_finalizado_ref is not None:
            pedido_finalizado_ref[0] = True
        if current_order_ref is not None:
            current_order_ref[0] = numero_orden

        # detener updater
        stop_actualizar = True
        await asyncio.sleep(0.1)
        if not actualizar_task.done():
            actualizar_task.cancel()

    # ejecutar fases
    await run_fases()

    # resize handler
    def on_resize(e):
        recompute_sizes()
        image_control.width = state["img_size"]
        image_control.height = state["img_size"]
        progreso_bar.width = state["box_w"]
        tiempo_progress.width = min(360, state["box_w"])
        page.update()

    page.on_resize = on_resize

# wrapper compatible (sincrónico/asincrónico)
def mostrar_carga_pizza(page: ft.Page, numero_orden: int, mostrar_pantalla, pedido_finalizado_ref: Optional[List[Any]] = None, current_order_ref: Optional[List[Any]] = None):
    pedido = {"orden": numero_orden}
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        asyncio.run(pantalla_preparar(page, pedido, mostrar_pantalla, pedido_finalizado_ref, current_order_ref))
    else:
        asyncio.create_task(pantalla_preparar(page, pedido, mostrar_pantalla, pedido_finalizado_ref, current_order_ref))
