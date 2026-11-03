"""PCB-12 · CoffeeRenTracker._evidencia_suficiente(): compuerta de evidencia antes de
accionar el servo (C1, C2 y C3).

Se usa el servo_controller real (sin modificarlo) y se simula el puerto serie:
arduino_serial se reemplaza con un mock que registra los comandos enviados. Así se
comprueba la orden que saldría al Arduino tras SERVO_DELAY_S.
"""
import time
from typing import Iterator
from unittest.mock import MagicMock, patch

import pytest

from src.config import Config
from src.ml.tracker import CoffeeRenTracker
from src.utilities.servo_controller import servo_controller
from tests.caja_blanca.conftest import pista, procesar

ESPERA_S = Config.SERVO_DELAY_S + Config.SERVO_HOLD_S + 0.5


@pytest.fixture
def servo() -> Iterator[tuple[MagicMock, MagicMock]]:
    """(arduino simulado, espía de servo_controller.solicitar)."""
    arduino = MagicMock()
    arduino.enviar_comando.return_value = True
    with patch("src.utilities.servo_controller.arduino_serial", arduino), \
         patch.object(servo_controller, "solicitar", wraps=servo_controller.solicitar) as solicitar:
        yield arduino, solicitar
    servo_controller.limpiar_cola()


def _comandos(arduino: MagicMock) -> list[str]:
    time.sleep(ESPERA_S)
    return [c.args[0] for c in arduino.enviar_comando.call_args_list]


def test_c1_una_deteccion_de_baja_confianza_no_acciona(
    tracker: CoffeeRenTracker, servo: tuple[MagicMock, MagicMock]
) -> None:
    arduino, solicitar = servo
    procesar(tracker, [pista(200, "defecto", 0.30)], ts_frame=time.monotonic())
    assert solicitar.call_count == 0
    assert "SERVO:DEFECTO" not in _comandos(arduino)


def test_c2_dos_detecciones_accionan(tracker: CoffeeRenTracker, servo: tuple[MagicMock, MagicMock]) -> None:
    arduino, solicitar = servo
    procesar(tracker, [pista(200, "defecto", 0.30)], ts_frame=time.monotonic())
    procesar(tracker, [pista(200, "defecto", 0.30)], ts_frame=time.monotonic())
    assert solicitar.call_count == 1
    assert _comandos(arduino)[0] == "SERVO:DEFECTO"


def test_c3_una_deteccion_de_alta_confianza_acciona(
    tracker: CoffeeRenTracker, servo: tuple[MagicMock, MagicMock]
) -> None:
    arduino, solicitar = servo
    procesar(tracker, [pista(200, "defecto", 0.50)], ts_frame=time.monotonic())
    assert solicitar.call_count == 1
    assert _comandos(arduino)[0] == "SERVO:DEFECTO"
