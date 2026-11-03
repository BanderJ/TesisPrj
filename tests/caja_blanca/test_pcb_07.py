"""PCB-07 · calcular_defectos(): total de defectos equivalentes del lote (C1, C2 y C3).

Sustituye al caso original de grado 1/2/3: el grado SCA se retiró del sistema y
classifier.py solo suma defectos equivalentes. Equivalencias: EQUIVALENCIAS_DEFECTO
del modelo yolov26n_2cls (defecto = 1, verde = 0.0, desconocido = 1.0).
"""
from src.ml.classifier import calcular_defectos
from src.ml.models.yolov26n_2cls.constants import EQUIVALENCIAS_DEFECTO


def test_c1_clase_sana_no_suma_defectos() -> None:
    r = calcular_defectos({"verde": 20}, EQUIVALENCIAS_DEFECTO)
    assert r["total_defectos"] == 0
    assert r["detalle"]["verde"]["defectos_equivalentes"] == 0


def test_c2_clase_con_equivalencia_suma_cantidad_por_peso() -> None:
    r = calcular_defectos({"defecto": 15, "verde": 5}, EQUIVALENCIAS_DEFECTO)
    assert r["total_defectos"] == 15
    assert r["detalle"]["defecto"]["defectos_equivalentes"] == 15


def test_c3_cantidad_cero_o_clase_sin_equivalencia_se_ignora() -> None:
    r = calcular_defectos({"defecto": 0, "piedra": 3}, EQUIVALENCIAS_DEFECTO)
    assert r["total_defectos"] == 0
    assert r["detalle"] == {}
