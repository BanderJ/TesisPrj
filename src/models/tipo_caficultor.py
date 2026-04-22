from src.database.bd import Connection
from typing import Any

class TipoCaficultor:
    def listar(self) -> list[dict[str, Any]]:
        """Lista todos los tipos de caficultor disponibles."""
        db = Connection()
        try:
            sql = "SELECT id, nombre FROM tipo_caficultor"
            return db.obtener(sql)
        finally:
            db.close()
    
    def obtener_por_nombre(self, nombre: str) -> int | None:
        """Obtiene el ID de un tipo de caficultor por su nombre."""
        db = Connection()
        try:
            sql = "SELECT id from tipo_caficultor WHERE nombre = %s"
            resultado = db.obtener_uno(sql, (nombre,))
            return int(resultado["id"]) if resultado else None
        finally:
            db.close()

    def obtener_por_id(self, tipo_caficultor_id: int) -> dict[str, Any] | None:
        """Obtiene un tipo de caficultor por su ID."""
        db = Connection()
        try:
            sql = "SELECT id, nombre FROM tipo_caficultor WHERE id = %s LIMIT 1"
            return db.obtener_uno(sql, (tipo_caficultor_id,))
        finally:
            db.close()