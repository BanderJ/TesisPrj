from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.schemas.reporte import FiltrosReporte, ReporteCatalogo, ReporteResponse
from src.services.reporte_service import reporte_service
from src.utilities.jwt_required import require_admin_o_gerente

reporte_router = APIRouter(prefix="/reportes", tags=["reportes"])


@reporte_router.get("", response_model=list[ReporteCatalogo])
def listar_reportes(usuario_actual: dict[str, Any] = Depends(require_admin_o_gerente)) -> list[dict[str, Any]]:
    return reporte_service.listar_catalogo()


@reporte_router.get("/{codigo}", response_model=ReporteResponse)
def obtener_reporte(
    codigo: str,
    filtros: Annotated[FiltrosReporte, Query()],
    usuario_actual: dict[str, Any] = Depends(require_admin_o_gerente),
) -> dict[str, Any]:
    reporte = reporte_service.generar(codigo, filtros)
    if not reporte:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontró el reporte.")
    return reporte
