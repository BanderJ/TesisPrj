from datetime import date

from fastapi import APIRouter, HTTPException, Query, Depends

from src.schemas.valor_cafe import (
    ValorCafeActualizarPrecioRequest,
    ValorCafeActualizarPrecioResponse,
    ValorCafeCambiosDiariosResponse,
    ValorCafeCrearBloqueRequest,
    ValorCafeCrearBloqueResponse,
    ValorCafeEliminarRangoResponse,
    ValorCafeHistorialResponse,
    ValorCafeCrearRequest,
    ValorCafeCrearResponse,
    ValorCafeMaximoResponse,
    ValorCafeResumenRangosResponse,
)
from src.services.valor_cafe_service import ValorCafeService
from src.utilities.jwt_required import obtener_usuario_actual


valor_cafe_router = APIRouter()
valor_cafe_service = ValorCafeService()
ROLES_PERMITIDOS = {2, 3}


def validar_permiso_creacion(token_payload: dict) -> None:
    tipo_personal_id = token_payload.get("tipo_personal_id")
    if tipo_personal_id not in ROLES_PERMITIDOS:
        raise HTTPException(
            status_code=403,
            detail="No tienes permiso. Solo Gerente o Administrador pueden crear precios.",
        )


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


@valor_cafe_router.post("/crear", response_model=ValorCafeCrearResponse)
async def crear_valor_cafe(
    data: ValorCafeCrearRequest,
    token_payload: dict = Depends(obtener_usuario_actual),
) -> ValorCafeCrearResponse:
    """
    Crea un nuevo registro de valor de café.
    Solo Gerente (tipo_personal_id=2) y Administrador (tipo_personal_id=3) pueden acceder.
    """
    validar_permiso_creacion(token_payload)
    
    try:
        return valor_cafe_service.crear_precio(data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Error al crear el registro") from exc


@valor_cafe_router.patch("/actualizar-precio", response_model=ValorCafeActualizarPrecioResponse)
async def actualizar_precio_rango(
    data: ValorCafeActualizarPrecioRequest,
    token_payload: dict = Depends(obtener_usuario_actual),
) -> ValorCafeActualizarPrecioResponse:
    """Reemplaza el precio de un rango del día actual (elimina registros anteriores e inserta uno nuevo)."""
    validar_permiso_creacion(token_payload)
    try:
        return valor_cafe_service.actualizar_precio_rango(data.rango, data.precio)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Error al actualizar el precio") from exc


@valor_cafe_router.delete("/eliminar-rango", response_model=ValorCafeEliminarRangoResponse)
async def eliminar_rango(
    rango: str = Query(..., min_length=1, max_length=10, description="Rango a eliminar del día actual"),
    token_payload: dict = Depends(obtener_usuario_actual),
) -> ValorCafeEliminarRangoResponse:
    """Elimina todos los registros de un rango en el día actual."""
    validar_permiso_creacion(token_payload)
    try:
        return valor_cafe_service.eliminar_rango_hoy(rango)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Error al eliminar el rango") from exc


@valor_cafe_router.post("/crear-bloque", response_model=ValorCafeCrearBloqueResponse)
async def crear_valor_cafe_bloque(
    data: ValorCafeCrearBloqueRequest,
    token_payload: dict = Depends(obtener_usuario_actual),
) -> ValorCafeCrearBloqueResponse:
    """Crea registros en bloque para multiples rangos de café."""
    validar_permiso_creacion(token_payload)

    try:
        return valor_cafe_service.crear_precios_bloque(data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Error al crear registros en bloque") from exc
