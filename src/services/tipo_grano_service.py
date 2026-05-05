from typing import Any

from src.models.tipo_grano import TipoGrano
from src.schemas.tipo_grano import TipoGranoResponse


class TipoGranoService:
    def __init__(self) -> None:
        self.tipo_grano_model = TipoGrano()

    def listar_tipos_grano(self) -> list[TipoGranoResponse]:
        resultados: list[dict[str, Any]] = self.tipo_grano_model.listar()
        return [
            TipoGranoResponse(id=int(item["id"]), nombre=str(item["nombre"]))
            for item in resultados
        ]
