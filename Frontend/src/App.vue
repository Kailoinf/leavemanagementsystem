<template>
  <div id="app" class="page">
    <RouterView />
  </div>
</template>

<style scoped>
#app {
  min-height: 100vh;
  background-color: var(--bg-secondary);
  font-family: var(--font-sans);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
</style>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { checkSystemHealth } from './api'
import type { HealthCheckResponse } from './types'

const router = useRouter()

// 简单的 toast 提示函数
const showToast = (message: string, type: 'error' | 'success' = 'error') => {
  const toast = document.createElement('div')
  toast.className = `toast toast-${type}`
  toast.textContent = message

  // 添加样式
  Object.assign(toast.style, {
    position: 'fixed',
    top: '20px',
    right: '20px',
    backgroundColor: type === 'error' ? '#dc3545' : '#28a745',
    color: 'white',
    padding: '12px 20px',
    borderRadius: '8px',
    fontSize: '14px',
    fontWeight: '500',
    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
    zIndex: '9999',
    maxWidth: '300px',
    wordWrap: 'break-word',
    opacity: '0',
    transform: 'translateX(100%)',
    transition: 'all 0.3s ease'
  })

  document.body.appendChild(toast)

  // 触发动画
  setTimeout(() => {
    toast.style.opacity = '1'
    toast.style.transform = 'translateX(0)'
  }, 10)

  // 3秒后移除
  setTimeout(() => {
    toast.style.opacity = '0'
    toast.style.transform = 'translateX(100%)'
    setTimeout(() => {
      if (toast.parentNode) {
        toast.parentNode.removeChild(toast)
      }
    }, 300)
  }, 3000)
}

// 将 showToast 函数挂载到全局，以便其他组件使用
;(window as any).showToast = showToast

// 执行健康检查
const performHealthCheck = async () => {
  try {
    console.log('正在检查系统健康状态...')
    const healthStatus = await checkSystemHealth() as unknown as HealthCheckResponse
    console.log('系统健康状态:', healthStatus)

    // 如果系统状态不健康且没有管理员，跳转到管理员创建页面
    if (healthStatus.status === 'unhealthy' && healthStatus.message === 'No admin found') {
      console.log('系统未初始化，跳转到管理员创建页面')
      router.replace('/admin/create')
      return
    }

    // 如果系统健康，正常启动
    console.log('系统状态正常')

  } catch (error: any) {
    console.error('系统健康检查失败:', error)

    // 检查是否是网络错误（请求没有回复）
    if (error.code === 'NETWORK_ERROR' || error.message?.includes('Network Error') ||
        error.message?.includes('ERR_NETWORK') || !error.response) {
      showToast('无法连接到服务器，请检查网络连接或稍后重试')
      return
    }

    // 其他类型的错误，允许正常使用
    console.log('健康检查出现其他错误，允许正常使用')
  }
}

// 应用启动时检查系统健康状态
onMounted(async () => {
  await performHealthCheck()
})
</script>

