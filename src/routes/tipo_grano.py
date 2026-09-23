from typing import Any
from fastapi import APIRouter, HTTPException, Depends, status

from src.schemas.tipo_grano import TipoGranoResponse, TipoGranoCreate, TipoGranoUpdate
from src.services.tipo_grano_service import TipoGranoService
from src.utilities.jwt_required import require_admin_o_gerente

tipo_grano_router = APIRouter()
tipo_grano_service = TipoGranoService()


@tipo_grano_router.get("/listar", response_model=list[TipoGranoResponse])
async def listar_tipo_grano() -> list[TipoGranoResponse]:
    try:
        return tipo_grano_service.listar_tipos_grano()
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudo obtener los tipos de grano.") from exc


@tipo_grano_router.post("/crear", response_model=TipoGranoResponse, status_code=status.HTTP_201_CREATED)
async def crear_tipo_grano(
    payload: TipoGranoCreate,
    _: dict[str, Any] = Depends(require_admin_o_gerente)
) -> TipoGranoResponse:
    try:
        return tipo_grano_service.crear_tipo_grano(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudo crear el tipo de grano.") from exc


@tipo_grano_router.patch("/{tipo_grano_id}", response_model=TipoGranoResponse)
async def actualizar_tipo_grano(
    tipo_grano_id: int,
    payload: TipoGranoUpdate,
    _: dict[str, Any] = Depends(require_admin_o_gerente)
) -> TipoGranoResponse:
    try:
        return tipo_grano_service.actualizar_tipo_grano(tipo_grano_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudo actualizar el tipo de grano.") from exc


@tipo_grano_router.delete("/{tipo_grano_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_tipo_grano(
    tipo_grano_id: int,
    _: dict[str, Any] = Depends(require_admin_o_gerente)
) -> None:
    try:
        tipo_grano_service.eliminar_tipo_grano(tipo_grano_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudo eliminar el tipo de grano.") from exc
