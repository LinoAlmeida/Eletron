<script setup lang="ts">
import { BarChart3, Boxes, CalendarClock, LogOut, Menu, ShoppingBag, ShoppingCart } from 'lucide-vue-next'
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useAuthStore } from './stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const usesShell = computed(() => route.meta.requiresAuth)

async function logout() {
  auth.logout()
  await router.push('/login')
}
</script>

<template>
  <RouterView v-if="!usesShell" />

  <div v-else class="app-shell">
    <aside class="sidebar">
      <div class="brand">
        <span class="brand-mark">
          <ShoppingBag :size="20" />
        </span>
        <span>
          <strong>Aredda</strong>
          <small>Eletron PDV</small>
        </span>
      </div>

      <nav class="nav-list">
        <RouterLink to="/pdv" class="nav-link">
          <ShoppingCart :size="18" />
          <span>PDV</span>
        </RouterLink>
        <RouterLink to="/" class="nav-link">
          <CalendarClock :size="18" />
          <span>Reservas</span>
        </RouterLink>
        <a class="nav-link disabled" href="#">
          <Boxes :size="18" />
          <span>Produtos</span>
        </a>
        <a class="nav-link disabled" href="#">
          <BarChart3 :size="18" />
          <span>Gestao</span>
        </a>
      </nav>
    </aside>

    <main class="main-area">
      <header class="topbar">
        <button class="btn btn-outline-secondary icon-btn" type="button" aria-label="Menu">
          <Menu :size="18" />
        </button>
        <div class="topbar-title">
          <strong>{{ route.name === 'pdv' ? 'PDV de Reservas' : 'Reservas' }}</strong>
          <span>
            {{ auth.usuario?.nome || 'PDV, pedidos e historico migrado' }}
            <template v-if="auth.empresaAtiva"> · {{ auth.empresaAtiva.fantasia }}</template>
          </span>
        </div>
        <button class="btn btn-outline-secondary icon-btn" type="button" aria-label="Sair" @click="logout">
          <LogOut :size="18" />
        </button>
      </header>

      <RouterView />
    </main>
  </div>
</template>
