<template>
  <header class="navbar">
    <RouterLink to="/" class="navbar-brand">MemoryBank</RouterLink>
    <nav class="navbar-links">
      <RouterLink to="/" class="nav-link" exact-active-class="active">Dashboard</RouterLink>
      <RouterLink to="/profile" class="nav-link" active-class="active">Profile</RouterLink>
      <RouterLink v-if="auth.user?.is_staff" to="/admin" class="nav-link" active-class="active">Admin</RouterLink>
    </nav>
    <button class="nav-btn logout-btn" @click="handleLogout">Sign out</button>
  </header>
</template>

<script setup lang="ts">
import { RouterLink, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

async function handleLogout() {
  await auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.navbar {
  background: white;
  padding: 0.75rem 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.navbar-brand {
  font-weight: 700;
  font-size: 1.15rem;
  color: var(--color-heading);
  text-decoration: none;
}

.navbar-links {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-left: auto;
}

.nav-link {
  color: #42b883;
  text-decoration: none;
  font-size: 0.9rem;
  padding: 0.35rem 0.75rem;
  border-radius: 4px;
  transition: background-color 0.2s, color 0.2s;
}

.nav-link:hover {
  background-color: rgba(66, 184, 131, 0.08);
}

.nav-link.active {
  background-color: rgba(66, 184, 131, 0.12);
  font-weight: 600;
}

.nav-btn {
  background: none;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 0.35rem 0.75rem;
  font-size: 0.9rem;
  color: #666;
  cursor: pointer;
  margin-left: 0.5rem;
  transition: border-color 0.2s, color 0.2s;
}

.nav-btn:hover {
  border-color: #999;
  color: #333;
}
</style>
