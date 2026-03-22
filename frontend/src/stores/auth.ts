import { ref } from 'vue'
import { defineStore } from 'pinia'
import { api } from '@/api'

export interface User {
  id: number
  username: string
  display_name: string
  avatar: string | null
  is_staff: boolean
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const loading = ref(false)

  async function fetchMe() {
    try {
      user.value = await api.me()
    } catch {
      user.value = null
    }
  }

  async function login(username: string, password: string) {
    await api.login(username, password)
    await fetchMe()
  }

  async function logout() {
    await api.logout()
    user.value = null
  }

  return { user, loading, fetchMe, login, logout }
})
