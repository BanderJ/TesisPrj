from src.database.bd import Connection
from typing import Any

class TipoGrano:
    def listar(self) -> list[dict[str, Any]]:
        db = Connection()
        try:
            return db.obtener("SELECT id, nombre FROM tipo_grano ORDER BY nombre")
        finally:
            db.close()
