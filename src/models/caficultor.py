from src.database.bd import Connection
from typing import Any


class Caficultor:
    def obtener_por_num_documento(
        self,
        num_documento: str,
        db: Connection | None = None,
    ) -> dict[str, Any] | None:
        """Obtiene un caficultor activo por numero de documento."""
        owns_db = db is None
        db = db or Connection()

        try:
            sql = """
                SELECT
                    p.id AS persona_id,
                    p.num_documento,
                    p.nombre,
                    p.ape_paterno,
                    p.ape_materno,
                    tc.nombre AS tipo_caficultor,
                    c.tipo_caficultor_id,
                    p.sexo,
                    p.fecha_nacimiento,
                    p.telefono
                FROM persona p
                INNER JOIN caficultor c ON c.caficultor_id = p.id
                INNER JOIN tipo_caficultor tc ON tc.id = c.tipo_caficultor_id
                WHERE p.num_documento = %s
                  AND p.estado = 'A'
                LIMIT 1
            """
            return db.obtener_uno(sql, (num_documento,))
        finally:
            if owns_db:
                db.close()

    def obtener_por_persona_id(
        self,
        persona_id: str,
        db: Connection | None = None,
    ) -> dict[str, Any] | None:
        """Obtiene registro de caficultor por persona_id."""
        owns_db = db is None
        db = db or Connection()

        try:
            sql = """
                SELECT caficultor_id, tipo_caficultor_id, fecha_registro
                FROM caficultor
                WHERE caficultor_id = %s
                LIMIT 1
            """
            return db.obtener_uno(sql, (persona_id,))
        finally:
            if owns_db:
                db.close()
    
    def registrar_caficultor(
        self,
        persona_id: str,
        tipo_caficultor_id: int,
        db: Connection | None = None,
    ) -> None:
        """Registra un nuevo caficultor asociado a una persona existente."""
        owns_db = db is None
        db = db or Connection()

        try:
            sql = """
                INSERT INTO caficultor (caficultor_id, tipo_caficultor_id, fecha_registro)
                VALUES (%s, %s, NOW())
            """
            db.ejecutar(sql, (persona_id, tipo_caficultor_id))
            if owns_db:
                db.commit()
        except Exception:
            if owns_db:
                db.rollback()
            raise
        finally:
            if owns_db:
                db.close()

    def obtener_estado_y_tipo_por_num_documento(
        self,
        num_documento: str,
        db: Connection | None = None,
    ) -> dict[str, Any] | None:
        """Obtiene estado, tipo y nombre completo del caficultor por numero de documento."""
        owns_db = db is None
        db = db or Connection()

        try:
            sql = """
                SELECT
                    p.id AS persona_id,
                    p.estado,
                    p.nombre,
                    p.ape_paterno,
                    p.ape_materno,
                    c.tipo_caficultor_id,
                    tc.nombre AS tipo_caficultor
                FROM caficultor c
                INNER JOIN persona p ON c.caficultor_id = p.id
                INNER JOIN tipo_caficultor tc ON tc.id = c.tipo_caficultor_id
                WHERE p.num_documento = %s
                LIMIT 1
            """
            return db.obtener_uno(sql, (num_documento,))
        finally:
            if owns_db:
                db.close()

    def listar_todos(self, db: Connection | None = None) -> list[dict[str, Any]]:
        owns_db = db is None
        db = db or Connection()
        try:
            sql = """
                SELECT
                    p.id::text                                        AS persona_id,
                    p.num_documento,
                    TRIM(p.nombre)                                    AS nombre,
                    TRIM(p.ape_paterno)                               AS ape_paterno,
                    TRIM(p.ape_materno)                               AS ape_materno,
                    p.sexo,
                    TRIM(COALESCE(p.telefono, ''))                    AS telefono,
                    TO_CHAR(p.fecha_nacimiento, 'DD/MM/YYYY')         AS fecha_nacimiento,
                    COALESCE(p.ubigeo, '')                            AS ubigeo,
                    tc.nombre                                         AS tipo_caficultor,
                    c.tipo_caficultor_id,
                    TO_CHAR(c.fecha_registro, 'DD/MM/YYYY')           AS fecha_registro,
                    COALESCE(TRIM(u.departamento), '')                AS departamento,
                    COALESCE(TRIM(u.provincia), '')                   AS provincia,
                    COALESCE(TRIM(u.distrito), '')                    AS distrito
                FROM persona p
                INNER JOIN caficultor c       ON c.caficultor_id   = p.id
                INNER JOIN tipo_caficultor tc ON tc.id             = c.tipo_caficultor_id
                LEFT  JOIN ubigeo u           ON u.ubigeo          = p.ubigeo
                WHERE p.estado = 'A'
                ORDER BY p.ape_paterno, p.ape_materno, p.nombre
            """
            return db.obtener(sql)
        finally:
            if owns_db:
                db.close()

    def actualizar_tipo_caficultor_por_num_documento(
        self,
        num_documento: str,
        nuevo_tipo_caficultor_id: int,
        db: Connection | None = None,
    ) -> bool:
        """Actualiza el tipo de caficultor usando numero de documento.

        Retorna True si se actualizó al menos un registro, False si no se encontró.
        El caller es responsable del commit/rollback cuando pasa un db externo.
        """
        owns_db = db is None
        db = db or Connection()

        try:
            sql = """
                UPDATE caficultor c
                SET tipo_caficultor_id = %s
                FROM persona p
                WHERE c.caficultor_id = p.id
                  AND p.num_documento = %s
            """
            cursor = db.ejecutar(sql, (nuevo_tipo_caficultor_id, num_documento))
            actualizado = cursor.rowcount > 0

            if owns_db:
                if actualizado:
                    db.commit()
                else:
                    db.rollback()

            return actualizado
        except Exception:
            if owns_db:
                db.rollback()
            raise
        finally:
            if owns_db:
                db.close()
