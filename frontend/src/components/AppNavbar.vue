<template>
  <header class="navbar">
    <RouterLink to="/" class="navbar-brand">MemoryBank</RouterLink>

    <!-- Desktop nav -->
    <nav class="navbar-links desktop-only">
      <RouterLink to="/" class="nav-link" exact-active-class="active">Dashboard</RouterLink>
      <RouterLink to="/profile" class="nav-link" active-class="active">Profile</RouterLink>
      <RouterLink v-if="auth.user?.is_staff" to="/admin" class="nav-link" active-class="active">Admin</RouterLink>
    </nav>
    <button class="nav-btn logout-btn desktop-only" @click="handleLogout">Sign out</button>

    <!-- Hamburger button (mobile/tablet) -->
    <button
      class="hamburger mobile-only"
      :class="{ open: menuOpen }"
      @click.stop="toggleMenu"
      aria-label="Toggle navigation menu"
    >
      <span class="hamburger-line" />
      <span class="hamburger-line" />
      <span class="hamburger-line" />
    </button>

    <!-- Mobile dropdown -->
    <nav v-if="menuOpen" class="mobile-menu mobile-only" @click.stop>
      <RouterLink to="/" class="nav-link" exact-active-class="active" @click="closeMenu">Dashboard</RouterLink>
      <RouterLink to="/profile" class="nav-link" active-class="active" @click="closeMenu">Profile</RouterLink>
      <RouterLink v-if="auth.user?.is_staff" to="/admin" class="nav-link" active-class="active" @click="closeMenu">Admin</RouterLink>
      <button class="nav-btn logout-btn" @click="handleLogoutMobile">Sign out</button>
    </nav>
  </header>

  <!-- Overlay backdrop -->
  <div v-if="menuOpen" class="menu-overlay mobile-only" @click="closeMenu" />
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const menuOpen = ref(false)

function toggleMenu() {
  menuOpen.value = !menuOpen.value
}

function closeMenu() {
  menuOpen.value = false
}

function handleClickOutside(e: MouseEvent) {
  if (menuOpen.value) {
    closeMenu()
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

async function handleLogout() {
  await auth.logout()
  router.push('/login')
}

async function handleLogoutMobile() {
  closeMenu()
  await auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.navbar {
  background: var(--color-navbar-bg);
  padding: 0.75rem 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 1px 3px var(--color-navbar-shadow);
  position: relative;
  z-index: 100;
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
  color: var(--color-primary);
  text-decoration: none;
  font-size: 0.9rem;
  padding: 0.35rem 0.75rem;
  border-radius: 4px;
  transition: background-color 0.2s, color 0.2s;
}

.nav-link:hover {
  background-color: var(--color-primary-bg);
}

.nav-link.active {
  background-color: var(--color-primary-bg-active);
  font-weight: 600;
}

.nav-btn {
  background: none;
  border: 1px solid var(--color-input-border);
  border-radius: 4px;
  padding: 0.35rem 0.75rem;
  font-size: 0.9rem;
  color: var(--color-text-subtle);
  cursor: pointer;
  margin-left: 0.5rem;
  transition: border-color 0.2s, color 0.2s;
}

.nav-btn:hover {
  border-color: var(--color-input-border-hover);
  color: var(--color-heading);
}

/* Hamburger button */
.hamburger {
  display: none;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 5px;
  width: 44px;
  height: 44px;
  min-width: 44px;
  min-height: 44px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  margin-left: auto;
}

.hamburger-line {
  display: block;
  width: 24px;
  height: 2px;
  background-color: var(--color-heading);
  border-radius: 2px;
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.hamburger.open .hamburger-line:nth-child(1) {
  transform: translateY(7px) rotate(45deg);
}

.hamburger.open .hamburger-line:nth-child(2) {
  opacity: 0;
}

.hamburger.open .hamburger-line:nth-child(3) {
  transform: translateY(-7px) rotate(-45deg);
}

/* Mobile menu dropdown */
.mobile-menu {
  display: none;
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: var(--color-navbar-bg);
  box-shadow: 0 4px 12px var(--color-navbar-shadow);
  flex-direction: column;
  padding: 0.5rem 0;
  z-index: 101;
}

.mobile-menu .nav-link {
  padding: 0.75rem 1.5rem;
  border-radius: 0;
  font-size: 1rem;
}

.mobile-menu .nav-btn {
  margin: 0.5rem 1.5rem;
  text-align: center;
  padding: 0.6rem 0.75rem;
}

/* Overlay */
.menu-overlay {
  display: none;
  position: fixed;
  inset: 0;
  background: var(--color-overlay);
  z-index: 99;
}

/* Responsive visibility */
@media (max-width: 1023px) {
  .desktop-only {
    display: none !important;
  }

  .hamburger.mobile-only {
    display: flex;
  }

  .mobile-menu.mobile-only {
    display: flex;
  }

  .menu-overlay.mobile-only {
    display: block;
  }
}

@media (min-width: 1024px) {
  .mobile-only {
    display: none !important;
  }
}
</style>
