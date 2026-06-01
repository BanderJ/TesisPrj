from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, JSONResponse
from src.schemas.auth import LoginRequest, LoginResponse
from src.services.auth_service import AuthService
import os

# ==================== CONFIGURACIÓN ====================
# Configurar Jinja2Templates
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "../templates"))

auth = APIRouter()
auth_service = AuthService()


# ==================== ENDPOINTS HTML (Formularios) ====================
@auth.get("/login")
async def login_get(request: Request):
    """
    GET /auth/login
    Retorna la página HTML del formulario de login
    """
    # Evitar múltiples inicios de sesión si la ruta es visitada de nuevo manualmente
    token = request.cookies.get("access_token")
    if auth_service.sesion_activa(token):
        return RedirectResponse(url="/", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"request": request},
    )

@auth.post("/login")
async def login_post(request: Request, usuario: str = Form(...), clave: str = Form(...)):
    """
    POST /auth/login (Formulario HTML)
    Procesa login desde formulario HTML
    """
    # Evitar que se intente loguear si ya tiene sesión iniciada
    token = request.cookies.get("access_token")
    if auth_service.sesion_activa(token):
        return RedirectResponse(url="/", status_code=303)

    login_response = auth_service.autenticar(usuario, clave)

    if login_response:
        # Redirigir y configurar la cookie JWT
        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie(key="access_token", value=login_response.token, httponly=True)
        return response

    # Si las credenciales son incorrectas
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"request": request, "error": "Credenciales incorrectas, intenta nuevamente."},
    )

@auth.get("/logout")
async def logout(request: Request):
    """
    GET /auth/logout
    Cierra sesión eliminando la cookie JWT y redirige a login.
    """
    response = RedirectResponse(url="/auth/login", status_code=303)
    response.delete_cookie("access_token")
    return response

# ==================== ENDPOINTS API JSON (Para Postman/Bruno) ====================
@auth.post("/api/login", response_model=LoginResponse)
async def login_api(credentials: LoginRequest):
    """
    POST /auth/api/login
    Endpoint para probar con Postman/Bruno

    Body (JSON):
    {
        "usuario": "admin",
        "clave": "password123"
    }
    """
    login_response = auth_service.autenticar(credentials.usuario, credentials.clave)

    if not login_response:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    # Return JSON response with httponly cookie
    response = JSONResponse(content=login_response.dict())
    response.set_cookie(key="access_token", value=login_response.token, httponly=True)
    return response

