import os
import uuid
from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from src.schemas.cooperativa import CooperativaCreate, CooperativaUpdate, CooperativaResponse
from src.services import cooperativa_service
from src.utilities.jwt_required import obtener_usuario_actual

router = APIRouter(prefix="/cooperativas", tags=["cooperativas"])


@router.get("/mi-cooperativa", response_model=CooperativaResponse)
async def obtener_mi_cooperativa(usuario_actual: dict = Depends(obtener_usuario_actual)):
    cooperativa = cooperativa_service.obtener_por_usuario(usuario_actual.get("personal_id"))
    if not cooperativa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no tiene cooperativa asociada")
    cooperativa["tipo_personal_id"] = usuario_actual.get("tipo_personal_id")
    return cooperativa


@router.get("", response_model=list[CooperativaResponse])
async def listar_cooperativas(usuario_actual: dict = Depends(obtener_usuario_actual)):
    return cooperativa_service.obtener_todas()


@router.get("/{cooperativa_id}", response_model=CooperativaResponse)
async def obtener_cooperativa(cooperativa_id: str, usuario_actual: dict = Depends(obtener_usuario_actual)):
    cooperativa = cooperativa_service.obtener_por_id(cooperativa_id)
    if not cooperativa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cooperativa no encontrada")
    return cooperativa


@router.post("", response_model=CooperativaResponse, status_code=status.HTTP_201_CREATED)
async def crear_cooperativa(data: CooperativaCreate, usuario_actual: dict = Depends(obtener_usuario_actual)):
    try:
        return cooperativa_service.crear(data)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear la cooperativa") from exc


@router.patch("/{cooperativa_id}", response_model=CooperativaResponse)
async def actualizar_cooperativa(
    cooperativa_id: str,
    data: CooperativaUpdate,
    usuario_actual: dict = Depends(obtener_usuario_actual),
):
    try:
        updated = cooperativa_service.actualizar(cooperativa_id, data)
        if not updated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cooperativa no encontrada")
        return updated
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar la cooperativa") from exc


@router.delete("/{cooperativa_id}", status_code=status.HTTP_204_NO_CONTENT)
async def desactivar_cooperativa(cooperativa_id: str, usuario_actual: dict = Depends(obtener_usuario_actual)):
    cooperativa = cooperativa_service.obtener_por_id(cooperativa_id)
    if not cooperativa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cooperativa no encontrada")
    cooperativa_service.desactivar(cooperativa_id)


@router.post("/upload-imagen")
async def upload_imagen_cooperativa(file: UploadFile = File(...), usuario_actual: dict = Depends(obtener_usuario_actual)):
    try:
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Solo se aceptan imágenes")

        upload_dir = "src/resources/cooperativa"
        os.makedirs(upload_dir, exist_ok=True)

        ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
        filename = f"{uuid.uuid4()}.{ext}"
        filepath = os.path.join(upload_dir, filename)

        contents = await file.read()
        with open(filepath, "wb") as f:
            f.write(contents)

        return {"imagen_url": f"/resources/cooperativa/{filename}"}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Error al subir la imagen") from exc
