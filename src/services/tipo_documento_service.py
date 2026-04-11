from src.models.tipo_documento import TipoDocumento


class TipoDocumentoService:
    """Servicio para casos de uso de tipos de documento."""

    def __init__(self):
        self.tipo_documento_model = TipoDocumento()

    def listar_tipos_documento(self):
        """Obtiene tipos de documento desde la capa de acceso a datos."""
        return self.tipo_documento_model.listar()
