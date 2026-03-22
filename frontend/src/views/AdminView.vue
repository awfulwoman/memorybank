<template>
  <div class="admin-page">
    <header class="navbar">
      <RouterLink to="/" class="back">← Dashboard</RouterLink>
      <span class="brand">Admin Console</span>
    </header>

    <main class="content">
      <!-- Categories -->
      <section class="card">
        <div class="section-header">
          <h3>Categories</h3>
          <button class="add-btn" @click="startAdd('category')">+ Add</button>
        </div>
        <div v-if="addingType === 'category'" class="inline-form">
          <input v-model="newName" placeholder="Category name" @keyup.enter="saveNew('category')" />
          <button @click="saveNew('category')">Save</button>
          <button @click="addingType = ''">Cancel</button>
        </div>
        <div v-for="item in categories" :key="item.id" class="list-row">
          <span v-if="editing?.type !== 'category' || editing.id !== item.id">{{ item.name }}</span>
          <input v-else v-model="editing.name" @keyup.enter="saveEdit" />
          <div class="row-actions">
            <button class="small-btn" @click="startEdit('category', item)">Edit</button>
            <button v-if="editing?.type === 'category' && editing.id === item.id" class="small-btn save" @click="saveEdit">Save</button>
            <button class="small-btn danger" @click="deleteItem('category', item.id)">Delete</button>
          </div>
        </div>
      </section>

      <!-- Group Types -->
      <section class="card">
        <div class="section-header">
          <h3>Group Types</h3>
          <button class="add-btn" @click="startAdd('grouptype')">+ Add</button>
        </div>
        <div v-if="addingType === 'grouptype'" class="inline-form">
          <input v-model="newName" placeholder="Group type name" @keyup.enter="saveNew('grouptype')" />
          <button @click="saveNew('grouptype')">Save</button>
          <button @click="addingType = ''">Cancel</button>
        </div>
        <div v-for="item in groupTypes" :key="item.id" class="list-row">
          <span v-if="editing?.type !== 'grouptype' || editing.id !== item.id">{{ item.name }}</span>
          <input v-else v-model="editing.name" @keyup.enter="saveEdit" />
          <div class="row-actions">
            <button class="small-btn" @click="startEdit('grouptype', item)">Edit</button>
            <button v-if="editing?.type === 'grouptype' && editing.id === item.id" class="small-btn save" @click="saveEdit">Save</button>
            <button class="small-btn danger" @click="deleteItem('grouptype', item.id)">Delete</button>
          </div>
        </div>
      </section>

      <!-- Currencies -->
      <section class="card">
        <div class="section-header">
          <h3>Currencies</h3>
          <button class="add-btn" @click="startAdd('currency')">+ Add</button>
        </div>
        <div v-if="addingType === 'currency'" class="inline-form">
          <input v-model="newCurrency.name" placeholder="Name (e.g. Euro)" />
          <input v-model="newCurrency.symbol" placeholder="Symbol (e.g. €)" style="width:60px" />
          <input v-model="newCurrency.code" placeholder="Code (e.g. EUR)" style="width:70px" />
          <button @click="saveCurrencyNew">Save</button>
          <button @click="addingType = ''">Cancel</button>
        </div>
        <div v-for="item in currencies" :key="item.id" class="list-row">
          <span>{{ item.code }} — {{ item.name }} ({{ item.symbol }})</span>
          <div class="row-actions">
            <button class="small-btn danger" @click="deleteItem('currency', item.id)">Delete</button>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { api } from '@/api'

const categories = ref<any[]>([])
const groupTypes = ref<any[]>([])
const currencies = ref<any[]>([])

const addingType = ref('')
const newName = ref('')
const newCurrency = ref({ name: '', symbol: '', code: '' })
const editing = ref<{ type: string; id: number; name: string } | null>(null)

onMounted(async () => {
  const [cats, gts, curs] = await Promise.all([
    api.categories(),
    api.groupTypes(),
    api.currencies(),
  ])
  categories.value = cats
  groupTypes.value = gts
  currencies.value = curs
})

