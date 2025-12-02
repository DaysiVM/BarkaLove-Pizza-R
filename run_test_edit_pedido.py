import shutil, os, random, json
from datetime import datetime
from utils.pedidos import guardar_pedido, cargar_pedidos, actualizar_pedido, obtener_pedido

ARCHIVO = 'data/pedidos.json'
backup = None
if os.path.exists(ARCHIVO):
    backup = ARCHIVO + '.bak'
    shutil.copy(ARCHIVO, backup)
    print('Backup creado')
else:
    print('No existía archivo pedidos.json, se creará uno nuevo para la prueba')

num = random.randint(100000, 999999)
pedido = {
    'orden': num,
    'masa': 'Delgada',
    'salsa': 'Tomate',
    'ingredientes': ['Queso extra'],
    'hora': datetime.now().isoformat()
}

print('Guardando pedido con orden', num)
guardar_pedido(pedido)
allp = cargar_pedidos()
print('Total pedidos después de guardar:', len(allp))
print('Último pedido guardado:', allp[-1])

# actualizar
pedido2 = {
    'orden': num,
    'masa': 'Gruesa',
    'salsa': 'BBQ',
    'ingredientes': ['Pepperoni', 'Queso extra']
}
print('Actualizando pedido', num)
actualizar_pedido(pedido2)
allp = cargar_pedidos()
count = sum(1 for p in allp if p.get('orden') == num)
print('Número de pedidos con esa orden (debe ser 1):', count)
print('Pedido actual:', obtener_pedido(num))

# Restaurar backup
if backup:
    shutil.move(backup, ARCHIVO)
    print('Backup restaurado')
else:
    # si no había backup, borrar el archivo creado
    try:
        os.remove(ARCHIVO)
        print('Archivo datos eliminado tras prueba')
    except Exception as e:
        print('No se pudo eliminar archivo nuevo:', e)

print('Prueba completada')
