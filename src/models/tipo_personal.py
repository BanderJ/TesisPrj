from src.bd import Connection

class TipoPersonal:
    def listar(self):
        db = Connection()
        try:
            sql = "SELECT id, nombre FROM tipo_personal"
            return db.obtener_todos(sql)
        finally:
            db.close()