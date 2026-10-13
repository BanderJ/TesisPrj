import json
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
        evaluacion_id: str | None = None,
        codigo: str | None = None,
        db: Connection | None = None,
    ) -> dict[str, Any] | None:
        """Retorna resumen por evaluacion_id o por codigo. Exactamente uno debe especificarse."""
        owns_db = db is None
        db = db or Connection()
        try:
            sql = """
                SELECT
                    e.id::text                                              AS evaluacion_id,
                    COALESCE(TRIM(e.codigo), '')                           AS codigo,
                    p.num_documento,
                    TRIM(p.nombre) || ' ' || TRIM(p.ape_paterno)
                        || ' ' || TRIM(p.ape_materno)                      AS caficultor_nombre,
                    tc.nombre                                               AS tipo_caficultor,
                    tg.nombre                                               AS tipo_grano,
                    tg.peso_qq                                              AS peso_qq_grano,
                    TRIM(pe.nombre) || ' ' || TRIM(pe.ape_paterno)
                        || ' ' || TRIM(pe.ape_materno)                     AS registrado_por,
                    e.num_sacos,
                    e.peso_bruto,
                    e.humedad,
                    e.peso_muestra,
                    e.peso_trillado,
                    e.num_tamiz,
                    e.peso_tamizado,
                    TO_CHAR(e.fecha, 'DD/MM/YYYY HH24:MI')                AS fecha,
                    e.incidencias,
                    e.total_defectos,
                    e.total_buenos,
                    e.peso_bueno,
                    e.factor_rendimiento,
                    e.peso_por_qq,
                    e.pago,
                    e.bono_socio,
                    vc.precio,
                    vc.rango
                FROM evaluacion e
                JOIN persona          p   ON p.id              = e.caficultor_id
                JOIN tipo_caficultor  tc  ON tc.id             = e.tipo_caficultor_id
                JOIN tipo_grano       tg  ON tg.id             = e.tipo_grano_id
                JOIN personal         per ON per.personal_id   = e.personal_id
                JOIN persona          pe  ON pe.id             = per.personal_id
                LEFT JOIN valor_cafe  vc  ON vc.id             = e.valor_cafe_id
            """
            if evaluacion_id is not None:
                sql += " WHERE e.id = %s"
                return db.obtener_uno(sql, (evaluacion_id,))
            if codigo is None:
                raise ValueError("Debe especificarse evaluacion_id o codigo.")
            sql += " WHERE TRIM(e.codigo) = %s"
            return db.obtener_uno(sql, (codigo.upper(),))
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
                    e.id::text,
                    COALESCE(TRIM(e.codigo), '') AS codigo,
                    e.tipo_grano_id,
                    e.num_sacos,
                    e.peso_bruto,
                    e.humedad,
                    e.peso_muestra,
                    e.peso_trillado,
                    e.tipo_caficultor_id,
                    e.factor_rendimiento
                FROM evaluacion e
                WHERE e.id = %s
            """
            return db.obtener_uno(sql, (evaluacion_id,))
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
        peso_neto: Decimal,
        peso_por_qq: Decimal,
        pago: Decimal,
        bono_socio: Decimal,
        total_defectos: int,
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
                    bono_socio         = %s,
                    total_defectos     = %s,
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
                peso_por_qq, pago, bono_socio,
                total_defectos,
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

    def obtener_kpis(
        self,
        db: Connection | None = None,
    ) -> dict[str, Any]:
        owns_db = db is None
        db = db or Connection()
        try:
            sql = """
                SELECT
                    COUNT(*)                            AS total_lotes,
                    COALESCE(SUM(total_defectos), 0)    AS total_defectos,
                    ROUND(AVG(factor_rendimiento), 2)   AS rendimiento_promedio
                FROM evaluacion
                WHERE codigo IS NOT NULL and factor_rendimiento is NOT NULL
            """
            return db.obtener_uno(sql)
        finally:
            if owns_db:
                db.close()

    def asignar_codigo(
        self,
        evaluacion_id: str,
        total_defectos: int | None = None,
        total_buenos: int | None = None,
        incidencias: list | None = None,
        db: Connection | None = None,
    ) -> dict[str, Any]:
        """Genera el codigo EVA correlativo y lo asigna a la evaluacion. Retorna id y codigo.

        Idempotente: si la evaluacion ya tiene codigo (reintento de red o doble
        submit hacia /finalizar) reutiliza el existente en vez de generar otro
        y dejar huerfano el que ya vio/imprimio el operador.
        """
        owns_db = db is None
        db = db or Connection()
        try:
            existente = db.obtener_uno(
                "SELECT TRIM(codigo) AS codigo FROM evaluacion WHERE id = %s",
                (evaluacion_id,),
            )
            if existente is None:
                raise ValueError("Evaluacion no encontrada.")
            codigo = existente.get("codigo") or self._generar_codigo(db)
            incidencias_json = json.dumps(incidencias) if incidencias else None
            sql = """
                UPDATE evaluacion
                SET codigo         = %s,
                    fecha          = NOW(),
                    total_defectos = %s,
                    total_buenos   = %s,
                    incidencias    = %s::jsonb
                WHERE id = %s
                RETURNING id::text, codigo
            """
            cursor = db.ejecutar(sql, (codigo, total_defectos, total_buenos, incidencias_json, evaluacion_id))
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
