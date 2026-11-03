from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from src.schemas.valor_cafe import (
    ValorCafeActualizarPrecioRequest,
    ValorCafeActualizarPrecioResponse,
    ValorCafeCambiosDiariosResponse,
    ValorCafeCrearBloqueRequest,
    ValorCafeCrearBloqueResponse,
    ValorCafeDesactivarRangoRequest,
    ValorCafeDesactivarRangoResponse,
    ValorCafeHistorialResponse,
    ValorCafeMaximoResponse,
    ValorCafeResumenRangosResponse,
)
from src.services.auditoria_service import auditoria_service
from src.services.valor_cafe_service import ValorCafeService
from src.utilities.jwt_required import obtener_usuario_actual, require_admin_o_gerente
from src.utilities.request_utils import get_client_ip


valor_cafe_router = APIRouter()
valor_cafe_service = ValorCafeService()


@valor_cafe_router.get("/historial", response_model=ValorCafeHistorialResponse)
def historial_dia(
    fecha: date | None = Query(default=None, description="Fecha a consultar (YYYY-MM-DD). Default: hoy"),
    rango: str | None = Query(default=None, description="Filtrar por rango de cafe"),
    _: dict = Depends(obtener_usuario_actual),
) -> ValorCafeHistorialResponse:
    try:
        return valor_cafe_service.obtener_historial_dia(fecha, rango)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudo obtener el historial de precios.") from exc


@valor_cafe_router.get("/maximo-dia", response_model=ValorCafeMaximoResponse)
def maximo_dia(
    fecha: date | None = Query(default=None, description="Fecha a consultar (YYYY-MM-DD). Default: hoy"),
    _: dict = Depends(obtener_usuario_actual),
) -> ValorCafeMaximoResponse:
    try:
        return valor_cafe_service.obtener_maximo_dia(fecha)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudo obtener el precio máximo del día.") from exc


@valor_cafe_router.get("/cambios-diarios", response_model=ValorCafeCambiosDiariosResponse)
def cambios_diarios(
    desde: date | None = Query(default=None, description="Fecha inicio (YYYY-MM-DD). Default: hace 30 dias"),
    hasta: date | None = Query(default=None, description="Fecha fin (YYYY-MM-DD). Default: hoy"),
    rango: str | None = Query(default=None, description="Filtrar por rango de cafe"),
    _: dict = Depends(obtener_usuario_actual),
) -> ValorCafeCambiosDiariosResponse:
    try:
        return valor_cafe_service.obtener_cambios_diarios(desde, hasta, rango)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudieron obtener los cambios diarios.") from exc


@valor_cafe_router.get("/resumen-rangos", response_model=ValorCafeResumenRangosResponse)
def resumen_rangos(
    fecha: date | None = Query(default=None, description="Fecha a consultar (YYYY-MM-DD). Default: hoy"),
    _: dict = Depends(obtener_usuario_actual),
) -> ValorCafeResumenRangosResponse:
    try:
        return valor_cafe_service.obtener_resumen_rangos(fecha)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudo obtener el resumen por rangos.") from exc


@valor_cafe_router.patch("/actualizar-precio", response_model=ValorCafeActualizarPrecioResponse)
def actualizar_precio_rango(
    request: Request,
    data: ValorCafeActualizarPrecioRequest,
    user: dict = Depends(require_admin_o_gerente),
) -> ValorCafeActualizarPrecioResponse:
    try:
        result = valor_cafe_service.actualizar_precio_rango(data.rango, data.precio)
        auditoria_service.registrar(
            accion="ACTUALIZAR_VALOR_CAFE",
            personal_id=user.get("personal_id"),
            usuario=user.get("usuario"),
            tipo_personal_id=user.get("tipo_personal_id"),
            rol=user.get("rol"),
            tabla_afectada="VALOR_CAFE",
            descripcion=f"Precio actualizado: rango={data.rango}, nuevo precio={data.precio}",
            ip_cliente=get_client_ip(request),
        )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudo actualizar el precio.") from exc


@valor_cafe_router.patch("/desactivar-rango", response_model=ValorCafeDesactivarRangoResponse)
def desactivar_rango(
    request: Request,
    data: ValorCafeDesactivarRangoRequest,
    user: dict = Depends(require_admin_o_gerente),
) -> ValorCafeDesactivarRangoResponse:
    try:
        result = valor_cafe_service.desactivar_rango_hoy(data.rango)
        auditoria_service.registrar(
            accion="DESACTIVAR_VALOR_CAFE",
            personal_id=user.get("personal_id"),
            usuario=user.get("usuario"),
            tipo_personal_id=user.get("tipo_personal_id"),
            rol=user.get("rol"),
            tabla_afectada="VALOR_CAFE",
            descripcion=f"Rango desactivado: {data.rango}; versiones retiradas: {result.desactivados}. Historial conservado.",
            ip_cliente=get_client_ip(request),
        )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudo desactivar el rango.") from exc


@valor_cafe_router.post("/crear-bloque", response_model=ValorCafeCrearBloqueResponse)
def crear_valor_cafe_bloque(
    request: Request,
    data: ValorCafeCrearBloqueRequest,
    user: dict = Depends(require_admin_o_gerente),
) -> ValorCafeCrearBloqueResponse:
    try:
        result = valor_cafe_service.crear_precios_bloque(data)
        auditoria_service.registrar(
            accion="CREAR_VALOR_CAFE",
            personal_id=user.get("personal_id"),
            usuario=user.get("usuario"),
            tipo_personal_id=user.get("tipo_personal_id"),
            rol=user.get("rol"),
            tabla_afectada="VALOR_CAFE",
            descripcion=f"Precios en bloque registrados ({len(getattr(data, 'precios', []))} rangos)",
            ip_cliente=get_client_ip(request),
        )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudieron registrar los precios en bloque.") from exc
