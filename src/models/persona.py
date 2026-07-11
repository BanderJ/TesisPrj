from datetime import date
from typing import Any

from src.database.bd import Connection


class Persona:
    def obtener_por_num_documento(
        self,
        num_documento: str,
        db: Connection | None = None,
    ) -> dict[str, Any] | None:
        owns_db = db is None
        db = db or Connection()

        try:
            sql = """
                SELECT id, nombre, ape_paterno, ape_materno, sexo, fecha_nacimiento,
                       tipo_documento_id, num_documento, telefono, ubigeo, cooperativa_id, estado
                FROM persona
                WHERE num_documento = %s
                  AND estado = 'A'
                LIMIT 1
            """
            return db.obtener_uno(sql, (num_documento,))
        finally:
            if owns_db:
                db.close()

    def registrar(
        self,
        nombre: str,
        ape_paterno: str,
        ape_materno: str,
        sexo: str,
        fecha_nacimiento: date,
        tipo_documento_id: int,
        num_documento: str,
        telefono: str | None,
        correo: str | None = None,
        ubigeo: str | None = None,
        cooperativa_id: str | None = None,
        db: Connection | None = None,
    ) -> str:
        owns_db = db is None
        db = db or Connection()

        try:
            sql = """
                INSERT INTO persona (
                    nombre,
                    ape_paterno,
                    ape_materno,
                    sexo,
                    fecha_nacimiento,
                    tipo_documento_id,
                    num_documento,
                    telefono,
                    correo,
                    ubigeo,
                    cooperativa_id,
                    estado
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """
            resultado = db.obtener_uno(
                sql,
                (
                    nombre,
                    ape_paterno,
                    ape_materno,
                    sexo,
                    fecha_nacimiento,
                    tipo_documento_id,
                    num_documento,
                    telefono,
                    correo,
                    ubigeo,
                    cooperativa_id,
                    "A",
                ),
            )

            if not resultado or "id" not in resultado:
                raise ValueError("No se pudo registrar la persona")

            if owns_db:
                db.commit()

            return str(resultado["id"])
        except Exception:
            if owns_db:
                db.rollback()
            raise
        finally:
            if owns_db:
                db.close()

    def actualizar_ubigeo(
        self,
        persona_id: str,
        ubigeo: str,
        db: Connection | None = None,
    ) -> None:
        owns_db = db is None
        db = db or Connection()

        try:
            sql = "UPDATE persona SET ubigeo = %s WHERE id = %s"
            db.ejecutar(sql, (ubigeo, persona_id))
            if owns_db:
                db.commit()
        except Exception:
            if owns_db:
                db.rollback()
            raise
        finally:
            if owns_db:
                db.close()

    def actualizar_completo(
        self,
        persona_id: str,
        nombre: str,
        ape_paterno: str,
        ape_materno: str,
        sexo: str,
        fecha_nacimiento: date,
        telefono: str | None,
        correo: str | None,
        ubigeo: str | None,
        db: Connection | None = None,
    ) -> bool:
        owns_db = db is None
        db = db or Connection()
        try:
            sql = """
                UPDATE persona
                SET nombre=%s, ape_paterno=%s, ape_materno=%s, sexo=%s,
                    fecha_nacimiento=%s, telefono=%s, correo=%s, ubigeo=%s
                WHERE id=%s
            """
            cursor = db.ejecutar(sql, (nombre, ape_paterno, ape_materno, sexo,
                                       fecha_nacimiento, telefono, correo, ubigeo, persona_id))
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

    def actualizar_datos_personales(
        self,
        persona_id: str,
        nombre: str,
        ape_paterno: str,
        ape_materno: str,
        telefono: str | None,
        correo: str | None = None,
        db: Connection | None = None,
    ) -> bool:
        owns_db = db is None
        db = db or Connection()

        try:
            sql = """
                UPDATE persona
                SET nombre = %s, ape_paterno = %s, ape_materno = %s, telefono = %s, correo = %s
                WHERE id = %s
            """
            cursor = db.ejecutar(sql, (nombre, ape_paterno, ape_materno, telefono, correo, persona_id))
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

    def obtener_personas_sin_usuario(self, db: Connection | None = None) -> list[dict[str, Any]]:
        owns_db = db is None
        db = db or Connection()

        try:
            sql = """
                SELECT p.id, p.nombre, p.ape_paterno, p.ape_materno, p.sexo,
                       p.fecha_nacimiento, p.num_documento, p.telefono, p.correo, p.estado
                FROM persona p
                LEFT JOIN personal pr ON p.id = pr.personal_id
                WHERE pr.personal_id IS NULL AND p.estado = 'A'
                ORDER BY p.nombre, p.ape_paterno
            """
            return db.obtener(sql, ())
        finally:
            if owns_db:
                db.close()

    def obtener_datos_perfil_completo(self, personal_id: str, db: Connection | None = None) -> dict[str, Any] | None:
        owns_db = db is None
        db = db or Connection()
        try:
            sql = """
                SELECT pe.nombre, pe.ape_paterno, pe.ape_materno, pe.telefono,
                       COALESCE(pe.correo, '') AS correo,
                       pe.num_documento, pe.sexo, pe.fecha_nacimiento,
                       p.usuario, p.estado, p.fecha_registro, p.tipo_personal_id,
                       tp.nombre AS rol
                FROM persona pe
                INNER JOIN personal p ON pe.id = p.personal_id
                INNER JOIN tipo_personal tp ON p.tipo_personal_id = tp.id
                WHERE pe.id = %s
            """
            return db.obtener_uno(sql, (personal_id,))
        finally:
            if owns_db:
                db.close()