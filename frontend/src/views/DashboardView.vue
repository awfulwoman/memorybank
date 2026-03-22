<template>
  <div class="dashboard">
    <AppNavbar />

    <main class="content">
      <!-- Balance Summary -->
      <section v-if="balances.length > 0" class="balance-summary">
        <h2>My Balances</h2>
        <div class="balance-cards">
          <div v-for="b in balances" :key="b.group_id" class="balance-card">
            <span class="balance-group">{{ b.group_name }}</span>
            <span class="balance-amount" :class="{ positive: Number(b.balance) > 0, negative: Number(b.balance) < 0 }">
              {{ Number(b.balance) >= 0 ? '+' : '' }}{{ Number(b.balance).toFixed(2) }}
            </span>
          </div>
        </div>
      </section>

      <div class="section-header">
        <h2>My Groups</h2>
        <button class="btn-create" @click="showCreateModal = true">+ Create Group</button>
      </div>
      <div v-if="loading" class="loading">Loading groups…</div>
      <div v-else-if="groups.length === 0" class="empty">You are not in any groups yet.</div>
      <div v-else class="group-grid">
        <RouterLink
          v-for="group in groups"
          :key="group.id"
          :to="{ name: 'group-detail', params: { id: group.id } }"
          class="group-card"
        >
          <h3><span class="group-icon mdi" :class="group.icon || 'mdi-account-group'"></span>{{ group.name }}</h3>
          <p class="meta">{{ group.group_type_name || 'General' }} · {{ group.currency_code || '—' }}</p>
          <p class="members">{{ group.member_count }} member{{ group.member_count === 1 ? '' : 's' }}</p>
        </RouterLink>
      </div>

      <CreateGroupModal
        v-if="showCreateModal"
        @close="showCreateModal = false"
        @created="onGroupCreated"
      />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { api } from '@/api'
import AppNavbar from '@/components/AppNavbar.vue'
import CreateGroupModal from '@/components/CreateGroupModal.vue'

const groups = ref<any[]>([])
const balances = ref<any[]>([])
const loading = ref(true)
const showCreateModal = ref(false)

onMounted(async () => {
  try {
    const [g, b] = await Promise.all([api.groups(), api.meBalances()])
    groups.value = g
    balances.value = (b as any[]).filter((item: any) => Number(item.balance) !== 0)
  } finally {
    loading.value = false
  }
})

function onGroupCreated(group: any) {
  groups.value.push(group)
  showCreateModal.value = false
}
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  background: var(--color-page-bg);
  overflow-x: hidden;
}

.content {
  max-width: 900px;
  margin: 2rem auto;
  padding: 0 1rem;
}

h2 {
  margin-bottom: 1rem;
  color: var(--color-heading);
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.section-header h2 {
  margin-bottom: 0;
}

.btn-create {
  padding: 0.4rem 0.9rem;
  border-radius: 4px;
  font-size: 0.9rem;
  cursor: pointer;
  border: 1px solid var(--color-primary);
  background: var(--color-primary);
  color: white;
  margin-bottom: 1rem;
}

/* Balance summary */
.balance-summary {
  margin-bottom: 2rem;
}

.balance-cards {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.balance-card {
  background: var(--color-card-bg);
  border-radius: 8px;
  padding: 0.75rem 1rem;
  box-shadow: 0 1px 4px var(--color-card-shadow);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  min-width: 180px;
  flex: 1 1 180px;
}

.balance-group {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
}

.balance-amount {
  font-weight: 600;
  font-size: 1rem;
}

.balance-amount.positive {
  color: var(--color-success);
}

.balance-amount.negative {
  color: var(--color-danger);
}

/* Group grid — responsive columns */
.group-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

@media (min-width: 768px) {
  .group-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .group-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

.group-card {
  background: var(--color-card-bg);
  border-radius: 8px;
  padding: 1.25rem;
  box-shadow: 0 1px 4px var(--color-card-shadow);
  text-decoration: none;
  color: inherit;
  transition: box-shadow 0.2s;
}

.group-card:hover {
  box-shadow: 0 2px 8px var(--color-card-shadow-hover);
}

.group-card h3 {
  margin: 0 0 0.5rem;
  font-size: 1.1rem;
  color: var(--color-heading);
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.group-icon {
  font-size: 1.25rem;
  color: var(--color-primary);
}

.meta {
  font-size: 0.8rem;
  color: var(--color-text-muted);
  margin: 0 0 0.25rem;
}

.members {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  margin: 0;
}

.loading, .empty {
  color: var(--color-text-subtle);
}

/* Phone: balance cards stack vertically */
@media (max-width: 767px) {
  .balance-cards {
    flex-direction: column;
  }

  .balance-card {
    min-width: 0;
    flex: 1 1 auto;
  }
}
</style>
