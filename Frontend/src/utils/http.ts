import axios from 'axios'

// 创建axios实例
const http = axios.create({
  // baseURL: 'http://localhost:8000/api/v1',
  // baseURL: 'https://amazon.gxj62.cn/api/v1',
  baseURL: 'https://lms.gxj62.cn/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
http.interceptors.request.use(
  (config) => {
    // 可以在这里添加token等
    const token = localStorage.getItem('token')
    if (token) {
      // 同时添加到 params 和 headers
      if (!config.params) {
        config.params = {}
      }
      config.params.token = token
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
http.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    console.error('HTTP请求错误:', error)
    return Promise.reject(error)
  }
)

export default http