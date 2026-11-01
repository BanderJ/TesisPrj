"""Infraestructura de las pruebas de caja blanca (PCB-XX).

No usan la base de datos ni hardware: los models, la conexión, el detector YOLO,
ByteTrack y el puerto serie del Arduino se reemplazan con mocks. El servo
(servo_controller.py) y el Arduino (arduino_serial.py) no se modifican.
"""
from decimal import Decimal, ROUND_FLOOR
from typing import Any, Callable, Iterator
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from src.ml.tracker import CoffeeRenTracker
from src.schemas.evaluacion import CompletarEvaluacionRequest
from src.services.evaluacion_service import EvaluacionService

FRAME = np.zeros((1080, 1920, 3), dtype=np.uint8)
CLASE_IDX = {"defecto": 0, "verde": 1}
TIPO_EXTERNO_ID = 2  # caficultor Externo: el pago no suma beneficio de socio


@pytest.fixture
def completar() -> Iterator[Callable[..., Any]]:
    """Ejecuta EvaluacionService.completar_evaluacion() sobre una evaluación simulada.

    Valores por defecto de PCB-05 y PCB-06: muestra 300 g, trillado 240 g, tamizado 230 g, 4 sacos,
    200.00 kg, Pergamino (55.20 kg por quintal) y un único rango de precio de hoy
    40-100 a S/ 2000. Devuelve (respuesta, kwargs pasados a Evaluacion.completar).
    """
    with patch("src.services.evaluacion_service.Connection"):
        servicio = EvaluacionService()
        servicio.evaluacion_model = MagicMock()
        servicio.tipo_grano_model = MagicMock()
        servicio.valor_cafe_model = MagicMock()
        servicio.bono_socio_service = MagicMock()
        servicio.tipo_grano_model.obtener_por_id.return_value = {"id": 1, "nombre": "Pergamino", "peso_qq": Decimal("55.20")}
        servicio.evaluacion_model.completar.side_effect = lambda **kw: {**kw, "codigo": kw["codigo"]}

        def _ejecutar(peso_bueno: int, humedad: int = 12, num_sacos: int = 4,
                      peso_bruto: str = "200.00",
                      rangos: list[tuple[str, str]] | None = None) -> tuple[Any, dict[str, Any]]:
            precios = rangos if rangos is not None else [("40-100", "2000")]

            def buscar_precio(fr: Decimal, fecha: Any, db: Any) -> dict[str, Any] | None:
                entero = fr.to_integral_value(rounding=ROUND_FLOOR)
                for i, (rango, precio) in enumerate(precios, start=1):
                    limites = rango.split("-")
                    if Decimal(limites[0]) <= entero <= Decimal(limites[-1]):
                        return {"id": f"vc-{i}", "rango": rango, "precio": Decimal(precio)}
                return None

            servicio.valor_cafe_model.obtener_por_factor.side_effect = buscar_precio
            servicio.evaluacion_model.obtener_para_completar.return_value = {
                "codigo": "EVA0000001", "factor_rendimiento": None, "tipo_grano_id": 1,
                "peso_muestra": Decimal("300"), "peso_trillado": Decimal("240"),
                "peso_tamizado": Decimal("230"),
                "peso_bruto": Decimal(peso_bruto), "num_sacos": num_sacos, "humedad": humedad,
                "tipo_caficultor_id": TIPO_EXTERNO_ID,
            }
            respuesta = servicio.completar_evaluacion(
                "0190a1b2-0000-7000-8000-0000000000e1",
                CompletarEvaluacionRequest(total_defectos=10, peso_bueno=peso_bueno),
            )
            return respuesta, servicio.evaluacion_model.completar.call_args.kwargs

        yield _ejecutar


@pytest.fixture(scope="session")
def tracker_base() -> CoffeeRenTracker:
    """Tracker real con el modelo YOLO simulado: __init__ carga constants.py,
    SERVO_MIN_FRAMES, SERVO_CONF_MIN y MARGEN_DEFECTO tal como en producción."""
    with patch("src.ml.tracker.YOLO", MagicMock()):
        return CoffeeRenTracker(conf=0.25)


@pytest.fixture
def tracker(tracker_base: CoffeeRenTracker) -> CoffeeRenTracker:
    """Tracker sin historial, con detector y ByteTrack simulados."""
    tracker_base.resetear_conteo()
    tracker_base._detectar = MagicMock(return_value=np.zeros((0, 6), dtype=np.float32))
    tracker_base._bytetracker = MagicMock()
    return tracker_base


def pista(lado_px: int, clase: str, conf: float, bytetrack_id: int = 1) -> list[float]:
    """Fila de ByteTrack (x1, y1, x2, y2, id, conf, cls, idx) para una caja cuadrada."""
    x1, y1 = 100, 100
    return [x1, y1, x1 + lado_px, y1 + lado_px, bytetrack_id, conf, CLASE_IDX[clase], 0]


def procesar(tracker: CoffeeRenTracker, pistas: list[list[float]], ts_frame: float | None = None) -> Any:
    """Pasa un frame por procesar_frame() con las pistas que devolvería ByteTrack."""
    tracker._bytetracker.update.return_value = np.array(pistas, dtype=np.float32)
    return tracker.procesar_frame(FRAME, ts_frame=ts_frame)
