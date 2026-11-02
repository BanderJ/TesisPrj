from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from starlette.concurrency import run_in_threadpool

from src.schemas.cooperativa import CooperativaUpdate, CooperativaResponse
from src.services.auditoria_service import auditoria_service
from src.services.cooperativa_service import MAX_TAMANO_IMAGEN_BYTES, cooperativa_service
from src.utilities.jwt_required import obtener_usuario_actual, require_admin_o_gerente
from src.utilities.request_utils import get_client_ip

router = APIRouter(prefix="/cooperativas", tags=["cooperativas"])


@router.get("/mi-cooperativa", response_model=CooperativaResponse)
def obtener_mi_cooperativa(usuario_actual: dict = Depends(obtener_usuario_actual)) -> Any:
    cooperativa = cooperativa_service.obtener_por_usuario(usuario_actual.get("personal_id"))
    if not cooperativa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No tienes una cooperativa asociada.")
    return {**cooperativa, "tipo_personal_id": usuario_actual.get("tipo_personal_id")}


@router.patch("/{cooperativa_id}", response_model=CooperativaResponse)
def actualizar_cooperativa(
    cooperativa_id: str,
    data: CooperativaUpdate,
    request: Request,
    usuario_actual: dict = Depends(require_admin_o_gerente),
) -> Any:
    try:
        datos_anteriores = cooperativa_service.obtener_por_id(cooperativa_id)
        updated = cooperativa_service.actualizar(cooperativa_id, data)
        if not updated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontró la cooperativa.")
        auditoria_service.registrar(
            accion="ACTUALIZAR_COOPERATIVA",
            personal_id=usuario_actual.get("personal_id"),
            usuario=usuario_actual.get("usuario"),
            tipo_personal_id=usuario_actual.get("tipo_personal_id"),
            rol=usuario_actual.get("rol"),
            tabla_afectada="COOPERATIVA",
            registro_id=cooperativa_id,
            descripcion=f"Cooperativa actualizada: {updated.get('nombre')}",
            datos_anteriores={k: str(v) for k, v in datos_anteriores.items()} if datos_anteriores else None,
            datos_nuevos={k: str(v) for k, v in updated.items()},
            ip_cliente=get_client_ip(request),
        )
        return updated
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="No se pudo actualizar la cooperativa.") from exc


@router.post("/upload-imagen")
async def upload_imagen_cooperativa(
    file: UploadFile = File(...),
    usuario_actual: dict = Depends(require_admin_o_gerente),
) -> dict[str, str]:
    # Se lee un byte más del máximo para detectar el exceso sin cargar archivos enormes.
    contenido = await file.read(MAX_TAMANO_IMAGEN_BYTES + 1)
    try:
        imagen_url = await run_in_threadpool(cooperativa_service.guardar_imagen, contenido)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudo subir la imagen.") from exc
    return {"imagen_url": imagen_url}
