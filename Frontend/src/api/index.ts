import http from '../utils/http'

// GET请求示例
export const getData = async (url: string, params?: any) => {
  try {
    const response = await http.get(url, { params })
    return response
  } catch (error) {
    console.error('GET请求失败:', error)
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
