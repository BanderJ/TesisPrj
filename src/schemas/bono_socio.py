from decimal import Decimal

from pydantic import BaseModel, Field


class BonoSocioRegistro(BaseModel):
    id: str
    monto: Decimal
    fecha: str
    registrado_por: str | None = None


class BonoSocioResponse(BaseModel):
    vigente: BonoSocioRegistro | None
    historial: list[BonoSocioRegistro]


class BonoSocioActualizarRequest(BaseModel):
    # numeric(7, 2) en BONO_SOCIO; 0 deja a los socios sin beneficio
    monto: Decimal = Field(..., ge=0, le=Decimal("99999.99"), decimal_places=2)