function startAdd(type: string) {
  addingType.value = type
  newName.value = ''
  newCurrency.value = { name: '', symbol: '', code: '' }
}

function startEdit(type: string, item: any) {
  editing.value = { type, id: item.id, name: item.name }
}

async function saveNew(type: string) {
  if (type === 'category') {
    const c = await api.createCategory({ name: newName.value })
    categories.value.push(c)
  } else if (type === 'grouptype') {
    const g = await api.createGroupType({ name: newName.value })
    groupTypes.value.push(g)
  }
  addingType.value = ''
  newName.value = ''
}

async function saveCurrencyNew() {
  const c = await api.createCurrency(newCurrency.value)
  currencies.value.push(c)
  addingType.value = ''
}

async function saveEdit() {
  if (!editing.value) return
  const { type, id, name } = editing.value
  if (type === 'category') {
    const updated = await api.updateCategory(id, { name })
    const idx = categories.value.findIndex(c => c.id === id)
    if (idx >= 0) categories.value[idx] = updated
  } else if (type === 'grouptype') {
    const updated = await api.updateGroupType(id, { name })
    const idx = groupTypes.value.findIndex(g => g.id === id)
    if (idx >= 0) groupTypes.value[idx] = updated
  }
  editing.value = null
}

async function deleteItem(type: string, id: number) {
  if (!confirm('Delete this item?')) return
  if (type === 'category') {
    await api.deleteCategory(id)
    categories.value = categories.value.filter(c => c.id !== id)
  } else if (type === 'grouptype') {
    await api.deleteGroupType(id)
    groupTypes.value = groupTypes.value.filter(g => g.id !== id)
  } else if (type === 'currency') {
    await api.deleteCurrency(id)
    currencies.value = currencies.value.filter(c => c.id !== id)
  }
}
</script>

<style scoped>
.admin-page { min-height: 100vh; background: #f5f5f5; }

.navbar {
  background: white; padding: 0.75rem 1.5rem;
  display: flex; align-items: center; gap: 1rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.back { color: #42b883; text-decoration: none; font-size: 0.9rem; }
.brand { font-weight: 700; font-size: 1.1rem; color: #2c3e50; }

.content {
  max-width: 700px; margin: 2rem auto; padding: 0 1rem;
  display: flex; flex-direction: column; gap: 1rem;
}

.card {
  background: white; border-radius: 8px; padding: 1.25rem;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}

.section-header {
  display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem;
}

.section-header h3 { margin: 0; color: #2c3e50; }

.add-btn {
  background: #42b883; color: white; border: none;
  border-radius: 4px; padding: 0.3rem 0.75rem; font-size: 0.875rem; cursor: pointer;
}

.inline-form {
  display: flex; gap: 0.5rem; margin-bottom: 0.75rem; align-items: center;
}

.inline-form input {
  flex: 1; padding: 0.4rem 0.6rem; border: 1px solid #ddd; border-radius: 4px; font-size: 0.9rem;
}

.inline-form button {
  padding: 0.35rem 0.75rem; border: 1px solid #ddd; border-radius: 4px;
  font-size: 0.875rem; cursor: pointer; background: white;
}

.list-row {
  display: flex; align-items: center; padding: 0.4rem 0;
  border-bottom: 1px solid #f0f0f0; gap: 0.5rem;
}

.list-row span { flex: 1; font-size: 0.9rem; }
.list-row input {
  flex: 1; padding: 0.3rem 0.5rem; border: 1px solid #42b883; border-radius: 3px; font-size: 0.9rem;
}

.row-actions { display: flex; gap: 0.4rem; }

.small-btn {
  padding: 0.2rem 0.5rem; font-size: 0.75rem; border: 1px solid #ddd;
  border-radius: 3px; background: white; cursor: pointer; color: #555;
}

.small-btn.save { border-color: #42b883; color: #42b883; }
.small-btn.danger { border-color: #e74c3c; color: #e74c3c; }
</style>
