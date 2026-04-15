from src.bd import Connection


class Caficultor:
    def obtener_por_num_documento(self, num_documento):
        """Obtiene un caficultor activo por numero de documento."""
        db = Connection()
        try:
            sql = """
                SELECT
                    p.id AS persona_id,
                    p.num_documento,
                    p.nombre,
                    p.ape_paterno,
                    p.ape_materno,
                    tc.nombre AS tipo_caficultor
                FROM persona p
                INNER JOIN caficultor c ON c.caficultor_id = p.id
                INNER JOIN tipo_caficultor tc ON tc.id = c.tipo_caficultor_id
                WHERE p.num_documento = %s
                  AND p.estado = 'A'
                LIMIT 1
            """
            resultado = db.obtener_uno(sql, (num_documento,))
            return resultado
        finally:
            db.close()
