from datetime import date

from fastapi import APIRouter, HTTPException, Query

from src.schemas.valor_cafe import (
    ValorCafeCambiosDiariosResponse,
    ValorCafeHistorialResponse,
    ValorCafeMaximoResponse,
    ValorCafeResumenRangosResponse,
)
from src.services.valor_cafe_service import ValorCafeService


valor_cafe_router = APIRouter()
valor_cafe_service = ValorCafeService()


@valor_cafe_router.get("/historial", response_model=ValorCafeHistorialResponse)
async def historial_dia(
    fecha: date | None = Query(default=None, description="Fecha a consultar (YYYY-MM-DD). Default: hoy"),
    rango: str | None = Query(default=None, description="Filtrar por rango de cafe"),
) -> ValorCafeHistorialResponse:
    try:
        return valor_cafe_service.obtener_historial_dia(fecha, rango)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudo obtener el historial") from exc


@valor_cafe_router.get("/maximo-dia", response_model=ValorCafeMaximoResponse)
async def maximo_dia(
    fecha: date | None = Query(default=None, description="Fecha a consultar (YYYY-MM-DD). Default: hoy"),
) -> ValorCafeMaximoResponse:
    try:
        return valor_cafe_service.obtener_maximo_dia(fecha)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudo obtener el precio maximo del dia") from exc


@valor_cafe_router.get("/cambios-diarios", response_model=ValorCafeCambiosDiariosResponse)
async def cambios_diarios(
    desde: date | None = Query(default=None, description="Fecha inicio (YYYY-MM-DD). Default: hace 30 dias"),
    hasta: date | None = Query(default=None, description="Fecha fin (YYYY-MM-DD). Default: hoy"),
    rango: str | None = Query(default=None, description="Filtrar por rango de cafe"),
) -> ValorCafeCambiosDiariosResponse:
    try:
        return valor_cafe_service.obtener_cambios_diarios(desde, hasta, rango)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudo obtener los cambios diarios") from exc


@valor_cafe_router.get("/resumen-rangos", response_model=ValorCafeResumenRangosResponse)
async def resumen_rangos(
    fecha: date | None = Query(default=None, description="Fecha a consultar (YYYY-MM-DD). Default: hoy"),
) -> ValorCafeResumenRangosResponse:
    try:
        return valor_cafe_service.obtener_resumen_rangos(fecha)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudo obtener el resumen por rangos") from exc
