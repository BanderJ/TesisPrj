from src.database.bd import Connection
from typing import Any

class Personal:
    def buscar_activo_por_usuario(self, usuario: str) -> dict[str, Any] | None:
        db = Connection()
        
        try:
            sql = """
                SELECT p.personal_id, p.tipo_personal_id, p.usuario, p.clave, p.estado, 
                       pe.nombre, pe.ape_paterno, pe.ape_materno, tp.nombre as rol
                FROM personal p
                INNER JOIN persona pe ON p.personal_id = pe.id
                INNER JOIN tipo_personal tp ON p.tipo_personal_id = tp.id
                WHERE p.usuario = %s AND p.estado = 'A'
            """

            return db.obtener_uno(sql, (usuario,))
        finally:
            db.close()

