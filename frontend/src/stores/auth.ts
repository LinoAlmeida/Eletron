import { defineStore } from 'pinia'

import { getMe, getMinhasEmpresas, login, type EmpresaAuth, type Usuario } from '../services/auth'

const TOKEN_KEY = 'eletron.access_token'

interface AuthState {
  token: string | null
  usuario: Usuario | null
  empresas: EmpresaAuth[]
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    token: localStorage.getItem(TOKEN_KEY),
    usuario: null,
    empresas: [],
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.token),
    empresaAtiva: (state) => {
      if (!state.usuario) return null
      return (
        state.empresas.find((empresa) => empresa.id === state.usuario?.empresa_padrao_id) ??
        state.empresas[0] ??
        null
      )
    },
  },
  actions: {
    async login(loginValue: string, senha: string) {
      const response = await login(loginValue, senha)
      this.token = response.access_token
      this.usuario = response.usuario
      localStorage.setItem(TOKEN_KEY, response.access_token)
      this.empresas = await getMinhasEmpresas()
    },
    async loadCurrentUser() {
      if (!this.token) return
      if (!this.usuario) {
        this.usuario = await getMe()
      }
      if (this.empresas.length === 0) {
        this.empresas = await getMinhasEmpresas()
      }
    },
    logout() {
      this.token = null
      this.usuario = null
      this.empresas = []
      localStorage.removeItem(TOKEN_KEY)
    },
  },
})
