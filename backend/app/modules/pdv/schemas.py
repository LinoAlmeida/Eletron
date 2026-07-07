from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class EstoqueOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    proton_id: int | None
    fantasia: str
    cnpj: str | None


class VendedorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    vendedor_proton_id: int
    nome: str | None
    nome_abreviado: str | None
    cpf_cnpj: str | None
    filial_proton_id: int
    ativo: bool


class ProdutoBuscaOut(BaseModel):
    codigo: int
    nome: str
    referencia: str | None = None
    codigo_barras: str | None = None
    preco_venda: Decimal


class PdvBootstrapResponse(BaseModel):
    estoques: list[EstoqueOut]


class PdvAdicionarItemRequest(BaseModel):
    reserva_id: int | None = None
    estoque_id: int
    vendedor_filial_id: int
    produto_codigo: int
    produto_nome: str
    valor_unitario: Decimal
    quantidade: Decimal = Decimal("1")
    percentual_desconto: Decimal = Decimal("0")
    referencia: str | None = None
    mezanino: bool = False
    motivo_desconto: str | None = None


class PdvItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    produto_codigo: str | None
    produto_nome: str | None
    valor_unitario: Decimal | None
    quantidade: Decimal | None
    valor_total: Decimal | None
    percentual_desconto: Decimal | None
    valor_desconto: Decimal | None
    valor_final: Decimal | None


class PdvAdicionarItemResponse(BaseModel):
    reserva_id: int
    item: PdvItemOut
    valor_total: Decimal
    valor_desconto: Decimal
    valor_liquido: Decimal


class PdvPagamentoRequest(BaseModel):
    forma: str
    valor: Decimal
    parcelas: int | None = None


class PdvFinalizarRequest(BaseModel):
    reserva_id: int
    pagamentos: list[PdvPagamentoRequest]


class PdvTituloOut(BaseModel):
    id: int
    forma_pagamento_id: int | None
    valor: Decimal | None
    status: str | None


class PdvFinalizarResponse(BaseModel):
    reserva_id: int
    status: str
    valor_total: Decimal
    valor_desconto: Decimal
    valor_liquido: Decimal
    total_pago: Decimal
    troco: Decimal
    titulos: list[PdvTituloOut]
