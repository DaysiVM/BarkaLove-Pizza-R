# utils/pedidos.py
import json
import os
from datetime import datetime
from typing import Any, Dict, List
from . import inventario as inv

ARCHIVO = "data/pedidos.json"


def cargar_pedidos() -> List[Dict[str, Any]]:
    if os.path.exists(ARCHIVO):
        with open(ARCHIVO, "r", encoding="utf-8") as f:
            txt = f.read().strip()
            if not txt:
                return []
            try:
                return json.loads(txt)
            except json.JSONDecodeError:
                return []
    return []


# utils/pedidos.py (solo reemplaza la función guardar_pedido existente)

def guardar_pedido(pedido: Dict[str, Any]) -> List[str]:
    """
    Valida inventario y descuenta insumos.
    - Si no hay stock suficiente -> lanza ValueError con detalle.
    - Si se guarda correctamente -> retorna lista de ingredientes que llegaron <= stock_minimo (alertas).
    Se añaden prints para ayudar a debug en caso de fallo.
    """
    os.makedirs("data", exist_ok=True)

    try:
        # verificar y descontar inventario -> inv.verificar_y_descontar devuelve (ok, info)
        ok, info = inv.verificar_y_descontar(pedido)
    except Exception as ex:
        # log/print extra para debugging: si esta excepción ocurre, el click en UI puede parecer "inmóvil"
        print(f"[DEBUG guardar_pedido] Error verificando inventario: {ex}")
        raise

    if not ok:
        # info en este caso es la lista de faltantes
        msg = "Stock insuficiente: " + "; ".join(info)
        print(f"[DEBUG guardar_pedido] {msg}")
        raise ValueError(msg)

    # si ok -> info contiene alertas (ingredientes que quedaron en o por debajo del mínimo)
    alertas = info if isinstance(info, list) else []

    pedidos = cargar_pedidos()
    # asegurarse de timestamp/hora
    if "hora" not in pedido or not pedido.get("hora"):
        pedido["hora"] = datetime.now().isoformat(timespec='seconds')

    pedidos.append(pedido)
    try:
        with open(ARCHIVO, "w", encoding="utf-8") as f:
            json.dump(pedidos, f, indent=4, ensure_ascii=False)
    except Exception as ex:
        print(f"[DEBUG guardar_pedido] Error escribiendo {ARCHIVO}: {ex}")
        raise

    print(f"[DEBUG guardar_pedido] Pedido {pedido.get('orden')} guardado. Alertas: {alertas}")
    return alertas

def actualizar_pedido(pedido: Dict[str, Any]):
    os.makedirs("data", exist_ok=True)
    pedidos = cargar_pedidos()
    for i, p in enumerate(pedidos):
        if p.get("orden") == pedido.get("orden"):
            if "hora" not in pedido:
                pedido["hora"] = p.get("hora")
            pedidos[i] = pedido
            with open(ARCHIVO, "w", encoding="utf-8") as f:
                json.dump(pedidos, f, indent=4, ensure_ascii=False)
            return
    raise ValueError(f"Pedido con orden {pedido.get('orden')} no encontrado")


def obtener_pedido(orden):
    pedidos = cargar_pedidos()
    for p in pedidos:
        if p.get("orden") == orden:
            return p
    return None


def pedidos_modificables(minutos=5):
    from datetime import timedelta
    pedidos = cargar_pedidos()
    now = datetime.now()
    return [p for p in pedidos if now - datetime.fromisoformat(p["hora"]) < timedelta(minutes=minutos)]
