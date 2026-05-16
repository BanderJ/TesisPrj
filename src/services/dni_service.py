from typing import Any

from src.apis.reniec_api import ReniecApi
from src.schemas.dni import DniConsultaResponse


class DniService:
    def consultar_dni(self, dni: str) -> DniConsultaResponse:
        data: dict[str, Any] | None = ReniecApi.consultar_dni(dni)
        if data is None:
            return DniConsultaResponse(encontrado=False)
        return DniConsultaResponse(encontrado=True, **data)
