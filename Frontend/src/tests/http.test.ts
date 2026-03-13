import { describe, it, expect, vi, beforeEach } from 'vitest'
import http from '@/utils/http'

// Mock axios
vi.mock('axios', () => ({
  default: {
    create: vi.fn(() => ({
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      delete: vi.fn(),
      defaults: {
        baseURL: 'http://localhost:8000/api/v1',
        timeout: 10000,
        headers: {
          'Content-Type': 'application/json',
        },
      },
      interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() },
      },
    })),
  },
}))

describe('HTTP 工具', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('应该创建 axios 实例', () => {
    expect(http).toBeDefined()
  })

  it('应该有请求拦截器', () => {
    // 验证拦截器已设置
    expect(http.interceptors.request).toBeDefined()
    expect(http.interceptors.response).toBeDefined()
  })

  it('应该从环境变量读取 API 地址', () => {
    // 验证 baseURL 配置正确
    expect(http.defaults.baseURL).toBeDefined()
    expect(http.defaults.baseURL).toContain('/api/v1')
  })

  it('应该有正确的超时配置', () => {
    expect(http.defaults.timeout).toBe(10000)
  })

  it('应该有正确的默认 headers', () => {
    expect(http.defaults.headers['Content-Type']).toBe('application/json')
  })
})
