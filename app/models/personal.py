from app.bd import Connection
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

class Personal:
    def __init__(self):
        self.ph = PasswordHasher(memory_cost=65536, time_cost=3, parallelism=4)

    def login(self, usuario, clave):
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
            
            resultado = db.obtener_uno(sql, (usuario,))
            
            if resultado:
                try:
                    self.ph.verify(resultado['clave'], clave)
                    # Eliminamos la clave del dict por seguridad antes de devolverlo
                    del resultado['clave']
                    return resultado
                except VerifyMismatchError:
                    return None
            return None
        finally:
            db.close()

