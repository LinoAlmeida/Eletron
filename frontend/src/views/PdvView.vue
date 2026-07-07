<script setup lang="ts">
import {
  Ban,
  CreditCard,
  Mail,
  MessageCircle,
  MoreVertical,
  Printer,
  RotateCcw,
  ScanBarcode,
  Trash2,
} from 'lucide-vue-next'
import { computed, onMounted, ref, watch } from 'vue'

import { getTurnoAtual, type TurnoAtual } from '../services/financeiro'
import { buscarProduto, listarEstoques, listarVendedores, type Estoque, type Vendedor } from '../services/pdv'

interface PdvItem {
  codigo: number
  nome: string
  referencia: string | null
  preco: number
  quantidade: number
  descontoPercentual: number
  motivoDesconto: string
}

interface Pagamento {
  forma: 'DINHEIRO' | 'PIX' | 'CARTAO' | 'LINK'
  valor: number
}

const estoques = ref<Estoque[]>([])
const vendedores = ref<Vendedor[]>([])
const turno = ref<TurnoAtual | null>(null)
const estoqueId = ref<number | null>(null)
const vendedorId = ref<number | null>(null)
const mezanino = ref(false)
const busca = ref('')
const itens = ref<PdvItem[]>([])
const pagamentos = ref<Pagamento[]>([])
const reservaCriada = ref(false)
const loadingProduto = ref(false)
const error = ref<string | null>(null)

const estoqueSelecionado = computed(() => estoques.value.find((item) => item.id === estoqueId.value) ?? null)
const vendedorSelecionado = computed(() => vendedores.value.find((item) => item.id === vendedorId.value) ?? null)

const qtdItens = computed(() => itens.value.reduce((total, item) => total + item.quantidade, 0))
const totalBruto = computed(() => itens.value.reduce((total, item) => total + item.preco * item.quantidade, 0))
const totalDesconto = computed(() =>
  itens.value.reduce((total, item) => total + item.preco * item.quantidade * (item.descontoPercentual / 100), 0),
)
const totalLiquido = computed(() => Math.max(totalBruto.value - totalDesconto.value, 0))
const totalPago = computed(() => pagamentos.value.reduce((total, item) => total + item.valor, 0))
const troco = computed(() => Math.max(totalPago.value - totalLiquido.value, 0))
const faltaPagar = computed(() => Math.max(totalLiquido.value - totalPago.value, 0))
const possuiDescontoAltoSemMotivo = computed(() =>
  itens.value.some((item) => item.descontoPercentual > 5 && !item.motivoDesconto.trim()),
)

