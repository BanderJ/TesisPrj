from decimal import Decimal
from typing import Any

import psycopg2.errors

from src.models.tipo_grano import TipoGrano
from src.schemas.tipo_grano import TipoGranoResponse, TipoGranoCreate, TipoGranoUpdate


class TipoGranoService:
    def __init__(self) -> None:
        self.tipo_grano_model = TipoGrano()

    def listar_tipos_grano(self) -> list[TipoGranoResponse]:
        resultados: list[dict[str, Any]] = self.tipo_grano_model.listar()
        return [
            TipoGranoResponse(
                id=int(item["id"]),
                nombre=str(item["nombre"]),
                peso_qq=Decimal(str(item["peso_qq"])) if item.get("peso_qq") else None
            )
            for item in resultados
        ]

    def crear_tipo_grano(self, payload: TipoGranoCreate) -> TipoGranoResponse:
        try:
            resultado = self.tipo_grano_model.crear(payload.nombre.strip(), payload.peso_qq)
        except psycopg2.errors.UniqueViolation as exc:
            raise ValueError(f"Ya existe un tipo de grano llamado '{payload.nombre.strip()}'.") from exc
        return TipoGranoResponse(
            id=int(resultado["id"]),
            nombre=str(resultado["nombre"]),
            peso_qq=Decimal(str(resultado["peso_qq"]))
        )

    def actualizar_tipo_grano(self, tipo_grano_id: int, payload: TipoGranoUpdate) -> TipoGranoResponse:
        nombre = payload.nombre.strip() if payload.nombre else None
        try:
            resultado = self.tipo_grano_model.actualizar(tipo_grano_id, nombre, payload.peso_qq)
        except psycopg2.errors.UniqueViolation as exc:
            raise ValueError(f"Ya existe un tipo de grano llamado '{nombre}'.") from exc
        if not resultado:
            raise ValueError("No se encontró el tipo de grano.")
        return TipoGranoResponse(
            id=int(resultado["id"]),
            nombre=str(resultado["nombre"]),
            peso_qq=Decimal(str(resultado["peso_qq"])) if resultado.get("peso_qq") else None
        )

    def eliminar_tipo_grano(self, tipo_grano_id: int) -> None:
        if not self.tipo_grano_model.eliminar(tipo_grano_id):
            raise ValueError("No se encontró el tipo de grano.")
