import { api } from './api'

export interface Reserva {
  id: number
  legacy_reserva_id: number | null
  empresa_id: number | null
  data: string | null
  hora: string | null
  vendedor_id: number | null
  vendedor_nome: string | null
  status: string | null
  valor_total: string | null
  valor_desconto: string | null
  valor_liquido: string | null
  total_pago: string | null
  troco: string | null
}

export interface ReservaListResponse {
  total: number
  items: Reserva[]
}

export interface Titulo {
  id: number
  legacy_titulo_id: number | null
  caixa_id: number | null
  empresa_id: number | null
  reserva_id: number | null
  forma_pagamento_id: number | null
  valor: string | null
  status: string | null
  data: string | null
  hora: string | null
  cod_autorizacao: string | null
  cod_autorizacao_pix: string | null
}

export interface TituloListResponse {
  total: number
  items: Titulo[]
}

export interface ReservaItem {
  id: number
  legacy_item_id: number | null
  produto_codigo: string | null
  produto_nome: string | null
  valor_unitario: string | null
  quantidade: string | null
  valor_total: string | null
  percentual_desconto: string | null
  valor_desconto: string | null
  valor_final: string | null
  grupo_codigo: string | null
  grupo_descricao: string | null
  tamanho: string | null
}

export interface ReservaCaixa {
  id: number
  status: string | null
  data_abertura: string | null
  hora_abertura: string | null
  data_fechamento: string | null
  hora_fechamento: string | null
  total_dinheiro: string | null
  total_pix: string | null
  total_credito: string | null
  total_debito: string | null
}

export interface ReservaTotais {
  soma_itens: string
  soma_titulos: string
  diferenca_itens_liquido: string
  diferenca_titulos_liquido: string
}

export interface ReservaDetalhe {
  reserva: Reserva
  itens: ReservaItem[]
  titulos: Titulo[]
  caixas: ReservaCaixa[]
  totais: ReservaTotais
}

export async function listarReservas(): Promise<ReservaListResponse> {
  const response = await api.get<ReservaListResponse>('/reservas')
  return response.data
}

export async function listarTitulosReserva(reservaId: number): Promise<TituloListResponse> {
  const response = await api.get<TituloListResponse>(`/financeiro/reservas/${reservaId}/titulos`)
  return response.data
}

export async function obterReservaDetalhe(reservaId: number): Promise<ReservaDetalhe> {
  const response = await api.get<ReservaDetalhe>(`/reservas/${reservaId}`)
  return response.data
}
