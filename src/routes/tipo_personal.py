from fastapi import APIRouter, HTTPException
from src.services.tipo_personal_service import TipoDocumentoService

tipo_personal_router = APIRouter()
tipo_personal_service = TipoDocumentoService()

@tipo_personal_router.get("/listar")
async def listar_tipo_personal():
    try:
        return tipo_personal_service.listar_tipo_personal()
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudo obtener tipos de personal") from exc
    