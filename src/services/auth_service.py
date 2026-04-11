from typing import Optional

from src.models.personal import Personal
from src.schemas.auth import LoginResponse
from src.utilities.jwt_utils import generar_token, verificar_token


class AuthService:
    """Servicio que centraliza la logica de autenticacion."""

    def __init__(self):
        self.personal_model = Personal()

    def sesion_activa(self, token_cookie: Optional[str]) -> bool:
        """Valida si el token de cookie representa una sesion activa."""
        if not token_cookie or not token_cookie.startswith("Bearer "):
            return False

        token = token_cookie.split(" ")[1]
        return verificar_token(token) is not None

    def autenticar(self, usuario: str, clave: str) -> Optional[LoginResponse]:
        """Autentica credenciales y retorna el objeto de respuesta si son validas."""
        usuario_valido = self.personal_model.login(usuario, clave)

        if not usuario_valido:
            return None

        nombre_completo = (
            f"{usuario_valido['nombre']} "
            f"{usuario_valido['ape_paterno']} "
            f"{usuario_valido['ape_materno']}"
        )
        payload = {
            "personal_id": str(usuario_valido["personal_id"]),
            "usuario": usuario_valido["usuario"],
            "rol": usuario_valido["rol"],
            "nombre": nombre_completo,
        }
        token = generar_token(payload)

        return LoginResponse(
            personal_id=str(usuario_valido["personal_id"]),
            usuario=usuario_valido["usuario"],
            rol=usuario_valido["rol"],
            nombre=nombre_completo,
            token=token,
        )
