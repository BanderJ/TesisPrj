#Conexion DATABASE_URI = 'postgresql://user:password@localhost:5432/mydatabase'
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key_here'

    USER = 'postgres'
    PASSWORD = 'admin'
    HOST = 'localhost'
    PORT = '5432'
    DATABASE = 'mydatabase'
