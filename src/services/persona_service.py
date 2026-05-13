from src.models.persona import Persona
from src.schemas.dni import DniConsultaResponse


class PersonaService:
    def __init__(self) -> None:
        self._persona_model = Persona()

    def consultar_por_documento(self, num_documento: str) -> DniConsultaResponse:
        fila = self._persona_model.obtener_por_num_documento(num_documento)
        if not fila:
            return DniConsultaResponse(encontrado=False)

        fecha = fila.get("fecha_nacimiento")
        return DniConsultaResponse(
            encontrado=True,
            nombres=fila.get("nombre"),
            apellido_paterno=fila.get("ape_paterno"),
            apellido_materno=fila.get("ape_materno"),
            sexo=fila.get("sexo"),
            fecha_nacimiento=fecha.strftime("%Y-%m-%d") if fecha else None,
            ubigeo=fila.get("ubigeo"),
        )
