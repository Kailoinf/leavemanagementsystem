<script setup lang="ts">
import { ref, watch, computed } from 'vue'

interface Props {
  currentPage: number
  totalPages: number
  total: number
  pageSize: number
  loading?: boolean
}

interface Emits {
  (e: 'page-change', page: number): void
  (e: 'page-size-change', pageSize: number): void
}

const props = withDefaults(defineProps<Props>(), {
  loading: false
})

const emit = defineEmits<Emits>()

// 输入框状态
const goToPageInput = ref(props.currentPage.toString())
const pageSizeInput = ref(props.pageSize.toString())

// 监听当前页变化
watch(() => props.currentPage, (newPage) => {
  goToPageInput.value = newPage.toString()
})

// 监听页面大小变化
watch(() => props.pageSize, (newSize) => {
  pageSizeInput.value = newSize.toString()
})

// 计算属性
const hasNextPage = computed(() => props.currentPage < props.totalPages)
const hasPrevPage = computed(() => props.currentPage > 1)

// 事件处理函数
const handleGoToFirstPage = () => {
  if (hasPrevPage.value) {
    emit('page-change', 1)
  }
}

const handleGoToPrevPage = () => {
  if (hasPrevPage.value) {
    emit('page-change', props.currentPage - 1)
  }
}

const handleGoToNextPage = () => {
  if (hasNextPage.value) {
    emit('page-change', props.currentPage + 1)
  }
}

const handleGoToLastPage = () => {
  if (hasNextPage.value) {
    emit('page-change', props.totalPages)
  }
}

// 处理页码跳转
const handleGoToPage = () => {
  const pageNum = parseInt(goToPageInput.value)
  if (!isNaN(pageNum) && pageNum >= 1 && pageNum <= props.totalPages) {
    emit('page-change', pageNum)
  } else {
    // 恢复原值
    goToPageInput.value = props.currentPage.toString()
  }
}

// 处理页面大小输入
const handlePageSizeChange = () => {
  const newSize = parseInt(pageSizeInput.value)
  if (!isNaN(newSize) && newSize >= 1 && newSize <= 50) {
    emit('page-size-change', newSize)
  } else {
    // 恢复原值
    pageSizeInput.value = props.pageSize.toString()
  }
}
</script>

<template>
  <div class="pagination-container">
    <div class="pagination-info">
      <span>显示第 {{ (currentPage - 1) * pageSize + 1 }} 到 
        {{ Math.min(currentPage * pageSize, total) }} 条，
        共 {{ total }} 条数据，
        每页
        <input 
          type="number" 
          v-model="pageSizeInput"
          @change="handlePageSizeChange"
          class="page-size-input"
          min="1"
          max="50"
        /> 条
      </span>
    </div>
    
    <div class="pagination-controls">
      <button @click="handleGoToFirstPage" :disabled="!hasPrevPage" class="btn">
        首页
      </button>
      <button @click="handleGoToPrevPage" :disabled="!hasPrevPage" class="btn">
        上页
      </button>
      
      <span class="page-info">
        {{ currentPage }} / {{ totalPages }}
      </span>
      
      <button @click="handleGoToNextPage" :disabled="!hasNextPage" class="btn">
        下页
      </button>
      <button @click="handleGoToLastPage" :disabled="!hasNextPage" class="btn">
        末页
      </button>
      
      <div class="go-to-page">
        跳至
        <input 
          type="number" 
          v-model="goToPageInput"
          @blur="handleGoToPage"
          class="page-input"
          :min="1"
          :max="totalPages"
        />
        页
      </div>
    </div>
  </div>
</template>

<style scoped>
.pagination-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--spacing);
  padding: var(--spacing);
  background-color: var(--bg-primary);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
}

.pagination-info {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  font-weight: 500;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  flex-wrap: wrap;
}

.pagination-controls .btn {
  padding: 0.375rem 0.75rem;
  font-size: var(--text-sm);
  font-weight: 500;
  border-radius: var(--radius);
  background-color: var(--bg-primary);
  color: var(--text-primary);
  border: 1px solid var(--border-medium);
  transition: all var(--transition);
  cursor: pointer;
}

.pagination-controls .btn:hover:not(:disabled) {
  background-color: var(--primary-50);
  border-color: var(--primary-300);
  color: var(--primary-700);
}

.pagination-controls .btn:active:not(:disabled) {
  transform: translateY(1px);
}

.pagination-controls .btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background-color: var(--gray-100);
  color: var(--text-tertiary);
}

.page-info {
  padding: 0.375rem 0.75rem;
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--primary-600);
  background-color: var(--primary-50);
  border-radius: var(--radius);
  border: 1px solid var(--primary-200);
  min-width: 60px;
  text-align: center;
}

.go-to-page {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  font-size: var(--text-sm);
  color: var(--text-secondary);
  font-weight: 500;
}

.page-input,
.page-size-input {
  width: 3.5rem;
  padding: 0.25rem 0.5rem;
  font-size: var(--text-sm);
  text-align: center;
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-sm);
  background-color: var(--bg-primary);
  color: var(--text-primary);
  transition: all var(--transition);
}

.page-input:focus,
.page-size-input:focus {
  outline: none;
  border-color: var(--primary-500);
  box-shadow: 0 0 0 2px rgba(14, 165, 233, 0.1);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .pagination-container {
    flex-direction: column;
    align-items: stretch;
    gap: var(--spacing-sm);
  }
  
  .pagination-controls {
    justify-content: center;
    flex-wrap: wrap;
    gap: var(--spacing-xs);
  }
  
  .pagination-controls .btn {
    padding: 0.25rem 0.5rem;
    font-size: var(--text-xs);
  }
  
  .page-info {
    padding: 0.25rem 0.5rem;
    font-size: var(--text-xs);
    min-width: 50px;
  }
  
  .go-to-page {
    font-size: var(--text-xs);
  }
  
  .page-input,
  .page-size-input {
    width: 3rem;
    font-size: var(--text-xs);
  }
}

@media (max-width: 480px) {
  .pagination-container {
    padding: var(--spacing-sm);
  }
  
  .pagination-info {
    font-size: var(--text-xs);
    text-align: center;
  }
  
  .pagination-controls {
    gap: 0.25rem;
  }
  
  .pagination-controls .btn {
    padding: 0.25rem 0.375rem;
    font-size: var(--text-xs);
  }
  
  .page-info {
    padding: 0.25rem 0.375rem;
    font-size: var(--text-xs);
    min-width: 45px;
  }
  
  .go-to-page {
    font-size: var(--text-xs);
    gap: 0.125rem;
  }
  
  .page-input,
  .page-size-input {
    width: 2.5rem;
    padding: 0.125rem 0.25rem;
  }
}
</style>