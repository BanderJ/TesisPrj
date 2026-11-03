"""PCB-08 · ValorCafeService.crear_precios_bloque(): validación de un bloque de rangos (C1, C2 y C3).

Sin precios previos registrados hoy (model simulado). Los límites van en el formato
del sistema: enteros "X-Y" (el schema no acepta decimales como 59.99).
"""
from datetime import datetime
from typing import Iterator
from unittest.mock import MagicMock, patch

import pytest

from src.schemas.valor_cafe import ValorCafeCrearBloqueRequest
from src.services.valor_cafe_service import ValorCafeService


@pytest.fixture
def servicio() -> Iterator[ValorCafeService]:
    s = ValorCafeService()
    s.model = MagicMock()
    s.model.obtener_resumen_rangos.return_value = []
    s.model.crear_bloque.side_effect = lambda filas, db=None: [
        {"id": f"vc-{i}", "rango": r, "precio": p, "fecha": datetime.now()}
        for i, (r, p) in enumerate(filas)
    ]
    with patch("src.services.valor_cafe_service.Connection"):
        yield s


def _bloque(*precios: tuple[str, float]) -> ValorCafeCrearBloqueRequest:
    return ValorCafeCrearBloqueRequest(precios=[{"rango": r, "precio": p} for r, p in precios])


def test_c1_rangos_sin_solapamiento_y_precio_no_decreciente(servicio: ValorCafeService) -> None:
    r = servicio.crear_precios_bloque(_bloque(("40-59", 1800), ("60-100", 2000)))
    assert r.total == 2
    servicio.model.crear_bloque.assert_called_once()


def test_c2_rangos_comparten_un_limite(servicio: ValorCafeService) -> None:
    with pytest.raises(ValueError, match="se solapa"):
        servicio.crear_precios_bloque(_bloque(("60-65", 1800), ("65-70", 1900)))
    servicio.model.crear_bloque.assert_not_called()


def test_c3_precio_baja_al_subir_el_rango(servicio: ValorCafeService) -> None:
    with pytest.raises(ValueError, match="no puede ser menor"):
        servicio.crear_precios_bloque(_bloque(("40-59", 2000), ("60-100", 1800)))
    servicio.model.crear_bloque.assert_not_called()
