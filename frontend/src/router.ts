import { createRouter, createWebHistory } from 'vue-router'

import { useAuthStore } from './stores/auth'
import { getTurnoAtual } from './services/financeiro'
import AberturaTurnoView from './views/AberturaTurnoView.vue'
import LoginView from './views/LoginView.vue'
import PdvView from './views/PdvView.vue'
import ReservasView from './views/ReservasView.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/',
      name: 'reservas',
      component: ReservasView,
      meta: { requiresAuth: true },
    },
    {
      path: '/pdv',
      name: 'pdv',
      component: PdvView,
      meta: { requiresAuth: true },
    },
    {
      path: '/abrir-turno',
      name: 'abrir-turno',
      component: AberturaTurnoView,
      meta: { requiresAuth: true, turnoPage: true },
    },
  ],
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'login' }
  }

  if (to.meta.requiresAuth && auth.isAuthenticated) {
    try {
      await auth.loadCurrentUser()
      const turno = await getTurnoAtual()
      if (turno.requerido && !turno.aberto && !to.meta.turnoPage) {
        return { name: 'abrir-turno' }
      }
      if ((!turno.requerido || turno.aberto) && to.meta.turnoPage) {
        return { name: 'pdv' }
      }
    } catch {
      auth.logout()
      return { name: 'login' }
    }
  }

  if (to.name === 'login' && auth.isAuthenticated) {
    return { name: 'pdv' }
  }

  return true
})
