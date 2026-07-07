<script setup lang="ts">
import { RefreshCw, Search } from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'

import {
  listarReservas,
  obterReservaDetalhe,
  type Reserva,
  type ReservaDetalhe,
} from '../services/reservas'

const reservas = ref<Reserva[]>([])
const total = ref(0)
const loading = ref(false)
const loadingDetalhe = ref(false)
const error = ref<string | null>(null)
const search = ref('')
const selectedReserva = ref<Reserva | null>(null)
const detalhe = ref<ReservaDetalhe | null>(null)

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
      await loadDetalhe(selectedReserva.value)
    }
  } catch {
    error.value = 'Nao foi possivel carregar as reservas.'
  } finally {
    loading.value = false
  }
}

async function loadDetalhe(reserva: Reserva): Promise<void> {
  selectedReserva.value = reserva
  loadingDetalhe.value = true
  try {
    detalhe.value = await obterReservaDetalhe(reserva.id)
  } catch {
    detalhe.value = null
  } finally {
    loadingDetalhe.value = false
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
                @click="loadDetalhe(reserva)"
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
          <span>Detalhe</span>
          <strong v-if="selectedReserva">Reserva #{{ selectedReserva.id }}</strong>
        </div>

        <div v-if="!selectedReserva" class="empty-state">Selecione uma reserva</div>
        <div v-else-if="loadingDetalhe" class="empty-state">Carregando detalhe...</div>
        <div v-else-if="!detalhe" class="empty-state">Detalhe indisponivel</div>
        <div v-else class="detail-content">
          <div class="metrics-grid">
            <div>
              <span>Liquido</span>
              <strong>{{ formatCurrency(detalhe.reserva.valor_liquido) }}</strong>
            </div>
            <div>
              <span>Itens</span>
              <strong>{{ formatCurrency(detalhe.totais.soma_itens) }}</strong>
            </div>
            <div>
              <span>Titulos</span>
              <strong>{{ formatCurrency(detalhe.totais.soma_titulos) }}</strong>
            </div>
            <div>
              <span>Dif. titulos</span>
              <strong>{{ formatCurrency(detalhe.totais.diferenca_titulos_liquido) }}</strong>
            </div>
          </div>

          <section class="detail-section">
            <h2>Itens</h2>
            <div v-if="detalhe.itens.length === 0" class="empty-state compact">Nenhum item</div>
            <div v-else class="item-list">
              <div v-for="item in detalhe.itens" :key="item.id" class="line-item">
                <div>
                  <strong>{{ item.produto_nome || '-' }}</strong>
                  <small>{{ item.produto_codigo || '-' }} · {{ item.grupo_descricao || '-' }}</small>
                </div>
                <span>{{ item.quantidade || '0' }} x {{ formatCurrency(item.valor_unitario) }}</span>
                <strong>{{ formatCurrency(item.valor_final) }}</strong>
              </div>
            </div>
          </section>

          <section class="detail-section">
            <h2>Pagamentos</h2>
            <div v-if="detalhe.titulos.length === 0" class="empty-state compact">Nenhum titulo</div>
            <div v-else class="payment-list">
              <div v-for="titulo in detalhe.titulos" :key="titulo.id" class="payment-item">
                <div>
                  <strong>{{ formatCurrency(titulo.valor) }}</strong>
                  <span>{{ titulo.status || '-' }}</span>
                </div>
                <small>
                  Caixa {{ titulo.caixa_id || '-' }} · Forma {{ titulo.forma_pagamento_id || '-' }}
                </small>
              </div>
            </div>
          </section>

          <section class="detail-section">
            <h2>Caixa</h2>
            <div v-if="detalhe.caixas.length === 0" class="empty-state compact">Nenhum caixa vinculado</div>
            <div v-else class="payment-list">
              <div v-for="caixa in detalhe.caixas" :key="caixa.id" class="payment-item">
                <div>
                  <strong>Caixa #{{ caixa.id }}</strong>
                  <span>{{ caixa.status || '-' }}</span>
                </div>
                <small>
                  Pix {{ formatCurrency(caixa.total_pix) }} · Cred {{ formatCurrency(caixa.total_credito) }}
                </small>
              </div>
            </div>
          </section>
          </div>
      </aside>
    </div>
  </section>
</template>
