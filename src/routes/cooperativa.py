import os

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status

from src.schemas.cooperativa import CooperativaUpdate, CooperativaResponse
from src.services.auditoria_service import auditoria_service
from src.services.cooperativa_service import cooperativa_service
from src.utilities.jwt_required import obtener_usuario_actual, require_admin_o_gerente
from src.utilities.request_utils import get_client_ip
from src.utilities.uuid_utils import uuid7

router = APIRouter(prefix="/cooperativas", tags=["cooperativas"])

EXTENSIONES_IMAGEN_PERMITIDAS = {"jpg", "jpeg", "png", "webp", "gif"}
MAX_TAMANO_IMAGEN_BYTES = 5 * 1024 * 1024


@router.get("/mi-cooperativa", response_model=CooperativaResponse)
async def obtener_mi_cooperativa(usuario_actual: dict = Depends(obtener_usuario_actual)):
    cooperativa = cooperativa_service.obtener_por_usuario(usuario_actual.get("personal_id"))
    if not cooperativa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No tienes una cooperativa asociada.")
    return {**cooperativa, "tipo_personal_id": usuario_actual.get("tipo_personal_id")}


@router.patch("/{cooperativa_id}", response_model=CooperativaResponse)
async def actualizar_cooperativa(
    cooperativa_id: str,
    data: CooperativaUpdate,
    request: Request,
    usuario_actual: dict = Depends(require_admin_o_gerente),
):
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
):
    try:
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Solo se aceptan imágenes.")
        # Extension por whitelist fija: nunca se usa la extension cruda del
        # archivo subido para construir la ruta de escritura (riesgo de path
        # traversal via un filename como "a.png/../../evil.py").
        ext = file.filename.rsplit(".", 1)[-1].lower() if file.filename and "." in file.filename else ""
        if ext not in EXTENSIONES_IMAGEN_PERMITIDAS:
            raise HTTPException(status_code=400, detail="Formato de imagen no permitido. Use JPG, PNG, WEBP o GIF.")
        contents = await file.read()
        if len(contents) > MAX_TAMANO_IMAGEN_BYTES:
            raise HTTPException(status_code=400, detail="La imagen no puede superar 5 MB.")
        upload_dir = "src/resources/cooperativa"
        os.makedirs(upload_dir, exist_ok=True)
        filename = f"{uuid7()}.{ext}"
        filepath = os.path.join(upload_dir, filename)
        with open(filepath, "wb") as f:
            f.write(contents)
        return {"imagen_url": f"/resources/cooperativa/{filename}"}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudo subir la imagen.") from exc
