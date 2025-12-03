import flet as ft
import os
import webbrowser


def pantalla_documentacion_tecnica(page: ft.Page, mostrar_pantalla):
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

	# === Ruta REAL de la carpeta de documentación técnica ===
	base_dir = os.path.dirname(os.path.abspath(__file__))
	doc_dir = os.path.join(base_dir, "..", "data", "documentacion")
	doc_dir = os.path.abspath(doc_dir)

	os.makedirs(doc_dir, exist_ok=True)

	# === Función abrir PDF ===
	def abrir_pdf(ruta):
		ruta_normalizada = ruta.replace("\\", "/")
		url = f"file:///{ruta_normalizada}"
		webbrowser.open(url)

	# === Listado de PDFs ===
	items = []
	for fn in sorted(os.listdir(doc_dir)):
		if fn.lower().endswith(".pdf"):
			ruta_pdf = os.path.join(doc_dir, fn)

			row = ft.Row(
				[
					ft.Text(fn, expand=True, size=16),
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
			ft.Text("Documentación técnica", size=24, weight=ft.FontWeight.BOLD),
			ft.ElevatedButton("Volver", on_click=lambda e: mostrar_pantalla("admin"))
		],
		alignment=ft.MainAxisAlignment.SPACE_BETWEEN
	)

	contenido = ft.Column([header, ft.Divider()] + items, spacing=10)
	return ft.Container(contenido, padding=20)

