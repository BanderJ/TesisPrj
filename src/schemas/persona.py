from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class PersonaRegistroRequest(BaseModel):
	nombre: str = Field(..., min_length=2, max_length=50)
	ape_paterno: str = Field(..., min_length=2, max_length=30)
	ape_materno: str = Field(..., min_length=2, max_length=30)
	sexo: Literal["M", "F"]
	fecha_nacimiento: date
	tipo_documento_id: int = Field(..., ge=1)
	num_documento: str = Field(
		...,
		pattern=r"^[A-Za-z0-9]{8,12}$",
		description="Documento alfanumerico de 8 a 12 caracteres.",
	)
	telefono: str | None = Field(
		default=None,
		pattern=r"^\d{9}$|^$",
		description="Telefono de 9 digitos. Puede enviarse vacio.",
	)
	ubigeo: str | None = Field(
		default=None,
		pattern=r"^\d{6}$|^$",
		description="Codigo INEI de 6 digitos del distrito. Opcional.",
	)
