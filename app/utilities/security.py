from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import re

# Instancia global (Reutilizable y eficiente)
# Aquí puedes configurar los parámetros de seguridad que mencionamos
ph = PasswordHasher(memory_cost=65536, time_cost=3, parallelism=4)

def hash_password(password_plain: str) -> str:
    return ph.hash(password_plain)

def verify_password(hash_stored: str, password_plain: str) -> bool:
    try:
        return ph.verify(hash_stored, password_plain)
    except VerifyMismatchError:
        return False

def password_validate(password: str):
    rules = [
        (len(password) >= 8, "al menos 8 caracteres"),
        (re.search(r'[A-Z]', password), "letras mayúsculas"),
        (re.search(r'\d', password), "números"),
        (re.search(r'[!@#%^&*(),.=?":{}$¿?¡]', password), "caracteres especiales")
    ]
    
    for passed, message in rules:
        if not passed:
            return False, f"La contraseña debe contener {message}"
            
    return True, 'Contraseña válida'