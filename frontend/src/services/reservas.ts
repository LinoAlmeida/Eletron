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

export async function listarReservas(): Promise<ReservaListResponse> {
  const response = await api.get<ReservaListResponse>('/reservas')
  return response.data
}
