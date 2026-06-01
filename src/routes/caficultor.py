from fastapi import APIRouter, HTTPException, status, Path, Depends
from src.utilities.jwt_required import obtener_usuario_actual

from src.schemas.caficultor import (
	ConvertirSocioResponse,
	ObtenerDatosResponse,
	RegistrarCaficultorRequest,
	RegistrarCaficultorResponse,
)
from src.services.caficultor_service import CaficultorService


caficultor_router = APIRouter()
caficultor_service = CaficultorService()


@caficultor_router.get("/listar")
async def listar_caficultores(
    _: dict = Depends(obtener_usuario_actual),
) -> list[dict]:
    try:
        return caficultor_service.listar_caficultores()
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudo listar los caficultores") from exc


@caficultor_router.get("/consultar/{num_documento}", response_model=ObtenerDatosResponse)
async def consultar_caficultor(
	num_documento: str = Path(..., pattern=r"^[A-Za-z0-9]{8,12}$")
) -> ObtenerDatosResponse:
	"""Consulta un caficultor por numero de documento (8 o 12 digitos)."""
	try:
		datos = caficultor_service.obtener_caficultor_por_documento(num_documento)

		if not datos:
			return ObtenerDatosResponse(
				encontrado=False,
				mensaje=(
					"No existe un caficultor con ese documento. "
					"Se recomienda registrarlo para continuar con el proceso."
				),
				data=None,
			)

		return ObtenerDatosResponse(
			encontrado=True,
			mensaje="Caficultor encontrado correctamente.",
			data=datos,
		)
	except ValueError as exc:
		raise HTTPException(status_code=400, detail=str(exc)) from exc
	except Exception as exc:
		raise HTTPException(status_code=500, detail="No se pudo consultar el caficultor") from exc


@caficultor_router.post(
	"/registrar",
	response_model=RegistrarCaficultorResponse,
	status_code=status.HTTP_201_CREATED,
)
async def registrar_caficultor(
	payload: RegistrarCaficultorRequest,
) -> RegistrarCaficultorResponse:
	"""Registra un caficultor creando primero la persona y luego el registro en caficultor."""
	try:
		return caficultor_service.registrar_caficultor(payload)
	except ValueError as exc:
		raise HTTPException(status_code=400, detail=str(exc)) from exc
	except Exception as exc:
		raise HTTPException(status_code=500, detail="No se pudo registrar el caficultor") from exc


@caficultor_router.patch(
	"/convertir-socio/{num_documento}",
	response_model=ConvertirSocioResponse,
)
async def convertir_caficultor_a_socio(
	num_documento: str = Path(..., pattern=r"^[A-Za-z0-9]{8,12}$")
) -> ConvertirSocioResponse:
	"""Convierte un caficultor existente, activo y no socio al tipo socio."""
	try:
		return caficultor_service.convertir_caficultor_a_socio(num_documento)
	except ValueError as exc:
		raise HTTPException(status_code=400, detail=str(exc)) from exc
	except Exception as exc:
		raise HTTPException(status_code=500, detail="No se pudo convertir el caficultor a socio") from exc
