<script setup lang="ts">
import { ref, reactive } from 'vue'
import GenericList from '../components/GenericList.vue'
import { formatDate, getStatusBadgeClass } from '../utils/formatters'
import { exportToExcel } from '../utils/excelExporter'
import { createLeave, getAllCourses, getStudentCourses, editLeave, auditLeave } from '../api'
import type { Leave, LeaveCreate, Course, StudentCourseResponse } from '../types'

// 创建请假条相关状态
const showCreateModal = ref(false)
const isCreating = ref(false)
const createError = ref('')
const courses = ref<Course[]>([])
const coursesLoading = ref(false)

// 编辑请假条相关状态
const showEditModal = ref(false)
const isEditing = ref(false)
const editError = ref('')
const currentEditLeave = ref<Leave | null>(null)

// 审核请假条相关状态
const showAuditModal = ref(false)
const isAuditing = ref(false)
const auditError = ref('')
const currentAuditLeave = ref<Leave | null>(null)
const auditForm = reactive({
  status: '',
  audit_remarks: ''
})

// 获取当前用户信息
const currentUserId = parseInt(localStorage.getItem('id') || '0')
const currentUserRole = localStorage.getItem('role') || ''

// 创建请假条表单数据
const leaveForm = reactive<LeaveCreate>({
  student_id: currentUserId, // 默认使用当前用户的ID
  leave_date: '',
  leave_hours: '',
  status: '待审批',
  leave_type: '',
  remarks: '',
  materials: '',
  course_id: 0,
  teacher_id: 0
})

// 获取课程数据
const fetchCourses = async () => {
  try {
    coursesLoading.value = true

    if (currentUserRole === 'student') {
      // 学生角色：只获取已选的课程
      const studentCoursesResponse = await getStudentCourses(currentUserId) as unknown as StudentCourseResponse[]

      // 将StudentCourseResponse转换为Course格式
      courses.value = studentCoursesResponse.map((sc: StudentCourseResponse) => ({
        course_id: sc.course_id,
        course_name: sc.course_name || `课程 ${sc.course_id}`,
        class_hours: 0, // 从StudentCourseResponse中无法直接获取class_hours
        teacher_id: 0, // 从StudentCourseResponse中无法直接获取teacher_id
        teacher_name: sc.teacher_name || '未知教师'
      }))

      console.log('学生已选课程:', courses.value)
    } else {
      // 其他角色：获取所有课程
      const response = await getAllCourses() as unknown as { items: Course[] }
      courses.value = response.items || []
      console.log('所有课程:', courses.value)
    }
  } catch (error) {
    console.error('获取课程失败:', error)
    courses.value = []
  } finally {
    coursesLoading.value = false
  }
}

// 打开创建弹窗
const openCreateModal = async () => {
  showCreateModal.value = true
  createError.value = ''

  // 先获取课程数据
  await fetchCourses()

  // 重置表单，学生ID根据角色设置
  Object.assign(leaveForm, {
    student_id: currentUserRole === 'student' ? currentUserId : 0, // 学生角色使用自己的ID
    leave_date: '',
    leave_hours: '',
    status: '待审批',
    leave_type: '',
    remarks: '',
    materials: '',
    course_id: 0,
    teacher_id: 0
  })
}

// 关闭创建弹窗
const closeCreateModal = () => {
  showCreateModal.value = false
  createError.value = ''
}

// 处理课程选择变化
const handleCourseChange = () => {
  // 重置教师ID，会根据选择的课程自动设置
  leaveForm.teacher_id = 0

  // 如果选择了课程，显示课程信息
  if (leaveForm.course_id && leaveForm.course_id > 0) {
    const selectedCourse = courses.value.find(c => c.course_id === leaveForm.course_id)
    if (selectedCourse) {
      console.log('选择课程:', selectedCourse)
      // 设置教师ID
      leaveForm.teacher_id = selectedCourse.teacher_id
    }
  }
}

