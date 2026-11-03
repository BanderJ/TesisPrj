"""Protección del lote compartido entre Monitoreo y Prueba, sin BD ni hardware."""

import threading
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.schemas.evaluacion import FinalizarEvaluacionResponse
from src.utilities.jwt_required import obtener_usuario_actual

with patch("src.ml.tracker.CoffeeRenTracker"):
    from src.services.tracker_service import TrackerService


EVALUACION = "0190a1b2-0000-7000-8000-000000000001"
OTRA_EVALUACION = "0190a1b2-0000-7000-8000-000000000002"


@pytest.fixture
def servicio() -> Iterator[TrackerService]:
    servicio = TrackerService.__new__(TrackerService)
    servicio._control_lock = threading.Lock()
    servicio._lock = threading.Lock()
    servicio._evaluacion_id = EVALUACION
    servicio._frame_anotado = b"frame original"
    servicio._thread = None
    servicio._camara_desconectada = False
    servicio._error_camara = None
    servicio.activo = True
    servicio.model_name = "modelo de prueba"
    servicio.tracker = MagicMock()
    servicio.tracker.EQUIVALENCIAS_DEFECTO = {"verde": 0, "defecto": 1}
    servicio.tracker.GRUPOS_DISPLAY = {}
    servicio.tracker.CLASE_DESCONOCIDO = "desconocido"
    servicio.tracker.ultima_deteccion_frame_ts = None
    servicio.tracker.obtener_fps.return_value = 0.0
    conteo = {"verde": 7, "defecto": 2}
    servicio.tracker.obtener_conteo.side_effect = lambda: dict(conteo)
    servicio.tracker.resetear_conteo.side_effect = conteo.clear
    with patch("src.services.tracker_service.arduino_serial"), \
         patch("src.services.tracker_service.registro_eventos"), \
         patch("src.services.tracker_service.servo_controller"), \
         patch("src.services.tracker_service.camara_service"), \
         patch.object(servicio, "_loop_procesamiento"), \
         patch("src.services.tracker_service.EvaluacionService") as evaluaciones:
        evaluaciones.return_value.verificar_estado.return_value = "activa"
        evaluaciones.return_value.finalizar_evaluacion.return_value = FinalizarEvaluacionResponse(
            finalizado=True, mensaje="Guardada", evaluacion_id=EVALUACION, codigo="EVA0000001",
            total_buenos=7, total_defectos=2,
        )
        yield servicio
        if servicio._thread:
            servicio.detener()


@pytest.fixture
def api(servicio: TrackerService) -> Iterator[TestClient]:
    from src.routes import evaluacion, video

    app = FastAPI()
    app.include_router(video.video_router)
    app.include_router(evaluacion.evaluacion_router, prefix="/evaluacion")
    app.dependency_overrides[obtener_usuario_actual] = lambda: {
        "personal_id": EVALUACION, "tipo_personal_id": 1, "usuario": "evaluador",
    }
    with patch.object(video, "tracker_service", servicio), \
         patch.object(evaluacion, "tracker_service", servicio), \
         patch.object(evaluacion, "auditoria_service"), TestClient(app) as cliente:
        yield cliente


@pytest.mark.parametrize("accion", ["detener", "resetear"])
@pytest.mark.parametrize("activo", [True, False])
@pytest.mark.parametrize("rol,identificador,error", [
    (1, None, ValueError),
    (2, None, ValueError),
    (3, None, ValueError),
    (1, OTRA_EVALUACION, ValueError),
    (2, EVALUACION, PermissionError),
    (3, EVALUACION, PermissionError),
])
def test_rechazo_conserva_el_lote(
    servicio: TrackerService, accion: str, activo: bool,
    rol: int, identificador: str | None, error: type[Exception],
) -> None:
    servicio.activo = activo
    with pytest.raises(error):
        servicio.controlar_lote(accion, identificador, rol)
    assert servicio.activo is activo
    assert servicio.evaluacion_id == EVALUACION
    assert servicio.obtener_conteo_actual() == {"verde": 7, "defecto": 2}
    assert servicio._frame_anotado == b"frame original"
    servicio.tracker.resetear_conteo.assert_not_called()


def test_evaluador_detiene_sin_perder_el_conteo_para_finalizar(servicio: TrackerService) -> None:
    servicio.controlar_lote("detener", EVALUACION, 1)
    assert servicio.activo is False
    assert servicio.evaluacion_id == EVALUACION
    conteo = servicio.conteo_de_evaluacion(EVALUACION)
    assert conteo["total_granos"] == 9
    assert conteo["total_defectos"] == 2
    assert conteo["total_sanos"] == 7


