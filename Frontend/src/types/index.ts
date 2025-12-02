/* 通用类型定义 */

export interface Student {
  student_id: string
  name: string
  department: string
  reviewer_id: string
  guarantee_permission: string
}

export interface Leave {
  leave_id: string
  student_id: string
  leave_type: string
  leave_days: number
  leave_date: string
  status: '已批准' | '待审批' | '已拒绝' | '已撤销'
  reviewer_id: string
  audit_remarks: string
  remarks: string
}

export interface Reviewer {
  reviewer_id: string
  name: string
  role: string
  department: string
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