// 创建请假条
const handleCreateLeave = async () => {
  try {
    isCreating.value = true
    createError.value = ''

    // 验证必填字段
    if (!leaveForm.student_id || !leaveForm.leave_date || !leaveForm.leave_hours) {
      createError.value = '请填写必填字段：学生ID、请假日期、请假课时'
      return
    }

    // 格式化数据以符合 API 要求
    const formattedData: any = {
      student_id: parseInt(leaveForm.student_id.toString()),
      leave_date: leaveForm.leave_date, // 直接使用日期字符串，后端会处理时间
      leave_hours: leaveForm.leave_hours ? leaveForm.leave_hours.toString() : '',
      status: leaveForm.status || '待审批'
    }

    // 如果选择了课程，添加课程ID和教师ID
    if (leaveForm.course_id && leaveForm.course_id > 0) {
      formattedData.course_id = parseInt(leaveForm.course_id.toString())

      // 查找对应的教师ID
      const selectedCourse = courses.value.find(c => c.course_id === leaveForm.course_id)
      if (selectedCourse) {
        formattedData.teacher_id = selectedCourse.teacher_id
      }
    }

    // 只添加有值的可选字段
    if (leaveForm.leave_type) {
      formattedData.leave_type = leaveForm.leave_type.slice(0, 8) // 限制长度为8
    }
    if (leaveForm.remarks) {
      formattedData.remarks = leaveForm.remarks.slice(0, 100) // 限制长度为100
    }
    if (leaveForm.materials) {
      formattedData.materials = leaveForm.materials.slice(0, 100) // 限制长度为100
    }

    console.log('提交请假条数据:', formattedData)

    // 调用创建API
    await createLeave(formattedData)

    // 创建成功，关闭弹窗并刷新列表
    closeCreateModal()
    refreshData()

  } catch (error: any) {
    console.error('创建请假条失败:', error)
    console.error('错误详情:', error.response?.data)

    // 尝试提取详细的错误信息
    let errorMessage = '创建失败，请重试'
    if (error.response?.data) {
      const errorData = error.response.data
      if (errorData.detail && Array.isArray(errorData.detail)) {
        // OpenAPI 验证错误格式
        errorMessage = errorData.detail.map((item: any) => `${item.loc?.join('.')}: ${item.msg}`).join('; ')
      } else if (errorData.message) {
        errorMessage = errorData.message
      } else if (typeof errorData === 'string') {
        errorMessage = errorData
      }
    }

    createError.value = errorMessage
  } finally {
    isCreating.value = false
  }
}

// 打开编辑弹窗
const openEditModal = async (leave: Leave) => {
  showEditModal.value = true
  editError.value = ''
  currentEditLeave.value = leave

  // 先获取课程数据
  await fetchCourses()

  // 用请假条当前数据填充表单
  Object.assign(leaveForm, {
    student_id: leave.student_id,
    leave_date: leave.leave_date ? new Date(leave.leave_date).toISOString().split('T')[0] : '',
    leave_hours: leave.leave_hours || '',
    leave_type: leave.leave_type || '',
    remarks: leave.remarks || '',
    materials: leave.materials || '',
    course_id: leave.course_id || 0,
    teacher_id: leave.teacher_id || 0
  })
}

// 关闭编辑弹窗
const closeEditModal = () => {
  showEditModal.value = false
  editError.value = ''
  currentEditLeave.value = null
}

