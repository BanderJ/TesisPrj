import json
import urllib.error
import urllib.request
from typing import Any

from src.config import Config


class ReniecApi:
    """Cliente para la API de Factiliza - consulta datos de DNI."""

    _BASE_URL = "https://api.factiliza.com/v1/dni/info"

    @classmethod
    def consultar_dni(cls, dni: str) -> dict[str, Any] | None:
        """
        Consulta los datos de un DNI en Factiliza.

        Retorna el dict `data` de la respuesta si tiene exito,
        None si el DNI no fue encontrado (400) o la respuesta indica fallo.
        Lanza excepcion en errores de red o de configuracion.
        """
        token = Config.FACTILIZA_TOKEN
        if not token:
            raise RuntimeError("Token de Factiliza no configurado (API_FACTILIZA en .env)")

        url = f"{cls._BASE_URL}/{dni}"
        req = urllib.request.Request(
            url,
            headers={"Authorization": f"Bearer {token}"},
        )

        try:
            with urllib.request.urlopen(req, timeout=8) as response:
                body = response.read().decode("utf-8")
                parsed: dict[str, Any] = json.loads(body)
        except urllib.error.HTTPError as exc:
            if exc.code == 400:
                return None
            raise

        if not parsed.get("success"):
            return None

        return parsed.get("data") or None
