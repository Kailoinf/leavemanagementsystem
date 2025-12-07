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
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { checkSystemHealth } from './api'
import type { HealthCheckResponse } from './types'

const router = useRouter()
const isHealthChecking = ref(true)

// 应用启动时检查系统健康状态
onMounted(async () => {
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

  } catch (error) {
    console.error('系统健康检查失败:', error)
    // 如果健康检查失败，也允许正常使用，可能是网络问题
  } finally {
    isHealthChecking.value = false
  }
})
</script>

