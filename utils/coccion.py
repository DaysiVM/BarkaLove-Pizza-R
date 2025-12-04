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

BASE_DIR = os.path.dirname(__file__)
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_PATH = os.path.join(LOG_DIR, "coccion.log")


def _log(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"[{ts}] {msg}\n")
    except Exception:
        # no rompemos la simulación por fallos de IO
        pass


@dataclass
class HornoTarget:
    temp_c: float = 220.0
    tiempo_min: float = 12.0   # minutos
    tol_temp: float = 5.0
    tol_tiempo: float = 0.5


@dataclass
class SensorState:
    temp_actual: float = 25.0            # °C
    tiempo_transcurrido: float = 0.0     # segundos
    ok: bool = True
    fallas: List[str] = field(default_factory=list)


class CoccionController:
    """
    Simulación de cocción por fases (calentamiento -> estable -> enfriamiento).
    - Si `duracion_seg` es None usa target.tiempo_min * 60 (comportamiento realista).
    - speed_factor permite acelerar (dev <1 rápido) o desacelerar (>1 lento) la simulación.
    """

    def __init__(
        self,
        tipo_pizza: Optional[str],
        id_pedido: Optional[int],
        tamanio: Optional[str] = None,
        duracion_seg: Optional[int] = None,
        rng_seed: Optional[int] = None,
        speed_factor: float = 1.0,   # 1.0 = tiempo "real" según tiempo objetivo, <1 acelera, >1 ralentiza
    ):
        self.tipo_pizza = tipo_pizza or "Genérica"
        self.id_pedido = id_pedido
        self.tamanio = (tamanio or "").lower()
        if rng_seed is not None:
            random.seed(rng_seed)

        self.target = self._cargar_objetivos()
        # duracion en segundos: si no se pasa, usar objetivo de receta (minutos -> seg)
        if duracion_seg is None:
            self.duracion_seg = max(1, int(self.target.tiempo_min * 60))
        else:
            # si el llamador pasó un valor pequeño (p. ej. 8s para pruebas),
            # lo respetamos, pero garantizamos un mínimo razonable de 4s.
            self.duracion_seg = max(4, int(duracion_seg))

        self.speed_factor = max(0.05, float(speed_factor))  # evitar 0 o negativo
        # ajustar duracion según speed_factor (speed_factor <1 -> más rápido)
        self.duracion_seg = int(self.duracion_seg * max(0.01, self.speed_factor))

        # sensor inicial
        self.sensor = SensorState(temp_actual=25.0)
        self._stop = False

    def _cargar_objetivos(self) -> HornoTarget:
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

        # ajuste simple por tamaño
        if self.tamanio == "familiar":
            tiempo_min *= 1.15
        elif self.tamanio == "individual":
            tiempo_min *= 0.9

        return HornoTarget(temp_c=temp_c, tiempo_min=tiempo_min, tol_temp=tol_temp, tol_tiempo=tol_time)

    async def run(
        self,
        on_update: Optional[Callable[[SensorState], None]] = None,
        on_alerta_visual: Optional[Callable[[str], None]] = None,
        on_alerta_sonora: Optional[Callable[[], None]] = None,
    ) -> Dict[str, Any]:
        _log(f"COCCION INICIO | Pedido #{self.id_pedido} | Tipo: {self.tipo_pizza} | Obj {self.target.temp_c}°C, {self.target.tiempo_min}min | dur_seg={self.duracion_seg}")

        # ticks: defino dt (segundos) y número de ticks
        dt = 0.5  # intervalo de actualización por defecto (seg)
        # si duracion_seg pequeño, bajar dt para tener más updates
        if self.duracion_seg < 10:
            dt = 0.25
        ticks = max(1, int(self.duracion_seg / dt))

        # dividir la duración en fases: warmup (20%), estable (60%), cooldown (20%)
        warmup_ticks = max(1, int(ticks * 0.20))
        stable_ticks = max(1, int(ticks * 0.60))
        cooldown_ticks = max(1, ticks - warmup_ticks - stable_ticks)

        try:
            # warmup: subir temp desde ambiente (25°C) hasta ~target*0.98
            for i in range(warmup_ticks):
                if self._stop:
                    _log(f"COCCION STOPPED (warmup) | Pedido #{self.id_pedido}")
                    break
                # factor de subida más agresivo en warmup
                objetivo = self.target.temp_c * 0.98
                progreso = (i + 1) / warmup_ticks
                # incremento proporcional a la diferencia
                delta = (objetivo - self.sensor.temp_actual) * (0.15 + 0.25 * (1 - progreso))
                ruido = random.uniform(-0.4, 0.4)
                self.sensor.temp_actual += max(-2.0, min(4.5, delta + ruido))
                self.sensor.tiempo_transcurrido += dt
                if on_update:
                    try:
                        on_update(self.sensor)
                    except Exception:
                        pass
                await asyncio.sleep(dt)

            # stable: mantener alrededor del objetivo con pequeños ajustes
            for i in range(stable_ticks):
                if self._stop:
                    _log(f"COCCION STOPPED (stable) | Pedido #{self.id_pedido}")
                    break
                objetivo = self.target.temp_c
                # micro-ajuste: movimiento suave hacia objetivo según proporción
                delta = (objetivo - self.sensor.temp_actual) * 0.06
                ruido = random.uniform(-0.8, 0.8)
                self.sensor.temp_actual += delta + ruido
                self.sensor.tiempo_transcurrido += dt
                # eventos raros: sobretemperatura o sensor fail
                if random.random() < 0.0015:
                    # falla breve de sensor
                    self.sensor.ok = False
                    self.sensor.fallas.append("sensor_temp_sin_lectura")
                    _log(f"ALERTA_SENSOR | Pedido #{self.id_pedido} | falla breve sensor")
                    if on_alerta_visual:
                        try:
                            on_alerta_visual("Falla de sensor: lectura intermitente")
                        except Exception:
                            pass
                    if on_alerta_sonora:
                        try:
                            on_alerta_sonora()
                        except Exception:
                            pass
                    # sleep extra corto para simular lectura perdida
                    await asyncio.sleep(dt * 1.0)
                    self.sensor.ok = True
                # sobretemperatura detectada?
                if self.sensor.temp_actual > (self.target.temp_c + self.target.tol_temp):
                    _log(f"ALERTA_SOBRECOCCION | Pedido #{self.id_pedido} | Temp {self.sensor.temp_actual:.1f}")
                    if on_alerta_visual:
                        try:
                            on_alerta_visual(f"⚠ Sobretemperatura: {self.sensor.temp_actual:.1f}°C")
                        except Exception:
                            pass
                    if on_alerta_sonora:
                        try:
                            on_alerta_sonora()
                        except Exception:
                            pass
                if on_update:
                    try:
                        on_update(self.sensor)
                    except Exception:
                        pass
                await asyncio.sleep(dt)

            # cooldown: descenso controlado (simula extracción y enfriamiento)
            for i in range(cooldown_ticks):
                if self._stop:
                    _log(f"COCCION STOPPED (cooldown) | Pedido #{self.id_pedido}")
                    break
                objetivo = 50.0  # temperatura segura post-extracción (no ambiente)
                delta = (objetivo - self.sensor.temp_actual) * 0.04
                ruido = random.uniform(-0.5, 0.5)
                self.sensor.temp_actual += delta + ruido
                self.sensor.tiempo_transcurrido += dt
                if on_update:
                    try:
                        on_update(self.sensor)
                    except Exception:
                        pass
                await asyncio.sleep(dt)

        except asyncio.CancelledError:
            _log(f"COCCION CANCELADA (CancelledError) | Pedido #{self.id_pedido}")
            raise
        except Exception as ex:
            _log(f"COCCION ERROR | Pedido #{self.id_pedido} | {ex}")

        # revisión final de sobretiempo respecto al objetivo de receta (en minutos)
        try:
            tiempo_min = self.target.tiempo_min
            tiempo_real_min = (self.sensor.tiempo_transcurrido / 60.0)
            if tiempo_real_min > (tiempo_min + self.target.tol_tiempo):
                _log(f"ALERTA_SOBRETIEMPO | Pedido #{self.id_pedido} | {tiempo_real_min:.2f} min (> {tiempo_min + self.target.tol_tiempo:.2f})")
                if on_alerta_visual:
                    try:
                        on_alerta_visual(f"⚠ Sobretiempo de cocción: {tiempo_real_min:.1f} min")
                    except Exception:
                        pass
                if on_alerta_sonora:
                    try:
                        on_alerta_sonora()
                    except Exception:
                        pass
        except Exception:
            pass

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
    speed_factor: float = 1.0,
) -> Dict[str, Any]:
    """
    Helper directo. Se puede pasar speed_factor para acelerar (ej. 0.1) en pruebas.
    """
    ctl = CoccionController(
        tipo_pizza=tipo_pizza,
        id_pedido=id_pedido,
        tamanio=tamanio,
        duracion_seg=duracion_seg,
        speed_factor=speed_factor,
    )
    return await ctl.run(on_update=on_update, on_alerta_visual=on_alerta_visual, on_alerta_sonora=on_alerta_sonora)
