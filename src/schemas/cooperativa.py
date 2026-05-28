"""
Cooperativa Schemas - Request/response models for cooperative endpoints
"""
from datetime import datetime
from pydantic import BaseModel, Field, field_serializer


class CooperativaBase(BaseModel):
    """Base schema for cooperative data."""
    nombre: str = Field(..., min_length=1, max_length=100)
    codigo: str | None = Field(None, max_length=20)
    direccion: str | None = Field(None, max_length=100)
    telefono: str | None = Field(None, pattern=r"^\d{9}$", description="Debe ser 9 dígitos")
    correo: str | None = Field(None, max_length=100)
    descripcion: str | None = Field(None, max_length=1000)
    imagen_url: str | None = Field(None, max_length=500)


class CooperativaCreate(CooperativaBase):
    """Schema for creating a cooperative."""
    pass


class CooperativaUpdate(BaseModel):
    """Schema for updating a cooperative (all fields optional)."""
    nombre: str | None = Field(None, min_length=1, max_length=100)
    codigo: str | None = Field(None, max_length=20)
    direccion: str | None = Field(None, max_length=100)
    telefono: str | None = Field(None, pattern=r"^\d{9}$")
    correo: str | None = Field(None, max_length=100)
    descripcion: str | None = Field(None, max_length=1000)
    imagen_url: str | None = Field(None, max_length=500)


class CooperativaResponse(CooperativaBase):
    """Schema for cooperative response."""
    cooperativa_id: str
    estado: str
    fecha_registro: datetime | str
    tipo_personal_id: int | None = None

    class Config:
        from_attributes = True

    @field_serializer('fecha_registro', when_used='json')
    def serialize_fecha(self, value: datetime | str) -> str:
        if isinstance(value, datetime):
            return value.isoformat()
        return value
