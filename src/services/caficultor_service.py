from src.models.caficultor import Caficultor


class CaficultorService:
    """Servicio para casos de uso relacionados con caficultores."""

    def __init__(self):
        self.caficultor_model = Caficultor()

    def obtener_caficultor_por_documento(self, num_documento):
        """Retorna datos de caficultor por documento o None si no existe."""
        resultado = self.caficultor_model.obtener_por_num_documento(num_documento)

        if not resultado:
            return None

        nombre_completo = (
            f"{resultado['nombre']} {resultado['ape_paterno']} {resultado['ape_materno']}"
        )

        return {
            "persona_id": str(resultado["persona_id"]),
            "num_documento": resultado["num_documento"],
            "nombre_completo": nombre_completo,
            "tipo_caficultor": resultado["tipo_caficultor"],
        }