<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-card">
        <!-- Logo区域 -->
        <div class="login-header">
          <div class="login-logo">
            <div class="logo-icon">📚</div>
          </div>
          <h1 class="login-title">请假管理系统</h1>
          <p class="login-subtitle">欢迎回来，请登录您的账户</p>
        </div>

        <!-- 登录模式切换 -->
        <div class="login-tabs">
          <button
            @click="loginMode = 'password'"
            :class="['tab-button', { active: loginMode === 'password' }]"
            type="button"
          >
            账号密码登录
          </button>
          <button
            @click="generateQRCode"
            :class="['tab-button', { active: loginMode === 'qrcode' }]"
            type="button"
          >
            扫码登录
          </button>
        </div>

        <!-- 账号密码登录 -->
        <div v-if="loginMode === 'password'" class="login-form-container">
          <form @submit.prevent="handleLogin" class="login-form">
            <div class="form-group">
              <label for="role" class="form-label">角色</label>
              <select id="role" v-model="loginForm.role" class="form-select" required>
                <option value="" disabled>请选择角色</option>
                <option value="admin">管理员</option>
                <option value="reviewer">审核员</option>
                <option value="teacher">教师</option>
                <option value="student">学生</option>
              </select>
            </div>

            <div class="form-group">
              <label for="id" class="form-label">账号</label>
              <input
                type="text"
                id="id"
                v-model="loginForm.id"
                class="form-input"
                placeholder="请输入用户ID"
                required
              />
            </div>

            <div class="form-group">
              <label for="password" class="form-label">密码</label>
              <input
                type="password"
                id="password"
                v-model="loginForm.password"
                class="form-input"
                placeholder="请输入密码"
                required
              />
            </div>

            <button type="submit" class="btn btn-primary btn-lg w-full" :disabled="isLoading">
              <span v-if="!isLoading">登录</span>
              <span v-else>登录中...</span>
            </button>
          </form>

          <!-- 错误信息显示 -->
          <div v-if="errorMessage" class="alert alert-danger mt-4">
            {{ errorMessage }}
          </div>
        </div>

        <!-- 扫码登录 -->
        <div v-if="loginMode === 'qrcode'" class="qrcode-container">
          <div class="qrcode-box">
            <div v-if="qrCodeDataUrl" class="qrcode-image">
              <img :src="qrCodeDataUrl" alt="登录二维码" />
            </div>
            <div v-else-if="qrLoading" class="qr-loading">
              <div class="loading-spinner"></div>
              <p>生成二维码中...</p>
            </div>
            <div v-else class="qr-error">
              <p>二维码生成失败</p>
            </div>
          </div>

          <div class="qr-token-display" v-if="qrToken">
            <code>{{ qrToken }}</code>
          </div>

          <button @click="handleQRCodeCheck" class="btn btn-success btn-lg w-full" :disabled="qrChecking">
            <span v-if="!qrChecking">我已扫码</span>
            <span v-else>验证中...</span>
          </button>

          <!-- 扫码错误信息显示 -->
          <div v-if="qrErrorMessage" class="alert alert-danger mt-4">
            {{ qrErrorMessage }}
          </div>

          <div class="qr-refresh">
            <button @click="generateQRCode" class="btn btn-outline w-full">刷新二维码</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--primary-50) 0%, var(--bg-secondary) 100%);
  padding: var(--spacing);
}

.login-container {
  width: 100%;
  max-width: 420px;
}

.login-card {
  background-color: var(--bg-primary);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  padding: var(--spacing-xl);
  border: 1px solid var(--border-light);
  position: relative;
  overflow: hidden;
}

.login-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--primary-500), var(--primary-600));
}

.login-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.login-logo {
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

.login-title {
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 var(--spacing-sm) 0;
  line-height: var(--leading-tight);
}

.login-subtitle {
  font-size: var(--text-base);
  color: var(--text-secondary);
  margin: 0;
  font-weight: 500;
}

.login-tabs {
  display: flex;
  background-color: var(--gray-100);
  border-radius: var(--radius-lg);
  padding: 0.25rem;
  margin-bottom: var(--spacing-xl);
  position: relative;
}

.tab-button {
  flex: 1;
  padding: 0.75rem 1rem;
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--text-secondary);
  background-color: transparent;
  border: none;
  border-radius: var(--radius);
  cursor: pointer;
  transition: all var(--transition);
  position: relative;
  z-index: 2;
}

.tab-button.active {
  color: var(--primary-700);
  background-color: var(--bg-primary);
  box-shadow: var(--shadow);
}

.tab-button:hover:not(.active) {
  color: var(--text-primary);
}

.login-form-container {
  margin-bottom: var(--spacing);
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
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

.form-input,
.form-select {
  padding: 0.75rem 1rem;
  font-size: var(--text-base);
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-lg);
  background-color: var(--bg-primary);
  color: var(--text-primary);
  transition: all var(--transition);
}

.form-input:focus,
.form-select:focus {
  outline: none;
  border-color: var(--primary-500);
  box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.1);
}

