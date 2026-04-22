from typing import Any

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

from src.models.personal import Personal
from src.schemas.auth import LoginResponse
from src.utilities.jwt_utils import generar_token, verificar_token


class AuthService:
    """Servicio que centraliza la logica de autenticacion."""

    def __init__(self) -> None:
        self.personal_model: Personal = Personal()
        self.password_hasher: PasswordHasher = PasswordHasher(
            memory_cost=65536,
            time_cost=3,
            parallelism=4,
        )

    def sesion_activa(self, token_cookie: str | None) -> bool:
        """Valida si el token de cookie representa una sesion activa."""
        if not token_cookie or not token_cookie.startswith("Bearer "):
            return False

        token = token_cookie.split(" ")[1]
        return verificar_token(token) is not None

    def autenticar(self, usuario: str, clave: str) -> LoginResponse | None:
        """Autentica credenciales y retorna el objeto de respuesta si son validas."""
        usuario_db: dict[str, Any] | None = self.personal_model.buscar_activo_por_usuario(usuario)

        if not usuario_db:
            return None

        clave_hash: str | None = usuario_db.get("clave")
        if not clave_hash:
            return None

        try:
            self.password_hasher.verify(clave_hash, clave)
        except (VerifyMismatchError, VerificationError, InvalidHashError):
            return None

        usuario_db.pop("clave", None)

        nombre_completo = (
            f"{usuario_db['nombre']} "
            f"{usuario_db['ape_paterno']} "
            f"{usuario_db['ape_materno']}"
        )
        payload = {
            "personal_id": str(usuario_db["personal_id"]),
            "usuario": usuario_db["usuario"],
            "rol": usuario_db["rol"],
            "nombre": nombre_completo,
        }
        token = generar_token(payload)

        return LoginResponse(
            personal_id=str(usuario_db["personal_id"]),
            usuario=usuario_db["usuario"],
            rol=usuario_db["rol"],
            nombre=nombre_completo,
            token=token,
        )
