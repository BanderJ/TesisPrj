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

from src.schemas.video import EventosMonitoreoResponse, IniciarMonitoreoRequest
from src.services.tracker_service import tracker_service
from src.utilities.jwt_required import obtener_usuario_actual

video_router = APIRouter(prefix="/video", tags=["video"])


@video_router.get("/stream")
async def stream_mjpeg():
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
# RUTAS DE CONTROL (requieren autenticación)
# ============================================================

@video_router.post("/iniciar")
async def iniciar_captura(
    payload: IniciarMonitoreoRequest | None = None,
    _: dict = Depends(obtener_usuario_actual),
) -> dict:
    """
    Inicia la captura de video y procesamiento en tiempo real.

    El id de evaluación llega para asociarle los eventos y las evidencias del
    lote; sin él el monitoreo corre igual, pero no se archiva nada.

    Returns:
        dict: {mensaje, activo}
    """
    if tracker_service.esta_activo():
        return {
            "mensaje": "El monitoreo ya está activo",
            "activo": True
        }

    try:
        exito = tracker_service.iniciar(payload.evaluacion_id if payload else None)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudo iniciar el monitoreo.") from exc

    if not exito:
        raise HTTPException(status_code=500, detail="No se pudo iniciar la cámara.")

    return {
        "mensaje": "Monitoreo iniciado exitosamente",
        "activo": True
    }


@video_router.post("/detener")
async def detener_captura(_: dict = Depends(obtener_usuario_actual)):
    """Detiene la captura y streaming de video."""
    tracker_service.detener()
    return {
        "mensaje": "Monitoreo detenido",
        "activo": False
    }


# ============================================================
# RUTAS DE ANÁLISIS DE LOTES
# ============================================================

@video_router.get("/eventos", response_model=EventosMonitoreoResponse)
async def obtener_eventos_monitoreo(
    desde: int = Query(0, ge=0),
    _: dict = Depends(obtener_usuario_actual),
) -> dict:
    """Eventos del lote con seq mayor a `desde`, para el registro del monitoreo."""
    return tracker_service.obtener_eventos(desde)


@video_router.get("/lote/conteo")
async def obtener_conteo_lote(_: dict = Depends(obtener_usuario_actual)):
    return tracker_service.obtener_conteo_enriquecido()


@video_router.post("/lote/generar-reporte")
async def generar_reporte_lote(_: dict = Depends(obtener_usuario_actual)) -> dict:
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
async def resetear_lote(_: dict = Depends(obtener_usuario_actual)):
    """
    Resetea el conteo de granos para iniciar análisis de un nuevo lote.

    Returns:
        dict: {mensaje, conteo}
    """
    tracker_service.resetear_lote()

    return {
        "mensaje": "Lote reseteado. Listo para nuevo análisis.",
        "conteo": tracker_service.obtener_conteo_actual()
    }


# ============================================================
# RUTAS DE STATUS
# ============================================================

@video_router.get("/frame")
async def obtener_frame():
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
async def obtener_status():
    """Retorna el estado actual del sistema de monitoreo, incluyendo errores de cámara."""
    estado_error = tracker_service.obtener_estado_error()
    return {
        "activo": tracker_service.esta_activo(),
        "modelo": tracker_service.model_name,
        "conteo_actual": tracker_service.obtener_conteo_actual(),
        # Evaluación dueña del lote en curso: el monitoreo lo compara con la suya
        # para no adoptar un lote que quedó activo de otra evaluación.
        "evaluacion_id": tracker_service.evaluacion_id,
        "camara_desconectada": estado_error["camara_desconectada"],
        "error": estado_error["error"],
    }

