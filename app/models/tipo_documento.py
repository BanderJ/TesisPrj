from app.bd import Connection

class TipoDocumento:
    def listar(self):
        db = Connection()
        try:
            sql = "SELECT id, nombre FROM tipo_documento ORDER BY nombre ASC"
            resultado = db.obtener(sql)
            return resultado
        finally:
            db.close()


        
    