from fastapi import APIRouter, HTTPException

from src.schemas.tipo_caficultor import TipoCaficultorResponse
from src.services.tipo_caficultor_service import TipoCaficultorService


tipo_caficultor_router = APIRouter()
tipo_caficultor_service = TipoCaficultorService()


@tipo_caficultor_router.get("/listar", response_model=list[TipoCaficultorResponse])
async def listar_tipo_caficultor() -> list[TipoCaficultorResponse]:
    try:
        return tipo_caficultor_service.listar_tipos_caficultor()
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudo obtener los tipos de caficultor.") from exc
