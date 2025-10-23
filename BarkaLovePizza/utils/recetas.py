# utils/recetas.py
import json
import os
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional

BASE_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE_DIR, "recetas_data.json")


@dataclass
class RecetaVersion:
    tipo_pizza: str
    version_id: str
    autor: str
    fecha: str
    notas: str
    ingredientes: Dict[str, Any]
    horno: Dict[str, Any]
    activo: bool = False


def _load_data() -> Dict[str, List[Dict[str, Any]]]:
    """Carga el JSON de recetas."""
    if not os.path.exists(DATA_PATH):
        return {}
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_data(data: Dict[str, Any]):
    """Guarda el JSON de recetas."""
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def listar_tipos() -> List[str]:
    data = _load_data()
    return list(data.keys())


def historial(tipo_pizza: str) -> List[RecetaVersion]:
    data = _load_data()
    versiones = data.get(tipo_pizza, [])
    return [RecetaVersion(**v) for v in versiones]


def vigente(tipo_pizza: str) -> Optional[RecetaVersion]:
    for v in historial(tipo_pizza):
        if v.activo:
            return v
    return None


def nueva_version(tipo_pizza: str, version_id: str, autor: str, notas: str,
                  ingredientes: Dict[str, Any], horno: Dict[str, Any], activar: bool = False) -> bool:
    """Crea una nueva versión de receta."""
    data = _load_data()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    version = RecetaVersion(
        tipo_pizza=tipo_pizza,
        version_id=version_id,
        autor=autor,
        fecha=now,
        notas=notas,
        ingredientes=ingredientes,
        horno=horno,
        activo=False
    )

    if tipo_pizza not in data:
        data[tipo_pizza] = []

    # Si activar=True, desactiva todas las anteriores
    if activar:
        for v in data[tipo_pizza]:
            v["activo"] = False
        version.activo = True

    data[tipo_pizza].append(asdict(version))
    _save_data(data)
    return True


def activar_version(tipo_pizza: str, version_id: str) -> bool:
    """Activa una versión y desactiva las demás."""
    data = _load_data()
    if tipo_pizza not in data:
        return False

    found = False
    for v in data[tipo_pizza]:
        if v["version_id"] == version_id:
            v["activo"] = True
            found = True
        else:
            v["activo"] = False

    if found:
        _save_data(data)
    return found
