<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useNavigation } from '../composables/useNavigation'
import { getCourseStudents } from '../api'
import { getStatusBadgeClass } from '../utils/formatters'
import type { StudentCourseResponse } from '../types'

// 获取路由参数
const route = useRoute()
const router = useRouter()
const courseId = parseInt(route.params.id as string)
const { goToHome } = useNavigation()

// 返回课程列表页面
const goBackToCourses = () => {
  router.push('/courses')
}

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
  <div class="course-students-page">
    <div class="container">
      <div class="page-header">
        <h1 class="page-title">{{ courseName }} - 学生名单</h1>
        <div class="header-buttons">
          <button @click="goBackToCourses" class="btn btn-back">返回课程列表</button>
        </div>
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
          <p class="stats-text">共 {{ students.length }} 名学生</p>
        </div>

        <div v-if="students.length === 0" class="empty-state">
          <div class="empty-icon">👥</div>
          <h3>暂无选课学生</h3>
          <p>该课程目前还没有学生选择</p>
        </div>

        <div v-else class="data-section">
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
                <tr v-for="student in students" :key="student.student_id" class="table-row">
                  <td class="table-cell">{{ student.student_id }}</td>
                  <td class="table-cell">{{ student.student_name || '未知' }}</td>
                  <td class="table-cell">{{ student.course_name || '未知' }}</td>
                  <td class="table-cell">{{ student.teacher_name || '未知' }}</td>
                  <td class="table-cell">{{ student.enrollment_date || '未知' }}</td>
                  <td class="table-cell">
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
  </div>
</template>

<style scoped>
.course-students-page {
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

.header-buttons {
  display: flex;
  gap: var(--spacing);
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
  .course-students-page {
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
  
  .header-buttons {
    justify-content: center;
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

