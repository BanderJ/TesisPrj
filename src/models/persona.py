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
                       tipo_documento_id, num_documento, telefono, estado
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
                    estado
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
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