from typing import Any

from src.database.bd import Connection
from src.schemas.reporte import FiltrosReporte


class Reporte:
    def evaluaciones(self, filtros: FiltrosReporte, resumen: bool = False) -> dict[str, Any]:
        """Consulta entregas con código EVA; conserva el tipo registrado en la entrega."""
        condiciones = ["e.codigo IS NOT NULL"]
        params: list[Any] = []
        if resumen:
            condiciones.append("e.factor_rendimiento IS NOT NULL")
        if filtros.desde:
            condiciones.append("e.fecha >= %s::date")
            params.append(filtros.desde)
        if filtros.hasta:
            condiciones.append("e.fecha < %s::date + INTERVAL '1 day'")
            params.append(filtros.hasta)
        if filtros.tipo_caficultor:
            condiciones.append("tc.nombre = %s")
            params.append(filtros.tipo_caficultor)
        if filtros.busqueda:
            condiciones.append("""(
                STRPOS(LOWER(CONCAT_WS(' ', p.nombre, p.ape_paterno, p.ape_materno)), LOWER(%s)) > 0
                OR STRPOS(p.num_documento, %s) > 0
            )""")
            params.extend([filtros.busqueda, filtros.busqueda])
        origen = """
            FROM evaluacion e
            JOIN persona p ON p.id = e.caficultor_id
            JOIN tipo_caficultor tc ON tc.id = e.tipo_caficultor_id
            WHERE
        """ + " AND ".join(condiciones)
        db = Connection()
        try:
            if resumen:
                filas = db.obtener("""
                    SELECT TO_CHAR(e.fecha::date, 'YYYY-MM-DD') AS fecha,
                           COUNT(*)::int AS evaluaciones,
                           SUM(e.peso_bruto) AS kilos_recibidos,
                           SUM(e.pago) AS pagos,
                           SUM(COALESCE(e.bono_socio, 0)) AS beneficios
                """ + origen + " GROUP BY e.fecha::date ORDER BY e.fecha::date DESC", params)
                return {"filas": filas, "total": len(filas)}
            conteo = db.obtener_uno("SELECT COUNT(*)::int AS total " + origen, params)
            filas = db.obtener("""
                SELECT e.id::text AS evaluacion_id, TRIM(e.codigo) AS codigo,
                       TO_CHAR(e.fecha, 'YYYY-MM-DD HH24:MI') AS fecha,
                       CONCAT_WS(' ', p.nombre, p.ape_paterno, p.ape_materno) AS caficultor,
                       p.num_documento AS documento, tc.nombre AS tipo_caficultor,
                       e.num_sacos, e.peso_bruto, e.peso_neto,
                       e.peso_muestra, e.peso_trillado, e.peso_tamizado, e.peso_bueno,
                       e.factor_rendimiento, e.pago, e.bono_socio
            """ + origen + " ORDER BY e.fecha DESC, e.id DESC LIMIT %s OFFSET %s",
                params + [filtros.por_pagina, (filtros.pagina - 1) * filtros.por_pagina])
            return {"filas": filas, "total": conteo["total"] if conteo else 0}
        finally:
            db.close()

    def conteo_personal_por_rol(self) -> list[dict[str, Any]]:
        """Cuenta usuarios activos agrupados por tipo de personal (rol)."""
        db = Connection()
        try:
            sql = """
                SELECT tp.nombre AS categoria, COUNT(*)::int AS cantidad
                FROM personal p
                INNER JOIN tipo_personal tp ON p.tipo_personal_id = tp.id
                WHERE p.estado = 'A'
                GROUP BY tp.nombre
                ORDER BY cantidad DESC
            """
            return db.obtener(sql)
        finally:
            db.close()

    def conteo_caficultores_por_tipo(self) -> list[dict[str, Any]]:
        """Cuenta caficultores activos agrupados por tipo (Socio / No socio).

        LEFT JOIN desde tipo_caficultor: los tipos sin caficultores aparecen con 0.
        """
        db = Connection()
        try:
            sql = """
                SELECT tc.nombre AS categoria,
                       COUNT(pe.id)::int AS cantidad
                FROM tipo_caficultor tc
                LEFT JOIN caficultor c ON c.tipo_caficultor_id = tc.id
                LEFT JOIN persona pe ON pe.id = c.caficultor_id AND pe.estado = 'A'
                GROUP BY tc.nombre
                ORDER BY cantidad DESC
            """
            return db.obtener(sql)
        finally:
            db.close()

    def conteo_caficultores(self) -> int:
        """Cuenta caficultores cuya persona está activa."""
        db = Connection()
        try:
            sql = """
                SELECT COUNT(*)::int AS cantidad
                FROM caficultor c
                INNER JOIN persona pe ON c.caficultor_id = pe.id
                WHERE pe.estado = 'A'
            """
            resultado = db.obtener_uno(sql)
            return resultado["cantidad"] if resultado else 0
        finally:
            db.close()
