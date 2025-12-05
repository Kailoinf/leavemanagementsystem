<script setup lang="ts">
import { onMounted } from 'vue'
import { usePagedData } from '../composables/usePagedData'
import { useNavigation } from '../composables/useNavigation'
import { formatDate } from '../utils/formatters'
import PaginationControls from '../components/PaginationControls.vue'
import type { Student } from '../types'

// 使用分页组合式函数
const {
  data: students,
  loading,
  error,
  currentPage,
  total,
  totalPages,
  pageSize,
  fetchData: fetchStudents,
  goToPage,
  setPageSize
} = usePagedData<Student>('/students')
const { goToHome } = useNavigation()

// 组件挂载时获取数据
onMounted(() => {
  fetchStudents()
})
</script>

<template>
  <div class="container">
    <h1 class="page-title">学生列表</h1>
    <button @click="goToHome" class="btn btn-back">← 返回首页</button>

    <div v-if="loading" class="loading">
      <span>🔄 正在加载数据...</span>
    </div>
    <div v-else-if="error" class="error">
      <span>❌ {{ error }}</span>
    </div>
    <div v-else>
      <div class="stats-card">
        <p class="stats-text">📚 共 {{ total }} 名学生 (第 {{ currentPage }} / {{ totalPages }} 页)</p>
      </div>

      <div v-if="students.length === 0" class="empty-state">
        <p>📋 暂无学生数据</p>
        <p>请等待数据添加完成后再来查看</p>
      </div>

      <div v-else>
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>学号</th>
                <th>姓名</th>
                <th>院系</th>
                <th>审核人ID</th>
                <th>审核人姓名</th>
                <th>担保权限到期时间</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="student in students" :key="student.student_id">
                <td>{{ student.student_id }}</td>
                <td>{{ student.name }}</td>
                <td>{{ student.school }}</td>
                <td>{{ student.reviewer_id }}</td>
                <td>{{ student.reviewer_name }}</td>
                <td>{{ formatDate(student.guarantee_permission) }}</td>
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