from typing import Any

from src.database.bd import Connection


class Reporte:
    def conteo_personal_por_rol(self) -> list[dict[str, Any]]:
        """Cuenta usuarios activos agrupados por tipo de personal (rol)."""
        db = Connection()
        try:
            sql = """
                SELECT tp.nombre AS categoria, COUNT(*)::int AS cantidad
                FROM personal p
                INNER JOIN tipo_personal tp ON p.tipo_personal_id = tp.id
                WHERE p.estado = 'A'
                GROUP BY tp.nombre
                ORDER BY cantidad DESC
            """
            return db.obtener(sql)
        finally:
            db.close()

    def conteo_caficultores(self) -> int:
        """Cuenta caficultores cuya persona está activa."""
        db = Connection()
        try:
            sql = """
                SELECT COUNT(*)::int AS cantidad
                FROM caficultor c
                INNER JOIN persona pe ON c.caficultor_id = pe.id
                WHERE pe.estado = 'A'
            """
            resultado = db.obtener_uno(sql)
            return resultado["cantidad"] if resultado else 0
        finally:
            db.close()
