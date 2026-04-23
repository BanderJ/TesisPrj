from datetime import date
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
                ORDER BY precio DESC
            """
            return db.obtener(sql, (fecha,))
        finally:
            db.close()
