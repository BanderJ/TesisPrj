from pydantic import BaseModel


class DniConsultaResponse(BaseModel):
    encontrado: bool
    nombres: str | None = None
    apellido_paterno: str | None = None
    apellido_materno: str | None = None
    sexo: str | None = None
    fecha_nacimiento: str | None = None
    ubigeo: str | None = None
    departamento: str | None = None
    provincia: str | None = None
    distrito: str | None = None
    direccion: str | None = None
