<template>
  <div class="group-detail">
    <AppNavbar />

    <main class="content">
      <div class="page-header">
        <span v-if="group" class="group-title-icon mdi" :class="group.icon || 'mdi-account-group'"></span>
        <h2>{{ group?.name ?? 'Loading…' }}</h2>
        <button
          v-if="canEditGroup"
          class="settings-btn"
          title="Group Settings"
          @click="showSettings = true"
        >
          <span class="mdi mdi-cog"></span>
        </button>
      </div>

      <div class="two-col">
        <!-- Main column: Expenses -->
        <div class="col-main">
          <section class="card">
            <div class="section-header">
              <h3>Expenses</h3>
              <button class="add-btn" @click="showAddExpense = true">+ Add Expense</button>
            </div>
            <div v-if="loadingExpenses" class="loading">Loading expenses…</div>
            <div v-else-if="expenses.length === 0" class="empty">No expenses yet.</div>
            <div v-for="e in expenses" :key="e.id" class="expense-row">
              <div class="expense-main">
                <span class="amount">{{ sym }}{{ e.amount }}</span>
                <span class="desc">{{ e.description }}</span>
                <span v-if="e.created_by_username === auth.user?.username" class="expense-actions">
                  <button class="edit-btn" @click="editingExpense = e">Edit</button>
                  <button class="delete-btn" @click="confirmDelete(e)">Delete</button>
                </span>
              </div>
              <div class="expense-meta">
                {{ e.date }} · <span class="mdi" :class="e.category_icon || 'mdi-shape-outline'"></span> {{ e.category_name || 'Uncategorised' }} · paid by {{ e.created_by_display_name }}
                <span v-if="e.receipts?.length" class="receipt-indicator">
                  <span class="mdi mdi-paperclip"></span> {{ e.receipts.length }}
                </span>
              </div>
            </div>
          </section>
        </div>

        <!-- Side column: Summary + Tools -->
        <div class="col-side">
          <!-- Balance & Debts Summary -->
          <section class="card">
            <div v-if="groupMembers.length > 2">
              <h3>Balances</h3>
              <div v-if="loadingBalances" class="loading">Loading balances…</div>
              <div v-else>
                <div v-for="b in balances" :key="b.user_id" class="balance-row">
                  <span>{{ b.display_name }}</span>
                  <span :class="Number(b.balance) >= 0 ? 'positive' : 'negative'">
                    {{ Number(b.balance) >= 0 ? '+' : '-' }}{{ sym }}{{ Math.abs(Number(b.balance)).toFixed(2) }}
                  </span>
                </div>
                <div v-if="balances.length === 0" class="empty">No balances yet.</div>
              </div>
            </div>

            <div :class="{ 'debts-section': groupMembers.length > 2 }">
              <h3 v-if="groupMembers.length <= 2">Split</h3>
              <h4 v-else>Split</h4>
              <div v-if="loadingBalances" class="loading">Loading…</div>
              <div v-else-if="debts.length === 0" class="empty">All settled up!</div>
              <div v-for="d in debts" :key="`${d.from_user_id}-${d.to_user_id}`" class="debt-row">
                <span class="negative">{{ d.from_display_name }}</span>
                owes
                <span class="positive">{{ d.to_display_name }}</span>
                <strong>{{ sym }}{{ d.amount }}</strong>
              </div>
            </div>
          </section>

          <!-- Tools -->
          <section class="card">
            <h3>Tools</h3>

            <h4>Settlements</h4>
            <button class="add-btn tool-btn" @click="showSettlement = true">+ Record Payment</button>
            <div v-if="settlements.length === 0" class="empty">No settlements yet.</div>
            <div v-for="s in settlements" :key="s.id" class="settlement-row">
              <span>{{ s.payer_display_name }}</span>
              paid
              <span>{{ s.payee_display_name }}</span>
              <strong>{{ sym }}{{ s.amount }}</strong>
              <span class="date">{{ s.date }}</span>
            </div>

            <h4>Export</h4>
            <div class="export-buttons">
              <a :href="api.groupExport(groupId, 'csv')" class="export-btn">CSV</a>
              <a :href="api.groupExport(groupId, 'json')" class="export-btn">JSON</a>
            </div>
          </section>
        </div>
      </div>
    </main>

    <SettlementForm
      v-if="showSettlement && group"
      :group-id="groupId"
      :members="groupMembers"
      @close="showSettlement = false"
      @saved="onSettlementSaved"
    />

    <EditExpenseForm
      v-if="editingExpense"
      :expense="editingExpense"
      :members="groupMembers"
      @close="editingExpense = null"
      @saved="onExpenseSaved"
    />

    <GroupSettingsModal
      v-if="showSettings && group"
      :group-id="groupId"
      :name="group.name"
      :icon="group.icon"
      :members-list="group.members_list ?? []"
      :current-user-id="auth.user?.id ?? 0"
      @close="showSettings = false"
      @saved="onSettingsSaved"
      @members-changed="onMembersChanged"
      @deleted="router.push('/')"
    />

    <AddExpenseForm
      v-if="showAddExpense && group"
      :group-id="groupId"
      :members="groupMembers"
      :default-split-method="group.default_split_method ?? 'equal'"
      @close="showAddExpense = false"
      @saved="onExpenseSaved"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '@/api'
