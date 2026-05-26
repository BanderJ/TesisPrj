"""
Cooperativa Routes - HTTP endpoints for cooperative management
"""
from fastapi import APIRouter, HTTPException, status, Depends
from src.schemas.cooperativa import CooperativaCreate, CooperativaUpdate, CooperativaResponse
from src.services import cooperativa_service
from src.utilities.jwt_required import obtener_usuario_actual

router = APIRouter(prefix="/cooperativas", tags=["cooperativas"])


@router.get("/mi-cooperativa", response_model=CooperativaResponse)
async def obtener_mi_cooperativa(usuario_actual: dict = Depends(obtener_usuario_actual)):
    """Get the cooperative associated with current user."""
    personal_id = usuario_actual.get("personal_id")
    cooperativa = cooperativa_service.obtener_por_usuario(personal_id)
    if not cooperativa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no tiene cooperativa asociada"
        )
    return cooperativa


@router.get("", response_model=list[CooperativaResponse])
async def listar_cooperativas(usuario_actual: dict = Depends(obtener_usuario_actual)):
    """List all active cooperatives."""
    return cooperativa_service.obtener_todas()


@router.get("/{cooperativa_id}", response_model=CooperativaResponse)
async def obtener_cooperativa(cooperativa_id: str, usuario_actual: dict = Depends(obtener_usuario_actual)):
    """Get cooperative by ID."""
    cooperativa = cooperativa_service.obtener_por_id(cooperativa_id)
    if not cooperativa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cooperativa no encontrada")
    return cooperativa


@router.post("", response_model=CooperativaResponse, status_code=status.HTTP_201_CREATED)
async def crear_cooperativa(data: CooperativaCreate, usuario_actual: dict = Depends(obtener_usuario_actual)):
    """Create a new cooperative."""
    # Check if codigo is already used (if provided)
    if data.codigo:
        existing = cooperativa_service.obtener_por_codigo(data.codigo)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El código '{data.codigo}' ya está en uso"
            )

    return cooperativa_service.crear(data)


@router.patch("/{cooperativa_id}", response_model=CooperativaResponse)
async def actualizar_cooperativa(
    cooperativa_id: str,
    data: CooperativaUpdate,
    usuario_actual: dict = Depends(obtener_usuario_actual)
):
    """Update cooperative data."""
    # Verify cooperativa exists
    cooperativa = cooperativa_service.obtener_por_id(cooperativa_id)
    if not cooperativa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cooperativa no encontrada")

    # Check if new codigo is already used (if changed)
    if data.codigo and data.codigo != cooperativa.get("codigo"):
        existing = cooperativa_service.obtener_por_codigo(data.codigo)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El código '{data.codigo}' ya está en uso"
            )

    updated = cooperativa_service.actualizar(cooperativa_id, data)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cooperativa no encontrada")
    return updated


@router.delete("/{cooperativa_id}", status_code=status.HTTP_204_NO_CONTENT)
async def desactivar_cooperativa(cooperativa_id: str, usuario_actual: dict = Depends(obtener_usuario_actual)):
    """Deactivate a cooperative (soft delete)."""
    cooperativa = cooperativa_service.obtener_por_id(cooperativa_id)
    if not cooperativa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cooperativa no encontrada")

    cooperativa_service.desactivar(cooperativa_id)


@router.get("/debug/usuario-info")
async def debug_usuario_info(usuario_actual: dict = Depends(obtener_usuario_actual)):
    """Debug endpoint to check user and cooperative association."""
    from src.database.bd import Connection

    personal_id = usuario_actual.get("personal_id")
    db = Connection()
    try:
        persona_sql = "SELECT id, nombre, cooperativa_id FROM PERSONA WHERE id = %s"
        persona = db.obtener_uno(persona_sql, [personal_id])

        return {
            "usuario_actual": usuario_actual,
            "persona": persona,
            "personal_id": personal_id,
        }
    finally:
        db.close()
