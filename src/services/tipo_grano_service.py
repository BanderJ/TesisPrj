from decimal import Decimal
from typing import Any

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
        resultado = self.tipo_grano_model.crear(payload.nombre.strip(), payload.peso_qq)
        return TipoGranoResponse(
            id=int(resultado["id"]),
            nombre=str(resultado["nombre"]),
            peso_qq=Decimal(str(resultado["peso_qq"]))
        )

    def actualizar_tipo_grano(self, tipo_grano_id: int, payload: TipoGranoUpdate) -> TipoGranoResponse:
        nombre = payload.nombre.strip() if payload.nombre else None
        resultado = self.tipo_grano_model.actualizar(tipo_grano_id, nombre, payload.peso_qq)
        if not resultado:
            raise ValueError(f"Tipo de grano {tipo_grano_id} no encontrado")
        return TipoGranoResponse(
            id=int(resultado["id"]),
            nombre=str(resultado["nombre"]),
            peso_qq=Decimal(str(resultado["peso_qq"])) if resultado.get("peso_qq") else None
        )

    def eliminar_tipo_grano(self, tipo_grano_id: int) -> None:
        self.tipo_grano_model.eliminar(tipo_grano_id)
