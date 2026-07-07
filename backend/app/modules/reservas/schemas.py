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
    valor_desconto: Decimal | None = None
    valor_liquido: Decimal | None
    total_pago: Decimal | None = None
    troco: Decimal | None = None


class ReservaListResponse(BaseModel):
    total: int
    items: list[ReservaOut]


class ReservaItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    legacy_item_id: int | None
    produto_codigo: str | None
    produto_nome: str | None
    valor_unitario: Decimal | None
    quantidade: Decimal | None
    valor_total: Decimal | None
    percentual_desconto: Decimal | None
    valor_desconto: Decimal | None
    valor_final: Decimal | None
    grupo_codigo: str | None
    grupo_descricao: str | None
    tamanho: str | None


class ReservaTituloOut(BaseModel):
    id: int
    legacy_titulo_id: int | None
    caixa_id: int | None
    forma_pagamento_id: int | None
    valor: Decimal | None
    status: str | None
    data: date | None
    hora: time | None


class ReservaCaixaOut(BaseModel):
    id: int
    status: str | None
    data_abertura: date | None
    hora_abertura: time | None
    data_fechamento: date | None
    hora_fechamento: time | None
    total_dinheiro: Decimal | None
    total_pix: Decimal | None
    total_credito: Decimal | None
    total_debito: Decimal | None


class ReservaTotaisOut(BaseModel):
    soma_itens: Decimal
    soma_titulos: Decimal
    diferenca_itens_liquido: Decimal
    diferenca_titulos_liquido: Decimal


class ReservaDetalheOut(BaseModel):
    reserva: ReservaOut
    itens: list[ReservaItemOut]
    titulos: list[ReservaTituloOut]
    caixas: list[ReservaCaixaOut]
    totais: ReservaTotaisOut
