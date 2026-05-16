from decimal import Decimal
from typing import Any

from src.database.bd import Connection


class Evaluacion:
    def _generar_codigo(self, db: Connection) -> str:
        """Genera el siguiente correlativo EVA0000001 basado en el maximo existente."""
        sql = """
            SELECT COALESCE(
                MAX(CAST(SUBSTRING(codigo FROM 4) AS INTEGER)), 0
            ) + 1 AS siguiente
            FROM evaluacion
            WHERE codigo ~ '^EVA[0-9]{7}$'
        """
        row = db.obtener_uno(sql)
        return f"EVA{int(row['siguiente']):07d}" if row else "EVA0000001"

    def registrar(
        self,
        personal_id: str,
        caficultor_id: str,
        tipo_caficultor_id: int,
        num_sacos: int,
        peso_bruto: Decimal,
        humedad: int,
        peso_muestra: Decimal,
        peso_trillado: Decimal,
        num_tamiz: int,
        peso_tamizado: Decimal,
        tipo_grano_id: int,
        db: Connection | None = None,
    ) -> dict[str, Any]:
        """Inserta una evaluacion sin codigo ni valor_cafe (se asignan al finalizar). Retorna el id."""
        owns_db = db is None
        db = db or Connection()
        try:
            sql = """
                INSERT INTO evaluacion (
                    personal_id, caficultor_id, tipo_caficultor_id,
                    num_sacos, peso_bruto, humedad,
                    peso_muestra, peso_trillado, num_tamiz, peso_tamizado,
                    tipo_grano_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id::text
            """
            params = (
                personal_id, caficultor_id, tipo_caficultor_id,
                num_sacos, peso_bruto, humedad,
                peso_muestra, peso_trillado, num_tamiz, peso_tamizado,
                tipo_grano_id,
            )
            cursor = db.ejecutar(sql, params)
            fila = dict(cursor.fetchone())
            if owns_db:
                db.commit()
            return fila
        except Exception:
            if owns_db:
                db.rollback()
            raise
        finally:
            if owns_db:
                db.close()

    def obtener_codigo(
        self,
        evaluacion_id: str,
        db: Connection | None = None,
    ) -> dict[str, Any] | None:
        """Retorna el codigo de la evaluacion (NULL si aún no fue finalizada)."""
        owns_db = db is None
        db = db or Connection()
        try:
            return db.obtener_uno(
                "SELECT TRIM(codigo) AS codigo FROM evaluacion WHERE id = %s",
                (evaluacion_id,),
            )
        finally:
            if owns_db:
                db.close()

    def obtener_resumen(
        self,
        evaluacion_id: str,
        db: Connection | None = None,
    ) -> dict[str, Any] | None:
        owns_db = db is None
        db = db or Connection()
        try:
            sql = """
                SELECT
                    e.id::text                                              AS evaluacion_id,
                    COALESCE(TRIM(e.codigo), '')                            AS codigo,
                    p.num_documento,
                    TRIM(p.nombre) || ' ' || TRIM(p.ape_paterno)
                        || ' ' || TRIM(p.ape_materno)                       AS caficultor_nombre,
                    tc.nombre                                               AS tipo_caficultor,
                    tg.nombre                                               AS tipo_grano,
                    TRIM(pe.nombre) || ' ' || TRIM(pe.ape_paterno)
                        || ' ' || TRIM(p.ape_materno)                       AS registrado_por,
                    e.num_sacos,
                    e.peso_bruto,
                    e.humedad,
                    e.peso_muestra,
                    e.peso_trillado,
                    e.num_tamiz,
                    e.peso_tamizado,
                    TO_CHAR(e.fecha, 'DD/MM/YYYY HH24:MI')                           AS fecha
                FROM evaluacion e
                JOIN persona          p   ON p.id              = e.caficultor_id
                JOIN tipo_caficultor  tc  ON tc.id             = e.tipo_caficultor_id
                JOIN tipo_grano       tg  ON tg.id             = e.tipo_grano_id
                JOIN personal         per ON per.personal_id   = e.personal_id
                JOIN persona          pe  ON pe.id             = per.personal_id
                WHERE e.id = %s
            """
            return db.obtener_uno(sql, (evaluacion_id,))
        finally:
            if owns_db:
                db.close()

    def obtener_para_completar(
        self,
        evaluacion_id: str,
        db: Connection | None = None,
    ) -> dict[str, Any] | None:
        """Retorna los campos base de una evaluacion necesarios para calcular los derivados."""
        owns_db = db is None
        db = db or Connection()
        try:
            sql = """
                SELECT
                    id::text,
                    COALESCE(TRIM(codigo), '') AS codigo,
                    tipo_grano_id,
                    num_sacos,
                    peso_bruto,
                    peso_muestra,
                    peso_trillado
                FROM evaluacion
                WHERE id = %s
            """
            return db.obtener_uno(sql, (evaluacion_id,))
        finally:
            if owns_db:
                db.close()

    def obtener_categoria_por_defectos(
        self,
        total_defectos: int,
        db: Connection | None = None,
    ) -> dict[str, Any] | None:
        """Retorna la categoría correspondiente al total de defectos detectados."""
        owns_db = db is None
        db = db or Connection()
        try:
            sql = """
                SELECT id, nombre
                FROM categoria
                WHERE cantidad_defectos >= %s
                ORDER BY cantidad_defectos ASC
                LIMIT 1
            """
            return db.obtener_uno(sql, (total_defectos,))
        finally:
            if owns_db:
                db.close()

    def completar(
        self,
        evaluacion_id: str,
        codigo: str,
        valor_cafe_id: str,
        peso_cascara: Decimal,
        peso_cascara_total: Decimal,
        peso_bueno: Decimal,
        peso_malo: Decimal,
        factor_rendimiento: Decimal,
        tara_saco: Decimal,
        tara_total: int,
        peso_neto: int,
        peso_por_qq: Decimal,
        pago: Decimal,
        categoria_id: int | None,
        db: Connection | None = None,
    ) -> dict[str, Any]:
        """Actualiza la evaluacion con todos los campos derivados. Genera codigo si aún no tiene."""
        owns_db = db is None
        db = db or Connection()
        try:
            if not codigo:
                codigo = self._generar_codigo(db)
            sql = """
                UPDATE evaluacion
                SET
                    codigo             = %s,
                    valor_cafe_id      = %s::uuid,
                    peso_cascara       = %s,
                    peso_cascara_total = %s,
                    peso_bueno         = %s,
                    peso_malo          = %s,
                    factor_rendimiento = %s,
                    tara_saco          = %s,
                    tara_total         = %s,
                    peso_neto          = %s,
                    peso_por_qq        = %s,
                    pago               = %s,
                    categoria_id       = %s,
                    fecha              = NOW()
                WHERE id = %s
                RETURNING id::text, TRIM(codigo) AS codigo, pago, peso_por_qq, factor_rendimiento
            """
            params = (
                codigo, valor_cafe_id,
                peso_cascara, peso_cascara_total,
                peso_bueno, peso_malo,
                factor_rendimiento, tara_saco,
                tara_total, peso_neto,
                peso_por_qq, pago,
                categoria_id,
                evaluacion_id,
            )
            cursor = db.ejecutar(sql, params)
            row = cursor.fetchone()
            if not row:
                raise ValueError("Evaluación no encontrada.")
            fila = dict(row)
            if owns_db:
                db.commit()
            return fila
        except Exception:
            if owns_db:
                db.rollback()
            raise
        finally:
            if owns_db:
                db.close()

    def obtener_resumen_por_codigo(
        self,
        codigo: str,
        db: Connection | None = None,
    ) -> dict[str, Any] | None:
        owns_db = db is None
        db = db or Connection()
        try:
            sql = """
                SELECT
                    e.id::text                                                        AS evaluacion_id,
                    COALESCE(TRIM(e.codigo), '')                                     AS codigo,
                    p.num_documento,
                    TRIM(p.nombre) || ' ' || TRIM(p.ape_paterno)
                        || ' ' || TRIM(p.ape_materno)                                AS caficultor_nombre,
                    tc.nombre                                                         AS tipo_caficultor,
                    tg.nombre                                                         AS tipo_grano,
                    TRIM(pe.nombre) || ' ' || TRIM(pe.ape_paterno)                   AS registrado_por,
                    e.num_sacos,
                    e.peso_bruto,
                    e.humedad,
                    e.peso_muestra,
                    e.peso_trillado,
                    e.num_tamiz,
                    e.peso_tamizado,
                    TO_CHAR(e.fecha, 'DD/MM/YYYY HH24:MI')                           AS fecha
                FROM evaluacion e
                JOIN persona          p   ON p.id              = e.caficultor_id
                JOIN tipo_caficultor  tc  ON tc.id             = e.tipo_caficultor_id
                JOIN tipo_grano       tg  ON tg.id             = e.tipo_grano_id
                JOIN personal         per ON per.personal_id   = e.personal_id
                JOIN persona          pe  ON pe.id             = per.personal_id
                WHERE TRIM(e.codigo) = %s
            """
            return db.obtener_uno(sql, (codigo.upper(),))
        finally:
            if owns_db:
                db.close()

    def asignar_codigo(
        self,
        evaluacion_id: str,
        db: Connection | None = None,
    ) -> dict[str, Any]:
        """Genera el codigo EVA correlativo y lo asigna a la evaluacion. Retorna id y codigo."""
        owns_db = db is None
        db = db or Connection()
        try:
            codigo = self._generar_codigo(db)
            sql = """
                UPDATE evaluacion
                SET codigo = %s,
                    fecha  = NOW()
                WHERE id = %s
                RETURNING id::text, codigo
            """
            cursor = db.ejecutar(sql, (codigo, evaluacion_id))
            row = cursor.fetchone()
            if not row:
                raise ValueError("Evaluacion no encontrada.")
            fila = dict(row)
            if owns_db:
                db.commit()
            return fila
        except Exception:
            if owns_db:
                db.rollback()
            raise
        finally:
            if owns_db:
                db.close()