// 处理编辑请假条
const handleEditLeave = async () => {
  try {
    isEditing.value = true
    editError.value = ''

    if (!currentEditLeave.value) return

    // 验证必填字段
    if (!leaveForm.student_id || !leaveForm.leave_date || !leaveForm.leave_hours) {
      editError.value = '请填写必填字段：学生ID、请假日期、请假课时'
      return
    }

    // 格式化数据以符合 API 要求
    const formattedData: any = {
      student_id: parseInt(leaveForm.student_id.toString()),
      leave_date: leaveForm.leave_date,
      leave_hours: leaveForm.leave_hours ? leaveForm.leave_hours.toString() : '',
      status: currentEditLeave.value.status // 保持原有状态
    }

    // 如果选择了课程，添加课程ID和教师ID
    if (leaveForm.course_id && leaveForm.course_id > 0) {
      formattedData.course_id = parseInt(leaveForm.course_id.toString())

      const selectedCourse = courses.value.find(c => c.course_id === leaveForm.course_id)
      if (selectedCourse) {
        formattedData.teacher_id = selectedCourse.teacher_id
      }
    }

    // 只添加有值的可选字段
    if (leaveForm.leave_type) {
      formattedData.leave_type = leaveForm.leave_type.slice(0, 8)
    }
    if (leaveForm.remarks) {
      formattedData.remarks = leaveForm.remarks.slice(0, 100)
    }
    if (leaveForm.materials) {
      formattedData.materials = leaveForm.materials.slice(0, 100)
    }

    console.log('提交编辑请假条数据:', formattedData)

    // 调用编辑API
    await editLeave(currentEditLeave.value.leave_id, formattedData)

    // 编辑成功，关闭弹窗并刷新列表
    closeEditModal()
    refreshData()

  } catch (error: any) {
    console.error('编辑请假条失败:', error)

    let errorMessage = '编辑失败，请重试'
    if (error.response?.data) {
      const errorData = error.response.data
      if (errorData.detail && Array.isArray(errorData.detail)) {
        errorMessage = errorData.detail.map((item: any) => `${item.loc?.join('.')}: ${item.msg}`).join('; ')
      } else if (errorData.message) {
        errorMessage = errorData.message
      } else if (typeof errorData === 'string') {
        errorMessage = errorData
      }
    }

    editError.value = errorMessage
  } finally {
    isEditing.value = false
  }
}

// 打开审核弹窗
const openAuditModal = (leave: Leave) => {
  showAuditModal.value = true
  auditError.value = ''
  currentAuditLeave.value = leave

  // 审核表单初始化为空，让审核人重新选择
  Object.assign(auditForm, {
    status: '',
    audit_remarks: ''
  })
}

// 关闭审核弹窗
const closeAuditModal = () => {
  showAuditModal.value = false
  auditError.value = ''
  currentAuditLeave.value = null
  Object.assign(auditForm, {
    status: '',
    audit_remarks: ''
  })
}

// 处理审核请假条
const handleAuditLeave = async () => {
  try {
    isAuditing.value = true
    auditError.value = ''

    if (!currentAuditLeave.value) return

    // 验证必填字段
    if (!auditForm.status) {
      auditError.value = '请选择审核状态'
      return
    }

    // 准备审核数据 - 需要包含原始数据的必要字段
    const auditData: any = {
      status: auditForm.status,
      audit_remarks: auditForm.audit_remarks ? auditForm.audit_remarks.slice(0, 100) : null,
      leave_hours: currentAuditLeave.value.leave_hours ? currentAuditLeave.value.leave_hours.toString() : ''
    }

    // 添加其他必要字段
    if (currentAuditLeave.value.student_id) {
      auditData.student_id = currentAuditLeave.value.student_id
    }
    if (currentAuditLeave.value.leave_date) {
      auditData.leave_date = currentAuditLeave.value.leave_date
    }
    if (currentAuditLeave.value.leave_type) {
      auditData.leave_type = currentAuditLeave.value.leave_type.slice(0, 8)
    }
    if (currentAuditLeave.value.remarks) {
      auditData.remarks = currentAuditLeave.value.remarks.slice(0, 100)
    }
    if (currentAuditLeave.value.materials) {
      auditData.materials = currentAuditLeave.value.materials.slice(0, 100)
    }
    if (currentAuditLeave.value.course_id) {
      auditData.course_id = currentAuditLeave.value.course_id
    }
    if (currentAuditLeave.value.teacher_id) {
      auditData.teacher_id = currentAuditLeave.value.teacher_id
    }

    console.log('提交审核数据:', auditData)

    // 调用审核API
    await auditLeave(currentAuditLeave.value.leave_id, auditData)

    // 审核成功，关闭弹窗并刷新列表
    closeAuditModal()
    refreshData()

  } catch (error: any) {
    console.error('审核请假条失败:', error)

    let errorMessage = '审核失败，请重试'
    if (error.response?.data) {
      const errorData = error.response.data
      if (errorData.detail && Array.isArray(errorData.detail)) {
        errorMessage = errorData.detail.map((item: any) => `${item.loc?.join('.')}: ${item.msg}`).join('; ')
      } else if (errorData.message) {
        errorMessage = errorData.message
      } else if (typeof errorData === 'string') {
        errorMessage = errorData
      }
    }

    auditError.value = errorMessage
  } finally {
    isAuditing.value = false
  }
}

