# utils/inventario.py
import os
import json
import unicodedata
from typing import List, Dict, Any, Optional, Tuple

# intentar integración con recetas (si existe)
try:
    from .recetas import vigente as receta_vigente
except Exception:
    receta_vigente = None

DATA_PATH = os.path.join("data", "inventario.json")


# -------------------- UTILIDADES --------------------

def _ensure_file():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump([], f)


def _load_raw() -> List[Dict[str, Any]]:
    _ensure_file()
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _save_raw(lista: List[Dict[str, Any]]):
    _ensure_file()
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(lista, f, indent=2, ensure_ascii=False)


def _normalize_text(s: str) -> str:
    """Lowercase, strip, remove accents and duplicate spaces."""
    if not s:
        return ""
    s2 = str(s).strip().lower()
    s2 = unicodedata.normalize("NFKD", s2)
    s2 = "".join(ch for ch in s2 if not unicodedata.combining(ch))
    s2 = " ".join(s2.split())
    return s2


# Diccionario de sinónimos: normalizado -> nombre canónico en inventario
# Añade o ajusta según tus recetas / UI.
_SYNONYMS: Dict[str, str] = {
    "queso extra": "queso",
    "queso": "queso",
    "masa": "Masa",
    "salsa": "Salsa",
    "pepperoni": "Pepperoni",
    "piña": "Piña",
    "pina": "Piña",
    "jamon": "Jamón",
    "jamón": "Jamón",
    "aceitunas": "Aceitunas",
    "aceituna": "Aceitunas",
    "champiñones": "Champiñones",
    "champinones": "Champiñones",
    "pimientos": "Pimientos",
    "pimiento": "Pimientos",
    # agrega más si tus recetas usan otros nombres
}


def _apply_synonym(name: str) -> str:
    n = _normalize_text(name)
    return _SYNONYMS.get(n, name)  # si no hay sinonimo, devolvemos original (no-normalizado)


# -------------------- OPERACIONES SOBRE ARCHIVO / NORMALIZACIÓN --------------------

def listar_inventario() -> List[Dict[str, Any]]:
    """Devuelve inventario normalizado (respetando mayúsculas original si hay)."""
    raw = _load_raw()
    out = []
    for item in raw:
        out.append({
            "ingrediente": item.get("ingrediente", ""),
            "cantidad_actual": int(item.get("cantidad_actual", 0)),
            "stock_minimo": int(item.get("stock_minimo", 0)),
            "unidad": item.get("unidad", "unidades"),
        })
    return out


def _find_index_and_item(inv: List[Dict[str, Any]], nombre: str) -> Tuple[Optional[int], Optional[Dict[str, Any]]]:
    """Busca por nombre, aplicando normalización y sinónimos. Retorna (index, item) o (None, None)."""
    if not nombre:
        return None, None
    # primero intento nombre tal cual (insensible a mayúsculas/acentos)
    target = _normalize_text(nombre)
    for idx, item in enumerate(inv):
        if _normalize_text(item.get("ingrediente", "")) == target:
            return idx, item
    # luego intento con sinónimo -> canonical
    canon = _apply_synonym(nombre)
    canon_norm = _normalize_text(canon)
    for idx, item in enumerate(inv):
        if _normalize_text(item.get("ingrediente", "")) == canon_norm:
            return idx, item
    # probar variantes title/upper/lower del canonical (por si "Masa" vs "masa")
    for idx, item in enumerate(inv):
        if _normalize_text(item.get("ingrediente", "")) == canon_norm:
            return idx, item
    return None, None


# -------------------- CRUD --------------------

def agregar_ingrediente(nombre: str, cantidad: int = 0, minimo: int = 1, unidad: str = "unidades") -> bool:
    inv = listar_inventario()
    idx, _ = _find_index_and_item(inv, nombre)
    if idx is not None:
        return False
    inv.append({
        "ingrediente": nombre.strip(),
        "cantidad_actual": int(cantidad),
        "stock_minimo": int(minimo),
        "unidad": unidad or "unidades",
    })
    _save_raw(inv)
    return True


def eliminar_ingrediente(nombre: str) -> bool:
    inv = listar_inventario()
    idx, _ = _find_index_and_item(inv, nombre)
    if idx is None:
        return False
    inv.pop(idx)
    _save_raw(inv)
    return True


def actualizar_ingrediente(nombre_original: str, nuevo_nombre: str, cantidad: int, minimo: int, unidad: str) -> bool:
    inv = listar_inventario()
    idx, item = _find_index_and_item(inv, nombre_original)
    if idx is None or item is None:
        return False
    inv[idx] = {
        "ingrediente": nuevo_nombre.strip(),
        "cantidad_actual": int(cantidad),
        "stock_minimo": int(minimo),
        "unidad": unidad or "unidades",
    }
    _save_raw(inv)
    return True


