from datetime import date, timedelta
from typing import Any

from src.models.valor_cafe import ValorCafe
from src.schemas.valor_cafe import (
    CambioDiario,
    ValorCafeCambiosDiariosResponse,
    ValorCafeHistorialResponse,
    ValorCafeItem,
    ValorCafeMaximoResponse,
)


def _row_to_item(row: dict[str, Any]) -> ValorCafeItem:
    return ValorCafeItem(
        id=str(row["id"]),
        rango=row["rango"],
        precio=float(row["precio"]),
        fecha=row["fecha"],
    )


class ValorCafeService:
    def __init__(self) -> None:
        self.model = ValorCafe()

    def obtener_historial_dia(self, fecha: date | None) -> ValorCafeHistorialResponse:
        fecha_efectiva = fecha or date.today()
        filas = self.model.obtener_historial_dia(fecha_efectiva)
        items = [_row_to_item(f) for f in filas]
        return ValorCafeHistorialResponse(
            fecha_consultada=fecha_efectiva,
            total=len(items),
            data=items,
        )

    def obtener_maximo_dia(self, fecha: date | None) -> ValorCafeMaximoResponse:
        fecha_efectiva = fecha or date.today()
        fila = self.model.obtener_maximo_dia(fecha_efectiva)
        return ValorCafeMaximoResponse(
            fecha_consultada=fecha_efectiva,
            data=_row_to_item(fila) if fila else None,
        )

    def obtener_cambios_diarios(
        self,
        desde: date | None,
        hasta: date | None,
    ) -> ValorCafeCambiosDiariosResponse:
        hasta_efectivo = hasta or date.today()
        desde_efectivo = desde or (hasta_efectivo - timedelta(days=29))

        if desde_efectivo > hasta_efectivo:
            raise ValueError("'desde' no puede ser posterior a 'hasta'")

        filas = self.model.obtener_cambios_diarios(desde_efectivo, hasta_efectivo)
        cambios = [
            CambioDiario(fecha=f["fecha"], precio_maximo=float(f["precio_maximo"]))
            for f in filas
        ]
        return ValorCafeCambiosDiariosResponse(
            desde=desde_efectivo,
            hasta=hasta_efectivo,
            total=len(cambios),
            data=cambios,
        )
