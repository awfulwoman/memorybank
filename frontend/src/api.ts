const BASE = '/api'

function getCsrfToken(): string {
  const match = document.cookie.match(/csrftoken=([^;]+)/)
  return match ? match[1]! : ''
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    'X-CSRFToken': getCsrfToken(),
    ...(options.headers as Record<string, string>),
  }
  const res = await fetch(`${BASE}${path}`, { ...options, credentials: 'include', headers })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw err
  }
  if (res.status === 204) return undefined as T
  return res.json()
}

export const api = {
  login: (username: string, password: string) =>
    request<{ username: string; is_staff: boolean }>('/auth/login/', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    }),

  logout: () => request<void>('/auth/logout/', { method: 'POST' }),

  me: () => request<{ id: number; username: string; display_name: string; avatar: string | null; is_staff: boolean }>('/users/me/'),

  updateMe: (data: Partial<{ display_name: string }>) =>
    request('/users/me/', { method: 'PATCH', body: JSON.stringify(data) }),

  uploadAvatar: (file: File) => {
    const form = new FormData()
    form.append('avatar', file)
    return fetch(`${BASE}/users/me/avatar/`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'X-CSRFToken': getCsrfToken() },
      body: form,
    }).then(r => {
      if (!r.ok) throw new Error(`Upload failed: ${r.status}`)
      return r.json()
    })
  },

  generateApiKey: () => request<{ key: string }>('/users/me/api-key/', { method: 'POST' }),
  revokeApiKey: () => request<void>('/users/me/api-key/', { method: 'DELETE' }),

  meBalances: () => request('/users/me/balances/'),
  meExport: (format: 'csv' | 'json') => `/api/users/me/export/?format=${format}`,

  groups: () => request<any[]>('/groups/'),
  createGroup: (data: any) => request('/groups/', { method: 'POST', body: JSON.stringify(data) }),
  updateGroup: (id: number, data: any) => request(`/groups/${id}/`, { method: 'PATCH', body: JSON.stringify(data) }),
  deleteGroup: (id: number) => request<void>(`/groups/${id}/`, { method: 'DELETE' }),
  addMember: (groupId: number, userId: number) =>
    request(`/groups/${groupId}/members/`, { method: 'POST', body: JSON.stringify({ user_id: userId }) }),
  addMemberByUsername: (groupId: number, username: string) =>
    request(`/groups/${groupId}/members/`, { method: 'POST', body: JSON.stringify({ username }) }),
  removeMember: (groupId: number, userId: number) =>
    request<void>(`/groups/${groupId}/members/${userId}/`, { method: 'DELETE' }),

  groupExpenses: (groupId: number) => request<any[]>(`/groups/${groupId}/expenses/`),
  createExpense: (groupId: number, data: any) =>
    request(`/groups/${groupId}/expenses/`, { method: 'POST', body: JSON.stringify(data) }),
  updateExpense: (id: number, data: any) =>
    request(`/expenses/${id}/`, { method: 'PATCH', body: JSON.stringify(data) }),
  deleteExpense: (id: number) => request<void>(`/expenses/${id}/`, { method: 'DELETE' }),

  groupSettlements: (groupId: number) => request<any[]>(`/groups/${groupId}/settlements/`),
  createSettlement: (groupId: number, data: any) =>
    request(`/groups/${groupId}/settlements/`, { method: 'POST', body: JSON.stringify(data) }),

  groupBalances: (groupId: number) => request(`/groups/${groupId}/balances/`),
  groupExport: (groupId: number, format: 'csv' | 'json') => `/api/groups/${groupId}/export/?format=${format}`,

  categories: () => request<any[]>('/categories/'),
  createCategory: (data: any) => request('/categories/', { method: 'POST', body: JSON.stringify(data) }),
  updateCategory: (id: number, data: any) =>
    request(`/categories/${id}/`, { method: 'PATCH', body: JSON.stringify(data) }),
  deleteCategory: (id: number) => request<void>(`/categories/${id}/`, { method: 'DELETE' }),

  groupTypes: () => request<any[]>('/group-types/'),
  createGroupType: (data: any) => request('/group-types/', { method: 'POST', body: JSON.stringify(data) }),
  updateGroupType: (id: number, data: any) =>
    request(`/group-types/${id}/`, { method: 'PATCH', body: JSON.stringify(data) }),
  deleteGroupType: (id: number) => request<void>(`/group-types/${id}/`, { method: 'DELETE' }),

  currencies: () => request<any[]>('/currencies/'),
  createCurrency: (data: any) => request('/currencies/', { method: 'POST', body: JSON.stringify(data) }),
  updateCurrency: (id: number, data: any) =>
    request(`/currencies/${id}/`, { method: 'PATCH', body: JSON.stringify(data) }),
  deleteCurrency: (id: number) => request<void>(`/currencies/${id}/`, { method: 'DELETE' }),

  adminUsers: () => request<any[]>('/admin/users/'),
  createUser: (data: any) => request('/admin/users/', { method: 'POST', body: JSON.stringify(data) }),
  updateUser: (id: number, data: any) => request(`/admin/users/${id}/`, { method: 'PATCH', body: JSON.stringify(data) }),
}
