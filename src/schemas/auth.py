from pydantic import BaseModel


class LoginRequest(BaseModel):

    usuario: str
    clave: str


class LoginResponse(BaseModel):

    personal_id: str
    usuario: str
    rol: str
    nombre: str
    token: str
