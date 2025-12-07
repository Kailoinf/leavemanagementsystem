<template>
  <div class="admin-create-container">
    <div class="admin-create-card">
      <h2 class="title">🔧 创建系统管理员</h2>
      <p class="subtitle">首次使用系统，需要创建管理员账户</p>

      <form @submit.prevent="handleCreateAdmin" class="admin-form">
        <div class="form-group">
          <label for="admin_id">管理员ID</label>
          <input
            type="number"
            id="admin_id"
            v-model="adminForm.admin_id"
            required
            placeholder="请输入管理员ID（数字）"
            min="1"
          />
        </div>

        <div class="form-group">
          <label for="name">管理员姓名</label>
          <input
            type="text"
            id="name"
            v-model="adminForm.name"
            required
            placeholder="请输入管理员姓名（最多8个字符）"
            maxlength="8"
          />
        </div>

        <div class="form-group">
          <label for="password">密码</label>
          <input
            type="password"
            id="password"
            v-model="adminForm.password"
            required
            placeholder="请输入密码"
          />
        </div>

        <button type="submit" class="create-button" :disabled="isLoading">
          {{ isLoading ? '创建中...' : '创建管理员' }}
        </button>
      </form>

      <!-- 错误信息显示 -->
      <div v-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </div>

      <!-- 成功信息显示 -->
      <div v-if="successMessage" class="success-message">
        {{ successMessage }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { createAdmin } from '../api'

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
</script>

<style scoped>
.admin-create-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.admin-create-card {
  background: white;
  padding: 3rem;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  width: 100%;
  max-width: 500px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.title {
  text-align: center;
  color: #333;
  margin-bottom: 1rem;
  font-size: 2rem;
  font-weight: 700;
}

.subtitle {
  text-align: center;
  color: #666;
  margin-bottom: 2.5rem;
  font-size: 1rem;
}

.admin-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

label {
  font-weight: 600;
  color: #555;
  font-size: 0.9rem;
}

input {
  padding: 1rem;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.3s ease;
}

input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.create-button {
  padding: 1rem;
  background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 1rem;
}

.create-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
}

.create-button:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.error-message {
  margin-top: 1.5rem;
  padding: 1rem;
  background-color: #fee;
  color: #c33;
  border: 1px solid #fcc;
  border-radius: 8px;
  text-align: center;
  font-weight: 500;
}

.success-message {
  margin-top: 1.5rem;
  padding: 1rem;
  background-color: #efe;
  color: #3c3;
  border: 1px solid #cfc;
  border-radius: 8px;
  text-align: center;
  font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .admin-create-card {
    margin: 1rem;
    padding: 2rem;
  }

  .title {
    font-size: 1.5rem;
  }

  .subtitle {
    font-size: 0.9rem;
  }
}
</style>