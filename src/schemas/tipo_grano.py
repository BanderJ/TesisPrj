from pydantic import BaseModel


class TipoGranoResponse(BaseModel):
    id: int
    nombre: str
