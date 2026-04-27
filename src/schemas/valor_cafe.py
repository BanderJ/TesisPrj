from datetime import date, datetime

from pydantic import BaseModel, Field


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
    """Schema para crear un nuevo registro de valor de café."""
    rango: str = Field(..., description="Rango de puntuación: 60-65, 66-70, 71-75, 76-80, 81-85, 86-90")
    precio: float = Field(..., gt=0, description="Precio debe ser mayor a 0")

    @property
    def rangos_validos(self) -> list[str]:
        return ['60-65', '66-70', '71-75', '76-80', '81-85', '86-90']

    def validar(self) -> dict[str, str]:
        """Retorna dict con errores, o {} si válido."""
        errores = {}
        if self.rango not in self.rangos_validos:
            errores["rango"] = f"Rango inválido. Válidos: {', '.join(self.rangos_validos)}"
        return errores


class ValorCafeCrearResponse(BaseModel):
    """Respuesta al crear un valor de café."""
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

            if item.rango in rangos_vistos:
                errores[f"item_{idx + 1}"] = f"Rango duplicado en bloque: {item.rango}"
            rangos_vistos.add(item.rango)

        return errores


class ValorCafeCrearBloqueResponse(BaseModel):
    total: int
    data: list[ValorCafeCrearResponse]