def test_evaluador_puede_resetear_su_lote(servicio: TrackerService) -> None:
    assert servicio.controlar_lote("resetear", EVALUACION, 1) == {}
    assert servicio.evaluacion_id == EVALUACION


@pytest.mark.parametrize("rol", [1, 2, 3])
@pytest.mark.parametrize("accion", ["detener", "resetear"])
def test_prueba_sin_evaluacion_disponible_para_toda_sesion(
    servicio: TrackerService, rol: int, accion: str,
) -> None:
    servicio.finalizar_evaluacion(EVALUACION)
    assert servicio.evaluacion_id is None
    assert servicio.iniciar(None, rol)
    servicio.controlar_lote(accion, None, rol)
    if accion == "detener":
        assert servicio.activo is False
    else:
        assert servicio.obtener_conteo_actual() == {}


@pytest.mark.parametrize("accion", ["detener", "resetear"])
def test_nuevo_arranque_espera_hasta_terminar_el_control(
    servicio: TrackerService, accion: str,
) -> None:
    entrada = threading.Event()
    liberar = threading.Event()
    arranque = threading.Event()
    metodo = servicio.detener if accion == "detener" else servicio.resetear_lote

    def controlar_con_espera() -> None:
        entrada.set()
        assert liberar.wait(3)
        metodo()

    def iniciar_otro_lote() -> bool:
        arranque.set()
        return servicio.iniciar(EVALUACION, 1)

    with patch.object(servicio, "detener" if accion == "detener" else "resetear_lote", side_effect=controlar_con_espera), \
         patch.object(servicio, "_loop_procesamiento"):
        with ThreadPoolExecutor(max_workers=2) as pool:
            control = pool.submit(servicio.controlar_lote, accion, EVALUACION, 1)
            assert entrada.wait(3)
            inicio = pool.submit(iniciar_otro_lote)
            try:
                assert arranque.wait(3)
                assert not inicio.done()
                assert servicio.evaluacion_id == EVALUACION
            finally:
                liberar.set()
            control.result(timeout=3)
            assert inicio.result(timeout=3)


@pytest.mark.parametrize("rol", [1, 2, 3])
@pytest.mark.parametrize("detener", [False, True])
def test_iniciar_sin_id_rechaza_lote_pendiente_sin_perder_conteo(
    api: TestClient, servicio: TrackerService, rol: int, detener: bool,
) -> None:
    if detener:
        servicio.controlar_lote("detener", EVALUACION, 1)
    api.app.dependency_overrides[obtener_usuario_actual] = lambda: {"tipo_personal_id": rol}
    respuesta = api.post("/video/iniciar")
    assert respuesta.status_code == 409
    assert servicio.evaluacion_id == EVALUACION
    assert servicio.activo is not detener
    assert servicio.conteo_de_evaluacion(EVALUACION)["total_granos"] == 9
    servicio.tracker.resetear_conteo.assert_not_called()


def test_reanudar_misma_evaluacion_conserva_conteo_y_asociacion(servicio: TrackerService) -> None:
    servicio.controlar_lote("detener", EVALUACION, 1)
    assert servicio.iniciar(EVALUACION, 1)
    assert servicio.evaluacion_id == EVALUACION
    assert servicio.conteo_de_evaluacion(EVALUACION)["total_granos"] == 9
    servicio.tracker.resetear_conteo.assert_not_called()


@pytest.mark.parametrize("rol", [2, 3])
def test_mismo_id_no_permite_iniciar_a_otro_rol(
    api: TestClient, servicio: TrackerService, rol: int,
) -> None:
    servicio.controlar_lote("detener", EVALUACION, 1)
    api.app.dependency_overrides[obtener_usuario_actual] = lambda: {"tipo_personal_id": rol}
    assert api.post("/video/iniciar", json={"evaluacion_id": EVALUACION}).status_code == 403
    assert servicio.conteo_de_evaluacion(EVALUACION)["total_granos"] == 9


def test_finalizar_libera_asociacion_y_prueba_funciona(api: TestClient, servicio: TrackerService) -> None:
    servicio.controlar_lote("detener", EVALUACION, 1)
    assert api.patch(f"/evaluacion/{EVALUACION}/finalizar", json={}).status_code == 200
    assert servicio.evaluacion_id is None
    assert api.get("/video/status").json()["evaluacion_id"] is None
    assert api.post("/video/iniciar").status_code == 200
    assert api.post("/video/lote/resetear").status_code == 200
    assert api.post("/video/detener").status_code == 200
    assert servicio.evaluacion_id is None


