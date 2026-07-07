import { api } from './api'

export interface Estoque {
  id: number
  proton_id: number | null
  fantasia: string
  cnpj: string | null
}

export interface Vendedor {
  id: number
  vendedor_proton_id: number
  nome: string | null
  nome_abreviado: string | null
  cpf_cnpj: string | null
  filial_proton_id: number
  ativo: boolean
}

export interface ProdutoBusca {
  codigo: number
  nome: string
  referencia: string | null
  codigo_barras: string | null
  preco_venda: string
}

export interface AdicionarItemPayload {
  reserva_id: number | null
  estoque_id: number
  vendedor_filial_id: number
  produto_codigo: number
  produto_nome: string
  valor_unitario: string
  quantidade: string
  percentual_desconto: string
  referencia: string | null
  mezanino: boolean
  motivo_desconto: string | null
}

export interface AdicionarItemResponse {
  reserva_id: number
  item: {
    id: number
    produto_codigo: string | null
    produto_nome: string | null
    valor_unitario: string | null
    quantidade: string | null
    valor_total: string | null
    percentual_desconto: string | null
    valor_desconto: string | null
    valor_final: string | null
  }
  valor_total: string
  valor_desconto: string
  valor_liquido: string
}

export async function listarEstoques(): Promise<Estoque[]> {
  const response = await api.get<Estoque[]>('/pdv/estoques')
  return response.data
}

export async function listarVendedores(filialProtonId: number): Promise<Vendedor[]> {
  const response = await api.get<Vendedor[]>('/pdv/vendedores', {
    params: { filial_proton_id: filialProtonId },
  })
  return response.data
}

export async function buscarProduto(codFil: number, codprod: string): Promise<ProdutoBusca> {
  const response = await api.get<ProdutoBusca>('/pdv/produtos/buscar', {
    params: { cod_fil: codFil, codprod },
  })
  return response.data
}

export async function adicionarItem(payload: AdicionarItemPayload): Promise<AdicionarItemResponse> {
  const response = await api.post<AdicionarItemResponse>('/pdv/itens', payload)
  return response.data
}
