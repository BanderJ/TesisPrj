"""PCB-09 · Evaluacion.asignar_codigo(), llamado por EvaluacionService.finalizar_evaluacion():
generación del código EVA (C1 y C2). Conexión simulada: no se usa la base de datos.
"""
from typing import Any, Iterator
from unittest.mock import MagicMock, patch

import pytest

from src.services.evaluacion_service import EvaluacionService

EVALUACION_ID = "0190a1b2-0000-7000-8000-0000000000e1"
INCIDENCIAS = [{"seg_apertura": 10, "seg_cierre": 14, "duracion_s": 4}]
# Conteo que el tracker del servidor entrega para el lote de esta evaluación.
CONTEO_LOTE = {"total_defectos": 12, "total_sanos": 88}


class BdSimulada:
    """Conexión mínima: guarda el código de la evaluación y el último correlativo EVA."""

    def __init__(self, ultimo_correlativo: int) -> None:
        self.codigo: str | None = None
        self.ultimo = ultimo_correlativo
        self.consultas: list[str] = []
        self.update_params: tuple[Any, ...] | None = None
        self.commit = MagicMock()
        self.rollback = MagicMock()
        self.close = MagicMock()

    def obtener_uno(self, sql: str, params: tuple[Any, ...] | None = None) -> dict[str, Any] | None:
        self.consultas.append(sql)
        if "TRIM(codigo)" in sql:
            return {"codigo": self.codigo}
        return {"codigo": f"EVA{self.ultimo + 1:07d}"}  # _generar_codigo (nextval)

    def ejecutar(self, sql: str, params: tuple[Any, ...]) -> Any:
        self.update_params = params
        self.codigo = params[0]
        cursor = MagicMock()
        cursor.fetchone.return_value = {"id": EVALUACION_ID, "codigo": self.codigo}
        return cursor


@pytest.fixture
def entorno() -> Iterator[tuple[EvaluacionService, BdSimulada]]:
    bd = BdSimulada(ultimo_correlativo=41)
    with patch("src.services.evaluacion_service.Connection", return_value=bd):
        servicio = EvaluacionService()
        servicio.evento_model = MagicMock()
        yield servicio, bd


def test_c1_evaluacion_sin_codigo_genera_el_siguiente(entorno: tuple[EvaluacionService, BdSimulada]) -> None:
    servicio, bd = entorno
    r = servicio.finalizar_evaluacion(EVALUACION_ID, CONTEO_LOTE, incidencias=INCIDENCIAS)
    assert r.codigo == "EVA0000042"
    codigo, total_defectos, total_buenos, incidencias_json, _ = bd.update_params
    assert (codigo, total_defectos, total_buenos) == ("EVA0000042", 12, 88)
    assert '"duracion_s": 4' in incidencias_json
    bd.commit.assert_called_once()


def test_c2_reintento_devuelve_el_mismo_codigo(entorno: tuple[EvaluacionService, BdSimulada]) -> None:
    servicio, bd = entorno
    primero = servicio.finalizar_evaluacion(EVALUACION_ID, CONTEO_LOTE)
    consultas_antes = len(bd.consultas)
    segundo = servicio.finalizar_evaluacion(EVALUACION_ID, CONTEO_LOTE)
    assert segundo.codigo == primero.codigo == "EVA0000042"
    # En el reintento solo se lee el código existente: no se pide otro correlativo
    # ni se reescribe la evaluación.
    assert not any("nextval" in c for c in bd.consultas[consultas_antes:])
    assert bd.update_params[0] == "EVA0000042"
