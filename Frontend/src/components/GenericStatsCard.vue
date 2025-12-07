<script setup lang="ts">
interface Props {
  title: string
  value: string | number
  icon?: string
  description?: string
}

withDefaults(defineProps<Props>(), {
  icon: '',
  description: ''
})
</script>

<template>
  <div class="stats-card">
    <div v-if="description" class="stats-content">
      <p class="stats-title">{{ title }}</p>
      <p class="stats-value">{{ value }}</p>
      <p class="stats-description">{{ description }}</p>
    </div>
    <p v-else class="stats-text">{{ icon }} {{ title }}: {{ value }}</p>
  </div>
</template>