from datetime import date, time
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ReservaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    legacy_reserva_id: int | None
    empresa_id: int | None
    data: date | None
    hora: time | None
    vendedor_id: int | None
    vendedor_nome: str | None
    status: str | None
    valor_total: Decimal | None
    valor_liquido: Decimal | None


class ReservaListResponse(BaseModel):
    total: int
    items: list[ReservaOut]
