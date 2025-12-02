import flet as ft

ROJO = "#E63946"
CREMA = "#FFF8E7"
NEGRO = "#1F1F1F"
GRIS = "#9E9E9E"
AZUL = "#2196F3"


def pantalla_errores_kpi(page: ft.Page, mostrar_pantalla):
    page.bgcolor = CREMA

    header = ft.Row([
        ft.Text("Errores de KPI", size=24, color=AZUL, weight=ft.FontWeight.BOLD, expand=True),
        ft.ElevatedButton("Volver", bgcolor=AZUL, color="white", height=36, on_click=lambda e: mostrar_pantalla("admin_indicadores")),
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    # Tarjeta de alerta técnica (mantenimiento)
    alerta = ft.Container(
        content=ft.Column([
            ft.Text("Alerta: Mantenimiento programado - Amasadora #3", size=16, weight=ft.FontWeight.W_700, color=NEGRO),
            ft.Container(height=8),
            ft.Text(
                "Se requiere intervención técnica en la unidad amasadora designada como \"Amasadora #3\". Se detectaron anomalías en el acoplamiento de transmisión y variaciones intermitentes en la señal del encoder del motor servo, que producen oscilaciones de par durante el ciclo de amasado.",
                size=13,
                color=NEGRO
            ),
            ft.Container(height=8),
            ft.Text("Recomendaciones técnicas:", size=14, weight=ft.FontWeight.W_600, color=NEGRO),
            ft.Container(height=6),
            ft.Column([
                ft.Text("• Detener operación de la unidad y aislarla del suministro eléctrico.", color=NEGRO),
                ft.Text("• Inspeccionar rodamiento del eje principal y alojamientos por juego o fatiga (reemplazar si la holgura > 0.2 mm).", color=NEGRO),
                ft.Text("• Verificar acoplamiento flexible entre motor y reductor; sustituir acoplamientos deformados o desgastados.", color=NEGRO),
                ft.Text("• Comprobar encoder del servo y su cableado (test de continuidad y ruido); recalibrar o reemplazar si hay pérdida de señal intermitente.", color=NEGRO),
                ft.Text("• Ejecutar prueba de torque con sensor calibrado y comparar contra los parámetros nominales; recalibrar control de par si es necesario.", color=NEGRO),
                ft.Text("• Actualizar firmware del PLC/drive a la versión estable más reciente y aplicar parámetros operativos recomendados por el fabricante.", color=NEGRO),
            ], spacing=6),
            ft.Container(height=8),
            ft.Text("Impacto esperado:", size=14, weight=ft.FontWeight.W_600, color=NEGRO),
            ft.Text("Se estima una ventana de mantenimiento de 2-4 horas dependiendo de la disponibilidad de repuestos; prioridad: ALTA.", color=NEGRO),
        ], spacing=8),
        padding=16,
        bgcolor="white",
        border_radius=12,
        width="100%",
    )

    layout = ft.Column([header, ft.Divider(), alerta], spacing=12)
    root = ft.Container(layout, padding=16, bgcolor=CREMA, expand=True)
    return root
