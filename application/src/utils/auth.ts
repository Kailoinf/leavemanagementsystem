import { checkAuth } from '../api'
import type { CheckAuthResponse } from '../types'

// 检查用户是否已登录
export const isAuthenticated = async (): Promise<boolean> => {
  const token = localStorage.getItem('token')
  if (!token) {
    return false
  }

  try {
    // 验证token是否有效并获取最新用户信息
    const response = await checkAuth(token) as unknown as CheckAuthResponse

    // 更新localStorage中的用户信息（可能已被后端修改）
    if (response.role && response.id && response.name) {
      localStorage.setItem('role', response.role)
      localStorage.setItem('id', response.id.toString())
      localStorage.setItem('name', response.name)
    }

    return true
  } catch (error) {
    // token无效，清除本地存储
    localStorage.removeItem('token')
    localStorage.removeItem('role')
    localStorage.removeItem('id')
    localStorage.removeItem('name')
    return false
  }
}

// 获取用户信息
export const getUserInfo = () => {
  const role = localStorage.getItem('role')
  const id = localStorage.getItem('id')
  const name = localStorage.getItem('name')

  return role && id && name ? {
    role: role,
    id: parseInt(id),
    name: name
  } : null
}

// 清除登录信息
export const clearAuth = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('role')
  localStorage.removeItem('id')
  localStorage.removeItem('name')
}