// 导出相关状态
const isExporting = ref(false)

// 导出CSV
const handleExportCSV = async () => {
  try {
    isExporting.value = true

    // 获取所有数据，不分页
    const token = localStorage.getItem('token')
    if (!token) {
      console.error('未找到 token，无法导出')
      return
    }

    console.log('正在获取所有数据用于导出...')

    let allData: any[] = []
    let currentPage = 1
    let hasMoreData = true

    // 循环获取所有页面的数据
    while (hasMoreData) {
      const params = new URLSearchParams({
        token,
        page: currentPage.toString(),
        page_size: '100' // 设置为最大值100
      })

      const response = await fetch(`/api/v1/leaves?${params}`)
      if (!response.ok) {
        throw new Error(`导出失败: ${response.statusText}`)
      }

      const result = await response.json()
      const currentPageData = result.items || []

      // 将当前页数据添加到总数据中
      allData = allData.concat(currentPageData)

      console.log(`已获取第 ${currentPage} 页数据，本页 ${currentPageData.length} 条，累计 ${allData.length} 条`)

      // 检查是否还有下一页
      if (currentPageData.length < 100) {
        hasMoreData = false
      } else {
        currentPage++
      }
    }

    if (allData.length === 0) {
      alert('没有数据可以导出')
      return
    }

    // 定义 CSV 列名和对应的数据键
    const headers = [
      '请假ID',
      '学生ID',
      '学生名称',
      '请假类型',
      '请假课时',
      '请假时间',
      '备注',
      '状态',
      '审核人ID',
      '审核人姓名',
      '审核意见',
      '审核时间',
      '材料',
      '课程ID',
      '教师ID'
    ]

    // 转换数据格式
    const csvData = allData.map((item: any) => ({
      '请假ID': item.leave_id,
      '学生ID': item.student_id,
      '学生名称': item.student_name || '',
      '请假类型': item.leave_type || '',
      '请假课时': item.leave_hours || '',
      '请假时间': item.leave_date ? new Date(item.leave_date).toLocaleString('zh-CN') : '',
      '备注': item.remarks || '',
      '状态': item.status || '',
      '审核人ID': item.reviewer_id || '',
      '审核人姓名': item.reviewer_name || '',
      '审核意见': item.audit_remarks || '',
      '审核时间': item.audit_time ? new Date(item.audit_time).toLocaleString('zh-CN') : '',
      '材料': item.materials || '',
      '课程ID': item.course_id || '',
      '教师ID': item.teacher_id || ''
    }))

    // 导出为 Excel
    exportToExcel(csvData, '请假条数据', headers)

  } catch (error: any) {
    console.error('导出失败:', error)
    alert(`导出失败: ${error.message || '未知错误'}`)
  } finally {
    isExporting.value = false
  }
}

