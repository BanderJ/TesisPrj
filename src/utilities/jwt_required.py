from typing import Any

from fastapi import Depends, Header, HTTPException, Request

from src.utilities.jwt_utils import verificar_token


class RequerirLoginException(Exception):
    """Excepcion para manejar redirecciones a login desde dependencias de rutas HTML."""
    pass


def obtener_usuario_actual(request: Request) -> dict[str, Any]:
    token_cookie: str | None = request.cookies.get("access_token")
    if not token_cookie:
        raise RequerirLoginException()

    token = token_cookie.split(" ", 1)[1].strip() if token_cookie.startswith("Bearer ") else token_cookie.strip()

    if not token:
        raise RequerirLoginException()

    payload: dict[str, Any] | None = verificar_token(token)
    if not payload:
        raise RequerirLoginException()

    return payload


def jwt_token_requerido(
    request: Request,
    authorization: str | None = Header(default=None),
) -> dict[str, Any]:
    token_source = authorization or request.cookies.get("access_token")

    if not token_source:
        raise HTTPException(status_code=401, detail="Token requerido")

    if not token_source.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Formato de token invalido")

    token = token_source.split(" ", 1)[1].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Token requerido")

    payload: dict[str, Any] | None = verificar_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token invalido o expirado")

    return payload


def require_admin_o_gerente(user: dict[str, Any] = Depends(obtener_usuario_actual)) -> dict[str, Any]:
    """Dependencia FastAPI — exige tipo_personal_id 2 (Gerente) o 3 (Administrador)."""
    if user.get("tipo_personal_id") not in [2, 3]:
        raise HTTPException(status_code=403, detail="No tienes permisos para acceder a esta sección")
    return user
