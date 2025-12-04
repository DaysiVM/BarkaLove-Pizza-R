# scripts/init_inventory.py
"""
Inicializador del inventario (data/inventario.json).

Uso:
  python scripts/init_inventory.py          # Sobrescribe/crea inventario con defaults
  python scripts/init_inventory.py --no-overwrite  # No sobrescribe si ya existe
"""

import os
import json
import sys

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "inventario.json")

# Ingredientes por defecto con cantidades razonables y unidades
DEFAULTS = [
    {"ingrediente": "Masa",           "cantidad_actual": 50, "stock_minimo": 5,  "unidad": "unidades"},
    {"ingrediente": "Salsa",          "cantidad_actual": 40, "stock_minimo": 5,  "unidad": "porciones"},
    {"ingrediente": "Queso",          "cantidad_actual": 60, "stock_minimo": 8,  "unidad": "porciones"},
    {"ingrediente": "Queso extra",    "cantidad_actual": 40, "stock_minimo": 5,  "unidad": "porciones"},
    {"ingrediente": "Pepperoni",      "cantidad_actual": 45, "stock_minimo": 6,  "unidad": "porciones"},
    {"ingrediente": "Piña",           "cantidad_actual": 30, "stock_minimo": 4,  "unidad": "porciones"},
    {"ingrediente": "Champiñones",    "cantidad_actual": 30, "stock_minimo": 4,  "unidad": "porciones"},
    {"ingrediente": "Aceitunas",      "cantidad_actual": 30, "stock_minimo": 4,  "unidad": "porciones"},
    {"ingrediente": "Pimientos",      "cantidad_actual": 30, "stock_minimo": 4,  "unidad": "porciones"},
    {"ingrediente": "Jamón",          "cantidad_actual": 40, "stock_minimo": 5,  "unidad": "porciones"},
    # puedes agregar más ingredientes si los usas en recetas
]

def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

def write_inventory(data, path=DATA_FILE):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_inventory(path=DATA_FILE):
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def main():
    ensure_data_dir()

    no_overwrite = "--no-overwrite" in sys.argv

    existing = load_inventory()
    if existing and no_overwrite:
        print(f"[init_inventory] El archivo '{DATA_FILE}' ya existe — no se sobrescribirá (--no-overwrite).")
        return

    write_inventory(DEFAULTS)
    print(f"[init_inventory] Inventario inicial escrito en '{DATA_FILE}' con {len(DEFAULTS)} ingredientes.")
    for it in DEFAULTS:
        print(f"  - {it['ingrediente']}: {it['cantidad_actual']} {it['unidad']} (mínimo {it['stock_minimo']})")

if __name__ == "__main__":
    main()
