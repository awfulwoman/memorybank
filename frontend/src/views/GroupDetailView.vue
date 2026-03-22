<template>
  <div class="group-detail">
    <header class="navbar">
      <RouterLink to="/" class="back">← Groups</RouterLink>
      <span class="brand">{{ group?.name ?? 'Loading…' }}</span>
      <RouterLink to="/profile" class="nav-link">Profile</RouterLink>
    </header>

    <main class="content">
      <!-- Balance Summary -->
      <section class="card">
        <h3>Balances</h3>
        <div v-if="loadingBalances" class="loading">Loading balances…</div>
        <div v-else>
          <div v-for="b in balances" :key="b.user_id" class="balance-row">
            <span>{{ b.username }}</span>
            <span :class="Number(b.balance) >= 0 ? 'positive' : 'negative'">
              {{ Number(b.balance) >= 0 ? '+' : '' }}{{ b.balance }}
            </span>
          </div>
          <div v-if="balances.length === 0" class="empty">No balances yet.</div>
        </div>
      </section>

      <!-- Pairwise Debts -->
      <section class="card">
        <h3>Who owes whom</h3>
        <div v-if="debts.length === 0" class="empty">All settled up!</div>
        <div v-for="d in debts" :key="`${d.from_user_id}-${d.to_user_id}`" class="debt-row">
          <span class="negative">{{ d.from_username }}</span>
          owes
          <span class="positive">{{ d.to_username }}</span>
          <strong>{{ d.amount }}</strong>
        </div>
      </section>

      <!-- Expenses -->
      <section class="card">
        <div class="section-header">
          <h3>Expenses</h3>
          <button class="add-btn" @click="showAddExpense = true">+ Add Expense</button>
        </div>
        <div v-if="loadingExpenses" class="loading">Loading expenses…</div>
        <div v-else-if="expenses.length === 0" class="empty">No expenses yet.</div>
        <div v-for="e in expenses" :key="e.id" class="expense-row">
          <div class="expense-main">
            <span class="desc">{{ e.description }}</span>
            <span class="amount">{{ e.amount }}</span>
            <button
              v-if="e.created_by_username === auth.user?.username"
              class="edit-btn"
              @click="editingExpense = e"
            >Edit</button>
            <button
              v-if="e.created_by_username === auth.user?.username"
              class="delete-btn"
              @click="confirmDelete(e)"
            >Delete</button>
          </div>
          <div class="expense-meta">
            {{ e.date }} · {{ e.category_name || 'Uncategorised' }} · paid by {{ e.created_by_username }}
          </div>
        </div>
      </section>

      <!-- Export -->
      <section class="card">
        <h3>Export Expenses</h3>
        <div class="export-buttons">
          <a :href="api.groupExport(groupId, 'csv')" class="export-btn">Download CSV</a>
          <a :href="api.groupExport(groupId, 'json')" class="export-btn">Download JSON</a>
        </div>
      </section>

      <!-- Settlements -->
      <section class="card">
        <div class="section-header">
          <h3>Settlements</h3>
          <button class="add-btn" @click="showSettlement = true">+ Record Payment</button>
        </div>
        <div v-if="settlements.length === 0" class="empty">No settlements yet.</div>
        <div v-for="s in settlements" :key="s.id" class="settlement-row">
          <span>{{ s.payer_username }}</span>
          paid
          <span>{{ s.payee_username }}</span>
          <strong>{{ s.amount }}</strong>
          <span class="date">{{ s.date }}</span>
        </div>
      </section>
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
import { useRoute, RouterLink } from 'vue-router'
import { api } from '@/api'
import { useAuthStore } from '@/stores/auth'
import AddExpenseForm from '@/components/AddExpenseForm.vue'
import EditExpenseForm from '@/components/EditExpenseForm.vue'
import SettlementForm from '@/components/SettlementForm.vue'

const route = useRoute()
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

const groupMembers = computed(() => group.value?.members_list ?? [])

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
  background: #f5f5f5;
}

.navbar {
  background: white;
  padding: 0.75rem 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.back, .nav-link {
  color: #42b883;
  text-decoration: none;
  font-size: 0.9rem;
}

.brand {
  flex: 1;
  font-weight: 700;
  font-size: 1.1rem;
  color: #2c3e50;
}

.content {
  max-width: 800px;
  margin: 2rem auto;
  padding: 0 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.card {
  background: white;
  border-radius: 8px;
  padding: 1.25rem;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}

.card h3 {
  margin: 0 0 1rem;
  color: #2c3e50;
}

.balance-row, .debt-row, .settlement-row {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  padding: 0.4rem 0;
  border-bottom: 1px solid #f0f0f0;
  font-size: 0.9rem;
}

.balance-row span:first-child {
  flex: 1;
}

.positive { color: #27ae60; font-weight: 600; }
.negative { color: #e74c3c; font-weight: 600; }

.expense-row {
  padding: 0.5rem 0;
  border-bottom: 1px solid #f0f0f0;
}

.expense-main {
  display: flex;
  justify-content: space-between;
  font-weight: 500;
}

.expense-meta {
  font-size: 0.8rem;
  color: #888;
}

.date { color: #aaa; font-size: 0.8rem; }

.empty, .loading { color: #999; font-size: 0.875rem; }

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.section-header h3 { margin: 0; }

.add-btn {
  background: #42b883;
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
  border: 1px solid #ddd;
  border-radius: 3px;
  background: white;
  cursor: pointer;
  color: #666;
  margin-left: 0.5rem;
}

.delete-btn {
  color: #e74c3c;
  border-color: #e74c3c;
}

.export-buttons { display: flex; gap: 0.75rem; }
.export-btn {
  padding: 0.4rem 1rem; border: 1px solid #42b883; border-radius: 4px;
  color: #42b883; text-decoration: none; font-size: 0.9rem;
}
</style>
