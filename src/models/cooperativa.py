"""
Cooperativa Model - Coffee cooperative data access layer
"""
from src.database.bd import Connection


def obtener_todas(db: Connection) -> list[dict]:
    """Get all active cooperatives."""
    sql = "SELECT * FROM COOPERATIVA WHERE estado='A' ORDER BY nombre"
    return db.obtener(sql)


def obtener_por_id(cooperativa_id: str, db: Connection = None) -> dict | None:
    """Get cooperative by ID."""
    sql = "SELECT * FROM COOPERATIVA WHERE cooperativa_id=%s"
    return db.obtener_uno(sql, [cooperativa_id])


def obtener_por_codigo(codigo: str, db: Connection = None) -> dict | None:
    """Get cooperative by codigo (unique)."""
    sql = "SELECT * FROM COOPERATIVA WHERE codigo=%s AND estado='A'"
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
    return db.obtener_uno(sql, [nombre, codigo, direccion, telefono, correo, descripcion, imagen_url])


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
    sql = f"UPDATE COOPERATIVA SET {', '.join(updates)} WHERE cooperativa_id=%s RETURNING *"
    return db.obtener_uno(sql, params)


def desactivar(cooperativa_id: str, db: Connection = None) -> dict | None:
    """Deactivate a cooperative (soft delete)."""
    sql = "UPDATE COOPERATIVA SET estado='I' WHERE cooperativa_id=%s RETURNING *"
    return db.obtener_uno(sql, [cooperativa_id])
