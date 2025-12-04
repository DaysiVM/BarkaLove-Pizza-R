# screens/videos_tutoriales.py
from __future__ import annotations
import flet as ft

def pantalla_videos_tutoriales(page: ft.Page, mostrar_pantalla):
    page.bgcolor = "#FFF8E7"
    page.scroll = ft.ScrollMode.AUTO
    page.clean()

    # Seguridad: solo admin
    is_admin = page.session.get("admin_auth") is True
    if not is_admin:
        page.snack_bar = ft.SnackBar(ft.Text("Necesitas sesión de admin.", color="white"), bgcolor="#E63946")
        page.snack_bar.open = True
        page.update()
        mostrar_pantalla("admin_login")
        return

    # Lista de videos (puedes añadir más aquí)
    videos = [
        {
            "title": "Canal: Barka-Love Pizza",
            "url": "https://www.youtube.com/@Barka-LovePizza",
        },
        {
            "title": "Barka-Love Pizza  - Video tutorial para realizar pedido",
            "url": "https://youtube.com/shorts/8se_a3kwAWQ",
        },
        {
            "title": "Barka-Love Pizza - Registro Panel de Administración",
            "url": "https://youtu.be/F8UR1ji7mng?si=M86Dki6V9YUatP4V",
        },
        {
            "title": "Barka-Love Pizza - Navegación en KDS (cocina)",
            "url": "https://youtu.be/U66sOAlSejQ?si=erKi16De3AIOKo2M",
        },
    ]

    def abrir_video(url: str):
        # use flet helper para abrir url (mejor integración)
        try:
            ft.launch_url(url)
        except Exception:
            # fallback: intentar con webbrowser si ft.launch_url falla
            try:
                import webbrowser
                webbrowser.open(url)
            except Exception:
                page.snack_bar = ft.SnackBar(ft.Text("No se pudo abrir el enlace.", color="white"), bgcolor="#E63946")
                page.snack_bar.open = True
                page.update()

    items = []
    for v in videos:
        row = ft.Row(
            [
                ft.Text(v["title"], expand=True, size=16, color="#E63946"),
                ft.IconButton(
                    icon=ft.Icons.PLAY_ARROW,
                    tooltip="Abrir en YouTube",
                    on_click=lambda e, u=v["url"]: abrir_video(u)
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        items.append(row)

    header = ft.Row(
        [
            ft.Text("Videos Tutoriales", size=24, weight=ft.FontWeight.BOLD, color="#E63946"),
            ft.ElevatedButton("Volver", on_click=lambda e: mostrar_pantalla("admin")),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    contenido = ft.Column([header, ft.Divider()] + items, spacing=10)

    cont = ft.Container(contenido, padding=20, expand=True, bgcolor="#FFF8E7")
    page.add(cont)
    page.update()
    return cont
