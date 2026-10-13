import os
import re
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import Depends, FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse, FileResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import Response
from starlette.types import Scope

from src.routes.arduino import arduino_router
from src.routes.auditoria import auditoria_router
from src.routes.auth_login import auth as auth_router
from src.routes.caficultor import caficultor_router
from src.routes.cooperativa import router as cooperativa_router
from src.routes.evaluacion import evaluacion_router
from src.routes.dni import dni_router
from src.routes.perfil import perfil
from src.routes.persona import persona_router
from src.routes.reporte import reporte_router
from src.routes.tipo_caficultor import tipo_caficultor_router
from src.routes.tipo_documento import tipo_documento_router
from src.routes.bono_socio import bono_socio_router
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
from src.utilities.jwt_required import (
    RequerirLoginException,
    obtener_usuario_actual,
    require_admin_o_gerente,
)

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


class _NoCacheStaticFiles(StaticFiles):
    """StaticFiles con Cache-Control: no-cache para que el browser siempre revalide.
    Cada request comprueba si el archivo cambió (304 si no cambió → sin descarga).
    Elimina la necesidad de incrementar ?v=N en templates manualmente."""

    async def get_response(self, path: str, scope: Scope) -> Response:
        response = await super().get_response(path, scope)
        response.headers["Cache-Control"] = "no-cache"
        return response


# ==================== APLICACIÓN ====================

app = FastAPI(lifespan=lifespan)

app.mount("/static", _NoCacheStaticFiles(directory="src/static"), name="static")
app.mount("/resources", _NoCacheStaticFiles(directory="src/resources"), name="resources")

templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_dir)


# ==================== MANEJO DE EXCEPCIONES ====================

@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse('src/static/icon/coffee-bean_icon.png')

@app.exception_handler(RequerirLoginException)
async def auth_exception_handler(request: Request, exc: RequerirLoginException) -> RedirectResponse:
    return RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> Response:
    """Navegación del browser: 404 → página HTML, 403 → redirect a inicio.
    Para fetch/API (Accept sin text/html) se mantiene el JSON con el status real."""
    navegacion_html = "text/html" in request.headers.get("accept", "")
    if exc.status_code == status.HTTP_404_NOT_FOUND and navegacion_html:
        return templates.TemplateResponse(
            request=request,
            name="404.html",
            context={"request": request},
            status_code=status.HTTP_404_NOT_FOUND,
        )
    if exc.status_code == status.HTTP_403_FORBIDDEN and navegacion_html:
        # Un rol sin permiso que escribe la URL de una página restringida a mano
        # va a inicio, no ve un JSON de error.
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code, headers=getattr(exc, "headers", None))


