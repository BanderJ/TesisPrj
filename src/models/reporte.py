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

    def conteo_caficultores_por_tipo(self) -> list[dict[str, Any]]:
        """Cuenta caficultores activos agrupados por tipo (Socio / No socio).

        LEFT JOIN desde tipo_caficultor: los tipos sin caficultores aparecen con 0.
        """
        db = Connection()
        try:
            sql = """
                SELECT tc.nombre AS categoria,
                       COUNT(pe.id)::int AS cantidad
                FROM tipo_caficultor tc
                LEFT JOIN caficultor c ON c.tipo_caficultor_id = tc.id
                LEFT JOIN persona pe ON pe.id = c.caficultor_id AND pe.estado = 'A'
                GROUP BY tc.nombre
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
