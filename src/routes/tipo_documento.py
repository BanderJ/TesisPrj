from fastapi import APIRouter, HTTPException

from src.schemas.tipo_documento import TipoDocumentoResponse
from src.services.tipo_documento_service import TipoDocumentoService

tipo_documento_router = APIRouter()
tipo_documento_service = TipoDocumentoService()


@tipo_documento_router.get("/listar", response_model=list[TipoDocumentoResponse])
async def listar_tipo_documento() -> list[TipoDocumentoResponse]:
    try:
        return tipo_documento_service.listar_tipos_documento()
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudo obtener los tipos de documento.") from exc
