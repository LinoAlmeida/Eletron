import { createRouter, createWebHistory } from 'vue-router'

import { useAuthStore } from './stores/auth'
import LoginView from './views/LoginView.vue'
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
    } catch {
      auth.logout()
      return { name: 'login' }
    }
  }

  if (to.name === 'login' && auth.isAuthenticated) {
    return { name: 'reservas' }
  }

  return true
})
