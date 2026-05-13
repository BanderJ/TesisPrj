from typing import Annotated

from fastapi import APIRouter, HTTPException, Path

from src.services.dni_service import DniService
from src.schemas.dni import DniConsultaResponse

dni_router = APIRouter()
_dni_service = DniService()


@dni_router.get("/consultar/{dni}", response_model=DniConsultaResponse)
async def consultar_dni(
    dni: Annotated[str, Path(pattern=r"^\d{8}$", description="Número de DNI de 8 dígitos")],
) -> DniConsultaResponse:
    try:
        return _dni_service.consultar_dni(dni)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Error al consultar el servicio externo.") from exc
