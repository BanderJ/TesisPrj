from decimal import Decimal
from typing import ClassVar

from pydantic import BaseModel, Field, model_validator


class RegistrarEvaluacionRequest(BaseModel):
    num_documento: str = Field(..., pattern=r"^[A-Za-z0-9]{8,12}$")
    num_sacos: int = Field(..., ge=1)
    peso_bruto: Decimal = Field(..., gt=0)
    humedad: int = Field(..., ge=1, le=100)
    peso_muestra: Decimal = Field(..., ge=100)
    peso_trillado: Decimal = Field(..., gt=0)
    num_tamiz: int = Field(..., ge=1)
    peso_tamizado: Decimal = Field(..., gt=0)
    tipo_grano_id: int = Field(..., ge=1)

    PESOS_MUESTRA_VALIDOS: ClassVar[set[Decimal]] = {
        Decimal("100"), Decimal("150"), Decimal("200"), Decimal("250"), Decimal("300")
    }

    @model_validator(mode="after")
    def validar_pesos(self):
        max_peso_bruto = self.num_sacos * Decimal("70")
        if self.peso_bruto > max_peso_bruto:
            raise ValueError(
                f"El peso total no puede superar {max_peso_bruto} kg ({self.num_sacos} sacos × 70 kg)"
            )
        if self.peso_muestra not in self.PESOS_MUESTRA_VALIDOS:
            raise ValueError("El peso de muestra debe ser 100, 150, 200, 250 o 300 gr.")
        if self.peso_trillado == self.peso_muestra:
            raise ValueError("El peso trillado debe ser diferente al peso de muestra")
        if self.peso_trillado > self.peso_muestra:
            raise ValueError("El peso trillado no puede ser mayor al peso de muestra")
        if self.peso_trillado > Decimal("0.83") * self.peso_muestra:
            raise ValueError("El peso trillado no puede superar el 83% del peso de muestra")
        if self.peso_tamizado > self.peso_trillado:
            raise ValueError("El peso tamizado no puede ser mayor al peso trillado")
        return self


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


class IncidenciaTapa(BaseModel):
    seg_apertura: int
    seg_cierre: int
    duracion_s: int


class FinalizarEvaluacionRequest(BaseModel):
    total_defectos: int | None = Field(None, ge=0)
    total_buenos: int | None = Field(None, ge=0)
    incidencias: list[IncidenciaTapa] | None = None


class FinalizarEvaluacionResponse(BaseModel):
    finalizado: bool
    mensaje: str
    evaluacion_id: str
    codigo: str


class CompletarEvaluacionRequest(BaseModel):
    total_defectos: int = Field(..., ge=0)
    # Gramos enteros — ingresado manualmente por el evaluador (sin celda de carga)
    peso_bueno: int = Field(..., ge=0)


class CompletarEvaluacionResponse(BaseModel):
    completado: bool
    mensaje: str
    evaluacion_id: str
    codigo: str
    factor_rendimiento: Decimal
    peso_por_qq: Decimal
    pago: Decimal
    precio: Decimal
    rango: str
    categoria: str | None = None


class KpisEvaluacionResponse(BaseModel):
    total_lotes: int
    total_defectos: int
    # Promedio del factor de rendimiento — None si no hay evaluaciones completadas
    rendimiento_promedio: float | None = None


class ResumenEvaluacionResponse(BaseModel):
    evaluacion_id: str
    codigo: str | None = None
    num_documento: str
    caficultor_nombre: str
    tipo_caficultor: str
    tipo_grano: str
    peso_qq_grano: Decimal | None = None
    registrado_por: str
    num_sacos: int
    peso_bruto: Decimal
    humedad: int
    peso_muestra: Decimal
    peso_trillado: Decimal
    num_tamiz: int
    peso_tamizado: Decimal
    fecha: str | None = None
    incidencias: list | None = None
    # Campos de rendimiento — NULL hasta que se complete la evaluación
    total_defectos: int | None = None
    total_buenos: int | None = None
    peso_bueno: Decimal | None = None
    factor_rendimiento: Decimal | None = None
    peso_por_qq: Decimal | None = None
    pago: Decimal | None = None
    precio: Decimal | None = None
    rango: str | None = None
    categoria: str | None = None
