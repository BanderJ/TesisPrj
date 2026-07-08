from src.database.bd import Connection
from typing import Any

class TipoDocumento:
    def listar(self) -> list[dict[str, Any]]:
        """Lista todos los tipos de documento disponibles."""
        db = Connection()
        try:
            sql = "SELECT id, nombre FROM tipo_documento"
            resultado = db.obtener(sql)
            return resultado
        finally:
            db.close()
    
    def obtener_por_id(self, tipo_documento_id: int) -> dict[str, Any] | None:
        """Obtiene un tipo de documento por su ID."""
        db = Connection()
        try:
            sql = "SELECT id, nombre FROM tipo_documento WHERE id = %s LIMIT 1"
            return db.obtener_uno(sql, (tipo_documento_id,))
        finally:
            db.close()
     