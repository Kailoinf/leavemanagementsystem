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

// 获取所有课程API
export const getAllCourses = async () => {
  try {
    // 自动添加token参数
    const token = localStorage.getItem('token')
    const requestParams: any = {}
    if (token) {
      requestParams.token = token
    }

    console.log('获取所有课程，参数:', requestParams)
    const response = await http.get('/courses', { params: requestParams })
    console.log('获取所有课程成功:', response)
    return response
  } catch (error) {
    console.error('获取所有课程失败:', error)
    throw error
  }
}

// 创建请假条API
export const createLeave = async (leaveData: any) => {
  try {
    // 获取token作为查询参数
    const token = localStorage.getItem('token')

    // 构建查询参数
    const params: any = {}
    if (token) {
      params.token = token
    }

    console.log('创建请假条数据:', leaveData)
    console.log('查询参数:', params)

    // POST请求，token通过查询参数传递
    const response = await http.post('/leaves', leaveData, { params })
    console.log('创建请假条成功:', response)
    return response
  } catch (error: any) {
    console.error('创建请假条失败:', error)
    if (error.response?.data) {
      console.error('错误详情:', error.response.data)
      if (error.response.data.detail) {
        console.error('验证错误详情:', error.response.data.detail)
        // 如果是数组，逐个输出
        if (Array.isArray(error.response.data.detail)) {
          error.response.data.detail.forEach((item: any, index: number) => {
            console.error(`验证错误 ${index + 1}:`, item)
          })
        }
      }
    }
    throw error
  }
}

// 学生选课API
export const createStudentCourse = async (studentCourseData: {
  student_id: number
  course_id: number
  enrollment_date?: string
  status?: string
}) => {
  try {
    // 获取token作为查询参数
    const token = localStorage.getItem('token')

    // 构建查询参数
    const params: any = {}
    if (token) {
      params.token = token
    }

    console.log('学生选课数据:', studentCourseData)

    // POST请求，token通过查询参数传递
    const response = await http.post('/student-courses', studentCourseData, { params })
    console.log('学生选课成功:', response)
    return response
  } catch (error) {
    console.error('学生选课失败:', error)
    throw error
  }
}

// 获取学生的选课列表API
export const getStudentCourses = async (studentId: number) => {
  try {
    const token = localStorage.getItem('token')
    const params: any = {}
    if (token) {
      params.token = token
    }

    console.log(`获取学生 ${studentId} 的选课列表`)
    const response = await http.get(`/student-courses/student/${studentId}`, { params })
    console.log('获取学生选课列表成功:', response)
    return response
  } catch (error) {
    console.error('获取学生选课列表失败:', error)
    throw error
  }
}

// 获取课程的学生列表API
export const getCourseStudents = async (courseId: number) => {
  try {
    const token = localStorage.getItem('token')
    const params: any = {}
    if (token) {
      params.token = token
    }

    console.log(`获取课程 ${courseId} 的学生列表`)
    const response = await http.get(`/student-courses/course/${courseId}`, { params })
    console.log('获取课程学生列表成功:', response)
    return response
  } catch (error) {
    console.error('获取课程学生列表失败:', error)
    throw error
  }
}

// 获取课程的选课人数API
export const getCourseEnrollmentCount = async (courseId: number) => {
  try {
    const token = localStorage.getItem('token')
    const params: any = {}
    if (token) {
      params.token = token
    }

    console.log(`获取课程 ${courseId} 的选课人数`)
    const response = await http.get(`/student-courses/course/${courseId}/count`, { params })
    console.log('获取课程选课人数成功:', response)
    return response
  } catch (error) {
    console.error('获取课程选课人数失败:', error)
    throw error
  }
}

// 获取同一教师下相似课程的学生列表API
export const getSimilarCourseStudents = async (teacherId: number, courseId: number) => {
  try {
    const token = localStorage.getItem('token')
    const params: any = {}
    if (token) {
      params.token = token
    }

    console.log(`获取教师 ${teacherId} 下相似课程 ${courseId} 的学生列表`)
    const response = await http.get(`/student-courses/teacher/${teacherId}/similar-courses/${courseId}`, { params })
    console.log('获取相似课程学生列表成功:', response)
    return response
  } catch (error) {
    console.error('获取相似课程学生列表失败:', error)
    throw error
  }
}
