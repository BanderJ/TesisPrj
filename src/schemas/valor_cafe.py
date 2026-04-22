from datetime import date, datetime

from pydantic import BaseModel


class ValorCafeItem(BaseModel):
    id: str
    rango: str
    precio: float
    fecha: datetime


class ValorCafeHistorialResponse(BaseModel):
    fecha_consultada: date
    total: int
    data: list[ValorCafeItem]


class ValorCafeMaximoResponse(BaseModel):
    fecha_consultada: date
    data: ValorCafeItem | None


class CambioDiario(BaseModel):
    fecha: date
    precio_maximo: float


class ValorCafeCambiosDiariosResponse(BaseModel):
    desde: date
    hasta: date
    total: int
    data: list[CambioDiario]
