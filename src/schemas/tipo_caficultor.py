from pydantic import BaseModel


class TipoCaficultorResponse(BaseModel):
    id: int
    nombre: str
    is_socio: bool
