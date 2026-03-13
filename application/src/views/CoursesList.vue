<script setup lang="ts">
import { onMounted } from 'vue'
import { usePagedData } from '../composables/usePagedData'
import { useNavigation } from '../composables/useNavigation'
import PaginationControls from '../components/PaginationControls.vue'
import type { Course } from '../types'

// 使用分页组合式函数
const {
  data: courses,
  loading,
  error,
  currentPage,
  total,
  totalPages,
  pageSize,
  fetchData: fetchCourses,
  goToPage,
  setPageSize
} = usePagedData<Course>('/courses')
const { goToHome } = useNavigation()

// 组件挂载时获取数据
onMounted(() => {
  fetchCourses()
})
</script>

<template>
  <div class="container">
    <h1 class="page-title">课程列表</h1>
    <button @click="goToHome" class="btn btn-back">← 返回首页</button>

    <div v-if="loading" class="loading">
      <span>🔄 正在加载数据...</span>
    </div>
    <div v-else-if="error" class="error">
      <span>❌ {{ error }}</span>
    </div>
    <div v-else>
      <div class="stats-card">
        <p class="stats-text">📚 共 {{ total }} 门课程 (第 {{ currentPage }} / {{ totalPages }} 页)</p>
      </div>

      <div v-if="courses.length === 0" class="empty-state">
        <p>📋 暂无课程数据</p>
        <p>请等待数据添加完成后再来查看</p>
      </div>

      <div v-else>
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>课程ID</th>
                <th>课程名称</th>
                <th>课时</th>
                <th>教师ID</th>
                <th>教师姓名</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="course in courses" :key="course.course_id">
                <td>{{ course.course_id }}</td>
                <td>{{ course.course_name }}</td>
                <td>{{ course.class_hours }}</td>
                <td>{{ course.teacher_id }}</td>
                <td>{{ course.teacher_name }}</td>
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