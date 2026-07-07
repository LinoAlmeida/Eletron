<script setup lang="ts">
import { LockKeyhole, ShoppingBag } from 'lucide-vue-next'
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const loginValue = ref('')
const senha = ref('')
const loading = ref(false)
const error = ref<string | null>(null)

async function submit() {
  loading.value = true
  error.value = null
  try {
    await auth.login(loginValue.value, senha.value)
    await router.push('/')
  } catch {
    error.value = 'Login ou senha invalidos.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="login-page">
    <section class="login-panel">
      <div class="login-brand">
        <ShoppingBag :size="30" />
        <div>
          <strong>Eletron</strong>
          <span>Reservas e PDV</span>
        </div>
      </div>

      <form class="login-form" @submit.prevent="submit">
        <div>
          <label class="form-label" for="login">Usuario</label>
          <input
            id="login"
            v-model="loginValue"
            class="form-control"
            autocomplete="username"
            required
            autofocus
          />
        </div>

        <div>
          <label class="form-label" for="senha">Senha</label>
          <input
            id="senha"
            v-model="senha"
            class="form-control"
            type="password"
            autocomplete="current-password"
            required
          />
        </div>

        <div v-if="error" class="alert alert-warning py-2">{{ error }}</div>

        <button class="btn btn-primary w-100 d-inline-flex justify-content-center align-items-center gap-2" type="submit" :disabled="loading">
          <LockKeyhole :size="17" />
          {{ loading ? 'Entrando...' : 'Entrar' }}
        </button>
      </form>
    </section>
  </main>
</template>
