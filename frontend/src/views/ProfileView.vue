<template>
  <div class="profile-page">
    <AppNavbar />

    <main class="content">
      <!-- Profile info -->
      <section class="card">
        <h3>Account</h3>
        <div class="avatar-section">
          <img v-if="auth.user?.avatar" :src="auth.user.avatar" class="avatar" alt="Avatar" />
          <div v-else class="avatar-placeholder">{{ initials }}</div>
          <label class="avatar-upload-btn">
            Change Avatar
            <input type="file" accept="image/*" style="display:none" @change="uploadAvatar" />
          </label>
        </div>
        <div class="field">
          <label>Username</label>
          <input :value="auth.user?.username" readonly />
        </div>
        <div class="field">
          <label>Display Name</label>
          <div v-if="!editingName" class="display-name-row">
            <span>{{ auth.user?.display_name || '—' }}</span>
            <button class="inline-btn" @click="editingName = true; nameInput = auth.user?.display_name ?? ''">Edit</button>
          </div>
          <div v-else class="display-name-row">
            <input v-model="nameInput" @keyup.enter="saveName" />
            <button class="inline-btn" @click="saveName">Save</button>
            <button class="inline-btn" @click="editingName = false">Cancel</button>
          </div>
        </div>
      </section>

      <!-- Cross-group balances -->
      <section class="card">
        <h3>My Balances</h3>
        <div v-if="loadingBalances" class="loading">Loading…</div>
        <div v-else>
          <p class="total-balance" :class="Number(balanceData?.total_balance) >= 0 ? 'positive' : 'negative'">
            Total: {{ Number(balanceData?.total_balance) >= 0 ? '+' : '-' }}{{ Math.abs(Number(balanceData?.total_balance)).toFixed(2) }}
          </p>
          <div v-for="g in balanceData?.groups ?? []" :key="g.group_id" class="group-balance">
            <div class="group-balance-header" @click="toggleGroup(g.group_id)">
              <span>{{ g.group_name }}</span>
              <span :class="Number(g.balance) >= 0 ? 'positive' : 'negative'">
                {{ Number(g.balance) >= 0 ? '+' : '-' }}{{ g.currency_symbol ?? '' }}{{ Math.abs(Number(g.balance)).toFixed(2) }}
              </span>
              <span class="toggle-arrow">{{ expandedGroups.has(g.group_id) ? '▲' : '▼' }}</span>
            </div>
            <div v-if="expandedGroups.has(g.group_id)" class="debt-list">
              <div v-for="d in g.debts" :key="`${d.from_user_id}-${d.to_user_id}`" class="debt-row">
                <span class="negative">{{ d.from_username }}</span> owes
                <span class="positive">{{ d.to_username }}</span>
                <strong>{{ g.currency_symbol ?? '' }}{{ d.amount }}</strong>
              </div>
              <div v-if="g.debts.length === 0" class="empty-small">Settled up!</div>
            </div>
          </div>
        </div>
      </section>

      <!-- API Key -->
      <section class="card">
        <h3>API Key</h3>
        <div v-if="newKey" class="key-display">
          <p class="key-notice">Copy this key — it won't be shown again:</p>
          <code>{{ newKey }}</code>
          <button class="inline-btn" @click="newKey = ''">Dismiss</button>
        </div>
        <div v-else>
          <p class="key-status">{{ hasKey ? '••••••••••••••••' : 'No key generated' }}</p>
        </div>
        <div class="export-buttons">
          <button class="export-btn" @click="generateKey">Generate New Key</button>
          <button v-if="hasKey" class="export-btn danger" @click="revokeKey">Revoke Key</button>
        </div>
      </section>

      <!-- Export -->
      <section class="card">
        <h3>Export My Expenses</h3>
        <div class="export-buttons">
          <a :href="api.meExport('csv')" class="export-btn">Download CSV</a>
          <a :href="api.meExport('json')" class="export-btn">Download JSON</a>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/api'
import AppNavbar from '@/components/AppNavbar.vue'

const auth = useAuthStore()
const editingName = ref(false)
const nameInput = ref('')
const loadingBalances = ref(true)
const balanceData = ref<any>(null)
const expandedGroups = ref(new Set<number>())

const hasKey = ref(false)
const newKey = ref('')

async function generateKey() {
  const result = await api.generateApiKey()
  newKey.value = result.key
  hasKey.value = true
}

async function revokeKey() {
  if (!confirm('Revoke your API key? Any integrations using it will stop working.')) return
  await api.revokeApiKey()
  hasKey.value = false
  newKey.value = ''
}

const initials = computed(() => {
  const name = auth.user?.display_name || auth.user?.username || '?'
  return name.slice(0, 2).toUpperCase()
})

onMounted(async () => {
  try {
    balanceData.value = await api.meBalances()
  } finally {
    loadingBalances.value = false
  }
})

