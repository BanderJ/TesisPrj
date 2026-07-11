from typing import Any

from src.models.tipo_documento import TipoDocumento
from src.schemas.tipo_documento import TipoDocumentoResponse


class TipoDocumentoService:
    """Servicio para casos de uso de tipos de documento."""

    def __init__(self) -> None:
        self.tipo_documento_model: TipoDocumento = TipoDocumento()

    def listar_tipos_documento(self) -> list[TipoDocumentoResponse]:
        """Obtiene tipos de documento desde la capa de acceso a datos."""
        resultados: list[dict[str, Any]] = self.tipo_documento_model.listar()
        return [
            TipoDocumentoResponse(id=int(item["id"]), nombre=str(item["nombre"]))
            for item in resultados
        ]
