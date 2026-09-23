from typing import Any

from pydantic import BaseModel, Field

from src.utilities.uuid_utils import UUID_PATTERN


class IniciarMonitoreoRequest(BaseModel):
    """Arranque del monitoreo. El id de evaluación es opcional: la vista /test
    monitorea sin evaluación asociada y entonces no se archiva evidencia."""

    evaluacion_id: str | None = Field(None, pattern=UUID_PATTERN)


class EventoMonitoreoItem(BaseModel):
    """Evento emitido durante el lote en curso."""

    seq: int
    segundo: int
    tipo: str
    severidad: str
    mensaje: str
    imagen_url: str | None = None
    datos: dict[str, Any] | None = None


class EventosMonitoreoResponse(BaseModel):
    """Eventos posteriores al cursor del cliente, más el cursor actualizado."""

    eventos: list[EventoMonitoreoItem]
    cursor: int
