import os
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import Depends, FastAPI, Request, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.routes.auth_login import auth as auth_router
from src.routes.caficultor import caficultor_router
from src.routes.tipo_caficultor import tipo_caficultor_router
from src.routes.tipo_documento import tipo_documento_router
from src.routes.tipo_personal import tipo_personal_router
from src.routes.valor_cafe import valor_cafe_router
from src.utilities.jwt_required import RequerirLoginException, obtener_usuario_actual


# ==================== CICLO DE VIDA ====================

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:  # noqa: ARG001
    del app  # required by the lifespan protocol; unused at runtime
    print("Application has started successfully!")
    yield
    print("Application is shutting down...")


# ==================== APLICACIÓN ====================

app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="src/static"), name="static")
app.mount("/resources", StaticFiles(directory="src/resources"), name="resources")

templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_dir)


# ==================== MANEJO DE EXCEPCIONES ====================

@app.exception_handler(RequerirLoginException)
async def auth_exception_handler(request: Request, exc: RequerirLoginException) -> RedirectResponse:
    return RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)


# ==================== RUTAS ====================

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(caficultor_router, prefix="/caficultor", tags=["caficultor"])
app.include_router(tipo_caficultor_router, prefix="/tipo-caficultor", tags=["tipo-caficultor"])
app.include_router(tipo_documento_router, prefix="/tipo-documento", tags=["tipo-documento"])
app.include_router(tipo_personal_router, prefix="/tipo-personal", tags=["tipo-personal"])
app.include_router(valor_cafe_router, prefix="/valor-cafe", tags=["valor-cafe"])


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


@app.get("/monitoreo")
async def monitoreo(request: Request, user: dict[str, Any] = Depends(obtener_usuario_actual)) -> Any:
    """Página de monitoreo en tiempo real de clasificación."""
    return templates.TemplateResponse(
        request=request,
        name="monitoreo.html",
        context={"request": request, "user": user},
    )


@app.get("/nuevo-caficultor")
@app.get("/registro-socios")
async def nuevo_caficultor(request: Request, user: dict[str, Any] = Depends(obtener_usuario_actual)) -> Any:
    """Pantalla de registro y conversion de caficultores."""
    return templates.TemplateResponse(
        request=request,
        name="nuevo_caficultor.html",
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
