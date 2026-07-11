from typing import Any

from src.models.tipo_caficultor import TipoCaficultor
from src.schemas.tipo_caficultor import TipoCaficultorResponse


class TipoCaficultorService:
    """Servicio para casos de uso de tipos de caficultor."""

    def __init__(self) -> None:
        self.tipo_caficultor_model: TipoCaficultor = TipoCaficultor()

    TIPO_SOCIO_ID: int = 1

    def listar_tipos_caficultor(self) -> list[TipoCaficultorResponse]:
        """Obtiene tipos de caficultor desde la capa de acceso a datos."""
        resultados: list[dict[str, Any]] = self.tipo_caficultor_model.listar()
        return [
            TipoCaficultorResponse(
                id=int(item["id"]),
                nombre=str(item["nombre"]),
                is_socio=int(item["id"]) == self.TIPO_SOCIO_ID,
            )
            for item in resultados
        ]
