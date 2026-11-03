"""PCB-03 · RegistrarEvaluacionRequest: pesos y límite de humedad (C1 a C14)."""
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


@pytest.mark.parametrize("muestra", ["100", "150", "200", "250", "300"])
@pytest.mark.parametrize("caso", ["uno", "diez", "debajo", "exacto", "encima"])
def test_c6_trillado_debe_superar_60_por_ciento(muestra: str, caso: str) -> None:
    minimo = Decimal(muestra) * Decimal("0.60")
    trillado = {
        "uno": Decimal("1"), "diez": Decimal("10"),
        "debajo": minimo - Decimal("0.01"), "exacto": minimo,
        "encima": minimo + Decimal("0.01"),
    }[caso]
    payload = {**BASE, "peso_muestra": muestra, "peso_trillado": trillado, "peso_tamizado": trillado}
    if caso == "encima":
        assert RegistrarEvaluacionRequest(**payload).peso_trillado == trillado
    else:
        with pytest.raises(ValidationError, match="El peso trillado debe ser mayor al 60% del peso de muestra"):
            RegistrarEvaluacionRequest(**payload)


@pytest.mark.parametrize("trillado,tamizado,valido", [
    ("240", "1", False), ("240", "10", False),
    ("240", "191.99", False), ("240", "192", False),
    ("240", "192.01", True), ("240", "240", True),
    ("200.15", "160.12", False), ("200.15", "160.13", True),
    ("232.51", "186.00", False), ("232.51", "186.01", True),
])
def test_c7_tamizado_debe_superar_80_por_ciento(trillado: str, tamizado: str, valido: bool) -> None:
    payload = {**BASE, "peso_trillado": trillado, "peso_tamizado": tamizado}
    if valido:
        assert RegistrarEvaluacionRequest(**payload).peso_tamizado == Decimal(tamizado)
    else:
        with pytest.raises(ValidationError, match="El peso tamizado debe ser mayor al 80% del peso trillado"):
            RegistrarEvaluacionRequest(**payload)


@pytest.mark.parametrize("muestra", ["100", "150", "200", "250", "300"])
def test_c8_maximo_83_por_ciento_es_inclusivo(muestra: str) -> None:
    maximo = Decimal(muestra) * Decimal("0.83")
    payload = {**BASE, "peso_muestra": muestra, "peso_trillado": maximo, "peso_tamizado": maximo}
    assert RegistrarEvaluacionRequest(**payload).peso_trillado == maximo
    with pytest.raises(ValidationError, match="no puede superar el 83% del peso de muestra"):
        RegistrarEvaluacionRequest(**{**payload, "peso_trillado": maximo + Decimal("0.01")})


@pytest.mark.parametrize("campo,valor", [("peso_trillado", "180.001"), ("peso_tamizado", "192.001")])
def test_c9_precision_de_pesos_coincide_con_la_base(campo: str, valor: str) -> None:
    with pytest.raises(ValidationError) as exc:
        RegistrarEvaluacionRequest(**{**BASE, campo: valor})
    error = exc.value.errors()[0]
    assert error["loc"] == (campo,)
    assert error["type"] == "decimal_max_places"


def test_c10_peso_muestra_no_permitido() -> None:
    with pytest.raises(ValidationError, match="El peso de muestra debe ser 100, 150, 200, 250 o 300 gr."):
        RegistrarEvaluacionRequest(**{**BASE, "peso_muestra": "125"})


def test_c11_trillado_igual_a_la_muestra() -> None:
    with pytest.raises(ValidationError, match="El peso trillado debe ser diferente al peso de muestra"):
        RegistrarEvaluacionRequest(**{**BASE, "peso_trillado": "300"})


def test_c12_trillado_mayor_a_la_muestra() -> None:
    with pytest.raises(ValidationError, match="El peso trillado no puede ser mayor al peso de muestra"):
        RegistrarEvaluacionRequest(**{**BASE, "peso_trillado": "300.01"})


@pytest.mark.parametrize("peso", ["280.00", "280.01"])
def test_c13_peso_bruto_maximo_por_saco(peso: str) -> None:
    payload = {**BASE, "peso_bruto": peso}
    if peso == "280.00":
        assert RegistrarEvaluacionRequest(**payload).peso_bruto == Decimal(peso)
    else:
        with pytest.raises(ValidationError, match="El peso total no puede superar 280 kg"):
            RegistrarEvaluacionRequest(**payload)


@pytest.mark.parametrize("peso", ["0.99", "1.00", "1.01"])
def test_c14_peso_bruto_debe_superar_la_tara(peso: str) -> None:
    payload = {**BASE, "peso_bruto": peso}
    if peso == "1.01":
        assert RegistrarEvaluacionRequest(**payload).peso_bruto == Decimal(peso)
    else:
        with pytest.raises(ValidationError, match="El peso total debe ser mayor a la tara de los sacos"):
            RegistrarEvaluacionRequest(**payload)
