from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, Response
from src.services.auth_service import auth_service
from src.services.auditoria_service import auditoria_service
from src.utilities.jwt_utils import DIAS_SESION
from src.utilities.request_utils import get_client_ip
import os

templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "../templates"))

auth = APIRouter()

@auth.get("/login")
def login_get(request: Request) -> Response:
    token = request.cookies.get("access_token")
    if auth_service.sesion_activa(token):
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(request=request, name="login.html", context={"request": request})


@auth.post("/login")
def login_post(request: Request, usuario: str = Form(...), clave: str = Form(...)) -> Response:
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
            ip_cliente=get_client_ip(request),
        )
        response = RedirectResponse(url="/?bienvenida=1", status_code=303)
        # samesite="lax": el navegador no envía la cookie en POST/PATCH iniciados
        # desde otro sitio (CSRF). max_age igual a la vigencia del JWT.
        response.set_cookie(
            key="access_token",
            value=login_response.token,
            httponly=True,
            samesite="lax",
            max_age=DIAS_SESION * 24 * 3600,
        )
        return response

    auditoria_service.registrar(
        accion="LOGIN_FALLIDO",
        descripcion=f"Intento fallido de inicio de sesión del usuario: {usuario}",
        ip_cliente=get_client_ip(request),
    )
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"request": request, "error": "Credenciales incorrectas, intenta nuevamente."},
    )


@auth.get("/logout")
def logout(request: Request) -> Response:
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
                ip_cliente=get_client_ip(request),
            )
    response = RedirectResponse(url="/auth/login", status_code=303)
    response.delete_cookie("access_token")
    return response
