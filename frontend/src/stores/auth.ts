import { defineStore } from 'pinia'

import { getMe, login, type Usuario } from '../services/auth'

const TOKEN_KEY = 'eletron.access_token'

interface AuthState {
  token: string | null
  usuario: Usuario | null
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    token: localStorage.getItem(TOKEN_KEY),
    usuario: null,
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.token),
  },
  actions: {
    async login(loginValue: string, senha: string) {
      const response = await login(loginValue, senha)
      this.token = response.access_token
      this.usuario = response.usuario
      localStorage.setItem(TOKEN_KEY, response.access_token)
    },
    async loadCurrentUser() {
      if (!this.token || this.usuario) return
      this.usuario = await getMe()
    },
    logout() {
      this.token = null
      this.usuario = null
      localStorage.removeItem(TOKEN_KEY)
    },
  },
})
