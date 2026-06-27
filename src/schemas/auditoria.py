from datetime import datetime
from pydantic import BaseModel


class AuditoriaResponse(BaseModel):
    id: str
    personal_id: str | None
    usuario: str | None
    tipo_personal_id: int | None
    rol: str | None
    accion: str
    tabla_afectada: str | None
    registro_id: str | None
    descripcion: str | None
    datos_anteriores: dict | None
    datos_nuevos: dict | None
    ip_cliente: str | None
    fecha_hora: datetime


class AuditoriaListResponse(BaseModel):
    registros: list[AuditoriaResponse]
    total: int
    pagina: int
    total_paginas: int
