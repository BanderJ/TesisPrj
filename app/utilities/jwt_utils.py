import jwt
from datetime import datetime, timedelta
from app.config import Config

def generar_token(payload, days=7):
    payload['exp'] = datetime.utcnow() + timedelta(days=days)
    token = jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")
    # if isinstance(token, bytes):
    #     token = token.decode('utf-8')
    return token

def verificar_token(token):
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None