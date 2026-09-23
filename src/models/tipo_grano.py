from decimal import Decimal
from src.database.bd import Connection
from typing import Any

class TipoGrano:
    def listar(self) -> list[dict[str, Any]]:
        db = Connection()
        try:
            return db.obtener("SELECT id, nombre, peso_qq FROM tipo_grano ORDER BY nombre")
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

    def crear(self, nombre: str, peso_qq: Decimal, db: Connection | None = None) -> dict[str, Any]:
        owns_db = db is None
        db = db or Connection()
        try:
            resultado = db.obtener_uno(
                "INSERT INTO tipo_grano (nombre, peso_qq) VALUES (%s, %s) RETURNING id, nombre, peso_qq",
                (nombre, peso_qq)
            )
            if owns_db:
                db.commit()
            return resultado
        finally:
            if owns_db:
                db.close()

    def actualizar(self, tipo_grano_id: int, nombre: str | None = None, peso_qq: Decimal | None = None, db: Connection | None = None) -> dict[str, Any] | None:
        owns_db = db is None
        db = db or Connection()
        try:
            campos = []
            valores = []
            if nombre is not None:
                campos.append("nombre = %s")
                valores.append(nombre)
            if peso_qq is not None:
                campos.append("peso_qq = %s")
                valores.append(peso_qq)

            if not campos:
                return db.obtener_uno("SELECT id, nombre, peso_qq FROM tipo_grano WHERE id = %s", (tipo_grano_id,))

            valores.append(tipo_grano_id)
            query = f"UPDATE tipo_grano SET {', '.join(campos)} WHERE id = %s RETURNING id, nombre, peso_qq"
            resultado = db.obtener_uno(query, valores)
            if owns_db and resultado:
                db.commit()
            return resultado
        finally:
            if owns_db:
                db.close()

    def eliminar(self, tipo_grano_id: int, db: Connection | None = None) -> bool:
        owns_db = db is None
        db = db or Connection()
        try:
            cursor = db.ejecutar("DELETE FROM tipo_grano WHERE id = %s", (tipo_grano_id,))
            eliminado = cursor.rowcount > 0
            if owns_db:
                if eliminado:
                    db.commit()
                else:
                    db.rollback()
            return eliminado
        finally:
            if owns_db:
                db.close()
