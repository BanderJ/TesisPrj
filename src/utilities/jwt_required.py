from typing import Any

from fastapi import Header, HTTPException, Request

from src.utilities.jwt_utils import verificar_token


class RequerirLoginException(Exception):
    """Excepcion para manejar redirecciones a login desde dependencias de rutas HTML."""
    pass


def obtener_usuario_actual(request: Request) -> dict[str, Any]:
    """Dependencia FastAPI para rutas HTML protegidas.

    Lee el token JWT desde la cookie 'access_token'.
    Lanza RequerirLoginException si el token no existe o es invalido,
    lo que el exception handler global convierte en redirect a /auth/login.
    """
    token_cookie: str | None = request.cookies.get("access_token")
    if not token_cookie:
        raise RequerirLoginException()

    # Soportar tanto token puro como formato legado "Bearer <token>"
    if token_cookie.startswith("Bearer "):
        token = token_cookie.split(" ", 1)[1].strip()
    else:
        token = token_cookie.strip()

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
    """Dependencia FastAPI para rutas API protegidas.

    Acepta token por cabecera Authorization o por cookie access_token.
    """
    token_source = authorization
    if not token_source:
        token_source = request.cookies.get("access_token")

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