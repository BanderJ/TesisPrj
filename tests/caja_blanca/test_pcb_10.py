"""PCB-10 · CoffeeRenTracker._resolver_clase(): clase final del grano (C1, C2 y C3).

Regla del código: se suma la confianza de cada detección por clase; si gana la clase
sana se devuelve; si gana defecto, solo se acepta cuando supera a la sana por
MARGEN_DEFECTO (1.3). Historial de detecciones simulado (sin cámara).
"""
from src.ml.tracker import CoffeeRenTracker


def test_c1_gana_la_clase_sana(tracker: CoffeeRenTracker) -> None:
    # defecto 2 × 0.60 = 1.20; verde 4 × 0.90 = 3.60
    detecciones = [("defecto", 0.60)] * 2 + [("verde", 0.90)] * 4
    assert tracker._resolver_clase(detecciones) == "verde"


def test_c2_defecto_supera_el_margen(tracker: CoffeeRenTracker) -> None:
    # defecto 4 × 0.60 = 2.40 >= verde 2 × 0.90 × 1.3 = 2.34
    detecciones = [("defecto", 0.60)] * 4 + [("verde", 0.90)] * 2
    assert tracker.MARGEN_DEFECTO == 1.3
    assert tracker._resolver_clase(detecciones) == "defecto"


def test_c3_defecto_no_supera_el_margen(tracker: CoffeeRenTracker) -> None:
    # defecto 2 × 0.50 = 1.00 gana a verde 0.90, pero 1.00 < 0.90 × 1.3 = 1.17
    detecciones = [("defecto", 0.50)] * 2 + [("verde", 0.90)]
    assert tracker._resolver_clase(detecciones) == "verde"
