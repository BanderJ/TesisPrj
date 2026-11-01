import math
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query

from src.schemas.auditoria import AuditoriaListResponse
from src.services.auditoria_service import auditoria_service
from src.utilities.jwt_required import require_admin_o_gerente

auditoria_router = APIRouter(prefix="/auditoria", tags=["auditoria"])


@auditoria_router.get("", response_model=AuditoriaListResponse)
async def listar_auditoria(
    usuario: str | None = Query(default=None),
    tipo_personal_id: int | None = Query(default=None),
    accion: str | None = Query(default=None),
    fecha_desde: date | None = Query(default=None),
    fecha_hasta: date | None = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=50, ge=1, le=200),
    _: dict = Depends(require_admin_o_gerente),
) -> AuditoriaListResponse:
    try:
        registros, total = auditoria_service.obtener(
            usuario=usuario,
            tipo_personal_id=tipo_personal_id,
            accion=accion,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            pagina=pagina,
            limite=limite,
        )
        total_paginas = math.ceil(total / limite) if total > 0 else 1
        return AuditoriaListResponse(
            registros=registros,
            total=total,
            pagina=pagina,
            total_paginas=total_paginas,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudieron obtener los registros de auditoría.") from exc


@auditoria_router.get("/usuarios")
async def listar_usuarios_auditados(
    _: dict = Depends(require_admin_o_gerente),
) -> dict:
    try:
        return {"usuarios": auditoria_service.obtener_usuarios_auditados()}
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudieron obtener los usuarios.") from exc


@auditoria_router.get("/acciones")
async def listar_acciones(
    _: dict = Depends(require_admin_o_gerente),
) -> dict:
    try:
        return {"acciones": auditoria_service.obtener_acciones_disponibles()}
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudieron obtener las acciones.") from exc
