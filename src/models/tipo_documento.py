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
    
    def obtener_por_nombre(self, nombre: str) -> int | None:
        """Obtiene el ID de un tipo de documento por su nombre."""
        db = Connection()
        try:
            sql = "SELECT id from tipo_documento WHERE nombre = %s"
            resultado = db.obtener_uno(sql, (nombre,))
            return int(resultado["id"]) if resultado else None
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
     