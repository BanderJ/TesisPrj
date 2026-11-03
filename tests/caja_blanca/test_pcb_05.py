"""PCB-05 · EvaluacionService.completar_evaluacion(): peso final y factor de rendimiento (C1 a C4).

Evaluación simulada: muestra 300 g, trillado 240 g y tamizado 230 g.
FR = peso bueno / (peso de muestra / 100).
"""
from decimal import Decimal
from typing import Any, Callable

import pytest


def test_c1_peso_valido_con_rango_de_precio(completar: Callable[..., Any]) -> None:
    respuesta, guardado = completar(peso_bueno=200)
    assert respuesta.factor_rendimiento == Decimal("66.67")  # 200 / (300 / 100)
    assert respuesta.rango == "40-100"
    assert respuesta.precio == Decimal("2000")
    assert guardado["valor_cafe_id"] == "vc-1"


def test_c2_peso_bueno_supera_peso_tamizado(completar: Callable[..., Any]) -> None:
    with pytest.raises(ValueError, match=r"El peso de grano bueno \(235 g\) no puede superar el peso tamizado \(230 g\)\."):
        completar(peso_bueno=235)


def test_c3_sin_rango_de_precio_para_el_fr(completar: Callable[..., Any]) -> None:
    # 119 / (300 / 100) = 39.67, fuera del rango 40-100.
    with pytest.raises(ValueError, match=r"No hay precio de café registrado hoy para el rango "
                                         r"del factor de rendimiento \(39\.67\)"):
        completar(peso_bueno=119)


def test_c4_factor_decimal_usa_rango_de_su_parte_entera(completar: Callable[..., Any]) -> None:
    respuesta, guardado = completar(peso_bueno=197, rangos=[("60-65", "1900"), ("66-70", "2000")])
    assert respuesta.factor_rendimiento == Decimal("65.67")
    assert guardado["factor_rendimiento"] == Decimal("65.67")
    assert respuesta.rango == "60-65"
    assert respuesta.precio == Decimal("1900")
    assert guardado["valor_cafe_id"] == "vc-1"
