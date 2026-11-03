"""
Rutas para streaming de video y análisis de defectos en tiempo real.
GET  /video/stream         → MJPEG streaming del monitoreo en vivo
POST /video/iniciar        → Inicia captura y procesamiento
POST /video/detener        → Detiene captura
GET  /video/eventos        → Eventos del lote para el panel de monitoreo
GET  /lote/conteo          → Conteo actual de granos por clase
POST /lote/generar-reporte → Genera reporte final del lote
POST /lote/resetear        → Resetea conteo para nuevo lote
"""

import asyncio

from fastapi import APIRouter, Depends, Query, Response, HTTPException
from fastapi.responses import StreamingResponse

from src.schemas.video import ControlMonitoreoRequest, DetenerMonitoreoRequest, EventosMonitoreoResponse
from src.services.tracker_service import tracker_service
from src.utilities.jwt_required import obtener_usuario_actual, require_evaluador

video_router = APIRouter(prefix="/video", tags=["video"])


@video_router.get("/stream")
async def stream_mjpeg(_: dict = Depends(obtener_usuario_actual)) -> StreamingResponse:
    """
    Streaming MJPEG del monitoreo en vivo.
    Retorna un stream de frames anotados (defectos en ROJO, estadísticas en tiempo real).

    Returns:
        StreamingResponse: MJPEG stream (multipart/x-mixed-replace)
    """
    async def frame_generator():
        """Genera frames JPEG en formato MJPEG."""
        while tracker_service.esta_activo():
            frame_jpeg = tracker_service.obtener_frame_streaming()
            if frame_jpeg is None:
                await asyncio.sleep(0.033)
                continue

            # Boundary MJPEG
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n"
                b"Content-Length: " + str(len(frame_jpeg)).encode() + b"\r\n\r\n"
                + frame_jpeg + b"\r\n"
            )
            await asyncio.sleep(0.033)  # ~30fps al cliente

    return StreamingResponse(
        frame_generator(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


# ============================================================
# RUTAS DE CONTROL
# ============================================================

@video_router.post("/iniciar")
def iniciar_captura(
    payload: ControlMonitoreoRequest | None = None,
    usuario: dict = Depends(obtener_usuario_actual),
) -> dict:
    """
    Inicia la captura de video y procesamiento en tiempo real.

    El id de evaluación llega para asociarle los eventos y las evidencias del
    lote; sin él el monitoreo corre igual, pero no se archiva nada.

    Returns:
        dict: {mensaje, activo}
    """
    try:
        exito = tracker_service.iniciar(
            payload.evaluacion_id if payload else None, usuario.get("tipo_personal_id", 0)
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudo iniciar el monitoreo.") from exc

    if not exito:
        raise HTTPException(status_code=500, detail="No se pudo iniciar la cámara.")

    return {
        "mensaje": "Monitoreo iniciado exitosamente",
        "activo": True
    }


@video_router.post("/detener")
def detener_captura(
    payload: DetenerMonitoreoRequest | None = None,
    usuario: dict = Depends(obtener_usuario_actual),
) -> dict:
    """Detiene la captura y streaming de video."""
    try:
        tracker_service.controlar_lote(
            "detener", payload.evaluacion_id if payload else None, usuario.get("tipo_personal_id", 0),
            descartar_lote=payload.descartar_lote if payload else False,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return {
        "mensaje": "Monitoreo detenido",
        "activo": False
    }


# ============================================================
# RUTAS DE ANÁLISIS DE LOTES
# ============================================================

@video_router.get("/eventos", response_model=EventosMonitoreoResponse)
def obtener_eventos_monitoreo(
    desde: int = Query(0, ge=0),
    _: dict = Depends(obtener_usuario_actual),
) -> dict:
    """Eventos del lote con seq mayor a `desde`, para el registro del monitoreo."""
    return tracker_service.obtener_eventos(desde)


@video_router.get("/lote/conteo")
def obtener_conteo_lote(_: dict = Depends(obtener_usuario_actual)) -> dict:
    return tracker_service.obtener_conteo_enriquecido()


@video_router.post("/lote/generar-reporte")
def generar_reporte_lote(_: dict = Depends(require_evaluador)) -> dict:
    """
    Genera el reporte final del lote actual.

    """
    try:
        return tracker_service.generar_reporte_lote()
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="No se pudo generar el reporte del lote.",
        ) from exc


@video_router.post("/lote/resetear")
def resetear_lote(
    payload: ControlMonitoreoRequest | None = None,
    usuario: dict = Depends(obtener_usuario_actual),
) -> dict:
    """
    Resetea el conteo de granos para iniciar análisis de un nuevo lote.

    Returns:
        dict: {mensaje, conteo}
    """
    try:
        conteo = tracker_service.controlar_lote(
            "resetear", payload.evaluacion_id if payload else None, usuario.get("tipo_personal_id", 0)
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    return {
        "mensaje": "Lote reseteado. Listo para nuevo análisis.",
        "conteo": conteo
    }


# ============================================================
# RUTAS DE STATUS
# ============================================================

@video_router.get("/frame")
def obtener_frame(_: dict = Depends(obtener_usuario_actual)) -> Response:
    """
    Retorna el último frame procesado como JPEG individual.
    Usado para refrescar continuamente la imagen en el frontend.
    """
    frame_jpeg = tracker_service.obtener_frame_streaming()
    if frame_jpeg is None:
        raise HTTPException(status_code=503, detail="Todavía no hay ninguna imagen disponible.")

    return Response(
        content=frame_jpeg,
        media_type="image/jpeg"
    )


@video_router.get("/status")
def obtener_status(_: dict = Depends(obtener_usuario_actual)) -> dict:
    """Retorna el estado actual del sistema de monitoreo, incluyendo errores de cámara."""
    estado_error = tracker_service.obtener_estado_error()
    return {
        "activo": tracker_service.esta_activo(),
        "modelo": tracker_service.model_name,
        "fps": tracker_service.obtener_fps(),
        "conteo_actual": tracker_service.obtener_conteo_actual(),
        # Evaluación dueña del lote en curso: el monitoreo lo compara con la suya
        # para no adoptar un lote que quedó activo de otra evaluación.
        "evaluacion_id": tracker_service.evaluacion_id,
        "camara_desconectada": estado_error["camara_desconectada"],
        "error": estado_error["error"],
    }