import { useAuthStore } from '@/stores/auth'
import AppNavbar from '@/components/AppNavbar.vue'
import AddExpenseForm from '@/components/AddExpenseForm.vue'
import EditExpenseForm from '@/components/EditExpenseForm.vue'
import SettlementForm from '@/components/SettlementForm.vue'
import GroupSettingsModal from '@/components/GroupSettingsModal.vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const groupId = Number(route.params.id)

const group = ref<any>(null)
const expenses = ref<any[]>([])
const settlements = ref<any[]>([])
const balances = ref<any[]>([])
const debts = ref<any[]>([])
const loadingExpenses = ref(true)
const loadingBalances = ref(true)
const showAddExpense = ref(false)
const showSettlement = ref(false)
const editingExpense = ref<any>(null)
const showSettings = ref(false)

const canEditGroup = computed(() => {
  if (!group.value || !auth.user) return false
  return group.value.created_by === auth.user.id || auth.user.is_staff
})

const groupMembers = computed(() => group.value?.members_list ?? [])
const sym = computed(() => group.value?.currency_symbol ?? '')

async function refreshData() {
  const [exps, setts, bals] = await Promise.allSettled([
    api.groupExpenses(groupId),
    api.groupSettlements(groupId),
    api.groupBalances(groupId),
  ])
  if (exps.status === 'fulfilled') expenses.value = exps.value
  if (setts.status === 'fulfilled') settlements.value = setts.value
  if (bals.status === 'fulfilled') {
    balances.value = (bals.value as any).balances ?? []
    debts.value = (bals.value as any).debts ?? []
  }
}

async function onExpenseSaved() {
  showAddExpense.value = false
  editingExpense.value = null
  await refreshData()
}

function onSettingsSaved(updated: any) {
  group.value = updated
  showSettings.value = false
}

async function onMembersChanged() {
  const groups = await api.groups()
  group.value = groups.find((g: any) => g.id === groupId) ?? group.value
}

async function onSettlementSaved() {
  showSettlement.value = false
  await refreshData()
}

async function confirmDelete(e: any) {
  if (!confirm(`Delete "${e.description}"? This cannot be undone.`)) return
  await api.deleteExpense(e.id)
  await refreshData()
}

onMounted(async () => {
  const [groups, exps, setts, bals] = await Promise.allSettled([
    api.groups(),
    api.groupExpenses(groupId),
    api.groupSettlements(groupId),
    api.groupBalances(groupId),
  ])

  if (groups.status === 'fulfilled') {
    group.value = groups.value.find((g: any) => g.id === groupId) ?? null
  }
  if (exps.status === 'fulfilled') expenses.value = exps.value
  loadingExpenses.value = false
  if (setts.status === 'fulfilled') settlements.value = setts.value
  if (bals.status === 'fulfilled') {
    balances.value = (bals.value as any).balances ?? []
    debts.value = (bals.value as any).debts ?? []
  }
  loadingBalances.value = false
})
</script>

<style scoped>
.group-detail {
  min-height: 100vh;
  background: var(--color-page-bg);
}

