from fastapi import APIRouter, HTTPException
from src.schemas.caficultor import ObtenerDatosResponse
from src.services.caficultor_service import CaficultorService


caficultor_router = APIRouter()
caficultor_service = CaficultorService()


@caficultor_router.get("/consultar/{num_documento}", response_model=ObtenerDatosResponse)
async def consultar_caficultor(num_documento: str):
	"""Consulta un caficultor por numero de documento (8 o 12 digitos)."""
	if not num_documento.isdigit() or len(num_documento) not in (8, 12):
		raise HTTPException(status_code=400, detail="El documento debe tener 8 o 12 digitos numericos")

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
	except Exception as exc:
		raise HTTPException(status_code=500, detail="No se pudo consultar el caficultor") from exc
