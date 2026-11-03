from fastapi import APIRouter, Depends, HTTPException

from src.schemas.tipo_caficultor import TipoCaficultorResponse
from src.services.tipo_caficultor_service import TipoCaficultorService
from src.utilities.jwt_required import obtener_usuario_actual


tipo_caficultor_router = APIRouter()
tipo_caficultor_service = TipoCaficultorService()


@tipo_caficultor_router.get("/listar", response_model=list[TipoCaficultorResponse], dependencies=[Depends(obtener_usuario_actual)])
def listar_tipo_caficultor() -> list[TipoCaficultorResponse]:
    try:
        return tipo_caficultor_service.listar_tipos_caficultor()
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudieron obtener los tipos de caficultor.") from exc
