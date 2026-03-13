<template>
  <div class="admin-create-page">
    <div class="admin-create-container">
      <div class="admin-create-card">
        <!-- Logo区域 -->
        <div class="create-header">
          <div class="create-logo">
            <div class="logo-icon">👤</div>
          </div>
          <h1 class="create-title">创建系统管理员</h1>
          <p class="create-subtitle">首次使用系统，需要创建管理员账户</p>
        </div>

        <div class="create-form-container">
          <form @submit.prevent="handleCreateAdmin" class="create-form">
            <div class="form-group">
              <label for="admin_id" class="form-label">管理员ID</label>
              <input type="number" id="admin_id" v-model="adminForm.admin_id" class="form-input" required placeholder="请输入管理员ID（数字）" min="1" />
            </div>

            <div class="form-group">
              <label for="name" class="form-label">管理员姓名</label>
              <input type="text" id="name" v-model="adminForm.name" class="form-input" required placeholder="请输入管理员姓名（最多8个字符）" maxlength="8" />
            </div>

            <div class="form-group">
              <label for="password" class="form-label">密码</label>
              <input type="password" id="password" v-model="adminForm.password" class="form-input" required placeholder="请输入密码" />
            </div>

            <button type="submit" class="btn btn-primary btn-lg w-full" :disabled="isLoading">
              <span v-if="!isLoading">创建管理员</span>
              <span v-else>创建中...</span>
            </button>
          </form>

          <!-- 错误信息显示 -->
          <div v-if="errorMessage" class="alert alert-danger mt-4">
            {{ errorMessage }}
          </div>

          <!-- 成功信息显示 -->
          <div v-if="successMessage" class="alert alert-success mt-4">
            {{ successMessage }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { createAdmin, checkSystemHealth } from '../api'
import type { HealthCheckResponse } from '../types'

const router = useRouter()

const adminForm = reactive({
  admin_id: '',
  name: '',
  password: ''
})

const isLoading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const handleCreateAdmin = async () => {
  try {
    isLoading.value = true
    errorMessage.value = ''
    successMessage.value = ''

    // 转换admin_id为数字
    const adminData = {
      admin_id: parseInt(adminForm.admin_id),
      name: adminForm.name,
      password: adminForm.password
    }

    console.log('创建管理员数据:', adminData)

    // 调用创建管理员API
    const response = await createAdmin(adminData)

    console.log('创建管理员成功:', response)
    successMessage.value = '管理员创建成功！正在跳转到登录页面...'

    // 延迟跳转到登录页面
    setTimeout(() => {
      router.push('/login')
    }, 2000)

  } catch (error: any) {
    console.error('创建管理员失败:', error)
    errorMessage.value = error.response?.data?.message || '创建管理员失败，请重试'
  } finally {
    isLoading.value = false
  }
}

// 检查系统健康状态
onMounted(async () => {
  try {
    console.log('管理员创建页面：检查系统健康状态...')
    const healthStatus = await checkSystemHealth() as unknown as HealthCheckResponse
    console.log('系统健康状态:', healthStatus)

    // 如果系统健康，跳转到首页
    if (healthStatus.status === 'healthy') {
      console.log('系统已初始化，跳转到首页')
      router.replace('/')
      return
    }

    // 如果系统状态不健康不是因为缺少管理员，也跳转到首页
    if (healthStatus.status === 'unhealthy' && healthStatus.message !== 'No admin found') {
      console.log('系统状态异常，但不是缺少管理员，跳转到首页')
      router.replace('/')
      return
    }

    // 如果是缺少管理员，允许继续在此页面
    console.log('系统缺少管理员，允许创建管理员')

  } catch (error) {
    console.error('健康检查失败:', error)
    // 健康检查失败时，允许用户继续尝试创建管理员
    console.log('健康检查失败，允许继续创建管理员')
  }
})
</script>

<style scoped>
.admin-create-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--primary-50) 0%, var(--bg-secondary) 100%);
  padding: var(--spacing);
}

.admin-create-container {
  width: 100%;
  max-width: 420px;
}

.admin-create-card {
  background-color: var(--bg-primary);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  padding: var(--spacing-xl);
  border: 1px solid var(--border-light);
  position: relative;
  overflow: hidden;
}

.create-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.create-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, var(--primary-500), var(--primary-600));
  border-radius: var(--radius-xl);
  margin: 0 auto var(--spacing);
  box-shadow: var(--shadow-lg);
}

.logo-icon {
  font-size: 2rem;
  color: var(--text-inverse);
}

.create-title {
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 var(--spacing-sm) 0;
  line-height: var(--leading-tight);
}

.create-subtitle {
  font-size: var(--text-base);
  color: var(--text-secondary);
  margin: 0;
  font-weight: 500;
}

.create-form-container {
  margin-bottom: var(--spacing);
}

.create-form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.form-label {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--text-primary);
}

.form-input {
  padding: 0.75rem 1rem;
  font-size: var(--text-base);
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-lg);
  background-color: var(--bg-primary);
  color: var(--text-primary);
  transition: all var(--transition);
}

.form-input:focus {
  outline: none;
  border-color: var(--primary-500);
  box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.1);
}

.form-input::placeholder {
  color: var(--text-tertiary);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .admin-create-page {
    padding: var(--spacing-sm);
  }

  .admin-create-container {
    max-width: 100%;
  }

  .admin-create-card {
    padding: var(--spacing-lg);
  }

  .create-logo {
    width: 56px;
    height: 56px;
  }

  .logo-icon {
    font-size: 1.75rem;
  }

  .create-title {
    font-size: var(--text-xl);
  }

  .create-subtitle {
    font-size: var(--text-sm);
  }
}

@media (max-width: 480px) {
  .admin-create-card {
    padding: var(--spacing);
  }

  .create-logo {
    width: 48px;
    height: 48px;
  }

  .logo-icon {
    font-size: 1.5rem;
  }

  .create-title {
    font-size: var(--text-lg);
  }

  .create-subtitle {
    font-size: var(--text-xs);
  }

  .form-input {
    padding: 0.625rem 0.875rem;
    font-size: var(--text-sm);
  }
}
</style>
