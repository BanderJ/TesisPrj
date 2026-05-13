from fastapi import APIRouter, HTTPException

from src.services.persona_service import PersonaService
from src.schemas.dni import DniConsultaResponse

persona_router = APIRouter()
_persona_service = PersonaService()


@persona_router.get("/consultar/{num_documento}", response_model=DniConsultaResponse)
async def consultar_persona(num_documento: str) -> DniConsultaResponse:
    try:
        return _persona_service.consultar_por_documento(num_documento)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Error al consultar persona") from exc
