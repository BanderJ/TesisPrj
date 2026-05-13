from src.database.bd import Connection
from typing import Any

class TipoGrano:
    def listar(self) -> list[dict[str, Any]]:
        db = Connection()
        try:
            return db.obtener("SELECT id, nombre FROM tipo_grano ORDER BY nombre")
        finally:
            db.close()

    def obtener_por_id(self, tipo_grano_id: int, db: Connection | None = None) -> dict[str, Any] | None:
        owns_db = db is None
        db = db or Connection()
        try:
            return db.obtener_uno("SELECT id, nombre, peso_qq FROM tipo_grano WHERE id = %s", (tipo_grano_id,))
        finally:
            if owns_db:
                db.close()
