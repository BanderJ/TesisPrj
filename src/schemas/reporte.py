"""
Reporte Schemas - Estructura genérica de reportes (tabla + gráfico).
Todo reporte se serializa con esta forma: el frontend (coffee-report.js)
renderiza cualquier reporte que la respete, sin código nuevo.
"""
from typing import Any, Literal

from pydantic import BaseModel, Field


class ColumnaReporte(BaseModel):
    """Columna de la tabla: `campo` es la clave en cada fila, `titulo` el header visible."""
    campo: str
    titulo: str


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


class ReporteResponse(ReporteCatalogo):
    """Reporte completo: metadatos + columnas + filas + gráfico opcional."""
    columnas: list[ColumnaReporte]
    filas: list[dict[str, Any]] = Field(default_factory=list)
    grafico: GraficoReporte | None = None
