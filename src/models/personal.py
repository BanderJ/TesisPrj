from src.database.bd import Connection
from typing import Any
from datetime import datetime

class Personal:
    def buscar_activo_por_usuario(self, usuario: str) -> dict[str, Any] | None:
        db = Connection()

        try:
            sql = """
                SELECT p.personal_id, p.tipo_personal_id, p.usuario, p.clave, p.estado,
                       pe.nombre, pe.ape_paterno, pe.ape_materno, tp.nombre as rol
                FROM personal p
                INNER JOIN persona pe ON p.personal_id = pe.id
                INNER JOIN tipo_personal tp ON p.tipo_personal_id = tp.id
                WHERE p.usuario = %s AND p.estado = 'A'
            """

            return db.obtener_uno(sql, (usuario,))
        finally:
            db.close()

    def obtener_clave_por_id(self, personal_id: str, db: Connection | None = None) -> dict[str, Any] | None:
        owns_db = db is None
        db = db or Connection()

        try:
            sql = "SELECT clave FROM personal WHERE personal_id = %s"
            return db.obtener_uno(sql, (personal_id,))
        finally:
            if owns_db:
                db.close()

    def actualizar_clave(
        self,
        personal_id: str,
        nueva_clave_hash: str,
        db: Connection | None = None,
    ) -> bool:
        owns_db = db is None
        db = db or Connection()

        try:
            sql = "UPDATE personal SET clave = %s WHERE personal_id = %s"
            cursor = db.ejecutar(sql, (nueva_clave_hash, personal_id))
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

    def obtener_todos_usuarios(self, db: Connection | None = None) -> list[dict[str, Any]]:
        owns_db = db is None
        db = db or Connection()

        try:
            sql = """
                SELECT p.personal_id, p.tipo_personal_id, p.usuario, p.estado, p.fecha_registro,
                       pe.id as persona_id, pe.nombre, pe.ape_paterno, pe.ape_materno,
                       pe.sexo, pe.fecha_nacimiento, pe.num_documento, pe.telefono, pe.correo,
                       tp.nombre as tipo_personal
                FROM personal p
                INNER JOIN persona pe ON p.personal_id = pe.id
                INNER JOIN tipo_personal tp ON p.tipo_personal_id = tp.id
                ORDER BY pe.nombre, pe.ape_paterno
            """
            return db.obtener(sql, ())
        finally:
            if owns_db:
                db.close()

    def obtener_usuario_por_id(self, personal_id: str, db: Connection | None = None) -> dict[str, Any] | None:
        owns_db = db is None
        db = db or Connection()

        try:
            sql = """
                SELECT p.personal_id, p.tipo_personal_id, p.usuario, p.estado, p.fecha_registro,
                       pe.id as persona_id, pe.nombre, pe.ape_paterno, pe.ape_materno,
                       pe.sexo, pe.fecha_nacimiento, pe.num_documento, pe.telefono, pe.correo,
                       pe.ubigeo,
                       tp.nombre as tipo_personal
                FROM personal p
                INNER JOIN persona pe ON p.personal_id = pe.id
                INNER JOIN tipo_personal tp ON p.tipo_personal_id = tp.id
                WHERE p.personal_id = %s
            """
            return db.obtener_uno(sql, (personal_id,))
        finally:
            if owns_db:
                db.close()

    def actualizar_tipo_personal(
        self,
        personal_id: str,
        tipo_personal_id: int,
        db: Connection | None = None,
    ) -> bool:
        owns_db = db is None
        db = db or Connection()
        try:
            sql = "UPDATE personal SET tipo_personal_id=%s WHERE personal_id=%s"
            cursor = db.ejecutar(sql, (tipo_personal_id, personal_id))
            actualizado = cursor.rowcount > 0
            if owns_db:
                db.commit() if actualizado else db.rollback()
            return actualizado
        except Exception:
            if owns_db:
                db.rollback()
            raise
        finally:
            if owns_db:
                db.close()

    def cambiar_estado(
        self,
        personal_id: str,
        nuevo_estado: str,
        db: Connection | None = None,
    ) -> bool:
        owns_db = db is None
        db = db or Connection()

        try:
            sql = "UPDATE personal SET estado = %s WHERE personal_id = %s"
            cursor = db.ejecutar(sql, (nuevo_estado, personal_id))
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

    def crear_usuario(
        self,
        persona_id: str,
        usuario: str,
        clave_hash: str,
        tipo_personal_id: int,
        db: Connection | None = None,
    ) -> str:
        owns_db = db is None
        db = db or Connection()

        try:
            sql = """
                INSERT INTO personal (personal_id, tipo_personal_id, usuario, clave, estado, fecha_registro)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING personal_id
            """
            resultado = db.obtener_uno(
                sql,
                (persona_id, tipo_personal_id, usuario, clave_hash, "A", datetime.now())
            )

            if not resultado or "personal_id" not in resultado:
                raise ValueError("No se pudo crear el usuario")

            if owns_db:
                db.commit()

            return str(resultado["personal_id"])
        except Exception:
            if owns_db:
                db.rollback()
            raise
        finally:
            if owns_db:
                db.close()

