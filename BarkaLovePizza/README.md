Barka Love Pizza

Aplicación ejemplo usando Flet para crear una UI de pedidos de pizza.

Requisitos:
- Python 3.10+
- Dependencias en `requirements.txt` (instalar con `pip install -r requirements.txt`)

Cómo ejecutar:

1. Abre PowerShell en la carpeta del proyecto (la que contiene `main`).
2. Instala dependencias:

```powershell
pip install -r requirements.txt
```

3. Ejecuta la app:

```powershell
python main
```

Notas:
- Si la app no abre, asegúrate de tener una versión compatible de Python y que `flet` esté instalada.
- Imágenes y assets deben estar en la carpeta `assets`.

GIF de carga (opcional):

Si quieres mostrar una animación GIF mientras la pizza se prepara, descarga un GIF y ponlo en:

```
assets/pizza_loading.gif
```

La pantalla de preparación usará ese GIF automáticamente si el archivo existe. Si no lo colocas, la pantalla usa una secuencia de imágenes (pizza_1.png ... pizza_5.png) como fallback.
