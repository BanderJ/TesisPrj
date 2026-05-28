from decimal import Decimal
from pydantic import BaseModel, Field


class TipoGranoResponse(BaseModel):
    id: int
    nombre: str
    peso_qq: Decimal | None = None


class TipoGranoCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=20)
    peso_qq: Decimal = Field(..., gt=0, decimal_places=2)


class TipoGranoUpdate(BaseModel):
    nombre: str | None = Field(None, min_length=1, max_length=20)
    peso_qq: Decimal | None = Field(None, gt=0, decimal_places=2)
