from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from src.config import Config

DIAS_SESION = 7
# HS256 necesita una clave de al menos 256 bits (RFC 7518, sección 3.2).
_LONGITUD_MINIMA_CLAVE = 32
# Textos de ejemplo publicados en el repositorio y en el manual de instalación.
_CLAVES_DE_EJEMPLO = {
    "your_secret_key_here",
    "su-clave-secreta-aleatoria-de-32-caracteres",
}


def validar_clave_secreta() -> None:
    """Detiene el arranque si SECRET_KEY falta o es un texto de ejemplo: con una
    clave conocida cualquiera puede firmar un token de Administrador."""
    clave = Config.SECRET_KEY
    if not clave or clave in _CLAVES_DE_EJEMPLO or len(clave) < _LONGITUD_MINIMA_CLAVE:
        raise RuntimeError(
            "SECRET_KEY no está configurada o no es válida. Defina en .env una clave "
            f"aleatoria de al menos {_LONGITUD_MINIMA_CLAVE} caracteres, por ejemplo con: "
            'python -c "import secrets; print(secrets.token_urlsafe(48))"'
        )


def generar_token(payload: dict[str, Any], days: int = DIAS_SESION) -> str:
    payload['exp'] = datetime.now(timezone.utc) + timedelta(days=days)
    return jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")


def verificar_token(token: str) -> dict[str, Any] | None:
    try:
        return jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
    except jwt.InvalidTokenError:
        return None