def _mensaje_validacion(exc: RequestValidationError) -> str:
    """Aplana el 422 de Pydantic/FastAPI a una sola frase legible en español.

    Sin esto `detail` llega al frontend como una lista de objetos y se renderiza
    como `[object Object]`. Con esto:
      - los mensajes de los validadores del schema (`raise ValueError("...")`)
        se muestran tal cual, sin el prefijo "Value error,";
      - las restricciones nativas de Pydantic (min_length, gt, pattern, ...)
        se traducen a español en vez de mostrar el texto en inglés.
    """
    errores = exc.errors()
    if not errores:
        return "Los datos enviados no son válidos."
    e = errores[0]
    tipo = e.get("type", "")
    ctx = e.get("ctx") or {}
    campo = next(
        (str(p) for p in reversed(e.get("loc", [])) if str(p) not in ("body", "query", "path")),
        None,
    )
    pref = f"{campo}: " if campo else ""

    def _num(v: Any) -> str:
        return str(int(v)) if isinstance(v, float) and v.is_integer() else str(v)

    if tipo == "missing":
        return f"Falta un dato obligatorio: {campo}" if campo else "Los datos enviados no son válidos."
    if tipo == "string_too_short":
        return f"{pref}debe tener al menos {ctx.get('min_length')} caracteres."
    if tipo == "string_too_long":
        return f"{pref}no puede superar los {ctx.get('max_length')} caracteres."
    if tipo == "greater_than":
        return f"{pref}debe ser mayor que {_num(ctx.get('gt'))}."
    if tipo == "greater_than_equal":
        return f"{pref}debe ser mayor o igual a {_num(ctx.get('ge'))}."
    if tipo == "less_than":
        return f"{pref}debe ser menor que {_num(ctx.get('lt'))}."
    if tipo == "less_than_equal":
        return f"{pref}debe ser menor o igual a {_num(ctx.get('le'))}."
    if tipo == "string_pattern_mismatch":
        return f"{pref}el formato no es válido."
    if tipo in ("int_parsing", "int_type", "int_from_float"):
        return f"{pref}debe ser un número entero."
    if tipo in ("float_parsing", "float_type", "decimal_parsing", "decimal_type"):
        return f"{pref}debe ser un número."
    if tipo in ("bool_parsing", "bool_type"):
        return f"{pref}debe ser verdadero o falso."
    if tipo in ("string_type", "string_unicode"):
        return f"{pref}debe ser texto."
    if tipo in ("date_parsing", "date_type", "date_from_datetime_parsing", "datetime_parsing"):
        return f"{pref}la fecha no es válida."
    if tipo == "literal_error":
        return f"{pref}valor no permitido."

    # Validador custom (raise ValueError) o cualquier otro caso: usar el msg ya redactado.
    msg = str(e.get("msg", "")).removeprefix("Value error, ").strip()
    return msg or (f"Dato inválido: {campo}" if campo else "Los datos enviados no son válidos.")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Errores de validación de request → `{"detail": "<frase legible>"}` (422)."""
    return JSONResponse(
        {"detail": _mensaje_validacion(exc)},
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


# ==================== RUTAS ====================


@app.get("/health", tags=["infra"])
async def health() -> dict[str, str]:
    """Health-check de liveness: confirma que el servidor FastAPI arrancó.
    Público a propósito (no depende de obtener_usuario_actual) y sin acceso a
    base de datos, para servir como sonda de arranque del primer incremento."""
    return {"status": "ok", "service": "CoffeeRen"}


app.include_router(arduino_router)
app.include_router(auditoria_router)
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(bono_socio_router, prefix="/bono-socio", tags=["bono-socio"])
app.include_router(caficultor_router, prefix="/caficultor", tags=["caficultor"])
app.include_router(cooperativa_router)
app.include_router(evaluacion_router, prefix="/evaluacion", tags=["evaluacion"])
app.include_router(dni_router, prefix="/dni", tags=["dni"])
app.include_router(perfil, prefix="/perfil", tags=["perfil"])
app.include_router(persona_router, prefix="/persona", tags=["persona"])
app.include_router(reporte_router)
app.include_router(tipo_caficultor_router, prefix="/tipo-caficultor", tags=["tipo-caficultor"])
app.include_router(tipo_documento_router, prefix="/tipo-documento", tags=["tipo-documento"])
app.include_router(tipo_grano_router, prefix="/tipo-grano", tags=["tipo-grano"])
app.include_router(tipo_personal_router, prefix="/tipo-personal", tags=["tipo-personal"])
app.include_router(ubigeo_router, prefix="/ubigeo", tags=["ubigeo"])
app.include_router(valor_cafe_router, prefix="/valor-cafe", tags=["valor-cafe"])
app.include_router(video_router)  # Video streaming y análisis ML


@app.get("/")
async def inicio(request: Request, user: dict[str, Any] = Depends(obtener_usuario_actual)) -> Any:
    """Página de inicio del sistema. URL canónica: `/`."""
    return templates.TemplateResponse(
        request=request,
        name="inicio.html",
        context={"request": request, "user": user},
    )


@app.get("/inicio", include_in_schema=False)
async def inicio_alias(_: dict[str, Any] = Depends(obtener_usuario_actual)) -> RedirectResponse:
    """Alias histórico → redirige a la URL canónica `/` (marcadores viejos).
    307 (temporal): no se cachea de forma permanente en el browser. Mantiene el
    guard de sesión como toda ruta de página (un no autenticado va a login)."""
    return RedirectResponse(url="/", status_code=status.HTTP_307_TEMPORARY_REDIRECT)


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


@app.get("/test")
async def test_deteccion(request: Request, user: dict[str, Any] = Depends(obtener_usuario_actual)) -> Any:
    """Vista de prueba: verificar la cámara y observar la detección del modelo en vivo,
    sin registrar una muestra ni una evaluación. Reutiliza los endpoints /video/*."""
    return templates.TemplateResponse(
        request=request,
        name="test.html",
        context={"request": request, "user": user},
    )


@app.get("/nuevo-caficultor")
async def nuevo_caficultor(request: Request, user: dict[str, Any] = Depends(obtener_usuario_actual)) -> Any:
    """Pantalla de registro y conversion de caficultores."""
    return templates.TemplateResponse(
        request=request,
        name="caficultor.html",
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
async def valor_cafe(request: Request, user: dict[str, Any] = Depends(require_admin_o_gerente)) -> Any:
    """Pantalla de registro de precios de café. Solo Gerente y Administrador —
    un Evaluador que escriba la URL a mano recibe 403 → redirect a `/`."""
    return templates.TemplateResponse(
        request=request,
        name="valor_cafe.html",
        context={"request": request, "user": user},
    )


@app.get("/configuracion-cooperativa")
async def configuracion_cooperativa(request: Request, user: dict[str, Any] = Depends(require_admin_o_gerente)) -> Any:
    """Pantalla de configuración de cooperativa. Solo Gerente y Administrador."""
    return templates.TemplateResponse(
        request=request,
        name="cooperativa.html",
        context={"request": request, "user": user},
    )
