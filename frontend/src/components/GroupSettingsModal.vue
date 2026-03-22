<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal">
      <h3>Group Settings</h3>
      <form @submit.prevent="submit">
        <div class="field">
          <label>Name</label>
          <input v-model="form.name" type="text" required placeholder="Group name" />
        </div>
        <div class="field">
          <label>Icon</label>
          <IconPicker v-model="form.icon" />
        </div>
        <p v-if="error" class="error">{{ error }}</p>
        <div class="actions">
          <button type="button" @click="$emit('close')">Cancel</button>
          <button type="submit" :disabled="loading">{{ loading ? 'Saving…' : 'Save' }}</button>
        </div>
      </form>

      <!-- Member Management -->
      <div class="members-section">
        <h4>Members</h4>
        <div class="member-list">
          <div v-for="m in members" :key="m.id" class="member-row">
            <span class="member-name">{{ m.display_name || m.username }}</span>
            <span class="member-username">@{{ m.username }}</span>
            <button
              v-if="m.id !== currentUserId"
              class="remove-btn"
              :disabled="removingId === m.id"
              @click="removeMember(m)"
            >{{ removingId === m.id ? 'Removing…' : 'Remove' }}</button>
            <span v-else class="owner-badge">you</span>
          </div>
        </div>
        <div class="add-member">
          <input
            v-model="newUsername"
            type="text"
            placeholder="Username to add"
            @keydown.enter.prevent="addMember"
          />
          <button type="button" :disabled="!newUsername.trim() || adding" @click="addMember">
            {{ adding ? 'Adding…' : 'Add' }}
          </button>
        </div>
        <p v-if="memberError" class="error">{{ memberError }}</p>
        <p v-if="memberSuccess" class="success">{{ memberSuccess }}</p>
      </div>

      <!-- Delete Group -->
      <div class="danger-section">
        <h4>Danger Zone</h4>
        <div v-if="!confirmingDelete">
          <button class="danger-btn" @click="confirmingDelete = true">Delete Group</button>
        </div>
        <div v-else class="confirm-delete">
          <p class="danger-text">Are you sure? This will permanently delete the group, all expenses, and settlements.</p>
          <div class="confirm-actions">
            <button type="button" @click="confirmingDelete = false">Cancel</button>
            <button class="danger-btn" :disabled="deleting" @click="deleteGroup">
              {{ deleting ? 'Deleting…' : 'Yes, delete' }}
            </button>
          </div>
          <p v-if="deleteError" class="error">{{ deleteError }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { api } from '@/api'
import IconPicker from '@/components/IconPicker.vue'

const props = defineProps<{
  groupId: number
  name: string
  icon: string
  membersList: Array<{ id: number; username: string; display_name: string }>
  currentUserId: number
}>()

const emit = defineEmits<{
  close: []
  saved: [group: any]
  membersChanged: []
  deleted: []
}>()

const loading = ref(false)
const error = ref('')

const form = ref({
  name: props.name,
  icon: props.icon || 'mdi-account-group',
})

const members = ref([...props.membersList])
const newUsername = ref('')
const adding = ref(false)
const removingId = ref<number | null>(null)
const memberError = ref('')
const memberSuccess = ref('')

async function submit() {
  loading.value = true
  error.value = ''
  try {
    const updated = await api.updateGroup(props.groupId, {
      name: form.value.name,
      icon: form.value.icon,
    })
    emit('saved', updated)
  } catch (e: any) {
    error.value = e.detail || e.name?.[0] || 'Failed to update group'
  } finally {
    loading.value = false
  }
}

async function addMember() {
  const username = newUsername.value.trim()
  if (!username) return
  adding.value = true
  memberError.value = ''
  memberSuccess.value = ''
  try {
    await api.addMemberByUsername(props.groupId, username)
    // Re-fetch group to get updated members_list
    const groups = await api.groups()
    const updated = groups.find((g: any) => g.id === props.groupId)
    if (updated) {
      members.value = updated.members_list ?? []
    }
    newUsername.value = ''
    memberSuccess.value = `${username} added`
    emit('membersChanged')
    setTimeout(() => { memberSuccess.value = '' }, 2000)
  } catch (e: any) {
    memberError.value = e.detail || 'User not found'
  } finally {
    adding.value = false
  }
}

const confirmingDelete = ref(false)
const deleting = ref(false)
const deleteError = ref('')

async function deleteGroup() {
  deleting.value = true
  deleteError.value = ''
  try {
    await api.deleteGroup(props.groupId)
    emit('deleted')
  } catch (e: any) {
    deleteError.value = e.detail || 'Failed to delete group'
  } finally {
    deleting.value = false
  }
}

async function removeMember(m: { id: number; username: string }) {
  removingId.value = m.id
  memberError.value = ''
  memberSuccess.value = ''
  try {
    await api.removeMember(props.groupId, m.id)
    members.value = members.value.filter(x => x.id !== m.id)
    memberSuccess.value = `${m.username} removed`
    emit('membersChanged')
    setTimeout(() => { memberSuccess.value = '' }, 2000)
  } catch (e: any) {
    memberError.value = e.detail || 'Failed to remove member'
  } finally {
    removingId.value = null
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.modal {
  background: var(--color-card-bg);
  border-radius: 8px;
  padding: 1.5rem;
  width: 100%;
  max-width: 480px;
  max-height: 90vh;
  overflow-y: auto;
}

h3 { margin: 0 0 1rem; color: var(--color-heading); }
h4 { margin: 0 0 0.5rem; color: var(--color-heading); font-size: 0.95rem; }

.field { margin-bottom: 0.75rem; }
label { display: block; font-size: 0.875rem; font-weight: 500; margin-bottom: 0.25rem; }
input {
  width: 100%;
  padding: 0.4rem 0.6rem;
  border: 1px solid var(--color-input-border);
  border-radius: 4px;
  font-size: 0.95rem;
  box-sizing: border-box;
  background: var(--color-card-bg);
  color: var(--color-text);
}

.actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
  margin-top: 1rem;
}

.actions button {
  padding: 0.4rem 1rem;
  border-radius: 4px;
  font-size: 0.9rem;
  cursor: pointer;
  border: 1px solid var(--color-input-border);
  background: var(--color-card-bg);
  color: var(--color-text);
}

.actions button[type="submit"] {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

.actions button:disabled { opacity: 0.6; cursor: not-allowed; }

.error { color: var(--color-danger); font-size: 0.875rem; margin: 0.25rem 0; }
.success { color: var(--color-success); font-size: 0.875rem; margin: 0.25rem 0; }

.members-section {
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--color-border);
}

.member-list {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  margin-bottom: 0.75rem;
}

.member-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.35rem 0;
  font-size: 0.9rem;
}

.member-name { font-weight: 500; }
.member-username { color: var(--color-text-muted); font-size: 0.8rem; flex: 1; }

.owner-badge {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  background: var(--color-background-soft);
  padding: 0.1rem 0.4rem;
  border-radius: 3px;
}

.remove-btn {
  font-size: 0.75rem;
  padding: 0.15rem 0.5rem;
  border: 1px solid var(--color-danger);
  border-radius: 3px;
  background: var(--color-card-bg);
  color: var(--color-danger);
  cursor: pointer;
}

.remove-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.add-member {
  display: flex;
  gap: 0.5rem;
}

.add-member input { flex: 1; }

.add-member button {
  padding: 0.4rem 0.75rem;
  border: 1px solid var(--color-primary);
  border-radius: 4px;
  background: var(--color-primary);
  color: white;
  cursor: pointer;
  font-size: 0.875rem;
  white-space: nowrap;
}

.add-member button:disabled { opacity: 0.5; cursor: not-allowed; }

.danger-section {
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--color-danger);
}

.danger-btn {
  padding: 0.4rem 1rem;
  border: 1px solid var(--color-danger);
  border-radius: 4px;
  background: var(--color-danger);
  color: white;
  cursor: pointer;
  font-size: 0.875rem;
}

.danger-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.danger-text {
  color: var(--color-danger);
  font-size: 0.875rem;
  margin: 0 0 0.75rem;
}

.confirm-delete { }

.confirm-actions {
  display: flex;
  gap: 0.75rem;
}

.confirm-actions button {
  padding: 0.4rem 1rem;
  border-radius: 4px;
  font-size: 0.875rem;
  cursor: pointer;
  border: 1px solid var(--color-input-border);
  background: var(--color-card-bg);
  color: var(--color-text);
}

@media (max-width: 479px) {
  .modal {
    max-width: 100%;
    margin: 0 0.5rem;
    max-height: 95vh;
  }
  .actions {
    position: sticky;
    bottom: -1.5rem;
    background: var(--color-card-bg);
    padding: 0.75rem 0;
    margin-bottom: -1.5rem;
  }
  .actions button {
    min-height: 44px;
    flex: 1;
  }
  .remove-btn { min-height: 44px; }
  .add-member button { min-height: 44px; }
}
</style>
