import { createRouter, createWebHistory } from 'vue-router'

import ReservasView from './views/ReservasView.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'reservas',
      component: ReservasView,
    },
  ],
})
