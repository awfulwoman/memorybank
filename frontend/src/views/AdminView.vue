<template>
  <div class="admin-page">
    <AppNavbar />

    <main class="content">
      <!-- Categories -->
      <section class="card">
        <div class="section-header">
          <h3>Categories</h3>
          <button class="add-btn" @click="startAdd('category')">+ Add</button>
        </div>
        <div v-if="addingType === 'category'" class="category-form">
          <div class="inline-form">
            <span class="mdi" :class="newCategoryIcon" style="font-size:1.25rem"></span>
            <input v-model="newName" placeholder="Category name" @keyup.enter="saveNew('category')" />
            <button @click="saveNew('category')">Save</button>
            <button @click="addingType = ''">Cancel</button>
          </div>
          <IconPicker v-model="newCategoryIcon" />
        </div>
        <div class="table-scroll-container">
          <div v-for="item in categories" :key="item.id">
            <div class="list-row">
              <span v-if="editing?.type !== 'category' || editing.id !== item.id">
                <span class="mdi" :class="item.icon || 'mdi-shape-outline'" style="font-size:1.1rem; margin-right:0.4rem; color:var(--color-primary)"></span>{{ item.name }}
              </span>
              <template v-else>
                <span class="mdi" :class="editing.icon || 'mdi-shape-outline'" style="font-size:1.1rem; margin-right:0.4rem; color:var(--color-primary)"></span>
                <input v-model="editing.name" @keyup.enter="saveEdit" />
              </template>
              <div class="row-actions">
                <button class="small-btn" @click="startEdit('category', item)">Edit</button>
                <button v-if="editing?.type === 'category' && editing.id === item.id" class="small-btn save" @click="saveEdit">Save</button>
                <button class="small-btn danger" @click="deleteItem('category', item.id)">Delete</button>
              </div>
            </div>
            <div v-if="editing?.type === 'category' && editing.id === item.id" class="edit-icon-picker">
              <IconPicker v-model="editing.icon" />
            </div>
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
        <div class="table-scroll-container">
          <div v-for="item in groupTypes" :key="item.id" class="list-row">
            <span v-if="editing?.type !== 'grouptype' || editing.id !== item.id">{{ item.name }}</span>
            <input v-else v-model="editing.name" @keyup.enter="saveEdit" />
            <div class="row-actions">
              <button class="small-btn" @click="startEdit('grouptype', item)">Edit</button>
              <button v-if="editing?.type === 'grouptype' && editing.id === item.id" class="small-btn save" @click="saveEdit">Save</button>
              <button class="small-btn danger" @click="deleteItem('grouptype', item.id)">Delete</button>
            </div>
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
        <div class="table-scroll-container">
          <div v-for="item in currencies" :key="item.id" class="list-row">
            <span>{{ item.code }} — {{ item.name }} ({{ item.symbol }})</span>
            <div class="row-actions">
              <button class="small-btn danger" @click="deleteItem('currency', item.id)">Delete</button>
            </div>
          </div>
        </div>
      </section>

      <!-- Users -->
      <section class="card">
        <div class="section-header">
          <h3>Users</h3>
          <button class="add-btn" @click="startAdd('user')">+ Add User</button>
        </div>
        <div v-if="addingType === 'user'" class="inline-form">
          <input v-model="newUser.username" placeholder="Username" />
          <input v-model="newUser.display_name" placeholder="Display name" />
          <input v-model="newUser.password" type="password" placeholder="Password" />
          <button @click="saveNewUser">Save</button>
          <button @click="addingType = ''">Cancel</button>
        </div>
        <div class="table-scroll-container">
          <div v-for="user in adminUsers" :key="user.id" class="list-row">
            <span :class="{ inactive: !user.is_active }">{{ user.username }} <small>{{ user.display_name }}</small></span>
            <span v-if="user.is_staff" class="badge">admin</span>
            <span v-if="!user.is_active" class="badge inactive-badge">inactive</span>
            <div class="row-actions">
              <button
                class="small-btn"
                :class="user.is_active ? 'danger' : ''"
                @click="toggleActive(user)"
              >{{ user.is_active ? 'Deactivate' : 'Reactivate' }}</button>
            </div>
          </div>
        </div>
      </section>

      <!-- Groups -->
      <section class="card">
        <div class="section-header">
          <h3>Groups</h3>
          <button class="add-btn" @click="startAdd('group')">+ Add Group</button>
        </div>
        <div v-if="addingType === 'group'" class="inline-form">
          <input v-model="newGroup.name" placeholder="Group name" />
          <select v-model="newGroup.group_type">
            <option value="">— Type —</option>
            <option v-for="gt in groupTypes" :key="gt.id" :value="gt.id">{{ gt.name }}</option>
          </select>
          <select v-model="newGroup.currency">
            <option value="">— Currency —</option>
            <option v-for="c in currencies" :key="c.id" :value="c.id">{{ c.code }}</option>
          </select>
          <select v-model="newGroup.default_split_method">
            <option value="equal">Equal</option>
            <option value="custom">Custom</option>
          </select>
          <button @click="saveNewGroup">Save</button>
          <button @click="addingType = ''">Cancel</button>
        </div>
        <div class="table-scroll-container">
          <div v-for="group in adminGroups" :key="group.id" class="list-row">
            <span>{{ group.name }} <small>{{ group.group_type_name }} · {{ group.currency_code }} · {{ group.member_count }} members</small></span>
            <div class="row-actions">
              <button class="small-btn" @click="managingGroup = group">Members</button>
            </div>
          </div>
        </div>
        <!-- Member management inline -->
        <div v-if="managingGroup" class="member-panel">
          <h4>Members of {{ managingGroup.name }}</h4>
          <div class="inline-form">
            <select v-model="addMemberId">
              <option value="">— Add user —</option>
              <option v-for="u in adminUsers" :key="u.id" :value="u.id">{{ u.username }}</option>
            </select>
            <button @click="addGroupMember">Add</button>
          </div>
          <div v-for="uid in managingGroupMemberIds" :key="uid" class="list-row">
            <span>{{ adminUsers.find(u => u.id === uid)?.username ?? uid }}</span>
            <button class="small-btn danger" @click="removeGroupMember(uid)">Remove</button>
          </div>
          <button class="small-btn" @click="managingGroup = null">Close</button>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { api } from '@/api'
