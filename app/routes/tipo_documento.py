from fastapi import APIRouter, HTTPException
from app.models.tipo_documento import TipoDocumento

tipo_documento_router = APIRouter()
tipo_documento_model = TipoDocumento()


@tipo_documento_router.get("/listar")
async def listar_tipo_documento():
	try:
		return tipo_documento_model.listar()
	except Exception as exc:
		raise HTTPException(status_code=500, detail="No se pudo obtener tipos de documento") from exc
