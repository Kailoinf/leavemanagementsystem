/* 分页数据获取组合式函数 */

import { ref, computed, type Ref } from 'vue'
import { getPagedData } from '../api'
import type { DataState, PaginatedResponse } from '../types'

/**
 * 分页数据获取组合式函数
 * @param endpoint API端点
 * @param pageSize 每页显示数量，默认20
 * @returns 包含分页数据、加载状态和错误的状态对象
 */
export function usePagedData<T>(endpoint: string, pageSize: number = 20) {
  const data = ref<T[]>([]) as Ref<T[]>
  const loading = ref(false)
  const error = ref('')
  const currentPage = ref(1)
  const total = ref(0)
  const totalPages = ref(0)
  const pageSizeValue = ref(pageSize)

  // 计算属性
  const hasNextPage = computed(() => currentPage.value < totalPages.value)
  const hasPrevPage = computed(() => currentPage.value > 1)

  /**
   * 获取分页数据
   * @param page 页码，默认为当前页
   * @param customPageSize 自定义每页数量，可选
   */
  const fetchData = async (page: number = currentPage.value, customPageSize?: number) => {
    loading.value = true
    error.value = ''
    const actualPageSize = customPageSize || pageSizeValue.value

    try {
      const result = await getPagedData(endpoint, page, actualPageSize)

      // 类型断言，确保返回的数据符合分页响应格式
      const paginatedResult = result as unknown as PaginatedResponse<T>

      // 更新数据
      data.value = paginatedResult.items || []
      currentPage.value = paginatedResult.page || 1
      total.value = paginatedResult.total || 0
      totalPages.value = paginatedResult.total_pages || 0

      // 如果设置了自定义页面大小，更新页面大小
      if (customPageSize) {
        pageSizeValue.value = customPageSize
      }

      console.log(`获取分页数据成功 (${endpoint}):`, paginatedResult)
    } catch (err: any) {
      error.value = err.message || `获取分页数据失败 (${endpoint})`
      console.error(`获取分页数据错误 (${endpoint}):`, err)
    } finally {
      loading.value = false
    }
  }

  /**
   * 跳转到第一页
   */
  const goToFirstPage = () => {
    if (currentPage.value !== 1) {
      fetchData(1)
    }
  }

  /**
   * 跳转到上一页
   */
  const goToPrevPage = () => {
    if (hasPrevPage.value) {
      fetchData(currentPage.value - 1)
    }
  }

  /**
   * 跳转到下一页
   */
  const goToNextPage = () => {
    if (hasNextPage.value) {
      fetchData(currentPage.value + 1)
    }
  }

  /**
   * 跳转到最后一页
   */
  const goToLastPage = () => {
    if (currentPage.value !== totalPages.value) {
      fetchData(totalPages.value)
    }
  }

  /**
   * 跳转到指定页
   * @param pageNum 目标页码
   */
  const goToPage = (pageNum: number) => {
    if (pageNum >= 1 && pageNum <= totalPages.value && pageNum !== currentPage.value) {
      fetchData(pageNum)
    }
  }

  /**
   * 设置页面大小
   * @param newSize 新的页面大小
   */
  const setPageSize = (newSize: number) => {
    // 限制页面大小在1-50之间
    const validSize = Math.min(Math.max(newSize, 1), 50)
    if (validSize !== pageSizeValue.value) {
      // 重置到第一页并使用新的页面大小
      fetchData(1, validSize)
    }
  }

  /**
   * 刷新当前页数据
   */
  const refresh = () => {
    fetchData(currentPage.value, pageSizeValue.value)
  }

  /**
   * 重置状态并刷新数据
   */
  const reset = () => {
    currentPage.value = 1
    data.value = [] as T[]
    loading.value = false
    error.value = ''
    total.value = 0
    totalPages.value = 0
    pageSizeValue.value = pageSize
  }

  return {
    data,
    loading,
    error,
    currentPage,
    total,
    totalPages,
    pageSize: pageSizeValue,
    hasNextPage,
    hasPrevPage,
    fetchData,
    goToFirstPage,
    goToPrevPage,
    goToNextPage,
    goToLastPage,
    goToPage,
    setPageSize,
    reset,
    refresh
  }
}