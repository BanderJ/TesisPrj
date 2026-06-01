import re
from datetime import date, datetime

from pydantic import BaseModel, Field, field_validator, model_validator

_RANGO_RE = re.compile(r'^\d+(-\d+)?$')


def _validar_formato_rango(v: str) -> str:
    r = v.strip()
    if not r:
        raise ValueError("El rango no puede estar vacío")
    if not _RANGO_RE.match(r):
        raise ValueError("Formato inválido. Use número (ej: 70) o rango X-Y (ej: 60-65)")
    if '-' in r:
        inicio, fin = map(int, r.split('-', 1))
        if inicio >= fin:
            raise ValueError("En el rango X-Y, X debe ser menor a Y")
    return r


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


class ResumenRangoItem(BaseModel):
    rango: str
    precio: float
    registrado_en: datetime


class ValorCafeResumenRangosResponse(BaseModel):
    fecha_consultada: date
    data: list[ResumenRangoItem]


class ValorCafeCrearRequest(BaseModel):
    rango: str = Field(..., description="Número simple (ej: 70) o rango X-Y (ej: 60-65)")
    precio: float = Field(..., gt=0, description="Precio debe ser mayor a 0")

    @field_validator("rango")
    @classmethod
    def validar_rango(cls, v: str) -> str:
        return _validar_formato_rango(v)


class ValorCafeCrearResponse(BaseModel):
    id: str
    rango: str
    precio: float
    fecha: datetime


class ValorCafeCrearBloqueRequest(BaseModel):
    precios: list[ValorCafeCrearRequest] = Field(..., min_length=1, max_length=20)

    @model_validator(mode="after")
    def sin_rangos_duplicados(self) -> "ValorCafeCrearBloqueRequest":
        vistos: set[str] = set()
        for item in self.precios:
            if item.rango in vistos:
                raise ValueError(f"Rango duplicado en bloque: {item.rango}")
            vistos.add(item.rango)
        return self


class ValorCafeCrearBloqueResponse(BaseModel):
    total: int
    data: list[ValorCafeCrearResponse]


class ValorCafeActualizarPrecioRequest(BaseModel):
    rango: str = Field(..., min_length=1, max_length=10, description="Rango a actualizar (debe existir hoy)")
    precio: float = Field(..., gt=0, description="Nuevo precio, debe ser mayor a 0")

    @field_validator("rango")
    @classmethod
    def validar_rango(cls, v: str) -> str:
        return _validar_formato_rango(v)


class ValorCafeActualizarPrecioResponse(BaseModel):
    id: str
    rango: str
    precio: float
    fecha: datetime


class ValorCafeEliminarRangoResponse(BaseModel):
    eliminados: int
    rango: str
