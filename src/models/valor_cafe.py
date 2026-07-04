from datetime import date
from decimal import Decimal
from typing import Any

from src.database.bd import Connection


class ValorCafe:
    def obtener_historial_dia(self, fecha: date, rango: str | None = None) -> list[dict[str, Any]]:
        db = Connection()
        try:
            sql = "SELECT id::text, rango, precio, fecha FROM valor_cafe WHERE fecha::date = %s"
            params: list[Any] = [fecha]
            if rango:
                sql += " AND rango = %s"
                params.append(rango)
            sql += " ORDER BY fecha DESC"
            return db.obtener(sql, params)
        finally:
            db.close()

    def obtener_maximo_dia(self, fecha: date) -> dict[str, Any] | None:
        db = Connection()
        try:
            sql = """
                SELECT id::text, rango, precio, fecha
                FROM valor_cafe
                WHERE fecha::date = %s
                ORDER BY precio DESC, fecha DESC
                LIMIT 1
            """
            return db.obtener_uno(sql, (fecha,))
        finally:
            db.close()

    def obtener_cambios_diarios(self, desde: date, hasta: date, rango: str | None = None) -> list[dict[str, Any]]:
        db = Connection()
        try:
            sql = """
                SELECT fecha::date AS fecha, MAX(precio) AS precio_maximo
                FROM valor_cafe
                WHERE fecha::date BETWEEN %s AND %s
            """
            params: list[Any] = [desde, hasta]
            if rango:
                sql += " AND rango = %s"
                params.append(rango)
            sql += " GROUP BY fecha::date ORDER BY fecha::date ASC"
            return db.obtener(sql, params)
        finally:
            db.close()

    def obtener_resumen_rangos(self, fecha: date) -> list[dict[str, Any]]:
        db = Connection()
        try:
            sql = """
                SELECT rango, MAX(precio) AS precio, MAX(fecha) AS registrado_en
                FROM valor_cafe
                WHERE fecha::date = %s
                GROUP BY rango
                ORDER BY CAST(SPLIT_PART(rango, '-', 1) AS INTEGER) ASC
            """
            return db.obtener(sql, (fecha,))
        finally:
            db.close()

    def obtener_mas_reciente(self, db: Connection | None = None) -> dict[str, Any] | None:
        """Retorna el registro de valor_cafe más reciente por fecha."""
        owns_db = db is None
        db = db or Connection()
        try:
            sql = """
                SELECT id::text, rango, precio, fecha
                FROM valor_cafe
                ORDER BY fecha DESC
                LIMIT 1
            """
            return db.obtener_uno(sql)
        finally:
            if owns_db:
                db.close()

    def obtener_por_factor(self, factor: Decimal, db: Connection | None = None) -> dict[str, Any] | None:
        """Retorna el precio más reciente cuyo rango contiene el factor de rendimiento.
        El rango puede ser 'X-Y' (ej: 70-75) o un número simple 'X' (ej: 70)."""
        owns_db = db is None
        db = db or Connection()
        try:
            sql = """
                SELECT id::text, rango, precio, fecha
                FROM valor_cafe
                WHERE CAST(SPLIT_PART(rango, '-', 1) AS numeric) <= %s
                  AND CAST(COALESCE(NULLIF(SPLIT_PART(rango, '-', 2), ''), SPLIT_PART(rango, '-', 1)) AS numeric) >= %s
                ORDER BY fecha DESC
                LIMIT 1
            """
            return db.obtener_uno(sql, (factor, factor))
        finally:
            if owns_db:
                db.close()

    def eliminar_por_rango_fecha(
        self, rango: str, fecha: date, db: Connection | None = None
    ) -> int:
        """Elimina todos los registros de un rango en una fecha. Retorna cantidad eliminada."""
        owns_db = db is None
        db = db or Connection()
        try:
            cursor = db.ejecutar(
                "DELETE FROM valor_cafe WHERE rango = %s AND fecha::date = %s",
                (rango, fecha),
            )
            if owns_db:
                db.commit()
            return cursor.rowcount
        except Exception:
            if owns_db:
                db.rollback()
            raise
        finally:
            if owns_db:
                db.close()

    def crear(self, rango: str, precio: float, db: Connection | None = None) -> dict[str, Any]:
        """Inserta un nuevo registro de valor_cafe. Retorna el registro creado."""
        owns_db = db is None
        db = db or Connection()
        try:
            sql = """
                INSERT INTO valor_cafe (rango, precio, fecha)
                VALUES (%s, %s, NOW())
                RETURNING id::text, rango, precio, fecha
            """
            fila = db.obtener_uno(sql, (rango, precio))
            if owns_db:
                db.commit()
            return fila
        except Exception:
            if owns_db:
                db.rollback()
            raise
        finally:
            if owns_db:
                db.close()

    def crear_bloque(self, precios: list[tuple[str, float]]) -> list[dict[str, Any]]:
        """Inserta multiples registros de valor_cafe en una sola operacion."""
        db = Connection()
        try:
            placeholders = ", ".join(["(%s, %s, NOW())"] * len(precios))
            params: list[Any] = []
            for rango, precio in precios:
                params.extend([rango, precio])

            sql = f"""
                INSERT INTO valor_cafe (rango, precio, fecha)
                VALUES {placeholders}
                RETURNING id::text, rango, precio, fecha
            """
            filas = db.obtener(sql, params)
            db.commit()
            return filas
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
