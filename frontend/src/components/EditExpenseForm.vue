<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal">
      <h3>Edit Expense</h3>
      <p class="last-modified">Last modified: {{ new Date(expense.updated_at).toLocaleString() }}</p>
      <form @submit.prevent="submit">
        <div class="field">
          <label>Amount</label>
          <input v-model="form.amount" type="number" step="0.01" min="0.01" required />
        </div>
        <div class="field">
          <label>Description</label>
          <input v-model="form.description" type="text" required />
        </div>
        <div class="field">
          <label>Date</label>
          <input v-model="form.date" type="date" required />
        </div>
        <div class="field">
          <label>Category</label>
          <select v-model="form.category">
            <option value="">— None —</option>
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
          </select>
        </div>
        <div class="field">
          <label>Replace receipt image</label>
          <input type="file" accept="image/*" @change="onFile" />
        </div>
        <div class="field">
          <label>Split method</label>
          <div class="toggle">
            <button type="button" :class="{ active: splitMethod === 'equal' }" @click="splitMethod = 'equal'">Equal</button>
            <button type="button" :class="{ active: splitMethod === 'custom' }" @click="splitMethod = 'custom'">Custom</button>
          </div>
        </div>
        <div v-if="splitMethod === 'equal'" class="split-info">
          Equal split: {{ equalShare }} each ({{ members.length }} members)
        </div>
        <div v-else class="custom-splits">
          <div v-for="m in members" :key="m.id" class="split-row">
            <span>{{ m.username }}</span>
            <input v-model="customSplits[m.id]" type="number" step="0.01" min="0" />
          </div>
          <p v-if="splitError" class="error">{{ splitError }}</p>
        </div>
        <p v-if="error" class="error">{{ error }}</p>
        <div class="actions">
          <button type="button" @click="$emit('close')">Cancel</button>
          <button type="submit" :disabled="loading">{{ loading ? 'Saving…' : 'Save Changes' }}</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { api } from '@/api'

const props = defineProps<{
  expense: any
  members: Array<{ id: number; username: string }>
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'saved'): void
}>()

const form = ref({
  amount: String(props.expense.amount),
  description: props.expense.description,
  date: props.expense.date,
  category: props.expense.category ?? '' as number | '',
})

const splitMethod = ref('equal')
const customSplits = ref<Record<number, string>>({})
const categories = ref<any[]>([])
const receiptFile = ref<File | null>(null)
const loading = ref(false)
const error = ref('')
const splitError = ref('')

onMounted(async () => {
  categories.value = await api.categories()
  // Initialise from existing splits
  if (props.expense.splits?.length) {
    splitMethod.value = 'custom'
    for (const s of props.expense.splits) {
      customSplits.value[s.user] = String(s.amount)
    }
  } else {
    for (const m of props.members) {
      customSplits.value[m.id] = ''
    }
  }
})

const equalShare = computed(() => {
  const amt = parseFloat(form.value.amount)
  if (!amt || props.members.length === 0) return '0.00'
  return (amt / props.members.length).toFixed(2)
})

function onFile(e: Event) {
  const input = e.target as HTMLInputElement
  receiptFile.value = input.files?.[0] ?? null
}

async function submit() {
  error.value = ''
  splitError.value = ''
  loading.value = true
  try {
    const payload: any = {
      amount: parseFloat(form.value.amount),
      description: form.value.description,
      date: form.value.date,
      category: form.value.category || null,
    }

    if (splitMethod.value === 'custom') {
      const splits = props.members.map(m => ({
        user_id: m.id,
        amount: parseFloat(customSplits.value[m.id] || '0'),
      }))
      const total = splits.reduce((s, x) => s + x.amount, 0)
      if (Math.abs(total - payload.amount) > 0.01) {
        splitError.value = `Split total (${total.toFixed(2)}) must equal expense amount`
        loading.value = false
        return
      }
      payload.split_data = splits
    }

    if (receiptFile.value) {
      const form2 = new FormData()
      form2.append('receipt_image', receiptFile.value)
      Object.entries(payload).forEach(([k, v]) => form2.append(k, String(v)))
      await fetch(`/api/expenses/${props.expense.id}/`, {
        method: 'PATCH',
        credentials: 'include',
        headers: { 'X-CSRFToken': document.cookie.match(/csrftoken=([^;]+)/)?.[1] ?? '' },
        body: form2,
      })
    } else {
      await api.updateExpense(props.expense.id, payload)
    }

    emit('saved')
  } catch (e: any) {
    error.value = e?.detail ?? 'Failed to save'
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
  width: 100%; max-width: 480px; max-height: 90vh; overflow-y: auto;
}
h3 { margin: 0 0 0.25rem; color: #2c3e50; }
.last-modified { font-size: 0.75rem; color: #aaa; margin: 0 0 1rem; }
.field { margin-bottom: 0.75rem; }
label { display: block; font-size: 0.875rem; font-weight: 500; margin-bottom: 0.25rem; }
input, select {
  width: 100%; padding: 0.4rem 0.6rem; border: 1px solid #ddd;
  border-radius: 4px; font-size: 0.95rem; box-sizing: border-box;
}
.toggle { display: flex; gap: 0.5rem; }
.toggle button {
  flex: 1; padding: 0.4rem; border: 1px solid #ddd; border-radius: 4px;
  background: white; cursor: pointer; font-size: 0.875rem;
}
.toggle button.active { background: #42b883; color: white; border-color: #42b883; }
.split-info { font-size: 0.875rem; color: #555; background: #f8f8f8; padding: 0.5rem; border-radius: 4px; }
.custom-splits .split-row { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.4rem; }
.custom-splits .split-row span { width: 120px; font-size: 0.875rem; }
.custom-splits .split-row input { flex: 1; }
.actions { display: flex; gap: 0.75rem; justify-content: flex-end; margin-top: 1rem; }
.actions button {
  padding: 0.4rem 1rem; border-radius: 4px; font-size: 0.9rem; cursor: pointer;
  border: 1px solid #ddd; background: white;
}
.actions button[type="submit"] { background: #42b883; color: white; border-color: #42b883; }
.actions button:disabled { opacity: 0.6; cursor: not-allowed; }
.error { color: #e74c3c; font-size: 0.875rem; }

/* Responsive modal — US-009 */
@media (max-width: 479px) {
  .modal {
    max-width: calc(100% - 16px);
    margin: 8px;
    padding: 1rem;
  }
}

@media (max-width: 767px) {
  input, select {
    min-height: 44px;
  }
  .toggle button {
    min-height: 44px;
  }
  .actions {
    position: sticky;
    bottom: -1.5rem;
    background: white;
    padding: 0.75rem 0;
    margin-bottom: -1.5rem;
  }
  .actions button {
    min-height: 44px;
    flex: 1;
  }
}
</style>
