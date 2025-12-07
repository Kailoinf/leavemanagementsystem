<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useApiCount } from '../composables/useApiData'
import { useNavigation } from '../composables/useNavigation'
import { logout } from '../api'
import { clearAuth } from '../utils/auth'
import GenericStatsCard from '../components/GenericStatsCard.vue'
import GenericFeatureCard from '../components/GenericFeatureCard.vue'
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

// 获取角色显示名称
const getRoleDisplayName = (role: string | undefined | null) => {
  switch (role) {
    case 'admin':
      return '管理员'
    case 'teacher':
      return '教师'
    case 'student':
      return '学生'
    case 'reviewer':
      return '审核员'
    default:
      return '用户'
  }
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
  <div class="dashboard-page">
    <!-- 头部导航 -->
    <header class="dashboard-header">
      <div class="container">
        <div class="header-content">
          <div class="header-brand">

            <div class="brand-text">
              <h1 class="brand-title">请假管理系统</h1>
              <p class="brand-subtitle">Leave Management System</p>
            </div>
          </div>

          <div class="header-actions">
            <div class="user-profile">
              <div class="user-info">
                <span class="user-name">{{ userInfo?.name || '用户' }}</span>
                <span class="user-role">{{ getRoleDisplayName(userInfo?.role) }}</span>
              </div>
            </div>

            <button @click="handleLogout" class="btn btn-ghost btn-sm logout-btn">

              退出登录
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- 主要内容 -->
    <main class="dashboard-main">
      <div class="container">
        <!-- 错误提示 -->
        <div v-if="error" class="alert alert-danger">
          {{ error }}
        </div>

        <!-- 功能网格 -->
        <section class="features-section">
          <div class="features-grid">
            <GenericFeatureCard title="学生管理" :count="studentResponse?.students_count || 0" description="查看和管理所有学生信息"
              icon="" :onClick="goToStudentsList" />
            <GenericFeatureCard title="请假条管理" :count="leaveResponse?.leaves_count || 0" description="处理和审核请假申请" icon=""
              :onClick="goToLeavesList" />
            <GenericFeatureCard title="审核员管理" :count="reviewerResponse?.reviewers_count || 0" description="管理审核员权限和设置"
              icon="" :onClick="goToReviewersList" />
            <GenericFeatureCard title="教师管理" :count="teacherResponse?.teachers_count || 0" description="维护教师信息档案"
              icon="" :onClick="goToTeachersList" />
            <GenericFeatureCard title="课程管理" :count="courseResponse?.courses_count || 0" description="设置和管理课程信息" icon=""
              :onClick="goToCoursesList" />
          </div>
        </section>
      </div>
    </main>
  </div>
</template>
