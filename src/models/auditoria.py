import json

from src.database.bd import Connection


class Auditoria:
    def registrar(
        self,
        accion: str,
        personal_id: str | None = None,
        usuario: str | None = None,
        tipo_personal_id: int | None = None,
        rol: str | None = None,
        tabla_afectada: str | None = None,
        registro_id: str | None = None,
        descripcion: str | None = None,
        datos_anteriores: dict | None = None,
        datos_nuevos: dict | None = None,
        ip_cliente: str | None = None,
        db: Connection | None = None,
    ) -> None:
        owns_db = db is None
        db = db or Connection()
        try:
            db.ejecutar(
                """
                INSERT INTO AUDITORIA
                    (personal_id, usuario, tipo_personal_id, rol, accion,
                     tabla_afectada, registro_id, descripcion,
                     datos_anteriores, datos_nuevos, ip_cliente)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                [
                    personal_id,
                    usuario,
                    tipo_personal_id,
                    rol,
                    accion,
                    tabla_afectada,
                    registro_id,
                    descripcion,
                    json.dumps(datos_anteriores, default=str) if datos_anteriores else None,
                    json.dumps(datos_nuevos, default=str) if datos_nuevos else None,
                    ip_cliente,
                ],
            )
            if owns_db:
                db.commit()
        finally:
            if owns_db:
                db.close()

    def obtener_filtrado(
        self,
        personal_id: str | None = None,
        tipo_personal_id: int | None = None,
        accion: str | None = None,
        usuario: str | None = None,
        fecha_desde: str | None = None,
        fecha_hasta: str | None = None,
        pagina: int = 1,
        limite: int = 50,
        db: Connection | None = None,
    ) -> tuple[list[dict], int]:
        owns_db = db is None
        db = db or Connection()
        try:
            where: list[str] = ["1=1"]
            params: list = []

            if personal_id:
                where.append("personal_id = %s")
                params.append(personal_id)
            if tipo_personal_id:
                where.append("tipo_personal_id = %s")
                params.append(tipo_personal_id)
            if accion:
                where.append("accion = %s")
                params.append(accion)
            if usuario:
                where.append("usuario ILIKE %s")
                params.append(f"%{usuario}%")
            if fecha_desde:
                where.append("fecha_hora >= %s")
                params.append(fecha_desde)
            if fecha_hasta:
                where.append("fecha_hora <= %s")
                params.append(f"{fecha_hasta} 23:59:59")

            where_sql = " AND ".join(where)
            offset = (pagina - 1) * limite

            total_row = db.obtener_uno(
                f"SELECT COUNT(*) AS total FROM AUDITORIA WHERE {where_sql}",
                params,
            )
            total = int(total_row["total"]) if total_row else 0

            registros = db.obtener(
                f"""
                SELECT id, personal_id, usuario, tipo_personal_id, rol,
                       accion, tabla_afectada, registro_id, descripcion,
                       datos_anteriores, datos_nuevos, ip_cliente, fecha_hora
                FROM AUDITORIA
                WHERE {where_sql}
                ORDER BY fecha_hora DESC
                LIMIT %s OFFSET %s
                """,
                params + [limite, offset],
            )
            return registros or [], total
        finally:
            if owns_db:
                db.close()

    def obtener_usuarios_auditados(self, db: Connection | None = None) -> list[dict]:
        owns_db = db is None
        db = db or Connection()
        try:
            return db.obtener(
                """
                SELECT DISTINCT personal_id, usuario, tipo_personal_id, rol
                FROM AUDITORIA
                WHERE usuario IS NOT NULL
                ORDER BY usuario
                """,
                [],
            ) or []
        finally:
            if owns_db:
                db.close()

    def obtener_acciones_disponibles(self, db: Connection | None = None) -> list[str]:
        owns_db = db is None
        db = db or Connection()
        try:
            rows = db.obtener(
                "SELECT DISTINCT accion FROM AUDITORIA ORDER BY accion",
                [],
            ) or []
            return [r["accion"] for r in rows]
        finally:
            if owns_db:
                db.close()