import AppNavbar from '@/components/AppNavbar.vue'
import IconPicker from '@/components/IconPicker.vue'

const categories = ref<any[]>([])
const groupTypes = ref<any[]>([])
const currencies = ref<any[]>([])
const adminUsers = ref<any[]>([])
const adminGroups = ref<any[]>([])

const addingType = ref('')
const newName = ref('')
const newCategoryIcon = ref('mdi-shape-outline')
const newCurrency = ref({ name: '', symbol: '', code: '' })
const newUser = ref({ username: '', display_name: '', password: '' })
const newGroup = ref({ name: '', group_type: '' as number | '', currency: '' as number | '', default_split_method: 'equal' })
const editing = ref<{ type: string; id: number; name: string; icon?: string } | null>(null)
const managingGroup = ref<any>(null)
const addMemberId = ref<number | ''>('')

const managingGroupMemberIds = ref<number[]>([])

watch(managingGroup, (g) => {
  managingGroupMemberIds.value = g?.member_ids ?? []
})

onMounted(async () => {
  const [cats, gts, curs, users, groups] = await Promise.all([
    api.categories(),
    api.groupTypes(),
    api.currencies(),
    api.adminUsers(),
    api.groups(),
  ])
  categories.value = cats
  groupTypes.value = gts
  currencies.value = curs
  adminUsers.value = users
  adminGroups.value = groups
})

function startAdd(type: string) {
  addingType.value = type
  newName.value = ''
  newCategoryIcon.value = 'mdi-shape-outline'
  newCurrency.value = { name: '', symbol: '', code: '' }
}

function startEdit(type: string, item: any) {
  editing.value = { type, id: item.id, name: item.name, icon: item.icon }
}

async function saveNew(type: string) {
  if (type === 'category') {
    const c = await api.createCategory({ name: newName.value, icon: newCategoryIcon.value })
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
    const updated = await api.updateCategory(id, { name, icon: editing.value.icon })
    const idx = categories.value.findIndex(c => c.id === id)
    if (idx >= 0) categories.value[idx] = updated
  } else if (type === 'grouptype') {
    const updated = await api.updateGroupType(id, { name })
    const idx = groupTypes.value.findIndex(g => g.id === id)
    if (idx >= 0) groupTypes.value[idx] = updated
  }
  editing.value = null
}

async function saveNewUser() {
  const u = await api.createUser(newUser.value)
  adminUsers.value.push(u)
  addingType.value = ''
  newUser.value = { username: '', display_name: '', password: '' }
}

async function toggleActive(user: any) {
  const updated = await api.updateUser(user.id, { is_active: !user.is_active })
  const idx = adminUsers.value.findIndex(u => u.id === user.id)
  if (idx >= 0) adminUsers.value[idx] = updated
}

