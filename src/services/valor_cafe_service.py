from datetime import date, timedelta
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from src.database.bd import Connection
from src.models.valor_cafe import ValorCafe
from src.schemas.valor_cafe import (
    CambioDiario,
    ResumenRangoItem,
    ValorCafeActualizarPrecioResponse,
    ValorCafeCrearBloqueRequest,
    ValorCafeCrearBloqueResponse,
    ValorCafeCambiosDiariosResponse,
    ValorCafeCrearResponse,
    ValorCafeDesactivarRangoResponse,
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
        activo=row["activo"],
    )


def _parsear_rango(rango: str) -> tuple[float, float]:
    """Convierte 'X-Y' o 'X' (ya validado por el schema) en (minimo, maximo)."""
    if "-" in rango:
        inicio, fin = rango.split("-", 1)
        return float(inicio), float(fin)
    valor = float(rango)
    return valor, valor


def _se_superponen(a: tuple[float, float], b: tuple[float, float]) -> bool:
    return a[0] <= b[1] and b[0] <= a[1]


class ValorCafeService:
    def __init__(self) -> None:
        self.model = ValorCafe()

    @contextmanager
    def _transaccion_precios(self) -> Iterator[Connection]:
        """Serializa los cambios de rangos para validar y guardar sobre la misma vigencia."""
        db = Connection()
        try:
            self.model.bloquear_para_cambio(db)
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def _validar_sin_solapamiento(
        self, nuevos_rangos: list[str], excluir_rango: str | None = None,
        db: Connection | None = None,
    ) -> None:
        """Rechaza un rango que se solape con uno vigente hoy o con otro del mismo
        lote. `obtener_por_factor` elige el mas reciente del dia cuando dos
        rangos cubren el mismo factor de rendimiento, asi que un solapamiento
        deja el precio pagado al caficultor determinado por el orden de
        insercion en vez de por el rango que realmente le corresponde.
        `excluir_rango` permite re-cotizar un rango existente (mismo string)
        sin que se rechace por "solaparse consigo mismo"."""
        existentes = self.model.obtener_resumen_rangos(date.today(), db=db)
        vigentes = [
            (fila["rango"], _parsear_rango(fila["rango"]))
            for fila in existentes
            if fila["rango"] != excluir_rango
        ]

        # `vigentes` ya excluye el propio rango cuando se pasa excluir_rango
        # (caso "re-cotizar"), y el schema de crear_bloque ya rechaza rangos
        # repetidos dentro del mismo lote, asi que no hace falta comparar
        # `rango_previo != rango` aqui: un duplicado exacto en `vigentes` (crear_bloque
        # contra un rango ya registrado hoy) SI debe reportarse como solapamiento.
        acumulados: list[tuple[str, tuple[float, float]]] = []
        for rango in nuevos_rangos:
            parsed = _parsear_rango(rango)
            for rango_previo, parsed_previo in vigentes + acumulados:
                if _se_superponen(parsed, parsed_previo):
                    raise ValueError(
                        f"El rango '{rango}' se solapa con el rango '{rango_previo}'. "
                        "Si quieres reemplazar un rango vigente, desactívalo primero."
                    )
            acumulados.append((rango, parsed))

    def _validar_precios_no_decrecientes(
        self, nuevos: list[tuple[str, float]], excluir_rango: str | None = None,
        db: Connection | None = None,
    ) -> None:
        """El precio no puede bajar conforme sube el rango de factor de rendimiento:
        un lote con mejor rendimiento nunca debe pagar menos que uno con peor
        rendimiento. Se llama despues de _validar_sin_solapamiento (que ya
        garantiza que cada rango es unico y sin ambiguedad), y compara la tabla
        de precios vigente hoy con los nuevos ya aplicados, ordenada por el
        limite inferior de cada rango."""
        existentes = self.model.obtener_resumen_rangos(date.today(), db=db)
        tabla: dict[str, tuple[tuple[float, float], float]] = {
            fila["rango"]: (_parsear_rango(fila["rango"]), float(fila["precio"]))
            for fila in existentes
            if fila["rango"] != excluir_rango
        }
        for rango, precio in nuevos:
            tabla[rango] = (_parsear_rango(rango), precio)

        ordenados = sorted(tabla.items(), key=lambda item: item[1][0][0])
        for i in range(1, len(ordenados)):
            rango_prev, (_, precio_prev) = ordenados[i - 1]
            rango_actual, (_, precio_actual) = ordenados[i]
            if precio_actual < precio_prev:
                raise ValueError(
                    f"El precio del rango '{rango_actual}' (S/ {precio_actual:.2f}) no puede ser "
                    f"menor al del rango '{rango_prev}' (S/ {precio_prev:.2f})."
                )

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
        with self._transaccion_precios() as db:
            self._validar_sin_solapamiento([item.rango for item in data.precios], db=db)
            self._validar_precios_no_decrecientes([(item.rango, item.precio) for item in data.precios], db=db)
            filas = self.model.crear_bloque([(item.rango, item.precio) for item in data.precios], db=db)
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
        with self._transaccion_precios() as db:
            activos = self.model.obtener_resumen_rangos(date.today(), db=db)
            if not any(item["rango"] == rango for item in activos):
                raise ValueError("El rango ya no está activo hoy. Actualiza la lista de rangos antes de editar.")
            self._validar_sin_solapamiento([rango], excluir_rango=rango, db=db)
            self._validar_precios_no_decrecientes([(rango, precio)], excluir_rango=rango, db=db)
            fila = self.model.crear(rango, precio, db=db)
        return ValorCafeActualizarPrecioResponse(
            id=str(fila["id"]),
            rango=fila["rango"],
            precio=float(fila["precio"]),
            fecha=fila["fecha"],
        )

    def desactivar_rango_hoy(self, rango: str) -> ValorCafeDesactivarRangoResponse:
        """Desactiva el rango del día sin modificar precios, pagos ni evaluaciones previas."""
        with self._transaccion_precios() as db:
            desactivados = self.model.desactivar_por_rango_fecha(rango, date.today(), db=db)
        return ValorCafeDesactivarRangoResponse(desactivados=desactivados, rango=rango)
