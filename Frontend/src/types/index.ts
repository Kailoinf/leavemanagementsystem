/* 通用类型定义 */

export interface Student {
  student_id: number
  name: string
  school: string
  reviewer_id: number
  reviewer_name: string
  password: string
  guarantee_permission: string
}

export interface Leave {
  leave_id: string
  student_id: string
  leave_type: string
  leave_days: number
  leave_date: string
  status: '已批准' | '待审批' | '已拒绝' | '已撤销'
  reviewer_id: number
  reviewer_name: string
  audit_remarks: string
  remarks: string
}

export interface LeaveCreate {
  student_id: number
  leave_date: string
  class_hours?: string
  leave_days: string
  status: string
  leave_type?: string
  remarks?: string
  materials?: string
  reviewer_id?: number
  teacher_id?: number
  audit_remarks?: string
  audit_time?: string | null
  course_id?: number
  is_modified?: string
  guarantee_student_id?: number
}

export interface Reviewer {
  reviewer_id: string
  name: string
  role: string
  school: string
}

export interface Course {
  course_id: number
  course_name: string
  class_hours: number
  teacher_id: number
  teacher_name: string
  enrollment_count?: number // 可选的选课人数字段
}

export interface Teacher {
  teacher_id: number
  name: string
  password: string
}

export interface ApiResponse<T> {
  data: T
  success: boolean
  message?: string
}

export interface CountResponse {
  students_count?: number
  leaves_count?: number
  reviewers_count?: number
}

export type LoadingState = 'idle' | 'loading' | 'success' | 'error'

export interface DataState<T> {
  data: T[]
  loading: boolean
  error: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

// 登录相关类型
export interface LoginRequest {
  role: string
  id: string
  password: string
  token: string
}

export interface LoginResponse {
  role: string
  id: number
  name: string
  token: string
}

export interface CheckAuthResponse {
  role: string
  id: number
  name: string
}

export interface HealthCheckResponse {
  status: 'healthy' | 'unhealthy'
  message?: string
  timestamp?: string
}

// 学生选课相关类型
export interface StudentCourse {
  student_id: number
  course_id: number
  enrollment_date: string
  status: string
}

export interface StudentCourseCreate {
  student_id: number
  course_id: number
  enrollment_date?: string
  status?: string
}

export interface StudentCourseResponse {
  student_id: number
  course_id: number
  enrollment_date: string | null
  status: string
  student_name: string | null
  course_name: string | null
  teacher_name: string | null
}