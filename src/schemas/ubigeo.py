from pydantic import BaseModel, Field


class DepartamentoResponse(BaseModel):
    codigo: str = Field(..., min_length=2, max_length=2)
    nombre: str


class ProvinciaResponse(BaseModel):
    codigo: str = Field(..., min_length=4, max_length=4)
    nombre: str


class DistritoResponse(BaseModel):
    codigo: str = Field(..., min_length=6, max_length=6)
    nombre: str


class UbigeoResponse(BaseModel):
    ubigeo: str
    distrito: str
    provincia: str
    departamento: str
