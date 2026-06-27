from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, JSONResponse
from src.schemas.auth import LoginRequest, LoginResponse
from src.services.auth_service import AuthService
from src.services.auditoria_service import auditoria_service
import os

templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "../templates"))

auth = APIRouter()
auth_service = AuthService()


def _ip(request: Request) -> str | None:
    return request.client.host if request.client else None


@auth.get("/login")
async def login_get(request: Request):
    token = request.cookies.get("access_token")
    if auth_service.sesion_activa(token):
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(request=request, name="login.html", context={"request": request})


@auth.post("/login")
async def login_post(request: Request, usuario: str = Form(...), clave: str = Form(...)):
    token = request.cookies.get("access_token")
    if auth_service.sesion_activa(token):
        return RedirectResponse(url="/", status_code=303)

    login_response = auth_service.autenticar(usuario, clave)

    if login_response:
        auditoria_service.registrar(
            accion="LOGIN",
            personal_id=login_response.personal_id,
            usuario=login_response.usuario,
            tipo_personal_id=None,
            rol=login_response.rol,
            descripcion=f"Inicio de sesión exitoso: {login_response.usuario}",
            ip_cliente=_ip(request),
        )
        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie(key="access_token", value=login_response.token, httponly=True)
        return response

    auditoria_service.registrar(
        accion="LOGIN_FALLIDO",
        descripcion=f"Intento de login fallido para usuario: {usuario}",
        ip_cliente=_ip(request),
    )
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"request": request, "error": "Credenciales incorrectas, intenta nuevamente."},
    )


@auth.get("/logout")
async def logout(request: Request):
    token_cookie = request.cookies.get("access_token")
    if token_cookie:
        from src.utilities.jwt_utils import verificar_token
        token = token_cookie.split(" ", 1)[1].strip() if token_cookie.startswith("Bearer ") else token_cookie
        payload = verificar_token(token)
        if payload:
            auditoria_service.registrar(
                accion="LOGOUT",
                personal_id=payload.get("personal_id"),
                usuario=payload.get("usuario"),
                tipo_personal_id=payload.get("tipo_personal_id"),
                rol=payload.get("rol"),
                descripcion=f"Cierre de sesión: {payload.get('usuario')}",
                ip_cliente=_ip(request),
            )
    response = RedirectResponse(url="/auth/login", status_code=303)
    response.delete_cookie("access_token")
    return response


@auth.post("/api/login", response_model=LoginResponse)
async def login_api(credentials: LoginRequest):
    login_response = auth_service.autenticar(credentials.usuario, credentials.clave)
    if not login_response:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    response = JSONResponse(content=login_response.dict())
    response.set_cookie(key="access_token", value=login_response.token, httponly=True)
    return response
