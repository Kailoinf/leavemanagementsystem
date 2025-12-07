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
  <div class="container">
    <h1 class="page-title">{{ title }}</h1>
    <button @click="goToHome" class="btn btn-back">返回首页</button>

    <div v-if="loading" class="loading">
      <span>正在加载数据...</span>
    </div>
    <div v-else-if="error" class="error">
      <span>{{ error }}</span>
    </div>
    <div v-else>
      <div class="stats-card">
        <p class="stats-text">共 {{ total }} {{ itemLabel }} (第 {{ currentPage }} / {{ totalPages }} 页)</p>
      </div>

      <div v-if="data.length === 0" class="empty-state">
        <p>暂无{{ itemLabel }}数据</p>
        <p>请等待数据添加完成后再来查看</p>
      </div>

      <div v-else>
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th v-for="column in columns" :key="column.key">{{ column.label }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in data" :key="item.id || item[columns[0].key]">
                <td v-for="column in columns" :key="column.key">
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
</template>