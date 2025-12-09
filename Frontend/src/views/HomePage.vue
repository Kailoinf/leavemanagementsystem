<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useApiCount } from '../composables/useApiData'
import { useNavigation } from '../composables/useNavigation'
import { logout } from '../api'
import { clearAuth } from '../utils/auth'
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

// 导航到个人资料页面
const goToProfile = () => {
  router.push('/profile')
}

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
            <div class="brand-logo">
              <div class="logo-icon">📚</div>
            </div>
            <div class="brand-text">
              <h1 class="brand-title">请假管理系统</h1>
              <p class="brand-subtitle">Leave Management System</p>
            </div>
          </div>

          <div class="header-actions">
            <div class="user-profile">
              <div class="user-avatar">
                <span class="avatar-text">{{ userInfo?.name?.charAt(0)?.toUpperCase() || 'U' }}</span>
              </div>
              <div class="user-info">
                <span class="user-name">{{ userInfo?.name || '用户' }}</span>
                <span class="user-role">{{ getRoleDisplayName(userInfo?.role) }}</span>
              </div>
            </div>

            <div class="header-buttons">
              <button @click="goToProfile" class="btn btn-outline btn-sm">
                个人资料
              </button>
              <button @click="handleLogout" class="btn btn-ghost btn-sm logout-btn">
                退出登录
              </button>
            </div>
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
              :onClick="goToStudentsList" />
            <GenericFeatureCard title="请假条管理" :count="leaveResponse?.leaves_count || 0" description="处理和审核请假申请"
              :onClick="goToLeavesList" />
            <GenericFeatureCard title="审核员管理" :count="reviewerResponse?.reviewers_count || 0" description="管理审核员权限和设置"
              :onClick="goToReviewersList" />
            <GenericFeatureCard title="教师管理" :count="teacherResponse?.teachers_count || 0" description="维护教师信息档案"
              :onClick="goToTeachersList" />
            <GenericFeatureCard title="课程管理" :count="courseResponse?.courses_count || 0" description="设置和管理课程信息"
              :onClick="goToCoursesList" />
          </div>
        </section>
      </div>
    </main>
  </div>
</template>

<style scoped>
.dashboard-page {
  min-height: 100vh;
  background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--gray-50) 100%);
}

.dashboard-header {
  background-color: var(--bg-primary);
  border-bottom: 1px solid var(--border-light);
  box-shadow: var(--shadow-sm);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing) 0;
}

.header-brand {
  display: flex;
  align-items: center;
  gap: var(--spacing);
}

.brand-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, var(--primary-500), var(--primary-600));
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
}

.logo-icon {
  font-size: 1.5rem;
  color: var(--text-inverse);
}

.brand-title {
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  line-height: var(--leading-tight);
}

.brand-subtitle {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
  margin: 0;
  font-weight: 500;
  letter-spacing: 0.025em;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
}

.header-buttons {
  display: flex;
  align-items: center;
  gap: var(--spacing);
}

.user-profile {
  display: flex;
  align-items: center;
  gap: var(--spacing);
}

.user-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, var(--primary-400), var(--primary-600));
  border-radius: 50%;
  box-shadow: var(--shadow);
}

.avatar-text {
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--text-inverse);
}

.user-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.user-name {
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--text-primary);
  line-height: var(--leading-tight);
}

.user-role {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
  font-weight: 500;
}

.logout-btn {
  padding: 0.5rem 1rem;
  background-color: transparent;
  color: var(--text-secondary);
  border: 1px solid var(--border-medium);
  border-radius: var(--radius);
  font-weight: 500;
  transition: all var(--transition);
}

.logout-btn:hover {
  background-color: var(--error-light);
  color: var(--error);
  border-color: var(--error);
}

.dashboard-main {
  padding: var(--spacing-xl) 0;
}

.features-section {
  margin-bottom: var(--spacing-2xl);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--spacing-lg);
  margin-top: var(--spacing-lg);
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .features-grid {
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: var(--spacing);
  }
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: stretch;
    gap: var(--spacing);
  }

  .header-brand {
    justify-content: center;
  }

  .header-actions {
    justify-content: space-between;
    flex-direction: row;
  }

  .user-profile {
    order: -1;
  }

  .dashboard-main {
    padding: var(--spacing-lg) 0;
  }

  .features-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: var(--spacing);
  }
}

@media (max-width: 480px) {
  .brand-title {
    font-size: var(--text-xl);
  }

  .brand-subtitle {
    font-size: var(--text-xs);
  }

  .user-avatar {
    width: 32px;
    height: 32px;
  }

  .avatar-text {
    font-size: var(--text-sm);
  }

  .user-name {
    font-size: var(--text-sm);
  }

  .user-role {
    font-size: var(--text-xs);
  }

  .logout-btn {
    padding: 0.375rem 0.75rem;
    font-size: var(--text-xs);
  }

  .dashboard-main {
    padding: var(--spacing) 0;
  }

  .features-grid {
    grid-template-columns: 1fr;
    gap: var(--spacing);
  }
}
</style>
