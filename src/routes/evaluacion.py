from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, status

from src.schemas.evaluacion import (
    CompletarEvaluacionRequest,
    CompletarEvaluacionResponse,
    FinalizarEvaluacionRequest,
    FinalizarEvaluacionResponse,
    KpisEvaluacionResponse,
    RegistrarEvaluacionRequest,
    RegistrarEvaluacionResponse,
    ResumenEvaluacionResponse,
)
from src.services.auditoria_service import auditoria_service
from src.services.evaluacion_service import EvaluacionService
from src.utilities.jwt_required import obtener_usuario_actual
from src.utilities.request_utils import get_client_ip
from src.utilities.uuid_utils import UUID_PATTERN


evaluacion_router = APIRouter()
evaluacion_service = EvaluacionService()



@evaluacion_router.post(
    "/registrar",
    response_model=RegistrarEvaluacionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def registrar_evaluacion(
    request: Request,
    payload: RegistrarEvaluacionRequest,
    usuario: dict[str, Any] = Depends(obtener_usuario_actual),
) -> RegistrarEvaluacionResponse:
    try:
        personal_id: str = str(usuario["personal_id"])
        result = evaluacion_service.registrar_evaluacion(personal_id, payload)
        auditoria_service.registrar(
            accion="CREAR_EVALUACION",
            personal_id=personal_id,
            usuario=usuario.get("usuario"),
            tipo_personal_id=usuario.get("tipo_personal_id"),
            rol=usuario.get("rol"),
            tabla_afectada="EVALUACION",
            registro_id=str(result.evaluacion_id) if hasattr(result, "evaluacion_id") else None,
            descripcion=f"Nueva evaluación registrada por {usuario.get('usuario')}",
            ip_cliente=get_client_ip(request),
        )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudo procesar la solicitud.") from exc


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
        raise HTTPException(status_code=500, detail="No se pudo procesar la solicitud.") from exc


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
        raise HTTPException(status_code=404, detail="No se encontró la evaluación.")
    return result


@evaluacion_router.get(
    "/{evaluacion_id}/resumen",
    response_model=ResumenEvaluacionResponse,
)
async def obtener_resumen_evaluacion(
    evaluacion_id: str = Path(..., pattern=UUID_PATTERN),
    _: dict[str, Any] = Depends(obtener_usuario_actual),
) -> ResumenEvaluacionResponse:
    try:
        return evaluacion_service.obtener_resumen_evaluacion(evaluacion_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudo procesar la solicitud.") from exc


@evaluacion_router.patch(
    "/{evaluacion_id}/completar",
    response_model=CompletarEvaluacionResponse,
)
async def completar_evaluacion(
    request: Request,
    payload: CompletarEvaluacionRequest,
    evaluacion_id: str = Path(..., pattern=UUID_PATTERN),
    usuario: dict[str, Any] = Depends(obtener_usuario_actual),
) -> CompletarEvaluacionResponse:
    try:
        result = evaluacion_service.completar_evaluacion(evaluacion_id, payload)
        auditoria_service.registrar(
            accion="COMPLETAR_EVALUACION",
            personal_id=str(usuario.get("personal_id", "")),
            usuario=usuario.get("usuario"),
            tipo_personal_id=usuario.get("tipo_personal_id"),
            rol=usuario.get("rol"),
            tabla_afectada="EVALUACION",
            registro_id=evaluacion_id,
            descripcion=f"Evaluación completada: {result.codigo if hasattr(result, 'codigo') else evaluacion_id}",
            ip_cliente=get_client_ip(request),
        )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudo procesar la solicitud.") from exc


@evaluacion_router.get("/{evaluacion_id}/estado")
async def obtener_estado_evaluacion(
    evaluacion_id: str = Path(..., pattern=UUID_PATTERN),
    _: dict[str, Any] = Depends(obtener_usuario_actual),
) -> dict[str, str | None]:
    try:
        return {"estado": evaluacion_service.verificar_estado(evaluacion_id)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudo procesar la solicitud.") from exc


@evaluacion_router.patch(
    "/{evaluacion_id}/finalizar",
    response_model=FinalizarEvaluacionResponse,
)
async def finalizar_evaluacion(
    request: Request,
    payload: FinalizarEvaluacionRequest,
    evaluacion_id: str = Path(..., pattern=UUID_PATTERN),
    usuario: dict[str, Any] = Depends(obtener_usuario_actual),
) -> FinalizarEvaluacionResponse:
    try:
        incidencias = [inc.model_dump() for inc in payload.incidencias] if payload.incidencias else None
        result = evaluacion_service.finalizar_evaluacion(
            evaluacion_id,
            total_defectos=payload.total_defectos,
            total_buenos=payload.total_buenos,
            incidencias=incidencias,
        )
        n = len(incidencias) if incidencias else 0
        descripcion = (
            f"Evaluación {result.codigo} finalizada con {n} incidencia(s) de tapa abierta."
            if n > 0
            else f"Evaluación {result.codigo} finalizada sin incidencias."
        )
        auditoria_service.registrar(
            accion="FINALIZAR_EVALUACION",
            personal_id=str(usuario.get("personal_id", "")),
            usuario=usuario.get("usuario"),
            tipo_personal_id=usuario.get("tipo_personal_id"),
            rol=usuario.get("rol"),
            tabla_afectada="EVALUACION",
            registro_id=evaluacion_id,
            descripcion=descripcion,
            datos_nuevos={
                "codigo": result.codigo,
                "total_defectos": payload.total_defectos,
                "total_buenos": payload.total_buenos,
                "incidencias": incidencias,
            },
            ip_cliente=get_client_ip(request),
        )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudo finalizar la evaluación.") from exc
