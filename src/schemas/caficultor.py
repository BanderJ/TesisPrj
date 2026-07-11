from pydantic import BaseModel, Field

from src.schemas.persona import PersonaRegistroRequest


class CaficultorData(BaseModel):
    persona_id: str
    num_documento: str
    nombre_completo: str
    tipo_caficultor: str
    es_socio: bool


class ObtenerDatosResponse(BaseModel):
    encontrado: bool
    mensaje: str
    data: CaficultorData | None = None


class RegistrarCaficultorRequest(PersonaRegistroRequest):
    tipo_caficultor_id: int = Field(..., ge=1)


class RegistrarCaficultorResponse(BaseModel):
    registrado: bool
    mensaje: str
    persona_id: str
    caficultor_id: str
    tipo_caficultor_id: int


class ConvertirSocioResponse(BaseModel):
    actualizado: bool
    mensaje: str
    num_documento: str
