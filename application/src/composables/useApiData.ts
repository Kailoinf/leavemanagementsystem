/* 通用API数据获取组合式函数 */

import { ref, type Ref } from 'vue'
import { getData } from '../api'
import type { DataState, ApiResponse } from '../types'

/**
 * 通用的API数据获取组合式函数
 * @param endpoint API端点
 * @returns 包含数据、加载状态和错误的状态对象
 */
export function useApiData<T>(endpoint: string) {
  const data = ref<T[]>([]) as Ref<T[]>
  const loading = ref(false)
  const error = ref('')

  /**
   * 获取数据
   */
  const fetchData = async () => {
    loading.value = true
    error.value = ''

    try {
      const result = await getData(endpoint)
      data.value = Array.isArray(result) ? result : []
      console.log(`获取数据成功 (${endpoint}):`, result)
    } catch (err: any) {
      error.value = err.message || `获取数据失败 (${endpoint})`
      console.error(`获取数据错误 (${endpoint}):`, err)
    } finally {
      loading.value = false
    }
  }

  /**
   * 重置状态
   */
  const reset = () => {
    data.value = [] as T[]
    loading.value = false
    error.value = ''
  }

  return {
    data,
    loading,
    error,
    fetchData,
    reset
  }
}

/**
 * 获取计数的组合式函数
 * @param endpoint 计数API端点
 * @returns 包含计数结果、加载状态和错误的状态对象
 */
export function useApiCount<T extends Record<string, number>>(endpoint: string) {
  const data = ref<T | null>(null)
  const loading = ref(false)
  const error = ref('')

  /**
   * 获取计数数据
   */
  const fetchCount = async () => {
    loading.value = true
    error.value = ''

    try {
      const result = await getData(endpoint)
      data.value = result
      console.log(`获取计数成功 (${endpoint}):`, result)
    } catch (err: any) {
      error.value = err.message || `获取计数失败 (${endpoint})`
      console.error(`获取计数错误 (${endpoint}):`, err)
    } finally {
      loading.value = false
    }
  }

  /**
   * 重置状态
   */
  const reset = () => {
    data.value = null
    loading.value = false
    error.value = ''
  }

  return {
    data,
    loading,
    error,
    fetchCount,
    reset
  }
}