from typing import Optional

from pydantic import BaseModel


class ObtenerDatosRequest(BaseModel):
    num_documento: str


class CaficultorData(BaseModel):
    persona_id: str
    num_documento: str
    nombre_completo: str
    tipo_caficultor: str


class ObtenerDatosResponse(BaseModel):
    encontrado: bool
    mensaje: str
    data: Optional[CaficultorData] = None