.content {
  max-width: 1100px;
  margin: 2rem auto;
  padding: 0 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.two-col {
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: 1rem;
  align-items: start;
}

.col-main, .col-side {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.col-side .card h4 {
  margin: 1rem 0 0.5rem;
  font-size: 0.85rem;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.col-side .card h4:first-of-type {
  margin-top: 0;
}

.debts-section {
  margin-top: 1rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--color-border);
}

.debts-section h4 {
  margin: 0 0 0.5rem;
  font-size: 0.85rem;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.tool-btn {
  width: 100%;
  text-align: center;
  margin-bottom: 0.75rem;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.page-header h2 { margin: 0; }

.group-title-icon {
  font-size: 1.5rem;
  color: var(--color-primary);
}

.settings-btn {
  background: none;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  padding: 0.25rem 0.5rem;
  cursor: pointer;
  color: var(--color-text-muted);
  font-size: 1.1rem;
  display: flex;
  align-items: center;
}

.settings-btn:hover {
  color: var(--color-primary);
  border-color: var(--color-primary);
}

.card {
  background: var(--color-card-bg);
  border-radius: 8px;
  padding: 1.25rem;
  box-shadow: 0 1px 4px var(--color-card-shadow);
  overflow-wrap: break-word;
  overflow: hidden;
}

.card h3 {
  margin: 0 0 1rem;
  color: var(--color-heading);
}

.balance-row, .debt-row, .settlement-row {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  padding: 0.4rem 0;
  border-bottom: 1px solid var(--color-border);
  font-size: 0.9rem;
}

.balance-row span:first-child {
  flex: 1;
  font-weight: 700;
  color: var(--color-heading);
}

.positive { color: var(--color-success); font-weight: 600; background: rgba(39, 174, 96, 0.1); padding: 0.15rem 0.5rem; border-radius: 4px; }
.negative { color: var(--color-danger); font-weight: 600; background: rgba(231, 76, 60, 0.1); padding: 0.15rem 0.5rem; border-radius: 4px; }

.expense-row {
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--color-border);
}

.expense-main {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.expense-main .amount {
  font-weight: 700;
  font-size: 1.1rem;
  color: var(--color-heading);
  white-space: nowrap;
  min-width: 5rem;
}

.expense-main .desc {
  flex: 1;
  font-weight: 400;
  color: var(--color-text-secondary);
}

.expense-actions {
  display: flex;
  gap: 0.25rem;
  margin-left: auto;
  flex-shrink: 0;
}

.expense-meta {
  font-size: 0.8rem;
  color: var(--color-text-muted);
}

.date { color: var(--color-text-faint); font-size: 0.8rem; }

.empty, .loading { color: var(--color-text-placeholder); font-size: 0.875rem; }

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.section-header h3 { margin: 0; }

.add-btn {
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 4px;
  padding: 0.3rem 0.75rem;
  font-size: 0.875rem;
  cursor: pointer;
}

.edit-btn, .delete-btn {
  font-size: 0.75rem;
  padding: 0.15rem 0.5rem;
  border: 1px solid var(--color-input-border);
  border-radius: 3px;
  background: var(--color-card-bg);
  cursor: pointer;
  color: var(--color-text-subtle);
}

.delete-btn {
  color: var(--color-danger);
  border-color: var(--color-danger);
}

.export-buttons { display: flex; gap: 0.75rem; }
.export-btn {
  padding: 0.4rem 1rem; border: 1px solid var(--color-primary); border-radius: 4px;
  color: var(--color-primary); text-decoration: none; font-size: 0.9rem;
}

.receipt-indicator {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  margin-left: 0.5rem;
  white-space: nowrap;
}

/* ── Responsive: phone — collapse to single column ── */
@media (max-width: 767px) {
  .two-col {
    grid-template-columns: 1fr;
  }
}

/* ── Responsive: phone (<768px) ── */
@media (max-width: 767px) {
  .content {
    margin: 1rem auto;
    padding: 0 0.5rem;
  }

  .expense-main {
    flex-wrap: wrap;
    gap: 0.25rem;
  }

  .expense-main .desc {
    flex: 1 1 100%;
  }

  .expense-main .amount {
    margin-right: auto;
  }

  .expense-meta {
    word-break: break-word;
  }

  .section-header {
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .add-btn {
    min-height: 44px;
    padding: 0.5rem 1rem;
    font-size: 1rem;
    width: 100%;
    text-align: center;
  }

  .edit-btn, .delete-btn {
    min-height: 44px;
    padding: 0.25rem 0.75rem;
    font-size: 0.85rem;
  }

  .balance-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
    padding: 0.6rem 0;
  }

  .debt-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.15rem;
    padding: 0.6rem 0;
  }

  .settlement-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.15rem;
    padding: 0.6rem 0;
  }

  .export-buttons {
    flex-direction: column;
  }

  .export-btn {
    text-align: center;
    min-height: 44px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}
</style>
