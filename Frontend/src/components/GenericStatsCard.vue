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

<style scoped>
.stats-card {
  background-color: var(--bg-primary);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow);
  transition: all var(--transition);
}

.stats-card:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--border-medium);
}

.stats-content {
  text-align: center;
}

.stats-title {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: var(--spacing-sm);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stats-value {
  font-size: var(--text-3xl);
  font-weight: 700;
  color: var(--primary-600);
  margin-bottom: var(--spacing-sm);
  line-height: 1;
}

.stats-description {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
  margin: 0;
  line-height: var(--leading-normal);
}

.stats-text {
  font-size: var(--text-base);
  color: var(--text-secondary);
  margin: 0;
  line-height: var(--leading-normal);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .stats-card {
    padding: var(--spacing);
  }
  
  .stats-value {
    font-size: var(--text-2xl);
  }
}

@media (max-width: 480px) {
  .stats-card {
    padding: var(--spacing-sm);
  }
  
  .stats-value {
    font-size: var(--text-xl);
  }
  
  .stats-title {
    font-size: var(--text-xs);
  }
  
  .stats-description,
  .stats-text {
    font-size: var(--text-xs);
  }
}
</style>