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
