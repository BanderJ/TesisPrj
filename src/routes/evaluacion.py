from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from src.schemas.evaluacion import (
    CompletarEvaluacionRequest,
    CompletarEvaluacionResponse,
    FinalizarEvaluacionResponse,
    KpisEvaluacionResponse,
    RegistrarEvaluacionRequest,
    RegistrarEvaluacionResponse,
    ResumenEvaluacionResponse,
)
from src.services.evaluacion_service import EvaluacionService
from src.utilities.jwt_required import obtener_usuario_actual


evaluacion_router = APIRouter()
evaluacion_service = EvaluacionService()

_UUID_PATTERN = r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"


@evaluacion_router.post(
    "/registrar",
    response_model=RegistrarEvaluacionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def registrar_evaluacion(
    payload: RegistrarEvaluacionRequest,
    usuario: dict[str, Any] = Depends(obtener_usuario_actual),
) -> RegistrarEvaluacionResponse:
    try:
        personal_id: str = str(usuario["personal_id"])
        return evaluacion_service.registrar_evaluacion(personal_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error interno: {exc}") from exc


@evaluacion_router.get(
    "/kpis",
    response_model=KpisEvaluacionResponse,
)
async def obtener_kpis(
    _: dict[str, Any] = Depends(obtener_usuario_actual),
) -> KpisEvaluacionResponse:
    try:
        data = evaluacion_service.obtener_kpis()
        return KpisEvaluacionResponse(**data)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error interno: {exc}") from exc


@evaluacion_router.get(
    "/buscar",
    response_model=ResumenEvaluacionResponse,
)
async def buscar_evaluacion_por_codigo(
    codigo: str = Query(..., min_length=1, max_length=10),
    _: dict[str, Any] = Depends(obtener_usuario_actual),
) -> ResumenEvaluacionResponse:
    result = evaluacion_service.buscar_evaluacion_por_codigo(codigo)
    if not result:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada.")
    return result


@evaluacion_router.get(
    "/{evaluacion_id}/resumen",
    response_model=ResumenEvaluacionResponse,
)
async def obtener_resumen_evaluacion(
    evaluacion_id: str = Path(..., pattern=_UUID_PATTERN),
    _: dict[str, Any] = Depends(obtener_usuario_actual),
) -> ResumenEvaluacionResponse:
    try:
        return evaluacion_service.obtener_resumen_evaluacion(evaluacion_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error interno: {exc}") from exc


@evaluacion_router.patch(
    "/{evaluacion_id}/completar",
    response_model=CompletarEvaluacionResponse,
)
async def completar_evaluacion(
    payload: CompletarEvaluacionRequest,
    evaluacion_id: str = Path(..., pattern=_UUID_PATTERN),
    _: dict[str, Any] = Depends(obtener_usuario_actual),
) -> CompletarEvaluacionResponse:
    try:
        return evaluacion_service.completar_evaluacion(evaluacion_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error interno: {exc}") from exc


@evaluacion_router.get("/{evaluacion_id}/estado")
async def obtener_estado_evaluacion(
    evaluacion_id: str = Path(..., pattern=_UUID_PATTERN),
    _: dict[str, Any] = Depends(obtener_usuario_actual),
) -> dict[str, str | None]:
    return {"estado": evaluacion_service.verificar_estado(evaluacion_id)}


@evaluacion_router.patch(
    "/{evaluacion_id}/finalizar",
    response_model=FinalizarEvaluacionResponse,
)
async def finalizar_evaluacion(
    evaluacion_id: str = Path(..., pattern=_UUID_PATTERN),
    _: dict[str, Any] = Depends(obtener_usuario_actual),
) -> FinalizarEvaluacionResponse:
    try:
        return evaluacion_service.finalizar_evaluacion(evaluacion_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudo finalizar la evaluacion") from exc
