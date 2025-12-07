<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useApiCount } from '../composables/useApiData'
import { useNavigation } from '../composables/useNavigation'
import { logout } from '../api'
import { clearAuth } from '../utils/auth'
import type { CountResponse } from '../types'

// 使用组合式函数
const { data: studentResponse, fetchCount: getStudentCount, error: studentError } = useApiCount<Record<string, number>>('/students/count')
const { data: leaveResponse, fetchCount: getLeavesCount, error: leaveError } = useApiCount<Record<string, number>>('/leaves/count')
const { data: reviewerResponse, fetchCount: getReviewerCount, error: reviewerError } = useApiCount<Record<string, number>>('/reviewers/count')
const { data: teacherResponse, fetchCount: getTeacherCount, error: teacherError } = useApiCount<Record<string, number>>('/teachers/count')
const { data: courseResponse, fetchCount: getCourseCount, error: courseError } = useApiCount<Record<string, number>>('/courses/count')

const router = useRouter()
const { goToStudents, goToLeaves, goToReviewers, goToTeachers, goToCourses } = useNavigation()

// 用户信息
const userInfo = computed(() => {
  const role = localStorage.getItem('role')
  const id = localStorage.getItem('id')
  const name = localStorage.getItem('name')

  return role && id && name ? {
    role: role,
    id: parseInt(id),
    name: name
  } : null
})

// 合并错误状态
const error = ref('')

// 退出登录
const handleLogout = async () => {
  try {
    const token = localStorage.getItem('token')
    if (token) {
      await logout(token)
    }
  } catch (error) {
    console.error('退出登录请求失败:', error)
  } finally {
    // 无论请求是否成功，都清除本地数据并跳转
    clearAuth()
    router.push('/login')
  }
}

// 更新导航方法名称
const goToStudentsList = () => {
  goToStudents()
}

const goToLeavesList = () => {
  goToLeaves()
}

const goToReviewersList = () => {
  goToReviewers()
}

const goToTeachersList = () => {
  goToTeachers()
}

const goToCoursesList = () => {
  goToCourses()
}

// 组件挂载时自动获取数据
onMounted(() => {
  getStudentCount()
  getLeavesCount()
  getReviewerCount()
  getTeacherCount()
  getCourseCount()
})
</script>
<template>
  <div class="container">
    <!-- 用户信息和退出按钮 -->
    <div class="header">
      <h1 class="page-title-home">🎓 LMS 管理系统</h1>
      <div class="user-info">
        <span class="welcome-text">欢迎，{{ userInfo?.name || '用户' }}</span>
        <span class="role-badge">{{ userInfo?.role === 'admin' ? '管理员' : userInfo?.role === 'teacher' ? '教师' : userInfo?.role === 'student' ? '学生' : '审核员' }}</span>
        <button @click="handleLogout" class="logout-button">退出登录</button>
      </div>
    </div>

    <div v-if="error" class="error">
      <span>❌ {{ error }}</span>
    </div>

    <div v-else class="button-grid">
      <button @click="goToStudentsList" class="dashboard-button btn-primary">
        <div class="button-icon">👨‍🎓</div>
        <div class="button-title">学生管理</div>
        <div class="button-count">{{ studentResponse?.students_count || 0 }}</div>
        <div class="button-description">查看所有学生信息</div>
      </button>

      <button @click="goToLeavesList" class="dashboard-button btn-secondary">
        <div class="button-icon">📄</div>
        <div class="button-title">请假条管理</div>
        <div class="button-count">{{ leaveResponse?.leaves_count || 0 }}</div>
        <div class="button-description">管理请假申请</div>
      </button>

      <button @click="goToReviewersList" class="dashboard-button btn-success">
        <div class="button-icon">👥</div>
        <div class="button-title">审核员管理</div>
        <div class="button-count">{{ reviewerResponse?.reviewers_count || 0 }}</div>
        <div class="button-description">管理审核人员</div>
      </button>

      <button @click="goToTeachersList" class="dashboard-button btn-success">
        <div class="button-icon">👨‍🏫</div>
        <div class="button-title">教师管理</div>
        <div class="button-count">{{ teacherResponse?.teachers_count || 0 }}</div>
        <div class="button-description">管理教师信息</div>
      </button>

      <button @click="goToCoursesList" class="dashboard-button btn-success">
        <div class="button-icon">📚</div>
        <div class="button-title">课程管理</div>
        <div class="button-count">{{ courseResponse?.courses_count || 0 }}</div>
        <div class="button-description">管理课程信息</div>
      </button>
    </div>
  </div>
</template>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding: 1rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.welcome-text {
  font-size: 1.1rem;
  color: #333;
  font-weight: 500;
}

.role-badge {
  background-color: #007bff;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 16px;
  font-size: 0.875rem;
  font-weight: 500;
}

.logout-button {
  background-color: #dc3545;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.2s;
}

.logout-button:hover {
  background-color: #c82333;
}

.page-title-home {
  margin: 0;
  color: #333;
}
</style>