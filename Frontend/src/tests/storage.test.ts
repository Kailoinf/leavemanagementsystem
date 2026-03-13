import { describe, it, expect, beforeEach, vi } from 'vitest'

describe('LocalStorage', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.clearAllMocks()
  })

  it('应该能够存储和获取数据', () => {
    const testData = { key: 'value' }
    localStorage.setItem('test', JSON.stringify(testData))
    const result = localStorage.getItem('test')
    expect(result).toBe(JSON.stringify(testData))
  })

  it('应该能够删除数据', () => {
    localStorage.setItem('test', 'data')
    localStorage.removeItem('test')
    const result = localStorage.getItem('test')
    expect(result).toBeNull()
  })

  it('应该能够清空所有数据', () => {
    localStorage.setItem('test1', 'data1')
    localStorage.setItem('test2', 'data2')
    localStorage.clear()
    expect(localStorage.getItem('test1')).toBeNull()
    expect(localStorage.getItem('test2')).toBeNull()
  })

  it('token 应该存储在 localStorage', () => {
    const token = 'test-token-123'
    localStorage.setItem('token', token)
    expect(localStorage.getItem('token')).toBe(token)
  })
})
