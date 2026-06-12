import os
import re
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import Depends, FastAPI, Request, status
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.routes.arduino import arduino_router
from src.routes.auth_login import auth as auth_router
from src.routes.caficultor import caficultor_router
from src.routes.camara import camara_router
from src.routes.cooperativa import router as cooperativa_router
from src.routes.evaluacion import evaluacion_router
from src.routes.dni import dni_router
from src.routes.perfil import perfil
from src.routes.persona import persona_router
from src.routes.tipo_caficultor import tipo_caficultor_router
from src.routes.tipo_documento import tipo_documento_router
from src.routes.tipo_grano import tipo_grano_router
from src.routes.tipo_personal import tipo_personal_router
from src.routes.ubigeo import ubigeo_router
from src.routes.valor_cafe import valor_cafe_router
from src.routes.video import video_router
from src.services.camara_service import camara_service
from src.services.tracker_service import tracker_service
from src.utilities.arduino_serial import arduino_serial
from src.utilities.servo_controller import servo_controller
from src.services.evaluacion_service import EvaluacionService
from src.utilities.jwt_required import RequerirLoginException, obtener_usuario_actual

_UUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
_evaluacion_service = EvaluacionService()


# ==================== CICLO DE VIDA ====================

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:  # noqa: ARG001
    del app  # required by the lifespan protocol; unused at runtime
    camara_service.iniciar()  # pre-conectar cámara al arrancar
    print("Application has started successfully!")
    yield
    tracker_service.detener()
    arduino_serial.enviar_comando("OFF")  # asegurar faja apagada al cerrar app
    camara_service.cerrar()
    servo_controller.cerrar()
    arduino_serial.cerrar()
    print("Application is shutting down...")


# ==================== APLICACIÓN ====================

app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="src/static"), name="static")
app.mount("/resources", StaticFiles(directory="src/resources"), name="resources")

templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_dir)


# ==================== MANEJO DE EXCEPCIONES ====================

@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse('src/static/icon/coffee-bean_icon.png')

@app.exception_handler(RequerirLoginException)
async def auth_exception_handler(request: Request, exc: RequerirLoginException) -> RedirectResponse:
    return RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)


# ==================== RUTAS ====================

app.include_router(arduino_router)
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(caficultor_router, prefix="/caficultor", tags=["caficultor"])
app.include_router(camara_router, prefix="/camara", tags=["camara"])
app.include_router(cooperativa_router)
app.include_router(evaluacion_router, prefix="/evaluacion", tags=["evaluacion"])
app.include_router(dni_router, prefix="/dni", tags=["dni"])
app.include_router(perfil, prefix="/perfil", tags=["perfil"])
app.include_router(persona_router, prefix="/persona", tags=["persona"])
app.include_router(tipo_caficultor_router, prefix="/tipo-caficultor", tags=["tipo-caficultor"])
app.include_router(tipo_documento_router, prefix="/tipo-documento", tags=["tipo-documento"])
app.include_router(tipo_grano_router, prefix="/tipo-grano", tags=["tipo-grano"])
app.include_router(tipo_personal_router, prefix="/tipo-personal", tags=["tipo-personal"])
app.include_router(ubigeo_router, prefix="/ubigeo", tags=["ubigeo"])
app.include_router(valor_cafe_router, prefix="/valor-cafe", tags=["valor-cafe"])
app.include_router(video_router)  # Video streaming y análisis ML


@app.get("/")
@app.get("/inicio")
async def inicio(request: Request, user: dict[str, Any] = Depends(obtener_usuario_actual)) -> Any:
    """Página de inicio del sistema."""
    return templates.TemplateResponse(
        request=request,
        name="inicio.html",
        context={"request": request, "user": user},
    )


@app.get("/registro")
async def registro(request: Request, user: dict[str, Any] = Depends(obtener_usuario_actual)) -> Any:
    """Página de registro de muestras."""
    return templates.TemplateResponse(
        request=request,
        name="registro.html",
        context={"request": request, "user": user},
    )


@app.get("/analisis/{evaluacion_id}")
async def analisis(
    evaluacion_id: str,
    request: Request,
    user: dict[str, Any] = Depends(obtener_usuario_actual),
) -> Any:
    """Página de resumen estadístico del análisis finalizado.
    Guard: solo accesible si la evaluacion tiene codigo asignado (finalizada).
    """
    if not _UUID_RE.match(evaluacion_id):
        return RedirectResponse(url="/registro", status_code=status.HTTP_303_SEE_OTHER)
    estado = _evaluacion_service.verificar_estado(evaluacion_id)
    if estado is None:
        return RedirectResponse(url="/registro", status_code=status.HTTP_303_SEE_OTHER)
    if estado == "activa":
        return RedirectResponse(
            url=f"/monitoreo/{evaluacion_id}", status_code=status.HTTP_303_SEE_OTHER
        )
    response = templates.TemplateResponse(
        request=request,
        name="analisis.html",
        context={"request": request, "user": user, "evaluacion_id": evaluacion_id},
    )
    response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/monitoreo/{evaluacion_id}")
async def monitoreo(
    evaluacion_id: str,
    request: Request,
    user: dict[str, Any] = Depends(obtener_usuario_actual),
) -> Any:
    """Página de monitoreo en tiempo real de clasificación.
    Guard: si la evaluacion ya fue finalizada (tiene codigo), redirige a analisis.
    Si el UUID no existe, redirige a registro.
    """
    if not _UUID_RE.match(evaluacion_id):
        return RedirectResponse(url="/registro", status_code=status.HTTP_303_SEE_OTHER)
    estado = _evaluacion_service.verificar_estado(evaluacion_id)
    if estado is None:
        return RedirectResponse(url="/registro", status_code=status.HTTP_303_SEE_OTHER)
    if estado == "finalizada":
        return RedirectResponse(
            url=f"/analisis/{evaluacion_id}", status_code=status.HTTP_303_SEE_OTHER
        )
    response = templates.TemplateResponse(
        request=request,
        name="monitoreo.html",
        context={"request": request, "user": user, "evaluacion_id": evaluacion_id},
    )
    response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/nuevo-caficultor")
@app.get("/registro-socios")
async def nuevo_caficultor(request: Request, user: dict[str, Any] = Depends(obtener_usuario_actual)) -> Any:
    """Pantalla de registro y conversion de caficultores."""
    return templates.TemplateResponse(
        request=request,
        name="nuevo_caficultor.html",
        context={"request": request, "user": user},
    )


@app.get("/reporte")
async def reporte(request: Request, user: dict[str, Any] = Depends(obtener_usuario_actual)) -> Any:
    """Página de búsqueda de muestras por código de evaluación."""
    return templates.TemplateResponse(
        request=request,
        name="reporte.html",
        context={"request": request, "user": user},
    )


@app.get("/valor-cafe")
async def valor_cafe(request: Request, user: dict[str, Any] = Depends(obtener_usuario_actual)) -> Any:
    """Pantalla de registro de precios de café. Solo accesible para Gerente y Administrador."""
    return templates.TemplateResponse(
        request=request,
        name="valor_cafe.html",
        context={"request": request, "user": user},
    )


@app.get("/configuracion-cooperativa")
async def configuracion_cooperativa(request: Request, user: dict[str, Any] = Depends(obtener_usuario_actual)) -> Any:
    """Pantalla de configuración de cooperativa."""
    return templates.TemplateResponse(
        request=request,
        name="configuracion_cooperativa.html",
        context={"request": request, "user": user},
    )
