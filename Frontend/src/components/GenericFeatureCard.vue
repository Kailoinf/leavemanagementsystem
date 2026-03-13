<script setup lang="ts">
interface Props {
  title: string
  count: number | string
  description: string
  onClick: () => void
}

defineProps<Props>()
</script>

<template>
  <button @click="onClick" class="feature-card">
    <h3 class="feature-title">{{ title }}</h3>
    <div class="feature-count">{{ count }}</div>
    <p class="feature-description">{{ description }}</p>
  </button>
</template>

<style scoped>
.feature-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: var(--spacing-xl);
  background-color: var(--bg-primary);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow);
  transition: all var(--transition);
  cursor: pointer;
  text-decoration: none;
  color: inherit;
  min-height: 200px;
  position: relative;
  overflow: hidden;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
  border-color: var(--primary-200);
}

.feature-card:active {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.feature-icon {
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--primary-500), var(--primary-600));
  border-radius: var(--radius-xl);
  margin-bottom: var(--spacing);
  box-shadow: var(--shadow-md);
}

.icon {
  font-size: 1.5rem;
  color: var(--text-inverse);
}

.feature-title {
  font-size: var(--text-xl);
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--spacing-sm);
  line-height: var(--leading-tight);
}

.feature-count {
  font-size: var(--text-3xl);
  font-weight: 700;
  color: var(--primary-600);
  margin-bottom: var(--spacing-sm);
  line-height: 1;
}

.feature-description {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  line-height: var(--leading-normal);
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .feature-card {
    padding: var(--spacing-lg);
    min-height: 160px;
  }

  .feature-icon {
    width: 50px;
    height: 50px;
  }

  .feature-title {
    font-size: var(--text-lg);
  }

  .feature-count {
    font-size: var(--text-2xl);
  }
}

@media (max-width: 480px) {
  .feature-card {
    padding: var(--spacing);
    min-height: 140px;
  }

  .feature-icon {
    width: 40px;
    height: 40px;
  }

  .icon {
    font-size: 1.25rem;
  }

  .feature-title {
    font-size: var(--text-base);
  }

  .feature-count {
    font-size: var(--text-xl);
  }

  .feature-description {
    font-size: var(--text-xs);
  }
}
</style>