<script setup lang="ts">
import { onMounted } from 'vue'
import { usePagedData } from '../composables/usePagedData'
import { useNavigation } from '../composables/useNavigation'
import PaginationControls from './PaginationControls.vue'

interface Props {
  endpoint: string
  title: string
  columns: Array<{ key: string; label: string; formatter?: (value: any) => string }>
  icon?: string
  itemLabel: string
}

const props = withDefaults(defineProps<Props>(), {
  icon: ''
})

const {
  data,
  loading,
  error,
  currentPage,
  total,
  totalPages,
  pageSize,
  fetchData,
  goToPage,
  setPageSize
} = usePagedData<any>(props.endpoint)

const { goToHome } = useNavigation()

onMounted(() => {
  fetchData()
})
</script>

<template>
  <div class="list-page">
    <div class="container">
      <div class="page-header">
        <h1 class="page-title">{{ title }}</h1>
        <button @click="goToHome" class="btn btn-back">返回首页</button>
      </div>

      <div v-if="loading" class="loading">
        <div class="loading-spinner"></div>
        <span>正在加载数据...</span>
      </div>
      <div v-else-if="error" class="error">
        <span>{{ error }}</span>
      </div>
      <div v-else class="page-content">
        <div class="stats-card">
          <p class="stats-text">共 {{ total }} {{ itemLabel }} (第 {{ currentPage }} / {{ totalPages }} 页)</p>
        </div>

        <div v-if="data.length === 0" class="empty-state">
          <div class="empty-icon">📋</div>
          <h3>暂无{{ itemLabel }}数据</h3>
          <p>请等待数据添加完成后再来查看</p>
        </div>

        <div v-else class="data-section">
          <div class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th v-for="column in columns" :key="column.key">{{ column.label }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in data" :key="item.id || item[columns[0].key]" class="table-row">
                  <td v-for="column in columns" :key="column.key" class="table-cell">
                    <span v-if="column.formatter">{{ column.formatter(item[column.key]) }}</span>
                    <span v-else>{{ item[column.key] }}</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- 分页控件 -->
          <PaginationControls
            :current-page="currentPage"
            :total-pages="totalPages"
            :total="total"
            :page-size="pageSize"
            :loading="loading"
            @page-change="goToPage"
            @page-size-change="setPageSize"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.list-page {
  min-height: 100vh;
  background-color: var(--bg-secondary);
  padding: var(--spacing-lg) 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-xl);
  padding-bottom: var(--spacing);
  border-bottom: 1px solid var(--border-light);
}

.page-title {
  font-size: var(--text-3xl);
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.btn-back {
  background-color: var(--gray-100);
  color: var(--text-secondary);
  border: 1px solid var(--border-medium);
  padding: 0.5rem 1rem;
  border-radius: var(--radius);
  font-weight: 500;
  transition: all var(--transition);
}

.btn-back:hover {
  background-color: var(--gray-200);
  color: var(--text-primary);
  border-color: var(--border-dark);
}

.page-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.stats-card {
  background-color: var(--bg-primary);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  padding: var(--spacing);
  box-shadow: var(--shadow);
}

.stats-text {
  font-size: var(--text-base);
  color: var(--text-secondary);
  margin: 0;
  font-weight: 500;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-2xl);
  color: var(--text-secondary);
  gap: var(--spacing);
}

.loading-spinner {
  width: 2rem;
  height: 2rem;
  border: 2px solid var(--border-light);
  border-top: 2px solid var(--primary-600);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-2xl);
  color: var(--error);
  background-color: var(--error-light);
  border: 1px solid #fca5a5;
  border-radius: var(--radius-lg);
  font-weight: 500;
}

.empty-state {
  text-align: center;
  padding: var(--spacing-2xl);
  background-color: var(--bg-primary);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: var(--spacing);
  opacity: 0.5;
}

.empty-state h3 {
  font-size: var(--text-xl);
  color: var(--text-primary);
  margin-bottom: var(--spacing-sm);
}

.empty-state p {
  color: var(--text-secondary);
  margin: 0;
}

.data-section {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.table-container {
  overflow-x: auto;
  background-color: var(--bg-primary);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid var(--border-light);
}

.data-table th {
  background-color: var(--gray-50);
  font-weight: 600;
  color: var(--text-primary);
  border-bottom: 2px solid var(--border-medium);
  font-size: var(--text-sm);
  text-transform: uppercase;
  letter-spacing: 0.025em;
  position: sticky;
  top: 0;
  z-index: 10;
}

.data-table td {
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

.table-row {
  transition: background-color var(--transition-fast);
}

.table-row:hover {
  background-color: var(--gray-50);
}

.table-row:last-child .table-cell {
  border-bottom: none;
}

.table-cell {
  position: relative;
  vertical-align: middle;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .list-page {
    padding: var(--spacing) 0;
  }
  
  .page-header {
    flex-direction: column;
    align-items: stretch;
    gap: var(--spacing);
    margin-bottom: var(--spacing-lg);
  }
  
  .page-title {
    font-size: var(--text-2xl);
    text-align: center;
  }
  
  .btn-back {
    align-self: center;
  }
  
  .data-table th,
  .data-table td {
    padding: 0.75rem 0.5rem;
    font-size: var(--text-xs);
  }
  
  .empty-state {
    padding: var(--spacing-lg);
  }
  
  .empty-icon {
    font-size: 2rem;
  }
  
  .empty-state h3 {
    font-size: var(--text-lg);
  }
}

@media (max-width: 480px) {
  .page-header {
    padding-bottom: var(--spacing-sm);
  }
  
  .page-title {
    font-size: var(--text-xl);
  }
  
  .data-table th,
  .data-table td {
    padding: 0.5rem 0.25rem;
  }
  
  .empty-state {
    padding: var(--spacing);
  }
  
  .empty-icon {
    font-size: 1.5rem;
  }
  
  .empty-state h3 {
    font-size: var(--text-base);
  }
}
</style>