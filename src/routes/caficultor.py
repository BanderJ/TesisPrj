from fastapi import APIRouter, Depends, HTTPException, Path, Request, status

from src.services.auditoria_service import auditoria_service
from src.utilities.jwt_required import obtener_usuario_actual
from src.utilities.request_utils import get_client_ip

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
    num_documento: str = Path(..., pattern=r"^[A-Za-z0-9]{8,12}$"),
    _: dict = Depends(obtener_usuario_actual),
) -> ObtenerDatosResponse:
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
        return ObtenerDatosResponse(encontrado=True, mensaje="Caficultor encontrado correctamente.", data=datos)
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
    request: Request,
    payload: RegistrarCaficultorRequest,
    usuario: dict = Depends(obtener_usuario_actual),
) -> RegistrarCaficultorResponse:
    try:
        result = caficultor_service.registrar_caficultor(payload)
        auditoria_service.registrar(
            accion="CREAR_CAFICULTOR",
            personal_id=str(usuario.get("personal_id", "")),
            usuario=usuario.get("usuario"),
            tipo_personal_id=usuario.get("tipo_personal_id"),
            rol=usuario.get("rol"),
            tabla_afectada="CAFICULTOR",
            descripcion=f"Caficultor registrado: {payload.nombre} {payload.ape_paterno} por {usuario.get('usuario')}",
            ip_cliente=get_client_ip(request),
        )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudo registrar el caficultor") from exc


@caficultor_router.patch(
    "/convertir-socio/{num_documento}",
    response_model=ConvertirSocioResponse,
)
async def convertir_caficultor_a_socio(
    request: Request,
    num_documento: str = Path(..., pattern=r"^[A-Za-z0-9]{8,12}$"),
    usuario: dict = Depends(obtener_usuario_actual),
) -> ConvertirSocioResponse:
    try:
        result = caficultor_service.convertir_caficultor_a_socio(num_documento)
        auditoria_service.registrar(
            accion="CONVERTIR_SOCIO",
            personal_id=str(usuario.get("personal_id", "")),
            usuario=usuario.get("usuario"),
            tipo_personal_id=usuario.get("tipo_personal_id"),
            rol=usuario.get("rol"),
            tabla_afectada="CAFICULTOR",
            descripcion=f"Caficultor convertido a socio: documento {num_documento} por {usuario.get('usuario')}",
            ip_cliente=get_client_ip(request),
        )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudo convertir el caficultor a socio") from exc
