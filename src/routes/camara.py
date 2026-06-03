import asyncio
from typing import Any, AsyncGenerator

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, StreamingResponse

from src.services.camara_service import CamaraService, camara_service
from src.utilities.jwt_required import obtener_usuario_actual

camara_router = APIRouter()


async def _generar_frames(service: CamaraService) -> AsyncGenerator[bytes, None]:
    loop = asyncio.get_running_loop()
    while service.esta_disponible():
        # run_in_executor delega el bloqueo al thread pool sin paralizar el event loop
        frame = await loop.run_in_executor(None, service.esperar_frame, 1.0)
        if frame is None:
            continue  # timeout de 1 s: verifica disponibilidad y vuelve a esperar
        yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"


@camara_router.get("/stream", response_model=None)
async def stream_camara(user: dict[str, Any] = Depends(obtener_usuario_actual)) -> StreamingResponse | JSONResponse:
    if not camara_service.esta_disponible():
        if not camara_service.iniciar():
            return JSONResponse({"detail": "Cámara no disponible"}, status_code=503)
    return StreamingResponse(
        _generar_frames(camara_service),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


@camara_router.get("/estado")
async def estado_camara(user: dict[str, Any] = Depends(obtener_usuario_actual)) -> dict[str, bool]:
    disponible = camara_service.esta_disponible()
    if not disponible:
        disponible = camara_service.iniciar()
    return {"disponible": disponible}
