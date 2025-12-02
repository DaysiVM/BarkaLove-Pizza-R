# screens/admin_login.py
from __future__ import annotations
import flet as ft

ROJO = "#E63946"
CREMA = "#FFF8E7"
NEGRO = "#1F1F1F"
AMARILLO = "#FFD93D"

USER_PRESET = "admin"
PASS_PRESET = "admin"


def pantalla_admin_login(page: ft.Page, mostrar_pantalla):
    page.bgcolor = CREMA
    page.scroll = ft.ScrollMode.AUTO
    page.clean()

    titulo = ft.Text("Acceso administrador", size=28, color=ROJO, weight=ft.FontWeight.BOLD)
    subt = ft.Text("Introduce tus credenciales", size=14, color=NEGRO)

    user_tf = ft.TextField(label="Usuario", width=280, color=NEGRO, text_size=16)
    pass_tf = ft.TextField(label="Contraseña", password=True, can_reveal_password=True,
                           width=280, color=NEGRO, text_size=16)

    msg_alert = ft.Text("", color=ROJO, size=14)

    def snack(msg: str, bg=ROJO):
        page.snack_bar = ft.SnackBar(ft.Text(msg, color="white"), bgcolor=bg)
        page.snack_bar.open = True
        page.update()

    def do_login(_):
        u = (user_tf.value or "").strip()
        p = (pass_tf.value or "").strip()
        if u == USER_PRESET and p == PASS_PRESET:
            # marca sesión admin
            page.session.set("admin_auth", True)
            page.session.set("admin_user", u)
            snack("Sesión iniciada", "#2A9D8F")
            mostrar_pantalla("admin")  # Ir al dashboard
        else:
            msg_alert.value = "Usuario o contraseña incorrectos."
            page.update()

    btn_login = ft.ElevatedButton(
        "Entrar",
        bgcolor=AMARILLO,
        color=NEGRO,
        width=280,
        height=44,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        on_click=do_login,
    )

    btn_cancel = ft.TextButton("Cancelar", on_click=lambda _: mostrar_pantalla("inicio"))

    card = ft.Container(
        bgcolor="white",
        border_radius=12,
        padding=20,
        width=360,
        content=ft.Column(
            [
                titulo,
                subt,
                ft.Divider(),
                user_tf,
                pass_tf,
                msg_alert,
                ft.Container(height=8),
                btn_login,
                btn_cancel,
            ],
            spacing=8,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

    root = ft.Container(
        content=ft.Column([card], alignment=ft.MainAxisAlignment.CENTER,
                          horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        expand=True,
        bgcolor=CREMA,
    )

    page.add(root)
    page.update()
    return root
