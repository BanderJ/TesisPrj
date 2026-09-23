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
        if not token_cookie:
            return False
        token = token_cookie.split(" ")[-1] if token_cookie.startswith("Bearer ") else token_cookie
        payload = verificar_token(token)
        if payload is None:
            return False
        # Una cuenta desactivada con cookie aun vigente no debe considerarse
        # "con sesion activa": si no, /auth/login la redirige a "/" y "/" la
        # devuelve a /auth/login por obtener_usuario_actual, en un loop infinito.
        return self.cuenta_habilitada(payload.get("personal_id"))

    def cuenta_habilitada(self, personal_id: str | None) -> bool:
        """True si la cuenta existe y sigue activa en la BD.

        El JWT es válido 7 días aunque la cuenta se desactive en ese lapso; esto
        permite cortar la sesión en cuanto el estado deja de ser 'A'. Ante un
        fallo transitorio de BD devuelve True para no expulsar por un error de
        infraestructura (el token sigue siendo criptográficamente válido).
        """
        if not personal_id:
            return False
        try:
            return self.personal_model.esta_activo(personal_id)
        except Exception:
            return True

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
            "personal_id":    str(usuario_db["personal_id"]),
            "usuario":        usuario_db["usuario"],
            "tipo_personal_id": usuario_db["tipo_personal_id"],
            "rol":            usuario_db["rol"],
            "nombre":         nombre_completo,
            "is_admin":       int(usuario_db["tipo_personal_id"]) in (2, 3),
        }
        token = generar_token(payload)

        return LoginResponse(
            personal_id=str(usuario_db["personal_id"]),
            usuario=usuario_db["usuario"],
            rol=usuario_db["rol"],
            nombre=nombre_completo,
            token=token,
        )


auth_service = AuthService()
