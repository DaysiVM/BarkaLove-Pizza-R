import flet as ft
import os


def pantalla_admin_respaldo(page: ft.Page, mostrar_pantalla):
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

    def volver(_):
        mostrar_pantalla("admin")

    # Directorio de respaldos (crearlo si no existe)
    backups_dir = os.path.join(os.getcwd(), "data", "backups")
    os.makedirs(backups_dir, exist_ok=True)

    # Construir lista de items (placeholder: solo nombres de archivo)
    items = []
    for fn in sorted(os.listdir(backups_dir), reverse=True):
        row = ft.Row(
            [
                ft.Text(fn, expand=True),
                ft.IconButton(ft.icons.DOWNLOAD, tooltip="Descargar", on_click=lambda e, name=fn: mostrar_msg(page, f"Descargar {name}")),
                ft.IconButton(ft.icons.DELETE, tooltip="Eliminar", on_click=lambda e, name=fn: mostrar_msg(page, f"Eliminar {name}")),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        items.append(row)

    header = ft.Row(
        [
            ft.Text("Respaldo de datos", size=24, weight=ft.FontWeight.BOLD),
            ft.Row(
                [
                    ft.ElevatedButton("Volver", on_click=lambda e: mostrar_pantalla("admin"), height=40),
                ],
                spacing=8
            )
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )

    body = ft.Column([header, ft.Divider()] + items, spacing=8)
    root = ft.Container(body, padding=16)
    return root


def mostrar_msg(page: ft.Page, texto: str):
    page.snack_bar = ft.SnackBar(ft.Text(texto, color="white"), bgcolor="#2196F3")
    page.snack_bar.open = True
    page.update()