.form-input::placeholder {
  color: var(--text-tertiary);
}

.qrcode-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-lg);
}

.qrcode-box {
  width: 200px;
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--bg-primary);
  border: 2px solid var(--border-medium);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.qrcode-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.qr-loading,
.qr-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--spacing);
  padding: var(--spacing);
  text-align: center;
  color: var(--text-secondary);
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

.qr-token-display {
  background-color: var(--gray-100);
  padding: var(--spacing-sm);
  border-radius: var(--radius);
  border: 1px solid var(--border-light);
  word-break: break-all;
}

.qr-token-display code {
  font-size: var(--text-xs);
  color: var(--text-secondary);
  font-family: var(--font-mono);
}

.qr-refresh {
  width: 100%;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-page {
    padding: var(--spacing-sm);
  }
  
  .login-container {
    max-width: 100%;
  }
  
  .login-card {
    padding: var(--spacing-lg);
  }
  
  .login-logo {
    width: 56px;
    height: 56px;
  }
  
  .logo-icon {
    font-size: 1.75rem;
  }
  
  .login-title {
    font-size: var(--text-xl);
  }
  
  .login-subtitle {
    font-size: var(--text-sm);
  }
  
  .tab-button {
    padding: 0.5rem 0.75rem;
    font-size: var(--text-xs);
  }
  
  .qrcode-box {
    width: 180px;
    height: 180px;
  }
}

@media (max-width: 480px) {
  .login-card {
    padding: var(--spacing);
  }
  
  .login-logo {
    width: 48px;
    height: 48px;
  }
  
  .logo-icon {
    font-size: 1.5rem;
  }
  
  .login-title {
    font-size: var(--text-lg);
  }
  
  .login-subtitle {
    font-size: var(--text-xs);
  }
  
  .qrcode-box {
    width: 160px;
    height: 160px;
  }
  
  .form-input,
  .form-select {
    padding: 0.625rem 0.875rem;
    font-size: var(--text-sm);
  }
}
</style>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { login, checkAuth } from '../api'
import QRCode from 'qrcode'
import type { LoginResponse, CheckAuthResponse } from '../types'

const router = useRouter()

const loginForm = reactive({
  role: '',
  id: '',
  password: '',
  token: ''
})

const isLoading = ref(false)
const errorMessage = ref('')

// 扫码登录相关
const loginMode = ref<'password' | 'qrcode'>('password')
const qrToken = ref('')
const qrCodeDataUrl = ref('')
const qrLoading = ref(false)
const qrChecking = ref(false)
const qrErrorMessage = ref('')

// 生成唯一token
const generateToken = (): string => {
  return Date.now().toString(36) + Math.random().toString(36).slice(2)
}

// 存储登录信息到localStorage
const storeLoginInfo = (token: string, role: string, id: number, name: string) => {
  localStorage.setItem('token', token)
  localStorage.setItem('role', role)
  localStorage.setItem('id', id.toString())
  localStorage.setItem('name', name)
}

const handleLogin = async () => {
  try {
    isLoading.value = true
    errorMessage.value = ''

    // 生成唯一token
    loginForm.token = generateToken()

    // 调用登录API
    const response = await login(loginForm) as unknown as LoginResponse

    // 分别存储到localStorage
    storeLoginInfo(response.token, response.role, response.id, response.name)

    console.log('登录成功:', response)

    // 登录成功后跳转到首页
    router.push('/')

  } catch (error: any) {
    console.error('登录失败:', error)
    errorMessage.value = error.response?.data?.message || '登录失败，请检查用户名和密码'
  } finally {
    isLoading.value = false
  }
}

// 生成二维码
const generateQRCode = async () => {
  try {
    loginMode.value = 'qrcode'
    qrLoading.value = true
    qrErrorMessage.value = ''

    // 生成唯一的扫码token
    qrToken.value = generateToken()

    // 生成二维码
    qrCodeDataUrl.value = await QRCode.toDataURL(qrToken.value, {
      width: 200,
      margin: 2,
      color: {
        dark: '#000000',
        light: '#FFFFFF'
      }
    })

    console.log('二维码生成成功:', qrToken.value)

  } catch (error) {
    console.error('二维码生成失败:', error)
    qrErrorMessage.value = '二维码生成失败，请重试'
  } finally {
    qrLoading.value = false
  }
}

// 验证扫码登录
const handleQRCodeCheck = async () => {
  try {
    qrChecking.value = true
    qrErrorMessage.value = ''

    // 调用登录检查API
    const response = await checkAuth(qrToken.value) as unknown as CheckAuthResponse

    // 分别存储到localStorage
    storeLoginInfo(qrToken.value, response.role, response.id, response.name)

    console.log('扫码登录成功:', response)

    // 登录成功后跳转到首页
    router.push('/')

  } catch (error: any) {
    console.error('扫码登录验证失败:', error)
    qrErrorMessage.value = '登录验证失败，请确认是否已扫码或重试'
  } finally {
    qrChecking.value = false
  }
}
</script>

