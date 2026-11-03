"""
Reporte Schemas - Estructura genérica de reportes (tabla + gráfico).
Todo reporte se serializa con esta forma: el frontend (coffee-report.js)
renderiza cualquier reporte que la respete, sin código nuevo.
"""
from datetime import date
from decimal import Decimal
from typing import Any, Literal, Self

from pydantic import BaseModel, Field, model_validator


class FiltrosReporte(BaseModel):
    desde: date | None = None
    hasta: date | None = None
    busqueda: str = Field(default="", max_length=200)
    tipo_caficultor: Literal["Socio", "Externo"] | None = None
    pagina: int = Field(default=1, ge=1)
    por_pagina: int = Field(default=20, ge=1, le=100)

    @model_validator(mode="after")
    def validar_periodo(self) -> Self:
        if self.desde and self.hasta and self.desde > self.hasta:
            raise ValueError("La fecha inicial no puede ser posterior a la fecha final.")
        self.busqueda = self.busqueda.strip()
        return self


class ColumnaReporte(BaseModel):
    """Columna de la tabla: `campo` es la clave en cada fila, `titulo` el header visible."""
    campo: str
    titulo: str
    formato: Literal["numero", "decimal", "moneda"] | None = None


class IndicadorReporte(BaseModel):
    titulo: str
    valor: Decimal
    unidad: str = ""


class GraficoReporte(BaseModel):
    """Especificación del gráfico que acompaña a la tabla."""
    tipo: Literal["pie", "bar"]
    campo_etiqueta: str
    campo_valor: str


class ReporteCatalogo(BaseModel):
    """Entrada del catálogo de reportes disponibles."""
    codigo: str
    titulo: str
    descripcion: str
    admite_filtros: bool = False


class ReporteResponse(ReporteCatalogo):
    """Reporte completo: metadatos + columnas + filas + gráfico opcional."""
    columnas: list[ColumnaReporte]
    filas: list[dict[str, Any]] = Field(default_factory=list)
    grafico: GraficoReporte | None = None
    indicadores: list[IndicadorReporte] = Field(default_factory=list)
    detalle_evaluacion: bool = False
    total_filas: int | None = None
    pagina: int = 1
    por_pagina: int = 20
