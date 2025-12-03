import flet as ft
import webbrowser


def pantalla_videos_tutoriales(page: ft.Page, mostrar_pantalla):
    page.bgcolor = "#FFF8E7"
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
            "title": "BarkaLove Pizza  - Video tutorial para realizar pedido",
            "url": "https://youtube.com/shorts/8se_a3kwAWQ",
        },
    ]

    def abrir_video(url):
        webbrowser.open(url)

    items = []
    for v in videos:
        row = ft.Row(
            [
                ft.Text(v["title"], expand=True, size=16),
                ft.IconButton(icon=ft.Icons.PLAY_ARROW, tooltip="Abrir en YouTube", on_click=lambda e, u=v["url"]: abrir_video(u)),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        items.append(row)

    header = ft.Row(
        [
            ft.Text("Videos Tutoriales", size=24, weight=ft.FontWeight.BOLD),
            ft.ElevatedButton("Volver", on_click=lambda e: mostrar_pantalla("admin")),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    contenido = ft.Column([header, ft.Divider()] + items, spacing=10)
    return ft.Container(contenido, padding=20)