async function saveNewGroup() {
  const g = await api.createGroup({
    name: newGroup.value.name,
    group_type: newGroup.value.group_type || null,
    currency: newGroup.value.currency || null,
    default_split_method: newGroup.value.default_split_method,
  })
  adminGroups.value.push(g)
  addingType.value = ''
  newGroup.value = { name: '', group_type: '', currency: '', default_split_method: 'equal' }
}

async function addGroupMember() {
  if (!managingGroup.value || !addMemberId.value) return
  await api.addMember(managingGroup.value.id, Number(addMemberId.value))
  managingGroupMemberIds.value.push(Number(addMemberId.value))
  addMemberId.value = ''
  await refreshGroupMembers()
}

async function removeGroupMember(userId: number) {
  if (!managingGroup.value) return
  await api.removeMember(managingGroup.value.id, userId)
  managingGroupMemberIds.value = managingGroupMemberIds.value.filter(id => id !== userId)
}

async function refreshGroupMembers() {
  const groups = await api.groups()
  const g = groups.find((x: any) => x.id === managingGroup.value?.id)
  if (g) managingGroup.value = g
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
.admin-page { min-height: 100vh; background: var(--color-page-bg); }

.content {
  max-width: 700px; margin: 2rem auto; padding: 0 1rem;
  display: flex; flex-direction: column; gap: 1rem;
}

.card {
  background: var(--color-card-bg); border-radius: 8px; padding: 1.25rem;
  box-shadow: 0 1px 4px var(--color-card-shadow);
}

.section-header {
  display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem;
}

.section-header h3 { margin: 0; color: var(--color-heading); }

.add-btn {
  background: var(--color-primary); color: white; border: none;
  border-radius: 4px; padding: 0.3rem 0.75rem; font-size: 0.875rem; cursor: pointer;
}

.inline-form {
  display: flex; gap: 0.5rem; margin-bottom: 0.75rem; align-items: center;
}

.inline-form input {
  flex: 1; padding: 0.4rem 0.6rem; border: 1px solid var(--color-input-border); border-radius: 4px; font-size: 0.9rem;
  background: var(--color-input-bg); color: var(--color-text);
}

.inline-form button {
  padding: 0.35rem 0.75rem; border: 1px solid var(--color-input-border); border-radius: 4px;
  font-size: 0.875rem; cursor: pointer; background: var(--color-card-bg); color: var(--color-text);
}

.list-row {
  display: flex; align-items: center; padding: 0.4rem 0;
  border-bottom: 1px solid var(--color-border); gap: 0.5rem;
}

.list-row span { flex: 1; font-size: 0.9rem; }
.list-row input {
  flex: 1; padding: 0.3rem 0.5rem; border: 1px solid var(--color-primary); border-radius: 3px; font-size: 0.9rem;
  background: var(--color-input-bg); color: var(--color-text);
}

.row-actions { display: flex; gap: 0.4rem; }

.small-btn {
  padding: 0.2rem 0.5rem; font-size: 0.75rem; border: 1px solid var(--color-input-border);
  border-radius: 3px; background: var(--color-card-bg); cursor: pointer; color: var(--color-text-secondary);
}

.small-btn.save { border-color: var(--color-primary); color: var(--color-primary); }
.small-btn.danger { border-color: var(--color-danger); color: var(--color-danger); }

.badge {
  font-size: 0.7rem; padding: 0.1rem 0.4rem; border-radius: 3px;
  background: var(--color-primary); color: white; margin-left: 0.25rem;
}

.inactive-badge { background: var(--color-badge-inactive); }
.inactive { color: var(--color-text-faint); text-decoration: line-through; }

.category-form { margin-bottom: 0.75rem; }
.edit-icon-picker { padding: 0.5rem 0; border-bottom: 1px solid var(--color-border); }

.member-panel {
  margin-top: 1rem; border-top: 1px solid var(--color-border); padding-top: 0.75rem;
}

.member-panel h4 { margin: 0 0 0.5rem; font-size: 0.9rem; color: var(--color-text-secondary); }

/* Responsive: phone (<768px) */
@media (max-width: 767px) {
  .inline-form {
    flex-direction: column;
    align-items: stretch;
  }

  .inline-form input,
  .inline-form select {
    min-height: 44px;
    width: 100% !important;
  }

  .inline-form button {
    min-height: 44px;
  }

  .list-row {
    flex-wrap: wrap;
  }

  .list-row span {
    flex: 1 1 100%;
  }

  .row-actions {
    flex-wrap: wrap;
    width: 100%;
  }

  .small-btn {
    min-height: 44px;
    flex: 1;
  }

  .add-btn {
    min-height: 44px;
  }

  .card {
    overflow-x: auto;
  }
}
</style>
