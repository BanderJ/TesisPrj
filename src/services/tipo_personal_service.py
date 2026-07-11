from typing import Any

from src.models.tipo_personal import TipoPersonal
from src.schemas.tipo_personal import TipoPersonalResponse

class TipoPersonalService:
    """Servicio para casos de uso de tipos de personal."""

    def __init__(self) -> None:
        self.tipo_personal_model: TipoPersonal = TipoPersonal()

    def listar_tipo_personal(self) -> list[TipoPersonalResponse]:
        """Obtiene tipos de personal desde la capa de acceso a datos."""
        resultados: list[dict[str, Any]] = self.tipo_personal_model.listar()
        return [
            TipoPersonalResponse(id=int(item["id"]), nombre=str(item["nombre"]))
            for item in resultados
        ]