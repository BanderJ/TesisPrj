from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path

from src.services.dni_service import DniService
from src.schemas.dni import DniConsultaResponse
from src.utilities.jwt_required import obtener_usuario_actual

dni_router = APIRouter()
_dni_service = DniService()


@dni_router.get("/consultar/{dni}", response_model=DniConsultaResponse, dependencies=[Depends(obtener_usuario_actual)])
def consultar_dni(
    dni: Annotated[str, Path(pattern=r"^\d{8}$", description="Número de DNI de 8 dígitos")],
) -> DniConsultaResponse:
    try:
        return _dni_service.consultar_dni(dni)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="No se pudo consultar el servicio externo. Intenta más tarde.") from exc
