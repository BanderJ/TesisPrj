from datetime import date, timedelta
from typing import Any

from src.models.valor_cafe import ValorCafe
from src.schemas.valor_cafe import (
    CambioDiario,
    ResumenRangoItem,
    ValorCafeActualizarPrecioResponse,
    ValorCafeCrearBloqueRequest,
    ValorCafeCrearBloqueResponse,
    ValorCafeCambiosDiariosResponse,
    ValorCafeCrearResponse,
    ValorCafeEliminarRangoResponse,
    ValorCafeHistorialResponse,
    ValorCafeItem,
    ValorCafeMaximoResponse,
    ValorCafeResumenRangosResponse,
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

    def obtener_historial_dia(self, fecha: date | None, rango: str | None = None) -> ValorCafeHistorialResponse:
        fecha_efectiva = fecha or date.today()
        filas = self.model.obtener_historial_dia(fecha_efectiva, rango)
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
        rango: str | None = None,
    ) -> ValorCafeCambiosDiariosResponse:
        hasta_efectivo = hasta or date.today()
        desde_efectivo = desde or (hasta_efectivo - timedelta(days=29))

        if desde_efectivo > hasta_efectivo:
            raise ValueError("La fecha inicial no puede ser posterior a la fecha final.")

        filas = self.model.obtener_cambios_diarios(desde_efectivo, hasta_efectivo, rango)
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

    def obtener_resumen_rangos(self, fecha: date | None = None) -> ValorCafeResumenRangosResponse:
        fecha_efectiva = fecha or date.today()
        filas = self.model.obtener_resumen_rangos(fecha_efectiva)
        items = [
            ResumenRangoItem(
                rango=f["rango"],
                precio=float(f["precio"]),
                registrado_en=f["registrado_en"],
            )
            for f in filas
        ]
        return ValorCafeResumenRangosResponse(
            fecha_consultada=fecha_efectiva,
            data=items,
        )

    def crear_precios_bloque(self, data: ValorCafeCrearBloqueRequest) -> ValorCafeCrearBloqueResponse:
        filas = self.model.crear_bloque([(item.rango, item.precio) for item in data.precios])
        items = [
            ValorCafeCrearResponse(
                id=str(fila["id"]),
                rango=fila["rango"],
                precio=float(fila["precio"]),
                fecha=fila["fecha"],
            )
            for fila in filas
        ]

        return ValorCafeCrearBloqueResponse(total=len(items), data=items)

    def actualizar_precio_rango(self, rango: str, precio: float) -> ValorCafeActualizarPrecioResponse:
        """Registra un NUEVO precio para el rango — nunca borra ni modifica los anteriores.
        Los registros previos son históricos (las evaluaciones completadas los referencian)
        y permiten ver la variación del precio durante el día. Las consultas de precio
        vigente siempre toman el registro más reciente por fecha."""
        fila = self.model.crear(rango, precio)
        return ValorCafeActualizarPrecioResponse(
            id=str(fila["id"]),
            rango=fila["rango"],
            precio=float(fila["precio"]),
            fecha=fila["fecha"],
        )

    def eliminar_rango_hoy(self, rango: str) -> ValorCafeEliminarRangoResponse:
        """Elimina todos los registros del rango en el día actual."""
        eliminados = self.model.eliminar_por_rango_fecha(rango, date.today())
        return ValorCafeEliminarRangoResponse(eliminados=eliminados, rango=rango)