// 判断是否可以编辑（学生只能编辑自己的请假条）
const canEdit = (leave: Leave): boolean => {
  return currentUserRole === 'student' && leave.student_id === currentUserId && leave.status === '待审批'
}

// 判断是否可以审核（审核员/教师可以审核待审批的请假条）
const canAudit = (leave: Leave): boolean => {
  return (currentUserRole === 'reviewer' || currentUserRole === 'teacher') && leave.status === '待审批'
}

// 刷新数据的函数，用于在创建/编辑/审核后刷新列表
const refreshData = () => {
  // GenericList组件会自动处理刷新，这里可以添加其他逻辑
  console.log('数据已刷新')
}
</script>

<template>
  <div class="leaves-page">
    <!-- 自定义页面头部，包含创建按钮 -->
    <div class="page-header">
      <h1 class="page-title">请假条列表</h1>
      <div class="header-buttons">
        <button @click="openCreateModal" class="btn btn-primary">
          创建请假条
        </button>
        <button @click="handleExportCSV" class="btn btn-export" :disabled="isExporting">
          {{ isExporting ? '导出中...' : '导出Excel' }}
        </button>
      </div>
    </div>

    <GenericList
      endpoint="/leaves"
      title=""
      item-label="张请假条"
      :show-actions="true"
      :hide-export="true"
      :hide-back-button="true"
      :columns="[
        { key: 'leave_id', label: '请假ID' },
        { key: 'student_name', label: '学生名称' },
        { key: 'leave_type', label: '请假类型' },
        { key: 'leave_hours', label: '请假课时' },
        {
          key: 'leave_date',
          label: '请假时间',
          formatter: formatDate
        },
        { key: 'remarks', label: '备注' },
        {
          key: 'status',
          label: '状态'
        },
        { key: 'reviewer_name', label: '审核人姓名' },
        { key: 'audit_remarks', label: '审核意见' }
      ]"
    >
      <template #actions="{ item }">
        <div class="action-buttons">
          <button v-if="canEdit(item)" @click="openEditModal(item)" class="btn btn-warning btn-sm">
            修改
          </button>
          <button v-if="canAudit(item)" @click="openAuditModal(item)" class="btn btn-primary btn-sm">
            审核
          </button>
        </div>
      </template>
    </GenericList>

    <!-- 创建请假条弹窗 -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="closeCreateModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>创建请假条</h3>
        </div>

        <form @submit.prevent="handleCreateLeave" class="modal-form">
          <div class="form-row-two">
            <div class="form-group">
              <label for="student_id">
                学生ID
              </label>
              <input type="number" id="student_id" v-model="leaveForm.student_id"
                :readonly="currentUserRole === 'student'" :disabled="currentUserRole === 'student'"
                :class="{ 'readonly-input': currentUserRole === 'student' }" required
                :placeholder="currentUserRole === 'student' ? `当前用户ID: ${currentUserId}` : '请输入学生ID'" min="1" />
            </div>
            <div class="form-group">
              <label for="leave_date">请假日期 *</label>
              <input type="date" id="leave_date" v-model="leaveForm.leave_date" required />
            </div>
          </div>

          <div class="form-group">
            <label for="course">课程</label>
            <select id="course" v-model="leaveForm.course_id" @change="handleCourseChange">
              <option value="0">请选择课程</option>
              <option v-if="coursesLoading" value="">加载中...</option>
              <option v-for="course in courses" :key="course.course_id" :value="course.course_id">
                {{ course.course_name }} ({{ course.teacher_name }})
              </option>
            </select>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="leave_hours">请假课时 *</label>
              <input type="number" id="leave_hours" v-model="leaveForm.leave_hours" required placeholder="数字" />
            </div>
            <div class="form-group">
              <label for="leave_type">请假类型</label>
              <select id="leave_type" v-model="leaveForm.leave_type">
                <option value="">请选择请假类型</option>
                <option value="病假">病假</option>
                <option value="事假">事假</option>
                <option value="公假">公假</option>
                <option value="其他">其他</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label for="remarks">备注</label>
            <textarea id="remarks" v-model="leaveForm.remarks" rows="3" placeholder="请输入请假事由等备注信息"
              maxlength="100"></textarea>
          </div>

          <!-- 错误信息 -->
          <div v-if="createError" class="error-message">
            {{ createError }}
          </div>

          <div class="modal-footer">
            <button type="button" @click="closeCreateModal" class="btn btn-secondary">
              取消
            </button>
            <button type="submit" class="btn btn-primary" :disabled="isCreating">
              {{ isCreating ? '创建中...' : '创建请假条' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 编辑请假条弹窗 -->
    <div v-if="showEditModal" class="modal-overlay" @click.self="closeEditModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>修改请假条</h3>
        </div>

        <form @submit.prevent="handleEditLeave" class="modal-form">
          <div class="form-row-two">
            <div class="form-group">
              <label for="edit_student_id">
                学生ID
              </label>
              <input type="number" id="edit_student_id" v-model="leaveForm.student_id" readonly disabled
                class="readonly-input" :placeholder="`当前用户ID: ${currentUserId}`" min="1" />
            </div>
            <div class="form-group">
              <label for="edit_leave_date">请假日期 *</label>
              <input type="date" id="edit_leave_date" v-model="leaveForm.leave_date" required />
            </div>
          </div>

          <div class="form-group">
            <label for="edit_course">课程</label>
            <select id="edit_course" v-model="leaveForm.course_id" @change="handleCourseChange">
              <option value="0">请选择课程</option>
              <option v-if="coursesLoading" value="">加载中...</option>
              <option v-for="course in courses" :key="course.course_id" :value="course.course_id">
                {{ course.course_name }} ({{ course.teacher_name }})
              </option>
            </select>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="edit_leave_hours">请假课时 *</label>
              <input type="number" id="edit_leave_hours" v-model="leaveForm.leave_hours" required placeholder="数字" />
            </div>
            <div class="form-group">
              <label for="edit_leave_type">请假类型</label>
              <select id="edit_leave_type" v-model="leaveForm.leave_type">
                <option value="">请选择请假类型</option>
                <option value="病假">病假</option>
                <option value="事假">事假</option>
                <option value="公假">公假</option>
                <option value="其他">其他</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label for="edit_remarks">备注</label>
            <textarea id="edit_remarks" v-model="leaveForm.remarks" rows="3" placeholder="请输入请假事由等备注信息"
              maxlength="100"></textarea>
          </div>

          <!-- 错误信息 -->
          <div v-if="editError" class="error-message">
            {{ editError }}
          </div>

          <div class="modal-footer">
            <button type="button" @click="closeEditModal" class="btn btn-secondary">
              取消
            </button>
            <button type="submit" class="btn btn-primary" :disabled="isEditing">
              {{ isEditing ? '修改中...' : '确认修改' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 审核请假条弹窗 -->
    <div v-if="showAuditModal" class="modal-overlay" @click.self="closeAuditModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>审核请假条</h3>
        </div>

        <form @submit.prevent="handleAuditLeave" class="modal-form">
          <div class="form-group">
            <label for="audit_status">审核状态 *</label>
            <select id="audit_status" v-model="auditForm.status" required>
              <option value="">请选择审核状态</option>
              <option value="已批准">已批准</option>
              <option value="已拒绝">已拒绝</option>
            </select>
          </div>

          <div class="form-group">
            <label for="audit_remarks">审核备注</label>
            <textarea id="audit_remarks" v-model="auditForm.audit_remarks" rows="4" placeholder="请输入审核意见"
              maxlength="100"></textarea>
          </div>

          <!-- 错误信息 -->
          <div v-if="auditError" class="error-message">
            {{ auditError }}
          </div>

          <div class="modal-footer">
            <button type="button" @click="closeAuditModal" class="btn btn-secondary">
              取消
            </button>
            <button type="submit" class="btn btn-primary" :disabled="isAuditing">
              {{ isAuditing ? '审核中...' : '确认审核' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-xl);
  padding-bottom: var(--spacing);
  border-bottom: 1px solid var(--border-light);
}

.page-title {
  font-size: var(--text-3xl);
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.header-buttons {
  display: flex;
  gap: var(--spacing);
}

.btn-export {
  background-color: #10b981;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: var(--radius);
  font-size: var(--text-sm);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition);
}

.btn-export:hover {
  background-color: #059669;
  color: white;
}

.btn-export:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
  opacity: 0.7;
}


/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: var(--spacing);
}

.modal-content {
  background-color: var(--bg-primary);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  max-width: 600px;
  width: 100%;
  max-height: 85vh;
  overflow-y: auto;
  position: relative;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem var(--spacing-lg);
  border-bottom: 1px solid var(--border-light);
}

.modal-header h3 {
  font-size: var(--text-xl);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.close-button {
  background: none;
  border: none;
  font-size: var(--text-2xl);
  color: var(--text-tertiary);
  cursor: pointer;
  padding: 0;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius);
  transition: all var(--transition);
}

.close-button:hover {
  background-color: var(--gray-100);
  color: var(--text-primary);
}

.modal-form {
  padding: var(--spacing-lg);
  display: flex;
  flex-direction: column;
  gap: var(--spacing);
}

.form-row-two {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing);
}

.form-row-two {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing);
}

