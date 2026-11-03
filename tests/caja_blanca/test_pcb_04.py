"""PCB-04 · EvaluacionService.registrar_evaluacion(): requisitos para crear la evaluación (C1, C2 y C3)."""
from typing import Iterator
from unittest.mock import MagicMock, patch

import pytest

from src.schemas.evaluacion import RegistrarEvaluacionRequest
from src.services.evaluacion_service import EvaluacionService

PERSONAL_ID = "0190a1b2-0000-7000-8000-000000000001"
PAYLOAD = RegistrarEvaluacionRequest(
    num_documento="12345678", num_sacos=4, peso_bruto="200", humedad=12,
    peso_muestra="300", peso_trillado="240", num_tamiz=1, peso_tamizado="230", tipo_grano_id=1,
)
CAFICULTOR_ACTIVO = {
    "persona_id": "0190a1b2-0000-7000-8000-0000000000c1", "estado": "A",
    "tipo_caficultor_id": 2, "tipo_caficultor": "Externo",
    "nombre": "Caficultor", "ape_paterno": "Prueba", "ape_materno": "PCB",
}
PRECIOS_HOY = [{"rango": "40-100", "precio": 2000, "registrado_en": None}]


@pytest.fixture
def servicio() -> Iterator[EvaluacionService]:
    """Servicio con conexión y models simulados (sin base de datos)."""
    with patch("src.services.evaluacion_service.Connection") as conexion:
        s = EvaluacionService()
        s.caficultor_model = MagicMock()
        s.tipo_grano_model = MagicMock()
        s.valor_cafe_model = MagicMock()
        s.evaluacion_model = MagicMock()
        s.tipo_grano_model.obtener_por_id.return_value = {"id": 1, "nombre": "Pergamino"}
        s.evaluacion_model.registrar.return_value = {"id": "0190a1b2-0000-7000-8000-0000000000e1"}
        s.db = conexion.return_value
        yield s


def test_c1_caficultor_activo_y_precios_crea_evaluacion(servicio: EvaluacionService) -> None:
    servicio.caficultor_model.obtener_estado_y_tipo_por_num_documento.return_value = CAFICULTOR_ACTIVO
    servicio.valor_cafe_model.obtener_resumen_rangos.return_value = PRECIOS_HOY
    r = servicio.registrar_evaluacion(PERSONAL_ID, PAYLOAD)
    assert r.registrado is True
    assert r.data.codigo == ""  # sin código: la evaluación queda activa hasta finalizar
    servicio.evaluacion_model.registrar.assert_called_once()
    servicio.db.commit.assert_called_once()


def test_c2_caficultor_inexistente_o_inactivo(servicio: EvaluacionService) -> None:
    servicio.valor_cafe_model.obtener_resumen_rangos.return_value = PRECIOS_HOY
    for caficultor in (None, {**CAFICULTOR_ACTIVO, "estado": "I"}):
        servicio.caficultor_model.obtener_estado_y_tipo_por_num_documento.return_value = caficultor
        with pytest.raises(ValueError):
            servicio.registrar_evaluacion(PERSONAL_ID, PAYLOAD)
    servicio.evaluacion_model.registrar.assert_not_called()
    servicio.db.commit.assert_not_called()


def test_c3_sin_precios_registrados(servicio: EvaluacionService) -> None:
    servicio.caficultor_model.obtener_estado_y_tipo_por_num_documento.return_value = CAFICULTOR_ACTIVO
    servicio.valor_cafe_model.obtener_resumen_rangos.return_value = []
    with pytest.raises(ValueError, match="No hay precios de café registrados hoy"):
        servicio.registrar_evaluacion(PERSONAL_ID, PAYLOAD)
    servicio.evaluacion_model.registrar.assert_not_called()
    servicio.db.commit.assert_not_called()
