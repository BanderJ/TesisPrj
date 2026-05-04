import re

from fastapi import APIRouter, HTTPException

from src.apis.reniec_api import ReniecApi
from src.schemas.dni import DniConsultaResponse

dni_router = APIRouter()


def _normalizar(valor: str | None) -> str | None:
    """Devuelve el valor en titulo si no es vacio, sino None."""
    if not valor or not valor.strip():
        return None
    return valor.strip().title()


def _normalizar_sexo(valor: str | None) -> str | None:
    """Mapea M/F o vacio a None."""
    if not valor:
        return None
    v = valor.strip().upper()
    return v if v in {"M", "F"} else None


def _normalizar_fecha(valor: str | None) -> str | None:
    """
    Intenta convertir DD/MM/YYYY → YYYY-MM-DD para el input[type=date].
    Devuelve None si el valor esta vacio o no se puede parsear.
    """
    if not valor or not valor.strip():
        return None
    texto = valor.strip()
    match = re.fullmatch(r"(\d{2})/(\d{2})/(\d{4})", texto)
    if match:
        return f"{match.group(3)}-{match.group(2)}-{match.group(1)}"
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", texto):
        return texto
    return None


def _normalizar_ubigeo(valor: str | None) -> str | None:
    """Acepta solo codigos de 6 digitos numericos."""
    if not valor:
        return None
    codigo = valor.strip()
    if re.fullmatch(r"\d{6}", codigo):
        return codigo
    return None


@dni_router.get("/consultar/{dni}", response_model=DniConsultaResponse)
async def consultar_dni(dni: str) -> DniConsultaResponse:
    """Consulta datos personales de un DNI via Factiliza y devuelve campos normalizados."""
    if not re.fullmatch(r"\d{8}", dni):
        raise HTTPException(status_code=400, detail="El DNI debe tener exactamente 8 digitos.")

    try:
        data = ReniecApi.consultar_dni(dni)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Error al consultar el servicio externo.") from exc

    if data is None:
        return DniConsultaResponse(encontrado=False)

    return DniConsultaResponse(
        encontrado=True,
        nombres=_normalizar(data.get("nombres")),
        apellido_paterno=_normalizar(data.get("apellido_paterno")),
        apellido_materno=_normalizar(data.get("apellido_materno")),
        sexo=_normalizar_sexo(data.get("sexo")),
        fecha_nacimiento=_normalizar_fecha(data.get("fecha_nacimiento")),
        ubigeo=_normalizar_ubigeo(data.get("ubigeo_sunat")),
        departamento=_normalizar(data.get("departamento")),
        provincia=_normalizar(data.get("provincia")),
        distrito=_normalizar(data.get("distrito")),
        direccion=_normalizar(data.get("direccion")),
    )
