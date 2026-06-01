from src.database.bd import Connection


def obtener_todas(db: Connection) -> list[dict]:
    sql = "SELECT *, id AS cooperativa_id FROM COOPERATIVA WHERE estado='A' ORDER BY nombre"
    return db.obtener(sql)


def obtener_por_id(cooperativa_id: str, db: Connection = None) -> dict | None:
    sql = "SELECT *, id AS cooperativa_id FROM COOPERATIVA WHERE id=%s"
    return db.obtener_uno(sql, [cooperativa_id])


def obtener_por_codigo(codigo: str, db: Connection = None) -> dict | None:
    sql = "SELECT *, id AS cooperativa_id FROM COOPERATIVA WHERE codigo=%s AND estado='A'"
    return db.obtener_uno(sql, [codigo])


def obtener_id_por_codigo(codigo: str, db: Connection = None) -> str | None:
    sql = "SELECT id FROM COOPERATIVA WHERE codigo = %s LIMIT 1"
    result = db.obtener_uno(sql, [codigo])
    return str(result["id"]) if result else None


def obtener_cooperativa_de_usuario(personal_id: str, db: Connection) -> dict | None:
    """Retorna la cooperativa activa del usuario según su persona.cooperativa_id."""
    sql = """
        SELECT c.*, c.id AS cooperativa_id
        FROM COOPERATIVA c
        JOIN PERSONA p ON p.cooperativa_id = c.id
        WHERE p.id = %s AND c.estado = 'A'
        LIMIT 1
    """
    return db.obtener_uno(sql, [personal_id])


def asignar_cooperativa_a_persona(personal_id: str, cooperativa_id: str, db: Connection) -> None:
    """Asigna cooperativa_id a la persona. Sin commit — responsabilidad del servicio."""
    db.ejecutar("UPDATE PERSONA SET cooperativa_id = %s WHERE id = %s", [cooperativa_id, personal_id])


def crear(nombre: str, codigo: str | None, direccion: str | None, telefono: str | None,
          correo: str | None, descripcion: str | None = None, imagen_url: str | None = None,
          db: Connection = None) -> dict:
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


def actualizar(cooperativa_id: str, nombre: str | None = None, codigo: str | None = None,
               direccion: str | None = None, telefono: str | None = None,
               correo: str | None = None, descripcion: str | None = None,
               imagen_url: str | None = None, db: Connection = None) -> dict | None:
    owns_db = db is None
    db = db or Connection()
    try:
        updates = []
        params = []

        if nombre is not None:
            updates.append("nombre=%s")
            params.append(nombre)
        if codigo is not None:
            updates.append("codigo=%s")
            params.append(codigo)
        if direccion is not None:
            updates.append("direccion=%s")
            params.append(direccion)
        if telefono is not None:
            updates.append("telefono=%s")
            params.append(telefono)
        if correo is not None:
            updates.append("correo=%s")
            params.append(correo)
        if descripcion is not None:
            updates.append("descripcion=%s")
            params.append(descripcion)
        if imagen_url is not None:
            updates.append("imagen_url=%s")
            params.append(imagen_url)

        if not updates:
            return obtener_por_id(cooperativa_id, db)

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


def desactivar(cooperativa_id: str, db: Connection = None) -> dict | None:
    owns_db = db is None
    db = db or Connection()
    try:
        sql = "UPDATE COOPERATIVA SET estado='I' WHERE id=%s RETURNING *, id AS cooperativa_id"
        result = db.obtener_uno(sql, [cooperativa_id])
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
