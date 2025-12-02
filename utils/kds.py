# utils/kds.py
import json
import os
from datetime import datetime
from typing import Dict, Any, List

BASE_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE_DIR, "pedidos_data.json")


def _load_data() -> List[Dict[str, Any]]:
    if not os.path.exists(DATA_PATH):
        return []
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _save_data(data: List[Dict[str, Any]]):
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def registrar_pedido(pedido: Dict[str, Any]) -> None:
    data = _load_data()
    pedido["fecha"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data.append(pedido)
    _save_data(data)


def listar_pedidos(estado: str = None) -> List[Dict[str, Any]]:
    data = _load_data()
    if estado:
        return [p for p in data if p.get("estado") == estado]
    return data


def actualizar_estado(id_pedido: int, nuevo_estado: str) -> bool:
    data = _load_data()
    for p in data:
        if p.get("id") == id_pedido:
            p["estado"] = nuevo_estado
            _save_data(data)
            return True
    return False
