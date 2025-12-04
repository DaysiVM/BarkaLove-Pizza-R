import flet as ft
import os
import webbrowser

def pantalla_manuales_usuario(page: ft.Page, mostrar_pantalla):
    page.bgcolor = "#FFF8E7"
    page.clean()

    # Seguridad solo admin
    is_admin = page.session.get("admin_auth") is True
    if not is_admin:
        page.snack_bar = ft.SnackBar(ft.Text("Necesitas sesión de admin.", color="white"), bgcolor="#E63946")
        page.snack_bar.open = True
        page.update()
        mostrar_pantalla("admin_login")
        return

    # === Ruta REAL de la carpeta manuales ===
    base_dir = os.path.dirname(os.path.abspath(__file__))       # carpeta actual del archivo .py
    manuales_dir = os.path.join(base_dir, "..", "data", "manuales")
    manuales_dir = os.path.abspath(manuales_dir)

    os.makedirs(manuales_dir, exist_ok=True)

    # === Función abrir PDF ===
    def abrir_pdf(ruta):
        ruta_normalizada = ruta.replace("\\", "/")
        url = f"file:///{ruta_normalizada}"
        webbrowser.open(url)

    # === Listado de PDFs ===
    items = []
    for fn in sorted(os.listdir(manuales_dir)):
        if fn.lower().endswith(".pdf"):
            ruta_pdf = os.path.join(manuales_dir, fn)

            row = ft.Row(
                [
                    ft.Text(fn, expand=True, size=16, color="#1F1F1F"),
                    ft.IconButton(
                        icon=ft.Icons.PICTURE_AS_PDF,
                        tooltip="Abrir PDF",
                        on_click=lambda e, r=ruta_pdf: abrir_pdf(r)
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            )
            items.append(row)

    # Header
    header = ft.Row(
        [
            ft.Text("Manuales de Usuario", size=24, weight=ft.FontWeight.BOLD, color="#1F1F1F"),
            ft.ElevatedButton("Volver", on_click=lambda e: mostrar_pantalla("admin"))
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )

    # Layout final
    contenido = ft.Column([header, ft.Divider()] + items, spacing=10)
    return ft.Container(contenido, padding=20)