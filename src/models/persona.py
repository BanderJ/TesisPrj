from src.bd import Connection

class Persona:
    def registrar(self, nombre, ape_paterno, ape_materno, tipo_documento_id, numero_documento):
        db = Connection()
        try:
            sql = """
                INSERT INTO persona (nombre, ape_paterno, ape_materno, tipo_documento_id, numero_documento)
                VALUES (%s, %s, %s, %s, %s) RETURNING id
            """
            resultado = db.obtener_uno(sql, (nombre, ape_paterno, ape_materno, tipo_documento_id, numero_documento))
            return resultado['id'] if resultado else None
        finally:
            db.close()