from pydantic import BaseModel


class TipoCaficultorResponse(BaseModel):
    id: int
    nombre: str
