from pydantic import BaseModel


class TipoDocumentoResponse(BaseModel):
    id: int
    nombre: str