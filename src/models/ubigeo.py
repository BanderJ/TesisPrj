from typing import Any

from src.database.bd import Connection


class Ubigeo:
    """Modelo de acceso a datos para la tabla UBIGEO.

    Los codigos siguen el estandar INEI: char(6) donde los 2 primeros
    identifican departamento, los 4 primeros la provincia y los 6 el distrito.
    """

    def listar_departamentos(self) -> list[dict[str, Any]]:
        db = Connection()
        try:
            sql = """
                SELECT DISTINCT SUBSTRING(ubigeo, 1, 2) AS codigo,
                                departamento AS nombre
                FROM ubigeo
                ORDER BY departamento
            """
            return db.obtener(sql)
        finally:
            db.close()

    def listar_provincias(self, departamento_codigo: str) -> list[dict[str, Any]]:
        db = Connection()
        try:
            sql = """
                SELECT DISTINCT SUBSTRING(ubigeo, 1, 4) AS codigo,
                                provincia AS nombre
                FROM ubigeo
                WHERE SUBSTRING(ubigeo, 1, 2) = %s
                ORDER BY provincia
            """
            return db.obtener(sql, (departamento_codigo,))
        finally:
            db.close()

    def listar_distritos(self, provincia_codigo: str) -> list[dict[str, Any]]:
        db = Connection()
        try:
            sql = """
                SELECT ubigeo AS codigo,
                       distrito AS nombre
                FROM ubigeo
                WHERE SUBSTRING(ubigeo, 1, 4) = %s
                ORDER BY distrito
            """
            return db.obtener(sql, (provincia_codigo,))
        finally:
            db.close()

    def obtener_por_codigo(self, ubigeo: str) -> dict[str, Any] | None:
        db = Connection()
        try:
            sql = """
                SELECT ubigeo, distrito, provincia, departamento
                FROM ubigeo
                WHERE ubigeo = %s
                LIMIT 1
            """
            return db.obtener_uno(sql, (ubigeo,))
        finally:
            db.close()
