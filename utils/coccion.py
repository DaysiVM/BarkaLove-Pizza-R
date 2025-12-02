# utils/coccion.py
import asyncio
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Optional, Dict, Any, List
import random

# Intentamos leer receta vigente si existe el módulo
try:
    import utils.recetas as rx
except Exception:
    rx = None


LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_PATH = os.path.join(LOG_DIR, "coccion.log")


def _log(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {msg}\n")


@dataclass
class HornoTarget:
    temp_c: float = 220.0
    tiempo_min: float = 12.0
    tol_temp: float = 5.0
    tol_tiempo: float = 0.5


@dataclass
class SensorState:
    temp_actual: float = 25.0
    tiempo_transcurrido: float = 0.0
    ok: bool = True
    fallas: List[str] = field(default_factory=list)


class CoccionController:
    """
    Controlador de cocción:
      - Lee receta vigente por tipo de pizza (si está disponible en utils.recetas).
      - Simula sensores de horno (temperatura/tiempo).
      - Ajusta automáticamente la temperatura hacia el objetivo.
      - Dispara alertas de sobrecocción y de fallo de sensor.
      - Registra eventos en logs (utils/logs/coccion.log).
    """

    def __init__(
        self,
        tipo_pizza: Optional[str],
        id_pedido: Optional[int],
        tamanio: Optional[str] = None,
        duracion_seg: Optional[int] = None,
        rng_seed: Optional[int] = None,
    ):
        self.tipo_pizza = tipo_pizza or "Genérica"
        self.id_pedido = id_pedido
        self.tamanio = (tamanio or "").lower()
        if rng_seed is not None:
            random.seed(rng_seed)

        self.target = self._cargar_objetivos()
        # Si no se indica duración, usamos el objetivo de la receta (tiempo_min en minutos -> a segundos).
        self.duracion_seg = duracion_seg if duracion_seg is not None else int(self.target.tiempo_min * 60)

        # Estado interno del sensor y “control” simple
        self.sensor = SensorState(temp_actual=25.0)
        self._stop = False

    def _cargar_objetivos(self) -> HornoTarget:
        """
        Lee receta vigente desde utils.recetas para tipo_pizza y extrae:
          - horno.temp_c
          - horno.tiempo_min
          - horno.tolerancias (temp, tiempo)
        Si no hay receta, usa defaults.
        Opcional: ajustar objetivos por tamaño (ejemplo simple).
        """
        temp_c = 220.0
        tiempo_min = 12.0
        tol_temp = 5.0
        tol_time = 0.5

        if rx is not None and self.tipo_pizza:
            try:
                ver = rx.vigente(self.tipo_pizza)
                if ver and getattr(ver, "horno", None):
                    hd: Dict[str, Any] = ver.horno or {}
                    tol = hd.get("tol") or {}
                    temp_c = float(hd.get("temp_c", temp_c))
                    tiempo_min = float(hd.get("tiempo_min", tiempo_min))
                    tol_temp = float(tol.get("temp", tol_temp))
                    tol_time = float(tol.get("tiempo", tol_time))
            except Exception as ex:
                _log(f"AVISO: No se pudo leer receta vigente para '{self.tipo_pizza}': {ex}")

        # Ajuste simple por tamaño (opcional, se puede tunear)
        if self.tamanio == "familiar":
            tiempo_min *= 1.15  # 15% más
        elif self.tamanio == "individual":
            tiempo_min *= 0.9   # 10% menos

        return HornoTarget(temp_c=temp_c, tiempo_min=tiempo_min, tol_temp=tol_temp, tol_tiempo=tol_time)

    async def run(
        self,
        on_update: Optional[Callable[[SensorState], None]] = None,
        on_alerta_visual: Optional[Callable[[str], None]] = None,
        on_alerta_sonora: Optional[Callable[[], None]] = None,
    ) -> Dict[str, Any]:
        """
        Ejecuta la sesión de cocción (asincrónica). Devuelve resumen.
        - on_update: callback para refrescar UI (temperatura/tiempo).
        - on_alerta_visual: callback para mostrar banner/mensaje de alerta.
        - on_alerta_sonora: callback para reproducir beep.
        """
        _log(f"COCCION INICIO | Pedido #{self.id_pedido} | Tipo: {self.tipo_pizza} | Objetivo: {self.target.temp_c}°C, {self.target.tiempo_min} min")

        dt = 0.5  # segundos por tick
        ticks = int(self.duracion_seg / dt)
        calentamiento = True

        for i in range(ticks):
            if self._stop:
                break

            # Simulación de fallo de sensor ocasional (muy baja probabilidad)
            if random.random() < 0.003:
                self.sensor.ok = False
                self.sensor.fallas.append("sensor_temp_sin_lectura")
                msg = f"ALERTA_SENSOR | Pedido #{self.id_pedido} | Falla sensor temperatura (sin lectura)"
                _log(msg)
                if on_alerta_visual: on_alerta_visual("⚠ Falla de sensor: temperatura sin lectura")
                if on_alerta_sonora: on_alerta_sonora()
                # Recuperación rápida al siguiente tick
                await asyncio.sleep(dt)
                self.sensor.ok = True

            # Si sensor está ok, “medimos” y ajustamos
            if self.sensor.ok:
                # Control súper simple: mover temp_actual hacia target con ruido
                objetivo = self.target.temp_c
                # during first 20%: subida rápida; luego microajustes
                if i < ticks * 0.2:
                    delta = (objetivo - self.sensor.temp_actual) * 0.15
                else:
                    delta = (objetivo - self.sensor.temp_actual) * 0.07
                ruido = random.uniform(-0.6, 0.6)
                self.sensor.temp_actual += delta + ruido
                self.sensor.tiempo_transcurrido = i * dt

                # Sobretemperatura (sobre-cocción por temp)
                if self.sensor.temp_actual > (self.target.temp_c + self.target.tol_temp):
                    msg = f"ALERTA_SOBRECOCCION | Pedido #{self.id_pedido} | Temp {self.sensor.temp_actual:.1f}°C (> {self.target.temp_c + self.target.tol_temp:.1f}°C)"
                    _log(msg)
                    if on_alerta_visual: on_alerta_visual(f"⚠ Sobretemperatura: {self.sensor.temp_actual:.1f}°C")
                    if on_alerta_sonora: on_alerta_sonora()

                # Update UI
                if on_update:
                    on_update(self.sensor)

            await asyncio.sleep(dt)

        # Fin de cocción: revisar sobretiempo
        tiempo_min = self.target.tiempo_min
        t_min_rebasado = (self.sensor.tiempo_transcurrido / 60.0) > (tiempo_min + self.target.tol_tiempo)
        if t_min_rebasado:
            msg = f"ALERTA_SOBRECOCCION | Pedido #{self.id_pedido} | Tiempo {self.sensor.tiempo_transcurrido/60.0:.2f} min (> {tiempo_min + self.target.tol_tiempo:.2f} min)"
            _log(msg)
            if on_alerta_visual: on_alerta_visual(f"⚠ Sobretiempo de cocción: {self.sensor.tiempo_transcurrido/60.0:.1f} min")
            if on_alerta_sonora: on_alerta_sonora()

        resumen = {
            "pedido": self.id_pedido,
            "tipo_pizza": self.tipo_pizza,
            "temp_objetivo": self.target.temp_c,
            "tiempo_objetivo_min": self.target.tiempo_min,
            "temp_final": round(self.sensor.temp_actual, 1),
            "tiempo_real_min": round(self.sensor.tiempo_transcurrido / 60.0, 2),
            "fallas": self.sensor.fallas,
        }
        _log(f"COCCION FIN | {resumen}")
        return resumen

    def stop(self):
        self._stop = True


async def ejecutar_coccion_para_pedido(
    id_pedido: int,
    tipo_pizza: Optional[str],
    tamanio: Optional[str],
    duracion_seg: Optional[int],
    on_update: Optional[Callable[[SensorState], None]],
    on_alerta_visual: Optional[Callable[[str], None]],
    on_alerta_sonora: Optional[Callable[[], None]],
) -> Dict[str, Any]:
    """
    Helper directo para usar desde pantallas.
    """
    ctl = CoccionController(
        tipo_pizza=tipo_pizza,
        id_pedido=id_pedido,
        tamanio=tamanio,
        duracion_seg=duracion_seg
    )
    return await ctl.run(on_update=on_update, on_alerta_visual=on_alerta_visual, on_alerta_sonora=on_alerta_sonora)
