import json, os
from datetime import datetime

ARCHIVO = "data/pedidos.json"

def guardar_pedido(pedido):
    os.makedirs("data", exist_ok=True)
    pedidos = cargar_pedidos()
    pedidos.append(pedido)
    with open(ARCHIVO, "w") as f:
        json.dump(pedidos, f, indent=4)

def cargar_pedidos():
    if os.path.exists(ARCHIVO):
        with open(ARCHIVO, "r") as f:
            return json.load(f)
    return []

def pedidos_modificables(minutos=5):
    from datetime import datetime, timedelta
    pedidos = cargar_pedidos()
    return [p for p in pedidos if datetime.now() - datetime.fromisoformat(p["hora"]) < timedelta(minutes=minutos)]
