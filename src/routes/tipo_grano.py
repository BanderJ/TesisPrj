from fastapi import APIRouter, HTTPException

from src.schemas.tipo_grano import TipoGranoResponse
from src.services.tipo_grano_service import TipoGranoService

tipo_grano_router = APIRouter()
tipo_grano_service = TipoGranoService()


@tipo_grano_router.get("/listar", response_model=list[TipoGranoResponse])
async def listar_tipo_grano() -> list[TipoGranoResponse]:
    try:
        return tipo_grano_service.listar_tipos_grano()
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudo obtener los tipos de grano") from exc
