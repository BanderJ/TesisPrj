"""
Cooperativa Service - Business logic for cooperative management
"""
from src.database.bd import Connection
from src.models import cooperativa as coop_model
from src.schemas.cooperativa import CooperativaCreate, CooperativaUpdate


def obtener_todas() -> list[dict]:
    """Get all active cooperatives."""
    db = Connection()
    try:
        return coop_model.obtener_todas(db)
    finally:
        db.close()


def obtener_por_id(cooperativa_id: str) -> dict | None:
    """Get cooperative by ID."""
    db = Connection()
    try:
        return coop_model.obtener_por_id(cooperativa_id, db)
    finally:
        db.close()


def obtener_por_codigo(codigo: str) -> dict | None:
    """Get cooperative by unique codigo."""
    db = Connection()
    try:
        return coop_model.obtener_por_codigo(codigo, db)
    finally:
        db.close()


def crear(data: CooperativaCreate) -> dict:
    """Create a new cooperative."""
    db = Connection()
    try:
        return coop_model.crear(
            nombre=data.nombre,
            codigo=data.codigo,
            direccion=data.direccion,
            telefono=data.telefono,
            correo=data.correo,
            descripcion=data.descripcion,
            imagen_url=data.imagen_url,
            db=db
        )
    finally:
        db.close()


def actualizar(cooperativa_id: str, data: CooperativaUpdate) -> dict | None:
    """Update cooperative (only non-None fields are updated)."""
    db = Connection()
    try:
        return coop_model.actualizar(
            cooperativa_id=cooperativa_id,
            nombre=data.nombre,
            codigo=data.codigo,
            direccion=data.direccion,
            telefono=data.telefono,
            correo=data.correo,
            descripcion=data.descripcion,
            imagen_url=data.imagen_url,
            db=db
        )
    finally:
        db.close()


def desactivar(cooperativa_id: str) -> dict | None:
    """Deactivate a cooperative (soft delete)."""
    db = Connection()
    try:
        return coop_model.desactivar(cooperativa_id, db)
    finally:
        db.close()


def obtener_por_usuario(personal_id: str) -> dict | None:
    """Get cooperative associated with a user with default assignment."""
    db = Connection()
    try:
        return coop_model.obtener_por_usuario(personal_id, db)
    finally:
        db.close()
