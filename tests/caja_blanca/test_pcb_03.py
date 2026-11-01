"""PCB-03 · RegistrarEvaluacionRequest: pesos y límite de humedad (C1 a C5)."""
from decimal import Decimal

import pytest
from pydantic import ValidationError

from src.schemas.evaluacion import RegistrarEvaluacionRequest

BASE = {
    "num_documento": "12345678",
    "num_sacos": 4,
    "peso_bruto": "200",
    "humedad": 12,
    "peso_muestra": "300",
    "peso_trillado": "240",
    "num_tamiz": 1,
    "peso_tamizado": "230",
    "tipo_grano_id": 1,
}


def test_c1_pesos_positivos_y_trillado_dentro_del_83() -> None:
    datos = RegistrarEvaluacionRequest(**BASE)
    assert datos.peso_muestra == Decimal("300")
    assert datos.peso_trillado == Decimal("240")


def test_c2_peso_no_positivo() -> None:
    with pytest.raises(ValidationError) as exc:
        RegistrarEvaluacionRequest(**{**BASE, "peso_bruto": "0"})
    error = exc.value.errors()[0]
    assert error["loc"] == ("peso_bruto",)
    assert error["type"] == "greater_than"


def test_c3_trillado_supera_83_por_ciento() -> None:
    # 83 % de 300 g = 249 g; 250 g lo supera.
    with pytest.raises(ValidationError) as exc:
        RegistrarEvaluacionRequest(**{**BASE, "peso_trillado": "250"})
    assert "no puede superar el 83% del peso de muestra" in str(exc.value)


def test_c4_tamizado_mayor_al_trillado() -> None:
    with pytest.raises(ValidationError) as exc:
        RegistrarEvaluacionRequest(**{**BASE, "peso_trillado": "240", "peso_tamizado": "250"})
    assert "El peso tamizado no puede ser mayor al peso trillado" in str(exc.value)


def test_c5_limite_humedad_validado_por_field() -> None:
    assert RegistrarEvaluacionRequest(**{**BASE, "humedad": 30}).humedad == 30
    for humedad, tipo, contexto in (
        (31, "less_than_equal", {"le": 30}),
        (0, "greater_than_equal", {"ge": 1}),
        (12.5, "int_from_float", None),
    ):
        with pytest.raises(ValidationError) as exc:
            RegistrarEvaluacionRequest(**{**BASE, "humedad": humedad})
        error = exc.value.errors()[0]
        assert error["loc"] == ("humedad",)
        assert error["type"] == tipo
        assert error.get("ctx") == contexto
