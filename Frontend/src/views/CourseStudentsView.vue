<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useNavigation } from '../composables/useNavigation'
import { getCourseStudents } from '../api'
import { getStatusBadgeClass } from '../utils/formatters'
import type { StudentCourseResponse } from '../types'

// 获取路由参数
const route = useRoute()
const courseId = parseInt(route.params.id as string)
const { goToHome } = useNavigation()

// 数据状态
const students = ref<StudentCourseResponse[]>([])
const loading = ref(false)
const error = ref('')
const courseName = ref('')

// 获取课程学生名单
const fetchCourseStudents = async () => {
  try {
    loading.value = true
    error.value = ''

    const response = await getCourseStudents(courseId) as unknown as StudentCourseResponse[]
    students.value = response

    // 从第一个学生的记录中获取课程名称
    if (response.length > 0 && response[0]?.course_name) {
      courseName.value = response[0].course_name
    } else {
      courseName.value = `课程 ${courseId}`
    }

    console.log(`课程 ${courseId} 的学生名单:`, students.value)
  } catch (err: any) {
    console.error('获取课程学生名单失败:', err)
    error.value = '获取课程学生名单失败，请重试'
  } finally {
    loading.value = false
  }
}

// 组件挂载时获取数据
onMounted(() => {
  if (courseId) {
    fetchCourseStudents()
  } else {
    error.value = '无效的课程ID'
  }
})
</script>

<template>
  <div class="container">
    <div class="page-header">
      <h1 class="page-title">{{ courseName }} - 学生名单</h1>
      <div class="header-buttons">
        <button @click="goToHome" class="btn btn-back">返回首页</button>
      </div>
    </div>

    <div v-if="loading" class="loading">
      <span>正在加载数据...</span>
    </div>
    <div v-else-if="error" class="error">
      <span>{{ error }}</span>
    </div>
    <div v-else>
      <div class="stats-card">
        <p class="stats-text">共 {{ students.length }} 名学生</p>
      </div>

      <div v-if="students.length === 0" class="empty-state">
        <p>暂无选课学生</p>
        <p>该课程目前还没有学生选择</p>
      </div>

      <div v-else>
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>学生ID</th>
                <th>学生姓名</th>
                <th>课程名称</th>
                <th>教师姓名</th>
                <th>选课日期</th>
                <th>状态</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="student in students" :key="student.student_id">
                <td>{{ student.student_id }}</td>
                <td>{{ student.student_name || '未知' }}</td>
                <td>{{ student.course_name || '未知' }}</td>
                <td>{{ student.teacher_name || '未知' }}</td>
                <td>{{ student.enrollment_date || '未知' }}</td>
                <td>
                  <span :class="getStatusBadgeClass(student.status)" class="badge">
                    {{ student.status }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

