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