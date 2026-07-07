import { api } from './api'

export interface Perfil {
  id: number
  nome: string
}

export interface Usuario {
  id: number
  legacy_usuario_id: number | null
  nome: string
  username: string
  email: string | null
  cod_proton: number | null
  perfil: Perfil | null
  empresa_padrao_id: number | null
  senha_deve_alterar: boolean
  glo_id_user: number
  glo_tp_user: number | null
  glo_empresa: number | null
  glo_id_proton: number | null
}

export interface EmpresaAuth {
  id: number
  fantasia: string
  cnpj: string | null
}

export interface LoginResponse {
  access_token: string
  token_type: string
  usuario: Usuario
  vendedores_filiais_sincronizados: number
}

export async function login(loginValue: string, senha: string): Promise<LoginResponse> {
  const response = await api.post<LoginResponse>('/auth/login', { login: loginValue, senha })
  return response.data
}

export async function getMe(): Promise<Usuario> {
  const response = await api.get<Usuario>('/auth/me')
  return response.data
}

export async function getMinhasEmpresas(): Promise<EmpresaAuth[]> {
  const response = await api.get<EmpresaAuth[]>('/auth/empresas')
  return response.data
}
