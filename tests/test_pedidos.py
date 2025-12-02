import json
import os
import pytest
from datetime import datetime

import utils.pedidos as pedidos_mod


def test_guardar_y_actualizar_pedido(tmp_path):
    # redirigir archivo de datos a tmp_path
    archivo_test = tmp_path / "pedidos.json"
    pedidos_mod.ARCHIVO = str(archivo_test)

    # asegurar archivo inicial vacío
    if os.path.exists(pedidos_mod.ARCHIVO):
        os.remove(pedidos_mod.ARCHIVO)

    pedido = {
        'orden': 123456,
        'masa': 'Delgada',
        'salsa': 'Tomate',
        'ingredientes': ['Queso extra'],
        'hora': datetime.now().isoformat()
    }

    # guardar
    pedidos_mod.guardar_pedido(pedido)
    todos = pedidos_mod.cargar_pedidos()
    assert len(todos) == 1
    assert todos[0]['orden'] == 123456

    # actualizar
    pedido_actualizado = {
        'orden': 123456,
        'masa': 'Gruesa',
        'salsa': 'BBQ',
        'ingredientes': ['Pepperoni']
    }
    pedidos_mod.actualizar_pedido(pedido_actualizado)
    todos = pedidos_mod.cargar_pedidos()
    assert len(todos) == 1
    p = todos[0]
    assert p['masa'] == 'Gruesa'
    assert p['salsa'] == 'BBQ'
    assert p['ingredientes'] == ['Pepperoni']

    # obtener_pedido
    encontrado = pedidos_mod.obtener_pedido(123456)
    assert encontrado is not None
    assert encontrado['orden'] == 123456

    # cleanup: file in tmp_path will be removed by fixture
