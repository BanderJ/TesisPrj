"""
Cooperativa Model - Coffee cooperative data access layer
"""
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


def crear(nombre: str, codigo: str | None, direccion: str | None, telefono: str | None,
          correo: str | None, descripcion: str | None = None, imagen_url: str | None = None,
          db: Connection = None) -> dict:
    """Create a new cooperative."""
    sql = """
    INSERT INTO COOPERATIVA (nombre, codigo, direccion, telefono, correo, descripcion, imagen_url, estado)
    VALUES (%s, %s, %s, %s, %s, %s, %s, 'A')
    RETURNING *
    """
    result = db.obtener_uno(sql, [nombre, codigo, direccion, telefono, correo, descripcion, imagen_url])
    if result:
        result["cooperativa_id"] = str(result["id"])
    db.commit()
    return result


def actualizar(cooperativa_id: str, nombre: str | None = None, codigo: str | None = None,
               direccion: str | None = None, telefono: str | None = None,
               correo: str | None = None, descripcion: str | None = None,
               imagen_url: str | None = None, db: Connection = None) -> dict | None:
    """Update cooperative data (only non-None fields)."""
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
    db.commit()
    return result


def desactivar(cooperativa_id: str, db: Connection = None) -> dict | None:
    sql = "UPDATE COOPERATIVA SET estado='I' WHERE id=%s RETURNING *, id AS cooperativa_id"
    result = db.obtener_uno(sql, [cooperativa_id])
    db.commit()
    return result


def obtener_id_por_codigo(codigo: str, db: Connection = None) -> str | None:
    sql = "SELECT id FROM COOPERATIVA WHERE codigo = %s LIMIT 1"
    result = db.obtener_uno(sql, [codigo])
    return str(result["id"]) if result else None


def obtener_por_usuario(personal_id: str, db: Connection = None) -> dict | None:
    """Get cooperative associated with a user, with default assignment if needed."""
    # Obtener cooperativa_id de la persona
    persona_sql = "SELECT cooperativa_id FROM PERSONA WHERE id = %s LIMIT 1"
    persona = db.obtener_uno(persona_sql, [personal_id])

    if not persona or not persona.get("cooperativa_id"):
        # Asignar cooperativa default si no tiene
        default_coop_sql = "SELECT id FROM COOPERATIVA WHERE codigo = %s LIMIT 1"
        default_coop = db.obtener_uno(default_coop_sql, ["LCM001"])

        if default_coop:
            update_sql = "UPDATE PERSONA SET cooperativa_id = %s WHERE id = %s"
            db.ejecutar(update_sql, [default_coop["id"], personal_id])
            db.commit()
            persona_cooperativa = default_coop["id"]
        else:
            return None
    else:
        persona_cooperativa = persona["cooperativa_id"]

    # Obtener la cooperativa
    coop_sql = "SELECT *, id AS cooperativa_id FROM COOPERATIVA WHERE id = %s AND estado = 'A' LIMIT 1"
    return db.obtener_uno(coop_sql, [persona_cooperativa])
