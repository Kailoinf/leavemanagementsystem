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

// 修改密码API（修改自己的密码）
export const changePassword = async (data: {
  old_password: string
  new_password: string
}, token: string) => {
  try {
    const response = await http.post('/change-password', data, {
      params: { token }
    })
    return response
  } catch (error) {
    console.error('修改密码失败:', error)
    throw error
  }
}

// 修改指定用户密码API（仅管理员可用）
export const changeUserPassword = async (userId: number, data: {
  old_password: string
  new_password: string
}, token: string) => {
  try {
    const response = await http.post(`/change-password/${userId}`, data, {
      params: { token }
    })
    return response
  } catch (error) {
    console.error('修改用户密码失败:', error)
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

// 编辑请假条API
export const editLeave = async (leaveId: number, leaveData: any) => {
  try {
    // 获取token作为查询参数
    const token = localStorage.getItem('token')

    // 构建查询参数
    const params: any = {}
    if (token) {
      params.token = token
    }

    console.log(`编辑请假条 ${leaveId} 数据:`, leaveData)
    console.log('查询参数:', params)

    // POST请求，token通过查询参数传递
    const response = await http.post(`/leaves/edit/${leaveId}`, leaveData, { params })
    console.log('编辑请假条成功:', response)
    return response
  } catch (error: any) {
    console.error('编辑请假条失败:', error)
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

// 审核请假条API (实际上是编辑的一种特殊情况)
export const auditLeave = async (leaveId: number, auditData: {
  status: string
  audit_remarks?: string
}) => {
  try {
    // 获取token作为查询参数
    const token = localStorage.getItem('token')

    // 构建查询参数
    const params: any = {}
    if (token) {
      params.token = token
    }

    console.log(`审核请假条 ${leaveId} 数据:`, auditData)
    console.log('查询参数:', params)

    // POST请求，token通过查询参数传递
    const response = await http.post(`/leaves/edit/${leaveId}`, auditData, { params })
    console.log('审核请假条成功:', response)
    return response
  } catch (error: any) {
    console.error('审核请假条失败:', error)
    if (error.response?.data) {
      console.error('错误详情:', error.response.data)
    }
    throw error
  }
}

// ============ 文件上传相关 API ============

// 上传请假材料
export const uploadMaterial = async (leaveId: number, file: File) => {
  try {
    const token = localStorage.getItem('token')
    const formData = new FormData()
    formData.append('file', file)

    const params: any = {}
    if (token) {
      params.token = token
    }

    console.log(`上传请假材料 ${leaveId}`, file.name)
    const response = await http.post(`/upload/material/${leaveId}`, formData, {
      params,
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    console.log('上传请假材料成功:', response)
    return response
  } catch (error: any) {
    console.error('上传请假材料失败:', error)
    throw error
  }
}

// 删除请假材料
export const deleteMaterial = async (filename: string) => {
  try {
    const token = localStorage.getItem('token')
    const params: any = {}
    if (token) {
      params.token = token
    }

    console.log(`删除请假材料 ${filename}`)
    const response = await http.delete(`/files/material/${filename}`, { params })
    console.log('删除请假材料成功:', response)
    return response
  } catch (error: any) {
    console.error('删除请假材料失败:', error)
    throw error
  }
}

// ============ 数据导出相关 API ============

// 导出请假记录为 CSV
export const exportLeavesCSV = async () => {
  try {
    const token = localStorage.getItem('token')
    const params: any = {}
    if (token) {
      params.token = token
    }

    console.log('导出请假记录为 CSV')
    const response = await http.get('/export/leaves/csv', {
      params,
      responseType: 'blob'
    })

    // 从响应头获取文件名
    const contentDisposition = response.headers?.['content-disposition'] || ''
    const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)
    const filename = filenameMatch ? filenameMatch[1].replace(/['"]/g, '') : `leaves_export_${Date.now()}.csv`

    // 创建下载链接
    const blob = new Blob([response.data], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    link.click()
    window.URL.revokeObjectURL(url)

    console.log('导出请假记录 CSV 成功:', filename)
    return { success: true, filename }
  } catch (error: any) {
    console.error('导出请假记录 CSV 失败:', error)
    throw error
  }
}

// 导出请假记录为 JSON
export const exportLeavesJSON = async () => {
  try {
    const token = localStorage.getItem('token')
    const params: any = {}
    if (token) {
      params.token = token
    }

    console.log('导出请假记录为 JSON')
    const response = await http.get('/export/leaves/json', {
      params,
      responseType: 'blob'
    })

    // 从响应头获取文件名
    const contentDisposition = response.headers?.['content-disposition'] || ''
    const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)
    const filename = filenameMatch ? filenameMatch[1].replace(/['"]/g, '') : `leaves_export_${Date.now()}.json`

    // 创建下载链接
    const blob = new Blob([response.data], { type: 'application/json' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    link.click()
    window.URL.revokeObjectURL(url)

    console.log('导出请假记录 JSON 成功:', filename)
    return { success: true, filename }
  } catch (error: any) {
    console.error('导出请假记录 JSON 失败:', error)
    throw error
  }
}

// 导出请假记录为 Excel
export const exportLeavesExcel = async () => {
  try {
    const token = localStorage.getItem('token')
    const params: any = {}
    if (token) {
      params.token = token
    }

    console.log('导出请假记录为 Excel')
    const response = await http.get('/export/leaves/excel', {
      params,
      responseType: 'blob'
    })

    // 从响应头获取文件名
    const contentDisposition = response.headers?.['content-disposition'] || ''
    const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)
    const filename = filenameMatch ? filenameMatch[1].replace(/['"]/g, '') : `leaves_export_${Date.now()}.xlsx`

    // 创建下载链接
    const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    link.click()
    window.URL.revokeObjectURL(url)

    console.log('导出请假记录 Excel 成功:', filename)
    return { success: true, filename }
  } catch (error: any) {
    console.error('导出请假记录 Excel 失败:', error)
    throw error
  }
}

// ============ 批量导入相关 API ============

// 批量导入学生
export const importStudents = async (file: File, defaultPassword: string = '123456') => {
  try {
    const formData = new FormData()
    formData.append('file', file)

    const params: any = { default_password: defaultPassword }

    console.log('批量导入学生', file.name)
    const response = await http.post('/import/students', formData, { params })
    console.log('批量导入学生成功:', response)
    return response
  } catch (error: any) {
    console.error('批量导入学生失败:', error)
    throw error
  }
}

// 批量导入教师
export const importTeachers = async (file: File, defaultPassword: string = '123456') => {
  try {
    const formData = new FormData()
    formData.append('file', file)

    const params: any = { default_password: defaultPassword }

    console.log('批量导入教师', file.name)
    const response = await http.post('/import/teachers', formData, { params })
    console.log('批量导入教师成功:', response)
    return response
  } catch (error: any) {
    console.error('批量导入教师失败:', error)
    throw error
  }
}

// 批量导入审核员
export const importReviewers = async (file: File, defaultPassword: string = '123456') => {
  try {
    const formData = new FormData()
    formData.append('file', file)

    const params: any = { default_password: defaultPassword }

    console.log('批量导入审核员', file.name)
    const response = await http.post('/import/reviewers', formData, { params })
    console.log('批量导入审核员成功:', response)
    return response
  } catch (error: any) {
    console.error('批量导入审核员失败:', error)
    throw error
  }
}

// 下载导入模板
export const downloadImportTemplate = async (role: 'student' | 'teacher' | 'reviewer') => {
  try {
    console.log(`下载导入模板 ${role}`)
    const response = await http.get(`/import/template/${role}`, {
      responseType: 'blob'
    })

    const filename = `${role}_import_template.csv`

    // 创建下载链接
    const blob = new Blob([response.data], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    link.click()
    window.URL.revokeObjectURL(url)

    console.log('下载导入模板成功:', filename)
    return { success: true, filename }
  } catch (error: any) {
    console.error('下载导入模板失败:', error)
    throw error
  }
}
