<template>
  <div class="icon-picker">
    <input
      v-model="search"
      type="text"
      placeholder="Search icons…"
      class="icon-search"
    />
    <div class="icon-grid">
      <button
        v-for="icon in filteredIcons"
        :key="icon"
        type="button"
        class="icon-item"
        :class="{ selected: icon === modelValue }"
        :title="icon"
        @click="$emit('update:modelValue', icon)"
      >
        <span class="mdi" :class="icon"></span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

defineProps<{
  modelValue?: string
}>()

defineEmits<{
  'update:modelValue': [icon: string]
}>()

const search = ref('')

const icons = [
  'mdi-home', 'mdi-food-apple', 'mdi-car', 'mdi-medical-bag', 'mdi-shopping',
  'mdi-airplane', 'mdi-coffee', 'mdi-beer', 'mdi-pizza', 'mdi-bus',
  'mdi-train', 'mdi-taxi', 'mdi-gas-station', 'mdi-hospital', 'mdi-school',
  'mdi-book', 'mdi-music', 'mdi-movie', 'mdi-gamepad-variant', 'mdi-basketball',
  'mdi-soccer', 'mdi-tennis', 'mdi-dumbbell', 'mdi-swim', 'mdi-run',
  'mdi-bike', 'mdi-walk', 'mdi-dog', 'mdi-cat', 'mdi-flower',
  'mdi-tree', 'mdi-beach', 'mdi-campfire', 'mdi-hiking', 'mdi-ski',
  'mdi-gift', 'mdi-heart', 'mdi-star', 'mdi-cash', 'mdi-credit-card',
  'mdi-cart', 'mdi-store', 'mdi-silverware-fork-knife', 'mdi-glass-cocktail', 'mdi-baby-carriage',
  'mdi-tshirt-crew', 'mdi-shoe-heel', 'mdi-sofa', 'mdi-lamp', 'mdi-washing-machine',
  'mdi-cellphone', 'mdi-laptop', 'mdi-television', 'mdi-camera', 'mdi-headphones',
  'mdi-printer', 'mdi-tools', 'mdi-hammer', 'mdi-wrench', 'mdi-palette',
  'mdi-brush', 'mdi-pill', 'mdi-bandage', 'mdi-thermometer', 'mdi-water',
  'mdi-lightning-bolt', 'mdi-fire', 'mdi-snowflake', 'mdi-umbrella', 'mdi-sun-wireless',
  'mdi-account-group', 'mdi-shape-outline', 'mdi-tag', 'mdi-receipt', 'mdi-chart-bar',
]

const filteredIcons = computed(() => {
  if (!search.value) return icons
  const q = search.value.toLowerCase()
  return icons.filter(icon => icon.toLowerCase().includes(q))
})
</script>

<style scoped>
.icon-picker {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.icon-search {
  padding: 0.4rem 0.6rem;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  font-size: 0.9rem;
  background: var(--color-background);
  color: var(--color-text);
}

.icon-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(2.5rem, 1fr));
  gap: 0.25rem;
  max-height: 12rem;
  overflow-y: auto;
  padding: 0.25rem;
  border: 1px solid var(--color-border);
  border-radius: 6px;
}

.icon-item {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  border: 1px solid transparent;
  border-radius: 4px;
  background: none;
  cursor: pointer;
  color: var(--color-text);
  font-size: 1.25rem;
}

.icon-item:hover {
  background: var(--color-background-soft);
  border-color: var(--color-border);
}

.icon-item.selected {
  background: var(--color-background-soft);
  border-color: var(--color-primary, #4a9eff);
  color: var(--color-primary, #4a9eff);
}
</style>
