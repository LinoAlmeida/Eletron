<script setup lang="ts">
import { RefreshCw, Search } from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'

import {
  listarReservas,
  listarTitulosReserva,
  type Reserva,
  type Titulo,
} from '../services/reservas'

const reservas = ref<Reserva[]>([])
const total = ref(0)
const loading = ref(false)
const loadingTitulos = ref(false)
const error = ref<string | null>(null)
const search = ref('')
const selectedReserva = ref<Reserva | null>(null)
const titulos = ref<Titulo[]>([])

const filteredReservas = computed(() => {
  const term = search.value.trim().toLowerCase()
  if (!term) return reservas.value

  return reservas.value.filter((reserva) => {
    return [
      reserva.id,
      reserva.legacy_reserva_id,
      reserva.vendedor_nome,
      reserva.status,
      reserva.valor_liquido,
    ]
      .join(' ')
      .toLowerCase()
      .includes(term)
  })
})

function formatCurrency(value: string | null): string {
  if (!value) return 'R$ 0,00'
  return Number(value).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

function formatDate(value: string | null): string {
  if (!value) return '-'
  const [year, month, day] = value.split('-')
  return `${day}/${month}/${year}`
}

async function loadReservas(): Promise<void> {
  loading.value = true
  error.value = null
  try {
    const data = await listarReservas()
    reservas.value = data.items
    total.value = data.total
    selectedReserva.value = data.items[0] ?? null
    if (selectedReserva.value) {
      await loadTitulos(selectedReserva.value)
    }
  } catch {
    error.value = 'Nao foi possivel carregar as reservas.'
  } finally {
    loading.value = false
  }
}

async function loadTitulos(reserva: Reserva): Promise<void> {
  selectedReserva.value = reserva
  loadingTitulos.value = true
  try {
    const data = await listarTitulosReserva(reserva.id)
    titulos.value = data.items
  } catch {
    titulos.value = []
  } finally {
    loadingTitulos.value = false
  }
}

onMounted(loadReservas)
</script>

<template>
  <section class="content">
    <div class="toolbar">
      <div class="search-box">
        <Search :size="18" />
        <input v-model="search" type="search" placeholder="Buscar reserva, vendedor ou status" />
      </div>
      <button class="btn btn-primary d-inline-flex align-items-center gap-2" type="button" @click="loadReservas">
        <RefreshCw :size="17" />
        Atualizar
      </button>
    </div>

    <div class="summary-grid">
      <div class="summary-item">
        <span>Total migrado</span>
        <strong>{{ total }}</strong>
      </div>
      <div class="summary-item">
        <span>Na tela</span>
        <strong>{{ filteredReservas.length }}</strong>
      </div>
      <div class="summary-item">
        <span>Status</span>
        <strong>{{ loading ? 'Carregando' : 'Pronto' }}</strong>
      </div>
    </div>

    <div v-if="error" class="alert alert-warning">{{ error }}</div>

    <div class="work-grid">
      <div class="table-wrap">
        <table class="table table-hover align-middle mb-0">
          <thead>
            <tr>
              <th>Reserva</th>
              <th>Data</th>
              <th>Vendedor</th>
              <th>Status</th>
              <th class="text-end">Valor</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="5" class="text-center muted-row">Carregando reservas...</td>
            </tr>
            <tr v-else-if="filteredReservas.length === 0">
              <td colspan="5" class="text-center muted-row">Nenhuma reserva para exibir</td>
            </tr>
            <template v-else>
              <tr
                v-for="reserva in filteredReservas"
                :key="reserva.id"
                :class="{ 'table-active': selectedReserva?.id === reserva.id }"
                role="button"
                @click="loadTitulos(reserva)"
              >
                <td>
                  <strong>#{{ reserva.id }}</strong>
                  <small v-if="reserva.legacy_reserva_id">HFSQL {{ reserva.legacy_reserva_id }}</small>
                </td>
                <td>{{ formatDate(reserva.data) }}</td>
                <td>{{ reserva.vendedor_nome || '-' }}</td>
                <td><span class="status-pill">{{ reserva.status || '-' }}</span></td>
                <td class="text-end">{{ formatCurrency(reserva.valor_liquido) }}</td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>

      <aside class="detail-panel">
        <div class="detail-header">
          <span>Pagamentos</span>
          <strong v-if="selectedReserva">Reserva #{{ selectedReserva.id }}</strong>
        </div>

        <div v-if="!selectedReserva" class="empty-state">Selecione uma reserva</div>
        <div v-else-if="loadingTitulos" class="empty-state">Carregando pagamentos...</div>
        <div v-else-if="titulos.length === 0" class="empty-state">Nenhum titulo encontrado</div>
        <div v-else class="payment-list">
          <div v-for="titulo in titulos" :key="titulo.id" class="payment-item">
            <div>
              <strong>{{ formatCurrency(titulo.valor) }}</strong>
              <span>{{ titulo.status || '-' }}</span>
            </div>
            <small>
              Caixa {{ titulo.caixa_id || '-' }} · Forma {{ titulo.forma_pagamento_id || '-' }}
            </small>
          </div>
        </div>
      </aside>
    </div>
  </section>
</template>