def ajustar_cantidad(nombre: str, delta: int) -> bool:
    inv = listar_inventario()
    idx, item = _find_index_and_item(inv, nombre)
    if idx is None or item is None:
        return False
    inv[idx]["cantidad_actual"] = max(0, int(inv[idx].get("cantidad_actual", 0)) + int(delta))
    _save_raw(inv)
    return True


# -------------------- UTIL / SINÓNIMOS / SEED --------------------

def seed_default_ingredients(defaults: List[Dict[str, Any]]):
    """
    Asegura que existan ingredientes en el JSON; no sobrescribe los existentes.
    defaults: lista de dicts: {"ingrediente": "Queso extra", "cantidad_actual": 0, "stock_minimo": 1, "unidad":"unidades"}
    Útil llamar al inicio de la app para sincronizar nombres usados por recetas/UI.
    """
    inv = listar_inventario()
    changed = False
    for d in defaults:
        nombre = d.get("ingrediente")
        if not nombre:
            continue
        idx, _ = _find_index_and_item(inv, nombre)
        if idx is None:
            inv.append({
                "ingrediente": d.get("ingrediente"),
                "cantidad_actual": int(d.get("cantidad_actual", 0)),
                "stock_minimo": int(d.get("stock_minimo", 1)),
                "unidad": d.get("unidad", "unidades")
            })
            changed = True
    if changed:
        _save_raw(inv)


# -------------------- LÓGICA DE CONSUMO / VERIFICACIÓN --------------------

def gramos_a_unidades(gramos: float) -> int:
    try:
        g = float(gramos)
        unidades = max(1, int(round(g / 100.0)))
        return unidades
    except Exception:
        return 1


def consumo_por_pizza(tipo_pizza: str) -> Dict[str, int]:
    uso: Dict[str, int] = {}
    try:
        if receta_vigente and tipo_pizza:
            r = receta_vigente(tipo_pizza)
            if r and getattr(r, "ingredientes", None):
                ingr = r.ingredientes or {}
                for nombre, datos in ingr.items():
                    nombre_canon = _apply_synonym(nombre)  # mapear nombre de receta a inventario si hay sinonimo
                    if isinstance(datos, dict) and ("gramos" in datos):
                        gramos = datos.get("gramos", 0)
                        uso[nombre_canon] = gramos_a_unidades(gramos)
                    else:
                        uso[nombre_canon] = 1
                return uso
    except Exception:
        pass
    # fallback mínimo
    uso[_apply_synonym("Masa")] = 1
    uso[_apply_synonym("Queso")] = 1
    return uso


def calcular_consumo_total(pedido: Dict[str, Any]) -> Dict[str, int]:
    total: Dict[str, int] = {}
    items = pedido.get("items") or []
    if isinstance(items, list) and items:
        for it in items:
            qty = int(it.get("cantidad") or 1)
            tipo = it.get("receta_tipo") or pedido.get("receta_tipo")
            uso = consumo_por_pizza(tipo or "")
            for ingr, u in uso.items():
                total[ingr] = total.get(ingr, 0) + u * qty
        return total
    # fallback de 1 pizza
    uso = consumo_por_pizza(pedido.get("receta_tipo") or "")
    for ingr, u in uso.items():
        total[ingr] = total.get(ingr, 0) + u
    return total


def verificar_y_descontar(pedido: Dict[str, Any]) -> Tuple[bool, List[str]]:
    inv = listar_inventario()
    consumo = calcular_consumo_total(pedido)
    faltantes: List[str] = []

    for ingr, needed in consumo.items():
        idx, rec = _find_index_and_item(inv, ingr)
        # si no existe, también probar con el ingrediente tal cual normalizado
        if rec is None:
            faltantes.append(f"{ingr} (no en inventario)")
            continue
        if rec.get("cantidad_actual", 0) < needed:
            faltantes.append(f"{ingr} (need {needed}, have {rec.get('cantidad_actual',0)})")

    if faltantes:
        # devolver lista de faltantes para que caller muestre diálogo
        return False, faltantes

    # descontar
    alertas: List[str] = []
    for ingr, needed in consumo.items():
        idx, rec = _find_index_and_item(inv, ingr)
        if rec is None:
            continue  # raro, ya validamos
        inv[idx]["cantidad_actual"] = int(inv[idx].get("cantidad_actual", 0)) - int(needed)
        if inv[idx]["cantidad_actual"] < 0:
            inv[idx]["cantidad_actual"] = 0
        if inv[idx]["cantidad_actual"] <= int(inv[idx].get("stock_minimo", 0)):
            alertas.append(inv[idx]["ingrediente"])

    _save_raw(inv)
    return True, alertas
