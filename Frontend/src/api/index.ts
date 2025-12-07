import http from '../utils/http'

// GET请求示例
export const getData = async (url: string, params?: any) => {
  try {
    // 自动添加token参数
    const token = localStorage.getItem('token')
    const requestParams = { ...params }
    if (token) {
      requestParams.token = token
    }

    console.log(`GET请求 ${url}，参数:`, requestParams)
    const response = await http.get(url, { params: requestParams })
    console.log(`GET请求成功 ${url}，响应:`, response)
    return response
  } catch (error) {
    console.error('GET请求失败:', error)
    throw error
  }
}

// 分页数据请求 - 仅使用GET方法
export const getPagedData = async (url: string, page: number = 1, pageSize: number = 20, params?: any) => {
  try {
    // 自动添加token参数
    const token = localStorage.getItem('token')
    const requestData = {
      page,
      page_size: pageSize,
      ...params
    }

    if (token) {
      requestData.token = token
    }

    // 直接使用GET方法
    const response = await http.get(url, { params: requestData })
    return response
  } catch (error) {
    console.error('分页请求失败:', error)
    throw error
  }
}

// POST请求示例
export const postData = async (url: string, data?: any) => {
  try {
    const response = await http.post(url, data)
    return response
  } catch (error) {
    console.error('POST请求失败:', error)
    throw error
  }
}

// 登录API
export const login = async (loginData: {
  role: string
  id: string
  password: string
  token: string
}) => {
  try {
    const response = await http.post('/login', loginData)
    return response
  } catch (error) {
    console.error('登录失败:', error)
    throw error
  }
}

// 检查登录状态API
export const checkAuth = async (token: string) => {
  try {
    const response = await http.get(`/login/check?token=${token}`)
    return response
  } catch (error) {
    console.error('检查登录状态失败:', error)
    throw error
  }
}

// 退出登录API
export const logout = async (token: string) => {
  try {
    const response = await http.get(`/logout?token=${token}`)
    return response
  } catch (error) {
    console.error('退出登录失败:', error)
    throw error
  }
}

// 系统健康检查API
export const checkSystemHealth = async () => {
  try {
    const response = await http.get('/')
    return response
  } catch (error) {
    console.error('系统健康检查失败:', error)
    throw error
  }
}

// 创建管理员API
export const createAdmin = async (adminData: {
  admin_id: number
  name: string
  password: string
}) => {
  try {
    const response = await http.post('/create/admin', adminData)
    return response
  } catch (error) {
    console.error('创建管理员失败:', error)
    throw error
  }
}
