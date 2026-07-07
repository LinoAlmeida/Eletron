import { api } from './api'

export interface Caixa {
  id: number
  legacy_caixa_id: number | null
  empresa_id: number | null
  filial_proton: number | null
  usuario_id: number | null
  usuario_nome: string | null
  data_abertura: string | null
  hora_abertura: string | null
  data_fechamento: string | null
  hora_fechamento: string | null
  status: string | null
  valor_inicial: string | null
}

export interface TurnoAtual {
  requerido: boolean
  aberto: boolean
  caixa: Caixa | null
}

export interface AbrirTurnoResponse {
  caixa: Caixa
}

export async function getTurnoAtual(): Promise<TurnoAtual> {
  const response = await api.get<TurnoAtual>('/financeiro/turno-atual')
  return response.data
}

export async function abrirTurno(valorInicial: string): Promise<AbrirTurnoResponse> {
  const response = await api.post<AbrirTurnoResponse>('/financeiro/turnos/abrir', {
    valor_inicial: valorInicial,
  })
  return response.data
}
