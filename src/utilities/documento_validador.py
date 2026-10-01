import re
import unicodedata

from src.models.tipo_documento import TipoDocumento

_tipo_documento_model = TipoDocumento()


def _normalizar_nombre_tipo_documento(nombre: str) -> str:
    """Normaliza texto para comparar nombres de tipos de documento."""
    texto = unicodedata.normalize("NFD", nombre)
    texto = "".join(ch for ch in texto if unicodedata.category(ch) != "Mn")
    return texto.strip().lower()


def validar_documento_por_tipo(tipo_documento_id: int, num_documento: str) -> None:
    """Valida num_documento en funcion del tipo de documento registrado.

    Regla de negocio (compartida por registro de caficultores y de personal
    del sistema): DNI exactamente 8 digitos numericos; Pasaporte, Carnet de
    extranjeria y cualquier otro tipo, 8 a 12 caracteres alfanumericos.
    Lanza ValueError con un mensaje listo para mostrar al usuario.
    """
    tipo_documento = _tipo_documento_model.obtener_por_id(tipo_documento_id)
    if not tipo_documento:
        raise ValueError("El tipo de documento seleccionado no existe.")

    nombre_tipo = _normalizar_nombre_tipo_documento(str(tipo_documento.get("nombre", "")))

    if nombre_tipo == "dni":
        if not num_documento.isdigit() or len(num_documento) != 8:
            raise ValueError("El DNI debe tener exactamente 8 dígitos numéricos.")
        return

    if nombre_tipo in {"pasaporte", "carnet de extranjeria"}:
        if not re.fullmatch(r"[A-Za-z0-9]{8,12}", num_documento):
            raise ValueError(
                "El pasaporte o carnet de extranjería debe tener entre 8 y 12 caracteres alfanuméricos."
            )
        return

    if not re.fullmatch(r"[A-Za-z0-9]{8,12}", num_documento):
        raise ValueError("El documento debe tener entre 8 y 12 caracteres alfanuméricos.")
