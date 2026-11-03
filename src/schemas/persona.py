from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, field_validator

EDAD_MINIMA_ANIOS = 18


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
		pattern=r"^\d{9}$",
		description="Telefono de 9 digitos. Puede enviarse vacio.",
	)
	ubigeo: str | None = Field(
		default=None,
		pattern=r"^\d{6}$",
		description="Codigo INEI de 6 digitos del distrito. Opcional.",
	)

	@field_validator("telefono", "ubigeo", mode="before")
	@classmethod
	def normalizar_opcionales(cls, v: str | None) -> str | None:
		if not v or not isinstance(v, str) or not v.strip():
			return None
		return v.strip()

	@field_validator("fecha_nacimiento")
	@classmethod
	def validar_mayoria_edad(cls, v: date) -> date:
		hoy = date.today()
		edad = hoy.year - v.year - ((hoy.month, hoy.day) < (v.month, v.day))
		if edad < EDAD_MINIMA_ANIOS:
			raise ValueError(f"El caficultor debe ser mayor de {EDAD_MINIMA_ANIOS} años.")
		return v
