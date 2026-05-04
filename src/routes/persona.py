from fastapi import APIRouter, HTTPException

from src.models.persona import Persona
from src.schemas.dni import DniConsultaResponse

persona_router = APIRouter()
_persona_model = Persona()


@persona_router.get("/consultar/{num_documento}", response_model=DniConsultaResponse)
async def consultar_persona(num_documento: str) -> DniConsultaResponse:
    """Busca una persona por número de documento y devuelve sus datos para autofill."""
    try:
        fila = _persona_model.obtener_por_num_documento(num_documento)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Error al consultar persona") from exc

    if not fila:
        return DniConsultaResponse(encontrado=False)

    fecha = fila.get("fecha_nacimiento")
    fecha_str = fecha.strftime("%Y-%m-%d") if fecha else None

    ubigeo = fila.get("ubigeo")
    ubigeo_str = str(ubigeo).strip() if ubigeo and str(ubigeo).strip() else None

    sexo = fila.get("sexo")
    sexo_str = str(sexo).strip() if sexo and str(sexo).strip() in {"M", "F"} else None

    tel = fila.get("telefono")
    tel_str = str(tel).strip() if tel and str(tel).strip() else None

    return DniConsultaResponse(
        encontrado=True,
        nombres=str(fila["nombre"]).strip() or None,
        apellido_paterno=str(fila["ape_paterno"]).strip() or None,
        apellido_materno=str(fila["ape_materno"]).strip() or None,
        sexo=sexo_str,
        fecha_nacimiento=fecha_str,
        ubigeo=ubigeo_str,
        telefono=tel_str,
    )
