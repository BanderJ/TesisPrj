import re

from fastapi import APIRouter, HTTPException

from src.apis.reniec_api import ReniecApi
from src.schemas.dni import DniConsultaResponse

dni_router = APIRouter()


@dni_router.get("/consultar/{dni}", response_model=DniConsultaResponse)
async def consultar_dni(dni: str) -> DniConsultaResponse:
    """Consulta datos personales de un DNI via Factiliza y devuelve campos normalizados."""
    if not re.fullmatch(r"\d{8}", dni):
        raise HTTPException(status_code=400, detail="El DNI debe tener exactamente 8 digitos.")

    try:
        data = ReniecApi.consultar_dni(dni)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Error al consultar el servicio externo.") from exc

    if data is None:
        return DniConsultaResponse(encontrado=False)

    return DniConsultaResponse(encontrado=True, **data)
