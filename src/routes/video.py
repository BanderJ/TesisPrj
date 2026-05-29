"""
Rutas para streaming de video y análisis de defectos en tiempo real.
GET  /video/stream         → MJPEG streaming del monitoreo en vivo
POST /video/iniciar        → Inicia captura y procesamiento
POST /video/detener        → Detiene captura
GET  /lote/conteo          → Conteo actual de granos por clase
POST /lote/generar-reporte → Genera reporte final del lote
POST /lote/resetear        → Resetea conteo para nuevo lote
"""

from fastapi import APIRouter, Depends, Response, HTTPException
from fastapi.responses import StreamingResponse

from src.services.tracker_service import tracker_service
from src.utilities.jwt_required import obtener_usuario_actual

router = APIRouter(prefix="/video", tags=["video"])


@router.get("/stream")
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
                continue

            # Boundary MJPEG
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n"
                b"Content-Length: " + str(len(frame_jpeg)).encode() + b"\r\n\r\n"
                + frame_jpeg + b"\r\n"
            )

    return StreamingResponse(
        frame_generator(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


# ============================================================
# RUTAS DE CONTROL (requieren autenticación)
# ============================================================

@router.post("/iniciar")
async def iniciar_captura(usuario_actual: dict = Depends(obtener_usuario_actual)):
    """
    Inicia la captura de video y procesamiento en tiempo real.

    Returns:
        dict: {mensaje, activo}
    """
    if tracker_service.esta_activo():
        return {
            "mensaje": "El monitoreo ya está activo",
            "activo": True
        }

    try:
        exito = tracker_service.iniciar()
        if not exito:
            raise HTTPException(status_code=500, detail="No se pudo iniciar la cámara")

        return {
            "mensaje": "Monitoreo iniciado exitosamente",
            "activo": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al iniciar: {str(e)}")


@router.post("/detener")
async def detener_captura(usuario_actual: dict = Depends(obtener_usuario_actual)):
    """Detiene la captura y streaming de video."""
    tracker_service.detener()
    return {
        "mensaje": "Monitoreo detenido",
        "activo": False
    }


# ============================================================
# RUTAS DE ANÁLISIS DE LOTES
# ============================================================

@router.get("/lote/conteo")
async def obtener_conteo_lote(usuario_actual: dict = Depends(obtener_usuario_actual)):
    """
    Retorna el conteo actual de granos detectados por clase.

    Returns:
        dict: {clase: cantidad_granos_unicos, total: int}
    """
    conteo = tracker_service.obtener_conteo_actual()

    return {
        "conteo": conteo,
        "total_granos": sum(conteo.values()),
        "clases_detectadas": len(conteo)
    }


@router.post("/lote/generar-reporte")
async def generar_reporte_lote(usuario_actual: dict = Depends(obtener_usuario_actual)):
    """
    Genera el reporte final del lote actual.

    Calcula:
    - Total de granos analizados
    - Total de defectos equivalentes (SCA)
    - Grado (1, 2 o 3)
    - Apto para Specialty (bool)
    - Detalle por clase de defecto

    Returns:
        dict: {grado, defectos, apto_specialty, detalle_por_clase, resumen}
    """
    try:
        reporte = tracker_service.generar_reporte_lote()
        return reporte
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generando reporte: {str(e)}"
        )


@router.post("/lote/resetear")
async def resetear_lote(usuario_actual: dict = Depends(obtener_usuario_actual)):
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

@router.get("/frame")
async def obtener_frame():
    """
    Retorna el último frame procesado como JPEG individual.
    Usado para refrescar continuamente la imagen en el frontend.
    """
    frame_jpeg = tracker_service.obtener_frame_streaming()
    if frame_jpeg is None:
        raise HTTPException(status_code=503, detail="No hay frame disponible")

    return Response(
        content=frame_jpeg,
        media_type="image/jpeg"
    )


@router.get("/status")
async def obtener_status():
    """Retorna el estado actual del sistema de monitoreo, incluyendo errores de cámara."""
    estado_error = tracker_service.obtener_estado_error()
    return {
        "activo": tracker_service.esta_activo(),
        "modelo": tracker_service.model_name,
        "conteo_actual": tracker_service.obtener_conteo_actual(),
        "camara_desconectada": estado_error["camara_desconectada"],
        "error": estado_error["error"],
    }


@router.post("/liberar-camara")
async def liberar_camara(usuario_actual: dict = Depends(obtener_usuario_actual)):
    """Fuerza la liberación de la cámara (útil si está bloqueada)."""
    tracker_service.detener()
    return {"mensaje": "Cámara liberada"}

