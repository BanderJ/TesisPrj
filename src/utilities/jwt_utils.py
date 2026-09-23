from typing import Any

import jwt
from datetime import datetime, timedelta
from src.config import Config

def generar_token(payload: dict[str, Any], days: int = 7) -> str:
    payload['exp'] = datetime.utcnow() + timedelta(days=days)
    token = jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")

    return token

def verificar_token(token: str) -> dict[str, Any] | None:
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None