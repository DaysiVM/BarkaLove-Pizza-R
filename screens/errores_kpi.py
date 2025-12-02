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

    # Descripciones adicionales de errores
    moldeadora = ft.Container(
        content=ft.Column([
            ft.Text("Alerta: Moldeadora #2 - Desalineación del transportador", size=15, weight=ft.FontWeight.W_700, color=NEGRO),
            ft.Container(height=6),
            ft.Text(
                "Se ha detectado un incremento en los rechazos dimensionales atribuibles a desalineación intermitente del transportador de entrada en la unidad Moldeadora #2. Se observan variaciones laterales de hasta 3 mm en el posicionamiento del molde durante el ciclo de carga, lo que afecta la geometría de la base.",
                size=13,
                color=NEGRO
            ),
            ft.Container(height=6),
            ft.Text("Acciones recomendadas: Realinear guías del transportador, verificar sensores de referencia de posición y ajustar la tensión de la correa motriz. Inspección visual de rodillos y sustitución si presentan desgaste.", size=13, color=NEGRO),
        ], spacing=8),
        padding=16,
        bgcolor="white",
        border_radius=12,
        width="100%",
    )

    empaquetado = ft.Container(
        content=ft.Column([
            ft.Text("Alerta: Línea de empaquetado - Sellado térmico intermitente", size=15, weight=ft.FontWeight.W_700, color=NEGRO),
            ft.Container(height=6),
            ft.Text(
                "Se han reportado fallos de sellado en la estación de empaquetado: sellos inconsistentes y bordes parcialmente adheridos. Los registros muestran fluctuaciones de temperatura en la resistencia de sellado y lecturas inconsistentes del sensor térmico.",
                size=13,
                color=NEGRO
            ),
            ft.Container(height=6),
            ft.Text("Acciones recomendadas: Limpiar cabezales de sellado, comprobar y recalibrar el sensor de temperatura, revisar la alimentación y los relés del circuito de potencia, y ajustar parámetros PID del controlador de temperatura.", size=13, color=NEGRO),
        ], spacing=8),
        padding=16,
        bgcolor="white",
        border_radius=12,
        width="100%",
    )

    layout = ft.Column([header, ft.Divider(), alerta, moldeadora, empaquetado], spacing=12)
    root = ft.Container(layout, padding=16, bgcolor=CREMA, expand=True)
    return root

