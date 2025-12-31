<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { usePagedData } from '../composables/usePagedData'
import { useNavigation } from '../composables/useNavigation'
import { exportToExcel } from '../utils/excelExporter'
import http from '../utils/http'
import PaginationControls from './PaginationControls.vue'

interface Props {
  endpoint: string
  title?: string
  columns: Array<{ key: string; label: string; formatter?: (value: any) => string }>
  icon?: string
  itemLabel: string
  showActions?: boolean
  showCreateLeaves?: boolean
  customData?: any[]
  customLoading?: boolean
  customError?: string
  customTotal?: number
  hideExport?: boolean
  hideBackButton?: boolean
  backButtonText?: string
  onBackClick?: () => void
}

const props = withDefaults(defineProps<Props>(), {
  title: '',
  icon: '',
  showActions: false,
  hideExport: false,
  hideBackButton: false,
  showCreateLeaves: false
})

// 导出相关状态
const isExporting = ref(false)

// 使用自定义数据或从endpoint获取数据
const {
  data: fetchedData,
  loading: fetchedLoading,
  error: fetchedError,
  currentPage,
  total,
  totalPages,
  pageSize,
  fetchData,
  goToPage,
  setPageSize
} = props.customData ? {
  data: ref(props.customData),
  loading: ref(false),
  error: ref(''),
  currentPage: ref(1),
  total: ref(props.customData?.length || 0),
  totalPages: ref(1),
  pageSize: ref(10),
  fetchData: () => Promise.resolve(),
  goToPage: () => { },
  setPageSize: () => { }
} : usePagedData<any>(props.endpoint)

// 使用自定义数据或获取的数据
const data = computed(() => props.customData || fetchedData.value)
const loading = computed(() => props.customLoading !== undefined ? props.customLoading : fetchedLoading.value)
const error = computed(() => props.customError !== undefined ? props.customError : fetchedError.value)
const displayTotal = computed(() => props.customTotal !== undefined ? props.customTotal : total.value)

const { goToHome } = useNavigation()

