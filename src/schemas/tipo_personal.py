from pydantic import BaseModel


class TipoPersonalResponse(BaseModel):
    id: int
    nombre: str