<script setup lang="ts">
interface Props {
  title: string
  count: number | string
  description: string
  icon: string
  onClick: () => void
}

defineProps<Props>()
</script>

<template>
  <button @click="onClick" class="feature-card">
    <div class="feature-icon">
      <span class="icon">{{ icon }}</span>
    </div>
    <h3 class="feature-title">{{ title }}</h3>
    <div class="feature-count">{{ count }}</div>
    <p class="feature-description">{{ description }}</p>
  </button>
</template>