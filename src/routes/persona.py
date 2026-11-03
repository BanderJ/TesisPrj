from fastapi import APIRouter, Depends, HTTPException

from src.services.persona_service import PersonaService
from src.schemas.dni import DniConsultaResponse
from src.utilities.jwt_required import obtener_usuario_actual

persona_router = APIRouter()
_persona_service = PersonaService()


@persona_router.get("/consultar/{num_documento}", response_model=DniConsultaResponse, dependencies=[Depends(obtener_usuario_actual)])
def consultar_persona(num_documento: str) -> DniConsultaResponse:
    try:
        return _persona_service.consultar_por_documento(num_documento)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudo consultar la persona.") from exc
