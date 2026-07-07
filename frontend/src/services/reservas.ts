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
  valor_liquido: string | null
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

export async function listarReservas(): Promise<ReservaListResponse> {
  const response = await api.get<ReservaListResponse>('/reservas')
  return response.data
}

export async function listarTitulosReserva(reservaId: number): Promise<TituloListResponse> {
  const response = await api.get<TituloListResponse>(`/financeiro/reservas/${reservaId}/titulos`)
  return response.data
}
