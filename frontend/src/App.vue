<script setup lang="ts">
import { BarChart3, Boxes, CalendarClock, LogOut, Menu, ShoppingBag } from 'lucide-vue-next'
</script>

<template>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="brand">
        <ShoppingBag :size="24" />
        <span>Eletron</span>
      </div>

      <nav class="nav-list">
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
          <strong>Reservas</strong>
          <span>PDV, pedidos e historico migrado</span>
        </div>
        <button class="btn btn-outline-secondary icon-btn" type="button" aria-label="Sair">
          <LogOut :size="18" />
        </button>
      </header>

      <RouterView />
    </main>
  </div>
</template>
