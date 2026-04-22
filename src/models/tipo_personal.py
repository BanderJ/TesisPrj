from typing import Any

from src.database.bd import Connection


class TipoPersonal:
    def listar(self) -> list[dict[str, Any]]:
        """Lista todos los tipos de personal disponibles."""
        db = Connection()
        try:
            sql = "SELECT id, nombre FROM tipo_personal"
            return db.obtener(sql)
        finally:
            db.close()