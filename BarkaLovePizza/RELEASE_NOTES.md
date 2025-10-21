Notas de la versión - Cambios subidos

Resumen:
- Se añadió soporte para animación de carga de pizza mediante un GIF ubicado en `assets/pizza_loading.*`.
- Se añadió la imagen final `assets/pizza_lista.png` que se muestra cuando la preparación termina.
- La pantalla de preparación (`screens/preparar.py`) detecta automáticamente un GIF en `assets/` y, si existe, lo usa durante el proceso de preparación (duración total: 60s). Si no hay GIF, se usan frames estáticos.
- Se agregó lógica para ocultar el botón "Modificar pedido" después de 30 segundos durante la preparación.
- Flujo de edición: al modificar un pedido no se crea una nueva orden; se actualiza la existente (`utils/pedidos.actualizar_pedido`).

Archivos clave modificados/creados:
- `screens/preparar.py` — detección GIF, uso de `pizza_lista.png`, ocultación de botón tras 30s.
- `screens/registro.py` — flujo para crear/editar pedidos y navegación a la pantalla `preparar`.
- `main` — dispatcher actualizado para pasar refs y mostrar la pantalla `preparar`.
- `utils/pedidos.py` — funciones `actualizar_pedido` y `obtener_pedido`.
- `assets/pizza_loading.gif` — GIF de carga (nuevo).
- `assets/pizza_lista.png` — imagen final (nuevo).

Notas de verificación:
- Test unitario `tests/test_pedidos.py` validó guardar y actualizar pedidos (1 passed).
- Se recomienda hacer backup de `data/pedidos.json` antes de pruebas manuales.

Si quieres, puedo convertir esto en un release tag o añadir más detalles al README.