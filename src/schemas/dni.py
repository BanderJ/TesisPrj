import re
from pydantic import BaseModel, ConfigDict, Field, field_validator


class DniConsultaResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    encontrado: bool
    nombres: str | None = None
    apellido_paterno: str | None = None
    apellido_materno: str | None = None
    sexo: str | None = None
    fecha_nacimiento: str | None = None
    ubigeo: str | None = Field(default=None, alias="ubigeo_sunat")
    departamento: str | None = None
    provincia: str | None = None
    distrito: str | None = None
    direccion: str | None = None

    @field_validator(
        "nombres",
        "apellido_paterno",
        "apellido_materno",
        "departamento",
        "provincia",
        "distrito",
        "direccion",
        mode="before"
    )
    @classmethod
    def normalizar_texto(cls, v: str | None) -> str | None:
        if not v or not isinstance(v, str) or not v.strip():
            return None
        return v.strip().title()

    @field_validator("sexo", mode="before")
    @classmethod
    def normalizar_sexo(cls, v: str | None) -> str | None:
        if not v or not isinstance(v, str):
            return None
        v = v.strip().upper()
        return v if v in {"M", "F"} else None

    @field_validator("fecha_nacimiento", mode="before")
    @classmethod
    def normalizar_fecha(cls, v: str | None) -> str | None:
        if not v or not isinstance(v, str) or not v.strip():
            return None
        texto = v.strip()
        match = re.fullmatch(r"(\d{2})/(\d{2})/(\d{4})", texto)
        if match:
            return f"{match.group(3)}-{match.group(2)}-{match.group(1)}"
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", texto):
            return texto
        return None

    @field_validator("ubigeo", mode="before")
    @classmethod
    def normalizar_ubigeo(cls, v: str | None) -> str | None:
        if not v or not isinstance(v, str):
            return None
        codigo = v.strip()
        if re.fullmatch(r"\d{6}", codigo):
            return codigo
        return None
