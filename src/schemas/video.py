from typing import Any

from pydantic import BaseModel, Field, field_validator

from src.utilities.uuid_utils import UUID_PATTERN


class ControlMonitoreoRequest(BaseModel):
    """Identifica el lote al iniciar, detener o resetear. Prueba no envía evaluación."""

    evaluacion_id: str | None = Field(None, pattern=UUID_PATTERN)

    @field_validator("evaluacion_id")
    @classmethod
    def normalizar_uuid(cls, valor: str | None) -> str | None:
        return valor.lower() if valor else valor


class DetenerMonitoreoRequest(ControlMonitoreoRequest):
    descartar_lote: bool = False


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
