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