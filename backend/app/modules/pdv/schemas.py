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
