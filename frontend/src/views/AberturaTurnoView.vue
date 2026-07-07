<script setup lang="ts">
import { Clock3, Save } from 'lucide-vue-next'
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'

import { abrirTurno } from '../services/financeiro'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const valorInicial = ref('0')
const loading = ref(false)
const error = ref<string | null>(null)

const now = computed(() => {
  return new Date().toLocaleString('pt-BR', {
    dateStyle: 'short',
    timeStyle: 'medium',
  })
})

async function submit() {
  loading.value = true
  error.value = null
  try {
    await abrirTurno(valorInicial.value || '0')
    await router.push('/')
  } catch {
    error.value = 'Nao foi possivel abrir o turno.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section class="content">
    <div class="turno-panel">
      <div class="login-brand">
        <Clock3 :size="30" />
        <div>
          <strong>Abertura de Turno</strong>
          <span>{{ auth.usuario?.nome }} · {{ auth.empresaAtiva?.fantasia }}</span>
        </div>
      </div>

      <form class="login-form" @submit.prevent="submit">
        <div class="summary-grid">
          <div class="summary-item">
            <span>Data e hora</span>
            <strong>{{ now }}</strong>
          </div>
          <div class="summary-item">
            <span>Operador</span>
            <strong>{{ auth.usuario?.glo_id_proton || '-' }}</strong>
          </div>
        </div>

        <div>
          <label class="form-label" for="valor-inicial">Fundo de Troco</label>
          <input
            id="valor-inicial"
            v-model="valorInicial"
            class="form-control"
            inputmode="decimal"
            placeholder="0,00"
          />
        </div>

        <div v-if="error" class="alert alert-warning py-2">{{ error }}</div>

        <button class="btn btn-primary d-inline-flex align-items-center justify-content-center gap-2" type="submit" :disabled="loading">
          <Save :size="17" />
          {{ loading ? 'Gravando...' : 'Gravar e abrir PDV' }}
        </button>
      </form>
    </div>
  </section>
</template>
