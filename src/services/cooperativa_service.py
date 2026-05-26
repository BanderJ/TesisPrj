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
    """Get cooperative associated with a user (via PERSONA.cooperativa_id)."""
    db = Connection()
    try:
        # Primero obtener cooperativa_id de la persona
        persona_sql = "SELECT cooperativa_id FROM PERSONA WHERE id = %s LIMIT 1"
        persona = db.obtener_uno(persona_sql, [personal_id])

        if not persona or not persona.get("cooperativa_id"):
            # Si no tiene cooperativa asignada, asignar la default
            default_coop_sql = "SELECT cooperativa_id FROM COOPERATIVA WHERE codigo = %s LIMIT 1"
            default_coop = db.obtener_uno(default_coop_sql, ["LCM001"])

            if default_coop:
                update_sql = "UPDATE PERSONA SET cooperativa_id = %s WHERE id = %s"
                db.ejecutar(update_sql, [default_coop["cooperativa_id"], personal_id])
                db.commit()
                persona_cooperativa = default_coop["cooperativa_id"]
            else:
                return None
        else:
            persona_cooperativa = persona["cooperativa_id"]

        # Obtener la cooperativa
        coop_sql = "SELECT * FROM COOPERATIVA WHERE cooperativa_id = %s AND estado = 'A' LIMIT 1"
        return db.obtener_uno(coop_sql, [persona_cooperativa])
    finally:
        db.close()
