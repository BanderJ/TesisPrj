from fastapi import APIRouter, HTTPException, Query

from src.schemas.ubigeo import (
    DepartamentoResponse,
    DistritoResponse,
    ProvinciaResponse,
    UbigeoResponse,
)
from src.services.ubigeo_service import UbigeoService

ubigeo_router = APIRouter()
ubigeo_service = UbigeoService()


@ubigeo_router.get("/departamentos", response_model=list[DepartamentoResponse])
async def listar_departamentos() -> list[DepartamentoResponse]:
    try:
        return ubigeo_service.listar_departamentos()
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudo obtener departamentos") from exc


@ubigeo_router.get("/provincias", response_model=list[ProvinciaResponse])
async def listar_provincias(
    departamento: str = Query(..., min_length=2, max_length=2, description="Codigo de 2 digitos del departamento"),
) -> list[ProvinciaResponse]:
    try:
        return ubigeo_service.listar_provincias(departamento)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudo obtener provincias") from exc


@ubigeo_router.get("/distritos", response_model=list[DistritoResponse])
async def listar_distritos(
    provincia: str = Query(..., min_length=4, max_length=4, description="Codigo de 4 digitos de la provincia"),
) -> list[DistritoResponse]:
    try:
        return ubigeo_service.listar_distritos(provincia)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudo obtener distritos") from exc


@ubigeo_router.get("/{codigo}", response_model=UbigeoResponse)
async def obtener_ubigeo(codigo: str) -> UbigeoResponse:
    try:
        resultado = ubigeo_service.obtener_por_codigo(codigo)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudo obtener el ubigeo") from exc

    if resultado is None:
        raise HTTPException(status_code=404, detail="Ubigeo no encontrado")
    return resultado