function toggleGroup(id: number) {
  if (expandedGroups.value.has(id)) expandedGroups.value.delete(id)
  else expandedGroups.value.add(id)
}

async function saveName() {
  await api.updateMe({ display_name: nameInput.value })
  await auth.fetchMe()
  editingName.value = false
}

async function uploadAvatar(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  await api.uploadAvatar(file)
  await auth.fetchMe()
}
</script>

<style scoped>
.profile-page { min-height: 100vh; background: var(--color-page-bg); }

.content {
  max-width: 640px; margin: 2rem auto; padding: 0 1rem;
  display: flex; flex-direction: column; gap: 1rem;
}

.card {
  background: var(--color-card-bg); border-radius: 8px; padding: 1.25rem;
  box-shadow: 0 1px 4px var(--color-card-shadow);
}

.card h3 { margin: 0 0 1rem; color: var(--color-heading); }

.avatar-section { display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem; }

.avatar {
  width: 64px; height: 64px; border-radius: 50%; object-fit: cover;
}

.avatar-placeholder {
  width: 64px; height: 64px; border-radius: 50%; background: var(--color-primary);
  color: white; display: flex; align-items: center; justify-content: center;
  font-size: 1.25rem; font-weight: 700;
}

.avatar-upload-btn {
  background: none; border: 1px solid var(--color-input-border); border-radius: 4px;
  padding: 0.3rem 0.75rem; cursor: pointer; font-size: 0.875rem; color: var(--color-text-label);
}

.field { margin-bottom: 0.75rem; }
label { display: block; font-size: 0.875rem; font-weight: 500; margin-bottom: 0.25rem; }
input {
  width: 100%; padding: 0.4rem 0.6rem; border: 1px solid var(--color-input-border);
  background: var(--color-input-bg); color: var(--color-text);
  border-radius: 4px; font-size: 0.95rem; box-sizing: border-box;
}

.display-name-row { display: flex; align-items: center; gap: 0.5rem; }
.display-name-row span { flex: 1; }
.display-name-row input { flex: 1; }

.inline-btn {
  padding: 0.25rem 0.6rem; border: 1px solid var(--color-input-border); border-radius: 4px;
  font-size: 0.8rem; cursor: pointer; background: var(--color-card-bg); color: var(--color-text); white-space: nowrap;
}

.total-balance { font-size: 1.1rem; font-weight: 700; margin-bottom: 1rem; }
.positive { color: var(--color-success); }
.negative { color: var(--color-danger); }

.group-balance { margin-bottom: 0.5rem; border: 1px solid var(--color-border); border-radius: 4px; }

.group-balance-header {
  display: flex; align-items: center; gap: 0.5rem; padding: 0.6rem 0.75rem;
  cursor: pointer; background: var(--color-background-soft);
}

.group-balance-header span:first-child { flex: 1; font-weight: 500; }
.toggle-arrow { color: var(--color-text-faint); font-size: 0.75rem; }

.debt-list { padding: 0.5rem 0.75rem; border-top: 1px solid var(--color-border); }
.debt-row { display: flex; gap: 0.4rem; align-items: center; font-size: 0.875rem; padding: 0.2rem 0; }
.empty-small { font-size: 0.8rem; color: var(--color-text-faint); }

.export-buttons { display: flex; gap: 0.75rem; }
.export-btn {
  padding: 0.4rem 1rem; border: 1px solid var(--color-primary); border-radius: 4px;
  color: var(--color-primary); text-decoration: none; font-size: 0.9rem;
}
.loading { color: var(--color-text-placeholder); font-size: 0.875rem; }

.key-display { margin-bottom: 0.75rem; }
.key-notice { font-size: 0.8rem; color: var(--color-text-subtle); margin: 0 0 0.25rem; }
code { display: block; background: var(--color-code-bg); padding: 0.5rem; border-radius: 4px; font-size: 0.8rem; word-break: break-all; margin-bottom: 0.5rem; color: var(--color-text); }
.key-status { color: var(--color-text-muted); font-size: 0.875rem; margin: 0 0 0.75rem; }
.export-btn.danger { color: var(--color-danger); border-color: var(--color-danger); }

/* Responsive: phone (<768px) */
@media (max-width: 767px) {
  .avatar-section {
    flex-direction: column;
    align-items: flex-start;
  }

  .avatar-upload-btn {
    min-height: 44px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .display-name-row {
    flex-wrap: wrap;
  }

  .display-name-row input {
    min-height: 44px;
  }

  .inline-btn {
    min-height: 44px;
  }

  .key-display code {
    overflow-wrap: break-word;
    word-break: break-all;
  }

  .key-status {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .export-buttons {
    flex-direction: column;
  }

  .export-btn {
    min-height: 44px;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
  }
}
</style>