def test_fallo_al_persistir_no_libera_ni_pierde_conteo(servicio: TrackerService) -> None:
    with patch("src.services.tracker_service.EvaluacionService") as evaluaciones:
        evaluaciones.return_value.finalizar_evaluacion.side_effect = RuntimeError("Fallo de BD")
        with pytest.raises(RuntimeError, match="Fallo de BD"):
            servicio.finalizar_evaluacion(EVALUACION)
    assert servicio.evaluacion_id == EVALUACION
    assert servicio.conteo_de_evaluacion(EVALUACION)["total_granos"] == 9


def test_evaluador_puede_descartar_lote_abandonado_y_empezar_otro(
    api: TestClient, servicio: TrackerService,
) -> None:
    respuesta = api.post("/video/detener", json={"evaluacion_id": EVALUACION, "descartar_lote": True})
    assert respuesta.status_code == 200
    assert servicio.activo is False
    assert servicio.evaluacion_id is None
    assert servicio.obtener_conteo_actual() == {}
    assert api.post("/video/iniciar", json={"evaluacion_id": OTRA_EVALUACION}).status_code == 200
    assert servicio.evaluacion_id == OTRA_EVALUACION


@pytest.mark.parametrize("rol", [2, 3])
def test_descartar_lote_abandonado_exige_evaluador(
    api: TestClient, servicio: TrackerService, rol: int,
) -> None:
    api.app.dependency_overrides[obtener_usuario_actual] = lambda: {"tipo_personal_id": rol}
    assert api.post("/video/detener", json={"evaluacion_id": EVALUACION, "descartar_lote": True}).status_code == 403
    assert servicio.conteo_de_evaluacion(EVALUACION)["total_granos"] == 9
    assert servicio.activo is True


def test_prueba_activa_no_es_adoptada_como_evaluacion(api: TestClient, servicio: TrackerService) -> None:
    servicio.finalizar_evaluacion(EVALUACION)
    assert servicio.iniciar()
    servicio.tracker.resetear_conteo.reset_mock()
    assert api.post("/video/iniciar", json={"evaluacion_id": OTRA_EVALUACION}).status_code == 409
    assert servicio.evaluacion_id is None
    servicio.tracker.resetear_conteo.assert_not_called()


def test_reintento_finalizado_no_libera_otro_lote(servicio: TrackerService) -> None:
    servicio.finalizar_evaluacion(EVALUACION)
    assert servicio.iniciar(OTRA_EVALUACION, 1)
    with patch("src.services.tracker_service.EvaluacionService") as evaluaciones:
        evaluaciones.return_value.verificar_estado.return_value = "finalizada"
        evaluaciones.return_value.finalizar_evaluacion.return_value = FinalizarEvaluacionResponse(
            finalizado=True, mensaje="Ya guardada", evaluacion_id=EVALUACION,
            codigo="EVA0000001", ya_finalizada=True,
        )
        assert servicio.finalizar_evaluacion(EVALUACION).ya_finalizada
        evaluaciones.return_value.finalizar_evaluacion.assert_called_once_with(EVALUACION, {}, None)
    assert servicio.evaluacion_id == OTRA_EVALUACION
    assert servicio.activo is True


@pytest.mark.parametrize("fallar", [False, True])
def test_inicio_espera_a_finalizacion_y_respeta_su_resultado(
    servicio: TrackerService, fallar: bool,
) -> None:
    entrada = threading.Event()
    liberar = threading.Event()
    arranque = threading.Event()
    with patch("src.services.tracker_service.EvaluacionService") as evaluaciones:
        def persistir(*args: object) -> FinalizarEvaluacionResponse:
            entrada.set()
            assert liberar.wait(3)
            if fallar:
                raise RuntimeError("Fallo al guardar")
            return FinalizarEvaluacionResponse(
                finalizado=True, mensaje="Guardada", evaluacion_id=EVALUACION, codigo="EVA0000001",
            )

        def iniciar_prueba() -> bool:
            arranque.set()
            return servicio.iniciar()

        evaluaciones.return_value.finalizar_evaluacion.side_effect = persistir
        with ThreadPoolExecutor(max_workers=2) as pool:
            finalizacion = pool.submit(servicio.finalizar_evaluacion, EVALUACION)
            assert entrada.wait(3)
            inicio = pool.submit(iniciar_prueba)
            try:
                assert arranque.wait(3)
                assert not inicio.done()
                assert servicio.evaluacion_id == EVALUACION
            finally:
                liberar.set()
            if fallar:
                with pytest.raises(RuntimeError):
                    finalizacion.result(timeout=3)
                with pytest.raises(ValueError):
                    inicio.result(timeout=3)
                assert servicio.conteo_de_evaluacion(EVALUACION)["total_granos"] == 9
            else:
                assert finalizacion.result(timeout=3).finalizado
                assert inicio.result(timeout=3)
                assert servicio.evaluacion_id is None
