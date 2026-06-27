from src.database.bd import Connection
from src.models.cooperativa import Cooperativa
from src.schemas.cooperativa import CooperativaCreate, CooperativaUpdate

_COOPERATIVA_DEFAULT_CODIGO = "LCM001"


class CooperativaService:
    def __init__(self) -> None:
        self.model = Cooperativa()

    def obtener_todas(self) -> list[dict]:
        db = Connection()
        try:
            return self.model.obtener_todas(db)
        finally:
            db.close()

    def obtener_por_id(self, cooperativa_id: str) -> dict | None:
        db = Connection()
        try:
            return self.model.obtener_por_id(cooperativa_id, db)
        finally:
            db.close()

    def obtener_por_codigo(self, codigo: str) -> dict | None:
        db = Connection()
        try:
            return self.model.obtener_por_codigo(codigo, db)
        finally:
            db.close()

    def crear(self, data: CooperativaCreate) -> dict:
        db = Connection()
        try:
            if data.codigo and self.model.obtener_por_codigo(data.codigo, db):
                raise ValueError(f"El código '{data.codigo}' ya está en uso")
            result = self.model.crear(
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

    def actualizar(self, cooperativa_id: str, data: CooperativaUpdate) -> dict | None:
        db = Connection()
        try:
            actual = self.model.obtener_por_id(cooperativa_id, db)
            if not actual:
                return None
            if data.codigo and data.codigo != actual.get("codigo"):
                if self.model.obtener_por_codigo(data.codigo, db):
                    raise ValueError(f"El código '{data.codigo}' ya está en uso")
            result = self.model.actualizar(
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

    def desactivar(self, cooperativa_id: str) -> dict | None:
        db = Connection()
        try:
            result = self.model.desactivar(cooperativa_id, db)
            db.commit()
            return result
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def obtener_por_usuario(self, personal_id: str) -> dict | None:
        db = Connection()
        try:
            cooperativa = self.model.obtener_cooperativa_de_usuario(personal_id, db)
            if cooperativa:
                return cooperativa

            default_id = self.model.obtener_id_por_codigo(_COOPERATIVA_DEFAULT_CODIGO, db)
            if not default_id:
                return None

            self.model.asignar_cooperativa_a_persona(personal_id, default_id, db)
            db.commit()
            return self.model.obtener_por_id(default_id, db)
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()


cooperativa_service = CooperativaService()
