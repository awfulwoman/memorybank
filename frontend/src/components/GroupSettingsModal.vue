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
}>()

const emit = defineEmits<{
  close: []
  saved: [group: any]
}>()

const loading = ref(false)
const error = ref('')

const form = ref({
  name: props.name,
  icon: props.icon || 'mdi-account-group',
})

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

.error { color: var(--color-danger); font-size: 0.875rem; }

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
}
</style>
