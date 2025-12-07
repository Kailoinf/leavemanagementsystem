<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-card card card-lg">
        <!-- Logo区域 -->
        <div class="login-header">
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

