<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { usePagedData } from '../composables/usePagedData'
import { useNavigation } from '../composables/useNavigation'
import { formatDate, getStatusBadgeClass } from '../utils/formatters'
import { createLeave, getAllCourses } from '../api'
import PaginationControls from '../components/PaginationControls.vue'
import type { Leave, LeaveCreate, Course } from '../types'

// 使用分页组合式函数
const {
  data: leaves,
  loading,
  error,
  currentPage,
  total,
  totalPages,
  pageSize,
  fetchData: fetchLeaves,
  goToPage,
  setPageSize
} = usePagedData<Leave>('/leaves')
const { goToHome } = useNavigation()

// 创建请假条相关状态
const showCreateModal = ref(false)
const isCreating = ref(false)
const createError = ref('')
const courses = ref<Course[]>([])
const coursesLoading = ref(false)

// 获取当前用户信息
const currentUserId = parseInt(localStorage.getItem('id') || '0')
const currentUserRole = localStorage.getItem('role') || ''

// 创建请假条表单数据
const leaveForm = reactive<LeaveCreate>({
  student_id: currentUserId, // 默认使用当前用户的ID
  leave_date: '',
  leave_days: '',
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
    const response = await getAllCourses() as unknown as { items: Course[] }
    courses.value = response.items || []
    console.log('课程数据:', courses.value)
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
    leave_days: '',
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
    }
  }
}

