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
    <div class="pagination-controls">
      <button
        @click="handleGoToFirstPage"
        :disabled="!hasPrevPage || loading"
        class="btn btn-pagination"
        title="第一页"
      >
        «
      </button>
      <button
        @click="handleGoToPrevPage"
        :disabled="!hasPrevPage || loading"
        class="btn btn-pagination"
        title="上一页"
      >
        ‹
      </button>

      <!-- 页码跳转输入框 -->
      <div class="pagination-input-group">
        <span class="pagination-label">跳转到</span>
        <input
          v-model="goToPageInput"
          @keyup.enter="handleGoToPage"
          @blur="handleGoToPage"
          type="number"
          :min="1"
          :max="totalPages"
          class="pagination-input"
          placeholder="页码"
          :disabled="loading"
        />
        <span class="pagination-label">页</span>
        <!-- <button
          @click="handleGoToPage"
          class="btn btn-pagination"
          title="跳转"
          :disabled="loading"
        >
          →
        </button> -->
      </div>

      <span class="pagination-info">
        第 {{ currentPage }} / {{ totalPages }} 页
      </span>

      <!-- 页面大小设置 -->
      <div class="pagination-input-group">
        <span class="pagination-label">每页</span>
        <input
          v-model="pageSizeInput"
          @keyup.enter="handlePageSizeChange"
          @blur="handlePageSizeChange"
          type="number"
          :min="1"
          :max="50"
          class="pagination-input"
          placeholder="条数"
          :disabled="loading"
        />
        <span class="pagination-label">条</span>
      </div>

      <span class="pagination-info">
        共 {{ total }} 条记录
      </span>

      <button
        @click="handleGoToNextPage"
        :disabled="!hasNextPage || loading"
        class="btn btn-pagination"
        title="下一页"
      >
        ›
      </button>
      <button
        @click="handleGoToLastPage"
        :disabled="!hasNextPage || loading"
        class="btn btn-pagination"
        title="最后一页"
      >
        »
      </button>
    </div>
  </div>
</template>