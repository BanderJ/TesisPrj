"""PCB-01 · AuthService.autenticar(): inicio de sesión (caminos C1, C2 y C3)."""
from unittest.mock import MagicMock

import pytest
from argon2 import PasswordHasher

from src.services.auth_service import AuthService
from src.utilities.jwt_utils import verificar_token

CLAVE = "Operario#2026"


@pytest.fixture
def servicio() -> AuthService:
    """AuthService con el model Personal simulado: pcn_operario activo, clave en Argon2."""
    s = AuthService()
    s.personal_model = MagicMock()
    usuarios = {
        "pcn_operario": {
            "personal_id": "0190a1b2-0000-7000-8000-000000000001",
            "tipo_personal_id": 1,
            "usuario": "pcn_operario",
            "clave": PasswordHasher().hash(CLAVE),
            "estado": "A",
            "nombre": "Operario",
            "ape_paterno": "Prueba",
            "ape_materno": "PCB",
            "rol": "Evaluador",
        }
    }
    # Igual que buscar_activo_por_usuario: devuelve una fila nueva o None.
    s.personal_model.buscar_activo_por_usuario.side_effect = (
        lambda u: dict(usuarios[u]) if u in usuarios else None
    )
    return s


def test_c1_credenciales_correctas_devuelve_token(servicio: AuthService) -> None:
    respuesta = servicio.autenticar("pcn_operario", CLAVE)
    assert respuesta is not None
    payload = verificar_token(respuesta.token)
    assert payload["personal_id"] == "0190a1b2-0000-7000-8000-000000000001"
    assert payload["usuario"] == "pcn_operario"
    assert payload["rol"] == "Evaluador"


def test_c2_usuario_inexistente_sin_token(servicio: AuthService) -> None:
    assert servicio.autenticar("usuario_inexistente", "cualquier_valor") is None


def test_c3_clave_incorrecta_sin_token(servicio: AuthService) -> None:
    assert servicio.autenticar("pcn_operario", "ClaveIncorrecta#1") is None
