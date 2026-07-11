from typing import Any

from src.models.ubigeo import Ubigeo
from src.schemas.ubigeo import (
    DepartamentoResponse,
    DistritoResponse,
    ProvinciaResponse,
    UbigeoResponse,
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

    def obtener_por_codigo(self, ubigeo: str) -> UbigeoResponse | None:
        codigo = self._validar_codigo(ubigeo, longitud=6, nombre="ubigeo")
        fila = self.ubigeo_model.obtener_por_codigo(codigo)
        if not fila:
            return None
        return UbigeoResponse(
            ubigeo=str(fila["ubigeo"]).strip(),
            distrito=str(fila["distrito"]),
            provincia=str(fila["provincia"]),
            departamento=str(fila["departamento"]),
        )

    @staticmethod
    def _validar_codigo(valor: str, longitud: int, nombre: str) -> str:
        if not valor or not valor.isdigit() or len(valor) != longitud:
            raise ValueError(
                f"Codigo de {nombre} invalido: debe tener {longitud} digitos."
            )
        return valor
