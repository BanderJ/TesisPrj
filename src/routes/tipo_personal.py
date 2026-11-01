from fastapi import APIRouter, HTTPException

from src.schemas.tipo_personal import TipoPersonalResponse
from src.services.tipo_personal_service import TipoPersonalService

tipo_personal_router = APIRouter()
tipo_personal_service = TipoPersonalService()


@tipo_personal_router.get("/listar", response_model=list[TipoPersonalResponse])
async def listar_tipo_personal() -> list[TipoPersonalResponse]:
    try:
        return tipo_personal_service.listar_tipo_personal()
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudieron obtener los tipos de personal.") from exc
    