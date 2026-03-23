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
          <div class="category-select-wrapper">
            <span v-if="selectedCategory" class="category-select-icon mdi" :class="selectedCategory.icon || 'mdi-shape-outline'"></span>
            <select v-model="form.category" :class="{ 'has-icon': selectedCategory }">
              <option value="">— None —</option>
              <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
            </select>
          </div>
        </div>
        <div class="field">
          <label>Receipts</label>
          <div v-if="receipts.length === 0" class="receipts-empty">No receipts attached</div>
          <div v-else class="receipts-grid">
            <img
              v-for="r in receipts"
              :key="r.id"
              :src="r.image"
              class="receipt-thumb"
              alt="Receipt"
            />
          </div>
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
const receipts = ref<Array<{ id: number; image: string }>>(props.expense.receipts ?? [])
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

const selectedCategory = computed(() =>
  categories.value.find((c: any) => c.id === form.value.category) ?? null
)

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
  background: var(--color-card-bg); border-radius: 8px; padding: 1.5rem;
  width: 100%; max-width: 480px; max-height: 90vh; overflow-y: auto;
}
h3 { margin: 0 0 0.25rem; color: var(--color-heading); }
.last-modified { font-size: 0.75rem; color: var(--color-text-faint); margin: 0 0 1rem; }
.field { margin-bottom: 0.75rem; }
label { display: block; font-size: 0.875rem; font-weight: 500; margin-bottom: 0.25rem; }
input, select {
  width: 100%; padding: 0.4rem 0.6rem; border: 1px solid var(--color-input-border);
  border-radius: 4px; font-size: 0.95rem; box-sizing: border-box;
  background: var(--color-input-bg); color: var(--color-text);
}
.toggle { display: flex; gap: 0.5rem; }
.toggle button {
  flex: 1; padding: 0.4rem; border: 1px solid var(--color-input-border); border-radius: 4px;
  background: var(--color-card-bg); cursor: pointer; font-size: 0.875rem; color: var(--color-text);
}
.toggle button.active { background: var(--color-primary); color: white; border-color: var(--color-primary); }
.split-info { font-size: 0.875rem; color: var(--color-text-secondary); background: var(--color-info-bg); padding: 0.5rem; border-radius: 4px; }
.custom-splits .split-row { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.4rem; }
.custom-splits .split-row span { width: 120px; font-size: 0.875rem; }
.custom-splits .split-row input { flex: 1; }
.actions { display: flex; gap: 0.75rem; justify-content: flex-end; margin-top: 1rem; }
.actions button {
  padding: 0.4rem 1rem; border-radius: 4px; font-size: 0.9rem; cursor: pointer;
  border: 1px solid var(--color-input-border); background: var(--color-card-bg); color: var(--color-text);
}
.actions button[type="submit"] { background: var(--color-primary); color: white; border-color: var(--color-primary); }
.actions button:disabled { opacity: 0.6; cursor: not-allowed; }
.error { color: var(--color-danger); font-size: 0.875rem; }

.receipts-empty { font-size: 0.875rem; color: var(--color-text-placeholder); }
.receipts-grid { display: flex; flex-wrap: wrap; gap: 0.5rem; }
.receipt-thumb { max-height: 80px; border-radius: 4px; cursor: pointer; object-fit: contain; }

.category-select-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.category-select-icon {
  position: absolute;
  left: 0.5rem;
  font-size: 1.1rem;
  color: var(--color-primary);
  pointer-events: none;
  z-index: 1;
}

.category-select-wrapper select.has-icon {
  padding-left: 2rem;
}

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
