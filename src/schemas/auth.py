from pydantic import BaseModel


class LoginResponse(BaseModel):

    personal_id: str
    usuario: str
    rol: str
    nombre: str
    token: str
