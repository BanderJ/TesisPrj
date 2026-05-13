from decimal import Decimal

from pydantic import BaseModel, Field


class RegistrarEvaluacionRequest(BaseModel):
    num_documento: str = Field(..., pattern=r"^[A-Za-z0-9]{8,12}$")
    num_sacos: int = Field(..., ge=1)
    peso_bruto: Decimal = Field(..., gt=0)
    humedad: int = Field(..., ge=0, le=100)
    peso_muestra: Decimal = Field(..., gt=0)
    peso_trillado: Decimal = Field(..., gt=0)
    num_tamiz: int = Field(..., ge=1)
    peso_tamizado: Decimal = Field(..., gt=0)
    tipo_grano_id: int = Field(..., ge=1)


class EvaluacionData(BaseModel):
    evaluacion_id: str
    codigo: str
    num_documento: str
    caficultor_nombre: str
    tipo_caficultor: str
    num_sacos: int
    peso_bruto: Decimal
    humedad: int
    peso_muestra: Decimal
    peso_trillado: Decimal
    num_tamiz: int
    peso_tamizado: Decimal
    tipo_grano_nombre: str


class RegistrarEvaluacionResponse(BaseModel):
    registrado: bool
    mensaje: str
    data: EvaluacionData


class FinalizarEvaluacionResponse(BaseModel):
    finalizado: bool
    mensaje: str
    evaluacion_id: str
    codigo: str


class CompletarEvaluacionRequest(BaseModel):
    total_defectos: int = Field(..., ge=0)
    peso_bueno: Decimal = Field(..., gt=0)


class CompletarEvaluacionResponse(BaseModel):
    completado: bool
    mensaje: str
    evaluacion_id: str
    codigo: str
    factor_rendimiento: Decimal
    peso_por_qq: Decimal
    pago: Decimal
    categoria: str | None = None


class ResumenEvaluacionResponse(BaseModel):
    evaluacion_id: str
    codigo: str | None = None
    num_documento: str
    caficultor_nombre: str
    tipo_caficultor: str
    tipo_grano: str
    registrado_por: str
    num_sacos: int
    peso_bruto: Decimal
    humedad: int
    peso_muestra: Decimal
    peso_trillado: Decimal
    num_tamiz: int
    peso_tamizado: Decimal
    fecha: str | None = None
