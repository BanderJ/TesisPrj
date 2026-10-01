import json
from typing import Any

from src.database.bd import Connection


class EventoMonitoreo:
    """Traza de lo que el sistema informó al operario durante un lote.

    Se escribe una sola vez, al finalizar la evaluación (el monitoreo mantiene
    los eventos en memoria), y se lee desde el análisis y desde el reporte por
    código.
    """

    def registrar_lote(
        self,
        evaluacion_id: str,
        eventos: list[dict[str, Any]],
        db: Connection | None = None,
    ) -> int:
        """Reemplaza la traza del lote. Retorna cuántos eventos se guardaron.

        Idempotente igual que Evaluacion.asignar_codigo: un reintento de red o
        un doble submit sobre /finalizar no debe dejar la traza duplicada en el
        historial. Se borra la traza previa de esa evaluacion y se reinserta.
        """
        if not eventos:
            return 0

        owns_db = db is None
        db = db or Connection()
        try:
            db.ejecutar(
                "DELETE FROM evento_monitoreo WHERE evaluacion_id = %s",
                (evaluacion_id,),
            )
            sql = """
                INSERT INTO evento_monitoreo
                    (evaluacion_id, segundo, tipo, severidad, mensaje, imagen_url, datos)
                VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb)
            """
            for evento in eventos:
                datos = evento.get("datos")
                db.ejecutar(sql, (
                    evaluacion_id,
                    int(evento.get("segundo") or 0),
                    evento.get("tipo"),
                    evento.get("severidad"),
                    evento.get("mensaje"),
                    evento.get("imagen_url"),
                    json.dumps(datos) if datos else None,
                ))
            if owns_db:
                db.commit()
            return len(eventos)
        except Exception:
            if owns_db:
                db.rollback()
            raise
        finally:
            if owns_db:
                db.close()

    def listar_por_evaluacion(
        self,
        evaluacion_id: str,
        db: Connection | None = None,
    ) -> list[dict[str, Any]]:
        """Eventos de una evaluacion en orden cronologico."""
        owns_db = db is None
        db = db or Connection()
        try:
            sql = """
                SELECT segundo, tipo, severidad, mensaje, imagen_url, datos
                FROM evento_monitoreo
                WHERE evaluacion_id = %s
                ORDER BY segundo, id
            """
            return db.obtener(sql, (evaluacion_id,))
        finally:
            if owns_db:
                db.close()
