from src.database.bd import Connection
from src.models import cooperativa as coop_model
from src.schemas.cooperativa import CooperativaCreate, CooperativaUpdate

_COOPERATIVA_DEFAULT_CODIGO = "LCM001"


def obtener_todas() -> list[dict]:
    db = Connection()
    try:
        return coop_model.obtener_todas(db)
    finally:
        db.close()


def obtener_por_id(cooperativa_id: str) -> dict | None:
    db = Connection()
    try:
        return coop_model.obtener_por_id(cooperativa_id, db)
    finally:
        db.close()


def obtener_por_codigo(codigo: str) -> dict | None:
    db = Connection()
    try:
        return coop_model.obtener_por_codigo(codigo, db)
    finally:
        db.close()


def crear(data: CooperativaCreate) -> dict:
    db = Connection()
    try:
        if data.codigo and coop_model.obtener_por_codigo(data.codigo, db):
            raise ValueError(f"El código '{data.codigo}' ya está en uso")
        result = coop_model.crear(
            nombre=data.nombre,
            codigo=data.codigo,
            direccion=data.direccion,
            telefono=data.telefono,
            correo=data.correo,
            descripcion=data.descripcion,
            imagen_url=data.imagen_url,
            db=db,
        )
        db.commit()
        return result
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def actualizar(cooperativa_id: str, data: CooperativaUpdate) -> dict | None:
    db = Connection()
    try:
        actual = coop_model.obtener_por_id(cooperativa_id, db)
        if not actual:
            return None
        if data.codigo and data.codigo != actual.get("codigo"):
            if coop_model.obtener_por_codigo(data.codigo, db):
                raise ValueError(f"El código '{data.codigo}' ya está en uso")
        result = coop_model.actualizar(
            cooperativa_id=cooperativa_id,
            nombre=data.nombre,
            codigo=data.codigo,
            direccion=data.direccion,
            telefono=data.telefono,
            correo=data.correo,
            descripcion=data.descripcion,
            imagen_url=data.imagen_url,
            db=db,
        )
        db.commit()
        return result
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def desactivar(cooperativa_id: str) -> dict | None:
    db = Connection()
    try:
        result = coop_model.desactivar(cooperativa_id, db)
        db.commit()
        return result
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def obtener_por_usuario(personal_id: str) -> dict | None:
    db = Connection()
    try:
        cooperativa = coop_model.obtener_cooperativa_de_usuario(personal_id, db)
        if cooperativa:
            return cooperativa

        default_id = coop_model.obtener_id_por_codigo(_COOPERATIVA_DEFAULT_CODIGO, db)
        if not default_id:
            return None

        coop_model.asignar_cooperativa_a_persona(personal_id, default_id, db)
        db.commit()
        return coop_model.obtener_por_id(default_id, db)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
