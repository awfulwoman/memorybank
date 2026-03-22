<template>
  <div class="dashboard">
    <header class="navbar">
      <span class="brand">MemoryBank</span>
      <nav>
        <RouterLink to="/profile">Profile</RouterLink>
        <RouterLink v-if="auth.user?.is_staff" to="/admin">Admin</RouterLink>
        <button class="logout-btn" @click="handleLogout">Sign out</button>
      </nav>
    </header>

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
import { useRouter, RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/api'

const auth = useAuthStore()
const router = useRouter()
const groups = ref<any[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    groups.value = await api.groups()
  } finally {
    loading.value = false
  }
})

async function handleLogout() {
  await auth.logout()
  router.push({ name: 'login' })
}
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  background: #f5f5f5;
}

.navbar {
  background: white;
  padding: 0.75rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.brand {
  font-weight: 700;
  font-size: 1.2rem;
  color: #2c3e50;
}

nav {
  display: flex;
  gap: 1rem;
  align-items: center;
}

nav a {
  color: #42b883;
  text-decoration: none;
  font-size: 0.9rem;
}

.logout-btn {
  background: none;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 0.25rem 0.75rem;
  cursor: pointer;
  font-size: 0.875rem;
  color: #666;
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
