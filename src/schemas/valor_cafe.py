import re
from datetime import date, datetime

from pydantic import BaseModel, Field

_RANGO_RE = re.compile(r'^\d+(-\d+)?$')


def _error_rango(rango: str) -> str | None:
    r = rango.strip()
    if not r:
        return "El rango no puede estar vacío"
    if not _RANGO_RE.match(r):
        return "Formato inválido. Use número (ej: 70) o rango X-Y (ej: 60-65)"
    if '-' in r:
        inicio, fin = map(int, r.split('-', 1))
        if inicio >= fin:
            return "En el rango X-Y, X debe ser menor a Y"
    return None


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

    def validar(self) -> dict[str, str]:
        errores = {}
        error = _error_rango(self.rango)
        if error:
            errores["rango"] = error
        return errores


class ValorCafeCrearResponse(BaseModel):
    id: str
    rango: str
    precio: float
    fecha: datetime


class ValorCafeCrearBloqueRequest(BaseModel):
    precios: list[ValorCafeCrearRequest] = Field(..., min_length=1, max_length=20)

    def validar(self) -> dict[str, str]:
        errores: dict[str, str] = {}
        rangos_vistos: set[str] = set()

        for idx, item in enumerate(self.precios):
            errores_item = item.validar()
            if errores_item:
                errores[f"item_{idx + 1}"] = str(errores_item)

            rango_norm = item.rango.strip()
            if rango_norm in rangos_vistos:
                errores[f"item_{idx + 1}"] = f"Rango duplicado en bloque: {rango_norm}"
            rangos_vistos.add(rango_norm)

        return errores


class ValorCafeCrearBloqueResponse(BaseModel):
    total: int
    data: list[ValorCafeCrearResponse]


class ValorCafeActualizarPrecioRequest(BaseModel):
    rango: str = Field(..., min_length=1, max_length=10, description="Rango a actualizar (debe existir hoy)")
    precio: float = Field(..., gt=0, description="Nuevo precio, debe ser mayor a 0")

    def validar(self) -> dict[str, str]:
        errores: dict[str, str] = {}
        error = _error_rango(self.rango)
        if error:
            errores["rango"] = error
        return errores


class ValorCafeActualizarPrecioResponse(BaseModel):
    id: str
    rango: str
    precio: float
    fecha: datetime


class ValorCafeEliminarRangoResponse(BaseModel):
    eliminados: int
    rango: str
