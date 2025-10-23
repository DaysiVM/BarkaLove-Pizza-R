# screens/admin_recetas.py
from __future__ import annotations
import flet as ft
from datetime import datetime
import utils.recetas as rx  # requiere utils/recetas.py

# Paleta
ROJO = "#E63946"
AMARILLO = "#FFD93D"
CREMA = "#FFF8E7"
NEGRO = "#1F1F1F"
BLANCO = "#FFFFFF"
VERDE = "#2A9D8F"

# Componentes base + ingredientes del registro
# (Un solo campo por elemento con formato "gramos±tolerancia", ej.: "120±5")
ING_NAMES = [
    "Masa",          # gramos de masa por pizza
    "Salsa",         # gramos de salsa por pizza
    "Queso extra",
    "Pepperoni",
    "Champiñones",
    "Aceitunas",
    "Pimientos",
    "Jamón",
    "Piña",
]


def pantalla_admin_recetas(page: ft.Page, mostrar_pantalla):
    # ---- Guard: requiere sesión admin ----
    if page.session.get("admin_auth") is not True:
        page.snack_bar = ft.SnackBar(ft.Text("Necesitas iniciar sesión de admin.", color="white"), bgcolor=ROJO)
        page.snack_bar.open = True
        page.update()
        mostrar_pantalla("admin_login")
        return

    page.bgcolor = CREMA
    page.clean()

    # -------- Helpers --------
    def snack(msg: str, bg: str = ROJO):
        page.snack_bar = ft.SnackBar(ft.Text(msg, color="white"), bgcolor=bg)
        page.snack_bar.open = True
        page.update()

    def ok(msg: str):
        snack(msg, VERDE)

    def parse_pm(value: str) -> tuple[int, int]:
        """
        Parsea 'n±m' -> (n, m). Acepta 'n' (toma ±0) y espacios.
        Ej: '120±5' -> (120,5); '80' -> (80,0)
        """
        s = (value or "").replace(" ", "")
        if not s:
            return 0, 0
        if "±" in s:
            n, m = s.split("±", 1)
            return int(n or 0), int(m or 0)
        return int(s), 0

    def parse_date(s: str) -> datetime | None:
        s = (s or "").strip()
        if not s:
            return None
        try:
            # admite 'YYYY-MM-DD' o ISO completo
            return datetime.fromisoformat(s)
        except Exception:
            return None

    # -------- Header --------
    titulo = ft.Text("Recetas estandarizadas", size=24, color=NEGRO, weight=ft.FontWeight.BOLD)
    btn_volver = ft.ElevatedButton(
        "⬅ Volver",
        bgcolor=ROJO, color="white", height=36,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        on_click=lambda _: mostrar_pantalla("admin"),
    )
    header = ft.Row([titulo, ft.Container(expand=True), btn_volver],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    # -------- Tipos (selector + alta) --------
    tipos = rx.listar_tipos()
    tipo_dd = ft.Dropdown(
        label="Tipo de pizza",
        width=240,
        options=[ft.dropdown.Option(t) for t in tipos],
        value=(tipos[0] if tipos else None),
        color=NEGRO, text_size=16
    )
    nuevo_tipo = ft.TextField(
        label="Nuevo tipo",
        hint_text="Ej. Pepperoni",
        width=220,
        color=NEGRO, text_size=16
    )

    def crear_tipo(_):
        t = (nuevo_tipo.value or "").strip()
        if not t:
            snack("Escribe un nombre para el nuevo tipo."); return
        if t in rx.listar_tipos():
            snack("Ese tipo ya existe."); return
        # Creamos versión inicial activa con todos los elementos a 0±0
        rx.nueva_version(
            tipo_pizza=t,
            version_id="v1.0.0",
            autor=page.session.get("admin_user") or "admin",
            notas="Versión inicial",
            ingredientes={name: {"gramos": 0, "tol": 0} for name in ING_NAMES},
            horno={"temp_c": 280, "tiempo_min": 12, "tol": {"temp": 5, "tiempo": 1}},
            activar=True,
        )
        tipo_dd.options = [ft.dropdown.Option(x) for x in rx.listar_tipos()]
        tipo_dd.value = t
        page.update()
        ok(f"Tipo '{t}' creado y activado (v1.0.0).")
        refresh_versions()

    btn_crear_tipo = ft.ElevatedButton("Crear tipo", bgcolor=AMARILLO, color=NEGRO, height=40, on_click=crear_tipo)

    top_tipo = ft.Container(
        bgcolor=BLANCO, border_radius=12, padding=12,
        content=ft.Row([tipo_dd, nuevo_tipo, btn_crear_tipo], spacing=12, wrap=True)
    )

    # -------- Filtros --------
    filtro_version = ft.TextField(
        label="Versión",
        hint_text="Ej. v1.1.0",
        width=140, color=NEGRO, text_size=16
    )
    filtro_desde = ft.TextField(
        label="Desde",
        hint_text="YYYY-MM-DD",
        width=150, color=NEGRO, text_size=16
    )
    filtro_hasta = ft.TextField(
        label="Hasta",
        hint_text="YYYY-MM-DD",
        width=150, color=NEGRO, text_size=16
    )
    chk_solo_vigente = ft.Checkbox(label="Solo vigente", value=False, label_style=ft.TextStyle(color=NEGRO))

    def limpiar_filtros(_):
        filtro_version.value = ""
        filtro_desde.value = ""
        filtro_hasta.value = ""
        chk_solo_vigente.value = False
        page.update()
        refresh_versions()

    btn_limpiar = ft.ElevatedButton("Limpiar", bgcolor=AMARILLO, color=NEGRO, height=36, on_click=limpiar_filtros)

    filtros = ft.Container(
        bgcolor=BLANCO, border_radius=12, padding=12,
        content=ft.Row(
            [filtro_version, filtro_desde, filtro_hasta, chk_solo_vigente, btn_limpiar],
            spacing=12, wrap=True
        )
    )

    # -------- Panel izquierdo: historial --------
    vigente_lbl = ft.Text("", size=14, color=NEGRO)
    lista_versions = ft.ListView(expand=True, spacing=8, padding=0, auto_scroll=False)

    izquierda = ft.Column(
        [
            ft.Text("Historial de versiones", size=18, color=NEGRO, weight=ft.FontWeight.W_600),
            vigente_lbl,
            ft.Container(lista_versions, height=440, bgcolor=BLANCO, border_radius=12, padding=10),
        ],
        spacing=8,
        expand=True
    )

    # -------- Panel derecho: detalle + crear versión --------
    detalle_card = ft.Container(
        bgcolor=BLANCO, border_radius=12, padding=12,
        content=ft.Column([], spacing=6)
    )

    ver_id = ft.TextField(label="ID versión", hint_text="Ej. v1.1.0", width=140, color=NEGRO, text_size=16)
    autor = ft.TextField(label="Autor", hint_text="Ej. admin", width=140, color=NEGRO, text_size=16,
                         value=page.session.get("admin_user") or "admin")
    notas = ft.TextField(label="Notas", hint_text="Ej. Ajuste de queso", width=300, color=NEGRO, text_size=16)

    # Un solo campo por elemento: "gramos±tolerancia"
    ing_inputs: dict[str, ft.TextField] = {}
    ing_rows: list[ft.Control] = []
    for name in ING_NAMES:
        tf = ft.TextField(
            label=name, hint_text="Ej. 120±5", width=180, color=NEGRO, text_size=16
        )
        ing_inputs[name] = tf
        ing_rows.append(tf)

    horno_temp = ft.TextField(label="Horno °C", hint_text="Ej. 280±5", width=160, color=NEGRO, text_size=16)
    horno_time = ft.TextField(label="Tiempo (min)", hint_text="Ej. 12±1", width=160, color=NEGRO, text_size=16)

    def render_detalle(version: rx.RecetaVersion):
        ings = version.ingredientes or {}
        horno = version.horno or {}
        det = ft.Column(
            [
                ft.Text(f"Detalle — {version.version_id}", size=18, color=NEGRO, weight=ft.FontWeight.W_600),
                ft.Text(f"Fecha: {version.fecha}", size=14, color=NEGRO),
                ft.Text(f"Autor: {version.autor}", size=14, color=NEGRO),
                ft.Text(f"Notas: {version.notas or '—'}", size=14, color=NEGRO),
                ft.Divider(),
                ft.Text("Ingredientes (g ± tolerancia)", size=16, color=NEGRO, weight=ft.FontWeight.W_600),
                ft.Column(
                    [ft.Text(f"• {k}: {v.get('gramos',0)} ± {v.get('tol',0)} g", size=14, color=NEGRO)
                     for k, v in ings.items()],
                    spacing=2
                ),
                ft.Divider(),
                ft.Text("Horno", size=16, color=NEGRO, weight=ft.FontWeight.W_600),
                ft.Text(
                    f"Temperatura: {horno.get('temp_c','—')} ± {(horno.get('tol') or {}).get('temp',0)} °C",
                    size=14, color=NEGRO),
                ft.Text(
                    f"Tiempo: {horno.get('tiempo_min','—')} ± {(horno.get('tol') or {}).get('tiempo',0)} min",
                    size=14, color=NEGRO),
            ],
            spacing=4
        )
        detalle_card.content = det
        page.update()

    def activar_version(tipo: str, version_id: str):
        ok_flag = rx.activar_version(tipo, version_id)
        ok("Versión activada." if ok_flag else "No se pudo activar la versión.")
        refresh_versions()

    def refresh_versions():
        lista_versions.controls.clear()
        t = tipo_dd.value
        if not t:
            vigente_lbl.value = "Versión activa: —"
            page.update()
            return

        vvig = rx.vigente(t)
        vigente_lbl.value = f"Versión activa: {vvig.version_id if vvig else '—'}"

        data = rx.historial(t)

        # aplicar filtros
        f_ver = (filtro_version.value or "").strip().lower()
        d_from = parse_date(filtro_desde.value)
        d_to = parse_date(filtro_hasta.value)
        only_active = chk_solo_vigente.value

        filtered = []
        for v in data:
            if f_ver and f_ver not in (v.version_id or "").lower():
                continue
            try:
                vf = datetime.fromisoformat(v.fecha)
            except Exception:
                vf = None
            if d_from and (vf is None or vf < d_from):
                continue
            if d_to and (vf is None or vf > d_to):
                continue
            if only_active and not v.activo:
                continue
            filtered.append(v)

        if not filtered:
            lista_versions.controls.append(ft.Text("Sin versiones para los filtros aplicados.", size=14, color=NEGRO))
        else:
            # Orden por fecha ASC
            filtered.sort(key=lambda vv: vv.fecha or "")
            for v in filtered:
                es_vig = v.activo is True
                estado_txt = "Vigente ✅" if es_vig else "Histórica"
                fila = ft.Container(
                    bgcolor=BLANCO, border_radius=12, padding=10,
                    content=ft.Row(
                        [
                            ft.Column([
                                ft.Text(v.version_id, size=16, color=NEGRO, weight=ft.FontWeight.W_600),
                                ft.Text(v.fecha, size=14, color=NEGRO),
                                ft.Text(f"Autor: {v.autor}", size=14, color=NEGRO),
                            ], spacing=2, expand=True),
                            ft.Text(estado_txt, size=14, color=NEGRO),
                            ft.TextButton("Ver", on_click=lambda _, data=v: render_detalle(data),
                                          style=ft.ButtonStyle(color={"": NEGRO})),
                            ft.ElevatedButton(
                                "Activar",
                                bgcolor=AMARILLO, color=NEGRO, height=36,
                                on_click=lambda _, typ=t, ver=v.version_id: activar_version(typ, ver),
                                disabled=es_vig,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                )
                lista_versions.controls.append(fila)
        page.update()

    def crear_version(_):
        t = tipo_dd.value
        if not t:
            snack("Selecciona o crea un tipo primero."); return
        if not ver_id.value:
            snack("Ingresa el ID de versión (p. ej., v1.1.0)."); return

        # Construir ingredientes desde inputs "n±m"
        ings: dict[str, dict] = {}
        try:
            for name in ING_NAMES:
                n, m = parse_pm(ing_inputs[name].value)
                ings[name] = {"gramos": n, "tol": m}
            # horno
            temp, temp_tol = parse_pm(horno_temp.value)
            tmn, tmn_tol = parse_pm(horno_time.value)
        except Exception:
            snack("Revisa los campos: usa el formato Ej. 120±5 (números enteros)."); return

        horno = {"temp_c": temp, "tiempo_min": tmn, "tol": {"temp": temp_tol, "tiempo": tmn_tol}}

        rx.nueva_version(
            tipo_pizza=t,
            version_id=ver_id.value.strip(),
            autor=(autor.value or "admin").strip(),
            notas=(notas.value or "").strip(),
            ingredientes=ings,
            horno=horno,
            activar=False,
        )
        ok("Versión creada. Puedes activarla cuando lo desees.")
        # limpiar inputs suaves
        ver_id.value = ""
        notas.value = ""
        page.update()
        refresh_versions()

    crear_version_card = ft.Container(
        bgcolor=BLANCO, border_radius=12, padding=12,
        content=ft.Column(
            [
                ft.Text("Crear nueva versión", size=18, color=NEGRO, weight=ft.FontWeight.W_600),
                ft.Row([ver_id, autor, notas], spacing=12, wrap=True),
                ft.Text("Ingredientes (usa formato: gramos±tolerancia)", size=16, color=NEGRO, weight=ft.FontWeight.W_600),
                ft.Row(ing_rows, spacing=12, run_spacing=8, wrap=True),
                ft.Text("Parámetros de horno", size=16, color=NEGRO, weight=ft.FontWeight.W_600),
                ft.Row([horno_temp, horno_time], spacing=12, wrap=True),
                ft.Container(
                    content=ft.Text(
                        "",
                        size=13, color=NEGRO
                    ),
                    padding=ft.padding.only(top=6, bottom=6),
                ),
                ft.Row(
                    [ft.Container(expand=True),
                     ft.ElevatedButton("Crear versión", bgcolor=AMARILLO, color=NEGRO, height=44, on_click=crear_version)],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
            ],
            spacing=10
        )
    )

    derecha = ft.Column(
        [
            ft.Text("Detalle de versión", size=18, color=NEGRO, weight=ft.FontWeight.W_600),
            detalle_card,
            ft.Container(height=8),
            crear_version_card,
        ],
        spacing=8,
        expand=True
    )

    grid = ft.ResponsiveRow(
        controls=[
            ft.Container(izquierda, col={"xs": 12, "md": 6, "lg": 6}),
            ft.Container(derecha,   col={"xs": 12, "md": 6, "lg": 6}),
        ],
        columns=12, spacing=12, run_spacing=12
    )

    root = ft.Container(
        content=ft.Column([header, ft.Divider(color=NEGRO), top_tipo, filtros, grid], spacing=12),
        padding=16, bgcolor=CREMA, expand=True
    )
    page.add(root)
    page.update()

    # primer render + listeners
    refresh_versions()
    tipo_dd.on_change = lambda _: refresh_versions()
    filtro_version.on_change = lambda _: refresh_versions()
    filtro_desde.on_change = lambda _: refresh_versions()
    filtro_hasta.on_change = lambda _: refresh_versions()
    chk_solo_vigente.on_change = lambda _: refresh_versions()

    return root
