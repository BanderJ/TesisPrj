from typing import Any

from src.models.tipo_caficultor import TipoCaficultor
from src.schemas.tipo_caficultor import TipoCaficultorResponse


class TipoCaficultorService:
    """Servicio para casos de uso de tipos de caficultor."""

    def __init__(self) -> None:
        self.tipo_caficultor_model: TipoCaficultor = TipoCaficultor()

    def listar_tipos_caficultor(self) -> list[TipoCaficultorResponse]:
        """Obtiene tipos de caficultor desde la capa de acceso a datos."""
        resultados: list[dict[str, Any]] = self.tipo_caficultor_model.listar()
        return [
            TipoCaficultorResponse(id=int(item["id"]), nombre=str(item["nombre"]))
            for item in resultados
        ]

    def obtener_id_por_nombre(self, nombre: str) -> int | None:
        """Retorna el ID del tipo de caficultor por nombre."""
        return self.tipo_caficultor_model.obtener_por_nombre(nombre)
