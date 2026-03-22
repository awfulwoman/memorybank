<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal">
      <h3>Record Settlement</h3>
      <form @submit.prevent="submit">
        <div class="field">
          <label>Pay to</label>
          <select v-model="form.payee" required>
            <option value="">— Select member —</option>
            <option v-for="m in otherMembers" :key="m.id" :value="m.id">{{ m.username }}</option>
          </select>
        </div>
        <div class="field">
          <label>Amount</label>
          <input v-model="form.amount" type="number" step="0.01" min="0.01" required />
        </div>
        <div class="field">
          <label>Date</label>
          <input v-model="form.date" type="date" required />
        </div>
        <p v-if="error" class="error">{{ error }}</p>
        <div class="actions">
          <button type="button" @click="$emit('close')">Cancel</button>
          <button type="submit" :disabled="loading">{{ loading ? 'Saving…' : 'Record' }}</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { api } from '@/api'
import { useAuthStore } from '@/stores/auth'

const props = defineProps<{
  groupId: number
  members: Array<{ id: number; username: string }>
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'saved'): void
}>()

const auth = useAuthStore()
const today = new Date().toISOString().slice(0, 10)

const form = ref({
  payee: '' as number | '',
  amount: '',
  date: today,
})

const loading = ref(false)
const error = ref('')

const otherMembers = computed(() =>
  props.members.filter(m => m.id !== auth.user?.id)
)

async function submit() {
  error.value = ''
  loading.value = true
  try {
    await api.createSettlement(props.groupId, {
      payee: form.value.payee,
      amount: parseFloat(form.value.amount),
      date: form.value.date,
    })
    emit('saved')
  } catch (e: any) {
    error.value = e?.detail ?? 'Failed to record settlement'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.5);
  display: flex; align-items: center; justify-content: center; z-index: 100;
}
.modal {
  background: white; border-radius: 8px; padding: 1.5rem;
  width: 100%; max-width: 400px;
}
h3 { margin: 0 0 1rem; color: #2c3e50; }
.field { margin-bottom: 0.75rem; }
label { display: block; font-size: 0.875rem; font-weight: 500; margin-bottom: 0.25rem; }
input, select {
  width: 100%; padding: 0.4rem 0.6rem; border: 1px solid #ddd;
  border-radius: 4px; font-size: 0.95rem; box-sizing: border-box;
}
.actions { display: flex; gap: 0.75rem; justify-content: flex-end; margin-top: 1rem; }
.actions button {
  padding: 0.4rem 1rem; border-radius: 4px; font-size: 0.9rem; cursor: pointer;
  border: 1px solid #ddd; background: white;
}
.actions button[type="submit"] { background: #42b883; color: white; border-color: #42b883; }
.actions button:disabled { opacity: 0.6; cursor: not-allowed; }
.error { color: #e74c3c; font-size: 0.875rem; }
</style>
