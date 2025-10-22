import json, os
from datetime import datetime

ARCHIVO = "data/pedidos.json"

def guardar_pedido(pedido):
    os.makedirs("data", exist_ok=True)
    pedidos = cargar_pedidos()
    pedidos.append(pedido)
    # Escritura robusta y UTF-8
    with open(ARCHIVO, "w", encoding="utf-8") as f:
        json.dump(pedidos, f, indent=4, ensure_ascii=False)


def actualizar_pedido(pedido):
    """Actualiza un pedido existente que coincida por 'orden'.
    Si no existe, lanza ValueError.
    """
    os.makedirs("data", exist_ok=True)
    pedidos = cargar_pedidos()
    for i, p in enumerate(pedidos):
        if p.get('orden') == pedido.get('orden'):
            # conservar la hora original si no viene en el nuevo pedido
            if 'hora' not in pedido:
                pedido['hora'] = p.get('hora')
            pedidos[i] = pedido
            with open(ARCHIVO, "w") as f:
                json.dump(pedidos, f, indent=4)
            return
    raise ValueError(f"Pedido con orden {pedido.get('orden')} no encontrado")


def obtener_pedido(orden):
    """Devuelve el pedido con la orden dada o None si no existe."""
    pedidos = cargar_pedidos()
    for p in pedidos:
        if p.get('orden') == orden:
            return p
    return None

def cargar_pedidos():
    if os.path.exists(ARCHIVO):
        with open(ARCHIVO, "r", encoding="utf-8") as f:
            txt = f.read().strip()
            if not txt:
                # archivo existente pero vacío
                return []
            try:
                return json.loads(txt)
            except json.JSONDecodeError:
                # tolera JSON corrupto devolviendo lista vacía
                return []
    return []

def pedidos_modificables(minutos=5):
    from datetime import datetime, timedelta
    pedidos = cargar_pedidos()
    return [p for p in pedidos if datetime.now() - datetime.fromisoformat(p["hora"]) < timedelta(minutes=minutos)]
