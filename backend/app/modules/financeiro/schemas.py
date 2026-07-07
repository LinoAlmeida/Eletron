from datetime import date, time
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class CaixaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    legacy_caixa_id: int | None
    empresa_id: int | None
    filial_proton: int | None
    usuario_id: int | None
    usuario_nome: str | None
    data_abertura: date | None
    hora_abertura: time | None
    data_fechamento: date | None
    hora_fechamento: time | None
    status: str | None
    valor_inicial: Decimal | None
    valor_final: Decimal | None
    total_dinheiro: Decimal | None
    total_pix: Decimal | None
    total_credito: Decimal | None
    total_debito: Decimal | None
    total_sangria: Decimal | None
    total_link: Decimal | None


class TituloOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    legacy_titulo_id: int | None
    caixa_id: int | None
    empresa_id: int | None
    reserva_id: int | None
    forma_pagamento_id: int | None
    valor: Decimal | None
    status: str | None
    data: date | None
    hora: time | None
    cod_autorizacao: str | None
    cod_autorizacao_pix: str | None


class TituloListResponse(BaseModel):
    total: int
    items: list[TituloOut]


class CaixaListResponse(BaseModel):
    total: int
    items: list[CaixaOut]


class TurnoAtualResponse(BaseModel):
    requerido: bool
    aberto: bool
    caixa: CaixaOut | None = None


class AbrirTurnoRequest(BaseModel):
    valor_inicial: Decimal = Decimal("0")


class AbrirTurnoResponse(BaseModel):
    caixa: CaixaOut
