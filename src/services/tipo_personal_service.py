from src.models.tipo_personal import TipoPersonal

class TipoPersonalService:
    """Servicio para casos de uso de tipos de personal."""

    def __init__(self):
        self.tipo_personal_model = TipoPersonal()

    def listar_tipo_personal(self):
        """Obtiene tipos de personal desde la capa de acceso a datos."""
        return self.tipo_personal_model.listar()