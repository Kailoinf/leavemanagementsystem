<template>
  <div class="login-container">
    <div class="login-card">
      <!-- 切换按钮 -->
      <div class="login-tabs">
        <button
          @click="loginMode = 'password'"
          :class="['tab-button', { active: loginMode === 'password' }]"
        >
          账号密码登录
        </button>
        <button
          @click="generateQRCode"
          :class="['tab-button', { active: loginMode === 'qrcode' }]"
        >
          扫码登录
        </button>
      </div>

      <!-- 账号密码登录 -->
      <div v-if="loginMode === 'password'" class="login-form-container">
        <h2>登录</h2>
        <form @submit.prevent="handleLogin" class="login-form">
          <div class="form-group">
            <label for="role">角色</label>
            <select
              id="role"
              v-model="loginForm.role"
              required
            >
              <option value="" disabled>请选择角色</option>
              <option value="reviewer">审核员</option>
              <option value="teacher">教师</option>
              <option value="student">学生</option>
            </select>
          </div>
          <div class="form-group">
            <label for="id">账号</label>
            <input
              type="text"
              id="id"
              v-model="loginForm.id"
              required
              placeholder="请输入用户ID"
            />
          </div>

          <div class="form-group">
            <label for="password">密码</label>
            <input
              type="password"
              id="password"
              v-model="loginForm.password"
              required
              placeholder="请输入密码"
            />
          </div>

          <button type="submit" class="login-button" :disabled="isLoading">
            {{ isLoading ? '登录中...' : '登录' }}
          </button>
        </form>

        <!-- 错误信息显示 -->
        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>
      </div>

      <!-- 扫码登录 -->
      <div v-if="loginMode === 'qrcode'" class="qrcode-container">
        <h2>扫码登录</h2>
        <div class="qrcode-box">
          <div v-if="qrCodeDataUrl" class="qrcode-image">
            <img :src="qrCodeDataUrl" alt="登录二维码" />
          </div>
          <div v-else-if="qrLoading" class="qr-loading">
            生成二维码中...
          </div>
          <div v-else class="qr-error">
            二维码生成失败
          </div>
        </div>

        <div class="qr-token-display" v-if="qrToken">
          <small>Token: {{ qrToken }}</small>
        </div>

        <button
          @click="handleQRCodeCheck"
          class="qr-check-button"
          :disabled="qrChecking"
        >
          {{ qrChecking ? '验证中...' : '我已扫码' }}
        </button>

        <!-- 扫码错误信息显示 -->
        <div v-if="qrErrorMessage" class="error-message">
          {{ qrErrorMessage }}
        </div>

        <div class="qr-refresh">
          <button @click="generateQRCode" class="refresh-button">
            刷新二维码
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

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

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
}

.login-card {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 450px;
}

/* 切换标签 */
.login-tabs {
  display: flex;
  margin-bottom: 2rem;
  border-bottom: 1px solid #ddd;
}

.tab-button {
  flex: 1;
  padding: 1rem;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  font-size: 1rem;
  color: #666;
  transition: all 0.2s;
}

.tab-button.active {
  color: #007bff;
  border-bottom-color: #007bff;
  font-weight: 500;
}

.tab-button:hover:not(.active) {
  color: #333;
  background-color: #f8f9fa;
}

.login-form-container {
  margin-top: 1rem;
}

.qrcode-container {
  margin-top: 1rem;
  text-align: center;
}

h2 {
  text-align: center;
  margin-bottom: 2rem;
  color: #333;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

label {
  font-weight: 500;
  color: #555;
}

select, input {
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

select:focus, input:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

.login-button {
  padding: 0.75rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.login-button:hover:not(:disabled) {
  background-color: #0056b3;
}

.login-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

/* 二维码样式 */
.qrcode-box {
  margin: 2rem 0;
  padding: 1.5rem;
  border: 2px dashed #ddd;
  border-radius: 8px;
  background-color: #fafafa;
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.qrcode-image img {
  max-width: 200px;
  height: auto;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.qr-loading, .qr-error {
  padding: 2rem;
  color: #666;
  font-size: 1rem;
}

.qr-token-display {
  margin: 1rem 0;
  padding: 0.5rem;
  background-color: #f1f3f4;
  border-radius: 4px;
  word-break: break-all;
}

.qr-check-button {
  width: 100%;
  padding: 0.75rem;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
  margin-top: 1rem;
}

.qr-check-button:hover:not(:disabled) {
  background-color: #218838;
}

.qr-check-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.qr-refresh {
  margin-top: 1rem;
}

.refresh-button {
  background: none;
  border: 1px solid #ddd;
  color: #666;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.refresh-button:hover {
  background-color: #f8f9fa;
  border-color: #aaa;
  color: #333;
}

.error-message {
  margin-top: 1rem;
  padding: 0.75rem;
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
  border-radius: 4px;
  text-align: center;
}
</style>