from typing import Any
from fastapi import APIRouter, HTTPException, Depends, status

from src.schemas.tipo_grano import TipoGranoResponse, TipoGranoCreate, TipoGranoUpdate
from src.services.tipo_grano_service import TipoGranoService
from src.utilities.jwt_required import obtener_usuario_actual

tipo_grano_router = APIRouter()
tipo_grano_service = TipoGranoService()


def verificar_admin(usuario_actual: dict[str, Any] = Depends(obtener_usuario_actual)) -> dict[str, Any]:
    """Verificar que el usuario sea administrador (tipo_personal_id 2 o 3)"""
    tipo_personal_id = usuario_actual.get("tipo_personal_id")
    if tipo_personal_id not in (2, 3):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para gestionar tipos de grano"
        )
    return usuario_actual


@tipo_grano_router.get("/listar", response_model=list[TipoGranoResponse])
async def listar_tipo_grano() -> list[TipoGranoResponse]:
    try:
        return tipo_grano_service.listar_tipos_grano()
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudo obtener los tipos de grano") from exc


@tipo_grano_router.post("/crear", response_model=TipoGranoResponse, status_code=status.HTTP_201_CREATED)
async def crear_tipo_grano(
    payload: TipoGranoCreate,
    _: dict[str, Any] = Depends(verificar_admin)
) -> TipoGranoResponse:
    try:
        return tipo_grano_service.crear_tipo_grano(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudo crear el tipo de grano") from exc


@tipo_grano_router.patch("/{tipo_grano_id}", response_model=TipoGranoResponse)
async def actualizar_tipo_grano(
    tipo_grano_id: int,
    payload: TipoGranoUpdate,
    _: dict[str, Any] = Depends(verificar_admin)
) -> TipoGranoResponse:
    try:
        return tipo_grano_service.actualizar_tipo_grano(tipo_grano_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudo actualizar el tipo de grano") from exc


@tipo_grano_router.delete("/{tipo_grano_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_tipo_grano(
    tipo_grano_id: int,
    _: dict[str, Any] = Depends(verificar_admin)
) -> None:
    try:
        tipo_grano_service.eliminar_tipo_grano(tipo_grano_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudo eliminar el tipo de grano") from exc