// 创建请假条
const handleCreateLeave = async () => {
  try {
    isCreating.value = true
    createError.value = ''

    // 验证必填字段
    if (!leaveForm.student_id || !leaveForm.leave_date || !leaveForm.leave_days) {
      createError.value = '请填写必填字段：学生ID、请假日期、请假天数'
      return
    }

    // 格式化数据以符合 API 要求
    const formattedData: any = {
      student_id: parseInt(leaveForm.student_id.toString()),
      leave_date: leaveForm.leave_date, // 直接使用日期字符串，后端会处理时间
      leave_days: leaveForm.leave_days.slice(0, 8), // 限制长度为8
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
    fetchLeaves()

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

// 组件挂载时获取数据
onMounted(() => {
  fetchLeaves()
})
</script>

<template>
  <div class="container">
    <div class="page-header">
      <h1 class="page-title">请假条列表</h1>
      <div class="header-buttons">
        <button @click="openCreateModal" class="btn btn-primary">
          ➕ 创建请假条
        </button>
        <button @click="goToHome" class="btn btn-back">← 返回首页</button>
      </div>
    </div>

    <div v-if="loading" class="loading">
      <span>🔄 正在加载数据...</span>
    </div>
    <div v-else-if="error" class="error">
      <span>❌ {{ error }}</span>
    </div>
    <div v-else>
      <div class="stats-card">
        <p class="stats-text">📄 共 {{ total }} 张请假条 (第 {{ currentPage }} / {{ totalPages }} 页)</p>
      </div>

      <div v-if="leaves.length === 0" class="empty-state">
        <p>📋 暂无请假条数据</p>
        <p>请等待数据添加完成后再来查看</p>
      </div>

      <div v-else>
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>请假ID</th>
                <th>学生ID</th>
                <th>请假类型</th>
                <th>请假天数</th>
                <th>请假时间</th>
                <th>状态</th>
                <th>审核人ID</th>
                <th>审核人姓名</th>
                <th>审核意见</th>
                <th>备注</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="leave in leaves" :key="leave.leave_id">
                <td>{{ leave.leave_id }}</td>
                <td>{{ leave.student_id }}</td>
                <td>{{ leave.leave_type }}</td>
                <td>{{ leave.leave_days }}</td>
                <td>{{ formatDate(leave.leave_date) }}</td>
                <td>
                  <span :class="getStatusBadgeClass(leave.status)" class="badge">
                    {{ leave.status }}
                  </span>
                </td>
                <td>{{ leave.reviewer_id }}</td>
                <td>{{ leave.reviewer_name }}</td>
                <td>{{ leave.audit_remarks }}</td>
                <td>{{ leave.remarks }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 分页控件 -->
        <PaginationControls
          :current-page="currentPage"
          :total-pages="totalPages"
          :total="total"
          :page-size="pageSize"
          :loading="loading"
          @page-change="goToPage"
          @page-size-change="setPageSize"
        />
      </div>
    </div>

    <!-- 创建请假条弹窗 -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="closeCreateModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>创建请假条</h3>
          <button @click="closeCreateModal" class="close-button">&times;</button>
        </div>

        <form @submit.prevent="handleCreateLeave" class="modal-form">
          <div class="form-row-three">
            <div class="form-group">
              <label for="student_id">
                学生ID *
                <span v-if="currentUserRole === 'student'" class="info-text">(当前登录用户)</span>
              </label>
              <input
                type="number"
                id="student_id"
                v-model="leaveForm.student_id"
                :readonly="currentUserRole === 'student'"
                :disabled="currentUserRole === 'student'"
                :class="{ 'readonly-input': currentUserRole === 'student' }"
                required
                :placeholder="currentUserRole === 'student' ? `当前用户ID: ${currentUserId}` : '请输入学生ID'"
                min="1"
              />
              <small v-if="currentUserRole === 'student'" class="help-text">
                作为学生，只能为自己创建请假条
              </small>
            </div>
            <div class="form-group">
              <label for="leave_date">请假日期 *</label>
              <input
                type="date"
                id="leave_date"
                v-model="leaveForm.leave_date"
                required
              />
            </div>
            <div class="form-group">
              <label for="course">课程</label>
              <select id="course" v-model="leaveForm.course_id" @change="handleCourseChange">
                <option value="0">请选择课程</option>
                <option v-if="coursesLoading" value="">加载中...</option>
                <option
                  v-for="course in courses"
                  :key="course.course_id"
                  :value="course.course_id"
                >
                  {{ course.course_name }} ({{ course.teacher_name }})
                </option>
              </select>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="leave_days">请假天数 *</label>
              <input
                type="text"
                id="leave_days"
                v-model="leaveForm.leave_days"
                required
                placeholder="如：1天、2小时等"
              />
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
            <textarea
              id="remarks"
              v-model="leaveForm.remarks"
              rows="3"
              placeholder="请输入请假事由等备注信息"
              maxlength="100"
            ></textarea>
          </div>

          <div class="form-group">
            <label for="materials">材料说明</label>
            <input
              type="text"
              id="materials"
              v-model="leaveForm.materials"
              placeholder="如：医院证明、家长签字等"
              maxlength="100"
            />
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
/* 页面头部样式 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  gap: 1rem;
  flex-wrap: wrap;
}

.header-buttons {
  display: flex;
  gap: 1rem;
  align-items: center;
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  background: white;
  border-radius: 12px;
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e1e5e9;
}

.modal-header h3 {
  margin: 0;
  color: #333;
  font-size: 1.5rem;
}

.close-button {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #666;
  padding: 0.25rem;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s;
}

.close-button:hover {
  background-color: #f1f3f4;
  color: #333;
}

.modal-form {
  padding: 1.5rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1rem;
}

/* 三列布局，用于学生ID、请假日期、课程的组合 */
.form-row-three {
  display: grid;
  grid-template-columns: 1fr 2fr 2fr;
  gap: 1rem;
  margin-bottom: 1rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #333;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.readonly-input {
  background-color: #f8f9fa;
  cursor: not-allowed;
  opacity: 0.8;
}

.info-text {
  color: #666;
  font-size: 0.85rem;
  font-weight: normal;
  margin-left: 0.5rem;
}

.help-text {
  color: #667eea;
  font-size: 0.8rem;
  margin-top: 0.25rem;
  display: block;
}

.error-message {
  background-color: #fee;
  color: #c33;
  border: 1px solid #fcc;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  text-align: center;
  font-weight: 500;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid #e1e5e9;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }

  .header-buttons {
    justify-content: center;
  }

  .form-row {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .form-row-three {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .modal-content {
    margin: 1rem;
    max-height: calc(100vh - 2rem);
  }

  .modal-footer {
    flex-direction: column-reverse;
  }

  .modal-footer button {
    width: 100%;
  }
}

@media (max-width: 1024px) {
  .form-row-three {
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
  }
}
</style>
