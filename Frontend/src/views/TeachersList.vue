<script setup lang="ts">
import { onMounted } from 'vue'
import { usePagedData } from '../composables/usePagedData'
import { useNavigation } from '../composables/useNavigation'
import PaginationControls from '../components/PaginationControls.vue'
import type { Teacher } from '../types'

// 使用分页组合式函数
const {
  data: teachers,
  loading,
  error,
  currentPage,
  total,
  totalPages,
  pageSize,
  fetchData: fetchTeachers,
  goToPage,
  setPageSize
} = usePagedData<Teacher>('/teachers')
const { goToHome } = useNavigation()

// 组件挂载时获取数据
onMounted(() => {
  fetchTeachers()
})
</script>

<template>
  <div class="container">
    <h1 class="page-title">教师列表</h1>
    <button @click="goToHome" class="btn btn-back">← 返回首页</button>

    <div v-if="loading" class="loading">
      <span>🔄 正在加载数据...</span>
    </div>
    <div v-else-if="error" class="error">
      <span>❌ {{ error }}</span>
    </div>
    <div v-else>
      <div class="stats-card">
        <p class="stats-text">👨‍🏫 共 {{ total }} 名教师 (第 {{ currentPage }} / {{ totalPages }} 页)</p>
      </div>

      <div v-if="teachers.length === 0" class="empty-state">
        <p>📋 暂无教师数据</p>
        <p>请等待数据添加完成后再来查看</p>
      </div>

      <div v-else>
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>教师ID</th>
                <th>姓名</th>
                <th>密码</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="teacher in teachers" :key="teacher.teacher_id">
                <td>{{ teacher.teacher_id }}</td>
                <td>{{ teacher.name }}</td>
                <td>{{ teacher.password }}</td>
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