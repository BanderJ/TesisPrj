"""PCB-11 · CoffeeRenTracker.procesar_frame(): filtro de tamaño de la detección (C1, C2 y C3).

Límites de constants.py: GRANO_MIN_PX = 50 y GRANO_MAX_PX = 640, inclusivos.
Detector y ByteTrack simulados; el servo se reemplaza con un mock.
"""
from unittest.mock import patch

from src.ml.tracker import CoffeeRenTracker
from tests.caja_blanca.conftest import pista, procesar


def _contados(tracker: CoffeeRenTracker, lado_px: int) -> int:
    tracker.resetear_conteo()
    with patch("src.ml.tracker.servo_controller"):
        procesar(tracker, [pista(lado_px, "verde", 0.90)])
    return sum(tracker.obtener_conteo().values())


def test_c1_tamano_dentro_del_rango_se_cuenta(tracker: CoffeeRenTracker) -> None:
    assert (tracker.GRANO_MIN_PX, tracker.GRANO_MAX_PX) == (50, 640)
    assert _contados(tracker, 50) == 1
    assert _contados(tracker, 640) == 1


def test_c2_tamano_menor_al_minimo_se_descarta(tracker: CoffeeRenTracker) -> None:
    assert _contados(tracker, 49) == 0


def test_c3_tamano_mayor_al_maximo_se_descarta(tracker: CoffeeRenTracker) -> None:
    assert _contados(tracker, 641) == 0
