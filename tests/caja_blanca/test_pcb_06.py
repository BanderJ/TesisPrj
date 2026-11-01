"""PCB-06 · EvaluacionService.completar_evaluacion(): castigo por humedad y peso por quintal (C1, C2 y C3).

Datos: 4 sacos, peso bruto 200.00 kg, Pergamino (55.20 kg/qq), precio del rango S/ 2000,
caficultor Externo (sin beneficio de socio). Tara = round(4 × 0.25) = 1; peso neto = 199.00.
Los esperados salen de las fórmulas de la sección 5 de DOCUMENTACION_SISTEMA.md.
"""
from decimal import Decimal
from typing import Any, Callable


def test_c1_humedad_hasta_12_sin_castigo(completar: Callable[..., Any]) -> None:
    respuesta, guardado = completar(peso_bueno=200, humedad=12)
    assert guardado["tara_total"] == 1
    assert guardado["peso_neto"] == Decimal("199.00")
    # Sin castigo el peso por quintal sale del peso neto completo: 199 / 55.20.
    assert respuesta.peso_por_qq == Decimal("3.60")


def test_c2_humedad_mayor_a_12_con_castigo(completar: Callable[..., Any]) -> None:
    respuesta, guardado = completar(peso_bueno=200, humedad=15)
    assert guardado["peso_neto"] == Decimal("199.00")
    # Castigo = 199 × 3 / 85 = 7.02; (199 − 7.02) / 55.20 = 3.477… → 3.47
    assert respuesta.peso_por_qq == Decimal("3.47")
    assert respuesta.pago == Decimal("6940.00")


def test_c3_peso_por_quintal_redondeo_hacia_abajo(completar: Callable[..., Any]) -> None:
    respuesta, _ = completar(peso_bueno=200, humedad=12)
    # 199 / 55.20 = 3.605… → 3.60 (no 3.61)
    assert respuesta.peso_por_qq == Decimal("3.60")
    assert respuesta.pago == Decimal("7200.00")
