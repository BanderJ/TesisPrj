from src.database.bd import Connection


class Cooperativa:
    def obtener_todas(self, db: Connection | None = None) -> list[dict]:
        owns_db = db is None
        db = db or Connection()
        try:
            return db.obtener("SELECT *, id AS cooperativa_id FROM COOPERATIVA WHERE estado='A' ORDER BY nombre")
        finally:
            if owns_db:
                db.close()

    def obtener_por_id(self, cooperativa_id: str, db: Connection | None = None) -> dict | None:
        owns_db = db is None
        db = db or Connection()
        try:
            return db.obtener_uno("SELECT *, id AS cooperativa_id FROM COOPERATIVA WHERE id=%s", [cooperativa_id])
        finally:
            if owns_db:
                db.close()

    def obtener_por_codigo(self, codigo: str, db: Connection | None = None) -> dict | None:
        owns_db = db is None
        db = db or Connection()
        try:
            return db.obtener_uno(
                "SELECT *, id AS cooperativa_id FROM COOPERATIVA WHERE codigo=%s AND estado='A'",
                [codigo],
            )
        finally:
            if owns_db:
                db.close()

    def obtener_id_por_codigo(self, codigo: str, db: Connection | None = None) -> str | None:
        owns_db = db is None
        db = db or Connection()
        try:
            result = db.obtener_uno("SELECT id FROM COOPERATIVA WHERE codigo = %s LIMIT 1", [codigo])
            return str(result["id"]) if result else None
        finally:
            if owns_db:
                db.close()

    def obtener_cooperativa_de_usuario(self, personal_id: str, db: Connection) -> dict | None:
        sql = """
            SELECT c.*, c.id AS cooperativa_id
            FROM COOPERATIVA c
            JOIN PERSONA p ON p.cooperativa_id = c.id
            WHERE p.id = %s AND c.estado = 'A'
            LIMIT 1
        """
        return db.obtener_uno(sql, [personal_id])

    def asignar_cooperativa_a_persona(self, personal_id: str, cooperativa_id: str, db: Connection) -> None:
        db.ejecutar("UPDATE PERSONA SET cooperativa_id = %s WHERE id = %s", [cooperativa_id, personal_id])

    def crear(
        self,
        nombre: str,
        codigo: str | None,
        direccion: str | None,
        telefono: str | None,
        correo: str | None,
        descripcion: str | None = None,
        imagen_url: str | None = None,
        db: Connection | None = None,
    ) -> dict:
        owns_db = db is None
        db = db or Connection()
        try:
            sql = """
                INSERT INTO COOPERATIVA (nombre, codigo, direccion, telefono, correo, descripcion, imagen_url, estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'A')
                RETURNING *
            """
            result = db.obtener_uno(sql, [nombre, codigo, direccion, telefono, correo, descripcion, imagen_url])
            if result:
                result["cooperativa_id"] = str(result["id"])
            if owns_db:
                db.commit()
            return result
        except Exception:
            if owns_db:
                db.rollback()
            raise
        finally:
            if owns_db:
                db.close()

    def actualizar(
        self,
        cooperativa_id: str,
        nombre: str | None = None,
        codigo: str | None = None,
        direccion: str | None = None,
        telefono: str | None = None,
        correo: str | None = None,
        descripcion: str | None = None,
        imagen_url: str | None = None,
        db: Connection | None = None,
    ) -> dict | None:
        owns_db = db is None
        db = db or Connection()
        try:
            updates: list[str] = []
            params: list = []

            if nombre is not None:
                updates.append("nombre=%s"); params.append(nombre)
            if codigo is not None:
                updates.append("codigo=%s"); params.append(codigo)
            if direccion is not None:
                updates.append("direccion=%s"); params.append(direccion)
            if telefono is not None:
                updates.append("telefono=%s"); params.append(telefono)
            if correo is not None:
                updates.append("correo=%s"); params.append(correo)
            if descripcion is not None:
                updates.append("descripcion=%s"); params.append(descripcion)
            if imagen_url is not None:
                updates.append("imagen_url=%s"); params.append(imagen_url)

            if not updates:
                return self.obtener_por_id(cooperativa_id, db)

            params.append(cooperativa_id)
            sql = f"UPDATE COOPERATIVA SET {', '.join(updates)} WHERE id=%s RETURNING *, id AS cooperativa_id"
            result = db.obtener_uno(sql, params)
            if owns_db:
                db.commit()
            return result
        except Exception:
            if owns_db:
                db.rollback()
            raise
        finally:
            if owns_db:
                db.close()

    def desactivar(self, cooperativa_id: str, db: Connection | None = None) -> dict | None:
        owns_db = db is None
        db = db or Connection()
        try:
            result = db.obtener_uno(
                "UPDATE COOPERATIVA SET estado='I' WHERE id=%s RETURNING *, id AS cooperativa_id",
                [cooperativa_id],
            )
            if owns_db:
                db.commit()
            return result
        except Exception:
            if owns_db:
                db.rollback()
            raise
        finally:
            if owns_db:
                db.close()
