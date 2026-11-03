from fastapi import APIRouter, Depends, HTTPException, Request

from src.schemas.bono_socio import BonoSocioActualizarRequest, BonoSocioResponse
from src.services.auditoria_service import auditoria_service
from src.services.bono_socio_service import BonoSocioService
from src.utilities.jwt_required import obtener_usuario_actual, require_gerente
from src.utilities.request_utils import get_client_ip

bono_socio_router = APIRouter()
bono_socio_service = BonoSocioService()


@bono_socio_router.get("", response_model=BonoSocioResponse)
def obtener_bono_socio(_: dict = Depends(obtener_usuario_actual)) -> BonoSocioResponse:
    try:
        return bono_socio_service.obtener()
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudo obtener el beneficio de socio.") from exc


@bono_socio_router.post("", response_model=BonoSocioResponse)
def actualizar_bono_socio(
    request: Request,
    payload: BonoSocioActualizarRequest,
    user: dict = Depends(require_gerente),
) -> BonoSocioResponse:
    try:
        anterior, resultado = bono_socio_service.actualizar(payload, str(user.get("personal_id")))
        auditoria_service.registrar(
            accion="ACTUALIZAR_BONO_SOCIO",
            personal_id=user.get("personal_id"),
            usuario=user.get("usuario"),
            tipo_personal_id=user.get("tipo_personal_id"),
            rol=user.get("rol"),
            tabla_afectada="BONO_SOCIO",
            descripcion=f"Beneficio de socio: S/ {anterior} -> S/ {payload.monto}",
            datos_anteriores={"monto": str(anterior)},
            datos_nuevos={"monto": str(payload.monto)},
            ip_cliente=get_client_ip(request),
        )
        return resultado
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudo actualizar el beneficio de socio.") from exc
