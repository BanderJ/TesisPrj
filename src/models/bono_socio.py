from decimal import Decimal
from typing import Any

from src.database.bd import Connection


class BonoSocio:
    _SELECT = """
        SELECT b.id::text, b.monto, TO_CHAR(b.fecha, 'DD/MM/YYYY HH24:MI') AS fecha,
               TRIM(p.nombre) || ' ' || TRIM(p.ape_paterno) AS registrado_por
        FROM bono_socio b
        LEFT JOIN persona p ON p.id = b.personal_id
    """

    def listar(self, limite: int | None = None, db: Connection | None = None) -> list[dict[str, Any]]:
        """Historial del beneficio, del más reciente al más antiguo; el primero es el vigente."""
        owns_db = db is None
        db = db or Connection()
        try:
            sql = self._SELECT + " ORDER BY b.fecha DESC"
            params: list[Any] = []
            if limite:
                sql += " LIMIT %s"
                params.append(limite)
            return db.obtener(sql, params)
        finally:
            if owns_db:
                db.close()

    def registrar(self, monto: Decimal, personal_id: str, db: Connection | None = None) -> dict[str, Any]:
        owns_db = db is None
        db = db or Connection()
        try:
            fila = db.obtener_uno(
                "INSERT INTO bono_socio (monto, personal_id) VALUES (%s, %s::uuid) RETURNING id::text",
                (monto, personal_id),
            )
            if owns_db:
                db.commit()
            return fila
        finally:
            if owns_db:
                db.close()