.form-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.form-group label {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--text-primary);
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 0.75rem;
  font-size: var(--text-base);
  border: 1px solid var(--border-medium);
  border-radius: var(--radius);
  background-color: var(--bg-primary);
  color: var(--text-primary);
  transition: all var(--transition);
  height: 2.75rem;
  line-height: 1.5;
  box-sizing: border-box;
}

.form-group input[type="date"] {
  height: 2.75rem;
  padding: 0.5rem 0.75rem;
}

.form-group select {
  height: 2.75rem;
  padding: 0.5rem 0.75rem;
  appearance: none;
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e");
  background-position: right 0.5rem center;
  background-repeat: no-repeat;
  background-size: 1.5em 1.5em;
  padding-right: 2.5rem;
}

.form-group textarea {
  height: auto;
  min-height: 80px;
  resize: vertical;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--primary-500);
  box-shadow: 0 0 0 2px rgba(14, 165, 233, 0.1);
}

.readonly-input {
  background-color: var(--gray-100);
  color: var(--text-tertiary);
  cursor: not-allowed;
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.error-message {
  background-color: var(--error-light);
  color: var(--error);
  padding: var(--spacing);
  border-radius: var(--radius);
  border: 1px solid #fca5a5;
  font-size: var(--text-sm);
  font-weight: 500;
}


.btn-export {
  background-color: #10b981;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: var(--radius);
  font-size: var(--text-sm);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition);
}

.btn-export:hover {
  background-color: #059669;
  color: white;
}

.btn-export:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
  opacity: 0.7;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing);
  padding-top: 0.75rem;
  border-top: 1px solid var(--border-light);
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .modal-content {
    max-width: 90%;
  }
}

@media (max-width: 768px) {
  .leaves-page {
    padding: var(--spacing) 0;
  }

  .page-header {
    flex-direction: column;
    align-items: stretch;
    gap: var(--spacing);
    margin-bottom: var(--spacing-lg);
  }

  .header-buttons {
    justify-content: center;
  }

  .form-row-three {
    grid-template-columns: 1fr;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .modal-content {
    max-width: 100%;
    margin: var(--spacing);
  }

  .modal-header {
    padding: var(--spacing);
  }

  .modal-form {
    padding: var(--spacing);
  }

  .data-table th,
  .data-table td {
    padding: 0.75rem 0.5rem;
    font-size: var(--text-xs);
  }
}

</style>
