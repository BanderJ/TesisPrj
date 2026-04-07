import os
import psycopg2
import psycopg2.extras
from app.config import Config
from datetime import date, datetime
from decimal import Decimal

class Connection:

    def __init__(self):
        """Inicializa la conexión a PostgreSQL con autocommit=False para transacciones"""
        try:
            self.conn = psycopg2.connect(
                user=Config.USER,
                password=Config.PASSWORD,
                host=Config.HOST,
                port=Config.PORT,
                database=Config.DATABASE
            )
            # En psycopg2, autocommit es una propiedad del objeto conexión, no un parámetro de conexión
            self.conn.autocommit = False 
            self.cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            print("Conexión a PostgreSQL exitosa")
        except Exception as e:
            print(f"Error al conectar a PostgreSQL: {e}")
            raise

    def get_connection(self):
        """Retorna la conexión actual"""
        return self.conn

    def get_cursor(self):
        """Retorna el cursor actual"""
        return self.cursor

    def ejecutar(self, query, params=None):
        """
        Ejecuta INSERT, UPDATE, DELETE.
        NO hace commit automático - el usuario debe llamar a commit() o rollback()
        esto permite agrupar múltiples operaciones en una transacción.
        """
        try:
            self.cursor.execute(query, params or ())
            # Para INSERT, retorna lastrowid si se usa RETURNING id
            return self.cursor
        except Exception as e:
            print(f"Error en ejecutar: {e}")
            self.rollback()
            raise

    def obtener(self, query, params=None):
        """
        Ejecuta SELECT y retorna una lista de diccionarios.
        Parsea DATETIME y DECIMAL automáticamente.
        """
        try:
            self.cursor.execute(query, params or ())
            resultados = self.cursor.fetchall()
            return [dict(row) for row in resultados]
        except Exception as e:
            print(f"Error en obtener: {e}")
            raise

    def obtener_uno(self, query, params=None):
        """Retorna un solo registro como diccionario o None"""
        try:
            self.cursor.execute(query, params or ())
            resultado = self.cursor.fetchone()
            return dict(resultado) if resultado else None
        except Exception as e:
            print(f"Error en obtener_uno: {e}")
            raise

    def begin(self):
        """
        Inicia una transacción explícita.
        En PostgreSQL con autocommit=False no es obligatorio, pero ayuda a claridad.
        """
        self.conn.autocommit = False

    def commit(self):
        """Confirma todos los cambios de la transacción actual"""
        try:
            self.conn.commit()
            print("Conexión a PostgreSQL exitosa")
        except Exception as e:
            print(f"Error en commit: {e}")
            self.rollback()
            raise

    def rollback(self):
        """Revierte todos los cambios de la transacción actual"""
        try:
            self.conn.rollback()
            print("Conexión a PostgreSQL exitosa")
        except Exception as e:
            print(f"Error en rollback: {e}")

    def close(self):
        """Cierra el cursor y la conexión"""
        try:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()
            print("Conexión a PostgreSQL exitosa")
        except Exception as e:
            print(f"Error al cerrar conexión: {e}")


# Función auxiliar para obtener una conexión rápidamente
def obtener_conexion():
    """Retorna una nueva instancia de Connection"""
    return Connection()