// 导出CSV功能
const handleExportCSV = async () => {
  try {
    isExporting.value = true

    let allData: any[] = []

    // 如果是自定义数据，直接使用
    if (props.customData) {
      allData = props.customData
    } else {
      // 获取所有数据，不分页
      console.log('正在获取所有数据用于导出...')

      let currentPage = 1
      let hasMoreData = true

      // 循环获取所有页面的数据
      while (hasMoreData) {
        const result: any = await http.get(props.endpoint, {
          params: {
            page: currentPage,
            page_size: 100 // 设置为最大值100
          }
        })

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
    }

    if (allData.length === 0) {
      alert('没有数据可以导出')
      return
    }

    // 使用props.columns的顺序作为主要导出顺序
    const mainFieldNames = props.columns.map(col => col.key)

    // 获取columns中没有但存在于数据中的其他字段
    const additionalFields = new Set<string>()
    allData.forEach((item: any) => {
      Object.keys(item).forEach(key => {
        if (!mainFieldNames.includes(key)) {
          additionalFields.add(key)
        }
      })
    })

    // 合并字段名：先按照columns顺序，然后是其他字段
    const fieldNames = [...mainFieldNames, ...Array.from(additionalFields)]

    // 使用字段名作为列名（翻译为中文）
    const headers = fieldNames.map(field => {
      // 简单的字段名翻译，可以根据需要扩展
      const fieldTranslations: { [key: string]: string } = {
        'student_id': '学生ID',
        'student_name': '学生姓名',
        'teacher_id': '教师ID',
        'teacher_name': '教师姓名',
        'reviewer_id': '审核员ID',
        'reviewer_name': '审核员姓名',
        'admin_id': '管理员ID',
        'course_id': '课程ID',
        'course_name': '课程名称',
        'leave_id': '请假ID',
        'class_hours': '课时',
        'school': '院系/部门',
        'role': '职务',
        'password': '密码',
        'guarantee_permission': '担保权限到期时间',
        'enrollment_date': '选课日期',
        'status': '状态',
        'enrollment_count': '选课人数',
        'leave_type': '请假类型',
        'leave_hours': '请假课时',
        'leave_date': '请假日期',
        'remarks': '备注',
        'materials': '材料',
        'audit_remarks': '审核意见',
        'audit_time': '审核时间'
      }
      return fieldTranslations[field] || field
    })

    // 转换数据格式，按照指定顺序
    const csvData = allData.map((item: any) => {
      const row: any = {}
      fieldNames.forEach((fieldName, index) => {
        let value = item[fieldName]

        // 格式化日期字段
        if (value && (fieldName.includes('date') || fieldName.includes('time'))) {
          value = new Date(value).toLocaleString('zh-CN')
        }

        const headerName = headers[index]
        if (headerName) {
          row[headerName] = value || ''
        }
      })
      return row
    })

    // 导出为 Excel
    exportToExcel(csvData, props.title, headers)

  } catch (error: any) {
    console.error('导出失败:', error)
    alert(`导出失败: ${error.message || '未知错误'}`)
  } finally {
    isExporting.value = false
  }
}



// 创建请假条相关
const showCreateModal = ref(false)
const isCreating = ref(false)
const createError = ref('')

interface LeaveForm {
  student_id: number | null
  course_id: number
  leave_date: string
  leave_hours: number | null
  leave_type: string
  remarks: string
}

const leaveForm = ref<LeaveForm>({
  student_id: null,
  course_id: 0,
  leave_date: '',
  leave_hours: null,
  leave_type: '',
  remarks: ''
})

// 获取当前用户信息
const currentUserId = ref<number | null>(null)
const currentUserRole = ref<string>('')

// 获取课程列表
const courses = ref<any[]>([])
const coursesLoading = ref(false)

const fetchCourses = async () => {
  try {
    coursesLoading.value = true
    const result: any = await http.get('/courses')
    courses.value = result.items || []
  } catch (error) {
    console.error('获取课程列表失败:', error)
  } finally {
    coursesLoading.value = false
  }
}

// 打开创建弹窗
const openCreateModal = () => {
  // 从 localStorage 获取当前用户信息
  const userInfo = localStorage.getItem('userInfo')
  if (userInfo) {
    try {
      const user = JSON.parse(userInfo)
      currentUserId.value = user.id
      currentUserRole.value = user.role || 'student'
      // 如果是学生，自动填充学生ID
      if (currentUserRole.value === 'student') {
        leaveForm.value.student_id = user.id
      }
    } catch (e) {
      console.error('解析用户信息失败:', e)
    }
  }

  showCreateModal.value = true
  fetchCourses()
  createError.value = ''
}

// 关闭创建弹窗
const closeCreateModal = () => {
  showCreateModal.value = false
  // 重置表单
  leaveForm.value = {
    student_id: currentUserRole.value === 'student' ? currentUserId.value : null,
    course_id: 0,
    leave_date: '',
    leave_hours: null,
    leave_type: '',
    remarks: ''
  }
  createError.value = ''
}

// 课程变更处理
const handleCourseChange = () => {
  // 可以在这里添加课程变更后的逻辑
}

// 创建请假条
const handleCreateLeave = async () => {
  try {
    isCreating.value = true
    createError.value = ''

    // 验证表单
    if (!leaveForm.value.student_id) {
      createError.value = '请输入学生ID'
      return
    }
    if (!leaveForm.value.leave_date) {
      createError.value = '请选择请假日期'
      return
    }
    if (!leaveForm.value.leave_hours || leaveForm.value.leave_hours <= 0) {
      createError.value = '请输入有效的请假课时'
      return
    }

    const payload = {
      student_id: leaveForm.value.student_id,
      course_id: leaveForm.value.course_id === 0 ? null : leaveForm.value.course_id,
      leave_date: leaveForm.value.leave_date,
      leave_hours: leaveForm.value.leave_hours,
      leave_type: leaveForm.value.leave_type || null,
      remarks: leaveForm.value.remarks || null
    }

    await http.post('/leaves', payload)
    alert('创建请假条成功')
    closeCreateModal()
    fetchData() // 刷新列表
  } catch (error: any) {
    console.error('创建请假条失败:', error)
    createError.value = error.response?.data?.message || error.message || '创建失败，请稍后重试'
  } finally {
    isCreating.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>

<template>
  <div class="list-page">
    <div class="container">
      <div class="page-header">
        <h1 v-if="title" class="page-title">{{ title }}</h1>
        <div class="header-buttons">
          <button v-if="!hideExport" @click="handleExportCSV" class="btn btn-export" :disabled="isExporting">
            {{ isExporting ? '导出中...' : '导出Excel' }}
          </button>
          <button v-if="showCreateLeaves" @click="openCreateModal" class="btn btn-primary">
            创建请假条
          </button>
          <button v-if="!hideBackButton" @click="onBackClick ? onBackClick() : goToHome()" class="btn btn-back">
            {{ backButtonText || '返回首页' }}
          </button>
        </div>
      </div>

      <div v-if="loading" class="loading">
        <div class="loading-spinner"></div>
        <span>正在加载数据...</span>
      </div>
      <div v-else-if="error" class="error">
        <span>{{ error }}</span>
      </div>
      <div v-else class="page-content">
        <div class="stats-card">
          <p class="stats-text">共 {{ displayTotal }} {{ itemLabel }} (第 {{ currentPage }} / {{ totalPages }} 页)</p>
        </div>

        <div v-if="data.length === 0" class="empty-state">
          <div class="empty-icon">📋</div>
          <h3>暂无{{ itemLabel }}数据</h3>
          <p>请等待数据添加完成后再来查看</p>
        </div>

        <div v-else class="data-section">
          <div class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th v-for="column in columns" :key="column.key">{{ column.label }}</th>
                  <th v-if="showActions">操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in data" :key="item.id || (columns[0] && item[columns[0].key])" class="table-row">
                  <template v-for="column in columns" :key="column.key">
                    <slot v-if="$slots['table-cell']" name="table-cell" :item="item" :column="column">
                      <td class="table-cell">
                        <span v-if="column.formatter">{{ column.formatter(item[column.key]) }}</span>
                        <span v-else>{{ item[column.key] }}</span>
                      </td>
                    </slot>
                    <td v-else class="table-cell">
                      <span v-if="column.formatter">{{ column.formatter(item[column.key]) }}</span>
                      <span v-else>{{ item[column.key] }}</span>
                    </td>
                  </template>
                  <td v-if="showActions" class="table-cell">
                    <slot name="actions" :item="item"></slot>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- 分页控件 (仅在非自定义数据时显示) -->
          <PaginationControls v-if="!props.customData" :current-page="currentPage" :total-pages="totalPages"
            :total="displayTotal" :page-size="pageSize" :loading="loading" @page-change="goToPage"
            @page-size-change="setPageSize" />
        </div>
      </div>
    </div>

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
                :placeholder="currentUserRole === 'student' ? `当前用户ID: ${currentUserId}` : '请输入学生ID'"
                min="1" />
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
  </div>
</template>

<style scoped>
.list-page {
  min-height: 100vh;
  background-color: var(--bg-secondary);
  padding: var(--spacing-lg) 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-xl);
  padding-bottom: var(--spacing);
  border-bottom: 1px solid var(--border-light);
}

.header-buttons {
  display: flex;
  gap: var(--spacing);
}

.page-title {
  font-size: var(--text-3xl);
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.btn-back {
  background-color: var(--gray-100);
  color: var(--text-secondary);
  border: 1px solid var(--border-medium);
  padding: 0.5rem 1rem;
  border-radius: var(--radius);
  font-weight: 500;
  transition: all var(--transition);
}

.btn-back:hover {
  background-color: var(--gray-200);
  color: var(--text-primary);
  border-color: var(--border-dark);
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

.page-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.stats-card {
  background-color: var(--bg-primary);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  padding: var(--spacing);
  box-shadow: var(--shadow);
}

.stats-text {
  font-size: var(--text-base);
  color: var(--text-secondary);
  margin: 0;
  font-weight: 500;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-2xl);
  color: var(--text-secondary);
  gap: var(--spacing);
}

.loading-spinner {
  width: 2rem;
  height: 2rem;
  border: 2px solid var(--border-light);
  border-top: 2px solid var(--primary-600);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}

.error {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-2xl);
  color: var(--error);
  background-color: var(--error-light);
  border: 1px solid #fca5a5;
  border-radius: var(--radius-lg);
  font-weight: 500;
}

.empty-state {
  text-align: center;
  padding: var(--spacing-2xl);
  background-color: var(--bg-primary);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: var(--spacing);
  opacity: 0.5;
}

.empty-state h3 {
  font-size: var(--text-xl);
  color: var(--text-primary);
  margin-bottom: var(--spacing-sm);
}

.empty-state p {
  color: var(--text-secondary);
  margin: 0;
}

.data-section {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.table-container {
  overflow-x: auto;
  background-color: var(--bg-primary);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid var(--border-light);
}

.data-table th {
  background-color: var(--gray-50);
  font-weight: 600;
  color: var(--text-primary);
  border-bottom: 2px solid var(--border-medium);
  font-size: var(--text-sm);
  text-transform: uppercase;
  letter-spacing: 0.025em;
  position: sticky;
  top: 0;
  z-index: 10;
}

.data-table td {
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

.table-row {
  transition: background-color var(--transition-fast);
}

.table-row:hover {
  background-color: var(--gray-50);
}

.table-row:last-child .table-cell {
  border-bottom: none;
}

.table-cell {
  position: relative;
  vertical-align: middle;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .list-page {
    padding: var(--spacing) 0;
  }

  .page-header {
    flex-direction: column;
    align-items: stretch;
    gap: var(--spacing);
    margin-bottom: var(--spacing-lg);
  }

  .page-title {
    font-size: var(--text-2xl);
    text-align: center;
  }

  .btn-back {
    align-self: center;
  }

  .data-table th,
  .data-table td {
    padding: 0.75rem 0.5rem;
    font-size: var(--text-xs);
  }

  .empty-state {
    padding: var(--spacing-lg);
  }

  .empty-icon {
    font-size: 2rem;
  }

  .empty-state h3 {
    font-size: var(--text-lg);
  }
}

@media (max-width: 480px) {
  .page-header {
    padding-bottom: var(--spacing-sm);
  }

  .page-title {
    font-size: var(--text-xl);
  }

  .data-table th,
  .data-table td {
    padding: 0.5rem 0.25rem;
  }

  .empty-state {
    padding: var(--spacing);
  }

  .empty-icon {
    font-size: 1.5rem;
  }

  .empty-state h3 {
    font-size: var(--text-base);
  }
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
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: var(--spacing);
}

.modal-content {
  background-color: var(--bg-primary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  padding: var(--spacing-lg);
  border-bottom: 1px solid var(--border-light);
}

.modal-header h3 {
  margin: 0;
  font-size: var(--text-xl);
  color: var(--text-primary);
}

.modal-form {
  padding: var(--spacing-lg);
}

.form-row-two {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing);
}

.form-group {
  margin-bottom: var(--spacing);
}

.form-group label {
  display: block;
  margin-bottom: var(--spacing-sm);
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--text-primary);
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--border-medium);
  border-radius: var(--radius);
  font-size: var(--text-sm);
  transition: border-color var(--transition);
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--primary-600);
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.readonly-input {
  background-color: var(--gray-100);
  cursor: not-allowed;
  color: var(--text-secondary);
}

.error-message {
  padding: var(--spacing);
  background-color: var(--error-light);
  color: var(--error);
  border: 1px solid #fca5a5;
  border-radius: var(--radius);
  font-size: var(--text-sm);
  margin-bottom: var(--spacing);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing);
  padding-top: var(--spacing);
  border-top: 1px solid var(--border-light);
}

.btn-secondary {
  background-color: var(--gray-100);
  color: var(--text-secondary);
  border: 1px solid var(--border-medium);
  padding: 0.5rem 1rem;
  border-radius: var(--radius);
  font-weight: 500;
  transition: all var(--transition);
}

.btn-secondary:hover {
  background-color: var(--gray-200);
  color: var(--text-primary);
  border-color: var(--border-dark);
}

.btn-primary {
  background-color: var(--primary-600);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: var(--radius);
  font-weight: 500;
  transition: all var(--transition);
}

.btn-primary:hover {
  background-color: var(--primary-700);
}

.btn-primary:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
  opacity: 0.7;
}

@media (max-width: 768px) {
  .form-row-two,
  .form-row {
    grid-template-columns: 1fr;
  }

  .modal-content {
    max-width: 100%;
  }

  .modal-footer {
    flex-direction: column;
  }

  .modal-footer button {
    width: 100%;
  }
}
</style>