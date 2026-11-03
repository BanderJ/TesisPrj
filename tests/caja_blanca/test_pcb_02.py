"""PCB-02 · obtener_usuario_actual(): validación de la sesión en cada petición (C1, C2 y C3)."""
from datetime import datetime, timedelta
from typing import Any, Iterator
from unittest.mock import patch

import jwt
import pytest
from fastapi import Depends, FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.testclient import TestClient

from src.config import Config
from src.utilities.jwt_required import RequerirLoginException, obtener_usuario_actual
from src.utilities.jwt_utils import generar_token

ID_ACTIVO = "0190a1b2-0000-7000-8000-000000000001"
ID_DESACTIVADO = "0190a1b2-0000-7000-8000-000000000002"


def _token(personal_id: str, usuario: str) -> str:
    return generar_token({"personal_id": personal_id, "usuario": usuario, "tipo_personal_id": 1})


@pytest.fixture
def cliente() -> Iterator[TestClient]:
    """App mínima con una ruta protegida por la dependencia real y el mismo manejo de
    RequerirLoginException que src/main.py (redirección 303 a /auth/login). El estado
    de la cuenta se simula en Personal.esta_activo."""
    app = FastAPI()

    @app.exception_handler(RequerirLoginException)
    async def _a_login(request: Request, exc: RequerirLoginException) -> RedirectResponse:
        return RedirectResponse(url="/auth/login", status_code=303)

    @app.get("/protegida")
    def protegida(usuario: dict[str, Any] = Depends(obtener_usuario_actual)) -> dict[str, Any]:
        return usuario

    with patch("src.services.auth_service.auth_service.personal_model.esta_activo",
               side_effect=lambda pid: pid == ID_ACTIVO):
        yield TestClient(app, follow_redirects=False)


def _redirige_a_login(cliente: TestClient) -> bool:
    r = cliente.get("/protegida")
    return r.status_code == 303 and r.headers["location"] == "/auth/login"


def test_c1_token_valido_y_cuenta_activa(cliente: TestClient) -> None:
    cliente.cookies.set("access_token", f"Bearer {_token(ID_ACTIVO, 'pcn_operario')}")
    r = cliente.get("/protegida")
    assert r.status_code == 200
    assert r.json()["personal_id"] == ID_ACTIVO
    assert r.json()["usuario"] == "pcn_operario"


def test_c2_token_ausente_alterado_o_expirado(cliente: TestClient) -> None:
    # Sin cookie access_token
    assert _redirige_a_login(cliente)
    # Token alterado: firma modificada
    token = _token(ID_ACTIVO, "pcn_operario")
    cliente.cookies.set("access_token", f"Bearer {token[:-4]}AAAA")
    assert _redirige_a_login(cliente)
    # Token expirado
    vencido = jwt.encode(
        {"personal_id": ID_ACTIVO, "exp": datetime.utcnow() - timedelta(minutes=1)},
        Config.SECRET_KEY, algorithm="HS256",
    )
    cliente.cookies.set("access_token", f"Bearer {vencido}")
    assert _redirige_a_login(cliente)


def test_c3_token_valido_cuenta_desactivada(cliente: TestClient) -> None:
    cliente.cookies.set("access_token", f"Bearer {_token(ID_DESACTIVADO, 'pcn_desactivado')}")
    assert _redirige_a_login(cliente)
