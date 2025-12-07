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

