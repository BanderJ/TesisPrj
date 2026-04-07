from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from app.models.personal import Personal
from app.utilities.jwt_utils import generar_token, verificar_token
import os

# ==================== MODELOS PYDANTIC ====================
class LoginRequest(BaseModel):
    """Modelo para validar datos de login en la API"""
    usuario: str
    clave: str

class LoginResponse(BaseModel):
    """Modelo para la respuesta de login exitoso"""
    personal_id: str
    usuario: str
    rol: str
    nombre: str
    token: str

# ==================== CONFIGURACIÓN ====================
# Configurar Jinja2Templates
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "../templates"))

auth = APIRouter()
personal_model = Personal()


# ==================== ENDPOINTS HTML (Formularios) ====================
@auth.get("/login")
async def login_get(request: Request):
    """
    GET /auth/login
    Retorna la página HTML del formulario de login
    """
    # Evitar múltiples inicios de sesión si la ruta es visitada de nuevo manualmente
    token = request.cookies.get("access_token")
    if token and token.startswith("Bearer "):
        if verificar_token(token.split(" ")[1]):
            return RedirectResponse(url="/", status_code=303)

    return templates.TemplateResponse("login.html", {"request": request})

@auth.post("/login")
async def login_post(request: Request, usuario: str = Form(...), clave: str = Form(...)):
    """
    POST /auth/login (Formulario HTML)
    Procesa login desde formulario HTML
    """
    # Evitar que se intente loguear si ya tiene sesión iniciada
    token = request.cookies.get("access_token")
    if token and token.startswith("Bearer "):
        if verificar_token(token.split(" ")[1]):
            return RedirectResponse(url="/", status_code=303)

    usuario_valido = personal_model.login(usuario, clave)
    
    if usuario_valido:
        # Generar token JWT con la información del usuario
        payload = {
            "personal_id": str(usuario_valido["personal_id"]),
            "usuario": usuario_valido["usuario"],
            "rol": usuario_valido["rol"],
            "nombre": f"{usuario_valido['nombre']} {usuario_valido['ape_paterno']} {usuario_valido['ape_materno']}"
        }
        token = generar_token(payload)
        
        # Redirigir y configurar la cookie JWT
        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie(key="access_token", value=f"Bearer {token}", httponly=True)
        return response
    
    # Si las credenciales son incorrectas
    return templates.TemplateResponse("login.html", {"request": request, "error": "Credenciales incorrectas, intenta nuevamente."})

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
    usuario_valido = personal_model.login(credentials.usuario, credentials.clave)
    
    if not usuario_valido:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    # Generar token JWT
    payload = {
        "personal_id": str(usuario_valido["personal_id"]),
        "usuario": usuario_valido["usuario"],
        "rol": usuario_valido["rol"],
        "nombre": f"{usuario_valido['nombre']} {usuario_valido['ape_paterno']} {usuario_valido['ape_materno']}"
    }
    token = generar_token(payload)
    
    return LoginResponse(
        personal_id=str(usuario_valido["personal_id"]),
        usuario=usuario_valido["usuario"],
        rol=usuario_valido["rol"],
        nombre=f"{usuario_valido['nombre']} {usuario_valido['ape_paterno']} {usuario_valido['ape_materno']}",
        token=token
    )

