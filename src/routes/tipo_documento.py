from fastapi import APIRouter, HTTPException
from src.services.tipo_documento_service import TipoDocumentoService

tipo_documento_router = APIRouter()
tipo_documento_service = TipoDocumentoService()


@tipo_documento_router.get("/listar")
async def listar_tipo_documento():
    try:
        return tipo_documento_service.listar_tipos_documento()
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudo obtener tipos de documento") from exc
