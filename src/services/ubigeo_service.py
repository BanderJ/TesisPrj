from typing import Any

from src.models.ubigeo import Ubigeo
from src.schemas.ubigeo import (
    DepartamentoResponse,
    DistritoResponse,
    ProvinciaResponse,
)


class UbigeoService:
    """Casos de uso para la cascada departamento -> provincia -> distrito."""

    def __init__(self) -> None:
        self.ubigeo_model: Ubigeo = Ubigeo()

    def listar_departamentos(self) -> list[DepartamentoResponse]:
        filas: list[dict[str, Any]] = self.ubigeo_model.listar_departamentos()
        return [
            DepartamentoResponse(codigo=str(f["codigo"]), nombre=str(f["nombre"]))
            for f in filas
        ]

    def listar_provincias(self, departamento_codigo: str) -> list[ProvinciaResponse]:
        codigo = self._validar_codigo(departamento_codigo, longitud=2, nombre="departamento")
        filas: list[dict[str, Any]] = self.ubigeo_model.listar_provincias(codigo)
        return [
            ProvinciaResponse(codigo=str(f["codigo"]), nombre=str(f["nombre"]))
            for f in filas
        ]

    def listar_distritos(self, provincia_codigo: str) -> list[DistritoResponse]:
        codigo = self._validar_codigo(provincia_codigo, longitud=4, nombre="provincia")
        filas: list[dict[str, Any]] = self.ubigeo_model.listar_distritos(codigo)
        return [
            DistritoResponse(codigo=str(f["codigo"]), nombre=str(f["nombre"]))
            for f in filas
        ]

    @staticmethod
    def _validar_codigo(valor: str, longitud: int, nombre: str) -> str:
        if not valor or not valor.isdigit() or len(valor) != longitud:
            raise ValueError(
                f"El código de {nombre} no es válido: debe tener {longitud} dígitos."
            )
        return valor
