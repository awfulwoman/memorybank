<template>
  <div class="dashboard">
    <AppNavbar />

    <main class="content">
      <h2>My Groups</h2>
      <div v-if="loading" class="loading">Loading groups…</div>
      <div v-else-if="groups.length === 0" class="empty">You are not in any groups yet.</div>
      <div v-else class="group-grid">
        <RouterLink
          v-for="group in groups"
          :key="group.id"
          :to="{ name: 'group-detail', params: { id: group.id } }"
          class="group-card"
        >
          <h3>{{ group.name }}</h3>
          <p class="meta">{{ group.group_type_name || 'General' }} · {{ group.currency_code || '—' }}</p>
          <p class="members">{{ group.member_count }} member{{ group.member_count === 1 ? '' : 's' }}</p>
        </RouterLink>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { api } from '@/api'
import AppNavbar from '@/components/AppNavbar.vue'

const groups = ref<any[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    groups.value = await api.groups()
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  background: #f5f5f5;
}

.content {
  max-width: 900px;
  margin: 2rem auto;
  padding: 0 1rem;
}

h2 {
  margin-bottom: 1rem;
  color: #2c3e50;
}

.group-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 1rem;
}

.group-card {
  background: white;
  border-radius: 8px;
  padding: 1.25rem;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
  text-decoration: none;
  color: inherit;
  transition: box-shadow 0.2s;
}

.group-card:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}

.group-card h3 {
  margin: 0 0 0.5rem;
  font-size: 1.1rem;
  color: #2c3e50;
}

.meta {
  font-size: 0.8rem;
  color: #888;
  margin: 0 0 0.25rem;
}

.members {
  font-size: 0.875rem;
  color: #555;
  margin: 0;
}

.loading, .empty {
  color: #666;
}
</style>