function money(value: number) {
  return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

function normalizarNumero(value: string | number) {
  if (typeof value === 'number') return Number.isFinite(value) ? value : 0
  return Number(value.replace(/\./g, '').replace(',', '.')) || 0
}

function validarTopo() {
  if (!turno.value?.aberto) return 'Turno aberto e obrigatorio.'
  if (!estoqueSelecionado.value?.proton_id) return 'Informe o estoque.'
  if (!vendedorSelecionado.value) return 'Informe o vendedor.'
  return null
}

async function carregarBase() {
  error.value = null
  try {
    const [turnoAtual, listaEstoques] = await Promise.all([getTurnoAtual(), listarEstoques()])
    turno.value = turnoAtual
    estoques.value = listaEstoques
    estoqueId.value = listaEstoques[0]?.id ?? null
  } catch {
    error.value = 'Nao foi possivel carregar os dados do PDV.'
  }
}

async function carregarVendedores() {
  vendedores.value = []
  vendedorId.value = null
  const filialProton = estoqueSelecionado.value?.proton_id
  if (!filialProton) return
  vendedores.value = await listarVendedores(filialProton)
  vendedorId.value = vendedores.value[0]?.id ?? null
}

async function adicionarProduto() {
  const validacao = validarTopo()
  if (validacao) {
    error.value = validacao
    return
  }
  if (!busca.value.trim() || !estoqueSelecionado.value?.proton_id) return

  loadingProduto.value = true
  error.value = null
  try {
    const produto = await buscarProduto(estoqueSelecionado.value.proton_id, busca.value.trim())
    const existente = itens.value.find((item) => item.codigo === produto.codigo)
    if (existente) {
      existente.quantidade += 1
    } else {
      itens.value.push({
        codigo: produto.codigo,
        nome: produto.nome,
        referencia: produto.referencia,
        preco: normalizarNumero(produto.preco_venda),
        quantidade: 1,
        descontoPercentual: 0,
        motivoDesconto: '',
      })
    }
    reservaCriada.value = true
    busca.value = ''
  } catch (err) {
    const detail = (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
    error.value = detail || 'Produto nao encontrado para o estoque selecionado.'
  } finally {
    loadingProduto.value = false
  }
}

function removerItem(codigo: number) {
  itens.value = itens.value.filter((item) => item.codigo !== codigo)
  if (itens.value.length === 0) reservaCriada.value = false
}

function limparItens() {
  itens.value = []
  reservaCriada.value = false
}

function cancelar() {
  limparItens()
  pagamentos.value = []
  mezanino.value = false
  error.value = null
}

function adicionarPagamento(forma: Pagamento['forma']) {
  const valorSugerido = faltaPagar.value || totalLiquido.value
  pagamentos.value.push({ forma, valor: Number(valorSugerido.toFixed(2)) })
}

function finalizar() {
  const validacao = validarTopo()
  if (validacao) {
    error.value = validacao
    return
  }
  if (itens.value.length === 0) {
    error.value = 'Inclua ao menos um produto.'
    return
  }
  if (possuiDescontoAltoSemMotivo.value) {
    error.value = 'Informe o motivo para descontos acima de 5%.'
    return
  }
  if (faltaPagar.value > 0) {
    error.value = 'Confirme o recebimento antes de finalizar.'
    return
  }
  error.value = 'Finalizacao, titulos e DAV entram na proxima etapa.'
}

watch(estoqueId, carregarVendedores)

onMounted(carregarBase)
</script>

<template>
  <section class="content pdv-page">
    <div class="pdv-top">
      <div>
        <label class="form-label" for="estoque">Estoque</label>
        <select id="estoque" v-model.number="estoqueId" class="form-select">
          <option v-for="estoque in estoques" :key="estoque.id" :value="estoque.id">
            {{ estoque.fantasia }} {{ estoque.proton_id ? `(${estoque.proton_id})` : '' }}
          </option>
        </select>
      </div>

      <div>
        <label class="form-label" for="vendedor">Vendedor</label>
        <select id="vendedor" v-model.number="vendedorId" class="form-select">
          <option v-for="vendedor in vendedores" :key="vendedor.id" :value="vendedor.id">
            {{ vendedor.nome_abreviado || vendedor.nome || vendedor.vendedor_proton_id }}
          </option>
        </select>
      </div>

      <div class="pdv-indicator">
        <span>Turno</span>
        <strong>{{ turno?.aberto ? `Aberto #${turno.caixa?.id}` : 'Fechado' }}</strong>
      </div>

      <div class="pdv-indicator">
        <span>Reserva</span>
        <strong>{{ reservaCriada ? 'Automatica' : 'Aguardando item' }}</strong>
      </div>

      <div class="pdv-indicator">
        <span>Qtd Itens</span>
        <strong>{{ qtdItens }}</strong>
      </div>

      <label class="pdv-check">
        <input v-model="mezanino" class="form-check-input" type="checkbox" />
        <span>Mezanino</span>
      </label>

      <div class="dropdown">
        <button class="btn btn-outline-secondary icon-btn" type="button" data-bs-toggle="dropdown" aria-label="Opcoes">
          <MoreVertical :size="18" />
        </button>
        <ul class="dropdown-menu dropdown-menu-end">
          <li><button class="dropdown-item" type="button">Consultar reserva</button></li>
          <li><button class="dropdown-item" type="button">Fechamento parcial</button></li>
        </ul>
      </div>
    </div>

    <form class="pdv-search" @submit.prevent="adicionarProduto">
      <ScanBarcode :size="22" />
      <input
        v-model="busca"
        class="form-control form-control-lg"
        placeholder="Bipe ou digite codigo Proton / codigo de barras"
        autofocus
      />
      <button class="btn btn-primary" type="submit" :disabled="loadingProduto">
        {{ loadingProduto ? 'Buscando...' : 'Adicionar' }}
      </button>
    </form>

    <div v-if="error" class="alert alert-warning py-2">{{ error }}</div>

    <div class="pdv-work">
      <div class="table-wrap">
        <table class="table table-hover align-middle mb-0">
          <thead>
            <tr>
              <th>Codigo</th>
              <th>Produto</th>
              <th>Preco</th>
              <th>Qtd</th>
              <th>Total</th>
              <th>% Desc.</th>
              <th>Vlr Desc.</th>
              <th>Vlr Final</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in itens" :key="item.codigo">
              <td>{{ item.codigo }}</td>
              <td>
                <strong>{{ item.nome }}</strong>
                <small v-if="item.referencia">{{ item.referencia }}</small>
                <input
                  v-if="item.descontoPercentual > 5"
                  v-model="item.motivoDesconto"
                  class="form-control form-control-sm mt-2"
                  placeholder="Motivo do desconto"
                />
              </td>
              <td>{{ money(item.preco) }}</td>
              <td>
                <input v-model.number="item.quantidade" class="form-control form-control-sm pdv-number" min="1" type="number" />
              </td>
              <td>{{ money(item.preco * item.quantidade) }}</td>
              <td>
                <input
                  v-model.number="item.descontoPercentual"
                  class="form-control form-control-sm pdv-number"
                  min="0"
                  max="100"
                  step="0.01"
                  type="number"
                />
              </td>
              <td>{{ money(item.preco * item.quantidade * (item.descontoPercentual / 100)) }}</td>
              <td>{{ money(item.preco * item.quantidade * (1 - item.descontoPercentual / 100)) }}</td>
              <td>
                <button class="btn btn-outline-danger icon-btn" type="button" aria-label="Limpar item" @click="removerItem(item.codigo)">
                  <Trash2 :size="16" />
                </button>
              </td>
            </tr>
            <tr v-if="itens.length === 0">
              <td class="empty-state text-center py-5" colspan="9">Nenhum item na reserva.</td>
            </tr>
          </tbody>
        </table>
      </div>

      <aside class="pdv-side">
        <div class="totals-list">
          <div><span>Bruto</span><strong>{{ money(totalBruto) }}</strong></div>
          <div><span>Desconto</span><strong>{{ money(totalDesconto) }}</strong></div>
          <div><span>Liquido</span><strong>{{ money(totalLiquido) }}</strong></div>
          <div><span>Pago</span><strong>{{ money(totalPago) }}</strong></div>
          <div><span>Troco</span><strong>{{ money(troco) }}</strong></div>
        </div>

        <div class="detail-section">
          <h2>Pagamentos</h2>
          <div class="payment-actions">
            <button class="btn btn-outline-secondary" type="button" @click="adicionarPagamento('DINHEIRO')">Dinheiro</button>
            <button class="btn btn-outline-secondary" type="button" @click="adicionarPagamento('PIX')">PIX</button>
            <button class="btn btn-outline-secondary" type="button" @click="adicionarPagamento('CARTAO')">Cartao</button>
            <button class="btn btn-outline-secondary" type="button" @click="adicionarPagamento('LINK')">Link</button>
          </div>
          <div v-for="(pagamento, index) in pagamentos" :key="index" class="payment-row">
            <span>{{ pagamento.forma }}</span>
            <input v-model.number="pagamento.valor" class="form-control form-control-sm" type="number" step="0.01" />
          </div>
          <small v-if="faltaPagar > 0">Falta receber {{ money(faltaPagar) }}</small>
        </div>

        <div class="pdv-actions">
          <button class="btn btn-primary" type="button" @click="finalizar">
            <CreditCard :size="17" />
            Finalizar
          </button>
          <button class="btn btn-outline-danger" type="button" @click="cancelar">
            <Ban :size="17" />
            Cancelar
          </button>
          <button class="btn btn-outline-secondary" type="button">
            <RotateCcw :size="17" />
            Troca
          </button>
          <button class="btn btn-outline-secondary" type="button">
            <Printer :size="17" />
            Imprimir
          </button>
          <button class="btn btn-outline-secondary" type="button">
            <MessageCircle :size="17" />
            WhatsApp
          </button>
          <button class="btn btn-outline-secondary" type="button">
            <Mail :size="17" />
            E-mail
          </button>
          <button class="btn btn-outline-secondary" type="button" @click="limparItens">
            <Trash2 :size="17" />
            Limpar item
          </button>
        </div>
      </aside>
    </div>
  </section>
</template>
